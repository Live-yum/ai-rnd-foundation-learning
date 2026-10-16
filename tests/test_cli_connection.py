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


@pytest.mark.parametrize(
    "status,receipt,headline",
    [
        (
            "SOURCE_READY",
            {"execution": "source-candidate", "generation_status": "partial"},
            "生成未完成，部分源码已保留",
        ),
        (
            "SOURCE_READY",
            {"execution": "source-candidate", "generation_status": "complete"},
            "源码已保留，未经运行验证",
        ),
        (
            "SOURCE_READY",
            {
                "execution": "source-candidate",
                "generation_status": "partial",
                "verification_status": "failed",
            },
            "验证失败，源码已保留",
        ),
        ("SOURCE_READY", {}, "成果已保留，运行验收状态待核实"),
        ("READY", {}, "完成"),
        (
            "READY",
            {"validation_level": "runtime", "verification_status": "failed"},
            "验证失败，源码已保留",
        ),
        (
            "SOURCE_READY",
            {"validation_level": "runtime", "delivery_kind": "partial"},
            "部分成果已通过运行验收，完整需求仍未完成",
        ),
        (
            "SOURCE_READY",
            {"runtime_verified": True, "delivery_kind": "partial"},
            "部分成果已通过运行验收，完整需求仍未完成",
        ),
        (
            "SOURCE_READY",
            {"validation_level": "source", "generation_status": "partial"},
            "生成未完成，部分源码已保留",
        ),
        (
            "SOURCE_READY",
            {"validation_level": "source", "runtime_verified": True, "delivery_kind": "partial"},
            "源码已保留，未经运行验证",
        ),
        (
            "SOURCE_READY",
            {
                "validation_level": "runtime",
                "verification_status": "failed",
                "generation_status": "partial",
                "delivery_kind": "partial",
            },
            "验证失败，源码已保留",
        ),
        (
            "SOURCE_READY",
            {"execution": "source-candidate", "runtime_verified": True, "delivery_kind": "partial"},
            "源码已保留，未经运行验证",
        ),
        (
            "SOURCE_READY",
            {"execution": "managed-runtime", "delivery_kind": "partial"},
            "成果已保留，运行验收状态待核实",
        ),
        (
            "SOURCE_READY",
            {"validation_level": "runtime", "runtime_verified": False},
            "源码已保留，未经运行验证",
        ),
        (
            "READY",
            {"validation_level": "runtime", "verification_status": "passed"},
            "完成",
        ),
    ],
)
def test_chat_delivery_headline_matches_candidate_evidence(
    monkeypatch, settings, status, receipt, headline
):
    settings.prepare()
    (settings.data_dir / "access-token").write_text("local-test-token", encoding="utf-8")
    monkeypatch.setattr(cli, "Settings", lambda: settings)

    def handler(request):
        return httpx.Response(200, json={"status": status, "result": receipt})

    monkeypatch.setattr(
        cli.httpx, "Client", partial(httpx.Client, transport=httpx.MockTransport(handler))
    )
    result = CliRunner().invoke(cli.app, ["chat", "--run", "saved-run"])
    assert result.exit_code == 0, result.output
    assert f"{headline}。下载命令：uv run rnd download saved-run" in result.output
    if headline != "完成":
        assert not any(line.startswith("完成。下载命令") for line in result.output.splitlines())
    else:
        assert result.output.splitlines()[-1] == "完成。下载命令：uv run rnd download saved-run"
    assert "这是原生源码导出" not in result.output
    if headline.startswith("部分成果已通过"):
        assert "运行验收仅覆盖本次部分交付范围" in result.output
        assert "尚未通过运行验收" not in result.output
        assert "源码候选" not in result.output
    elif headline.startswith(("验证失败", "生成未完成", "源码已保留")):
        assert "这是源码候选，尚未通过运行验收" in result.output
        assert "部分成果已通过运行验收" not in result.output
    elif "待核实" in headline:
        assert "不能确认已通过运行验收" in result.output
        assert "部分成果已通过运行验收" not in result.output
