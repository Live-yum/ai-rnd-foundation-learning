# tests/test_workbench_browser_fixture.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_guided_browser`、`scripts.news_fixture`、`workbench.domain`、`workbench.llm`、`workbench.model_settings`、`workbench.streaming`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fragments`（L34–L45）：接收`value`。 控制顺序：L37遍历`packets`；L38断言`packet.startswith(b"data: ") and packet.endswith(b"\r\n\r\n")`；L39按`packet == b"data: [DONE]\r\n\r\n"`分支；L42断言`item["object"] == "chat.completion.chunk"`。 调用`list`、`stream_packets`、`packet.startswith`、`packet.endswith`、`json.loads`、`packet[6:].decode`、`content.append`、`choice["delta"].get`。 返回路径：L45的`packets, content`。
- `test_browser_provider_holds_real_terminal_bytes_until_a_visible_draft`（L48–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L54遍历`content`；L55按`boundary`分支；L56断言`root_string_prefix(raw, "summary") == STREAM_SUMMARY`；L63抛异常，停止当前正常路径；L66断言`json.loads(raw) == value`；L67断言`len(set(before_release)) >= 3`；L68断言`any(fragment.endswith(r"\ud8") for _, fragment in content)`；L69断言`packets[-1][1] == b"data: [DONE]\r\n\r\n"`。后续分支沿下方源码相同行号继续阅读。 调用`news_requirement`、`fragments`、`root_string_prefix`、`json.loads`、`AssertionError`、`before_release.append`、`len`、`set`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_fixture_preserves_strict_planning_and_review_contracts`（L74–L83）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L79遍历`values`；L83断言`finish["choices"][0]["finish_reason"] == "stop"`。 调用`news_spec`、`fragments`、`schema.model_validate_json`、`"".join`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_provider_packets_pass_the_actual_structured_model_gateway`（L86–L117）：接收`store`。 控制顺序：L113断言`gateway.complete(run, "requirement:fixture", "JSON", {}, Requirement).summary == STRE…`；L117断言`store.transcript(run)["messages"][-1]["validation"] == "validated"`。 调用`SecretStr`、`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`news_requirement`、`b"".join`、`stream_packets`、`ModelGateway`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_provider_packets_pass_the_actual_structured_model_gateway.Bytes`（L98–L101）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_browser_provider_packets_pass_the_actual_structured_model_gateway.Bytes.__iter__`（L99–L101）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L100遍历`range(0, len(raw), 2)`。 调用`range`、`len`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_browser_catalog_fixture_uses_explicit_safe_catalog_responses`（L121–L132）：接收`mode`、`status`。 控制顺序：L125断言`code == status`；L126按`mode == "success"`分支；L127断言`[row["id"] for row in payload["data"]] == CATALOG_MODELS`；L128断言`fixture.status() == { "calls": [{"method": "GET", "path": "/catalog-v1/models"}], "st…`；L132断言`CATALOG_KEY not in json.dumps(payload) + json.dumps(fixture.status())`。 调用`CatalogFixture`、`fixture.arm`、`fixture.response`、`fixture.status`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_catalog_fixture_holds_response_until_browser_releases`（L135–L146）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L141断言`fixture.started.wait(2)`；L142断言`not future.done()`；L143断言`len(fixture.calls) == 1`；L146断言`future.result(timeout=2)[0] == 200`。 调用`CatalogFixture`、`fixture.arm`、`ThreadPoolExecutor`、`executor.submit`、`fixture.started.wait`、`future.done`、`len`、`fixture.release.set`、`future.result`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_catalog_fixture_fails_closed_on_wrong_destination_or_key`（L152–L157）：接收`path`、`key`。 控制顺序：L156断言`fixture.calls == [{"method": "GET", "path": path}]`；L157断言`key not in json.dumps(fixture.status())`。 调用`CatalogFixture`、`pytest.raises`、`fixture.response`、`json.dumps`、`fixture.status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_settings_read_faults_preserve_real_saves_and_manual_retry`（L160–L210）：接收`settings`。 调用`FastAPI`、`register_model_settings_routes`、`SettingsReadControl`、`SettingsReadFixture`、`ModelSettingsRepository`、`asyncio.run`、`exercise`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_settings_read_faults_preserve_real_saves_and_manual_retry.exercise`（L167–L208）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L175遍历`range(100)`；L176按`control.started.is_set()`分支；L179断言`control.started.is_set() and not pending.done()`；L182断言`(await asyncio.wait_for(pending, timeout=2)).json() == original`；L197断言`saved.status_code == 200`；L198断言`saved.json()["default"]["model"] == "manual-model"`；L201断言`failure.status_code == 503`；L202断言`failure.json() == {"detail": SETTINGS_READ_FAILURE}`。后续分支沿下方源码相同行号继续阅读。 调用`httpx.AsyncClient`、`httpx.ASGITransport`、`(await client.get("/settings/models")).json`、`client.get`、`control.arm`、`asyncio.create_task`、`range`、`control.started.is_set`、`asyncio.sleep`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_read_fault_does_not_intercept_real_discovery_validation`（L213–L230）：接收`settings`。 调用`FastAPI`、`register_model_settings_routes`、`SettingsReadControl`、`control.arm`、`asyncio.run`、`exercise`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_read_fault_does_not_intercept_real_discovery_validation.exercise`（L219–L228）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L225断言`response.status_code == 422`；L226断言`not control.started.is_set()`；L227断言`(await client.get("/settings/models")).status_code == 503`；L228断言`(await client.get("/settings/models")).status_code == 200`。 调用`httpx.AsyncClient`、`httpx.ASGITransport`、`SettingsReadFixture`、`client.post`、`control.started.is_set`、`client.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_workbench_browser_fixture.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L230。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9192`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_workbench_browser_fixture.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "acb27f337176669b66fbd219e743564b6d686cd76995823740208ecbe7277432"} -->
````python
# tests/test_workbench_browser_fixture.py
"""The actual Chromium driver lives in scripts/ci_guided_browser.py.

These fast tests guard the explicit fixture's streaming proof and preserved guided
regression independently of optional local Chromium installation.
"""

import asyncio
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi import FastAPI
from pydantic import SecretStr

from scripts.ci_guided_browser import (
    CATALOG_KEY,
    CATALOG_MODELS,
    SETTINGS_READ_FAILURE,
    STREAM_SUMMARY,
    CatalogFixture,
    SettingsReadControl,
    SettingsReadFixture,
    stream_packets,
)
from scripts.news_fixture import news_requirement, news_spec
from workbench.domain import ModelReview, Plan, Requirement
from workbench.llm import ModelGateway
from workbench.model_settings import ModelSettingsRepository, register_model_settings_routes
from workbench.streaming import root_string_prefix


def fragments(value):
    packets = list(stream_packets(value, "explicit-fixture"))
    content = []
    for boundary, packet in packets:
        assert packet.startswith(b"data: ") and packet.endswith(b"\r\n\r\n")
        if packet == b"data: [DONE]\r\n\r\n":
            continue
        item = json.loads(packet[6:].decode("utf-8"))
        assert item["object"] == "chat.completion.chunk"
        choice = item["choices"][0]
        content.append((boundary, choice["delta"].get("content", "")))
    return packets, content


def test_browser_provider_holds_real_terminal_bytes_until_a_visible_draft():
    value = news_requirement()
    value["summary"] = STREAM_SUMMARY
    packets, content = fragments(value)
    raw = ""
    before_release = []
    for boundary, fragment in content:
        if boundary:
            assert root_string_prefix(raw, "summary") == STREAM_SUMMARY
            # A visible summary cannot masquerade as a complete validated object.
            try:
                json.loads(raw)
            except ValueError:
                pass
            else:
                raise AssertionError("Fixture must withhold part of the model JSON")
        raw += fragment
        before_release.append(root_string_prefix(raw, "summary"))
    assert json.loads(raw) == value
    assert len(set(before_release)) >= 3, "The fixture yields genuinely distinct partial text"
    assert any(fragment.endswith(r"\ud8") for _, fragment in content)
    assert packets[-1][1] == b"data: [DONE]\r\n\r\n"
    assert sum(boundary for boundary, _ in packets) == 1
    Requirement.model_validate_json(raw)


def test_browser_fixture_preserves_strict_planning_and_review_contracts():
    values = [
        (news_spec(), Plan),
        ({"summary": "审阅结果", "observations": [], "uncovered_requirements": []}, ModelReview),
    ]
    for value, schema in values:
        packets, content = fragments(value)
        schema.model_validate_json("".join(text for _, text in content))
        finish = json.loads(packets[-2][1][6:])
        assert finish["choices"][0]["finish_reason"] == "stop"


def test_browser_provider_packets_pass_the_actual_structured_model_gateway(store):
    store.settings.base_url = "http://127.0.0.1:8888/v1"
    store.settings.model = "requirements-fixture"
    store.settings.api_key = SecretStr("explicit-ci-only")
    project = store.create_project("Browser fixture", str(uuid.uuid4()))
    run = store.create_run(
        project["id"], {"requirement": "fixture", "template": "python-basic"}, str(uuid.uuid4())
    )["run_id"]
    value = news_requirement()
    value["summary"] = STREAM_SUMMARY
    raw = b"".join(packet for _, packet in stream_packets(value, "requirements-fixture"))

    class Bytes(httpx.SyncByteStream):
        def __iter__(self):
            for offset in range(0, len(raw), 2):
                yield raw[offset : offset + 2]

    gateway = ModelGateway(
        store.settings,
        store,
        httpx.MockTransport(
            lambda _: httpx.Response(
                200, headers={"content-type": "text/event-stream"}, stream=Bytes()
            )
        ),
        streaming=True,
    )
    assert (
        gateway.complete(run, "requirement:fixture", "JSON", {}, Requirement).summary
        == STREAM_SUMMARY
    )
    assert store.transcript(run)["messages"][-1]["validation"] == "validated"


@pytest.mark.parametrize("mode,status", [("success", 200), ("unsupported", 404), ("denied", 401)])
def test_browser_catalog_fixture_uses_explicit_safe_catalog_responses(mode, status):
    fixture = CatalogFixture()
    fixture.arm(mode)
    code, payload = fixture.response("/catalog-v1/models", "Bearer " + CATALOG_KEY)
    assert code == status
    if mode == "success":
        assert [row["id"] for row in payload["data"]] == CATALOG_MODELS
    assert fixture.status() == {
        "calls": [{"method": "GET", "path": "/catalog-v1/models"}],
        "started": True,
    }
    assert CATALOG_KEY not in json.dumps(payload) + json.dumps(fixture.status())


def test_browser_catalog_fixture_holds_response_until_browser_releases():
    fixture = CatalogFixture()
    fixture.arm("success", hold=True)
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fixture.response, "/catalog-v1/models", "Bearer " + CATALOG_KEY)
        try:
            assert fixture.started.wait(2)
            assert not future.done(), "The UI must observe a genuinely pending provider response"
            assert len(fixture.calls) == 1
        finally:
            fixture.release.set()
        assert future.result(timeout=2)[0] == 200


@pytest.mark.parametrize(
    "path,key", [("/wrong-destination/models", CATALOG_KEY), ("/catalog-v1/models", "wrong-key")]
)
def test_browser_catalog_fixture_fails_closed_on_wrong_destination_or_key(path, key):
    fixture = CatalogFixture()
    with pytest.raises(AssertionError):
        fixture.response(path, "Bearer " + key)
    assert fixture.calls == [{"method": "GET", "path": path}]
    assert key not in json.dumps(fixture.status())


def test_browser_settings_read_faults_preserve_real_saves_and_manual_retry(settings):
    app = FastAPI()
    register_model_settings_routes(app, settings, lambda: None)
    control = SettingsReadControl()
    fixture = SettingsReadFixture(app, control)
    repository = ModelSettingsRepository(settings)

    async def exercise():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=fixture), base_url="http://fixture.local"
        ) as client:
            original = (await client.get("/settings/models")).json()
            control.arm("hold")
            pending = asyncio.create_task(client.get("/settings/models"))
            try:
                for _ in range(100):
                    if control.started.is_set():
                        break
                    await asyncio.sleep(0.01)
                assert control.started.is_set() and not pending.done()
            finally:
                control.release.set()
            assert (await asyncio.wait_for(pending, timeout=2)).json() == original

            control.arm("fail")
            # A read failure must not intercept PATCH or fabricate the persisted result.
            saved = await client.patch(
                "/settings/models",
                json={
                    "expected_revision": original["revision"],
                    "default": {
                        "base_url": "http://127.0.0.1:8888/catalog-v1",
                        "model": "manual-model",
                        "api_key": CATALOG_KEY,
                    },
                },
            )
            assert saved.status_code == 200
            assert saved.json()["default"]["model"] == "manual-model"
            persisted = repository.path.read_bytes()
            failure = await client.get("/settings/models")
            assert failure.status_code == 503
            assert failure.json() == {"detail": SETTINGS_READ_FAILURE}
            assert repository.path.read_bytes() == persisted
            retried = await client.get("/settings/models")
            assert retried.status_code == 200 and retried.json() == saved.json()
            assert repository.path.read_bytes() == persisted
            assert CATALOG_KEY not in saved.text + failure.text + retried.text
            assert sum(request["method"] == "PATCH" for request in control.requests) == 1

    asyncio.run(exercise())


def test_browser_read_fault_does_not_intercept_real_discovery_validation(settings):
    app = FastAPI()
    register_model_settings_routes(app, settings, lambda: None)
    control = SettingsReadControl()
    control.arm("fail")

    async def exercise():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=SettingsReadFixture(app, control)),
            base_url="http://fixture.local",
        ) as client:
            response = await client.post("/settings/models/discover", json={})
            assert response.status_code == 422
            assert not control.started.is_set()
            assert (await client.get("/settings/models")).status_code == 503
            assert (await client.get("/settings/models")).status_code == 200

    asyncio.run(exercise())
````
