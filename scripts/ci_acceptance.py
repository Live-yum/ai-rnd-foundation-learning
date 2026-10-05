"""Always-run acceptance gate: failed dependencies or incomplete evidence are never green."""

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path

from scripts.ci_evidence import (
    digest,
    read_json,
    restore_source_artifact,
    run_binding,
    safe_name,
    write_json,
)

REQUIRED_JOBS = {
    "frontend",
    "source-validation",
    "tests",
    "postgres",
    "clean-install",
    "native-sources",
    "handbook-only",
    "restored-tests",
    "restored-browser",
    "restored-install",
    "browser",
}
STAGES = {
    "frontend": [],
    "source-validation-ubuntu-latest": ["protocol.xml"],
    "source-validation-windows-latest": ["protocol.xml"],
    "postgres": ["postgres.xml"],
    "clean-install-ubuntu-latest": ["clean-install.json"],
    "clean-install-windows-latest": ["clean-install.json"],
    "native-sources": ["native-sources.json"],
    "handbook-only": [
        "learning-docs-clean-room.json",
        "restored-source/manifest.json",
        "restored-source/source.zip",
    ],
    "restored-browser": [
        "restored/restored.json",
        "restored/guided-browser/summary.json",
        "restored/signup-scope-browser/browser.json",
    ],
    "restored-install": ["restored/restored.json", "restored/clean-install.json"],
    "browser": ["guided-browser/summary.json", "signup-scope-browser/browser.json"],
}


def file_hashes(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlink evidence")
        if path.is_file() and path != folder / "stage.json":
            name = safe_name(path.relative_to(folder).as_posix())
            result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def stage_binding(binding, name):
    return {
        **binding,
        "stage": name,
        "platform": "win32" if name.endswith("windows-latest") else "linux",
    }


def receipt(name, folder):
    if name not in STAGES:
        raise ValueError("Unknown CI stage")
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / "stage.json").exists():
        raise ValueError("Refuse stale stage receipt")
    for relative in STAGES[name]:
        if not (folder / relative).is_file() or not (folder / relative).stat().st_size:
            raise ValueError("Missing required stage evidence: " + relative)
    binding = stage_binding(run_binding(), name)
    if binding["platform"] != sys.platform:
        raise ValueError("Wrong stage platform")
    write_json(
        folder / "stage.json", {"version": 1, "binding": binding, "files": file_hashes(folder)}
    )


def require_jobs(needs):
    if not isinstance(needs, dict) or set(needs) != REQUIRED_JOBS:
        raise ValueError("Missing or unexpected required jobs")
    failed = [
        name
        for name, value in needs.items()
        if not isinstance(value, dict) or value.get("result") != "success"
    ]
    if failed:
        raise ValueError("Required jobs failed, cancelled or skipped: " + ", ".join(sorted(failed)))


def aggregate(folder, needs, binding, *, count=4):
    from scripts.ci_pytest import validate_shard

    require_jobs(needs)
    if type(count) is not int or not 1 <= count <= 64:
        raise ValueError("Invalid aggregate shard count")
    prefix = "acceptance-" + binding["attempt"] + "-"
    expected = {prefix + name for name in STAGES}
    groups = [
        ("source", "linux", "ubuntu-latest"),
        ("source", "win32", "windows-latest"),
        ("restored", "linux", "ubuntu-latest"),
    ]
    expected.update(
        prefix + f"{origin}-{os_name}-{index}"
        for origin, _, os_name in groups
        for index in range(count)
    )
    if not folder.is_dir() or {path.name for path in folder.iterdir()} != expected:
        raise ValueError("Missing, duplicate or unexpected acceptance artifacts")
    for name in STAGES:
        path = folder / (prefix + name)
        stage = read_json(path / "stage.json")
        if digest(stage) != digest(
            {"version": 1, "binding": stage_binding(binding, name), "files": file_hashes(path)}
        ):
            raise ValueError("Stale or changed stage evidence: " + name)
        if any(
            not (path / item).is_file() or not (path / item).stat().st_size for item in STAGES[name]
        ):
            raise ValueError("Missing required stage evidence: " + name)
    prepared = folder / (prefix + "handbook-only")
    with tempfile.TemporaryDirectory(prefix="verify-restored-source-") as temporary:
        manifest = restore_source_artifact(
            prepared / "restored-source", Path(temporary) / "verified", binding
        )
    preparation = read_json(prepared / "learning-docs-clean-room.json")
    source_digest = manifest.get("source_digest")
    if (
        manifest.get("binding") != binding
        or not isinstance(source_digest, str)
        or preparation.get("source_digest") != source_digest
        or preparation.get("original_project_imported") is not False
        or preparation.get("original_archives_copied") is not False
        or preparation.get("python_environment") != "independent locked student-project venv"
        or preparation.get("passed") is not False
        or preparation.get("prepared") is not True
        or preparation.get("tests_executed") is not False
        or preparation.get("phase") != "prepared_for_independent_acceptance"
    ):
        raise ValueError("Missing genuine reconstruction evidence")
    for phase in ("browser", "install"):
        restored = read_json(folder / (prefix + "restored-" + phase) / "restored/restored.json")
        if (
            restored.get("binding") != {**binding, "source_digest": source_digest}
            or restored.get("phase") != phase
            or restored.get("passed") is not True
            or restored.get("original_project_imported") is not False
            or restored.get("python_environment") != "independent locked student-project venv"
        ):
            raise ValueError("Restored acceptance did not pass independently")
    inventories, summaries = {}, []
    for origin, platform, os_name in groups:
        reference, union, skipped = None, [], 0
        current = {
            **binding,
            "origin": origin,
            "platform": platform,
            "source_digest": binding["head"] if origin == "source" else source_digest,
        }
        for index in range(count):
            path = folder / (prefix + f"{origin}-{os_name}-{index}")
            inventory, omitted = validate_shard(path, current, index, count)
            if reference is not None and inventory["nodeids"] != reference:
                raise ValueError("Shards disagree on complete platform collection")
            reference = inventory["nodeids"]
            union.extend(inventory["selected"])
            skipped += omitted
        if sorted(union) != reference or len(union) != len(set(union)):
            raise ValueError("Shards do not cover the exact full suite once")
        inventories[(origin, platform)] = reference
        summaries.append(
            {
                "origin": origin,
                "platform": platform,
                "collected": len(reference),
                "passed": len(reference) - skipped,
                "skipped": skipped,
                "inventory_digest": inventory["inventory_digest"],
                "shards": count,
            }
        )
    if inventories[("source", "linux")] != inventories[("restored", "linux")]:
        raise ValueError("Restored suite lost or added source tests")
    return {
        "passed": True,
        "binding": binding,
        "groups": summaries,
        "required_jobs": sorted(REQUIRED_JOBS),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    stage = commands.add_parser("receipt")
    stage.add_argument("name", choices=sorted(STAGES))
    stage.add_argument("--reports", type=Path, default=Path("reports"))
    gate = commands.add_parser("aggregate")
    gate.add_argument("--artifacts", type=Path, default=Path("acceptance-artifacts"))
    args = parser.parse_args()
    if args.command == "receipt":
        receipt(args.name, args.reports)
    else:
        import json

        result = aggregate(args.artifacts, json.loads(os.environ["CI_NEEDS"]), run_binding())
        write_json(Path("reports/acceptance.json"), result)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
