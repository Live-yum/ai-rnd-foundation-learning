"""Prove a directory-only textbook rebuild, then run the actual complete platform suite."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.build_handbook import OUTPUT as LEGACY
from scripts.build_handbook import generated_frontend_asset
from scripts.build_learning_docs import OUTPUT, ROOT
from scripts.ci_handbook import run_full_tests
from scripts.rebuild_learning_docs import read_bundle, sha


def verify_frontend_bundle(destination, expected):
    """No Git or original checkout: compare the rebuilt complete runtime asset set."""
    wanted = {name: data for name, data in expected.items() if generated_frontend_asset(name)}
    if not wanted:
        raise AssertionError("The textbook must include the generated control-plane assets")
    actual = {
        path.relative_to(destination).as_posix(): path.read_bytes()
        for path in (destination / "workbench/web").rglob("*")
        if path.is_file()
    }
    if actual.keys() != wanted.keys():
        raise AssertionError(
            "Vue asset inventory differs: missing="
            + str(sorted(wanted.keys() - actual.keys()))
            + "; extra="
            + str(sorted(actual.keys() - wanted.keys()))
        )
    for name, data in wanted.items():
        if actual[name] != data:
            raise AssertionError("Vue clean-build byte comparison failed: " + name)
    return len(wanted)


def rebuild_frontend(destination, expected, npm, run):
    """Build only from the restored source and its lock; do not accept the saved bundle alone."""
    run([npm, "ci", "--prefix", "ui", "--no-audit", "--no-fund"])
    run([npm, "test", "--prefix", "ui"])
    run([npm, "run", "build", "--prefix", "ui"])
    return verify_frontend_bundle(destination, expected)


def verify_frontend_browser(destination, python, run, reports):
    """Keep real HTTP/Chromium evidence from the restored platform, including failures."""
    # Never merge a failed rerun into old passed:true summaries or screenshots.
    # Callers retain this run-specific path even when the driver raises.
    reports.mkdir(parents=True, exist_ok=False)
    browser_reports = destination / "reports/guided-browser"
    try:
        run([python, "-m", "scripts.ci_guided_browser"])
    finally:
        if browser_reports.is_dir():
            shutil.copytree(browser_reports, reports, dirs_exist_ok=True)
    summary = json.loads((browser_reports / "summary.json").read_text(encoding="utf-8"))
    required = (
        "passed",
        "real_browser",
        "actual_incremental_sse",
        "first_delta_before_provider_complete",
        "unicode_split_replay_dedupe",
    )
    if any(summary.get(field) is not True for field in required):
        raise AssertionError("Restored Vue workbench requires real incremental-browser evidence")
    if summary.get("model_mode") != "explicit-local-http-fixtures":
        raise AssertionError("Textbook acceptance must not call live or paid model providers")
    return {field: summary[field] for field in (*required, "model_mode")}


SIGNUP_SCOPE_TRUE_FIELDS = (
    "passed",
    "real_browser",
    "real_http",
    "same_run_id",
    "original_request_preserved",
    "no_default_scope_selection",
    "discarded_admin_selection_not_submitted",
    "authenticated_entrant_goal_preserved",
    "legacy_failed_import_checkpoint",
    "earlier_scope_invalidates_old_progress",
    "mobile_no_horizontal_overflow",
    "mobile_submit_above_fixed_navigation",
)


def verify_signup_scope_browser(destination, python, run, reports):
    """Prove the restored legacy recovery flow; retain distinct evidence on failure."""
    reports.mkdir(parents=True, exist_ok=False)
    browser_reports = destination / "reports/signup-scope-browser"
    # A new cleanroom has no earlier driver output. Reject accidental reuse rather
    # than letting an old passed:true result become this run's evidence.
    if browser_reports.exists():
        raise AssertionError("Signup browser evidence must be new for this restored project")
    try:
        run([python, "-m", "scripts.ci_signup_scope_browser"])
    finally:
        if browser_reports.is_dir():
            shutil.copytree(browser_reports, reports, dirs_exist_ok=True)
    summary = json.loads((browser_reports / "browser.json").read_text(encoding="utf-8"))
    if any(summary.get(field) is not True for field in SIGNUP_SCOPE_TRUE_FIELDS):
        raise AssertionError("Restored signup scope requires real browser/recovery evidence")
    if (
        summary.get("native_generation_attempted") is not False
        or summary.get("external_provider_calls") is not False
        or summary.get("fixture_mode") != "in-process-requirement-gateway"
        or summary.get("status") != "WAITING_REQUIREMENTS"
        or summary.get("errors") != []
    ):
        raise AssertionError("Signup browser must stop at the local-fixture requirements gate")
    calls = summary.get("fixture_model_calls")
    run_id = summary.get("run_id")
    if (
        not isinstance(run_id, str)
        or not run_id
        or not isinstance(calls, list)
        or len(calls) != 1
        or not isinstance(calls[0], dict)
        or calls[0].get("run_id") != run_id
    ):
        raise AssertionError("Known signup decisions must not repeat model calls or change run")
    for field in ("original_approval_count", "recovered_approval_count"):
        if type(summary.get(field)) is not int or summary[field] != 1:
            raise AssertionError("Legacy signup recovery must preserve its original approval")
    screenshots = summary.get("screenshots")
    expected_screenshots = {
        "scope-blocked.png",
        "scope-blocked-mobile.png",
        "scope-options-mobile.png",
        "scope-corrected.png",
    }
    if (
        not isinstance(screenshots, list)
        or any(not isinstance(name, str) for name in screenshots)
        or len(screenshots) != len(expected_screenshots)
        or set(screenshots) != expected_screenshots
    ):
        raise AssertionError("Signup browser must retain all desktop/mobile PNG screenshots")
    if any(
        not (browser_reports / name).is_file()
        or not (browser_reports / name).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        for name in screenshots
    ):
        raise AssertionError("Signup browser must retain all desktop/mobile PNG screenshots")
    actual_bundle = {
        path.relative_to(destination).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (destination / "workbench/web").rglob("*")
        if path.is_file()
    }
    actual_screenshots = {
        name: hashlib.sha256((reports / name).read_bytes()).hexdigest() for name in screenshots
    }
    if not actual_bundle or summary.get("ui_bundle_sha256") != actual_bundle:
        raise AssertionError("Signup browser evidence must bind the restored Vue bundle")
    if summary.get("screenshot_sha256") != actual_screenshots:
        raise AssertionError("Signup browser evidence must bind the preserved PNG bytes")
    return summary


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
            status["phase"] = "build_vue_control_plane"
            frontend_count = rebuild_frontend(destination, expected, npm, run)
            status["frontend"] = {
                "source": "restored ui directory and npm lock",
                "unit_tests": "passed",
                "typescript_and_production_build": "passed",
                "runtime_assets_byte_equal": True,
                "runtime_assets": frontend_count,
            }
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
            status["phase"] = "vue_real_browser_acceptance"
            browser_evidence = reports / "learning-docs-guided-browser" / uuid.uuid4().hex
            status["frontend"]["browser"] = {
                "passed": False,
                "evidence_directory": browser_evidence.relative_to(reports).as_posix(),
            }
            status["frontend"]["browser"].update(
                verify_frontend_browser(destination, python, run, browser_evidence)
            )
            status["phase"] = "signup_scope_real_browser_acceptance"
            signup_evidence = reports / "learning-docs-signup-scope-browser" / uuid.uuid4().hex
            status["frontend"]["signup_scope_browser"] = {
                "passed": False,
                "evidence_directory": signup_evidence.relative_to(reports).as_posix(),
            }
            status["frontend"]["signup_scope_browser"].update(
                verify_signup_scope_browser(destination, python, run, signup_evidence)
            )
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
