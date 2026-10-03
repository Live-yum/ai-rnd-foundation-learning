# tests/test_model_connection.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.model_connection`、`workbench.model_settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `configured`（L28–L42）：接收`settings`。 调用`ModelSettingsRepository`、`repository.update`。 返回路径：L42的`repository, saved`。
- `command`（L45–L52）：接收`revision`、`stage`、`**extra`。 调用`ConnectionTestRequest`、`str`、`uuid.uuid4`。 返回路径：L46的`ConnectionTestRequest( stage=stage, expected_revision=revision, request_id=str(uuid.uuid4(…`。
- `completion`（L55–L72）：接收`content`、`finish`。 调用`httpx.Response`。 返回路径：L56的`httpx.Response( 200, json={ "id": "test-probe", "object": "chat.completion", "created": 0,…`。
- `test_probe_uses_saved_effective_profile_one_bounded_call_and_no_project_data`（L75–L103）：接收`settings`、`configured`。 控制顺序：L87断言`result["ok"] and result["code"] == "connected"`；L88断言`result["phase"] == "completed" and result["attempts"] == 1`；L89断言`result["revision"] == saved["revision"] and result["stage"] == "coding"`；L90断言`result["model"] == "saved-coder"`；L91断言`result["usage"]["total_tokens"] == 17`；L92断言`len(seen) == 1`；L93断言`str(seen[0].url) == "https://provider.example/v1/chat/completions"`；L94断言`seen[0].headers["authorization"] == "Bearer " + SECRET`。后续分支沿下方源码相同行号继续阅读。 调用`ModelConnectionTester`、`httpx.MockTransport`、`tester.test`、`command`、`len`、`str`、`json.loads`、`body.get`、`json.dumps(body).lower`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_probe_uses_saved_effective_profile_one_bounded_call_and_no_project_data.handle`（L81–L83）：接收`request`。 调用`seen.append`、`completion`。 返回路径：L83的`completion()`。
- `test_probe_keeps_one_snapshot_when_configuration_changes_during_call`（L106–L120）：接收`settings`、`configured`。 控制顺序：L119断言`result["ok"] and result["revision"] == saved["revision"]`；L120断言`repository.public()["revision"] != result["revision"]`。 调用`ModelConnectionTester(settings, httpx.MockTransport(handle)).test`、`ModelConnectionTester`、`httpx.MockTransport`、`command`、`repository.public`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_probe_keeps_one_snapshot_when_configuration_changes_during_call.handle`（L109–L114）：接收`request`。 控制顺序：L113断言`json.loads(request.content)["model"] == "saved-model"`。 调用`repository.update`、`json.loads`、`completion`。 返回路径：L114的`completion()`。
- `test_http_failures_are_actionable_redacted_and_never_retried`（L134–L155）：接收`settings`、`configured`、`status`、`code`、`retryable`、`caplog`。 控制顺序：L151断言`not result["ok"] and result["code"] == code and result["phase"] == "request"`；L152断言`result["retryable"] is retryable and result["http_status"] == status`；L153断言`len(requests) == result["attempts"] == 1`；L154断言`SECRET not in json.dumps(result) + caplog.text`；L155断言`len(result["trace_id"]) == 32`。 调用`ModelConnectionTester(settings, httpx.MockTransport(handle)).test`、`ModelConnectionTester`、`httpx.MockTransport`、`command`、`len`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_http_failures_are_actionable_redacted_and_never_retried.handle`（L140–L146）：接收`request`。 调用`requests.append`、`httpx.Response`。 返回路径：L142的`httpx.Response( status, headers={"location": "https://unapproved.example/v1"}, json={"erro…`。
- `test_transport_errors_do_not_echo_exception_text`（L161–L173）：接收`settings`、`configured`、`exception`、`code`。 控制顺序：L172断言`result["code"] == code and result["retryable"]`；L173断言`len(calls) == 1 and SECRET not in json.dumps(result)`。 调用`ModelConnectionTester(settings, httpx.MockTransport(handle)).test`、`ModelConnectionTester`、`httpx.MockTransport`、`command`、`len`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_errors_do_not_echo_exception_text.handle`（L165–L167）：接收`request`。 控制顺序：L167抛异常，停止当前正常路径。 调用`calls.append`、`exception`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_model_output_is_not_reported_as_connected`（L185–L193）：接收`settings`、`configured`、`content`、`finish`、`code`。 控制顺序：L192断言`not result["ok"] and result["phase"] == "validation" and result["code"] == code`；L193断言`SECRET not in json.dumps(result)`。 调用`ModelConnectionTester( settings, httpx.MockTransport(lambda reque…`、`ModelConnectionTester`、`httpx.MockTransport`、`completion`、`command`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_duplicate_request_is_cached_and_stale_configuration_cannot_call`（L196–L209）：接收`settings`、`configured`。 控制顺序：L204断言`tester.test(request) == first and len(calls) == 1`；L209断言`len(calls) == 1`。 调用`ModelConnectionTester`、`httpx.MockTransport`、`calls.append`、`completion`、`command`、`tester.test`、`len`、`pytest.raises`、`request.model_copy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_concurrent_probe_is_blocked_before_second_model_call`（L212–L233）：接收`settings`、`configured`。 控制顺序：L225断言`started.wait(5)`；L233断言`running.result()["ok"]`。 调用`threading.Event`、`ModelConnectionTester`、`httpx.MockTransport`、`ThreadPoolExecutor`、`executor.submit`、`command`、`started.wait`、`pytest.raises`、`tester.test`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_concurrent_probe_is_blocked_before_second_model_call.handle`（L216–L219）：接收`request`。 控制顺序：L218断言`release.wait(5)`。 调用`started.set`、`release.wait`、`completion`。 返回路径：L219的`completion()`。
- `test_missing_configuration_never_uses_network`（L236–L241）：接收`settings`。 控制顺序：L241断言`result["code"] == "invalid_configuration" and result["attempts"] == 0`。 调用`ModelConnectionTester(settings, httpx.MockTransport(unexpected)).…`、`ModelConnectionTester`、`httpx.MockTransport`、`command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_configuration_never_uses_network.unexpected`（L237–L238）：接收`request`。 控制顺序：L238抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_test_route_requires_auth_origin_saved_revision_and_explicit_cost_confirmation`（L244–L288）：接收`settings`、`configured`、`monkeypatch`。 控制顺序：L262断言`client.post("/settings/models/test", json=body).status_code == 401`；L264断言`client.post( "/settings/models/test", json=body, headers={"origin": "https://evil.exa…`；L270遍历`( {**body, "confirm_cost": False}, {**body, "stage": SECRET}, {**…`；L276断言`response.status_code == 422 and SECRET not in response.text`；L277断言`client.post( "/settings/models/test", json={**body, "expected_revision": "stale"} ).s…`；L283断言`not calls`；L285断言`response.status_code == 200 and response.json()["ok"]`；L286断言`response.headers["cache-control"] == "no-store"`。后续分支沿下方源码相同行号继续阅读。 调用`ModelConnectionTester`、`httpx.MockTransport`、`calls.append`、`completion`、`monkeypatch.setattr`、`FastAPI`、`register_model_settings_routes`、`command(saved["revision"]).model_dump`、`command`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_test_route_requires_auth_origin_saved_revision_and_explicit_cost_confirmation.auth`（L255–L257）：接收`request`。用本机Dex真实签发的JWT访问本机API创建密钥，不伪造token，也不向云身份服务注册账号。 控制顺序：L256按`request.headers.get("authorization") != "Bearer local-test-token"`分支；L257抛异常，停止当前正常路径。 调用`request.headers.get`、`HTTPException`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_model_connection.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L288。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10150`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_model_connection.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "37a936277740d836603f49e430703e9e188447b7a53c761f6fa14562c98a41ff"} -->
````python
# tests/test_model_connection.py
"""Offline connection probes: real adapter, mocked transport, no paid calls."""

import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from workbench.model_connection import (
    ConnectionTestBusy,
    ConnectionTestRequest,
    ModelConnectionTester,
)
from workbench.model_settings import (
    ModelSettingsRepository,
    RevisionConflict,
    register_model_settings_routes,
)

SECRET = "dummy-connection-probe-secret-never-real"


@pytest.fixture
def configured(settings):
    repository = ModelSettingsRepository(settings)
    saved = repository.update(
        {
            "expected_revision": "0",
            "default": {
                "base_url": "https://provider.example/v1",
                "model": "saved-model",
                "api_key": SECRET,
                "max_output_tokens": 8000,
            },
            "stages": {"coding": {"model": "saved-coder"}},
        }
    )
    return repository, saved


def command(revision, stage="default", **extra):
    return ConnectionTestRequest(
        stage=stage,
        expected_revision=revision,
        request_id=str(uuid.uuid4()),
        confirm_cost=True,
        **extra,
    )


def completion(content='{"ok":true}', finish="stop"):
    return httpx.Response(
        200,
        json={
            "id": "test-probe",
            "object": "chat.completion",
            "created": 0,
            "model": "saved-model",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": finish,
                }
            ],
            "usage": {"prompt_tokens": 12, "completion_tokens": 5, "total_tokens": 17},
        },
    )


def test_probe_uses_saved_effective_profile_one_bounded_call_and_no_project_data(
    settings, configured
):
    repository, saved = configured
    seen = []

    def handle(request):
        seen.append(request)
        return completion()

    tester = ModelConnectionTester(settings, httpx.MockTransport(handle))
    result = tester.test(command(saved["revision"], "coding"))
    assert result["ok"] and result["code"] == "connected"
    assert result["phase"] == "completed" and result["attempts"] == 1
    assert result["revision"] == saved["revision"] and result["stage"] == "coding"
    assert result["model"] == "saved-coder"
    assert result["usage"]["total_tokens"] == 17
    assert len(seen) == 1
    assert str(seen[0].url) == "https://provider.example/v1/chat/completions"
    assert seen[0].headers["authorization"] == "Bearer " + SECRET
    body = json.loads(seen[0].content)
    assert body["model"] == "saved-coder"
    assert body.get("max_tokens", body.get("max_completion_tokens")) == 128
    assert body["response_format"] == {"type": "json_object"}
    assert body["stream"] is False
    assert "project" not in json.dumps(body).lower()
    assert SECRET not in json.dumps(result)
    assert repository.public()["revision"] == saved["revision"]
    assert not (settings.data_dir / "workbench.db").exists()


def test_probe_keeps_one_snapshot_when_configuration_changes_during_call(settings, configured):
    repository, saved = configured

    def handle(request):
        repository.update(
            {"expected_revision": saved["revision"], "default": {"model": "next-model"}}
        )
        assert json.loads(request.content)["model"] == "saved-model"
        return completion()

    result = ModelConnectionTester(settings, httpx.MockTransport(handle)).test(
        command(saved["revision"])
    )
    assert result["ok"] and result["revision"] == saved["revision"]
    assert repository.public()["revision"] != result["revision"]


@pytest.mark.parametrize(
    "status,code,retryable",
    [
        (401, "authentication_failed", False),
        (403, "permission_denied", False),
        (404, "model_or_endpoint_not_found", False),
        (429, "rate_limited", True),
        (500, "http_500", True),
        (302, "http_302", False),
    ],
)
def test_http_failures_are_actionable_redacted_and_never_retried(
    settings, configured, status, code, retryable, caplog
):
    _, saved = configured
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(
            status,
            headers={"location": "https://unapproved.example/v1"},
            json={"error": {"message": SECRET}},
        )

    result = ModelConnectionTester(settings, httpx.MockTransport(handle)).test(
        command(saved["revision"])
    )
    assert not result["ok"] and result["code"] == code and result["phase"] == "request"
    assert result["retryable"] is retryable and result["http_status"] == status
    assert len(requests) == result["attempts"] == 1
    assert SECRET not in json.dumps(result) + caplog.text
    assert len(result["trace_id"]) == 32


@pytest.mark.parametrize(
    "exception,code", [(httpx.ReadTimeout, "timeout"), (httpx.ConnectError, "connection_failed")]
)
def test_transport_errors_do_not_echo_exception_text(settings, configured, exception, code):
    _, saved = configured
    calls = []

    def handle(request):
        calls.append(request)
        raise exception(SECRET, request=request)

    result = ModelConnectionTester(settings, httpx.MockTransport(handle)).test(
        command(saved["revision"])
    )
    assert result["code"] == code and result["retryable"]
    assert len(calls) == 1 and SECRET not in json.dumps(result)


@pytest.mark.parametrize(
    "content,finish,code",
    [
        (SECRET, "stop", "invalid_response"),
        ('{"ok":false}', "stop", "invalid_response"),
        ('{"ok":true}', "length", "truncated"),
        ("", "stop", "empty_content"),
    ],
)
def test_invalid_model_output_is_not_reported_as_connected(
    settings, configured, content, finish, code
):
    _, saved = configured
    result = ModelConnectionTester(
        settings, httpx.MockTransport(lambda request: completion(content, finish))
    ).test(command(saved["revision"]))
    assert not result["ok"] and result["phase"] == "validation" and result["code"] == code
    assert SECRET not in json.dumps(result)


def test_duplicate_request_is_cached_and_stale_configuration_cannot_call(settings, configured):
    _, saved = configured
    calls = []
    tester = ModelConnectionTester(
        settings, httpx.MockTransport(lambda request: calls.append(request) or completion())
    )
    request = command(saved["revision"])
    first = tester.test(request)
    assert tester.test(request) == first and len(calls) == 1
    with pytest.raises(RevisionConflict):
        tester.test(request.model_copy(update={"stage": "coding"}))
    with pytest.raises(RevisionConflict):
        tester.test(command("stale"))
    assert len(calls) == 1


def test_concurrent_probe_is_blocked_before_second_model_call(settings, configured):
    _, saved = configured
    started, release = threading.Event(), threading.Event()

    def handle(request):
        started.set()
        assert release.wait(5)
        return completion()

    tester = ModelConnectionTester(settings, httpx.MockTransport(handle))
    with ThreadPoolExecutor(max_workers=1) as executor:
        running = executor.submit(tester.test, command(saved["revision"]))
        try:
            assert started.wait(5)
            with pytest.raises(ConnectionTestBusy):
                tester.test(command(saved["revision"]))
            # Independent service instances must share the same file lock.
            with pytest.raises(ConnectionTestBusy):
                ModelConnectionTester(settings).test(command(saved["revision"]))
        finally:
            release.set()
        assert running.result()["ok"]


def test_missing_configuration_never_uses_network(settings):
    def unexpected(request):
        raise AssertionError("No network permitted")

    result = ModelConnectionTester(settings, httpx.MockTransport(unexpected)).test(command("0"))
    assert result["code"] == "invalid_configuration" and result["attempts"] == 0


def test_test_route_requires_auth_origin_saved_revision_and_explicit_cost_confirmation(
    settings, configured, monkeypatch
):
    _, saved = configured
    calls = []
    tester = ModelConnectionTester(
        settings, httpx.MockTransport(lambda request: calls.append(request) or completion())
    )
    monkeypatch.setattr("workbench.model_connection.ModelConnectionTester", lambda settings: tester)
    app = FastAPI()

    def auth(request: Request):
        if request.headers.get("authorization") != "Bearer local-test-token":
            raise HTTPException(401)

    register_model_settings_routes(app, settings, auth)
    body = command(saved["revision"]).model_dump()
    with TestClient(app) as client:
        assert client.post("/settings/models/test", json=body).status_code == 401
        client.headers["authorization"] = "Bearer local-test-token"
        assert (
            client.post(
                "/settings/models/test", json=body, headers={"origin": "https://evil.example"}
            ).status_code
            == 403
        )
        for invalid in (
            {**body, "confirm_cost": False},
            {**body, "stage": SECRET},
            {**body, "api_key": SECRET},
        ):
            response = client.post("/settings/models/test", json=invalid)
            assert response.status_code == 422 and SECRET not in response.text
        assert (
            client.post(
                "/settings/models/test", json={**body, "expected_revision": "stale"}
            ).status_code
            == 409
        )
        assert not calls
        response = client.post("/settings/models/test", json=body)
        assert response.status_code == 200 and response.json()["ok"]
        assert response.headers["cache-control"] == "no-store"
        assert client.post("/settings/models/test", json=body).json() == response.json()
        assert len(calls) == 1 and SECRET not in response.text
````
