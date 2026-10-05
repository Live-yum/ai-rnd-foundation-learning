# tests/test_capability_contest_adapter.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.extension_oracles.contest`、`workbench`、`workbench.capability_verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `envelope`（L20–L21）：接收`data`、`**changes`。 返回路径：L21的`{"code": 0, "msg": "成功", "data": data, "status_code": 200, "success": True, **changes}`。
- `factory`（L24–L30）：接收`responder`、`clients`。 返回路径：L30的`create`。
- `factory.create`（L25–L28）：接收`**kwargs`。 控制顺序：L26按`clients is not None`分支。 调用`clients.append`、`httpx.Client`、`httpx.MockTransport`。 返回路径：L28的`httpx.Client(**kwargs, transport=httpx.MockTransport(responder))`。
- `instance`（L33–L46）：接收`responder`、`**kwargs`。 调用`httpx.Response`、`httpx.ByteStream`、`json.dumps(envelope({"id": 1})).encode`、`json.dumps`、`envelope`、`adapter.ContestOracleAdapter`、`SimpleNamespace`、`factory`。 返回路径：L39的`adapter.ContestOracleAdapter( "http://8000-owned.proxy.localhost", "preview-token", Simple…`。
- `test_envelope_does_not_discard_extra_fields_or_blind_metadata`（L49–L58）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L50断言`adapter.normalized_response(200, envelope({"id": 1}), blind=True) == {"id": 1}`；L51遍历`( envelope({}, student_name="secret"), envelope({}, msg="Student …`。 调用`adapter.normalized_response`、`envelope`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_success_never_normalizes_invalid_native_envelope`（L64–L66）：接收`body`。 调用`pytest.raises`、`adapter.normalized_response`、`pytest.mark.parametrize`、`envelope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_denied_responses_cannot_carry_business_records`（L69–L72）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L70断言`adapter.normalized_response(403, {"detail": "Forbidden"}) == {"detail": "Forbidden"}`。 调用`adapter.normalized_response`、`pytest.raises`、`envelope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_rejects_compression_large_or_ambiguous_json`（L84–L93）：接收`encoding`、`raw`。 调用`instance`、`pytest.raises`、`value.http`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_rejects_compression_large_or_ambiguous_json.respond`（L85–L89）：接收`request`。 控制顺序：L86断言`request.headers["accept-encoding"] == "identity"`。 调用`httpx.Response`、`httpx.ByteStream`。 返回路径：L87的`httpx.Response( 200, headers={"content-encoding": encoding}, stream=httpx.ByteStream(raw) …`。
- `test_http_uses_distinct_clients_no_cookie_inheritance_and_fixed_origin`（L96–L120）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L112断言`seen[0].headers["authorization"] == "Bearer captain-token"`；L113断言`"authorization" not in seen[1].headers`；L114断言`seen[0].headers["x-daytona-preview-token"] == "preview-token"`；L120断言`value._tokens == {} and value._preview_token == ""`。 调用`instance`、`value.http`、`pytest.raises`、`value.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_uses_distinct_clients_no_cookie_inheritance_and_fixed_origin.respond`（L99–L106）：接收`request`。 控制顺序：L101断言`"cookie" not in request.headers`。 调用`seen.append`、`httpx.Response`、`httpx.ByteStream`、`json.dumps(envelope({"id": 1})).encode`、`json.dumps`、`envelope`。 返回路径：L102的`httpx.Response( 200, headers={"set-cookie": "leak=admin"}, stream=httpx.ByteStream(json.du…`。
- `test_native_bootstrap_uses_real_form_auth_and_distinct_nonadmin_roles`（L123–L178）：接收`monkeypatch`。 控制顺序：L171断言`set(value.actor_ids) == set(adapter.ACTORS)`；L172断言`len(set(value.actor_ids.values())) == 5`；L173断言`len(forms) == 6 and forms[0]["password"] == ["123456"]`；L174断言`len(value._tokens) == 5`；L175断言`"super" not in value._tokens.values()`。 调用`monkeypatch.setattr`、`adapter.ContestOracleAdapter`、`SimpleNamespace`、`factory`、`set`、`len`、`value.actor_ids.values`、`value._tokens.values`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_bootstrap_uses_real_form_auth_and_distinct_nonadmin_roles.respond`（L127–L163）：接收`request`。 控制顺序：L134按`path.endswith("/captcha/get")`分支；L136按`path.endswith("/captcha/slider/complete")`分支；L137断言`body == {"captcha_key": "synthetic-key"}`；L139按`path.endswith("/auth/login")`分支；L144断言`form["captcha_key"] == ["synthetic-key"]`；L146按`path.endswith("/role/create")`分支；L147断言`request.headers["authorization"] == "Bearer super"`；L150按`path.endswith("/user/create")`分支。后续分支沿下方源码相同行号继续阅读。 调用`request.headers.get("content-type", "").startswith`、`request.headers.get`、`json.loads`、`path.endswith`、`parse_qs`、`request.content.decode`、`forms.append`、`len`、`request.headers["authorization"].removeprefix`等。 返回路径：L163的`httpx.Response(200, stream=httpx.ByteStream(json.dumps(envelope(data)).encode()))`。
- `test_probe_rejects_candidate_sql_and_noninteger_parameters`（L192–L194）：接收`sql`、`params`。 调用`pytest.raises`、`adapter.probe_statement`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_physical_probe_checks_and_reads_inside_one_locked_readonly_transaction`（L198–L214）：接收`sql`。 控制顺序：L200断言`result.startswith("BEGIN READ ONLY;")`；L201断言`"SET LOCAL search_path = pg_catalog" in result`；L202断言`"SET LOCAL statement_timeout = '3000ms'" in result`；L203断言`"LOCK TABLE public." in result`；L204断言`"c.relkind='r'" in result and "c.relpersistence='p'" in result`；L205断言`"NOT c.relrowsecurity" in result and "NOT c.relforcerowsecurity" in result`；L206断言`"tn.nspname='pg_catalog'" in result and "t.typtype='b'" in result`；L207断言`"SET LOCAL row_security = off" in result`。后续分支沿下方源码相同行号继续阅读。 调用`adapter.probe_statement`、`result.startswith`、`result.index`、`result.endswith`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pg_probe_bounds_output_and_uses_independent_readonly_identity`（L217–L244）：接收`monkeypatch`。 控制顺序：L230断言`value.probe(IDENTITY_SQL, ()) == [{"database": "rnd_product", "database_oid": 42}]`；L232断言`"127.0.0.1" in serialized and "rnd_product" in serialized`；L233断言`"rnd_verify" in serialized and "RLIMIT_FSIZE" in serialized`；L234断言`"PGPASSWORD" in serialized and "SET ROLE" not in serialized`；L235断言`"enable_indexscan=off" in serialized and "row_security=off" in serialized`；L236断言`"-X" in serialized and "ON_ERROR_STOP=1" in serialized`。 调用`monkeypatch.setattr`、`commands.append`、`SimpleNamespace`、`instance`、`value.probe`、`str`、`pytest.raises`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_contest_adapter.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L244。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9207`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_contest_adapter.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e892d75c31cd8e0f5e27ffc69ecf7daad8374a04665e700db36f0dd4c380e337"} -->
````python
# tests/test_capability_contest_adapter.py
"""Trusted transport unit simulations; never counted as native integration evidence."""

import json
from types import SimpleNamespace

import httpx
import pytest

from scripts.extension_oracles.contest import (
    EMPTY_SQL,
    IDENTITY_SQL,
    INVITE_SQL,
    MEMBER_SQL,
    TEAM_SQL,
)
from workbench import capability_contest_oracle as adapter
from workbench.capability_verification import CheckFailure


def envelope(data=None, **changes):
    return {"code": 0, "msg": "成功", "data": data, "status_code": 200, "success": True, **changes}


def factory(responder, clients=None):
    def create(**kwargs):
        if clients is not None:
            clients.append(kwargs)
        return httpx.Client(**kwargs, transport=httpx.MockTransport(responder))

    return create


def instance(responder=None, **kwargs):
    responder = responder or (
        lambda request: httpx.Response(
            200, stream=httpx.ByteStream(json.dumps(envelope({"id": 1})).encode())
        )
    )
    return adapter.ContestOracleAdapter(
        "http://8000-owned.proxy.localhost",
        "preview-token",
        SimpleNamespace(id="owned"),
        bootstrap=False,
        client_factory=factory(responder),
        **kwargs,
    )


def test_envelope_does_not_discard_extra_fields_or_blind_metadata():
    assert adapter.normalized_response(200, envelope({"id": 1}), blind=True) == {"id": 1}
    for changed in (
        envelope({}, student_name="secret"),
        envelope({}, msg="Student Alice"),
        envelope({}, code=200),
        envelope({}, success=False),
    ):
        with pytest.raises(CheckFailure):
            adapter.normalized_response(200, changed, blind=True)


@pytest.mark.parametrize(
    "body", [envelope({}, code=True), envelope({}, status_code=201), envelope([1]), {"id": 1}, []]
)
def test_success_never_normalizes_invalid_native_envelope(body):
    with pytest.raises(CheckFailure):
        adapter.normalized_response(200, body)


def test_denied_responses_cannot_carry_business_records():
    assert adapter.normalized_response(403, {"detail": "Forbidden"}) == {"detail": "Forbidden"}
    with pytest.raises(CheckFailure):
        adapter.normalized_response(403, envelope({"student": "Alice"}, success=False))


@pytest.mark.parametrize(
    "encoding,raw",
    [
        ("gzip", b"small compressed payload"),
        ("identity", b"x" * (adapter.MAX_HTTP_BYTES + 1)),
        ("identity", b'{"code":0,"code":1}'),
        ("identity", b'{"value":NaN}'),
    ],
)
def test_http_rejects_compression_large_or_ambiguous_json(encoding, raw):
    def respond(request):
        assert request.headers["accept-encoding"] == "identity"
        return httpx.Response(
            200, headers={"content-encoding": encoding}, stream=httpx.ByteStream(raw)
        )

    value = instance(respond)
    with pytest.raises(CheckFailure):
        value.http("anonymous", "GET", "/rnd/contest/teams/1")


def test_http_uses_distinct_clients_no_cookie_inheritance_and_fixed_origin():
    seen = []

    def respond(request):
        seen.append(request)
        assert "cookie" not in request.headers
        return httpx.Response(
            200,
            headers={"set-cookie": "leak=admin"},
            stream=httpx.ByteStream(json.dumps(envelope({"id": 1})).encode()),
        )

    value = instance(respond)
    value._tokens["captain"] = "captain-token"
    value.http("captain", "GET", "/rnd/contest/teams/1")
    value.http("anonymous", "GET", "/rnd/contest/teams/1")
    assert seen[0].headers["authorization"] == "Bearer captain-token"
    assert "authorization" not in seen[1].headers
    assert seen[0].headers["x-daytona-preview-token"] == "preview-token"
    with pytest.raises(CheckFailure):
        value.http("anonymous", "GET", "https://elsewhere.invalid/path")
    value.close()
    with pytest.raises(CheckFailure):
        value.http("anonymous", "GET", "/rnd/contest/teams/1")
    assert value._tokens == {} and value._preview_token == ""


def test_native_bootstrap_uses_real_form_auth_and_distinct_nonadmin_roles(monkeypatch):
    monkeypatch.setattr(adapter.time, "sleep", lambda _: None)
    users, roles, forms = {}, {}, []

    def respond(request):
        path = request.url.path
        body = (
            json.loads(request.content)
            if request.headers.get("content-type", "").startswith("application/json")
            else None
        )
        if path.endswith("/captcha/get"):
            data = {"key": "synthetic-key"}
        elif path.endswith("/captcha/slider/complete"):
            assert body == {"captcha_key": "synthetic-key"}
            data = None
        elif path.endswith("/auth/login"):
            from urllib.parse import parse_qs

            form = parse_qs(request.content.decode())
            forms.append(form)
            assert form["captcha_key"] == ["synthetic-key"]
            data = {"access_token": form["username"][0]}
        elif path.endswith("/role/create"):
            assert request.headers["authorization"] == "Bearer super"
            roles[len(roles) + 1] = body["code"]
            data = {"id": len(roles)}
        elif path.endswith("/user/create"):
            assert body["is_superuser"] is False
            data = {"id": len(users) + 10}
            users[body["username"]] = {**body, **data}
        elif path.endswith("/user/current/info"):
            user = users[request.headers["authorization"].removeprefix("Bearer ")]
            data = {
                "id": user["id"],
                "is_superuser": False,
                "roles": [{"code": roles[user["role_ids"][0]]}],
            }
        else:
            raise AssertionError(path)
        return httpx.Response(200, stream=httpx.ByteStream(json.dumps(envelope(data)).encode()))

    value = adapter.ContestOracleAdapter(
        "http://8000-owned.proxy.localhost",
        "preview",
        SimpleNamespace(id="owned"),
        client_factory=factory(respond),
    )
    assert set(value.actor_ids) == set(adapter.ACTORS)
    assert len(set(value.actor_ids.values())) == 5
    assert len(forms) == 6 and forms[0]["password"] == ["123456"]
    assert len(value._tokens) == 5
    assert "super" not in value._tokens.values()
    with pytest.raises(CheckFailure):
        value.bootstrap()
    value.close()


@pytest.mark.parametrize(
    "sql,params",
    [
        ("SELECT 1", ()),
        (TEAM_SQL, ("1; DROP TABLE x",)),
        (TEAM_SQL, (True,)),
        (TEAM_SQL, (2**31,)),
        (TEAM_SQL, ()),
        (EMPTY_SQL, (1,)),
    ],
)
def test_probe_rejects_candidate_sql_and_noninteger_parameters(sql, params):
    with pytest.raises(CheckFailure):
        adapter.probe_statement(sql, params)


@pytest.mark.parametrize("sql", [EMPTY_SQL, TEAM_SQL, MEMBER_SQL, INVITE_SQL])
def test_physical_probe_checks_and_reads_inside_one_locked_readonly_transaction(sql):
    result = adapter.probe_statement(sql, () if sql == EMPTY_SQL else (12,))
    assert result.startswith("BEGIN READ ONLY;")
    assert "SET LOCAL search_path = pg_catalog" in result
    assert "SET LOCAL statement_timeout = '3000ms'" in result
    assert "LOCK TABLE public." in result
    assert "c.relkind='r'" in result and "c.relpersistence='p'" in result
    assert "NOT c.relrowsecurity" in result and "NOT c.relforcerowsecurity" in result
    assert "tn.nspname='pg_catalog'" in result and "t.typtype='b'" in result
    assert "SET LOCAL row_security = off" in result
    assert "SET LOCAL enable_indexscan = off" in result
    assert "SET LOCAL enable_indexonlyscan = off" in result
    assert "SET LOCAL enable_bitmapscan = off" in result
    assert "FROM ONLY public." in result
    assert result.index("LOCK TABLE") < result.index("RAISE EXCEPTION") < result.index("json_agg")
    assert "LIMIT 101" in result and result.endswith("COMMIT;")
    assert "%s" not in result


def test_pg_probe_bounds_output_and_uses_independent_readonly_identity(monkeypatch):
    commands = []
    monkeypatch.setattr(
        adapter,
        "control_exec",
        lambda sandbox, argv, timeout: commands.append(argv) or SimpleNamespace(exit_code=0),
    )
    monkeypatch.setattr(
        adapter,
        "read_command_output",
        lambda *args: '[{"database":"rnd_product","database_oid":42}]',
    )
    value = instance()
    assert value.probe(IDENTITY_SQL, ()) == [{"database": "rnd_product", "database_oid": 42}]
    serialized = str(commands[0])
    assert "127.0.0.1" in serialized and "rnd_product" in serialized
    assert "rnd_verify" in serialized and "RLIMIT_FSIZE" in serialized
    assert "PGPASSWORD" in serialized and "SET ROLE" not in serialized
    assert "enable_indexscan=off" in serialized and "row_security=off" in serialized
    assert "-X" in serialized and "ON_ERROR_STOP=1" in serialized
    monkeypatch.setattr(
        adapter, "read_command_output", lambda *args: "x" * (adapter.MAX_PROBE_BYTES + 1)
    )
    with pytest.raises(CheckFailure, match="字节预算"):
        value.probe(IDENTITY_SQL, ())
    monkeypatch.setattr(adapter, "read_command_output", lambda *args: json.dumps([{}] * 101))
    with pytest.raises(CheckFailure, match="结构无效"):
        value.probe(IDENTITY_SQL, ())
````
