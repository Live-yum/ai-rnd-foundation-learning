# tests/test_ci_native_capability_source.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.ci_native_capability_security`、`scripts.daytona_native_capability_profile`、`scripts.extension_oracles`、`workbench`、`workbench.capability_dependencies`、`workbench.capability_verification`、`workbench.domain`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `product`（L31–L36）：接收`baseline_product`。 控制顺序：L32遍历`DESCRIPTORS`。 调用`atomic_text`、`name.endswith`。 返回路径：L36的`baseline_product`。
- `accepted`（L39–L50）：接收`archive`。 返回路径：L40的`{ "generated_runtime_verified": True, "portable_restored": { "passed": True, "fresh_databa…`。
- `ready`（L53–L57）：接收`product`、`tmp_path`。 调用`handoff.SourceHandoff`、`state.capture`、`manifest`、`state.complete`、`accepted`。 返回路径：L57的`state`。
- `test_exact_source_handoff_preserves_all_bytes_descriptors_and_public_examples`（L61–L75）：接收`product`、`tmp_path`。 控制顺序：L67断言`receipt["inventory"] == original == manifest(state.product) == manifest(product)`；L68断言`receipt["source_identity"] == digest(original)`；L70断言`inputs["source_identity"] == receipt["source_identity"]`；L71断言`inputs["descriptors"] == receipt["descriptors"]`；L72断言`receipt["source_archive_sha256"] == "a" * 64`；L73断言`(state.product / "frontend/web/.env.production.example").exists()`。 调用`manifest`、`ready`、`handoff.require_handoff`、`digest`、`product_inputs`、`(state.product / "frontend/web/.env.production.example").exists`、`profile_record`、`require_dependency_descriptors`、`fixed_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_dirty_candidate_stays_rejected_while_independent_clean_handoff_is_admitted`（L82–L94）：接收`product`、`tmp_path`、`relative`。 控制顺序：L92断言`not (tmp_path / "must-not-exist").exists()`；L94断言`(product / relative).is_dir()`。 调用`ready`、`(product / relative).mkdir`、`profile_record`、`pytest.raises`、`require_dependency_descriptors`、`fixed_plan`、`handoff.copy_exact_source`、`(tmp_path / "must-not-exist").exists`、`(product / relative).is_dir`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_capture_rejects_every_uninventoried_physical_entry`（L112–L139）：接收`product`、`tmp_path`、`mutation`。 控制顺序：L115按`mutation == "extra"`分支；L117按`mutation == "missing"`分支；L119按`mutation == "bytes"`分支；L121按`mutation == "empty-dir"`分支；L123按`mutation == "ignored-dir"`分支；L125按`mutation == "secret"`分支；L127按`mutation == "symlink"`分支；L130按`mutation == "hardlink"`分支。后续分支沿下方源码相同行号继续阅读。 调用`manifest`、`atomic_text`、`path.unlink`、`path.write_text`、`(product / "empty").mkdir`、`path.symlink_to`、`os.link`、`os.mkfifo`、`handoff.SourceHandoff`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_copy_detects_mutations_between_preflight_and_copy`（L146–L175）：接收`product`、`tmp_path`、`monkeypatch`、`mutation`。 调用`manifest`、`monkeypatch.setattr`、`pytest.raises`、`handoff.copy_exact_source`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_copy_detects_mutations_between_preflight_and_copy.changing`（L154–L171）：接收`root`、`expected`。 控制顺序：L158按`calls == 1`分支；L160按`mutation == "source-byte"`分支；L162按`mutation == "source-link"`分支；L165按`mutation == "source-directory-link"`分支；L169按`calls == 2 and mutation == "destination-extra"`分支。 调用`real`、`path.write_text`、`path.unlink`、`path.symlink_to`、`old.rename`、`old.symlink_to`、`atomic_text`。 返回路径：L171的`result`。
- `test_fd_read_rejects_link_swap_after_stat_without_reading_target`（L179–L200）：接收`product`、`tmp_path`、`monkeypatch`。 控制顺序：L200断言`target.read_text() == "must not be copied"`。 调用`target.write_text`、`manifest`、`monkeypatch.setattr`、`pytest.raises`、`handoff.require_exact_source`、`target.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fd_read_rejects_link_swap_after_stat_without_reading_target.swap`（L188–L194）：接收`directory`、`name`、`expected`。 控制顺序：L190按`name == "__init__.py" and not changed`分支。 调用`path.unlink`、`path.symlink_to`、`real`。 返回路径：L194的`real(directory, name, expected)`。
- `test_failed_completion_never_publishes_readiness`（L207–L224）：接收`product`、`tmp_path`、`mutation`。 控制顺序：L209按`mutation != "uncaptured"`分支；L212按`mutation == "source"`分支；L214按`mutation == "descriptor"`分支；L216按`mutation == "archive"`分支；L218按`mutation == "different-archive"`分支；L220按`mutation == "acceptance"`分支；L224断言`json.loads(state.receipt.read_text())["passed"] is False`。 调用`handoff.SourceHandoff`、`state.capture`、`manifest`、`accepted`、`atomic_text`、`(state.product / "backend/uv.lock").write_text`、`pytest.raises`、`state.complete`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stale_receipt_invalidated_without_overwriting_or_deleting_existing_source`（L228–L238）：接收`product`、`tmp_path`。 控制顺序：L235断言`manifest(state.product) == original`；L236断言`json.loads(state.receipt.read_text())["passed"] is False`。 调用`ready`、`manifest`、`pytest.raises`、`handoff.SourceHandoff`、`json.loads`、`state.receipt.read_text`、`handoff.require_handoff`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_consumer_rejects_stale_or_tampered_readiness`（L255–L278）：接收`product`、`tmp_path`、`monkeypatch`、`mutation`。 控制顺序：L258按`mutation == "run"`分支；L260按`mutation.startswith("receipt-") and mutation in {"receipt-hash", "receipt-descriptor"…`分支；L261按`mutation == "receipt-hash"`分支；L266按`mutation == "source"`分支；L268按`mutation == "dependencies"`分支；L270按`mutation == "receipt-fifo"`分支；L273按`mutation == "receipt-hardlink"`分支。 调用`ready`、`json.loads`、`state.receipt.read_text`、`monkeypatch.setenv`、`mutation.startswith`、`write_json`、`(state.product / "backend/app/__init__.py").write_text`、`(state.product / "backend/.venv").mkdir`、`state.receipt.unlink`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `portable_runtime`（L282–L296）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`Connection`。 返回路径：L296的`operations`。
- `portable_runtime.Connection`（L285–L293）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `portable_runtime.Connection.__enter__`（L286–L287）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L287的`self`。
- `portable_runtime.Connection.__exit__`（L289–L290）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `portable_runtime.Connection.execute`（L292–L293）：接收`statement`。 调用`operations.append`、`statement.as_string`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_capture_precedes_independent_build_and_never_readies_failed_acceptance`（L303–L370）：接收`product`、`tmp_path`、`monkeypatch`、`portable_runtime`、`failure`。 控制顺序：L341按`failure == "roundtrip-extra"`分支；L350按`failure is None`分支；L354断言`events == ["capture", "independent-build"]`；L359断言`manifest(state.product) == inventory`；L360断言`(product / "backend/.venv/leave-intact").exists()`；L366断言`json.loads(state.receipt.read_text())["passed"] is False`；L367断言`len(portable_runtime) == 2`；L368断言`portable_runtime[0].startswith('CREATE DATABASE "restore_')`。后续分支沿下方源码相同行号继续阅读。 调用`manifest`、`handoff.SourceHandoff`、`atomic_text`、`monkeypatch.setattr`、`portable.verify_native_delivery`、`accepted`、`report["portable_restored"].update`、`state.complete`、`handoff.require_handoff`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_capture_precedes_independent_build_and_never_readies_failed_acceptance.capture`（L313–L320）：接收`clean`、`expected`、`archive_sha256`。 控制顺序：L314断言`expected == inventory`；L315按`failure != "roundtrip-extra"`分支；L316断言`not (clean / "backend/.venv").exists()`；L317断言`not (clean / "frontend/web/node_modules").exists()`；L319断言`json.loads(state.receipt.read_text())["passed"] is False`。 调用`(clean / "backend/.venv").exists`、`(clean / "frontend/web/node_modules").exists`、`state.capture`、`json.loads`、`state.receipt.read_text`、`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_capture_precedes_independent_build_and_never_readies_failed_acceptance.run`（L322–L338）：接收`command`、`cwd`、`*args`、`**kwargs`。 控制顺序：L324断言`events == ["capture"]`；L328按`failure == "launch"`分支；L329抛异常，停止当前正常路径；L330按`failure == "archive-drift"`分支；L332按`failure == "original-drift"`分支。 调用`copies.append`、`events.append`、`atomic_text`、`RuntimeError`、`(cwd.parent / "delivery.zip").write_bytes`、`(product / "backend/uv.lock").write_text`、`write_json`。 返回路径：L338的`{"log": "mocked launcher evidence only"}`。
- `test_capture_precedes_independent_build_and_never_readies_failed_acceptance.extra`（L344–L347）：接收`archive`、`destination`、`**kwargs`。 调用`original_unpack`、`(destination / "backend/.venv").mkdir`。 返回路径：L347的`result`。
- `test_native_tools_finalizes_only_after_all_acceptance_and_outcome_write`（L376–L459）：接收`product`、`tmp_path`、`monkeypatch`、`failure`。 控制顺序：L443按`failure == "outcome-write"`分支；L451按`failure is None`分支；L454断言`json.loads((reports / "toolchain-acceptance.json").read_text())["passed"] is True`；L458断言`json.loads(receipt.read_text())["passed"] is False`；L459断言`manifest(product)`。 调用`monkeypatch.setattr`、`write_json`、`monkeypatch.setenv`、`str`、`native_tools.main`、`handoff.validate_receipt`、`json.loads`、`receipt.read_text`、`(reports / "toolchain-acceptance.json").read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_tools_finalizes_only_after_all_acceptance_and_outcome_write.fixture_copy`（L386–L389）：接收`source`、`destination`、`inventory`。 控制顺序：L387断言`manifest(source) == inventory`。 调用`manifest`、`shutil.copytree`。 返回路径：L389的`destination`。
- `test_native_tools_finalizes_only_after_all_acceptance_and_outcome_write.fixture_inventory`（L391–L393）：接收`source`、`inventory`。 控制顺序：L392断言`manifest(source) == inventory`。 调用`manifest`。 返回路径：L393的`inventory`。
- `test_native_tools_finalizes_only_after_all_acceptance_and_outcome_write.run`（L420–L440）：接收`*args`、`**kwargs`。 控制顺序：L423断言`json.loads(receipt.read_text())["passed"] is False`；L424按`calls == 1`分支；L427按`calls == 2`分支；L429按`failure == "before-capture"`分支；L430抛异常，停止当前正常路径；L432按`failure == "after-capture"`分支；L433抛异常，停止当前正常路径。 调用`json.loads`、`receipt.read_text`、`write_json`、`kwargs["customization"]`、`native_lab.generated_permissions`、`RuntimeError`、`kwargs["source_handoff"]`、`manifest`、`accepted`。 返回路径：L440的`accepted()`。
- `test_native_tools_finalizes_only_after_all_acceptance_and_outcome_write.write`（L445–L448）：接收`path`、`value`。 控制顺序：L446按`path.name == "toolchain-acceptance.json"`分支；L447抛异常，停止当前正常路径。 调用`OSError`、`write_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_contest_adds_only_authored_inventory_and_keeps_registered_baseline_exact`（L463–L480）：接收`product`、`tmp_path`。 控制顺序：L471断言`set(augmented) - set(baseline["inventory"]) == { "backend/app/plugin/module_rnd/__ini…`；L475断言`handoff.descriptors(augmented) == baseline["descriptors"]`；L476断言`manifest(state.product) == baseline["inventory"]`；L477断言`(target / "frontend/web/.env.production.example").exists()`。 调用`ready`、`handoff.require_handoff`、`handoff.copy_exact_source`、`contest_ci.install_authored_fixture`、`set`、`manifest`、`handoff.descriptors`、`(target / "frontend/web/.env.production.example").exists`、`require_dependency_descriptors`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_contest_consumer_uses_same_ready_profile_source_without_filtering`（L487–L550）：接收`product`、`tmp_path`、`monkeypatch`、`mutation`。 控制顺序：L493按`mutation == "wrong-profile-source"`分支；L495按`mutation == "dirty-baseline"`分支；L536按`mutation is None`分支；L538断言`events == ["client", "verify", "close"]`；L539断言`json.loads((tmp_path / "reports/contest-capability.json").read_text())["passed"] is T…`；L545断言`json.loads((tmp_path / "reports/contest-capability.json").read_text())["passed"] is F…`；L549按`mutation in {"wrong-profile-source", "dirty-baseline"}`分支；L550断言`events == []`。 调用`ready`、`profile_record`、`product_inputs`、`str`、`(state.product / "backend/.venv").mkdir`、`monkeypatch.setattr`、`copy.deepcopy`、`events.append`、`object`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_contest_consumer_uses_same_ready_profile_source_without_filtering.verify`（L514–L533）：接收`root`、`plan`、`*args`、`**kwargs`。 控制顺序：L519断言`handoff.descriptors(inventory) == record["inputs"]["descriptors"]`。 调用`events.append`、`manifest`、`handoff.require_exact_source`、`require_dependency_descriptors`、`handoff.descriptors`、`digest`、`list`、`dict.fromkeys`。 返回路径：L520的`{ "passed": True, "cleanup": "deleted", "source_digest": "f" * 64 if mutation == "proof-dr…`。
- `test_workflow_binds_all_consumers_to_one_clean_product_and_receipt`（L553–L564）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L555断言`"ci_native_tools fastapiadmin --capability-source .native/capability-source" in workf…`；L556遍历`( "ci_native_capability_source", "daytona_native_capability_profi…`；L562断言`command + " --product .native/capability-source" in workflow`；L563断言`workflow.count("--source-receipt reports/native-tools/capability-source.json") == 2`；L564断言`"prepare --product .native/tool-product" not in workflow`。 调用`(handoff.ROOT / ".github/workflows/native-capability-profile.yml"…`、`workflow.count`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inventory_schema_rejects_non_source_and_ambiguous_paths_on_all_platforms`（L588–L590）：接收`inventory`。 调用`pytest.raises`、`handoff.validate_inventory`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_receipt_schema_and_binding_are_portable`（L597–L630）：接收`product`、`monkeypatch`、`mutation`。 控制顺序：L610按`mutation == "schema"`分支；L612按`mutation == "passed"`分支；L614按`mutation == "path"`分支；L616按`mutation == "run"`分支；L618按`mutation == "identity"`分支；L620按`mutation == "descriptor"`分支；L622按`mutation == "archive"`分支；L624按`mutation == "extra"`分支。后续分支沿下方源码相同行号继续阅读。 调用`manifest`、`str`、`digest`、`handoff.descriptors`、`handoff.run_identity`、`monkeypatch.setenv`、`handoff.validate_receipt`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unsupported_platform_fails_closed_before_opening_source`（L633–L637）：接收`tmp_path`、`monkeypatch`。 调用`monkeypatch.delattr`、`pytest.raises`、`handoff.directory_fd`、`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_parent_traversal_roots_fail_before_any_write`（L640–L652）：接收`product`、`tmp_path`。 控制顺序：L645断言`manifest(product) == inventory`；L646断言`not (product / "unused").exists()`；L647断言`not (product / "new-source").exists()`；L652断言`receipt.read_text() == "existing receipt"`。 调用`manifest`、`pytest.raises`、`handoff.copy_exact_source`、`(product / "unused").exists`、`(product / "new-source").exists`、`receipt.write_text`、`handoff.SourceHandoff`、`receipt.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cli_rejects_overlapping_original_and_handoff_before_any_writes`（L656–L687）：接收`product`、`tmp_path`、`monkeypatch`、`relation`。 控制顺序：L685断言`manifest(product) == inventory`；L686断言`not root.exists()`；L687断言`not (product / "new-handoff").exists()`。 调用`manifest`、`monkeypatch.setattr`、`str`、`pytest.fail`、`pytest.raises`、`native_tools.main`、`root.exists`、`(product / "new-handoff").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_ci_native_capability_source.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L687。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`26607`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_ci_native_capability_source.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2d42d1dbe82953171f4608fd3ba0e2410abce25681832799604133aa5fe450f3"} -->
````python
# tests/test_ci_native_capability_source.py
"""CI source handoff contracts only; no live container/native acceptance claims."""

import copy
import json
import os
import shutil

import pytest
from capability_dependency_fixtures import profile_record
from test_ci_native_capability_security import product as baseline_product  # noqa: F401

from scripts import ci_contest_capability as contest_ci
from scripts import ci_native_capability_source as handoff
from scripts import ci_native_tools as native_tools
from scripts.ci_native_capability_security import fixed_plan
from scripts.daytona_native_capability_profile import DESCRIPTORS, product_inputs
from scripts.extension_oracles import contest
from workbench import filesystem, native_lab, portable, tools
from workbench.capability_dependencies import require_dependency_descriptors
from workbench.capability_verification import CheckFailure
from workbench.domain import digest
from workbench.filesystem import atomic_text, manifest, write_json

posix_filesystem = pytest.mark.skipif(
    not hasattr(os, "O_NOFOLLOW"), reason="CI native source handoff requires POSIX no-follow FDs"
)
URL = "postgresql+psycopg://native:ci-only@127.0.0.1/native_codegen"


@pytest.fixture
def product(baseline_product):  # noqa: F811 - imported pytest fixture
    for name in DESCRIPTORS:
        atomic_text(baseline_product / name, "{}\n" if name.endswith(".json") else "# exact lock\n")
    atomic_text(baseline_product / "frontend/web/.env.production.example", "VITE_PUBLIC=example\n")
    atomic_text(baseline_product / "start.py", "# authored CI source, never run by these tests\n")
    return baseline_product


def accepted(archive="a" * 64):
    return {
        "generated_runtime_verified": True,
        "portable_restored": {
            "passed": True,
            "fresh_database": True,
            "standalone_launcher": True,
            "archive_round_trip": True,
            "source_archive_sha256": archive,
            "business_rules": {"passed": True},
        },
    }


def ready(product, tmp_path):
    state = handoff.SourceHandoff(tmp_path / "clean-ci", tmp_path / "source-ready.json")
    state.capture(product, manifest(product), "a" * 64)
    state.complete(accepted(), product)
    return state


@posix_filesystem
def test_exact_source_handoff_preserves_all_bytes_descriptors_and_public_examples(
    product, tmp_path
):
    original = manifest(product)
    state = ready(product, tmp_path)
    receipt = handoff.require_handoff(state.product, state.receipt)
    assert receipt["inventory"] == original == manifest(state.product) == manifest(product)
    assert receipt["source_identity"] == digest(original)
    inputs = product_inputs(state.product)
    assert inputs["source_identity"] == receipt["source_identity"]
    assert inputs["descriptors"] == receipt["descriptors"]
    assert receipt["source_archive_sha256"] == "a" * 64
    assert (state.product / "frontend/web/.env.production.example").exists()
    record = profile_record(state.product, "fastapiadmin")
    require_dependency_descriptors(state.product, fixed_plan(state.product), record)


@pytest.mark.parametrize(
    "relative", [".venv", "backend/.venv", "node_modules", "frontend/web/node_modules"]
)
@posix_filesystem
def test_dirty_candidate_stays_rejected_while_independent_clean_handoff_is_admitted(
    product, tmp_path, relative
):
    state = ready(product, tmp_path)
    (product / relative).mkdir(parents=True)
    record = profile_record(product, "fastapiadmin")
    with pytest.raises(CheckFailure, match="虚拟环境或依赖目录"):
        require_dependency_descriptors(product, fixed_plan(product), record)
    with pytest.raises(ValueError, match="extra directory"):
        handoff.copy_exact_source(product, tmp_path / "must-not-exist", state.inventory)
    assert not (tmp_path / "must-not-exist").exists()
    require_dependency_descriptors(state.product, fixed_plan(state.product), record)
    assert (product / relative).is_dir()


@pytest.mark.parametrize(
    "mutation",
    [
        "extra",
        "missing",
        "bytes",
        "empty-dir",
        "ignored-dir",
        "secret",
        "symlink",
        "hardlink",
        "fifo",
    ],
)
@posix_filesystem
def test_capture_rejects_every_uninventoried_physical_entry(product, tmp_path, mutation):
    inventory = manifest(product)
    path = product / "backend/app/__init__.py"
    if mutation == "extra":
        atomic_text(product / "backend/app/new_import.py", "extra")
    elif mutation == "missing":
        path.unlink()
    elif mutation == "bytes":
        path.write_text("changed")
    elif mutation == "empty-dir":
        (product / "empty").mkdir()
    elif mutation == "ignored-dir":
        atomic_text(product / "backend/logs/hidden.py", "extra")
    elif mutation == "secret":
        atomic_text(product / ".env", "DUMMY=not-a-credential")
    elif mutation == "symlink":
        path.unlink()
        path.symlink_to(product / "start.py")
    elif mutation == "hardlink":
        os.link(path, tmp_path / "hardlink")
    else:
        path.unlink()
        os.mkfifo(path)
    state = handoff.SourceHandoff(tmp_path / "clean", tmp_path / "receipt.json")
    with pytest.raises((ValueError, OSError)):
        state.capture(product, inventory, "a" * 64)
    assert json.loads(state.receipt.read_text())["passed"] is False
    assert not state.product.exists()


@pytest.mark.parametrize(
    "mutation", ["source-byte", "source-link", "source-directory-link", "destination-extra"]
)
@posix_filesystem
def test_copy_detects_mutations_between_preflight_and_copy(
    product, tmp_path, monkeypatch, mutation
):
    inventory = manifest(product)
    destination = tmp_path / "new"
    real = handoff.require_exact_source
    calls = 0

    def changing(root, expected):
        nonlocal calls
        result = real(root, expected)
        calls += 1
        if calls == 1:
            path = product / "backend/app/__init__.py"
            if mutation == "source-byte":
                path.write_text("changed after preflight")
            elif mutation == "source-link":
                path.unlink()
                path.symlink_to(tmp_path / "outside")
            elif mutation == "source-directory-link":
                old = product / "backend/app"
                old.rename(tmp_path / "original-app")
                old.symlink_to(tmp_path / "original-app", target_is_directory=True)
        if calls == 2 and mutation == "destination-extra":
            atomic_text(destination / "hidden.py", "extra")
        return result

    monkeypatch.setattr(handoff, "require_exact_source", changing)
    with pytest.raises((ValueError, OSError)):
        handoff.copy_exact_source(product, destination, inventory)


@posix_filesystem
def test_fd_read_rejects_link_swap_after_stat_without_reading_target(
    product, tmp_path, monkeypatch
):
    target = tmp_path / "outside"
    target.write_text("must not be copied")
    path = product / "backend/app/__init__.py"
    real = handoff.read_regular
    changed = False

    def swap(directory, name, expected=None):
        nonlocal changed
        if name == "__init__.py" and not changed:
            changed = True
            path.unlink()
            path.symlink_to(target)
        return real(directory, name, expected)

    inventory = manifest(product)
    monkeypatch.setattr(handoff, "read_regular", swap)
    with pytest.raises(OSError):
        handoff.require_exact_source(product, inventory)
    assert target.read_text() == "must not be copied"


@pytest.mark.parametrize(
    "mutation", ["source", "descriptor", "archive", "different-archive", "acceptance", "uncaptured"]
)
@posix_filesystem
def test_failed_completion_never_publishes_readiness(product, tmp_path, mutation):
    state = handoff.SourceHandoff(tmp_path / "clean", tmp_path / "receipt.json")
    if mutation != "uncaptured":
        state.capture(product, manifest(product), "a" * 64)
    report = accepted()
    if mutation == "source":
        atomic_text(product / "new.py", "changed source")
    elif mutation == "descriptor":
        (state.product / "backend/uv.lock").write_text("changed lock")
    elif mutation == "archive":
        report["portable_restored"]["source_archive_sha256"] = "not a hash"
    elif mutation == "different-archive":
        report["portable_restored"]["source_archive_sha256"] = "b" * 64
    elif mutation == "acceptance":
        report["portable_restored"]["passed"] = False
    with pytest.raises(ValueError):
        state.complete(report, product)
    assert json.loads(state.receipt.read_text())["passed"] is False


@posix_filesystem
def test_stale_receipt_invalidated_without_overwriting_or_deleting_existing_source(
    product, tmp_path
):
    state = ready(product, tmp_path)
    original = manifest(state.product)
    with pytest.raises(FileExistsError):
        handoff.SourceHandoff(state.product, state.receipt)
    assert manifest(state.product) == original
    assert json.loads(state.receipt.read_text())["passed"] is False
    with pytest.raises(ValueError):
        handoff.require_handoff(state.product, state.receipt)


@pytest.mark.parametrize(
    "mutation",
    [
        "run",
        "receipt-hash",
        "receipt-descriptor",
        "source",
        "dependencies",
        "receipt-fifo",
        "receipt-hardlink",
        "duplicate-key",
    ],
)
@posix_filesystem
def test_consumer_rejects_stale_or_tampered_readiness(product, tmp_path, monkeypatch, mutation):
    state = ready(product, tmp_path)
    value = json.loads(state.receipt.read_text())
    if mutation == "run":
        monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "changed")
    elif mutation.startswith("receipt-") and mutation in {"receipt-hash", "receipt-descriptor"}:
        if mutation == "receipt-hash":
            value["source_identity"] = "f" * 64
        else:
            value["descriptors"]["backend/uv.lock"] = "f" * 64
        write_json(state.receipt, value)
    elif mutation == "source":
        (state.product / "backend/app/__init__.py").write_text("tampered")
    elif mutation == "dependencies":
        (state.product / "backend/.venv").mkdir()
    elif mutation == "receipt-fifo":
        state.receipt.unlink()
        os.mkfifo(state.receipt)
    elif mutation == "receipt-hardlink":
        os.link(state.receipt, tmp_path / "linked-receipt")
    else:
        state.receipt.write_text('{"passed":false,' + state.receipt.read_text()[1:])
    with pytest.raises((ValueError, OSError)):
        handoff.require_handoff(state.product, state.receipt)


@pytest.fixture
def portable_runtime(monkeypatch):
    operations = []

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, statement):
            operations.append(statement.as_string())

    monkeypatch.setattr(portable.psycopg, "connect", lambda *args, **kwargs: Connection())
    return operations


@pytest.mark.parametrize(
    "failure", [None, "launch", "archive-drift", "original-drift", "roundtrip-extra"]
)
@posix_filesystem
def test_capture_precedes_independent_build_and_never_readies_failed_acceptance(
    product, tmp_path, monkeypatch, portable_runtime, failure
):
    inventory = manifest(product)
    state = handoff.SourceHandoff(tmp_path / "clean-ci", tmp_path / "ready.json")
    events, copies = [], []
    # The native generator's existing buildtree is intentionally dirty.
    atomic_text(product / "backend/.venv/leave-intact", "installed")
    atomic_text(product / "frontend/web/node_modules/leave-intact", "installed")

    def capture(clean, expected, archive_sha256):
        assert expected == inventory
        if failure != "roundtrip-extra":
            assert not (clean / "backend/.venv").exists()
            assert not (clean / "frontend/web/node_modules").exists()
        state.capture(clean, expected, archive_sha256)
        assert json.loads(state.receipt.read_text())["passed"] is False
        events.append("capture")

    def run(command, cwd, *args, **kwargs):
        copies.append(cwd)
        assert events == ["capture"]
        events.append("independent-build")
        atomic_text(cwd / "backend/.venv/created-by-launcher", "installed")
        atomic_text(cwd / "frontend/web/node_modules/created-by-launcher", "installed")
        if failure == "launch":
            raise RuntimeError("explicit independent launcher failure")
        if failure == "archive-drift":
            (cwd.parent / "delivery.zip").write_bytes(b"changed archive")
        if failure == "original-drift":
            (product / "backend/uv.lock").write_text("changed lock")
        write_json(
            cwd / ".deployment/reports/portable-start.json",
            {"passed": True, "frontend_started": True, "restart": True},
        )
        return {"log": "mocked launcher evidence only"}

    monkeypatch.setattr(tools, "run_command", run)
    if failure == "roundtrip-extra":
        original_unpack = filesystem.unpack

        def extra(archive, destination, **kwargs):
            result = original_unpack(archive, destination, **kwargs)
            (destination / "backend/.venv").mkdir()
            return result

        monkeypatch.setattr(filesystem, "unpack", extra)
    if failure is None:
        result = portable.verify_native_delivery(
            product, URL, tmp_path / "reports", template="fastapiadmin", source_handoff=capture
        )
        assert events == ["capture", "independent-build"]
        report = accepted()
        report["portable_restored"].update(result)
        state.complete(report, product)
        handoff.require_handoff(state.product, state.receipt)
        assert manifest(state.product) == inventory
        assert (product / "backend/.venv/leave-intact").exists()
    else:
        with pytest.raises((ValueError, RuntimeError)):
            portable.verify_native_delivery(
                product, URL, tmp_path / "reports", template="fastapiadmin", source_handoff=capture
            )
        assert json.loads(state.receipt.read_text())["passed"] is False
    assert len(portable_runtime) == 2
    assert portable_runtime[0].startswith('CREATE DATABASE "restore_')
    assert portable_runtime[1].startswith('DROP DATABASE "restore_')
    assert all(not path.exists() for path in copies)


@pytest.mark.parametrize(
    "failure", [None, "before-capture", "after-capture", "final-assertion", "outcome-write"]
)
def test_native_tools_finalizes_only_after_all_acceptance_and_outcome_write(
    product, tmp_path, monkeypatch, failure
):
    root = tmp_path / "ci"
    reports = root / "reports/native-tools"
    destination = root / "clean-ci"
    receipt = reports / "capability-source.json"

    # Cross-platform CLI ordering test. POSIX physical safety is tested above;
    # this fixture copies only its known synthetic inputs without native tools.
    def fixture_copy(source, destination, inventory):
        assert manifest(source) == inventory
        shutil.copytree(source, destination)
        return destination

    def fixture_inventory(source, inventory):
        assert manifest(source) == inventory
        return inventory

    monkeypatch.setattr(handoff, "copy_exact_source", fixture_copy)
    monkeypatch.setattr(handoff, "require_exact_source", fixture_inventory)
    write_json(receipt, {"passed": True, "stale": True})
    monkeypatch.setattr(native_tools, "ROOT", root)
    monkeypatch.setattr(
        native_tools, "prepare_sources", lambda *a: [{"slot": "fastapiadmin", "path": product}]
    )
    monkeypatch.setattr(native_tools, "native_rule_customizer", lambda *a: lambda *args: None)
    monkeypatch.setattr(
        native_lab, "generated_permissions", lambda *a: {"attempt_id": "interrupted"}
    )
    monkeypatch.setenv("NATIVE_TEST_DATABASE_URL", URL)
    monkeypatch.setattr(
        "sys.argv",
        [
            "ci-native-tools",
            "fastapiadmin",
            "--output",
            str(product),
            "--capability-source",
            str(destination),
        ],
    )
    calls = 0

    def run(*args, **kwargs):
        nonlocal calls
        calls += 1
        assert json.loads(receipt.read_text())["passed"] is False
        if calls == 1:
            write_json(reports / "recovery.json", {"resumable": True, "targets": ["device"]})
            kwargs["customization"]()
        if calls == 2:
            native_lab.generated_permissions()
        if failure == "before-capture":
            raise RuntimeError("before capture")
        kwargs["source_handoff"](product, manifest(product), "a" * 64)
        if failure == "after-capture":
            raise RuntimeError("after capture")
        write_json(reports / "generated/permissions.json", {"attempt_id": "final"})
        write_json(
            reports / "native-coding.json",
            {"passed": True, "repaired": failure != "final-assertion", "attempts": 2},
        )
        write_json(reports / "coding-0.json", {"rolled_back": True, "verified": False})
        return accepted()

    monkeypatch.setattr(native_tools, "run_acceptance", run)
    if failure == "outcome-write":

        def write(path, value):
            if path.name == "toolchain-acceptance.json":
                raise OSError("explicit outcome write failure")
            write_json(path, value)

        monkeypatch.setattr(native_tools, "write_json", write)
    if failure is None:
        native_tools.main()
        handoff.validate_receipt(json.loads(receipt.read_text()), destination)
        assert json.loads((reports / "toolchain-acceptance.json").read_text())["passed"] is True
    else:
        with pytest.raises((RuntimeError, AssertionError, OSError)):
            native_tools.main()
        assert json.loads(receipt.read_text())["passed"] is False
    assert manifest(product)


@posix_filesystem
def test_contest_adds_only_authored_inventory_and_keeps_registered_baseline_exact(
    product, tmp_path
):
    state = ready(product, tmp_path)
    baseline = handoff.require_handoff(state.product, state.receipt)
    target = tmp_path / "contest"
    handoff.copy_exact_source(state.product, target, baseline["inventory"])
    augmented = contest_ci.install_authored_fixture(target)
    assert set(augmented) - set(baseline["inventory"]) == {
        "backend/app/plugin/module_rnd/__init__.py",
        *("backend/app/plugin/module_rnd/contest/" + name for name in manifest(contest_ci.FIXTURE)),
    }
    assert handoff.descriptors(augmented) == baseline["descriptors"]
    assert manifest(state.product) == baseline["inventory"]
    assert (target / "frontend/web/.env.production.example").exists()
    require_dependency_descriptors(
        target, fixed_plan(target), profile_record(state.product, "fastapiadmin")
    )


@pytest.mark.parametrize(
    "mutation", [None, "wrong-profile-source", "dirty-baseline", "proof-drift"]
)
@posix_filesystem
def test_contest_consumer_uses_same_ready_profile_source_without_filtering(
    product, tmp_path, monkeypatch, mutation
):
    state = ready(product, tmp_path)
    record = profile_record(state.product, "fastapiadmin")
    record["inputs"] = product_inputs(state.product)
    if mutation == "wrong-profile-source":
        record["inputs"]["product"] = str(product)
    elif mutation == "dirty-baseline":
        (state.product / "backend/.venv").mkdir()
    events = []
    monkeypatch.setattr(contest_ci, "ROOT", tmp_path)
    monkeypatch.setattr(contest_ci, "install_loopback_guard", lambda: None)
    monkeypatch.setattr(
        contest_ci,
        "capability_execution_prerequisites",
        lambda *a: (tmp_path, copy.deepcopy(record)),
    )
    monkeypatch.setattr(contest_ci, "require_native_profile", lambda *a: record)
    monkeypatch.setattr(contest_ci, "client_for", lambda *a: events.append("client") or object())
    monkeypatch.setattr(contest_ci, "close_client", lambda *a: events.append("close"))
    monkeypatch.setattr(contest_ci, "security_probe_for_profile", lambda *a: None)
    monkeypatch.setattr(
        "sys.argv",
        ["contest", "--product", str(state.product), "--source-receipt", str(state.receipt)],
    )

    def verify(root, plan, *args, **kwargs):
        events.append("verify")
        inventory = manifest(root)
        handoff.require_exact_source(root, inventory)
        require_dependency_descriptors(root, plan, record)
        assert handoff.descriptors(inventory) == record["inputs"]["descriptors"]
        return {
            "passed": True,
            "cleanup": "deleted",
            "source_digest": "f" * 64 if mutation == "proof-drift" else digest(inventory),
            "business_oracle": {
                "protocol": contest.CONTRACT_VERSION,
                "full_request_complete": False,
                "remaining_obligations": list(contest.REMAINING),
                "fresh_replay": True,
                "same_cluster": True,
                "distinct_database_oid": True,
                "witnesses": dict.fromkeys(contest.SEMANTICS, True),
            },
        }

    monkeypatch.setattr(contest_ci, "_verify", verify)
    if mutation is None:
        contest_ci.main()
        assert events == ["client", "verify", "close"]
        assert (
            json.loads((tmp_path / "reports/contest-capability.json").read_text())["passed"] is True
        )
    else:
        with pytest.raises(ValueError):
            contest_ci.main()
        assert (
            json.loads((tmp_path / "reports/contest-capability.json").read_text())["passed"]
            is False
        )
        if mutation in {"wrong-profile-source", "dirty-baseline"}:
            assert events == []


def test_workflow_binds_all_consumers_to_one_clean_product_and_receipt():
    workflow = (handoff.ROOT / ".github/workflows/native-capability-profile.yml").read_text()
    assert "ci_native_tools fastapiadmin --capability-source .native/capability-source" in workflow
    for command in (
        "ci_native_capability_source",
        "daytona_native_capability_profile prepare",
        "ci_native_capability_security",
        "ci_contest_capability",
    ):
        assert command + " --product .native/capability-source" in workflow
    assert workflow.count("--source-receipt reports/native-tools/capability-source.json") == 2
    assert "prepare --product .native/tool-product" not in workflow


@pytest.mark.parametrize(
    "inventory",
    [
        {},
        [],
        {"../escape": "a" * 64},
        {"x": "bad"},
        {"node_modules/a": "a" * 64},
        {"backend/.venv/a": "a" * 64},
        {".env": "a" * 64},
        {"a.pyc": "a" * 64},
        {"a\\x": "a" * 64},
        {"a\x00x": "a" * 64},
        {"a\nx": "a" * 64},
        {"a": "a" * 64, "a/x": "b" * 64},
        {"A": "a" * 64, "a/x": "b" * 64},
        {"A/x": "a" * 64, "a/y": "b" * 64},
        {"A": "a" * 64, "a": "b" * 64},
        {"x" * 4097: "a" * 64},
    ],
)
def test_inventory_schema_rejects_non_source_and_ambiguous_paths_on_all_platforms(inventory):
    with pytest.raises(ValueError):
        handoff.validate_inventory(inventory)


@pytest.mark.parametrize(
    "mutation",
    [None, "schema", "passed", "path", "run", "identity", "descriptor", "archive", "extra"],
)
def test_receipt_schema_and_binding_are_portable(product, monkeypatch, mutation):
    inventory = manifest(product)
    value = {
        "schema": 1,
        "passed": True,
        "provenance": handoff.PROVENANCE,
        "product": str(product),
        "source_identity": digest(inventory),
        "source_archive_sha256": "a" * 64,
        "inventory": inventory,
        "descriptors": handoff.descriptors(inventory),
        "run": handoff.run_identity(),
    }
    if mutation == "schema":
        value["schema"] = True
    elif mutation == "passed":
        value["passed"] = 1
    elif mutation == "path":
        value["product"] += "-different"
    elif mutation == "run":
        monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "a-different-attempt")
    elif mutation == "identity":
        value["source_identity"] = "b" * 64
    elif mutation == "descriptor":
        value["descriptors"]["backend/uv.lock"] = "b" * 64
    elif mutation == "archive":
        value["source_archive_sha256"] = "a" * 63
    elif mutation == "extra":
        value["untrusted"] = True
    if mutation is None:
        assert handoff.validate_receipt(value, product) == value
    else:
        with pytest.raises(ValueError):
            handoff.validate_receipt(value, product)


def test_unsupported_platform_fails_closed_before_opening_source(tmp_path, monkeypatch):
    monkeypatch.delattr(os, "O_NOFOLLOW", raising=False)
    with pytest.raises(ValueError, match="no-follow"):
        with handoff.directory_fd(tmp_path):
            pytest.fail("unsupported platform opened source")


def test_parent_traversal_roots_fail_before_any_write(product, tmp_path):
    inventory = manifest(product)
    path = product / "unused/../new-source"
    with pytest.raises(ValueError, match="parent traversal"):
        handoff.copy_exact_source(product, path, inventory)
    assert manifest(product) == inventory
    assert not (product / "unused").exists()
    assert not (product / "new-source").exists()
    receipt = tmp_path / "unchanged.json"
    receipt.write_text("existing receipt")
    with pytest.raises(ValueError, match="parent traversal"):
        handoff.SourceHandoff(path, receipt)
    assert receipt.read_text() == "existing receipt"


@pytest.mark.parametrize("relation", ["same", "inside-buildtree", "contains-buildtree"])
def test_cli_rejects_overlapping_original_and_handoff_before_any_writes(
    product, tmp_path, monkeypatch, relation
):
    destination = {
        "same": product,
        "inside-buildtree": product / "new-handoff",
        "contains-buildtree": product.parent,
    }[relation]
    inventory = manifest(product)
    root = tmp_path / "controller"
    monkeypatch.setattr(native_tools, "ROOT", root)
    monkeypatch.setattr(
        "sys.argv",
        [
            "ci-native-tools",
            "fastapiadmin",
            "--output",
            str(product),
            "--capability-source",
            str(destination),
        ],
    )
    monkeypatch.setattr(
        native_tools,
        "prepare_sources",
        lambda *a: pytest.fail("native build started before output preflight"),
    )
    with pytest.raises(ValueError, match="independent"):
        native_tools.main()
    assert manifest(product) == inventory
    assert not root.exists()
    assert not (product / "new-handoff").exists()
````
