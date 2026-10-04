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
