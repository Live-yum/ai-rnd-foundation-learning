"""Real installed SDK shape plus local bootstrap HTTP contracts; no cloud calls."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
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

    monkeypatch.setattr(socket, "getaddrinfo", no_network)
    monkeypatch.setattr(socket.socket, "connect", no_network)
    settings.daytona_api_key = SecretStr("local-test-key")
    settings.daytona_target = "local"
    client = client_for(settings)
    assert not hasattr(client, "close"), "Pinned SDK contract changed; review the transport adapter"
    assert callable(client._api_client.close)
    assert callable(client._toolbox_api_client.close)
    close_client(client)


def test_transport_cleanup_attempts_all_and_does_not_hide_the_original_failure():
    client = SimpleNamespace(_http_client=Mock(), _api_client=Mock(), _toolbox_api_client=Mock())
    client._http_client.close.side_effect = RuntimeError("local cleanup fixture")
    original = ValueError("original snapshot failure")
    with pytest.raises(ValueError, match="original snapshot") as caught:
        try:
            raise original
        finally:
            close_client(client)
    assert caught.value is original and "RuntimeError" in original.__notes__[0]
    client._api_client.close.assert_called_once()
    client._toolbox_api_client.close.assert_called_once()


def test_transport_failure_after_success_still_fails_the_operation():
    client = SimpleNamespace(_api_client=Mock())
    client._api_client.close.side_effect = RuntimeError("local cleanup fixture")
    with pytest.raises(RuntimeError, match="传输资源关闭失败"):
        close_client(client)
