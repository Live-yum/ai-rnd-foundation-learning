# tests/test_learning_docs_signup.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.handbook_notes`、`scripts.rebuild_learning_docs`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `valid_summary`（L27–L44）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`dict.fromkeys`、`hashlib.sha256(data).hexdigest`、`hashlib.sha256`、`BUNDLE_FILES.items`、`hashlib.sha256(PNG_BYTES).hexdigest`。 返回路径：L28的`{ **dict.fromkeys(acceptance.SIGNUP_SCOPE_TRUE_FIELDS, True), "run_id": "same-fixture-run"…`。
- `browser_files`（L47–L57）：接收`destination`、`summary`、`missing_image`。 控制顺序：L51遍历`BUNDLE_FILES.items()`；L55遍历`SCREENSHOTS`；L56按`not missing_image or name != "scope-corrected.png"`分支。 调用`folder.mkdir`、`(folder / "browser.json").write_text`、`json.dumps`、`BUNDLE_FILES.items`、`path.parent.mkdir`、`path.write_bytes`、`(folder / name).write_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_cleanroom_driver_and_evidence_are_separate`（L60–L73）：接收`tmp_path`。 控制顺序：L70断言`result == summary`；L71断言`commands == [["student-python", "-m", "scripts.ci_signup_scope_browser"]]`；L72断言`json.loads((evidence / "browser.json").read_text()) == summary`；L73断言`(evidence / "scope-corrected.png").is_file()`。 调用`valid_summary`、`acceptance.verify_signup_scope_browser`、`json.loads`、`(evidence / "browser.json").read_text`、`(evidence / "scope-corrected.png").is_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_cleanroom_driver_and_evidence_are_separate.run`（L65–L67）：接收`argv`。 调用`commands.append`、`browser_files`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_evidence_requires_literal_success_for_every_claim`（L78–L86）：接收`tmp_path`、`field`、`bad`。 控制顺序：L86断言`(tmp_path / "out/browser.json").is_file()`。 调用`valid_summary`、`pytest.raises`、`acceptance.verify_signup_scope_browser`、`browser_files`、`(tmp_path / "out/browser.json").is_file`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_cleanroom_rejects_changed_scope_or_missing_contract`（L112–L119）：接收`tmp_path`、`field`、`bad`。 调用`valid_summary`、`pytest.raises`、`acceptance.verify_signup_scope_browser`、`browser_files`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_cleanroom_requires_all_screenshot_files`（L122–L130）：接收`tmp_path`。 调用`pytest.raises`、`acceptance.verify_signup_scope_browser`、`browser_files`、`valid_summary`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_cleanroom_preserves_failure_and_never_merges_previous_success`（L133–L150）：接收`tmp_path`。 控制顺序：L148断言`(evidence / "browser.log").read_text() == "current failure"`；L149断言`not (evidence / "browser.json").exists()`；L150断言`(previous / "browser.json").read_text() == '{"passed":true}'`。 调用`previous.mkdir`、`(previous / "browser.json").write_text`、`pytest.raises`、`acceptance.verify_signup_scope_browser`、`(evidence / "browser.log").read_text`、`(evidence / "browser.json").exists`、`(previous / "browser.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_cleanroom_preserves_failure_and_never_merges_previous_success.run`（L140–L144）：接收`_`。 控制顺序：L144抛异常，停止当前正常路径。 调用`folder.mkdir`、`(folder / "browser.log").write_text`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_cleanroom_refuses_preexisting_evidence_before_running`（L154–L163）：接收`tmp_path`、`reuse`。 控制顺序：L156按`reuse == "source"`分支；L163断言`commands == []`。 调用`browser_files`、`valid_summary`、`evidence.mkdir`、`pytest.raises`、`acceptance.verify_signup_scope_browser`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_teaching_source_assignment_and_lessons_match_current_boundaries`（L166–L182）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L167遍历`("requirement_intent", "requirement_canonical")`；L168断言`builder.stage_for(f"workbench/{name}.py") == 3`；L169断言`"项目根配置" not in purpose(f"workbench/{name}.py")[0]`；L170遍历`("ci_signup_scope_browser.py", "signup_scope_browser.cjs")`；L171断言`builder.stage_for(f"scripts/{name}") == 14`；L172断言`"浏览器" in purpose(f"scripts/{name}")[0]`；L174断言`"uv sync --locked --extra postgres" in stages[0]["body"]`；L175断言`"不能因为框架能注册账号" in stages[3]["body"]`。后续分支沿下方源码相同行号继续阅读。 调用`builder.stage_for`、`purpose`、`builder.read_content`、`all`、`check_fences`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_cleanroom_rejects_artifact_changes_after_report`（L186–L201）：接收`tmp_path`、`damage`。 调用`pytest.raises`、`acceptance.verify_signup_scope_browser`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_signup_cleanroom_rejects_artifact_changes_after_report.run`（L189–L198）：接收`_`。 控制顺序：L191按`damage == "asset"`分支；L193按`damage == "extra_asset"`分支。 调用`browser_files`、`valid_summary`、`(destination / "workbench/web/app.js").write_bytes`、`(destination / "workbench/web/unreported.js").write_bytes`、`(destination / "reports/signup-scope-browser/scope-corrected.png"…`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_learning_docs_signup.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L201。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8194`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_learning_docs_signup.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2b03e619bfae38735057a548a3ebfca3344532f06634093e5a37e4b84b39570c"} -->
````python
# tests/test_learning_docs_signup.py
"""Signup lessons and restored real-browser evidence fail closed independently."""

import hashlib
import json

import pytest

from scripts import build_learning_docs as builder
from scripts import ci_learning_docs as acceptance
from scripts.handbook_notes import purpose
from scripts.rebuild_learning_docs import check_fences

PNG_BYTES = b"\x89PNG\r\n\x1a\nfixture-test-bytes"
BUNDLE_FILES = {
    "workbench/web/index.html": b"fixture HTML",
    "workbench/web/app.js": b"fixture Javascript",
    "workbench/web/style.css": b"fixture CSS",
}
SCREENSHOTS = [
    "scope-blocked.png",
    "scope-blocked-mobile.png",
    "scope-options-mobile.png",
    "scope-corrected.png",
]


def valid_summary():
    return {
        **dict.fromkeys(acceptance.SIGNUP_SCOPE_TRUE_FIELDS, True),
        "run_id": "same-fixture-run",
        "native_generation_attempted": False,
        "external_provider_calls": False,
        "fixture_mode": "in-process-requirement-gateway",
        "fixture_model_calls": [{"run_id": "same-fixture-run", "key": "requirement:3"}],
        "original_approval_count": 1,
        "recovered_approval_count": 1,
        "status": "WAITING_REQUIREMENTS",
        "errors": [],
        "screenshots": SCREENSHOTS,
        "ui_bundle_sha256": {
            name: hashlib.sha256(data).hexdigest() for name, data in BUNDLE_FILES.items()
        },
        "screenshot_sha256": dict.fromkeys(SCREENSHOTS, hashlib.sha256(PNG_BYTES).hexdigest()),
    }


def browser_files(destination, summary, *, missing_image=False):
    folder = destination / "reports/signup-scope-browser"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "browser.json").write_text(json.dumps(summary))
    for name, data in BUNDLE_FILES.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for name in SCREENSHOTS:
        if not missing_image or name != "scope-corrected.png":
            (folder / name).write_bytes(PNG_BYTES)


def test_signup_cleanroom_driver_and_evidence_are_separate(tmp_path):
    destination, evidence = tmp_path / "student", tmp_path / "evidence/current"
    summary = valid_summary()
    commands = []

    def run(argv):
        commands.append(argv)
        browser_files(destination, summary)

    result = acceptance.verify_signup_scope_browser(destination, "student-python", run, evidence)
    assert result == summary
    assert commands == [["student-python", "-m", "scripts.ci_signup_scope_browser"]]
    assert json.loads((evidence / "browser.json").read_text()) == summary
    assert (evidence / "scope-corrected.png").is_file()


@pytest.mark.parametrize("field", acceptance.SIGNUP_SCOPE_TRUE_FIELDS)
@pytest.mark.parametrize("bad", [False, None, 1, "true"])
def test_signup_evidence_requires_literal_success_for_every_claim(tmp_path, field, bad):
    destination = tmp_path / "student"
    summary = valid_summary()
    summary[field] = bad
    with pytest.raises(AssertionError, match="browser/recovery evidence"):
        acceptance.verify_signup_scope_browser(
            destination, "python", lambda _: browser_files(destination, summary), tmp_path / "out"
        )
    assert (tmp_path / "out/browser.json").is_file()


@pytest.mark.parametrize(
    "field,bad",
    [
        ("native_generation_attempted", True),
        ("native_generation_attempted", 0),
        ("external_provider_calls", True),
        ("external_provider_calls", None),
        ("fixture_mode", "real-model"),
        ("status", "READY"),
        ("errors", ["failed request"]),
        ("fixture_model_calls", []),
        ("fixture_model_calls", [{"run_id": "other-run"}]),
        ("fixture_model_calls", [{"run_id": "same-fixture-run"}] * 2),
        ("run_id", ""),
        ("original_approval_count", 0),
        ("recovered_approval_count", True),
        ("recovered_approval_count", 2),
        ("screenshots", []),
        ("screenshots", ["../unrelated.png"]),
        ("ui_bundle_sha256", {}),
        ("screenshot_sha256", {"scope-blocked.png": "wrong"}),
    ],
)
def test_signup_cleanroom_rejects_changed_scope_or_missing_contract(tmp_path, field, bad):
    destination = tmp_path / "student"
    summary = valid_summary()
    summary[field] = bad
    with pytest.raises(AssertionError):
        acceptance.verify_signup_scope_browser(
            destination, "python", lambda _: browser_files(destination, summary), tmp_path / "out"
        )


def test_signup_cleanroom_requires_all_screenshot_files(tmp_path):
    destination = tmp_path / "student"
    with pytest.raises(AssertionError, match="all desktop/mobile PNG"):
        acceptance.verify_signup_scope_browser(
            destination,
            "python",
            lambda _: browser_files(destination, valid_summary(), missing_image=True),
            tmp_path / "out",
        )


def test_signup_cleanroom_preserves_failure_and_never_merges_previous_success(tmp_path):
    destination = tmp_path / "student"
    previous = tmp_path / "evidence/previous"
    previous.mkdir(parents=True)
    (previous / "browser.json").write_text('{"passed":true}')
    evidence = tmp_path / "evidence/current"

    def run(_):
        folder = destination / "reports/signup-scope-browser"
        folder.mkdir(parents=True)
        (folder / "browser.log").write_text("current failure")
        raise RuntimeError("Chromium failed")

    with pytest.raises(RuntimeError, match="Chromium failed"):
        acceptance.verify_signup_scope_browser(destination, "python", run, evidence)
    assert (evidence / "browser.log").read_text() == "current failure"
    assert not (evidence / "browser.json").exists()
    assert (previous / "browser.json").read_text() == '{"passed":true}'


@pytest.mark.parametrize("reuse", ["source", "destination"])
def test_signup_cleanroom_refuses_preexisting_evidence_before_running(tmp_path, reuse):
    destination, evidence = tmp_path / "student", tmp_path / "evidence"
    if reuse == "source":
        browser_files(destination, valid_summary())
    else:
        evidence.mkdir()
    commands = []
    with pytest.raises((FileExistsError, AssertionError)):
        acceptance.verify_signup_scope_browser(destination, "python", commands.append, evidence)
    assert commands == []


def test_signup_teaching_source_assignment_and_lessons_match_current_boundaries():
    for name in ("requirement_intent", "requirement_canonical"):
        assert builder.stage_for(f"workbench/{name}.py") == 3
        assert "项目根配置" not in purpose(f"workbench/{name}.py")[0]
    for name in ("ci_signup_scope_browser.py", "signup_scope_browser.cjs"):
        assert builder.stage_for(f"scripts/{name}") == 14
        assert "浏览器" in purpose(f"scripts/{name}")[0]
    stages = builder.read_content()
    assert "uv sync --locked --extra postgres" in stages[0]["body"]
    assert "不能因为框架能注册账号" in stages[3]["body"]
    assert "Workflow.capability_recovery" in stages[7]["body"]
    assert "capability_conflicts" in stages[8]["body"]
    assert "副作用" in stages[9]["body"]
    assert "uv run python -m scripts.ci_signup_scope_browser" in stages[14]["body"]
    assert "reports/learning-docs-signup-scope-browser/" in stages[14]["body"]
    assert "进程内需求网关夹具" in stages[14]["body"]
    assert all(check_fences(stage["body"]) >= 0 for stage in stages)


@pytest.mark.parametrize("damage", ["asset", "extra_asset", "screenshot"])
def test_signup_cleanroom_rejects_artifact_changes_after_report(tmp_path, damage):
    destination = tmp_path / "student"

    def run(_):
        browser_files(destination, valid_summary())
        if damage == "asset":
            (destination / "workbench/web/app.js").write_bytes(b"changed")
        elif damage == "extra_asset":
            (destination / "workbench/web/unreported.js").write_bytes(b"extra")
        else:
            (destination / "reports/signup-scope-browser/scope-corrected.png").write_bytes(
                PNG_BYTES + b"changed"
            )

    with pytest.raises(AssertionError, match="must bind"):
        acceptance.verify_signup_scope_browser(destination, "python", run, tmp_path / "out")
````
