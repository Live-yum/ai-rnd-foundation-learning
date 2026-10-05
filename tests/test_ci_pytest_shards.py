"""Independent evidence for complete partitions and fail-closed shard acceptance."""

import copy
import hashlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import ci_pytest as shards

ROOT = Path(__file__).resolve().parents[1]
BINDING = {
    "head": "a" * 40,
    "run": "123",
    "attempt": "2",
    "origin": "source",
    "platform": "linux",
    "source_digest": "a" * 40,
}
NODEIDS = [f"tests/test_fixture.py::test_{number:02}" for number in range(16)]


def dump(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def seal(folder, *, binding=None, index=0, count=2):
    value = {
        "version": 1,
        "binding": binding or BINDING,
        "index": index,
        "count": count,
        "files": {
            name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
            for name in shards.EVIDENCE_FILES
        },
    }
    dump(folder / "complete.json", value)


def make_receipt(tmp_path, *, skip_stage="call"):
    folder = tmp_path / "evidence"
    folder.mkdir()
    nodeids = NODEIDS[:4]
    selected = nodeids[::2]
    inventory = {
        "version": 1,
        "binding": dict(BINDING),
        "selection": "not postgres",
        "index": 0,
        "count": 2,
        "nodeids": nodeids,
        "inventory_digest": shards.digest(nodeids),
        "selected": selected,
        "selected_digest": shards.digest(selected),
    }
    passed = {"setup": "passed", "call": "passed", "teardown": "passed"}
    skipped = {"setup": "passed", "call": "skipped", "teardown": "passed"}
    if skip_stage == "setup":
        skipped = {"setup": "skipped", "teardown": "passed"}
    outcomes = {
        "version": 1,
        "binding": dict(BINDING),
        "exitstatus": 0,
        "selected_digest": shards.digest(selected),
        "collected": len(selected),
        "outcomes": {selected[0]: passed, selected[1]: skipped},
    }
    process = {
        "version": 1,
        "binding": dict(BINDING),
        "timed_out": False,
        "returncode": 0,
        "error_type": None,
        "cleanup_error_type": None,
        "junit_available": True,
    }
    dump(folder / "inventory.json", inventory)
    dump(folder / "outcomes.json", outcomes)
    dump(folder / "process.json", process)
    dump(folder / "context.json", {"binding": BINDING, "index": 0, "count": 2})
    root = ET.Element("testsuites")
    suite = ET.SubElement(root, "testsuite", tests="2", failures="0", errors="0", skipped="1")
    for index, nodeid in enumerate(selected):
        case = ET.SubElement(suite, "testcase", name=f"test_{index}")
        properties = ET.SubElement(case, "properties")
        ET.SubElement(properties, "property", name="ci_nodeid", value=nodeid)
        if index:
            ET.SubElement(case, "skipped", message="explicit runtime skip")
    ET.ElementTree(root).write(folder / "junit.xml", encoding="utf-8")
    (folder / "pytest.log").write_text("1 passed, 1 skipped\n", encoding="utf-8")
    (folder / "coverage.xml").write_text('<coverage version="fixture"/>\n', encoding="utf-8")
    seal(folder)
    return folder


def change_json(folder, name, change):
    path = folder / name
    value = json.loads(path.read_text(encoding="utf-8"))
    change(value)
    dump(path, value)


def reject(folder, *, require_complete=False):
    with pytest.raises((ValueError, FileNotFoundError, ET.ParseError)):
        shards.validate_shard(folder, BINDING, 0, 2, require_complete=require_complete)


@pytest.mark.parametrize("count", [1, 2, 4, 8])
def test_partition_is_complete_disjoint_and_deterministic(count):
    before = list(NODEIDS)
    parts = [shards.partition(NODEIDS, index, count) for index in range(count)]
    assert all(parts)
    assert sorted(item for part in parts for item in part) == NODEIDS
    assert sum(map(len, parts)) == len(set().union(*(set(part) for part in parts)))
    assert parts == [shards.partition(list(NODEIDS), index, count) for index in range(count)]
    assert NODEIDS == before
    assert max(map(len, parts)) - min(map(len, parts)) <= 1


@pytest.mark.parametrize(
    "nodeids,index,count",
    [
        ([], 0, 1),
        (None, 0, 1),
        ("a", 0, 1),
        (("a",), 0, 1),
        ([None], 0, 1),
        ([1], 0, 1),
        ([[]], 0, 1),
        ([""], 0, 1),
        (["a\x00b"], 0, 1),
        (["a", "a"], 0, 1),
        (["b", "a"], 0, 1),
        (["a"], -1, 1),
        (["a"], 1, 1),
        (["a"], True, 1),
        (["a"], 0.0, 1),
        (["a"], "0", 1),
        (["a"], 0, 0),
        (["a"], 0, -1),
        (["a"], 0, True),
        (["a"], 0, 1.0),
        (["a"], 0, "1"),
        (["a"], 0, 2),
        (NODEIDS, 0, 65),
    ],
)
def test_partition_rejects_malformed_inventory_and_boundaries(nodeids, index, count):
    with pytest.raises(ValueError):
        shards.partition(nodeids, index, count)


def test_maximum_shards_and_one_test_per_shard_are_supported():
    nodeids = [f"test_{number:02}" for number in range(64)]
    assert [shards.partition(nodeids, index, 64) for index in range(64)] == [
        [nodeid] for nodeid in nodeids
    ]
    assert shards.partition(["中文::test_🧪"], 0, 1) == ["中文::test_🧪"]


@pytest.mark.parametrize("skip_stage", ["call", "setup"])
def test_valid_receipt_requires_complete_hashes_and_preserves_runtime_skips(tmp_path, skip_stage):
    folder = make_receipt(tmp_path, skip_stage=skip_stage)
    inventory, skipped = shards.validate_shard(folder, BINDING, 0, 2)
    assert inventory["nodeids"] == NODEIDS[:4]
    assert inventory["selected"] == NODEIDS[:4:2]
    assert skipped == 1


@pytest.mark.parametrize("name", [*shards.EVIDENCE_FILES, "complete.json"])
def test_missing_required_evidence_fails_closed(tmp_path, name):
    folder = make_receipt(tmp_path)
    (folder / name).unlink()
    reject(folder, require_complete=True)


@pytest.mark.parametrize("name", shards.EVIDENCE_FILES)
def test_completed_hashes_reject_changed_evidence_bytes(tmp_path, name):
    folder = make_receipt(tmp_path)
    with (folder / name).open("ab") as file:
        file.write(b"\n")
    reject(folder, require_complete=True)


@pytest.mark.parametrize("damage", ["version", "binding", "index", "count", "files"])
def test_complete_manifest_identity_and_inventory_are_exact(tmp_path, damage):
    folder = make_receipt(tmp_path)
    replacements = {
        "version": 2,
        "binding": {**BINDING, "attempt": "3"},
        "index": 1,
        "count": 4,
        "files": {},
    }
    change_json(folder, "complete.json", lambda value: value.update({damage: replacements[damage]}))
    reject(folder, require_complete=True)


@pytest.mark.parametrize("name", ["inventory.json", "outcomes.json", "process.json"])
@pytest.mark.parametrize("document", [[], None, 1, "not an object"])
def test_nonobject_receipts_are_rejected_as_invalid_input(tmp_path, name, document):
    folder = make_receipt(tmp_path)
    dump(folder / name, document)
    reject(folder)


@pytest.mark.parametrize(
    "name", ["inventory.json", "outcomes.json", "process.json", "complete.json"]
)
@pytest.mark.parametrize("version", [True, "1", None, 0, 2])
def test_receipt_versions_require_an_exact_integer(tmp_path, name, version):
    folder = make_receipt(tmp_path)
    change_json(folder, name, lambda value: value.update(version=version))
    reject(folder, require_complete=name == "complete.json")


@pytest.mark.parametrize(
    "name", ["inventory.json", "outcomes.json", "process.json", "context.json"]
)
@pytest.mark.parametrize(
    "key,value",
    [
        ("head", "b" * 40),
        ("run", "124"),
        ("attempt", "3"),
        ("origin", "restored"),
        ("platform", "win32"),
        ("source_digest", "c" * 64),
    ],
)
def test_stale_wrong_origin_or_wrong_platform_receipts_cannot_mix(tmp_path, name, key, value):
    folder = make_receipt(tmp_path)
    change_json(folder, name, lambda receipt: receipt["binding"].update({key: value}))
    reject(folder)


@pytest.mark.parametrize("name", ["inventory.json", "context.json", "complete.json"])
@pytest.mark.parametrize(
    "field,value", [("index", False), ("index", 1), ("count", 2.0), ("count", 3)]
)
def test_shard_identity_rejects_wrong_or_coercible_numbers(tmp_path, name, field, value):
    folder = make_receipt(tmp_path)
    change_json(folder, name, lambda receipt: receipt.update({field: value}))
    reject(folder, require_complete=name == "complete.json")


@pytest.mark.parametrize(
    "field,value",
    [
        ("selection", "not postgres and not slow"),
        ("nodeids", NODEIDS[:3]),
        ("nodeids", [NODEIDS[0], NODEIDS[0]]),
        ("nodeids", list(reversed(NODEIDS[:4]))),
        ("selected", NODEIDS[:2]),
        ("selected", [NODEIDS[0], NODEIDS[0]]),
        ("inventory_digest", "0" * 64),
        ("selected_digest", "0" * 64),
    ],
)
def test_inventory_membership_selection_and_digests_must_match(tmp_path, field, value):
    folder = make_receipt(tmp_path)
    change_json(folder, "inventory.json", lambda receipt: receipt.update({field: value}))
    reject(folder)


@pytest.mark.parametrize(
    "field,value",
    [
        ("exitstatus", 1),
        ("exitstatus", 5),
        ("exitstatus", False),
        ("exitstatus", "0"),
        ("collected", 1),
        ("collected", True),
        ("collected", "2"),
        ("selected_digest", "0" * 64),
        ("outcomes", {}),
        ("outcomes", []),
        ("outcomes", None),
    ],
)
def test_failed_or_partial_outcome_receipt_cannot_pass(tmp_path, field, value):
    folder = make_receipt(tmp_path)
    change_json(folder, "outcomes.json", lambda receipt: receipt.update({field: value}))
    reject(folder)


@pytest.mark.parametrize(
    "stages",
    [
        {},
        None,
        [],
        {"setup": "passed", "call": "passed"},
        {"setup": "failed", "teardown": "passed"},
        {"setup": "passed", "call": "failed", "teardown": "passed"},
        {"setup": "passed", "call": "passed", "teardown": "failed"},
        {"setup": "skipped", "call": "passed", "teardown": "passed"},
        {"setup": "passed", "call": "passed", "teardown": "passed", "extra": "passed"},
    ],
)
def test_missing_failed_or_unexpected_test_phases_cannot_pass(tmp_path, stages):
    folder = make_receipt(tmp_path)
    change_json(
        folder, "outcomes.json", lambda receipt: receipt["outcomes"].update({NODEIDS[0]: stages})
    )
    reject(folder)


def test_extra_unselected_test_outcome_cannot_pass(tmp_path):
    folder = make_receipt(tmp_path)
    change_json(
        folder,
        "outcomes.json",
        lambda receipt: receipt["outcomes"].update({NODEIDS[1]: receipt["outcomes"][NODEIDS[0]]}),
    )
    reject(folder)


@pytest.mark.parametrize(
    "field,value",
    [
        ("timed_out", True),
        ("timed_out", 0),
        ("returncode", 3),
        ("returncode", None),
        ("returncode", False),
        ("returncode", "0"),
        ("error_type", "OSError"),
        ("cleanup_error_type", "RuntimeError"),
        ("junit_available", False),
        ("junit_available", 1),
    ],
)
def test_timeout_cleanup_or_process_failure_cannot_be_overridden_by_success_xml(
    tmp_path, field, value
):
    folder = make_receipt(tmp_path)
    change_json(folder, "process.json", lambda receipt: receipt.update({field: value}))
    reject(folder)


@pytest.mark.parametrize(
    "field",
    [
        "version",
        "binding",
        "timed_out",
        "returncode",
        "error_type",
        "cleanup_error_type",
        "junit_available",
    ],
)
def test_incomplete_process_receipt_must_not_imply_error_free_completion(tmp_path, field):
    folder = make_receipt(tmp_path)
    change_json(folder, "process.json", lambda receipt: receipt.pop(field))
    reject(folder)


@pytest.mark.parametrize(
    "damage",
    [
        "root",
        "multiple_suites",
        "tests",
        "failures",
        "errors",
        "skipped",
        "missing_case",
        "extra_case",
        "duplicate_case",
        "missing_nodeid",
        "duplicate_nodeid_property",
        "wrong_nodeid",
        "failure",
        "error",
        "missing_skip",
        "extra_skip",
    ],
)
def test_junit_counts_membership_properties_and_skips_are_independently_checked(tmp_path, damage):
    folder = make_receipt(tmp_path)
    tree = ET.parse(folder / "junit.xml")
    root, suite = tree.getroot(), tree.getroot()[0]
    cases = suite.findall("testcase")
    if damage == "root":
        root.tag = "other"
    elif damage == "multiple_suites":
        root.append(copy.deepcopy(suite))
    elif damage in {"tests", "failures", "errors", "skipped"}:
        suite.set(damage, "9")
    elif damage == "missing_case":
        suite.remove(cases[0])
    elif damage == "extra_case":
        suite.append(copy.deepcopy(cases[0]))
    elif damage == "duplicate_case":
        suite.remove(cases[1])
        suite.append(copy.deepcopy(cases[0]))
    elif damage == "missing_nodeid":
        cases[0].remove(cases[0].find("properties"))
    elif damage == "duplicate_nodeid_property":
        properties = cases[0].find("properties")
        properties.append(copy.deepcopy(properties[0]))
    elif damage == "wrong_nodeid":
        cases[0].find("./properties/property").set("value", NODEIDS[1])
    elif damage in {"failure", "error"}:
        ET.SubElement(cases[0], damage)
    elif damage == "missing_skip":
        cases[1].remove(cases[1].find("skipped"))
    else:
        ET.SubElement(cases[0], "skipped")
    tree.write(folder / "junit.xml", encoding="utf-8")
    reject(folder)


@pytest.mark.parametrize("text", ["", "not XML", "<testsuites>"])
def test_malformed_junit_is_rejected(tmp_path, text):
    folder = make_receipt(tmp_path)
    (folder / "junit.xml").write_text(text, encoding="utf-8")
    reject(folder)


@pytest.mark.parametrize("missing", [False, True])
def test_missing_or_empty_log_is_not_complete_evidence(tmp_path, missing):
    folder = make_receipt(tmp_path)
    if missing:
        (folder / "pytest.log").unlink()
    else:
        (folder / "pytest.log").write_bytes(b"")
    reject(folder)


@pytest.mark.parametrize(
    "name", ["inventory.json", "outcomes.json", "process.json", "context.json"]
)
def test_duplicate_json_key_in_receipt_is_rejected(tmp_path, name):
    folder = make_receipt(tmp_path)
    path = folder / name
    text = path.read_text(encoding="utf-8")
    key, value = ("index", "0") if name == "context.json" else ("version", "1")
    path.write_text(text[:-1] + f', "{key}":{value}' + "}", encoding="utf-8")
    reject(folder)


def test_plugin_refuses_changed_marker_expression(tmp_path):
    plugin = shards.EvidencePlugin(tmp_path, BINDING, 0, 1)
    config = SimpleNamespace(option=SimpleNamespace(markexpr="not postgres and not slow"))
    with pytest.raises(pytest.UsageError, match="not postgres"):
        plugin.pytest_collection_modifyitems(config, [])
    assert not (tmp_path / "inventory.json").exists()


def test_plugin_refuses_duplicate_test_phase_reports(tmp_path):
    plugin = shards.EvidencePlugin(tmp_path, BINDING, 0, 1)
    report = SimpleNamespace(nodeid=NODEIDS[0], when="setup", outcome="passed")
    plugin.pytest_runtest_logreport(report)
    with pytest.raises(RuntimeError, match="Duplicate"):
        plugin.pytest_runtest_logreport(report)


def test_real_pytest_plugin_preserves_nonpostgres_inventory_nodeids_and_runtime_skips(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "pytest.ini").write_text(
        "[pytest]\nmarkers = postgres: database required\n", encoding="utf-8"
    )
    (project / "test_sample.py").write_text(
        "import pytest\n"
        "def test_a_pass(): pass\n"
        "def test_b_runtime_skip(): pytest.skip('runtime prerequisite unavailable')\n"
        "@pytest.mark.postgres\n"
        "def test_c_postgres(): pytest.fail('must remain deselected')\n"
        "def test_d_pass(): pass\n"
        "@pytest.mark.skip(reason='platform prerequisite')\n"
        "def test_e_setup_skip(): pass\n"
        "def test_f_pass(): pass\n",
        encoding="utf-8",
    )
    expected = [
        "test_sample.py::test_a_pass",
        "test_sample.py::test_b_runtime_skip",
        "test_sample.py::test_d_pass",
        "test_sample.py::test_e_setup_skip",
        "test_sample.py::test_f_pass",
    ]
    env = dict(os.environ, PYTHONPATH=str(ROOT), PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    env.pop("CI_PYTEST_EVIDENCE", None)
    env.pop("PYTEST_ADDOPTS", None)
    results = []
    for index in range(2):
        folder = tmp_path / f"shard-{index}"
        folder.mkdir()
        context = {"binding": BINDING, "index": index, "count": 2}
        dump(folder / "context.json", context)
        script = (
            "import sys; from pathlib import Path; import pytest; "
            "from scripts.ci_pytest import EvidencePlugin; "
            "from scripts.ci_evidence import read_json; "
            "folder=Path(sys.argv[1]); context=read_json(folder/'context.json'); "
            "plugin=EvidencePlugin(folder,context['binding'],context['index'],context['count']); "
            "raise SystemExit(pytest.main(['-m','not postgres','-q',"
            "'--junitxml='+str(folder/'junit.xml')],plugins=[plugin]))"
        )
        result = subprocess.run(
            [sys.executable, "-c", script, str(folder)],
            cwd=project,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        inventory = json.loads((folder / "inventory.json").read_text(encoding="utf-8"))
        outcomes = json.loads((folder / "outcomes.json").read_text(encoding="utf-8"))
        assert inventory["nodeids"] == expected
        assert inventory["selected"] == expected[index::2]
        assert outcomes["collected"] == len(expected[index::2])
        assert set(outcomes["outcomes"]) == set(expected[index::2])
        cases = ET.parse(folder / "junit.xml").getroot().findall(".//testcase")
        assert (
            sorted(
                case.find("./properties/property[@name='ci_nodeid']").get("value") for case in cases
            )
            == expected[index::2]
        )
        results.append(outcomes)
    skipped = results[1]["outcomes"]
    assert skipped[expected[1]] == {"setup": "passed", "call": "skipped", "teardown": "passed"}
    assert skipped[expected[3]] == {"setup": "skipped", "teardown": "passed"}


def restored_receipt(tmp_path):
    from scripts.ci_restored import seal_restored_shard

    folder = make_receipt(tmp_path)
    binding = {**BINDING, "origin": "restored", "source_digest": "b" * 64}
    for name in ("context.json", "inventory.json", "outcomes.json", "process.json"):
        change_json(folder, name, lambda value: value.update(binding=binding))
    seal(folder, binding=binding)
    lifecycle = {key: binding[key] for key in ("head", "run", "attempt", "source_digest")}
    process = {
        "timeout_seconds": 900,
        "returncode": 0,
        "timed_out": False,
        "error_type": None,
        "cleanup_error_type": None,
    }
    dump(
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
    dump(
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
    seal_restored_shard(folder, lifecycle, 0, 2)
    return folder, binding


def test_restored_shard_requires_successful_inner_and_outer_lifecycle_seal(tmp_path):
    folder, binding = restored_receipt(tmp_path)
    inventory, skipped = shards.validate_shard(folder, binding, 0, 2)
    assert skipped == 1 and inventory["selected"] == NODEIDS[:4:2]


@pytest.mark.parametrize("name", ["restored.json", "bootstrap.json", "restored-complete.json"])
def test_restored_shard_missing_lifecycle_evidence_cannot_pass(tmp_path, name):
    folder, binding = restored_receipt(tmp_path)
    (folder / name).unlink()
    with pytest.raises(FileNotFoundError):
        shards.validate_shard(folder, binding, 0, 2)


@pytest.mark.parametrize("name", ["restored.json", "bootstrap.json", "complete.json"])
def test_restored_outer_seal_binds_all_lifecycle_bytes_and_inner_seal(tmp_path, name):
    folder, binding = restored_receipt(tmp_path)
    with (folder / name).open("ab") as stream:
        stream.write(b"\n")
    with pytest.raises(ValueError, match="restored completion seal"):
        shards.validate_shard(folder, binding, 0, 2)


@pytest.mark.parametrize("name", ["restored.json", "bootstrap.json"])
@pytest.mark.parametrize(
    "field,value",
    [
        ("passed", False),
        ("passed", 1),
        ("step", "setup"),
        ("phase", "browser"),
        ("binding", {}),
        ("error_type", "TimeoutExpired"),
        ("process", {}),
    ],
)
def test_resealed_failed_or_stale_lifecycle_still_cannot_pass(tmp_path, name, field, value):
    from scripts.ci_restored import RESTORED_FILES

    folder, binding = restored_receipt(tmp_path)
    change_json(folder, name, lambda receipt: receipt.update({field: value}))
    change_json(
        folder,
        "restored-complete.json",
        lambda receipt: receipt.update(
            files={
                path: hashlib.sha256((folder / path).read_bytes()).hexdigest()
                for path in RESTORED_FILES
            }
        ),
    )
    with pytest.raises(ValueError, match="did not complete successfully"):
        shards.validate_shard(folder, binding, 0, 2)


@pytest.mark.parametrize("name", ["restored.json", "bootstrap.json"])
@pytest.mark.parametrize(
    "field,value",
    [
        ("returncode", 1),
        ("returncode", False),
        ("timed_out", True),
        ("cleanup_error_type", "RuntimeError"),
        ("error_type", "OSError"),
        ("timeout_seconds", 1),
    ],
)
def test_restored_lifecycle_requires_successful_owned_process_receipts(
    tmp_path, name, field, value
):
    from scripts.ci_restored import seal_restored_shard

    folder, binding = restored_receipt(tmp_path)
    change_json(folder, name, lambda receipt: receipt["process"].update({field: value}))
    with pytest.raises(ValueError, match="did not complete successfully"):
        seal_restored_shard(folder, binding, 0, 2)


@pytest.mark.parametrize(
    "field,value",
    [
        ("version", True),
        ("binding", {}),
        ("index", 1),
        ("count", 4),
        ("phase", "browser"),
        ("files", {}),
    ],
)
def test_restored_completion_seal_requires_exact_identity_and_inventory(tmp_path, field, value):
    folder, binding = restored_receipt(tmp_path)
    change_json(folder, "restored-complete.json", lambda receipt: receipt.update({field: value}))
    with pytest.raises(ValueError, match="restored completion seal"):
        shards.validate_shard(folder, binding, 0, 2)
