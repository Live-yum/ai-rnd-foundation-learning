# tests/test_cli_connection.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_offline_cli_fails_before_prompts_with_start_instructions`（L23–L48）：接收`monkeypatch`、`settings`、`args`。 控制顺序：L39断言`result.exit_code == 1`；L40断言`"无法连接本机平台" in result.output`；L41断言`"http://127.0.0.1:8000" in result.output`；L42断言`"uv run rnd start" in result.output`；L43断言`"另一个终端" in result.output`；L44断言`"模板编号" not in result.output`；L45断言`"项目名称" not in result.output`；L46断言`not isinstance(result.exception, httpx.ConnectError)`。后续分支沿下方源码相同行号继续阅读。 调用`settings.prepare`、`(settings.data_dir / "access-token").write_text`、`monkeypatch.setattr`、`httpx.Client`、`httpx.MockTransport`、`monkeypatch.chdir`、`CliRunner().invoke`、`CliRunner`、`isinstance`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_offline_cli_fails_before_prompts_with_start_instructions.refused`（L29–L31）：接收`request`。 控制顺序：L31抛异常，停止当前正常路径。 调用`requests.append`、`httpx.ConnectError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cli_checks_health_and_handles_later_disconnect`（L52–L78）：接收`monkeypatch`、`settings`、`disconnect`。 控制顺序：L73断言`[(r.method, r.url.path) for r in requests] == [ ("GET", "/health"), ("GET", "/runs/sa…`；L77断言`result.exit_code == int(disconnect)`；L78断言`("uv run rnd start" if disconnect else "READY") in result.output`。 调用`settings.prepare`、`(settings.data_dir / "access-token").write_text`、`monkeypatch.setattr`、`partial`、`httpx.MockTransport`、`CliRunner().invoke`、`CliRunner`、`int`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cli_checks_health_and_handles_later_disconnect.handler`（L59–L67）：接收`request`。 控制顺序：L61断言`request.headers["Authorization"] == "Bearer local-test-token"`；L62断言`request.url.port == 8123`；L63按`request.url.path == "/health"`分支；L65按`disconnect`分支；L66抛异常，停止当前正常路径。 调用`requests.append`、`httpx.Response`、`httpx.ConnectError`。 返回路径：L64的`httpx.Response(200, json={"status": "ok"})`；L67的`httpx.Response(200, json={"status": "READY"})`。
- `test_chat_delivery_headline_matches_candidate_evidence`（L162–L192）：接收`monkeypatch`、`settings`、`status`、`receipt`、`headline`。 控制顺序：L176断言`result.exit_code == 0`；L177断言`f"{headline}。下载命令：uv run rnd download saved-run" in result.output`；L178按`headline != "完成"`分支；L179断言`not any(line.startswith("完成。下载命令") for line in result.output.splitlines())`；L181断言`result.output.splitlines()[-1] == "完成。下载命令：uv run rnd download saved-run"`；L182断言`"这是原生源码导出" not in result.output`；L183按`headline.startswith("部分成果已通过")`分支；L184断言`"运行验收仅覆盖本次部分交付范围" in result.output`。后续分支沿下方源码相同行号继续阅读。 调用`settings.prepare`、`(settings.data_dir / "access-token").write_text`、`monkeypatch.setattr`、`partial`、`httpx.MockTransport`、`CliRunner().invoke`、`CliRunner`、`any`、`line.startswith`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chat_delivery_headline_matches_candidate_evidence.handler`（L169–L170）：接收`request`。 调用`httpx.Response`。 返回路径：L170的`httpx.Response(200, json={"status": status, "result": receipt})`。

</details>

**创建路径：** `tests/test_cli_connection.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L192。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7375`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_cli_connection.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "91f3840cff90dcd869ae1ed44f81f93e555ffa317069a9a6e661798c13dcb5e2"} -->
````python
# tests/test_cli_connection.py
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
````
