# tests/test_ci_acceptance_gate.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.ci_evidence`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `successful_jobs`（L18–L19）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L19的`{name: {"result": "success"} for name in gate.REQUIRED_JOBS}`。
- `stage_receipt`（L22–L30）：接收`folder`、`name`。 调用`write_json`、`gate.stage_binding`、`gate.file_hashes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `make_shard`（L33–L132）：接收`folder`、`binding`、`index`、`count`、`nodeids`。 控制顺序：L80遍历`selected`；L98按`binding["origin"] == "restored"`分支。 调用`shards.partition`、`write_json`、`digest`、`len`、`ET.Element`、`ET.SubElement`、`str`、`ET.ElementTree(root).write`、`ET.ElementTree`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `make_artifacts`（L135–L194）：接收`tmp_path`、`count`。 控制顺序：L138遍历`gate.STAGES.items()`；L141遍历`paths`；L142按`path.startswith("restored-source/")`分支；L166遍历`("browser", "install")`；L177遍历`gate.STAGES`；L179遍历`[ ("source", "linux", "ubuntu-latest"), ("source", "win32", "wind…`；L190遍历`range(count)`。 调用`gate.STAGES.items`、`stage.mkdir`、`path.startswith`、`target.parent.mkdir`、`target.write_text`、`source.mkdir`、`(source / "app.py").write_bytes`、`create_source_artifact`、`write_json`等。 返回路径：L194的`folder`。
- `test_complete_three_platform_origin_groups_pass_with_exact_union`（L198–L210）：接收`tmp_path`、`count`。 控制顺序：L202断言`result["passed"] is True`；L203断言`len(result["groups"]) == 3`；L204断言`all( group["collected"] == 8 and group["passed"] == 8 and group["skipped"] == 0 and g…`。 调用`gate.aggregate`、`make_artifacts`、`successful_jobs`、`len`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_each_unsuccessful_required_job_fails_before_reading_artifacts`（L215–L219）：接收`tmp_path`、`name`、`state`。 调用`successful_jobs`、`pytest.raises`、`gate.aggregate`、`pytest.mark.parametrize`、`sorted`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_or_incomplete_dependency_snapshot_is_rejected`（L225–L238）：接收`damage`。 控制顺序：L227按`damage == "missing"`分支；L229按`damage == "extra"`分支；L231按`damage == "not-dict"`分支；L233按`damage == "missing-result"`分支。 调用`successful_jobs`、`jobs.pop`、`pytest.raises`、`gate.require_jobs`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_artifact_inventory_must_be_exact`（L244–L258）：接收`tmp_path`、`damage`。 控制顺序：L247按`damage == "missing-shard"`分支；L249按`damage == "missing-stage"`分支；L251按`damage == "old-attempt"`分支；L253按`damage == "duplicate"`分支。 调用`make_artifacts`、`shutil.rmtree`、`shard.rename`、`shutil.copytree`、`(folder / "unexpected").mkdir`、`pytest.raises`、`gate.aggregate`、`successful_jobs`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stage_evidence_is_complete_current_and_byte_bound`（L274–L292）：接收`tmp_path`、`damage`。 控制顺序：L279按`damage == "missing-stage-receipt"`分支；L281按`damage == "changed-file"`分支；L283按`damage == "extra-file"`分支；L285按`damage == "bool-version"`分支。 调用`make_artifacts`、`read_json`、`receipt.unlink`、`(stage / "postgres.xml").write_text`、`(stage / "extra.txt").write_text`、`write_json`、`damage.removeprefix`、`pytest.raises`、`gate.aggregate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preparation_is_not_substituted_for_complete_acceptance`（L309–L318）：接收`tmp_path`、`field`、`bad`。 调用`make_artifacts`、`read_json`、`write_json`、`stage_receipt`、`pytest.raises`、`gate.aggregate`、`successful_jobs`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_each_restored_phase_requires_its_own_current_success`（L333–L342）：接收`tmp_path`、`phase`、`field`、`bad`。 调用`make_artifacts`、`read_json`、`write_json`、`stage_receipt`、`pytest.raises`、`gate.aggregate`、`successful_jobs`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_even_rebound_malformed_reconstruction_archive_is_rejected`（L345–L351）：接收`tmp_path`。 调用`make_artifacts`、`(stage / "restored-source/source.zip").write_bytes`、`stage_receipt`、`pytest.raises`、`gate.aggregate`、`successful_jobs`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_one_shard_cannot_silently_collect_a_different_inventory`（L355–L362）：接收`tmp_path`、`group`。 调用`make_artifacts`、`read_json`、`shutil.rmtree`、`make_shard`、`pytest.raises`、`gate.aggregate`、`successful_jobs`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_restored_group_cannot_consistently_drop_source_tests`（L365–L373）：接收`tmp_path`。 控制顺序：L367遍历`range(4)`。 调用`make_artifacts`、`range`、`read_json`、`shutil.rmtree`、`make_shard`、`pytest.raises`、`gate.aggregate`、`successful_jobs`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_has_independent_complete_gates_and_always_run_fail_closed_aggregate`（L376–L409）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L380断言`set(jobs["acceptance"]["needs"]) == gate.REQUIRED_JOBS`；L381断言`jobs["acceptance"]["if"] == "always()"`；L382断言`jobs["delivery"]["needs"] == "acceptance"`；L383断言`jobs["tests"]["strategy"]["matrix"] == { "os": ["ubuntu-latest", "windows-latest"], "…`；L387断言`jobs["restored-tests"]["strategy"]["matrix"]["shard"] == list(range(shards.SHARDS))`；L388遍历`["tests", "source-validation", "clean-install", "restored-tests"]`；L389断言`jobs[name]["strategy"]["fail-fast"] is False`；L390遍历`gate.REQUIRED_JOBS`。后续分支沿下方源码相同行号继续阅读。 调用`Path(__file__).resolve`、`Path`、`(root / ".github/workflows/test.yml").read_text`、`yaml.safe_load`、`set`、`list`、`range`、`job.get`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_ci_acceptance_gate.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L409。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14983`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_ci_acceptance_gate.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "90dd8b58d77bdf6aa21704bd2e01f20b64cdb232776b14bd8270abe8d855614f"} -->
````python
# tests/test_ci_acceptance_gate.py
"""Cross-job acceptance is fail-closed, including skipped/missing Actions evidence."""

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

from scripts import ci_acceptance as gate
from scripts import ci_pytest as shards
from scripts.ci_evidence import create_source_artifact, digest, read_json, write_json

BINDING = {"head": "a" * 40, "run": "123", "attempt": "2"}
NODEIDS = [f"tests/test_example.py::test_{i}" for i in range(8)]


def successful_jobs():
    return {name: {"result": "success"} for name in gate.REQUIRED_JOBS}


def stage_receipt(folder, name):
    write_json(
        folder / "stage.json",
        {
            "version": 1,
            "binding": gate.stage_binding(BINDING, name),
            "files": gate.file_hashes(folder),
        },
    )


def make_shard(folder, binding, index, count, nodeids):
    selected = shards.partition(nodeids, index, count)
    write_json(folder / "context.json", {"binding": binding, "index": index, "count": count})
    write_json(
        folder / "inventory.json",
        {
            "version": 1,
            "binding": binding,
            "selection": "not postgres",
            "index": index,
            "count": count,
            "nodeids": nodeids,
            "selected": selected,
            "inventory_digest": digest(nodeids),
            "selected_digest": digest(selected),
        },
    )
    write_json(
        folder / "outcomes.json",
        {
            "version": 1,
            "binding": binding,
            "exitstatus": 0,
            "collected": len(selected),
            "selected_digest": digest(selected),
            "outcomes": {
                name: {"setup": "passed", "call": "passed", "teardown": "passed"}
                for name in selected
            },
        },
    )
    write_json(
        folder / "process.json",
        {
            "version": 1,
            "binding": binding,
            "timed_out": False,
            "returncode": 0,
            "error_type": None,
            "cleanup_error_type": None,
            "junit_available": True,
        },
    )
    root = ET.Element("testsuites")
    suite = ET.SubElement(
        root, "testsuite", tests=str(len(selected)), failures="0", errors="0", skipped="0"
    )
    for name in selected:
        case = ET.SubElement(suite, "testcase", name=name)
        properties = ET.SubElement(case, "properties")
        ET.SubElement(properties, "property", name="ci_nodeid", value=name)
    ET.ElementTree(root).write(folder / "junit.xml")
    (folder / "pytest.log").write_text("complete\n")
    (folder / "coverage.xml").write_text("<coverage/>")
    write_json(
        folder / "complete.json",
        {
            "version": 1,
            "binding": binding,
            "index": index,
            "count": count,
            "files": shards.evidence_hashes(folder),
        },
    )

    if binding["origin"] == "restored":
        from scripts.ci_restored import seal_restored_shard

        lifecycle = {key: binding[key] for key in ("head", "run", "attempt", "source_digest")}
        process = {
            "timeout_seconds": 900,
            "returncode": 0,
            "timed_out": False,
            "error_type": None,
            "cleanup_error_type": None,
        }
        write_json(
            folder / "restored.json",
            {
                "binding": lifecycle,
                "phase": "tests",
                "passed": True,
                "step": "complete",
                "original_project_imported": False,
                "python_environment": "independent locked student-project venv",
                "process": process,
            },
        )
        write_json(
            folder / "bootstrap.json",
            {
                "binding": {key: binding[key] for key in ("head", "run", "attempt")},
                "source_digest": binding["source_digest"],
                "phase": "tests",
                "passed": True,
                "step": "complete",
                "process": {**process, "timeout_seconds": 3300},
            },
        )
        seal_restored_shard(folder, lifecycle, index, count)


def make_artifacts(tmp_path, count=4):
    folder = tmp_path / "artifacts"
    prefix = "acceptance-2-"
    for name, paths in gate.STAGES.items():
        stage = folder / (prefix + name)
        stage.mkdir(parents=True)
        for path in paths:
            if path.startswith("restored-source/"):
                continue
            target = stage / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}", encoding="utf-8")
    source = tmp_path / "source"
    source.mkdir()
    (source / "app.py").write_bytes(b"# reconstructed source\n")
    prepare = folder / (prefix + "handbook-only")
    manifest = create_source_artifact(source, ["app.py"], prepare / "restored-source", BINDING)
    source_digest = manifest["source_digest"]
    write_json(
        prepare / "learning-docs-clean-room.json",
        {
            "source_digest": source_digest,
            "prepared": True,
            "tests_executed": False,
            "passed": False,
            "phase": "prepared_for_independent_acceptance",
            "original_project_imported": False,
            "original_archives_copied": False,
            "python_environment": "independent locked student-project venv",
        },
    )
    for phase in ("browser", "install"):
        write_json(
            folder / (prefix + "restored-" + phase) / "restored/restored.json",
            {
                "binding": {**BINDING, "source_digest": source_digest},
                "phase": phase,
                "passed": True,
                "original_project_imported": False,
                "python_environment": "independent locked student-project venv",
            },
        )
    for name in gate.STAGES:
        stage_receipt(folder / (prefix + name), name)
    for origin, platform, os_name in [
        ("source", "linux", "ubuntu-latest"),
        ("source", "win32", "windows-latest"),
        ("restored", "linux", "ubuntu-latest"),
    ]:
        binding = {
            **BINDING,
            "origin": origin,
            "platform": platform,
            "source_digest": BINDING["head"] if origin == "source" else source_digest,
        }
        for index in range(count):
            make_shard(
                folder / (prefix + f"{origin}-{os_name}-{index}"), binding, index, count, NODEIDS
            )
    return folder


@pytest.mark.parametrize("count", [1, 2, 4, 8])
def test_complete_three_platform_origin_groups_pass_with_exact_union(tmp_path, count):
    result = gate.aggregate(
        make_artifacts(tmp_path, count), successful_jobs(), BINDING, count=count
    )
    assert result["passed"] is True
    assert len(result["groups"]) == 3
    assert all(
        group["collected"] == 8
        and group["passed"] == 8
        and group["skipped"] == 0
        and group["shards"] == count
        for group in result["groups"]
    )


@pytest.mark.parametrize("state", ["failure", "cancelled", "skipped", None, True, "Success", ""])
@pytest.mark.parametrize("name", sorted(gate.REQUIRED_JOBS))
def test_each_unsuccessful_required_job_fails_before_reading_artifacts(tmp_path, name, state):
    jobs = successful_jobs()
    jobs[name]["result"] = state
    with pytest.raises(ValueError, match="failed, cancelled or skipped"):
        gate.aggregate(tmp_path / "never-needed", jobs, BINDING)


@pytest.mark.parametrize(
    "damage", ["missing", "extra", "not-dict", "missing-result", "malformed-job"]
)
def test_malformed_or_incomplete_dependency_snapshot_is_rejected(damage):
    jobs = successful_jobs()
    if damage == "missing":
        jobs.pop("browser")
    elif damage == "extra":
        jobs["unexpected"] = {"result": "success"}
    elif damage == "not-dict":
        jobs = []
    elif damage == "missing-result":
        jobs["browser"] = {}
    else:
        jobs["browser"] = "success"
    with pytest.raises(ValueError):
        gate.require_jobs(jobs)


@pytest.mark.parametrize(
    "damage", ["missing-shard", "missing-stage", "extra", "old-attempt", "duplicate"]
)
def test_artifact_inventory_must_be_exact(tmp_path, damage):
    folder = make_artifacts(tmp_path)
    shard = folder / "acceptance-2-source-ubuntu-latest-0"
    if damage == "missing-shard":
        shutil.rmtree(shard)
    elif damage == "missing-stage":
        shutil.rmtree(folder / "acceptance-2-browser")
    elif damage == "old-attempt":
        shard.rename(folder / "acceptance-1-source-ubuntu-latest-0")
    elif damage == "duplicate":
        shutil.copytree(shard, folder / "duplicate")
    else:
        (folder / "unexpected").mkdir()
    with pytest.raises(ValueError, match="acceptance artifacts"):
        gate.aggregate(folder, successful_jobs(), BINDING)


@pytest.mark.parametrize(
    "damage",
    [
        "missing-stage-receipt",
        "changed-file",
        "extra-file",
        "wrong-head",
        "wrong-run",
        "wrong-attempt",
        "wrong-platform",
        "bool-version",
    ],
)
def test_stage_evidence_is_complete_current_and_byte_bound(tmp_path, damage):
    folder = make_artifacts(tmp_path)
    stage = folder / "acceptance-2-postgres"
    receipt = stage / "stage.json"
    value = read_json(receipt)
    if damage == "missing-stage-receipt":
        receipt.unlink()
    elif damage == "changed-file":
        (stage / "postgres.xml").write_text("different")
    elif damage == "extra-file":
        (stage / "extra.txt").write_text("unexpected")
    elif damage == "bool-version":
        value["version"] = True
        write_json(receipt, value)
    else:
        value["binding"][damage.removeprefix("wrong-")] = "wrong"
        write_json(receipt, value)
    with pytest.raises((ValueError, FileNotFoundError)):
        gate.aggregate(folder, successful_jobs(), BINDING)


@pytest.mark.parametrize(
    "field,bad",
    [
        ("prepared", False),
        ("prepared", "true"),
        ("passed", True),
        ("tests_executed", True),
        ("source_digest", "wrong"),
        ("original_project_imported", True),
        ("original_archives_copied", True),
        ("python_environment", "original venv"),
        ("phase", "complete"),
    ],
)
def test_preparation_is_not_substituted_for_complete_acceptance(tmp_path, field, bad):
    folder = make_artifacts(tmp_path)
    stage = folder / "acceptance-2-handbook-only"
    path = stage / "learning-docs-clean-room.json"
    value = read_json(path)
    value[field] = bad
    write_json(path, value)
    stage_receipt(stage, "handbook-only")
    with pytest.raises(ValueError, match="genuine reconstruction"):
        gate.aggregate(folder, successful_jobs(), BINDING)


@pytest.mark.parametrize("phase", ["browser", "install"])
@pytest.mark.parametrize(
    "field,bad",
    [
        ("passed", False),
        ("passed", 1),
        ("phase", "other"),
        ("original_project_imported", True),
        ("python_environment", "source venv"),
        ("binding", {}),
    ],
)
def test_each_restored_phase_requires_its_own_current_success(tmp_path, phase, field, bad):
    folder = make_artifacts(tmp_path)
    stage = folder / ("acceptance-2-restored-" + phase)
    path = stage / "restored/restored.json"
    value = read_json(path)
    value[field] = bad
    write_json(path, value)
    stage_receipt(stage, "restored-" + phase)
    with pytest.raises(ValueError, match="Restored acceptance"):
        gate.aggregate(folder, successful_jobs(), BINDING)


def test_even_rebound_malformed_reconstruction_archive_is_rejected(tmp_path):
    folder = make_artifacts(tmp_path)
    stage = folder / "acceptance-2-handbook-only"
    (stage / "restored-source/source.zip").write_bytes(b"not a source archive")
    stage_receipt(stage, "handbook-only")
    with pytest.raises(ValueError, match="archive byte mismatch"):
        gate.aggregate(folder, successful_jobs(), BINDING)


@pytest.mark.parametrize("group", ["source-ubuntu-latest", "restored-ubuntu-latest"])
def test_one_shard_cannot_silently_collect_a_different_inventory(tmp_path, group):
    folder = make_artifacts(tmp_path)
    shard = folder / ("acceptance-2-" + group + "-3")
    binding = read_json(shard / "context.json")["binding"]
    shutil.rmtree(shard)
    make_shard(shard, binding, 3, 4, NODEIDS + ["tests/test_extra.py::test_new"])
    with pytest.raises(ValueError, match="disagree"):
        gate.aggregate(folder, successful_jobs(), BINDING)


def test_restored_group_cannot_consistently_drop_source_tests(tmp_path):
    folder = make_artifacts(tmp_path)
    for index in range(4):
        shard = folder / f"acceptance-2-restored-ubuntu-latest-{index}"
        binding = read_json(shard / "context.json")["binding"]
        shutil.rmtree(shard)
        make_shard(shard, binding, index, 4, NODEIDS[:-1])
    with pytest.raises(ValueError, match="lost or added"):
        gate.aggregate(folder, successful_jobs(), BINDING)


def test_workflow_has_independent_complete_gates_and_always_run_fail_closed_aggregate():
    root = Path(__file__).resolve().parents[1]
    text = (root / ".github/workflows/test.yml").read_text(encoding="utf-8")
    jobs = yaml.safe_load(text)["jobs"]
    assert set(jobs["acceptance"]["needs"]) == gate.REQUIRED_JOBS
    assert jobs["acceptance"]["if"] == "always()"
    assert jobs["delivery"]["needs"] == "acceptance"
    assert jobs["tests"]["strategy"]["matrix"] == {
        "os": ["ubuntu-latest", "windows-latest"],
        "shard": list(range(shards.SHARDS)),
    }
    assert jobs["restored-tests"]["strategy"]["matrix"]["shard"] == list(range(shards.SHARDS))
    for name in ["tests", "source-validation", "clean-install", "restored-tests"]:
        assert jobs[name]["strategy"]["fail-fast"] is False
    for name in gate.REQUIRED_JOBS:
        job = jobs[name]
        assert not job.get("continue-on-error")
        assert all(not step.get("continue-on-error") for step in job["steps"])
        uploads = [
            step for step in job["steps"] if step.get("uses") == "actions/upload-artifact@v4"
        ]
        assert len(uploads) == 1
        assert uploads[0]["if"] == "always()"
        assert uploads[0]["with"]["if-no-files-found"] == "error"
        assert "${{ github.run_attempt }}" in uploads[0]["with"]["name"]
    assert jobs["handbook-only"].get("needs") is None
    for name in ["restored-tests", "restored-browser", "restored-install"]:
        assert jobs[name]["needs"] == "handbook-only"
        commands = "\n".join(step.get("run", "") for step in jobs[name]["steps"])
        assert "uv run --no-project python -m scripts.ci_restored" in commands
        assert "--artifact .ci-artifact/restored-source" in commands
    assert "pytest -m postgres -q" in text
    assert 'pytest -m "not postgres"' not in text
    assert "--count 4" in text and "--index ${{ matrix.shard }}" in text
````
