# tests/test_product_browser_gate.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.generator`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `product`（L12–L15）：接收`tmp_path`、`plan`、`frontend`。 调用`generate_basic`。 返回路径：L15的`path`。
- `test_ui_never_accepts_missing_partial_browser_report`（L34–L37）：接收`tmp_path`、`plan`、`browser`。 调用`product`、`pytest.raises`、`require_browser_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_api_only_has_no_fabricated_browser_success`（L40–L42）：接收`tmp_path`、`plan`。 调用`product`、`require_browser_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ui_rejects_older_http_only_runtime_receipt`（L45–L55）：接收`tmp_path`、`plan`、`settings`、`monkeypatch`。 控制顺序：L55断言`not (tmp_path / "verification.json").exists()`。 调用`product`、`monkeypatch.setattr`、`pytest.raises`、`verify_basic`、`(tmp_path / "verification.json").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ui_rejects_older_http_only_runtime_receipt.old_probe`（L48–L50）：接收`product`、`python`、`report_path`、`settings`。 调用`write_json`。 返回路径：L50的`{"returncode": 0}`。
- `test_real_browser_spec_and_cleanroom_gate`（L58–L72）：接收`tmp_path`、`settings`。 控制顺序：L66断言`report["passed"] is True`；L67断言`report["browser"]["real_browser"] is True`；L69断言`delivery["cleanroom"]["browser"]["real_browser"] is True`；L70断言`delivery["cleanroom"]["browser"]["entities"] == [e.name for e in plan.entities]`；L72断言`saved["browser"]["errors"] == []`。 调用`Plan.model_validate`、`news_spec`、`product`、`verify_basic`、`package_basic`、`json.loads`、`(tmp_path / "verification.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_browser_is_environment_blocker_not_auto_repair`（L75–L83）：接收`tmp_path`、`plan`、`settings`、`monkeypatch`。 控制顺序：L82断言`not (tmp_path / "verification.json").exists()`；L83断言`not (tmp_path / "delivery.zip").exists()`。 调用`product`、`monkeypatch.setenv`、`str`、`pytest.raises`、`verify_basic`、`(tmp_path / "verification.json").exists`、`(tmp_path / "delivery.zip").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_browser_rejects_broken_generated_search_ui`（L86–L110）：接收`tmp_path`、`settings`。 控制顺序：L99断言`broken != original`；L109断言`report["passed"] is False`；L110断言`"browser acceptance failed" in report["message"]`。 调用`Plan.model_validate`、`news_spec`、`product`、`ui.read_text`、`original.replace`、`ui.write_text`、`pytest.raises`、`run_probe`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_optional_text_omitted_in_approved_rule_sample_still_checks_limits`（L113–L139）：接收`tmp_path`、`plan`、`settings`。 控制顺序：L138断言`report["passed"] is True`；L139断言`"browser-overlength-rejected:task.notes" in report["browser"]["checks"]`。 调用`plan.model_dump`、`data["entities"][0]["fields"].append`、`Plan.model_validate`、`product`、`(target / "custom_rules.py").write_text`、`verify_basic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_product_browser_gate.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L139。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5262`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_product_browser_gate.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "86f8e51bdb3c30dd332004ebce1fee87316339de6702b793a2f0800ded56d418"} -->
````python
# tests/test_product_browser_gate.py
"""Browser evidence is mandatory for each generated UI and its clean-room delivery."""

import json

import pytest

from workbench.filesystem import write_json
from workbench.generator import PrerequisiteError, generate_basic
from workbench.verification import package_basic, require_browser_evidence, verify_basic


def product(tmp_path, plan, frontend="simple-admin"):
    path = tmp_path / "product"
    generate_basic(plan, path, {"template": "python-basic", "frontend": frontend})
    return path


@pytest.mark.parametrize(
    "browser",
    [
        None,
        {},
        {"passed": True},
        {
            "passed": True,
            "real_browser": True,
            "applicable": True,
            "entities": ["task"],
            "checks": [],
            "errors": [],
        },
    ],
)
def test_ui_never_accepts_missing_partial_browser_report(tmp_path, plan, browser):
    target = product(tmp_path, plan)
    with pytest.raises(PrerequisiteError, match="浏览器"):
        require_browser_evidence(target, {"passed": True, "browser": browser})


def test_api_only_has_no_fabricated_browser_success(tmp_path, plan):
    target = product(tmp_path, plan, "api-only")
    require_browser_evidence(target, {"passed": True})


def test_ui_rejects_older_http_only_runtime_receipt(tmp_path, plan, settings, monkeypatch):
    target = product(tmp_path, plan)

    def old_probe(product, python, report_path, settings):
        write_json(report_path, {"passed": True, "restart": True, "http": True})
        return {"returncode": 0}

    monkeypatch.setattr("workbench.verification.run_probe", old_probe)
    with pytest.raises(PrerequisiteError, match="浏览器"):
        verify_basic(plan, target, settings)
    assert not (tmp_path / "verification.json").exists()


def test_real_browser_spec_and_cleanroom_gate(tmp_path, settings):
    # Real browser, real generated product, no model and no patched evidence.
    from scripts.news_fixture import news_spec
    from workbench.domain import Plan

    plan = Plan.model_validate(news_spec())
    target = product(tmp_path, plan)
    report = verify_basic(plan, target, settings)
    assert report["passed"] is True, report
    assert report["browser"]["real_browser"] is True
    delivery = package_basic(plan, target, settings, report)
    assert delivery["cleanroom"]["browser"]["real_browser"] is True
    assert delivery["cleanroom"]["browser"]["entities"] == [e.name for e in plan.entities]
    saved = json.loads((tmp_path / "verification.json").read_text(encoding="utf-8"))
    assert saved["browser"]["errors"] == []


def test_missing_browser_is_environment_blocker_not_auto_repair(
    tmp_path, plan, settings, monkeypatch
):
    target = product(tmp_path, plan)
    monkeypatch.setenv("PRODUCT_VERIFY_PLAYWRIGHT", str(tmp_path / "absent-playwright"))
    with pytest.raises(PrerequisiteError, match="Playwright"):
        verify_basic(plan, target, settings)
    assert not (tmp_path / "verification.json").exists()
    assert not (tmp_path / "delivery.zip").exists()


def test_real_browser_rejects_broken_generated_search_ui(tmp_path, settings):
    from scripts.news_fixture import news_spec
    from workbench.domain import Plan
    from workbench.tools import ToolFailure
    from workbench.verification import run_probe

    plan = Plan.model_validate(news_spec())
    target = product(tmp_path, plan)
    ui = target / "web/app.js"
    original = ui.read_text(encoding="utf-8")
    broken = original.replace(
        "if (value) query.set(key, value);", "if (value && key !== 'q') query.set(key, value);"
    )
    assert broken != original
    ui.write_text(broken, encoding="utf-8")
    report_path = tmp_path / "broken-browser.json"
    # Probe directly to prove the browser itself detects a broken UI. The normal
    # gate additionally rejects this mutation against the generation manifest.
    import sys

    with pytest.raises(ToolFailure):
        run_probe(target, sys.executable, report_path, settings)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["passed"] is False
    assert "browser acceptance failed" in report["message"]


def test_optional_text_omitted_in_approved_rule_sample_still_checks_limits(
    tmp_path, plan, settings
):
    from workbench.domain import Plan

    data = plan.model_dump()
    data["entities"][0]["fields"].append(
        {"name": "notes", "kind": "text", "required": False, "max_length": 30}
    )
    data["custom_rules"] = [
        {
            "description": "priority cannot be negative",
            "entity": "task",
            "accept_examples": [{"title": "allowed", "priority": 1, "done": False}],
            "reject_examples": [{"title": "rejected", "priority": -1, "done": False}],
        }
    ]
    plan = Plan.model_validate(data)
    target = product(tmp_path, plan)
    (target / "custom_rules.py").write_text(
        "def validate(entity, data):\n"
        "    if entity == 'task' and data['priority'] < 0:\n"
        "        raise ValueError('priority cannot be negative')\n"
    )
    report = verify_basic(plan, target, settings)
    assert report["passed"] is True, report
    assert "browser-overlength-rejected:task.notes" in report["browser"]["checks"]
````
