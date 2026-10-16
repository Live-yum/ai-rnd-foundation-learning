# tests/test_source_candidate_transaction.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.delivery`、`workbench.filesystem`、`workbench.generation.python_basic`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `initial`（L20–L51）：接收`tmp_path`、`monkeypatch`、`plan`。 调用`plan.model_copy`、`upstream.mkdir`、`(upstream / "base.txt").write_text`、`str`、`digest`、`manifest`、`monkeypatch.setattr`、`product.parent.mkdir`、`(product.parent / "design.json").write_text`等。 返回路径：L49的`SimpleNamespace( product=product, plan=plan, settings=SimpleNamespace(), generate=generate…`。
- `initial.generate`（L37–L43）：接收`template`、`plan`、`destination`、`sources`。 调用`(destination / "business.py").write_text`。 返回路径：L39的`{ "generation_status": "partial", "pending_steps": ["runtime verification"], "generated_fi…`。
- `build`（L54–L57）：接收`initial`。 调用`candidate.generate_candidate`。 返回路径：L55的`candidate.generate_candidate( initial.settings, "fastapiadmin", initial.plan, initial.prod…`。
- `test_preparation_failure_leaves_no_product_and_retry_succeeds`（L61–L85）：接收`initial`、`monkeypatch`、`window`。 控制顺序：L81断言`not initial.product.exists()`；L82断言`sorted(path.name for path in initial.product.parent.iterdir()) == ["design.json"]`；L85断言`candidate.verify_candidate(initial.product, receipt)["source_checks_passed"]`。 调用`getattr`、`monkeypatch.setattr`、`pytest.raises`、`build`、`initial.product.exists`、`sorted`、`initial.product.parent.iterdir`、`candidate.verify_candidate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preparation_failure_leaves_no_product_and_retry_succeeds.failed`（L74–L76）：接收`*args`、`**kwargs`。 控制顺序：L76抛异常，停止当前正常路径。 调用`original`、`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_publication_failure_resumes_before_capability_changes`（L90–L120）：接收`initial`、`monkeypatch`、`item`、`after`。 控制顺序：L115断言`result["execution"] == "source-candidate"`；L116断言`not (initial.product.parent / ".source-candidate-transaction").exists()`；L117断言`native.managed_generate(initial.settings, "fastapiadmin", initial.plan, initial.produ…`。 调用`monkeypatch.setattr`、`pytest.raises`、`build`、`native.managed_generate`、`(initial.product.parent / ".source-candidate-transaction").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_publication_failure_resumes_before_capability_changes.interrupted`（L94–L101）：接收`path`、`target`。 控制顺序：L96按`Path(target) == initial.product.parent / item and not raised`分支；L98按`after`分支；L100抛异常，停止当前正常路径。 调用`Path`、`original`、`SystemExit`。 返回路径：L101的`original(path, target)`。
- `test_publication_failure_resumes_before_capability_changes.forbidden`（L108–L109）：接收`*args`、`**kwargs`。 控制顺序：L109抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `interrupted_transaction`（L123–L135）：接收`initial`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.raises`、`build`。 返回路径：L135的`initial.product.parent / ".source-candidate-transaction"`。
- `interrupted_transaction.interrupted`（L126–L129）：接收`path`、`target`。 控制顺序：L127按`Path(target) == initial.product`分支；L128抛异常，停止当前正常路径。 调用`Path`、`SystemExit`、`original`。 返回路径：L129的`original(path, target)`。
- `test_recovery_never_adopts_unknown_or_changed_content`（L139–L155）：接收`initial`、`monkeypatch`、`tamper`。 控制顺序：L141按`tamper == "unknown_product"`分支；L144按`tamper == "extra_secret"`分支；L146按`tamper == "receipt"`分支；L148按`tamper == "plan"`分支；L154按`tamper == "unknown_product"`分支；L155断言`(initial.product / "mine.txt").read_text(encoding="utf-8") == "user content"`。 调用`interrupted_transaction`、`initial.product.mkdir`、`(initial.product / "mine.txt").write_text`、`(transaction / "candidate/product/.env").write_text`、`(transaction / "candidate/native-generation.json").write_text`、`initial.plan.model_copy`、`(transaction / "candidate/product/business.py").write_text`、`pytest.raises`、`build`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_completed_transaction_does_not_block_legitimate_refresh`（L158–L167）：接收`initial`。 控制顺序：L161断言`native.managed_generate(initial.settings, "fastapiadmin", initial.plan, initial.produ…`；L165断言`json.loads((initial.product.parent / "design.json").read_text(encoding="utf-8")) == {…`。 调用`build`、`candidate.refresh_candidate`、`native.managed_generate`、`json.loads`、`(initial.product.parent / "design.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_process_exit_after_publication_can_resume`（L171–L223）：接收`tmp_path`、`plan`、`monkeypatch`、`item`。 控制顺序：L214断言`result.returncode == 73`；L222断言`candidate.verify_candidate(product, receipt)["source_checks_passed"]`；L223断言`not (product.parent / ".source-candidate-transaction").exists()`。 调用`plan.model_copy`、`root.mkdir`、`plan_path.write_text`、`plan.model_dump_json`、`subprocess.run`、`str`、`Path(__file__).resolve`、`Path`、`monkeypatch.setattr`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_process_exit_after_publication_can_resume.forbidden`（L216–L217）：接收`*args`、`**kwargs`。 控制顺序：L217抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_no_replace_preserves_existing_even_empty_target`（L227–L242）：接收`tmp_path`、`directory`。 控制顺序：L229按`directory`分支；L238按`directory`分支；L239断言`list(target.iterdir()) == []`；L241断言`target.read_text(encoding="utf-8") == "user content"`；L242断言`source.exists()`。 调用`source.mkdir`、`target.mkdir`、`(source / "business.txt").write_text`、`source.write_text`、`target.write_text`、`pytest.raises`、`candidate._publish_new`、`list`、`target.iterdir`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_target_created_after_preflight_is_not_overwritten`（L246–L265）：接收`initial`、`monkeypatch`、`item`。 控制顺序：L261断言`(list(target.iterdir()) == []) if item == "product" else target.read_text(encoding="u…`。 调用`monkeypatch.setattr`、`pytest.raises`、`build`、`list`、`target.iterdir`、`target.read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_target_created_after_preflight_is_not_overwritten.raced`（L249–L255）：接收`source`、`target`。 控制顺序：L250按`Path(target) == initial.product.parent / item`分支；L251按`item == "product"`分支。 调用`Path`、`Path(target).mkdir`、`Path(target).write_text`、`original`。 返回路径：L255的`original(source, target)`。
- `test_marker_publication_and_retirement_failures_are_recoverable`（L270–L301）：接收`initial`、`monkeypatch`、`window`、`after`。 控制顺序：L300断言`result["execution"] == "source-candidate"`；L301断言`not (initial.product.parent / ".source-candidate-transaction").exists()`。 调用`monkeypatch.setattr`、`pytest.raises`、`build`、`native.managed_generate`、`(initial.product.parent / ".source-candidate-transaction").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_marker_publication_and_retirement_failures_are_recoverable.interrupted`（L276–L288）：接收`source`、`target`。 控制顺序：L283按`match and not raised`分支；L285按`after`分支；L287抛异常，停止当前正常路径。 调用`Path`、`original`、`SystemExit`。 返回路径：L288的`original(source, target)`。
- `test_git_journal_publication_resumes_without_git`（L305–L334）：接收`initial`、`monkeypatch`、`after`。 控制顺序：L306按`not REAL_WHICH("git")`分支；L329断言`receipt["source_commit"]["status"] == "committed"`；L330断言`(initial.product.parent / "verification.json").read_bytes() == sealed_report`；L331断言`candidate.verify_candidate(initial.product, receipt)["source_commit"]["status"] == "u…`。 调用`REAL_WHICH`、`pytest.skip`、`monkeypatch.setattr`、`pytest.raises`、`build`、`(transaction / "candidate/verification.json").read_bytes`、`candidate.recover_candidate`、`(initial.product.parent / "verification.json").read_bytes`、`candidate.verify_candidate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_journal_publication_resumes_without_git.crash`（L312–L319）：接收`source`、`target`。 控制顺序：L314按`Path(target) == initial.product.parent / "source-revisions" and not interrupted`分支；L316按`after`分支；L318抛异常，停止当前正常路径。 调用`Path`、`original`、`SystemExit`。 返回路径：L319的`original(source, target)`。

</details>

**创建路径：** `tests/test_source_candidate_transaction.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L334。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12755`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_source_candidate_transaction.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "17e5ffb136bd696f89db2d611dffcff79fd0c855e9e3c74cf3adb2fc63178cd6"} -->
````python
# tests/test_source_candidate_transaction.py
"""Initial source publication survives failures without adopting unknown content."""

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from workbench.core.contracts import digest
from workbench.delivery import native
from workbench.delivery import source_candidate as candidate
from workbench.filesystem import manifest
from workbench.generation.python_basic import PrerequisiteError

REAL_WHICH = shutil.which


@pytest.fixture
def initial(tmp_path, monkeypatch, plan):
    from workbench.generation.native import offline, service
    from workbench.templates import standards

    plan = plan.model_copy(update={"data_scope": "shared"})
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    (upstream / "base.txt").write_text("trusted baseline\n", encoding="utf-8")
    source = {
        "slot": "fastapiadmin",
        "path": str(upstream),
        "source_digest": digest(manifest(upstream)),
    }
    monkeypatch.setattr(service, "prepare_sources", lambda *args: [source])
    monkeypatch.setattr(standards, "write_coding_standard", lambda *args: None)
    monkeypatch.setattr(candidate.shutil, "which", lambda _: None)

    def generate(template, plan, destination, sources):
        (destination / "business.py").write_text("value = 42\n", encoding="utf-8")
        return {
            "generation_status": "partial",
            "pending_steps": ["runtime verification"],
            "generated_files": ["business.py"],
        }

    monkeypatch.setattr(offline, "generate_offline", generate)
    product = tmp_path / "run/product"
    product.parent.mkdir()
    (product.parent / "design.json").write_text('{"approved": true}\n', encoding="utf-8")
    return SimpleNamespace(
        product=product, plan=plan, settings=SimpleNamespace(), generate=generate
    )


def build(initial):
    return candidate.generate_candidate(
        initial.settings, "fastapiadmin", initial.plan, initial.product, "no runtime"
    )


@pytest.mark.parametrize("window", ["copy", "generate", "status", "snapshot", "receipt"])
def test_preparation_failure_leaves_no_product_and_retry_succeeds(initial, monkeypatch, window):
    from workbench.generation.native import offline
    from workbench.infrastructure.native import environment

    owner, name = {
        "copy": (environment, "copy_source"),
        "generate": (offline, "generate_offline"),
        "status": (candidate, "write_status"),
        "snapshot": (candidate, "source_snapshot"),
        "receipt": (candidate, "refresh_candidate"),
    }[window]
    original = getattr(owner, name)

    def failed(*args, **kwargs):
        original(*args, **kwargs)
        raise PermissionError("injected preparation failure")

    monkeypatch.setattr(owner, name, failed)
    with pytest.raises(PermissionError):
        build(initial)
    assert not initial.product.exists()
    assert sorted(path.name for path in initial.product.parent.iterdir()) == ["design.json"]
    monkeypatch.setattr(owner, name, original)
    receipt = build(initial)
    assert candidate.verify_candidate(initial.product, receipt)["source_checks_passed"]


@pytest.mark.parametrize("item", ["product", "verification.json", "native-generation.json"])
@pytest.mark.parametrize("after", [False, True])
def test_publication_failure_resumes_before_capability_changes(initial, monkeypatch, item, after):
    original = candidate._publish_new
    raised = False

    def interrupted(path, target):
        nonlocal raised
        if Path(target) == initial.product.parent / item and not raised:
            raised = True
            if after:
                original(path, target)
            raise SystemExit("simulated process interruption")
        return original(path, target)

    monkeypatch.setattr(candidate, "_publish_new", interrupted)
    with pytest.raises(SystemExit):
        build(initial)
    monkeypatch.setattr(candidate, "_publish_new", original)

    def forbidden(*args, **kwargs):
        raise AssertionError("Recovery must precede capability discovery")

    monkeypatch.setattr(native, "generation_capability", forbidden)
    result = native.managed_generate(
        initial.settings, "fastapiadmin", initial.plan, initial.product
    )
    assert result["execution"] == "source-candidate"
    assert not (initial.product.parent / ".source-candidate-transaction").exists()
    assert (
        native.managed_generate(initial.settings, "fastapiadmin", initial.plan, initial.product)
        == result
    )


def interrupted_transaction(initial, monkeypatch):
    original = candidate._publish_new

    def interrupted(path, target):
        if Path(target) == initial.product:
            raise SystemExit("before first publication")
        return original(path, target)

    monkeypatch.setattr(candidate, "_publish_new", interrupted)
    with pytest.raises(SystemExit):
        build(initial)
    monkeypatch.setattr(candidate, "_publish_new", original)
    return initial.product.parent / ".source-candidate-transaction"


@pytest.mark.parametrize("tamper", ["unknown_product", "extra_secret", "receipt", "plan", "stage"])
def test_recovery_never_adopts_unknown_or_changed_content(initial, monkeypatch, tamper):
    transaction = interrupted_transaction(initial, monkeypatch)
    if tamper == "unknown_product":
        initial.product.mkdir()
        (initial.product / "mine.txt").write_text("user content", encoding="utf-8")
    elif tamper == "extra_secret":
        (transaction / "candidate/product/.env").write_text("PRIVATE=secret", encoding="utf-8")
    elif tamper == "receipt":
        (transaction / "candidate/native-generation.json").write_text("{}", encoding="utf-8")
    elif tamper == "plan":
        initial.plan = initial.plan.model_copy(update={"title": "different approval"})
    else:
        (transaction / "candidate/product/business.py").write_text("tampered", encoding="utf-8")
    with pytest.raises(PrerequisiteError):
        build(initial)
    if tamper == "unknown_product":
        assert (initial.product / "mine.txt").read_text(encoding="utf-8") == "user content"


def test_completed_transaction_does_not_block_legitimate_refresh(initial):
    receipt = build(initial)
    receipt = candidate.refresh_candidate(initial.product, receipt, pending_steps=["new review"])
    assert (
        native.managed_generate(initial.settings, "fastapiadmin", initial.plan, initial.product)
        == receipt
    )
    assert json.loads((initial.product.parent / "design.json").read_text(encoding="utf-8")) == {
        "approved": True
    }


@pytest.mark.parametrize("item", ["product", "verification.json", "native-generation.json"])
def test_real_process_exit_after_publication_can_resume(tmp_path, plan, monkeypatch, item):
    import subprocess
    import sys

    plan = plan.model_copy(update={"data_scope": "shared"})
    root = tmp_path / "child"
    root.mkdir()
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(plan.model_dump_json(), encoding="utf-8")
    script = r"""
import os, runpy, sys
from pathlib import Path
import pytest
from workbench.core.contracts import Plan
ns = runpy.run_path(sys.argv[1])
root = Path(sys.argv[2])
plan = Plan.model_validate_json(Path(sys.argv[3]).read_text(encoding="utf-8"))
fixture = ns["initial"].__wrapped__(root, pytest.MonkeyPatch(), plan)
candidate = ns["candidate"]
original = candidate._publish_new
def crash(path, target):
    result = original(path, target)
    if Path(target) == fixture.product.parent / sys.argv[4]:
        os._exit(73)
    return result
candidate._publish_new = crash
ns["build"](fixture)
"""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(Path(__file__).resolve()),
            str(root),
            str(plan_path),
            item,
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 73, result.stderr

    def forbidden(*args, **kwargs):
        raise AssertionError("Process recovery must precede runtime selection")

    monkeypatch.setattr(native, "generation_capability", forbidden)
    product = root / "run/product"
    receipt = native.managed_generate(SimpleNamespace(), "fastapiadmin", plan, product)
    assert candidate.verify_candidate(product, receipt)["source_checks_passed"]
    assert not (product.parent / ".source-candidate-transaction").exists()


@pytest.mark.parametrize("directory", [False, True])
def test_no_replace_preserves_existing_even_empty_target(tmp_path, directory):
    source, target = tmp_path / "source", tmp_path / "target"
    if directory:
        source.mkdir()
        target.mkdir()
        (source / "business.txt").write_text("source", encoding="utf-8")
    else:
        source.write_text("source", encoding="utf-8")
        target.write_text("user content", encoding="utf-8")
    with pytest.raises(FileExistsError):
        candidate._publish_new(source, target)
    if directory:
        assert list(target.iterdir()) == []
    else:
        assert target.read_text(encoding="utf-8") == "user content"
    assert source.exists()


@pytest.mark.parametrize("item", ["product", "native-generation.json"])
def test_target_created_after_preflight_is_not_overwritten(initial, monkeypatch, item):
    original = candidate._publish_new

    def raced(source, target):
        if Path(target) == initial.product.parent / item:
            if item == "product":
                Path(target).mkdir()
            else:
                Path(target).write_text("user content", encoding="utf-8")
        return original(source, target)

    monkeypatch.setattr(candidate, "_publish_new", raced)
    with pytest.raises(FileExistsError):
        build(initial)
    target = initial.product.parent / item
    assert (
        (list(target.iterdir()) == [])
        if item == "product"
        else target.read_text(encoding="utf-8") == "user content"
    )


@pytest.mark.parametrize("window", ["marker", "retire"])
@pytest.mark.parametrize("after", [False, True])
def test_marker_publication_and_retirement_failures_are_recoverable(
    initial, monkeypatch, window, after
):
    original = candidate._publish_new
    raised = False

    def interrupted(source, target):
        nonlocal raised
        match = (
            (Path(target).name == ".source-candidate-transaction")
            if window == "marker"
            else (Path(source).name == ".source-candidate-transaction")
        )
        if match and not raised:
            raised = True
            if after:
                original(source, target)
            raise SystemExit("marker interruption")
        return original(source, target)

    monkeypatch.setattr(candidate, "_publish_new", interrupted)
    with pytest.raises(SystemExit):
        build(initial)
    monkeypatch.setattr(candidate, "_publish_new", original)
    monkeypatch.setattr(
        native, "generation_capability", lambda *args: {"available": False, "reason": "offline"}
    )
    result = native.managed_generate(
        initial.settings, "fastapiadmin", initial.plan, initial.product
    )
    assert result["execution"] == "source-candidate"
    assert not (initial.product.parent / ".source-candidate-transaction").exists()


@pytest.mark.parametrize("after", [False, True])
def test_git_journal_publication_resumes_without_git(initial, monkeypatch, after):
    if not REAL_WHICH("git"):
        pytest.skip("Git is required")
    monkeypatch.setattr(candidate.shutil, "which", REAL_WHICH)
    original = candidate._publish_new
    interrupted = False

    def crash(source, target):
        nonlocal interrupted
        if Path(target) == initial.product.parent / "source-revisions" and not interrupted:
            interrupted = True
            if after:
                original(source, target)
            raise SystemExit("journal interrupted")
        return original(source, target)

    monkeypatch.setattr(candidate, "_publish_new", crash)
    with pytest.raises(SystemExit):
        build(initial)
    transaction = initial.product.parent / ".source-candidate-transaction"
    sealed_report = (transaction / "candidate/verification.json").read_bytes()
    monkeypatch.setattr(candidate, "_publish_new", original)
    monkeypatch.setattr(candidate.shutil, "which", lambda _: None)
    receipt = candidate.recover_candidate("fastapiadmin", initial.plan, initial.product)
    assert receipt["source_commit"]["status"] == "committed"
    assert (initial.product.parent / "verification.json").read_bytes() == sealed_report
    assert (
        candidate.verify_candidate(initial.product, receipt)["source_commit"]["status"]
        == "unavailable"
    )
````
