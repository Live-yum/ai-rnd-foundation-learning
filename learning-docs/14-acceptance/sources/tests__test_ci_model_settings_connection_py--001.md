# tests/test_ci_model_settings_connection.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_model_settings_connection`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `completion`（L17–L34）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`httpx.Response`。 返回路径：L18的`httpx.Response( 200, json={ "id": "test", "object": "chat.completion", "created": 0, "mode…`。
- `test_env_settings_save_and_one_probe`（L37–L59）：接收`monkeypatch`。 控制顺序：L54断言`result["code"] == "passed"`；L55断言`result["settings_lifecycle"] == "passed"`；L56断言`result["real_service"] is False`；L57断言`result["inference_requests"] == len(seen) == 1`；L58断言`result["catalog_requests"] == 0`；L59断言`not any(value in json.dumps(result) for value in VALUES.values())`。 调用`monkeypatch.setenv`、`acceptance`、`httpx.MockTransport`、`len`、`any`、`json.dumps`、`VALUES.values`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_env_settings_save_and_one_probe.handle`（L42–L51）：接收`request`。 控制顺序：L44断言`request.headers["authorization"] == "Bearer " + VALUES["API_KEY"]`；L45断言`str(request.url) == "https://provider.example/v1/chat/completions"`；L47断言`body["model"] == VALUES["MODE"]`；L48断言`body.get("max_tokens", body.get("max_completion_tokens")) == 128`；L49断言`body["stream"] is False`；L50断言`all(value <= 20 for value in request.extensions["timeout"].values())`。 调用`seen.append`、`str`、`json.loads`、`body.get`、`all`、`request.extensions["timeout"].values`、`completion`。 返回路径：L51的`completion()`。
- `test_unsupported_catalog_does_not_fail_successful_inference`（L63–L78）：接收`status`。 控制顺序：L71断言`result["code"] == "passed"`；L72断言`result["catalog"]["ok"] is False`；L73断言`result["catalog"]["http_status"] == status`；L74按`status in (404, 405)`分支；L75断言`result["catalog"]["code"] == "discovery_unsupported"`；L76断言`result["probe"]["ok"] is True`；L77断言`result["inference_requests"] == result["catalog_requests"] == 1`；L78断言`seen == ["GET", "POST"]`。 调用`acceptance`、`httpx.MockTransport`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unsupported_catalog_does_not_fail_successful_inference.handle`（L66–L68）：接收`request`。 调用`seen.append`、`httpx.Response`、`completion`。 返回路径：L68的`httpx.Response(status) if request.method == "GET" else completion()`。
- `test_failure_never_retries_or_redirects`（L82–L97）：接收`status`。 控制顺序：L94断言`result["code"] == "probe_failed"`；L95断言`result["inference_requests"] == len(seen) == 1`；L96断言`result["catalog_requests"] == 0`；L97断言`VALUES["API_KEY"] not in json.dumps(result)`。 调用`acceptance`、`httpx.MockTransport`、`len`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_never_retries_or_redirects.handle`（L85–L91）：接收`request`。 调用`seen.append`、`str`、`httpx.Response`。 返回路径：L87的`httpx.Response( status, headers={"location": "https://other.example"}, text="provider erro…`。
- `test_static_configuration_failures_do_not_network`（L110–L116）：接收`values`、`code`。 控制顺序：L115断言`result["code"] == code`；L116断言`result["inference_requests"] == result["catalog_requests"] == 0`。 调用`acceptance`、`httpx.MockTransport`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_static_configuration_failures_do_not_network.forbidden`（L111–L112）：接收`request`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_hard_budget_and_exact_destination`（L119–L131）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L131断言`len(calls) == 1`。 调用`BoundedTransport`、`httpx.MockTransport`、`calls.append`、`httpx.Response`、`httpx.Request`、`transport.handle_request`、`pytest.raises`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_receipts_exclude_raw_provider_strings`（L134–L136）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L136断言`result == {"ok": False, "code": "other_failure"}`。 调用`safe_result`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_is_bounded_and_credentials_are_step_scoped`（L139–L165）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L146断言`trigger == {"push": {"branches": ["fix/model-settings-env-connection"]}}`；L147断言`workflow["permissions"] == {"contents": "read"}`；L149断言`job["timeout-minutes"] == 10`；L150断言`"github.run_attempt == 1" in job["if"]`；L151断言`"github.event.created == true" in job["if"]`；L152断言`"github.event.before == '0000000000000000000000000000000000000000'" in job["if"]`；L153断言`"contains(github.event.head_commit.message, '[settings-connection-acceptance-20261015…`；L157断言`"env" not in job and "env" not in workflow`。后续分支沿下方源码相同行号继续阅读。 调用`yaml.safe_load`、`Path(".github/workflows/model-settings-connection.yml").read_text`、`Path`、`workflow.get`、`enumerate`、`str`、`len`、`any`、`step.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_dotenv_and_saved_credentials_are_private_and_removed`（L168–L189）：接收`monkeypatch`。 控制顺序：L188断言`result["code"] == "passed"`；L189断言`paths and not paths[0].exists()`。 调用`monkeypatch.setattr`、`acceptance`、`httpx.MockTransport`、`completion`、`paths[0].exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_dotenv_and_saved_credentials_are_private_and_removed.settings`（L178–L184）：接收`**kwargs`。 控制顺序：L181按`os.name == "posix"`分支；L182断言`stat.S_IMODE(dotenv.stat().st_mode) == 0o600`；L183断言`stat.S_IMODE(dotenv.parent.stat().st_mode) == 0o700`。 调用`Path`、`paths.append`、`stat.S_IMODE`、`dotenv.stat`、`dotenv.parent.stat`、`original`。 返回路径：L184的`original(**kwargs)`。
- `test_tls_failure_is_static_and_never_retried`（L192–L208）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L205断言`result["code"] == "probe_failed"`；L206断言`result["probe"]["code"] == "tls_certificate_verification_failed"`；L207断言`result["inference_requests"] == len(calls) == 1`；L208断言`VALUES["API_KEY"] not in json.dumps(result)`。 调用`acceptance`、`httpx.MockTransport`、`len`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_tls_failure_is_static_and_never_retried.handle`（L197–L202）：接收`request`。 控制顺序：L200抛异常，停止当前正常路径；L202抛异常，停止当前正常路径。 调用`calls.append`、`ssl.SSLCertVerificationError`、`httpx.ConnectError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_job_is_independent_and_has_only_fixture_access`（L211–L235）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L218断言`"environment" not in browser and "needs" not in browser`；L219断言`"secrets." not in str(browser)`；L220断言`"API_KEY" not in str(browser)`；L221断言`browser["timeout-minutes"] == 15`；L222断言`"github.run_attempt == 1" in browser["if"]`；L224断言`any(step.get("with", {}).get("node-version") == "22" for step in steps)`；L226断言`"playwright@1.56.1" in commands`；L227断言`"npm ci --prefix ui" in commands and "npm run build --prefix ui" in commands`。后续分支沿下方源码相同行号继续阅读。 调用`yaml.safe_load`、`Path(".github/workflows/model-settings-connection.yml").read_text`、`Path`、`str`、`any`、`step.get("with", {}).get`、`step.get`、`"\n".join`、`upload["with"]["path"].splitlines`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_ci_model_settings_connection.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L235。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9123`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_ci_model_settings_connection.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "723c74fccad23aede32735d411e80cd064ff77dd4ac32a057d9a48d1f25a9012"} -->
````python
# tests/test_ci_model_settings_connection.py
"""Mock-only acceptance contracts; never certify a real provider."""

import json

import httpx
import pytest

from scripts.ci_model_settings_connection import BoundedTransport, acceptance, safe_result

VALUES = {
    "BASE_URL": "https://provider.example/v1/",
    "API_KEY": "dummy-test-secret",
    "MODE": "test-model",
}


def completion():
    return httpx.Response(
        200,
        json={
            "id": "test",
            "object": "chat.completion",
            "created": 0,
            "model": "test-model",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": '{"ok":true}'},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 12, "completion_tokens": 5, "total_tokens": 17},
        },
    )


def test_env_settings_save_and_one_probe(monkeypatch):
    monkeypatch.setenv("API_KEY", "wrong-process-key")
    monkeypatch.setenv("BASE_URL", "https://wrong.example")
    seen = []

    def handle(request):
        seen.append(request)
        assert request.headers["authorization"] == "Bearer " + VALUES["API_KEY"]
        assert str(request.url) == "https://provider.example/v1/chat/completions"
        body = json.loads(request.content)
        assert body["model"] == VALUES["MODE"]
        assert body.get("max_tokens", body.get("max_completion_tokens")) == 128
        assert body["stream"] is False
        assert all(value <= 20 for value in request.extensions["timeout"].values())
        return completion()

    result = acceptance(VALUES, transport=httpx.MockTransport(handle))
    assert result["code"] == "passed"
    assert result["settings_lifecycle"] == "passed"
    assert result["real_service"] is False
    assert result["inference_requests"] == len(seen) == 1
    assert result["catalog_requests"] == 0
    assert not any(value in json.dumps(result) for value in VALUES.values())


@pytest.mark.parametrize("status", [404, 405, 501])
def test_unsupported_catalog_does_not_fail_successful_inference(status):
    seen = []

    def handle(request):
        seen.append(request.method)
        return httpx.Response(status) if request.method == "GET" else completion()

    result = acceptance(VALUES, transport=httpx.MockTransport(handle), discover=True)
    assert result["code"] == "passed"
    assert result["catalog"]["ok"] is False
    assert result["catalog"]["http_status"] == status
    if status in (404, 405):
        assert result["catalog"]["code"] == "discovery_unsupported"
    assert result["probe"]["ok"] is True
    assert result["inference_requests"] == result["catalog_requests"] == 1
    assert seen == ["GET", "POST"]


@pytest.mark.parametrize("status", [301, 307, 401, 429, 500])
def test_failure_never_retries_or_redirects(status):
    seen = []

    def handle(request):
        seen.append(str(request.url))
        return httpx.Response(
            status,
            headers={"location": "https://other.example"},
            text="provider error " + VALUES["API_KEY"],
        )

    result = acceptance(VALUES, transport=httpx.MockTransport(handle))
    assert result["code"] == "probe_failed"
    assert result["inference_requests"] == len(seen) == 1
    assert result["catalog_requests"] == 0
    assert VALUES["API_KEY"] not in json.dumps(result)


@pytest.mark.parametrize(
    "values,code",
    [
        ({**VALUES, "API_KEY": ""}, "missing_configuration"),
        ({**VALUES, "MODE": ""}, "missing_configuration"),
        ({**VALUES, "BASE_URL": "http://provider.example/v1"}, "https_required"),
        ({**VALUES, "BASE_URL": "http://127.0.0.1:9000/v1"}, "https_required"),
        ({**VALUES, "BASE_URL": "https://user:secret@provider.example"}, "invalid_configuration"),
    ],
)
def test_static_configuration_failures_do_not_network(values, code):
    def forbidden(request):
        pytest.fail("network must not be attempted")

    result = acceptance(values, transport=httpx.MockTransport(forbidden), discover=True)
    assert result["code"] == code
    assert result["inference_requests"] == result["catalog_requests"] == 0


def test_transport_hard_budget_and_exact_destination():
    calls = []
    transport = BoundedTransport(
        "https://provider.example/v1",
        inner=httpx.MockTransport(lambda request: calls.append(request) or httpx.Response(200)),
    )
    first = httpx.Request("POST", "https://provider.example/v1/chat/completions")
    transport.handle_request(first)
    with pytest.raises(httpx.RequestError):
        transport.handle_request(first)
    with pytest.raises(httpx.RequestError):
        transport.handle_request(httpx.Request("POST", "https://other.example/chat/completions"))
    assert len(calls) == 1


def test_receipts_exclude_raw_provider_strings():
    result = safe_result({"ok": False, "code": VALUES["API_KEY"], "models": [VALUES["API_KEY"]]})
    assert result == {"ok": False, "code": "other_failure"}


def test_workflow_is_bounded_and_credentials_are_step_scoped():
    from pathlib import Path

    import yaml

    workflow = yaml.safe_load(Path(".github/workflows/model-settings-connection.yml").read_text())
    trigger = workflow.get("on", workflow.get(True))
    assert trigger == {"push": {"branches": ["fix/model-settings-env-connection"]}}
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["connection"]
    assert job["timeout-minutes"] == 10
    assert "github.run_attempt == 1" in job["if"]
    assert "github.event.created == true" in job["if"]
    assert "github.event.before == '0000000000000000000000000000000000000000'" in job["if"]
    assert (
        "contains(github.event.head_commit.message, '[settings-connection-acceptance-20261015]')"
        in job["if"]
    )
    assert "env" not in job and "env" not in workflow
    steps = job["steps"]
    secret_steps = [i for i, step in enumerate(steps) if "secrets.API_KEY" in str(step)]
    assert len(secret_steps) == 1
    index = secret_steps[0]
    assert any("pytest" in step.get("run", "") for step in steps[:index])
    assert any("uv sync --locked" in step.get("run", "") for step in steps[:index])
    assert steps[index]["run"] == "uv run --no-sync python -m scripts.ci_model_settings_connection"
    assert "real-model.yml" not in str(workflow)


def test_dotenv_and_saved_credentials_are_private_and_removed(monkeypatch):
    import os
    import stat
    from pathlib import Path

    from scripts import ci_model_settings_connection as module

    original = module.Settings
    paths = []

    def settings(**kwargs):
        dotenv = Path(kwargs["_env_file"])
        paths.append(dotenv.parent)
        if os.name == "posix":
            assert stat.S_IMODE(dotenv.stat().st_mode) == 0o600
            assert stat.S_IMODE(dotenv.parent.stat().st_mode) == 0o700
        return original(**kwargs)

    monkeypatch.setattr(module, "Settings", settings)
    result = acceptance(VALUES, transport=httpx.MockTransport(lambda request: completion()))
    assert result["code"] == "passed"
    assert paths and not paths[0].exists()


def test_tls_failure_is_static_and_never_retried():
    import ssl

    calls = []

    def handle(request):
        calls.append(request)
        try:
            raise ssl.SSLCertVerificationError("untrusted certificate " + VALUES["API_KEY"])
        except ssl.SSLCertVerificationError as exc:
            raise httpx.ConnectError("TLS failed", request=request) from exc

    result = acceptance(VALUES, transport=httpx.MockTransport(handle))
    assert result["code"] == "probe_failed"
    assert result["probe"]["code"] == "tls_certificate_verification_failed"
    assert result["inference_requests"] == len(calls) == 1
    assert VALUES["API_KEY"] not in json.dumps(result)


def test_browser_job_is_independent_and_has_only_fixture_access():
    from pathlib import Path

    import yaml

    workflow = yaml.safe_load(Path(".github/workflows/model-settings-connection.yml").read_text())
    browser = workflow["jobs"]["browser"]
    assert "environment" not in browser and "needs" not in browser
    assert "secrets." not in str(browser)
    assert "API_KEY" not in str(browser)
    assert browser["timeout-minutes"] == 15
    assert "github.run_attempt == 1" in browser["if"]
    steps = browser["steps"]
    assert any(step.get("with", {}).get("node-version") == "22" for step in steps)
    commands = "\n".join(step.get("run", "") for step in steps)
    assert "playwright@1.56.1" in commands
    assert "npm ci --prefix ui" in commands and "npm run build --prefix ui" in commands
    assert "npm ci --prefix tools/node" in commands
    assert "python -m scripts.ci_guided_browser" in commands
    assert "ci_model_settings_connection" not in commands and "ci_real_model" not in commands
    upload = steps[-1]
    assert upload["if"] == "always()"
    paths = upload["with"]["path"].splitlines()
    assert all(path.startswith("reports/guided-browser/") for path in paths)
    assert not any(".env" in path or "input" in path or "config" in path for path in paths)
````
