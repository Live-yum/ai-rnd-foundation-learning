# workbench/capability_contest_oracle.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.extension_oracles.contest`、`workbench.capability_contracts`、`workbench.capability_isolation`、`workbench.capability_stack`、`workbench.capability_verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_decode`（L51–L67）：接收`raw`。 控制顺序：L67抛异常，停止当前正常路径。 调用`json.loads`、`(_ for _ in ()).throw`、`ValueError`、`CheckFailure`。 返回路径：L61的`json.loads( raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(V…`。
- `_decode.pairs`（L52–L58）：接收`items`。 控制顺序：L54遍历`items`；L55按`key in result`分支；L56抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L58的`result`。
- `normalized_response`（L70–L97）：接收`status`、`body`、`blind`。 控制顺序：L71按`not isinstance(body, dict)`分支；L72抛异常，停止当前正常路径；L73按`200 <= status < 300`分支；L74按`set(body) != ENVELOPE or type(body["code"]) is not int or body["code"] not in (0, 200…`分支；L82抛异常，停止当前正常路径；L83按`blind and (body["code"] != 0 or body["msg"] != "成功")`分支；L84抛异常，停止当前正常路径；L86按`data is None`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`CheckFailure`、`set`、`type`、`len`。 返回路径：L87的`{}`；L90的`data`；L94的`body`。
- `probe_statement`（L100–L177）：接收`sql`、`params`。 源码说明：Compile only exact reviewed probes; no SQL or identifier comes from candidates. Relation locks, catalog checks and reads share one read-only transaction. This prevents a candidate swapping a checked p。 控制顺序：L106按`sql not in {IDENTITY_SQL, EMPTY_SQL, TEAM_SQL, MEMBER_SQL, INVITE_SQL}`分支；L107抛异常，停止当前正常路径；L109按`not isinstance(params, tuple) or len(params) != int(needs_id) or any(type(value) is n…`分支；L114抛异常，停止当前正常路径；L121按`sql == IDENTITY_SQL`分支；L134遍历`TABLE_COLUMNS[table].items()`；L158按`needs_id`分支；L162按`sql == TEAM_SQL`分支。后续分支沿下方源码相同行号继续阅读。 调用`CheckFailure`、`isinstance`、`len`、`int`、`any`、`type`、`TABLE_COLUMNS[table].items`、`checks.append`、`" AND ".join`等。 返回路径：L126的`settings + "SELECT pg_catalog.json_agg(q) FROM (" + query + ") q; COMMIT;"`；L174的`settings + guard + "SELECT COALESCE(pg_catalog.json_agg(q),'[]'::pg_catalog.json) " "FROM …`。
- `ContestOracleAdapter`（L180–L384）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ContestOracleAdapter.__init__`（L181–L208）：接收`base_url`、`preview_token`、`sandbox`、`timeout`、`bootstrap`、`client_factory`。 控制顺序：L186按`not match`分支；L187抛异常，停止当前正常路径；L189按`not isinstance(preview_token, str) or not 0 < len(preview_token) <= 16384`分支；L190抛异常，停止当前正常路径；L203按`bootstrap`分支；L208抛异常，停止当前正常路径。 调用`urlsplit`、`re.fullmatch`、`re.escape`、`CheckFailure`、`preview_url`、`int`、`isinstance`、`len`、`min`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ContestOracleAdapter._remaining`（L210–L213）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L211按`self._closed or time.monotonic() >= self.deadline`分支；L212抛异常，停止当前正常路径。 调用`time.monotonic`、`CheckFailure`、`min`。 返回路径：L213的`min(self.timeout, self.deadline - time.monotonic())`。
- `ContestOracleAdapter._request`（L215–L258）：接收`method`、`path`、`body`、`token`、`form`。 控制顺序：L219按`self._calls > 100`分支；L220抛异常，停止当前正常路径；L222按`token is not None`分支；L225按`body is not None`分支；L226按`form`分支；L230按`len(json.dumps(body).encode()) > 65536`分支；L231抛异常，停止当前正常路径；L243按`response.headers.get("content-encoding", "identity").strip().lower() != "identity"`分支。后续分支沿下方源码相同行号继续阅读。 调用`HttpStep.loopback_path`、`CheckFailure`、`HttpStep.bounded_form`、`len`、`json.dumps(body).encode`、`json.dumps`、`self._factory`、`min`、`self._remaining`等。 返回路径：L258的`status, normalized_response(status, _decode(raw), blind="/review/" in path)`。
- `ContestOracleAdapter._success`（L260–L264）：接收`method`、`path`、`body`、`token`、`form`。 控制顺序：L262按`status not in (200, 201)`分支；L263抛异常，停止当前正常路径。 调用`self._request`、`CheckFailure`。 返回路径：L264的`value`。
- `ContestOracleAdapter._login`（L266–L290）：接收`username`、`password`。 控制顺序：L270按`not isinstance(key, str) or not key`分支；L271抛异常，停止当前正常路径；L272按`self._remaining() <= 0.31`分支；L273抛异常，停止当前正常路径；L284按`not isinstance(token, str) or not token or any(ord(c) < 33 or ord(c) > 126 for c in t…`分支；L289抛异常，停止当前正常路径。 调用`self._success`、`value.get`、`self._budget.store`、`isinstance`、`CheckFailure`、`self._remaining`、`time.sleep`、`any`、`ord`。 返回路径：L290的`token`。
- `ContestOracleAdapter._record_id`（L293–L297）：接收`value`。 控制顺序：L295按`type(value) is not int or not 0 < value < 2**31`分支；L296抛异常，停止当前正常路径。 调用`value.get`、`type`、`CheckFailure`。 返回路径：L297的`value`。
- `ContestOracleAdapter.bootstrap`（L299–L350）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L300按`self.actor_ids or self._tokens`分支；L301抛异常，停止当前正常路径；L304遍历`("student", "reviewer")`；L318遍历`ACTORS`；L338按`info.get("id") != user_id or info.get("is_superuser") is not False or {row.get("code"…`分支；L343抛异常，停止当前正常路径；L347按`len(set(self.actor_ids.values())) != len(ACTORS)`分支；L348抛异常，停止当前正常路径。 调用`CheckFailure`、`self._login`、`self._success`、`self._record_id`、`uuid.uuid4`、`info.get`、`row.get`、`self._budget.store`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ContestOracleAdapter.http`（L352–L357）：接收`actor`、`method`、`path`、`payload`。 控制顺序：L353按`not path.startswith("/rnd/contest/") or method not in {"GET", "POST"}`分支；L354抛异常，停止当前正常路径；L355按`actor != "anonymous" and actor not in self._tokens`分支；L356抛异常，停止当前正常路径。 调用`path.startswith`、`CheckFailure`、`self._request`、`self._tokens.get`。 返回路径：L357的`self._request(method, path, payload, token=self._tokens.get(actor))`。
- `ContestOracleAdapter.probe`（L359–L378）：接收`sql`、`params`。 控制顺序：L364按`result.exit_code != 0`分支；L365抛异常，停止当前正常路径；L369按`not isinstance(raw, str) or len(raw.encode()) > MAX_PROBE_BYTES`分支；L370抛异常，停止当前正常路径；L372按`not isinstance(rows, list) or len(rows) > 100 or any(not isinstance(row, dict) for ro…`分支；L377抛异常，停止当前正常路径。 调用`probe_statement`、`pg_verifier_argv`、`redirected_command`、`control_exec`、`min`、`self._remaining`、`CheckFailure`、`read_command_output`、`isinstance`等。 返回路径：L378的`rows`。
- `ContestOracleAdapter.close`（L380–L384）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self._tokens.clear`、`self._captures.clear`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/capability_contest_oracle.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L384。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16039`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_contest_oracle.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cebefd783721c7a2ede199a62b17787178682a6c817a5651da307e7022b257ef"} -->
````python
# workbench/capability_contest_oracle.py
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
````
