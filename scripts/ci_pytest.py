"""Deterministic complete pytest partitions and outcome receipts; also a pytest plugin."""

import argparse
import hashlib
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from scripts.ci_evidence import digest, read_json, run_binding, write_json

SHARDS = 4
SELECTION = "not postgres"


def partition(nodeids, index, count):
    if (
        type(index) is not int
        or type(count) is not int
        or not 1 <= count <= 64
        or not 0 <= index < count
        or not isinstance(nodeids, list)
        or not nodeids
        or any(not isinstance(item, str) or not item or "\x00" in item for item in nodeids)
        or len(set(nodeids)) != len(nodeids)
        or nodeids != sorted(nodeids)
        or count > len(nodeids)
    ):
        raise ValueError("Invalid full inventory or shard boundary")
    return nodeids[index::count]


class EvidencePlugin:
    def __init__(self, folder, binding, index, count):
        self.folder, self.binding, self.index, self.count = folder, binding, index, count
        self.inventory = None
        self.selected = None
        self.outcomes = {}

    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, config, items):
        if config.option.markexpr != SELECTION:
            raise pytest.UsageError("CI selection must remain not postgres")
        self.inventory = sorted(item.nodeid for item in items)
        self.selected = partition(self.inventory, self.index, self.count)
        selected = set(self.selected)
        discarded = [item for item in items if item.nodeid not in selected]
        items[:] = [item for item in items if item.nodeid in selected]
        for item in items:
            item.user_properties.append(("ci_nodeid", item.nodeid))
        config.hook.pytest_deselected(items=discarded)
        write_json(
            self.folder / "inventory.json",
            {
                "version": 1,
                "binding": self.binding,
                "selection": SELECTION,
                "index": self.index,
                "count": self.count,
                "nodeids": self.inventory,
                "inventory_digest": digest(self.inventory),
                "selected": self.selected,
                "selected_digest": digest(self.selected),
            },
        )

    def pytest_runtest_logreport(self, report):
        stages = self.outcomes.setdefault(report.nodeid, {})
        if report.when in stages:
            raise RuntimeError("Duplicate test phase report")
        stages[report.when] = report.outcome

    def pytest_sessionfinish(self, session, exitstatus):
        write_json(
            self.folder / "outcomes.json",
            {
                "version": 1,
                "binding": self.binding,
                "exitstatus": int(exitstatus),
                "selected_digest": digest(self.selected),
                "outcomes": self.outcomes,
                "collected": session.testscollected,
            },
        )


def pytest_configure(config):
    folder = os.environ.get("CI_PYTEST_EVIDENCE")
    if folder:
        context = read_json(Path(folder) / "context.json")
        config.pluginmanager.register(
            EvidencePlugin(Path(folder), context["binding"], context["index"], context["count"]),
            "ci-evidence",
        )


EVIDENCE_FILES = (
    "context.json",
    "inventory.json",
    "outcomes.json",
    "process.json",
    "junit.xml",
    "pytest.log",
    "coverage.xml",
)


def evidence_hashes(folder):
    return {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in EVIDENCE_FILES
    }


def validate_shard(folder, expected_binding, index, count, *, require_complete=True):
    if require_complete:
        if expected_binding.get("origin") == "restored":
            from scripts.ci_restored import validate_restored_completion

            validate_restored_completion(folder, expected_binding, index, count)
        complete = read_json(folder / "complete.json")
        if digest(complete) != digest(
            {
                "version": 1,
                "binding": expected_binding,
                "index": index,
                "count": count,
                "files": evidence_hashes(folder),
            }
        ):
            raise ValueError("Missing or changed completed-shard evidence")
    inventory = read_json(folder / "inventory.json")
    outcomes = read_json(folder / "outcomes.json")
    process = read_json(folder / "process.json")
    context = read_json(folder / "context.json")
    if digest(context) != digest({"binding": expected_binding, "index": index, "count": count}):
        raise ValueError("Wrong shard context")
    for receipt in (inventory, outcomes):
        if (
            not isinstance(receipt, dict)
            or type(receipt.get("version")) is not int
            or receipt["version"] != 1
            or receipt.get("binding") != expected_binding
        ):
            raise ValueError("Wrong shard identity")
    if not isinstance(process, dict):
        raise ValueError("Malformed pytest process receipt")
    nodeids = inventory.get("nodeids")
    selected = partition(nodeids, index, count)
    if (
        inventory.get("selection") != SELECTION
        or type(inventory.get("index")) is not int
        or inventory.get("index") != index
        or type(inventory.get("count")) is not int
        or inventory.get("count") != count
        or inventory.get("selected") != selected
        or inventory.get("inventory_digest") != digest(nodeids)
        or inventory.get("selected_digest") != digest(selected)
        or outcomes.get("selected_digest") != digest(selected)
    ):
        raise ValueError("Shard membership/digest mismatch")
    if (
        not {"error_type", "cleanup_error_type"}.issubset(process)
        or type(outcomes.get("exitstatus")) is not int
        or outcomes["exitstatus"] != 0
        or type(outcomes.get("collected")) is not int
        or outcomes["collected"] != len(selected)
        or process.get("binding") != expected_binding
        or type(process.get("version")) is not int
        or process.get("version") != 1
        or process.get("timed_out") is not False
        or type(process.get("returncode")) is not int
        or process["returncode"] != 0
        or process.get("error_type") is not None
        or process.get("cleanup_error_type") is not None
        or process.get("junit_available") is not True
    ):
        raise ValueError("Failed, incomplete or timed-out pytest process")
    reports = outcomes.get("outcomes")
    if not isinstance(reports, dict) or set(reports) != set(selected):
        raise ValueError("Missing/extra test outcomes")
    skipped = set()
    for nodeid, stages in reports.items():
        if stages == {"setup": "skipped", "teardown": "passed"} or stages == {
            "setup": "passed",
            "call": "skipped",
            "teardown": "passed",
        }:
            skipped.add(nodeid)
        elif stages != {"setup": "passed", "call": "passed", "teardown": "passed"}:
            raise ValueError("Failed or incomplete test phases")
    root = ET.parse(folder / "junit.xml").getroot()
    if root.tag != "testsuites" or len(root) != 1 or root[0].tag != "testsuite":
        raise ValueError("Malformed JUnit suite")
    suite = root[0]
    cases = suite.findall("testcase")
    if (
        suite.get("tests") != str(len(selected))
        or suite.get("failures") != "0"
        or suite.get("errors") != "0"
        or suite.get("skipped") != str(len(skipped))
        or len(cases) != len(selected)
    ):
        raise ValueError("JUnit count/failure mismatch")
    junit_ids = []
    for case in cases:
        properties = case.findall("./properties/property[@name='ci_nodeid']")
        if (
            len(properties) != 1
            or case.find("failure") is not None
            or case.find("error") is not None
        ):
            raise ValueError("Missing node ID or failed JUnit case")
        nodeid = properties[0].get("value")
        if (case.find("skipped") is not None) != (nodeid in skipped):
            raise ValueError("JUnit skip mismatch")
        junit_ids.append(nodeid)
    if sorted(junit_ids) != selected:
        raise ValueError("JUnit missing/duplicate/extra test case")
    if not (folder / "pytest.log").is_file() or not (folder / "pytest.log").stat().st_size:
        raise ValueError("Missing pytest log")
    return inventory, len(skipped)


def run_shard(folder, origin, index, count, source_digest):
    from scripts.ci_handbook import run_full_tests

    if origin not in {"source", "restored"} or sys.platform not in {"linux", "win32"}:
        raise ValueError("Unsupported acceptance origin/platform")
    binding = {
        **run_binding(),
        "origin": origin,
        "platform": sys.platform,
        "source_digest": source_digest,
    }
    folder = folder.resolve()
    folder.mkdir(parents=True, exist_ok=False)
    write_json(folder / "context.json", {"binding": binding, "index": index, "count": count})
    env = dict(
        os.environ,
        CI_PYTEST_EVIDENCE=str(folder),
        PYTHONPATH="",
        PYTHONUTF8="1",
        PYTHONIOENCODING="utf-8",
        RND_REQUIRE_NODE_TESTS="1",
    )
    env.pop("PYTEST_ADDOPTS", None)
    argv = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "scripts.ci_pytest",
        "-m",
        SELECTION,
        "-q",
        "--tb=short",
        f"--junitxml={folder / 'junit.xml'}",
        "--cov=workbench",
        f"--cov-report=xml:{folder / 'coverage.xml'}",
        "--cov-report=term",
    ]
    try:
        with (folder / "pytest.log").open("w", encoding="utf-8") as log:
            run_full_tests(
                argv,
                Path.cwd(),
                env,
                folder / "junit.xml",
                folder,
                status_name="process.json",
                junit_name=None,
                stdout=log,
                binding=binding,
            )
        inventory, skipped = validate_shard(folder, binding, index, count, require_complete=False)
        write_json(
            folder / "complete.json",
            {
                "version": 1,
                "binding": binding,
                "index": index,
                "count": count,
                "files": evidence_hashes(folder),
            },
        )
        print(
            f"{origin}/{sys.platform} shard {index + 1}/{count}: "
            f"{len(inventory['selected'])} complete ({skipped} skipped), "
            f"full inventory {len(inventory['nodeids'])} / {inventory['inventory_digest']}"
        )
    finally:
        log = folder / "pytest.log"
        if log.is_file():
            with log.open("rb") as stream:
                stream.seek(max(0, log.stat().st_size - 12000))
                print(stream.read().decode("utf-8", errors="replace"), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--count", type=int, default=SHARDS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_shard(args.output, "source", args.index, args.count, run_binding()["head"])


if __name__ == "__main__":
    main()
