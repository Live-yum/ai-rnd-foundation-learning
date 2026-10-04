"""Trusted adapter for the authored contest reference oracle, outside candidate code.

Only disposable native sandbox accounts and fixed private PostgreSQL probes are
supported. Never use this adapter with a user database or a public service.
"""

import json
import re
import threading
import time
import uuid
from urllib.parse import urlsplit

import httpx

from scripts.extension_oracles.contest import (
    EMPTY_SQL,
    IDENTITY_SQL,
    INVITE_SQL,
    MEMBER_SQL,
    TEAM_SQL,
)
from workbench.capability_contracts import HttpStep
from workbench.capability_isolation import control_exec, read_command_output, redirected_command
from workbench.capability_stack import pg_verifier_argv
from workbench.capability_verification import CaptureBudget, CheckFailure, preview_url

MAX_HTTP_BYTES = 2_000_000
MAX_PROBE_BYTES = 65_536
ENVELOPE = {"code", "msg", "data", "status_code", "success"}
ACTORS = ("captain", "member_a", "member_b", "outsider", "reviewer")
TABLE_COLUMNS = {
    "rnd_contest_team": {
        "id": "int4",
        "captain_id": "int4",
        "capacity": "int4",
        "name": "varchar",
        "submission_title": "varchar",
    },
    "rnd_contest_membership": {"team_id": "int4", "user_id": "int4"},
    "rnd_contest_invitation": {
        "id": "int4",
        "team_id": "int4",
        "code_hash": "varchar",
        "status": "varchar",
        "expires_at": "timestamptz",
    },
}


def _decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    try:
        return json.loads(
            raw,
            object_pairs_hook=pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError()),
        )
    except ValueError, UnicodeError, RecursionError:
        raise CheckFailure("原生业务验收响应不是有效且无重复键的JSON") from None


def normalized_response(status, body, *, blind=False):
    if not isinstance(body, dict):
        raise CheckFailure("原生业务验收只接受JSON对象")
    if 200 <= status < 300:
        if (
            set(body) != ENVELOPE
            or type(body["code"]) is not int
            or body["code"] not in (0, 200, 201)
            or body["success"] is not True
            or body["status_code"] != status
            or not isinstance(body["msg"], str)
        ):
            raise CheckFailure("原生成功响应信封不符合固定合同，拒绝丢弃额外字段")
        if blind and (body["code"] != 0 or body["msg"] != "成功"):
            raise CheckFailure("盲审响应元数据不是固定原生成功值")
        data = body["data"]
        if data is None:
            return {}
        if not isinstance(data, dict):
            raise CheckFailure("原生业务成功数据必须是对象")
        return data
    if set(body) == ENVELOPE:
        if body["data"] not in (None, {}) or body["success"] is not False:
            raise CheckFailure("拒绝响应不得携带业务数据")
        return body
    if set(body) == {"detail"} and isinstance(body["detail"], str) and len(body["detail"]) <= 512:
        return body
    raise CheckFailure("原生拒绝响应结构不符合固定合同")


def probe_statement(sql, params):
    """Compile only exact reviewed probes; no SQL or identifier comes from candidates.

    Relation locks, catalog checks and reads share one read-only transaction. This
    prevents a candidate swapping a checked physical table for a privileged view.
    """
    if sql not in {IDENTITY_SQL, EMPTY_SQL, TEAM_SQL, MEMBER_SQL, INVITE_SQL}:
        raise CheckFailure("不允许候选指定数据库探针SQL")
    needs_id = sql in {TEAM_SQL, MEMBER_SQL, INVITE_SQL}
    if (
        not isinstance(params, tuple)
        or len(params) != int(needs_id)
        or any(type(value) is not int or not 0 < value < 2**31 for value in params)
    ):
        raise CheckFailure("数据库探针只接受一个有界整数ID或空参数")
    settings = (
        "BEGIN READ ONLY; SET LOCAL search_path = pg_catalog; "
        "SET LOCAL statement_timeout = '3000ms'; SET LOCAL lock_timeout = '1000ms'; "
        "SET LOCAL row_security = off; SET LOCAL enable_indexscan = off; "
        "SET LOCAL enable_indexonlyscan = off; SET LOCAL enable_bitmapscan = off; "
    )
    if sql == IDENTITY_SQL:
        query = (
            "SELECT pg_catalog.current_database() AS database, oid::pg_catalog.int8 AS database_oid "
            "FROM pg_catalog.pg_database WHERE datname = pg_catalog.current_database()"
        )
        return settings + "SELECT pg_catalog.json_agg(q) FROM (" + query + ") q; COMMIT;"
    table = {
        EMPTY_SQL: "rnd_contest_team",
        TEAM_SQL: "rnd_contest_team",
        MEMBER_SQL: "rnd_contest_membership",
        INVITE_SQL: "rnd_contest_invitation",
    }[sql]
    checks = []
    for column, kind in TABLE_COLUMNS[table].items():
        checks.append(
            "EXISTS (SELECT 1 FROM pg_catalog.pg_attribute a "
            "JOIN pg_catalog.pg_type t ON t.oid=a.atttypid "
            "JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace "
            f"WHERE a.attrelid=c.oid AND a.attname='{column}' AND a.attnum>0 "
            f"AND NOT a.attisdropped AND t.typname='{kind}' AND tn.nspname='pg_catalog' "
            "AND t.typtype='b')"
        )
    valid = (
        "SELECT 1 FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n "
        "ON n.oid=c.relnamespace "
        f"WHERE n.nspname='public' AND c.relname='{table}' AND c.relkind='r' "
        "AND c.relpersistence='p' AND NOT c.relispartition "
        "AND NOT c.relrowsecurity AND NOT c.relforcerowsecurity AND " + " AND ".join(checks)
    )
    guard = (
        f"LOCK TABLE public.{table} IN ACCESS SHARE MODE; DO $oracle$ BEGIN "
        f"IF NOT EXISTS ({valid}) THEN RAISE EXCEPTION 'untrusted physical table'; "
        "END IF; END; $oracle$ LANGUAGE plpgsql; "
    )
    query = sql.replace("FROM " + table, "FROM ONLY public." + table).replace(
        "count(*)", "pg_catalog.count(*)"
    )
    if needs_id:
        query = query.replace("%s", str(params[0]) + "::pg_catalog.int4")
    # Bound server-side text serialization as well as controller-side bytes.
    # Returning one extra character preserves detection of oversized values.
    if sql == TEAM_SQL:
        query = query.replace(
            "capacity, name, submission_title",
            "capacity, pg_catalog.left(name,121) AS name, "
            "pg_catalog.left(submission_title,201) AS submission_title",
        )
    elif sql == INVITE_SQL:
        query = query.replace(
            "id, code_hash, status",
            "id, pg_catalog.left(code_hash,65) AS code_hash, pg_catalog.left(status,21) AS status",
        )
    query += " LIMIT 101"
    return (
        settings + guard + "SELECT COALESCE(pg_catalog.json_agg(q),'[]'::pg_catalog.json) "
        "FROM (" + query + ") q; COMMIT;"
    )


class ContestOracleAdapter:
    def __init__(
        self, base_url, preview_token, sandbox, timeout=120, *, bootstrap=True, client_factory=None
    ):
        host = urlsplit(base_url).hostname or ""
        match = re.fullmatch(r"([0-9]+)-" + re.escape(sandbox.id) + r"\.proxy\.localhost", host)
        if not match:
            raise CheckFailure("业务验收只访问本次私有沙箱预览")
        self.base_url = preview_url(base_url, sandbox.id, int(match[1]))
        if not isinstance(preview_token, str) or not 0 < len(preview_token) <= 16384:
            raise CheckFailure("本次业务验收缺少有界私有预览令牌")
        self.sandbox = sandbox
        self.timeout = min(max(float(timeout), 1), 120)
        self.deadline = time.monotonic() + 300
        self._preview_token = preview_token
        self._factory = client_factory or httpx.Client
        self._tokens = {}
        self._captures = {}
        self._budget = CaptureBudget({"native-contest": self._captures})
        self._lock = threading.Lock()
        self._calls = 0
        self._closed = False
        self.actor_ids = {}
        if bootstrap:
            try:
                self.bootstrap()
            except BaseException:
                self.close()
                raise

    def _remaining(self):
        if self._closed or time.monotonic() >= self.deadline:
            raise CheckFailure("原生业务验收已关闭或超过总期限")
        return min(self.timeout, self.deadline - time.monotonic())

    def _request(self, method, path, body=None, *, token=None, form=False):
        HttpStep.loopback_path(path)
        with self._lock:
            self._calls += 1
            if self._calls > 100:
                raise CheckFailure("原生业务验收超过请求数预算")
        headers = {"x-daytona-preview-token": self._preview_token, "accept-encoding": "identity"}
        if token is not None:
            headers["authorization"] = "Bearer " + token
        options = {}
        if body is not None:
            if form:
                HttpStep.bounded_form(body)
                options["data"] = body
            else:
                if len(json.dumps(body).encode()) > 65536:
                    raise CheckFailure("原生业务请求超过预算")
                options["json"] = body
        # Independent clients avoid cookie/auth leakage and provide independent
        # concurrent network connections for final-slot acceptance.
        try:
            with self._factory(
                base_url=self.base_url,
                trust_env=False,
                follow_redirects=False,
                timeout=min(15, self._remaining()),
            ) as client:
                with client.stream(method, path, headers=headers, **options) as response:
                    if (
                        response.headers.get("content-encoding", "identity").strip().lower()
                        != "identity"
                    ):
                        raise CheckFailure("原生业务HTTP响应必须使用identity编码")
                    raw = bytearray()
                    for block in response.iter_raw():
                        self._remaining()
                        if len(block) > MAX_HTTP_BYTES - len(raw):
                            raise CheckFailure("原生业务HTTP响应超过2MB预算")
                        raw.extend(block)
                    status = response.status_code
        except httpx.HTTPError:
            raise CheckFailure("原生业务验收HTTP传输失败") from None
        self._remaining()
        return status, normalized_response(status, _decode(raw), blind="/review/" in path)

    def _success(self, method, path, body=None, *, token=None, form=False):
        status, value = self._request(method, path, body, token=token, form=form)
        if status not in (200, 201):
            raise CheckFailure("原生合成身份准备失败，未使用管理员身份代替")
        return value

    def _login(self, username, password):
        value = self._success("GET", "/system/auth/captcha/get")
        key = value.get("key")
        self._budget.store(self._captures, "captcha-key", key)
        if not isinstance(key, str) or not key:
            raise CheckFailure("原生验证码键无效")
        if self._remaining() <= 0.31:
            raise CheckFailure("原生认证剩余期限不足")
        time.sleep(0.31)
        self._success("POST", "/system/auth/captcha/slider/complete", {"captcha_key": key})
        value = self._success(
            "POST",
            "/system/auth/login",
            {"username": username, "password": password, "captcha_key": key},
            form=True,
        )
        token = value.get("access_token")
        self._budget.store(self._captures, "login-token", token)
        if (
            not isinstance(token, str)
            or not token
            or any(ord(c) < 33 or ord(c) > 126 for c in token)
        ):
            raise CheckFailure("原生认证令牌无效")
        return token

    @staticmethod
    def _record_id(value):
        value = value.get("id")
        if type(value) is not int or not 0 < value < 2**31:
            raise CheckFailure("原生创建响应缺少有界身份ID")
        return value

    def bootstrap(self):
        if self.actor_ids or self._tokens:
            raise CheckFailure("拒绝在同一适配器重复创建身份")
        admin = self._login("super", "123456")
        roles = {}
        for kind in ("student", "reviewer"):
            value = self._success(
                "POST",
                "/system/role/create",
                {
                    "name": "RND contest " + kind,
                    "code": "rnd_contest_" + kind,
                    "status": 0,
                    "order": 1,
                    "data_scope": 1,
                },
                token=admin,
            )
            roles[kind] = self._record_id(value)
        for actor in ACTORS:
            username = "rnd" + uuid.uuid4().hex[:20]
            password = "RND-" + uuid.uuid4().hex[:20] + "!"
            kind = "reviewer" if actor == "reviewer" else "student"
            value = self._success(
                "POST",
                "/system/user/create",
                {
                    "username": username,
                    "password": password,
                    "name": "Synthetic " + actor,
                    "status": 0,
                    "is_superuser": False,
                    "role_ids": [roles[kind]],
                },
                token=admin,
            )
            user_id = self._record_id(value)
            token = self._login(username, password)
            info = self._success("GET", "/system/user/current/info", token=token)
            if (
                info.get("id") != user_id
                or info.get("is_superuser") is not False
                or {row.get("code") for row in info.get("roles", [])} != {"rnd_contest_" + kind}
            ):
                raise CheckFailure("原生合成账号身份或角色未被真实认证确认")
            self._budget.store(self._captures, actor + "-token", token)
            self._tokens[actor] = token
            self.actor_ids[actor] = user_id
        if len(set(self.actor_ids.values())) != len(ACTORS):
            raise CheckFailure("原生合成账号身份重复")
        self._captures.pop("login-token", None)
        self._captures.pop("captcha-key", None)

    def http(self, actor, method, path, payload=None):
        if not path.startswith("/rnd/contest/") or method not in {"GET", "POST"}:
            raise CheckFailure("业务断言越过固定竞赛端点")
        if actor != "anonymous" and actor not in self._tokens:
            raise CheckFailure("业务断言缺少独立原生身份")
        return self._request(method, path, payload, token=self._tokens.get(actor))

    def probe(self, sql, params):
        statement = probe_statement(sql, params)
        argv = pg_verifier_argv(statement)
        command, path = redirected_command(argv)
        result = control_exec(self.sandbox, command, min(self._remaining(), 10))
        if result.exit_code != 0:
            raise CheckFailure("独立PostgreSQL表结构或物理读取失败")
        raw = read_command_output(
            self.sandbox, path, min(self._remaining(), 10), MAX_PROBE_BYTES + 1
        )
        if not isinstance(raw, str) or len(raw.encode()) > MAX_PROBE_BYTES:
            raise CheckFailure("独立PostgreSQL证据超过字节预算")
        rows = _decode(raw)
        if (
            not isinstance(rows, list)
            or len(rows) > 100
            or any(not isinstance(row, dict) for row in rows)
        ):
            raise CheckFailure("独立PostgreSQL证据结构无效")
        return rows

    def close(self):
        self._closed = True
        self._tokens.clear()
        self._captures.clear()
        self._preview_token = ""
