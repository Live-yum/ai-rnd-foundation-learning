"""Prove a directory-only textbook rebuild, then run the actual complete platform suite."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.build_handbook import OUTPUT as LEGACY
from scripts.build_learning_docs import OUTPUT, ROOT
from scripts.ci_handbook import run_full_tests
from scripts.rebuild_learning_docs import read_bundle, sha


def main():
    expected = read_bundle(OUTPUT)
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    status = {
        "passed": False,
        "phase": "copy_docs",
        "original_project_imported": False,
        "original_archives_copied": False,
    }
    try:
        with tempfile.TemporaryDirectory(prefix="rnd-learning-only-") as folder:
            base = Path(folder)
            docs = base / "learning-docs"
            shutil.copytree(OUTPUT, docs)
            destination = base / "student-project"
            env = dict(os.environ, PYTHONPATH="", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")

            def run(argv, cwd=destination, timeout=900):
                subprocess.run(argv, cwd=cwd, env=env, check=True, timeout=timeout)

            status["phase"] = "standard_library_rebuild"
            run([sys.executable, "-I", str(docs / "rebuild.py"), str(destination)], cwd=base)
            for name, data in expected.items():
                if (destination / name).read_bytes() != data:
                    raise AssertionError("Docs-only byte comparison failed: " + name)
            if list((destination / "templates/vendor").glob("*.zip")):
                raise AssertionError("Original upstream archives were copied")
            uv = shutil.which("uv")
            npm = shutil.which("npm")
            if not uv or not npm:
                raise RuntimeError("Install uv and Node 22/npm before full clean-room acceptance")
            status["phase"] = "browser_preflight"
            node = shutil.which("node")
            module = env.get("PRODUCT_VERIFY_PLAYWRIGHT")
            if not node or not module or not Path(module).is_dir():
                raise RuntimeError(
                    "Install Playwright 1.56.1/Chromium as stage 06 describes and set "
                    "PRODUCT_VERIFY_PLAYWRIGHT to its absolute module directory"
                )
            # Several actual browser tests intentionally use Playwright's hermetic
            # installation. Check that same location before launching thousands of tests.
            env["PLAYWRIGHT_BROWSERS_PATH"] = "0"
            run(
                [
                    node,
                    "-e",
                    "const {chromium}=require(process.argv[1]); "
                    "(async()=>{const b=await chromium.launch({headless:true}); "
                    "await b.close(); console.log('Hermetic Chromium preflight PASS')})()"
                    ".catch(e=>{console.error(e.message);process.exitCode=1})",
                    module,
                ],
                cwd=base,
                timeout=60,
            )
            status["phase"] = "locked_install"
            run([uv, "sync", "--locked", "--all-extras"])
            python = str(
                destination / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            )
            # The student's own venv is used; not even the project's .pth entry is reused.
            run(
                [
                    python,
                    "-c",
                    "from pathlib import Path; import workbench.store; "
                    "assert Path(workbench.store.__file__).resolve().is_relative_to(Path.cwd())",
                ]
            )
            status["phase"] = "exact_textbook_roundtrip"
            run([python, "-m", "scripts.build_handbook"])
            if (destination / LEGACY.name).read_bytes() != LEGACY.read_bytes():
                raise AssertionError("Legacy compatibility book roundtrip differs")
            run([python, "-m", "scripts.build_learning_docs"])
            for original in docs.rglob("*"):
                if original.is_file():
                    relative = original.relative_to(docs)
                    if (
                        destination / "learning-docs" / relative
                    ).read_bytes() != original.read_bytes():
                        raise AssertionError("Staged textbook roundtrip differs: " + str(relative))
            pinned = json.loads(expected["templates/vendor/manifest.json"])
            status["phase"] = "fetch_pinned_upstream_templates"
            run([python, "-m", "scripts.vendor_templates", "--fetch"])
            actual = json.loads(
                (destination / "templates/vendor/manifest.json").read_text(encoding="utf-8")
            )
            for want, got in zip(pinned["sources"], actual["sources"], strict=True):
                for field in ("name", "url", "sha", "source_digest", "files", "license"):
                    if want[field] != got[field]:
                        raise AssertionError(
                            "Pinned template mismatch: " + want["name"] + ":" + field
                        )
            # zlib variations may legitimately change compressed ZIP bytes only.
            run([python, "-m", "scripts.build_handbook"])
            run([python, "-m", "scripts.build_learning_docs"])
            status["phase"] = "build_real_node_tools"
            run([npm, "ci", "--prefix", "tools/node", "--no-audit", "--no-fund"])
            run([npm, "run", "build", "--prefix", "tools/node"])
            env["RND_REQUIRE_NODE_TESTS"] = "1"
            status["phase"] = "ruff"
            run([python, "-m", "ruff", "check", "."])
            run([python, "-m", "ruff", "format", "--check", "."])
            run([python, "-m", "scripts.build_learning_docs", "--check"])
            status["phase"] = "full_non_postgres_tests"
            junit = base / "learning-docs-tests.xml"
            run_full_tests(
                [
                    python,
                    "-m",
                    "pytest",
                    "-m",
                    "not postgres",
                    "-v",
                    "--tb=short",
                    f"--junitxml={junit}",
                ],
                destination,
                env,
                junit,
                reports,
            )
            shutil.copyfile(junit, reports / "learning-docs-tests.xml")
            cases = ET.parse(junit).getroot().findall(".//testcase")
            if not cases or any(
                case.find("failure") is not None or case.find("error") is not None for case in cases
            ):
                raise AssertionError("The actual platform suite must pass")
            status.update(
                passed=True,
                phase="complete",
                files_restored=len(expected),
                binary_files_restored=sum(name.endswith(".png") for name in expected),
                tests_passed=sum(case.find("skipped") is None for case in cases),
                tests_skipped=sum(case.find("skipped") is not None for case in cases),
                test_selection="full non-PostgreSQL platform suite with real Node/browser tools",
                python_environment="independent locked student-project venv",
                third_party_fixed_revisions_rebuilt=len(actual["sources"]),
                manifest_sha256=sha((docs / "manifest.json").read_bytes()),
            )
    except BaseException as exc:
        status["error_type"] = type(exc).__name__
        raise
    finally:
        (reports / "learning-docs-clean-room.json").write_text(
            json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(status, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
