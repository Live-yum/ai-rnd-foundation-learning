import httpx
import pytest

from workbench import business_probe as probe


@pytest.mark.parametrize(
    "violation", [None, "role", "identity", "global_admin", "menus", "registration_denied"]
)
def test_public_registration_is_anonymous_and_requires_native_default_role(monkeypatch, violation):
    original_client = httpx.Client
    clients, registered, logins = [], [], []

    def handler(request):
        if request.url.path == "/system/user/register":
            assert "authorization" not in request.headers
            import json

            body = json.loads(request.content)
            assert body["is_superuser"] is True and body["role_ids"] == [1]
            registered.append(True)
            if violation == "registration_denied":
                return httpx.Response(409, json={"code": 409})
            data = {"id": 8}
        elif request.url.path == "/business/configuration":
            assert request.headers["Authorization"] == "Bearer synthetic-test-token"
            data = {
                "actor": {
                    "id": "9" if violation == "identity" else "8",
                    "role": "manager" if violation == "role" else "employee",
                },
                "can_manage_roles": False,
            }
        else:
            assert request.url.path == "/system/user/current/info"
            data = {
                "is_superuser": violation == "global_admin",
                "menus": [] if violation == "menus" else [{"id": 10}],
            }
        return httpx.Response(200, json={"code": 200, "data": data})

    def factory(**kwargs):
        client = original_client(**kwargs, transport=httpx.MockTransport(handler))
        clients.append(client)
        return client

    def login(*args):
        logins.append(args)
        return "synthetic-test-token"

    monkeypatch.setattr(probe.httpx, "Client", factory)
    monkeypatch.setattr(probe, "login", login)
    if violation:
        with pytest.raises(AssertionError):
            probe.register_fastapi_actor(
                "http://127.0.0.1", "syntheticuser", "SyntheticPass123!", []
            )
        assert all(client.is_closed for client in clients)
    else:
        identifier, actor = probe.register_fastapi_actor(
            "http://127.0.0.1", "syntheticuser", "SyntheticPass123!", []
        )
        assert identifier == "8"
        actor.close()
    assert registered == [True]
    assert len(logins) == (0 if violation == "registration_denied" else 1)


@pytest.mark.parametrize(
    "violation",
    [None, "role", "identity", "global_admin", "permissions", "menus", "registration_denied"],
)
def test_yudao_registration_requires_native_anonymous_default_membership(monkeypatch, violation):
    import json

    original_client = httpx.Client
    clients = []

    def handler(request):
        if request.url.path == "/admin-api/system/auth/register":
            assert "authorization" not in request.headers
            assert request.headers["tenant-id"] == "1"
            body = json.loads(request.content)
            assert body["roleIds"] == [1] and body["roles"] == ["super_admin"]
            if violation == "registration_denied":
                return httpx.Response(200, json={"code": 403})
            data = {"userId": 8}
        elif request.url.path.endswith("/me"):
            data = {
                "id": "9" if violation == "identity" else "8",
                "roles": ["manager" if violation == "role" else "employee"],
            }
        else:
            assert request.url.path == "/admin-api/system/auth/get-permission-info"
            data = {
                "roles": ["super_admin"] if violation == "global_admin" else ["rnd_employee"],
                "permissions": ["*:*:*"] if violation == "permissions" else ["infra:rnd:query"],
                "menus": [] if violation == "menus" else [{"id": 20}],
            }
        return httpx.Response(200, json={"code": 0, "data": data})

    def factory(**kwargs):
        client = original_client(**kwargs, transport=httpx.MockTransport(handler))
        clients.append(client)
        return client

    monkeypatch.setattr(probe.httpx, "Client", factory)
    monkeypatch.setattr(probe, "login", lambda *args: "synthetic-test-token")
    if violation:
        with pytest.raises(AssertionError):
            probe.register_yudao_actor("http://127.0.0.1", "syntheticuser", "Synthetic123!", [])
    else:
        identifier, actor = probe.register_yudao_actor(
            "http://127.0.0.1", "syntheticuser", "Synthetic123!", []
        )
        assert identifier == "8"
        actor.close()
    assert all(client.is_closed for client in clients)
