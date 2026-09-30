"""Real installed SDK shape plus local bootstrap HTTP contracts; no cloud calls."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
import urllib3
from pydantic import SecretStr

from scripts.daytona_bootstrap import configure_personal_region
from workbench.sandbox import client_for, close_client

ORG = "717b182c-a636-45f0-893c-37499a1b9e32"
HEADERS = {"Authorization": "Bearer local-test-only", "X-Daytona-Organization-ID": ORG}


def organization(region=None):
    return {"id": ORG, "personal": True, "defaultRegionId": region}


@pytest.mark.parametrize("current", [None, "", "local"])
def test_region_initialization_uses_signed_local_api_and_confirms_write(current):
    seen = []

    def handler(request):
        seen.append(request)
        assert request.url.host == "127.0.0.1" and request.url.port == 3000
        assert request.headers["Authorization"] == HEADERS["Authorization"]
        assert request.headers["X-Daytona-Organization-ID"] == ORG
        if request.method == "PATCH":
            assert request.url.path == f"/api/organizations/{ORG}/default-region"
            assert json.loads(request.content) == {"defaultRegionId": "local"}
            return httpx.Response(204)
        assert request.method == "GET" and request.url.path == "/api/organizations"
        return httpx.Response(200, json=[organization("local")])

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        configure_personal_region(client, HEADERS, organization(current))
    assert [request.method for request in seen] == (
        ["GET"] if current == "local" else ["PATCH", "GET"]
    )


@pytest.mark.parametrize(
    "change", [{"defaultRegionId": "us"}, {"personal": False}, {"id": "../other"}]
)
def test_other_region_nonpersonal_or_malformed_organization_never_written(change):
    client = Mock()
    with pytest.raises(ValueError):
        configure_personal_region(client, HEADERS, organization() | change)
    client.patch.assert_not_called()
    client.get.assert_not_called()


@pytest.mark.parametrize("status", [401, 403, 500])
def test_region_auth_or_server_failure_propagates(status):
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(status))
    ) as client:
        with pytest.raises(httpx.HTTPStatusError):
            configure_personal_region(client, HEADERS, organization())


@pytest.mark.parametrize(
    "rows", [[], [organization()], [organization("local"), organization("local")]]
)
def test_region_is_not_ready_until_server_confirms_exact_organization(rows):
    def handler(request):
        return httpx.Response(204) if request.method == "PATCH" else httpx.Response(200, json=rows)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError, match="未保存"):
            configure_personal_region(client, HEADERS, organization())


def test_actual_installed_sdk_transports_can_be_closed_without_a_network_request(
    settings, monkeypatch
):
    import socket

    def no_network(*args, **kwargs):
        raise AssertionError("SDK construction/transport cleanup must not use a network")

    # Production client construction runs inside clean_env()'s isolated child.
    # Mirror that boundary instead of inheriting the test runner's HTTP/SOCKS proxy.
    for variable in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setattr(socket, "getaddrinfo", no_network)
    monkeypatch.setattr(socket.socket, "connect", no_network)
    settings.daytona_api_key = SecretStr("local-test-key")
    settings.daytona_target = "local"
    client = client_for(settings)
    assert not hasattr(client, "close"), "Pinned SDK contract changed; review the transport adapter"
    assert client._http_client.is_closed is False
    managers, pools = [], []
    for api in (client._api_client, client._toolbox_api_client):
        assert not hasattr(api, "close")
        manager = api.rest_client.pool_manager
        managers.append(manager)
        # Construct real pools without opening sockets. Retain references so GC
        # cannot accidentally make a broken explicit cleanup look successful.
        pools.extend(
            manager.connection_from_url(url)
            for url in ("http://127.0.0.1:3000", "http://127.0.0.1:3001")
        )
        assert len(manager.pools) == 2
    close_client(client)
    assert client._http_client.is_closed is True
    assert all(len(manager.pools) == 0 for manager in managers)
    assert all(pool.pool is None for pool in pools)
    close_client(client)  # Repeat cleanup is safe and remains entirely local.


def test_transport_cleanup_attempts_all_and_does_not_hide_the_original_failure():
    managers = [urllib3.PoolManager(), urllib3.PoolManager()]
    pools = [manager.connection_from_url("http://127.0.0.1:3000") for manager in managers]
    client = SimpleNamespace(
        _http_client=Mock(),
        _api_client=SimpleNamespace(rest_client=SimpleNamespace(pool_manager=managers[0])),
        _toolbox_api_client=SimpleNamespace(rest_client=SimpleNamespace(pool_manager=managers[1])),
    )
    client._http_client.close.side_effect = RuntimeError("local cleanup fixture")
    original = ValueError("original snapshot failure")
    with pytest.raises(ValueError, match="original snapshot") as caught:
        try:
            raise original
        finally:
            close_client(client)
    assert caught.value is original and "RuntimeError" in original.__notes__[0]
    assert all(pool.pool is None for pool in pools)
    assert all(len(manager.pools) == 0 for manager in managers)


def test_transport_failure_after_success_still_fails_the_operation():
    client = SimpleNamespace(_http_client=Mock())
    client._http_client.close.side_effect = RuntimeError("local cleanup fixture")
    with pytest.raises(RuntimeError, match="传输资源关闭失败"):
        close_client(client)


def test_pool_failure_does_not_prevent_other_pool_cleanup(monkeypatch):
    manager = urllib3.PoolManager()
    first = manager.connection_from_url("http://127.0.0.1:3000")
    second = manager.connection_from_url("http://127.0.0.1:3001")
    original_close = first.close
    monkeypatch.setattr(first, "close", Mock(side_effect=OSError("local fixture")))
    client = SimpleNamespace(
        _api_client=SimpleNamespace(rest_client=SimpleNamespace(pool_manager=manager))
    )
    with pytest.raises(RuntimeError, match="传输资源关闭失败"):
        close_client(client)
    assert second.pool is None and len(manager.pools) == 0
    original_close()
