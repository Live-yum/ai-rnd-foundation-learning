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
