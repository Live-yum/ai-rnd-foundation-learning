# tests/test_source_candidate_delivery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.delivery`、`workbench.filesystem`、`workbench.generation.native.service`、`workbench.generation.python_basic`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_plan`（L18–L26）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan`。 返回路径：L19的`Plan( title="任务", data_scope="shared", acceptance=["CRUD"], entities=[ {"name": "task", "d…`。
- `minimal_candidate`（L29–L47）：接收`tmp_path`、`monkeypatch`、`verification`。 调用`product.mkdir`、`(product / "example.py").write_text`、`monkeypatch.setattr`、`source_candidate.refresh_candidate`、`digest`、`native_plan().model_dump`、`native_plan`。 返回路径：L47的`product, receipt`。
- `test_candidate_package_keeps_truth_and_filters_secrets`（L51–L68）：接收`tmp_path`、`monkeypatch`、`verification`。 控制顺序：L58断言`report["passed"] is False`；L59断言`report["source_checks_passed"] is True`；L61断言`delivery["verification_status"] == verification`；L62断言`delivery["runtime_verified"] is delivery["production_ready"] is False`；L63断言`delivery["source_commit"]["status"] == "unavailable"`；L65断言`not {".env", "credentials.json", "logs/private.log"} & set(archive.namelist())`；L67断言`status["verification_status"] == verification`；L68断言`status["generation_status"] == "partial"`。 调用`minimal_candidate`、`(product / ".env").write_text`、`(product / "credentials.json").write_text`、`(product / "logs").mkdir`、`(product / "logs/private.log").write_text`、`verify_native`、`package_native`、`zipfile.ZipFile`、`set`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changed_sources_and_forged_runtime_report_fail_closed`（L71–L78）：接收`tmp_path`、`monkeypatch`。 调用`minimal_candidate`、`verify_native`、`pytest.raises`、`package_native`、`(product / "example.py").write_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_candidate_retry_reuses_receipt_without_generation`（L81–L88）：接收`tmp_path`、`monkeypatch`、`settings`。 控制顺序：L88断言`native.managed_generate(settings, "fastapiadmin", native_plan(), product) == receipt`。 调用`minimal_candidate`、`monkeypatch.setattr`、`native.managed_generate`、`native_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_candidate_retry_reuses_receipt_without_generation.forbidden`（L84–L85）：接收`*args`、`**kwargs`。 控制顺序：L85抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_runtime_sources_and_recovery_checkpoint_remain_unchanged`（L91–L118）：接收`tmp_path`、`monkeypatch`。 控制顺序：L111断言`receipt["verification_status"] == "failed"`；L112断言`receipt["generation_status"] == "complete"`；L113断言`manifest(product) == before`；L114断言`checkpoint.read_bytes() == raw`；L117断言`json.loads(archive.read("SOURCE-STATUS.json"))["verification_status"] == "failed"`；L118断言`manifest(product) == before`。 调用`product.mkdir`、`(product / "actual.py").write_text`、`manifest`、`write_json`、`checkpoint.read_bytes`、`monkeypatch.setattr`、`source_candidate.retain_failed_candidate`、`native_plan`、`package_native`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_integrity_error_not_reclassified`（L121–L130）：接收`tmp_path`、`monkeypatch`。 控制顺序：L130断言`not (tmp_path / "native-generation.json").exists()`。 调用`product.mkdir`、`(product / "changed.py").write_text`、`write_json`、`pytest.raises`、`source_candidate.retain_failed_candidate`、`native_plan`、`(tmp_path / "native-generation.json").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_git_snapshot_is_traceable_and_replayed`（L133–L149）：接收`tmp_path`。 控制顺序：L134按`not source_candidate.shutil.which("git")`分支；L140断言`first["status"] == "committed"`；L141断言`source_candidate.source_snapshot(product) == first`；L149断言`result.stdout == "value = 3\n"`。 调用`source_candidate.shutil.which`、`pytest.skip`、`product.mkdir`、`(product / "source.py").write_text`、`source_candidate.source_snapshot`、`subprocess.run`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_snapshot_integrity_race_is_not_a_git_failure`（L152–L167）：接收`tmp_path`、`monkeypatch`。 调用`product.mkdir`、`(product / "source.py").write_text`、`monkeypatch.setattr`、`pytest.raises`、`source_candidate.source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_snapshot_integrity_race_is_not_a_git_failure.raced_git`（L160–L163）：接收`work`、`home`、`*args`。 控制顺序：L161按`args[0] == "rev-parse"`分支。 调用`(product / "source.py").write_text`。 返回路径：L163的`{"log": "a" * 40}`。
- `test_unclassified_or_permission_runtime_failure_cannot_become_candidate`（L171–L197）：接收`settings`、`monkeypatch`、`error`。 控制顺序：L197断言`not (product.parent / "native-generation.json").exists()`。 调用`monkeypatch.setattr`、`source.mkdir`、`(source / "code.py").write_text`、`str`、`monkeypatch.setitem`、`SimpleNamespace`、`pytest.raises`、`type`、`native.managed_generate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unclassified_or_permission_runtime_failure_cannot_become_candidate.fail`（L188–L189）：接收`*args`、`**kwargs`。 控制顺序：L189抛异常，停止当前正常路径。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permission_failure_of_services_does_not_generate_fallback`（L200–L216）：接收`settings`、`monkeypatch`。 控制顺序：L216断言`not product.exists()`。 调用`monkeypatch.setattr`、`monkeypatch.setitem`、`SimpleNamespace`、`pytest.raises`、`native.managed_generate`、`native_plan`、`product.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permission_failure_of_services_does_not_generate_fallback.denied`（L209–L210）：接收`*args`。 控制顺序：L210抛异常，停止当前正常路径。 调用`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fixed_tool_runner_preserves_actual_process_permission_denial`（L219–L227）：接收`tmp_path`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.raises`、`tools.run_command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fixed_tool_runner_preserves_actual_process_permission_denial.denied`（L222–L223）：接收`*args`、`**kwargs`。 控制顺序：L223抛异常，停止当前正常路径。 调用`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_runtime_generates_actual_sources_without_processes`（L231–L259）：接收`settings`、`monkeypatch`、`platform`。 控制顺序：L254断言`receipt["execution"] == "source-candidate"`；L255断言`receipt["verification_status"] == "unverified"`；L256断言`receipt["generation_status"] == "partial"`；L257断言`(product / "backend/app/plugin/module_rnd/task/controller.py").is_file()`；L258断言`len(receipt["generated_files"]) >= 8`；L259断言`native.managed_generate(settings, "fastapiadmin", native_plan(), product) == receipt`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`native.managed_generate`、`native_plan`、`(product / "backend/app/plugin/module_rnd/task/controller.py").is…`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_runtime_generates_actual_sources_without_processes.unavailable`（L241–L242）：接收`name`。 控制顺序：L242抛异常，停止当前正常路径。 调用`ImportError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_runtime_generates_actual_sources_without_processes.no_execution`（L248–L249）：接收`*args`、`**kwargs`。 控制顺序：L249抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `committed_candidate`（L263–L281）：接收`tmp_path`。 控制顺序：L264按`not source_candidate.shutil.which("git")`分支；L280断言`receipt["source_commit"]["status"] == "committed"`。 调用`source_candidate.shutil.which`、`pytest.skip`、`product.mkdir`、`(product / "source.py").write_text`、`source_candidate.refresh_candidate`。 返回路径：L281的`product, receipt`。
- `test_verify_and_package_revalidate_committed_candidate`（L287–L306）：接收`committed_candidate`、`tamper`。 控制顺序：L291按`tamper == "commit"`分支；L293按`tamper == "digest"`分支；L295按`tamper == "journal"`分支；L297按`tamper == "missing-journal"`分支；L306断言`not (product.parent / "native-source.zip").exists()`。 调用`verify_native`、`journal.parent.rename`、`journal.parent.with_name`、`(journal / ".git").rename`、`write_json`、`pytest.raises`、`package_native`、`(product.parent / "native-source.zip").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verification_without_git_removes_previously_committed_claim`（L309–L319）：接收`committed_candidate`、`monkeypatch`。 控制顺序：L315断言`report["source_commit"]["status"] == "unavailable"`；L316断言`"commit" not in report["source_commit"]`；L318断言`"commit" not in result["source_commit"]`；L319断言`result["runtime_verified"] is False`。 调用`monkeypatch.setattr`、`verify_native`、`package_native`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_uncommitted_receipt_cannot_smuggle_commit_into_delivery`（L322–L328）：接收`tmp_path`、`monkeypatch`。 控制顺序：L327断言`"commit" not in report["source_commit"]`；L328断言`"journal" not in package_native(product, report)["source_commit"]`。 调用`minimal_candidate`、`receipt["source_commit"].update`、`write_json`、`verify_native`、`package_native`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_source_candidate_delivery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L328。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13575`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_source_candidate_delivery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "004dc52629698849d14e9f2d0b0d7fbd8b6afcd6e878766cdb283a6fc06a26a9"} -->
````python
# tests/test_source_candidate_delivery.py
"""Source preservation is portable; no runtime acceptance is inferred from a ZIP/commit."""

import json
import subprocess
import sys
import zipfile
from types import SimpleNamespace

import pytest

from workbench.core.contracts import Plan, digest
from workbench.delivery import native, source_candidate
from workbench.filesystem import manifest, write_json
from workbench.generation.native.service import package_native, verify_native
from workbench.generation.python_basic import PrerequisiteError


def native_plan():
    return Plan(
        title="任务",
        data_scope="shared",
        acceptance=["CRUD"],
        entities=[
            {"name": "task", "description": "任务", "fields": [{"name": "title", "kind": "text"}]}
        ],
    )


def minimal_candidate(tmp_path, monkeypatch, verification="unverified"):
    product = tmp_path / "product"
    product.mkdir()
    (product / "example.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: None)
    receipt = source_candidate.refresh_candidate(
        product,
        {
            "template": "fastapiadmin",
            "execution": "source-candidate",
            "spec_digest": digest(native_plan().model_dump()),
            "generation_status": "partial",
            "verification_status": verification,
            "pending_steps": ["运行验收"],
            "runtime_unavailable_reason": "无执行环境",
            "generated_files": ["example.py"],
        },
    )
    return product, receipt


@pytest.mark.parametrize("verification", ["unverified", "failed"])
def test_candidate_package_keeps_truth_and_filters_secrets(tmp_path, monkeypatch, verification):
    product, receipt = minimal_candidate(tmp_path, monkeypatch, verification)
    (product / ".env").write_text("SECRET=not-for-export", encoding="utf-8")
    (product / "credentials.json").write_text("secret", encoding="utf-8")
    (product / "logs").mkdir()
    (product / "logs/private.log").write_text("secret", encoding="utf-8")
    report = verify_native(product)
    assert report["passed"] is False
    assert report["source_checks_passed"] is True
    delivery = package_native(product, report)
    assert delivery["verification_status"] == verification
    assert delivery["runtime_verified"] is delivery["production_ready"] is False
    assert delivery["source_commit"]["status"] == "unavailable"
    with zipfile.ZipFile(product.parent / delivery["package"]) as archive:
        assert not {".env", "credentials.json", "logs/private.log"} & set(archive.namelist())
        status = json.loads(archive.read("SOURCE-STATUS.json"))
        assert status["verification_status"] == verification
        assert status["generation_status"] == "partial"


def test_changed_sources_and_forged_runtime_report_fail_closed(tmp_path, monkeypatch):
    product, _ = minimal_candidate(tmp_path, monkeypatch)
    report = verify_native(product)
    with pytest.raises(PrerequisiteError):
        package_native(product, {**report, "passed": True})
    (product / "example.py").write_text("changed", encoding="utf-8")
    with pytest.raises(PrerequisiteError):
        verify_native(product)


def test_candidate_retry_reuses_receipt_without_generation(tmp_path, monkeypatch, settings):
    product, receipt = minimal_candidate(tmp_path, monkeypatch)

    def forbidden(*args, **kwargs):
        raise AssertionError("Replay must not execute or regenerate")

    monkeypatch.setattr(native, "runtime_capability", forbidden)
    assert native.managed_generate(settings, "fastapiadmin", native_plan(), product) == receipt


def test_failed_runtime_sources_and_recovery_checkpoint_remain_unchanged(tmp_path, monkeypatch):
    product = tmp_path / "product"
    product.mkdir()
    (product / "actual.py").write_text("print('generated business source')\n", encoding="utf-8")
    before = manifest(product)
    checkpoint = tmp_path / "native-evidence/recovery.json"
    write_json(
        checkpoint,
        {
            "files": before,
            "targets": [{"entity": "task"}],
            "stage": "validation-interrupted",
            "resumable": True,
        },
    )
    raw = checkpoint.read_bytes()
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: None)
    receipt = source_candidate.retain_failed_candidate(
        "fastapiadmin", native_plan(), product, [], "ToolFailure"
    )
    assert receipt["verification_status"] == "failed"
    assert receipt["generation_status"] == "complete"
    assert manifest(product) == before
    assert checkpoint.read_bytes() == raw
    delivery = package_native(product, verify_native(product))
    with zipfile.ZipFile(tmp_path / delivery["package"]) as archive:
        assert json.loads(archive.read("SOURCE-STATUS.json"))["verification_status"] == "failed"
    assert manifest(product) == before


def test_runtime_integrity_error_not_reclassified(tmp_path, monkeypatch):
    product = tmp_path / "product"
    product.mkdir()
    (product / "changed.py").write_text("modified\n", encoding="utf-8")
    write_json(tmp_path / "native-evidence/recovery.json", {"files": {}, "targets": [1]})
    with pytest.raises(PrerequisiteError):
        source_candidate.retain_failed_candidate(
            "fastapiadmin", native_plan(), product, [], "ToolFailure"
        )
    assert not (tmp_path / "native-generation.json").exists()


def test_real_git_snapshot_is_traceable_and_replayed(tmp_path):
    if not source_candidate.shutil.which("git"):
        pytest.skip("Git not installed")
    product = tmp_path / "product"
    product.mkdir()
    (product / "source.py").write_text("value = 3\n", encoding="utf-8")
    first = source_candidate.source_snapshot(product)
    assert first["status"] == "committed"
    assert source_candidate.source_snapshot(product) == first
    journal = tmp_path / first["journal"]
    result = subprocess.run(
        ["git", "-C", str(journal), "show", first["commit"] + ":source.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout == "value = 3\n"


def test_git_snapshot_integrity_race_is_not_a_git_failure(tmp_path, monkeypatch):
    from workbench.coding import aider

    product = tmp_path / "product"
    product.mkdir()
    (product / "source.py").write_text("original\n", encoding="utf-8")
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: "git")

    def raced_git(work, home, *args):
        if args[0] == "rev-parse":
            (product / "source.py").write_text("raced\n", encoding="utf-8")
        return {"log": "a" * 40}

    monkeypatch.setattr(aider, "git", raced_git)
    with pytest.raises(PrerequisiteError, match="发生变化"):
        source_candidate.source_snapshot(product)


@pytest.mark.parametrize("error", [PermissionError("denied"), AssertionError("unclassified")])
def test_unclassified_or_permission_runtime_failure_cannot_become_candidate(
    settings, monkeypatch, error
):
    from workbench.generation.native import service

    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: True)
    monkeypatch.setattr(
        native, "runtime_config", lambda *args: (None, "postgresql://localhost/test_codegen")
    )
    source = settings.data_dir / "source"
    source.mkdir(parents=True)
    (source / "code.py").write_text("source\n", encoding="utf-8")
    monkeypatch.setattr(
        service, "prepare_sources", lambda *args: [{"slot": "fastapiadmin", "path": str(source)}]
    )

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=fail)
    )
    product = settings.data_dir / "runs/failure/product"
    with pytest.raises(type(error)):
        native.managed_generate(settings, "fastapiadmin", native_plan(), product)
    assert not (product.parent / "native-generation.json").exists()


def test_permission_failure_of_services_does_not_generate_fallback(settings, monkeypatch):
    from workbench.infrastructure.native import resources

    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=None)
    )
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: False)

    def denied(*args):
        raise PermissionError("denied")

    monkeypatch.setattr(resources, "for_run", denied)
    product = settings.data_dir / "runs/failure/product"
    with pytest.raises(PermissionError):
        native.managed_generate(settings, "fastapiadmin", native_plan(), product)
    assert not product.exists()


def test_fixed_tool_runner_preserves_actual_process_permission_denial(tmp_path, monkeypatch):
    from workbench.infrastructure.processes import tools

    def denied(*args, **kwargs):
        raise PermissionError("process permission denied")

    monkeypatch.setattr(tools.subprocess, "Popen", denied)
    with pytest.raises(PermissionError):
        tools.run_command(["git", "--version"], tmp_path)


@pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
def test_missing_runtime_generates_actual_sources_without_processes(
    settings, monkeypatch, platform
):
    # Native host tests also run this file in the CI OS matrix; these simulated
    # capability cases are not a substitute for actual Windows/macOS execution.
    monkeypatch.setattr(native, "sys", SimpleNamespace(platform=platform))
    monkeypatch.setattr(
        native, "os", SimpleNamespace(name="nt" if platform == "win32" else "posix")
    )

    def unavailable(name):
        raise ImportError(name)

    monkeypatch.setattr(native, "import_module", unavailable)
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: None)
    from workbench.infrastructure.processes import tools

    def no_execution(*args, **kwargs):
        raise AssertionError("No command or product code may run in source generation")

    monkeypatch.setattr(tools, "run_command", no_execution)
    product = settings.data_dir / "runs/offline/product"
    receipt = native.managed_generate(settings, "fastapiadmin", native_plan(), product)
    assert receipt["execution"] == "source-candidate"
    assert receipt["verification_status"] == "unverified"
    assert receipt["generation_status"] == "partial"
    assert (product / "backend/app/plugin/module_rnd/task/controller.py").is_file()
    assert len(receipt["generated_files"]) >= 8
    assert native.managed_generate(settings, "fastapiadmin", native_plan(), product) == receipt


@pytest.fixture
def committed_candidate(tmp_path):
    if not source_candidate.shutil.which("git"):
        pytest.skip("Git is required for candidate journal verification")
    product = tmp_path / "product"
    product.mkdir()
    (product / "source.py").write_text("value = 3\n", encoding="utf-8")
    receipt = source_candidate.refresh_candidate(
        product,
        {
            "template": "fastapiadmin",
            "execution": "source-candidate",
            "generation_status": "partial",
            "verification_status": "unverified",
            "pending_steps": ["运行验证"],
            "runtime_unavailable_reason": "unavailable",
        },
    )
    assert receipt["source_commit"]["status"] == "committed"
    return product, receipt


@pytest.mark.parametrize(
    "tamper", ["commit", "digest", "journal", "missing-journal", "missing-git"]
)
def test_verify_and_package_revalidate_committed_candidate(committed_candidate, tamper):
    product, receipt = committed_candidate
    report = verify_native(product)
    journal = product.parent / receipt["source_commit"]["journal"]
    if tamper == "commit":
        receipt["source_commit"]["commit"] = "f" * 40
    elif tamper == "digest":
        receipt["source_commit"]["source_digest"] = "f" * 64
    elif tamper == "journal":
        receipt["source_commit"]["journal"] = "../../forged"
    elif tamper == "missing-journal":
        journal.parent.rename(journal.parent.with_name("removed-journal"))
    else:
        (journal / ".git").rename(journal / "removed-git")
    write_json(product.parent / "native-generation.json", receipt)
    with pytest.raises(PrerequisiteError):
        verify_native(product)
    with pytest.raises(PrerequisiteError):
        package_native(product, report)
    assert not (product.parent / "native-source.zip").exists()


def test_verification_without_git_removes_previously_committed_claim(
    committed_candidate, monkeypatch
):
    product, _ = committed_candidate
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: None)
    report = verify_native(product)
    assert report["source_commit"]["status"] == "unavailable"
    assert "commit" not in report["source_commit"]
    result = package_native(product, report)
    assert "commit" not in result["source_commit"]
    assert result["runtime_verified"] is False


def test_uncommitted_receipt_cannot_smuggle_commit_into_delivery(tmp_path, monkeypatch):
    product, receipt = minimal_candidate(tmp_path, monkeypatch)
    receipt["source_commit"].update(commit="f" * 40, journal="../../forged")
    write_json(product.parent / "native-generation.json", receipt)
    report = verify_native(product)
    assert "commit" not in report["source_commit"]
    assert "journal" not in package_native(product, report)["source_commit"]
````
