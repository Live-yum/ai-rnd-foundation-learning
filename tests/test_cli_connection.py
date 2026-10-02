import uuid
from functools import partial

import httpx
import pytest
from typer.testing import CliRunner

from workbench import cli


@pytest.mark.parametrize(
    "args",
    [
        ["chat"],
        ["chat", "--run", "saved-run"],
        ["show", "saved-run"],
        ["retry", "saved-run"],
        ["recommend", "saved-run"],
        ["manual", "saved-run"],
        ["download", str(uuid.UUID(int=1))],
    ],
)
def test_offline_cli_fails_before_prompts_with_start_instructions(monkeypatch, settings, args):
    settings.prepare()
    (settings.data_dir / "access-token").write_text("local-test-token", encoding="utf-8")
    monkeypatch.setattr(cli, "Settings", lambda: settings)
    requests = []

    def refused(request):
        requests.append(request)
        raise httpx.ConnectError("[WinError 10061] Connection refused", request=request)

    connection = httpx.Client(
        base_url="http://127.0.0.1:8000", transport=httpx.MockTransport(refused)
    )
    monkeypatch.setattr(cli.httpx, "Client", lambda **kwargs: connection)
    monkeypatch.chdir(settings.data_dir)
    result = CliRunner().invoke(cli.app, args)
    assert result.exit_code == 1, result.output
    assert "无法连接本机平台" in result.output
    assert "http://127.0.0.1:8000" in result.output
    assert "uv run rnd start" in result.output
    assert "另一个终端" in result.output
    assert "模板编号" not in result.output
    assert "项目名称" not in result.output
    assert not isinstance(result.exception, httpx.ConnectError)
    assert [(r.method, r.url.path) for r in requests] == [("GET", "/health")]
    assert connection.is_closed


@pytest.mark.parametrize("disconnect", [False, True])
def test_cli_checks_health_and_handles_later_disconnect(monkeypatch, settings, disconnect):
    settings.port = 8123
    settings.prepare()
    (settings.data_dir / "access-token").write_text("local-test-token", encoding="utf-8")
    monkeypatch.setattr(cli, "Settings", lambda: settings)
    requests = []

    def handler(request):
        requests.append(request)
        assert request.headers["Authorization"] == "Bearer local-test-token"
        assert request.url.port == 8123
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if disconnect:
            raise httpx.ConnectError("Connection refused", request=request)
        return httpx.Response(200, json={"status": "READY"})

    monkeypatch.setattr(
        cli.httpx, "Client", partial(httpx.Client, transport=httpx.MockTransport(handler))
    )
    result = CliRunner().invoke(cli.app, ["show", "saved-run"])
    assert [(r.method, r.url.path) for r in requests] == [
        ("GET", "/health"),
        ("GET", "/runs/saved-run"),
    ]
    assert result.exit_code == int(disconnect), result.output
    assert ("uv run rnd start" if disconnect else "READY") in result.output
