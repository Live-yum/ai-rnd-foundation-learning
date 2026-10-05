# tests/test_capability_form_dispatch.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.capability_contracts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_wait_is_a_strict_small_nonnegative_integer`（L15–L17）：接收`wait`。 调用`pytest.raises`、`HttpStep`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_request_representation_headers_are_not_model_overrides`（L28–L30）：接收`headers`。 调用`pytest.raises`、`HttpStep`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_form_values_are_string_only_and_bounded`（L37–L39）：接收`body`。 调用`pytest.raises`、`HttpStep`、`pytest.mark.parametrize`、`str`、`range`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_form_dispatch_encodes_once_and_wait_uses_the_same_deadline`（L42–L80）：接收`monkeypatch`。 控制顺序：L72断言`result[0]["passed"] is True`；L73断言`seen[0][0] == pytest.approx(10.3)`；L75断言`request.headers["content-type"] == "application/x-www-form-urlencoded"`；L76断言`parse_qs(request.content.decode()) == { "username": ["synthetic+user"], "captcha_key"…`；L80断言`request.extensions["timeout"]["read"] <= 0.701`。 调用`monkeypatch.setattr`、`now.__setitem__`、`httpx.Client`、`httpx.MockTransport`、`verifier.run_steps`、`HttpStep`、`pytest.approx`、`parse_qs`、`request.content.decode`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_form_dispatch_encodes_once_and_wait_uses_the_same_deadline.respond`（L49–L51）：接收`request`。 调用`seen.append`、`httpx.Response`、`httpx.ByteStream`。 返回路径：L51的`httpx.Response(200, stream=httpx.ByteStream(b'{"ok":true}'))`。
- `test_wait_and_capture_expansion_cannot_consume_past_phase_budget`（L83–L101）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`httpx.Client`、`httpx.MockTransport`、`pytest.fail`、`HttpStep`、`pytest.raises`、`verifier.run_steps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_body_remains_json_and_never_uses_form`（L104–L118）：接收`monkeypatch`。 控制顺序：L117断言`json.loads(seen[0].content) == {"id": 7}`；L118断言`seen[0].headers["content-type"] == "application/json"`。 调用`httpx.Client`、`httpx.MockTransport`、`verifier.run_steps`、`HttpStep`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_body_remains_json_and_never_uses_form.respond`（L107–L109）：接收`request`。 调用`seen.append`、`httpx.Response`、`httpx.ByteStream`。 返回路径：L109的`httpx.Response(200, stream=httpx.ByteStream(b"{}"))`。
- `test_wait_budget_counts_all_scenarios_before_first_request`（L121–L139）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`AcceptanceScenario`、`HttpStep`、`httpx.Client`、`httpx.MockTransport`、`pytest.fail`、`pytest.raises`、`verifier.run_scenarios`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_form_dispatch.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L139。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4817`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_form_dispatch.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ac112bf7f971e5c7cc0d6c2968cba68a81377296468aa08deb964351c7f58d2f"} -->
````python
# tests/test_capability_form_dispatch.py
"""Bounded owned-native form protocol; no external CAPTCHA or account calls."""

import json
from urllib.parse import parse_qs

import httpx
import pytest
from pydantic import ValidationError

from workbench import capability_verification as verifier
from workbench.capability_contracts import AcceptanceScenario, HttpStep


@pytest.mark.parametrize("wait", [-1, 1001, True, "300"])
def test_wait_is_a_strict_small_nonnegative_integer(wait):
    with pytest.raises(ValidationError):
        HttpStep(path="/", status=200, wait_ms=wait)


@pytest.mark.parametrize(
    "headers",
    [
        {"Content-Type": "text/plain"},
        {"content-encoding": "gzip"},
        {"Transfer-Encoding": "chunked"},
    ],
)
def test_request_representation_headers_are_not_model_overrides(headers):
    with pytest.raises(ValidationError):
        HttpStep(path="/", status=200, headers=headers)


@pytest.mark.parametrize(
    "body",
    [None, [], {"x": 1}, {"x": "x" * 4097}, {str(i): "x" for i in range(21)}, {"x": "é" * 4096}],
)
def test_form_values_are_string_only_and_bounded(body):
    with pytest.raises(ValidationError):
        HttpStep(method="POST", path="/", status=200, body=body, body_encoding="form")


def test_form_dispatch_encodes_once_and_wait_uses_the_same_deadline(monkeypatch):
    now, seen = [10.0], []
    monkeypatch.setattr(verifier.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        verifier.time, "sleep", lambda seconds: now.__setitem__(0, now[0] + seconds)
    )

    def respond(request):
        seen.append((now[0], request))
        return httpx.Response(200, stream=httpx.ByteStream(b'{"ok":true}'))

    with httpx.Client(
        base_url="http://owned.invalid", transport=httpx.MockTransport(respond)
    ) as client:
        result = verifier.run_steps(
            client,
            [
                HttpStep(
                    method="POST",
                    path="/system/auth/login",
                    status=200,
                    wait_ms=300,
                    body_encoding="form",
                    body={"username": "synthetic+user", "captcha_key": "${challenge}"},
                    equals={"$.ok": True},
                )
            ],
            {"challenge": "a&b"},
            deadline=11.0,
        )
    assert result[0]["passed"] is True
    assert seen[0][0] == pytest.approx(10.3)
    request = seen[0][1]
    assert request.headers["content-type"] == "application/x-www-form-urlencoded"
    assert parse_qs(request.content.decode()) == {
        "username": ["synthetic+user"],
        "captcha_key": ["a&b"],
    }
    assert request.extensions["timeout"]["read"] <= 0.701


def test_wait_and_capture_expansion_cannot_consume_past_phase_budget(monkeypatch):
    monkeypatch.setattr(verifier.time, "monotonic", lambda: 10.0)
    with httpx.Client(
        base_url="http://owned.invalid",
        transport=httpx.MockTransport(lambda request: pytest.fail("Must fail before network")),
    ) as client:
        step = HttpStep(
            method="POST",
            path="/",
            status=200,
            wait_ms=300,
            body_encoding="form",
            body={"x": "${value}"},
        )
        with pytest.raises(verifier.CheckFailure, match="期限"):
            verifier.run_steps(client, [step], {"value": "ok"}, deadline=10.2)
        step.wait_ms = 0
        with pytest.raises(verifier.CheckFailure, match="form"):
            verifier.run_steps(client, [step], {"value": "x" * 5000}, deadline=11)


def test_json_body_remains_json_and_never_uses_form(monkeypatch):
    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(200, stream=httpx.ByteStream(b"{}"))

    with httpx.Client(
        base_url="http://owned.invalid", transport=httpx.MockTransport(respond)
    ) as client:
        verifier.run_steps(
            client, [HttpStep(method="POST", path="/", status=200, body={"id": 7})], {}
        )
    assert json.loads(seen[0].content) == {"id": 7}
    assert seen[0].headers["content-type"] == "application/json"


def test_wait_budget_counts_all_scenarios_before_first_request(monkeypatch):
    monkeypatch.setattr(verifier, "MAX_HTTP_PHASE_WAIT_MS", 1000)
    scenarios = [
        AcceptanceScenario(
            id=name,
            title=name,
            requirements=["r"],
            steps=[HttpStep(path="/", status=200, wait_ms=600)],
        )
        for name in ("one", "two")
    ]
    with httpx.Client(
        base_url="http://owned.invalid",
        transport=httpx.MockTransport(
            lambda request: pytest.fail("No request before aggregate budget validation")
        ),
    ) as client:
        with pytest.raises(verifier.CheckFailure, match="等待总量"):
            verifier.run_scenarios(client, scenarios)
````
