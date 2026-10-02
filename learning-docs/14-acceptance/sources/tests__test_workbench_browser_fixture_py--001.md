# tests/test_workbench_browser_fixture.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_guided_browser`、`scripts.news_fixture`、`workbench.domain`、`workbench.llm`、`workbench.streaming`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fragments`（L20–L31）：接收`value`。 控制顺序：L23遍历`packets`；L24断言`packet.startswith(b"data: ") and packet.endswith(b"\r\n\r\n")`；L25按`packet == b"data: [DONE]\r\n\r\n"`分支；L28断言`item["object"] == "chat.completion.chunk"`。 调用`list`、`stream_packets`、`packet.startswith`、`packet.endswith`、`json.loads`、`packet[6:].decode`、`content.append`、`choice["delta"].get`。 返回路径：L31的`packets, content`。
- `test_browser_provider_holds_real_terminal_bytes_until_a_visible_draft`（L34–L57）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L40遍历`content`；L41按`boundary`分支；L42断言`root_string_prefix(raw, "summary") == STREAM_SUMMARY`；L49抛异常，停止当前正常路径；L52断言`json.loads(raw) == value`；L53断言`len(set(before_release)) >= 3`；L54断言`any(fragment.endswith(r"\ud8") for _, fragment in content)`；L55断言`packets[-1][1] == b"data: [DONE]\r\n\r\n"`。后续分支沿下方源码相同行号继续阅读。 调用`news_requirement`、`fragments`、`root_string_prefix`、`json.loads`、`AssertionError`、`before_release.append`、`len`、`set`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_fixture_preserves_strict_planning_and_review_contracts`（L60–L69）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L65遍历`values`；L69断言`finish["choices"][0]["finish_reason"] == "stop"`。 调用`news_spec`、`fragments`、`schema.model_validate_json`、`"".join`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_provider_packets_pass_the_actual_structured_model_gateway`（L72–L103）：接收`store`。 控制顺序：L99断言`gateway.complete(run, "requirement:fixture", "JSON", {}, Requirement).summary == STRE…`；L103断言`store.transcript(run)["messages"][-1]["validation"] == "validated"`。 调用`SecretStr`、`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`news_requirement`、`b"".join`、`stream_packets`、`ModelGateway`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_provider_packets_pass_the_actual_structured_model_gateway.Bytes`（L84–L87）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_browser_provider_packets_pass_the_actual_structured_model_gateway.Bytes.__iter__`（L85–L87）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L86遍历`range(0, len(raw), 2)`。 调用`range`、`len`。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `tests/test_workbench_browser_fixture.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L103。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3949`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_workbench_browser_fixture.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "64953ee2b8082cbbcbf01f3dcde6fdbd3957108a775b73ab9c122a8939ef28df"} -->
````python
# tests/test_workbench_browser_fixture.py
"""The actual Chromium driver lives in scripts/ci_guided_browser.py.

These fast tests guard the explicit fixture's streaming proof and preserved guided
regression independently of optional local Chromium installation.
"""

import json
import uuid

import httpx
from pydantic import SecretStr

from scripts.ci_guided_browser import STREAM_SUMMARY, stream_packets
from scripts.news_fixture import news_requirement, news_spec
from workbench.domain import ModelReview, Plan, Requirement
from workbench.llm import ModelGateway
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
````
