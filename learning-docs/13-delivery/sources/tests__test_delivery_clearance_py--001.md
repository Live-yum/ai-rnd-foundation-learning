# tests/test_delivery_clearance.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.errors`、`workbench.filesystem`、`workbench.flow`、`workbench.generator`、`workbench.native_delivery`、`workbench.runtime`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_explicit_review_gap_blocks_smart_delivery`（L18–L51）：接收`settings`、`store`、`plan`。 控制顺序：L36断言`current["status"] == "BLOCKED"`；L37断言`"组合筛选" in current["error"]`；L38断言`current["pending"] is None`；L40断言`not (root / "delivery.zip").exists()`；L41断言`not (root / "delivery.json").exists()`；L43断言`report["delivery_clearance"] is False`；L44断言`report["uncovered_requirements"] == ["已批准的组合筛选尚未实现"]`；L45断言`len(store.messages(run)) == 1`。后续分支沿下方源码相同行号继续阅读。 调用`new_run`、`store.set_automation`、`Runtime`、`Reviewer`、`worker.tick`、`store.get_run`、`(root / "delivery.zip").exists`、`(root / "delivery.json").exists`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_review_gap_blocks_smart_delivery.Reviewer`（L21–L29）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_explicit_review_gap_blocks_smart_delivery.Reviewer.complete`（L22–L29）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L23按`schema is ModelReview`分支；L24断言`payload["independent_evidence"]["passed"] is True`。 调用`ModelReview`、`super().complete`、`super`。 返回路径：L25的`ModelReview( summary="发现缺口，不能交付", uncovered_requirements=["已批准的组合筛选尚未实现"], )`；L29的`super().complete(run, key, instruction, payload, schema)`。
- `test_package_rechecks_review_from_older_checkpoint`（L54–L72）：接收`settings`、`store`、`monkeypatch`。 调用`monkeypatch.setattr`、`Workflow`、`pytest.raises`、`workflow.package`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_package_rechecks_review_from_older_checkpoint.must_not_package`（L57–L58）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_requires_exact_positive_restore_evidence`（L87–L94）：接收`tmp_path`、`field`、`value`。 调用`verified_fixture`、`json.loads`、`target.read_text`、`data.setdefault`、`write_json`、`sha`、`pytest.raises`、`managed_verify`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_cannot_depend_on_generation_environment`（L101–L108）：接收`tmp_path`、`field`、`value`。 调用`verified_fixture`、`json.loads`、`target.read_text`、`data.setdefault`、`write_json`、`sha`、`pytest.raises`、`managed_verify`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rejects_absent_or_partial_restore_report`（L112–L119）：接收`tmp_path`、`restored`。 调用`verified_fixture`、`json.loads`、`target.read_text`、`write_json`、`sha`、`pytest.raises`、`managed_verify`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_style_receipt_cannot_be_skipped_or_forged`（L146–L186）：接收`tmp_path`、`change`。 控制顺序：L150按`change == "missing"`分支；L152按`change == "partial"`分支；L154按`change == "template"`分支；L156按`change == "family"`分支；L158按`change in {"passed", "truthy_passed"}`分支；L160按`change in {"shell", "truthy_shell"}`分支；L162按`change in {"substitution", "falsey_substitution"}`分支；L164按`change == "protected"`分支。后续分支沿下方源码相同行号继续阅读。 调用`verified_fixture`、`json.loads`、`target.read_text`、`data.pop`、`write_json`、`sha`、`pytest.raises`、`managed_verify`、`(product.parent / "verification.json").exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_delivery_clearance.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L186。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7018`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_delivery_clearance.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6f3d978ee5803abbe03dfa83207c7df7a4c9e1d9bc70344ca8130a5f1b4531a3"} -->
````python
# tests/test_delivery_clearance.py
"""Missing acceptance evidence must never become READY, even with green unit tests."""

import json

import pytest
from conftest import FixtureGateway, new_run
from test_native_managed import verified_fixture

from workbench.domain import ModelReview
from workbench.errors import UnsupportedScope
from workbench.filesystem import sha, write_json
from workbench.flow import Workflow
from workbench.generator import PrerequisiteError
from workbench.native_delivery import managed_verify
from workbench.runtime import Runtime


def test_explicit_review_gap_blocks_smart_delivery(settings, store, plan):
    settings.model_review = True

    class Reviewer(FixtureGateway):
        def complete(self, run, key, instruction, payload, schema):
            if schema is ModelReview:
                assert payload["independent_evidence"]["passed"] is True
                return ModelReview(
                    summary="发现缺口，不能交付",
                    uncovered_requirements=["已批准的组合筛选尚未实现"],
                )
            return super().complete(run, key, instruction, payload, schema)

    run = new_run(store)
    store.set_automation(run, True, "one-consent")
    with Runtime(settings, store, Reviewer(plan)) as worker:
        worker.tick()
    current = store.get_run(run)
    assert current["status"] == "BLOCKED", current
    assert "组合筛选" in current["error"]
    assert current["pending"] is None
    root = settings.data_dir / "runs" / run
    assert not (root / "delivery.zip").exists()
    assert not (root / "delivery.json").exists()
    report = json.loads((root / "model-review.json").read_text(encoding="utf-8"))
    assert report["delivery_clearance"] is False
    assert report["uncovered_requirements"] == ["已批准的组合筛选尚未实现"]
    assert len(store.messages(run)) == 1
    settings.model_review = False
    store.retry(run, "cannot-waive-review")
    with Runtime(settings, store, Reviewer(plan)) as worker:
        worker.tick()
    assert store.get_run(run)["status"] == "BLOCKED"
    assert not (root / "delivery.zip").exists()


def test_package_rechecks_review_from_older_checkpoint(settings, store, monkeypatch):
    import workbench.flow as flow

    def must_not_package(*args, **kwargs):
        pytest.fail("A saved review with missing requirements must not reach packaging")

    monkeypatch.setattr(flow, "package_basic", must_not_package)
    workflow = Workflow(settings, store, None)
    with pytest.raises(UnsupportedScope, match="审阅"):
        workflow.package(
            {
                "run_id": "saved-review",
                "template": "python-basic",
                "model_review": {
                    "enabled": True,
                    "uncovered_requirements": ["未实现已批准功能"],
                },
            }
        )


@pytest.mark.parametrize(
    "field",
    [
        "passed",
        "fresh_database",
        "frontend_started",
        "installed_from_lock",
        "standalone_launcher",
        "restart",
    ],
)
@pytest.mark.parametrize("value", [False, None, "true", 1])
def test_native_requires_exact_positive_restore_evidence(tmp_path, field, value):
    product, receipt, target = verified_fixture(tmp_path)
    data = json.loads(target.read_text(encoding="utf-8"))
    data.setdefault("portable_restored", {})[field] = value
    write_json(target, data)
    receipt["evidence_sha256"] = sha(target)
    with pytest.raises(PrerequisiteError, match="独立"):
        managed_verify(product, receipt)


@pytest.mark.parametrize(
    "field", ["source_database_reused", "original_platform_imported", "model_required"]
)
@pytest.mark.parametrize("value", [True, None, "false", 0])
def test_native_cannot_depend_on_generation_environment(tmp_path, field, value):
    product, receipt, target = verified_fixture(tmp_path)
    data = json.loads(target.read_text(encoding="utf-8"))
    data.setdefault("portable_restored", {})[field] = value
    write_json(target, data)
    receipt["evidence_sha256"] = sha(target)
    with pytest.raises(PrerequisiteError, match="独立"):
        managed_verify(product, receipt)


@pytest.mark.parametrize("restored", [None, {}, True, {"passed": True}])
def test_native_rejects_absent_or_partial_restore_report(tmp_path, restored):
    product, receipt, target = verified_fixture(tmp_path)
    data = json.loads(target.read_text(encoding="utf-8"))
    data["portable_restored"] = restored
    write_json(target, data)
    receipt["evidence_sha256"] = sha(target)
    with pytest.raises(PrerequisiteError, match="独立"):
        managed_verify(product, receipt)


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "partial",
        "template",
        "family",
        "passed",
        "truthy_passed",
        "shell",
        "truthy_shell",
        "substitution",
        "falsey_substitution",
        "protected",
        "digest",
        "pages",
        "page_hash",
        "page_path",
        "components",
        "entities",
        "wrong_components",
        "unhashable_path",
    ],
)
def test_native_style_receipt_cannot_be_skipped_or_forged(tmp_path, change):
    product, receipt, target = verified_fixture(tmp_path)
    data = json.loads(target.read_text(encoding="utf-8"))
    style = data["native_style"]
    if change == "missing":
        data.pop("native_style")
    elif change == "partial":
        data["native_style"] = {"passed": True}
    elif change == "template":
        style["template"] = "yudao-vben"
    elif change == "family":
        style["ui_family"] = "simple-admin"
    elif change in {"passed", "truthy_passed"}:
        style["passed"] = False if change == "passed" else 1
    elif change in {"shell", "truthy_shell"}:
        style["shell_and_theme_unchanged"] = False if change == "shell" else "true"
    elif change in {"substitution", "falsey_substitution"}:
        style["generic_frontend_substitution"] = True if change == "substitution" else 0
    elif change == "protected":
        style["protected_files"] = {}
    elif change == "digest":
        style["protected_source_digest"] = "0" * 64
    elif change == "pages":
        style["generated_pages"] = []
    elif change == "page_hash":
        style["generated_pages"][0]["sha256"] = "0" * 64
    elif change == "page_path":
        style["generated_pages"][0]["path"] = "../../unrelated.vue"
    elif change == "components":
        style["generated_pages"][0]["native_components"] = []
    elif change == "entities":
        data["entities"] = []
    elif change == "wrong_components":
        style["generated_pages"][0]["native_components"] = ["GenericTable"]
    elif change == "unhashable_path":
        style["generated_pages"][0]["path"] = []
    write_json(target, data)
    receipt["evidence_sha256"] = sha(target)
    with pytest.raises(PrerequisiteError, match="原生UI"):
        managed_verify(product, receipt)
    assert not (product.parent / "verification.json").exists()
````
