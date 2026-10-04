"""Run independent acceptance solely from verified docs-reconstructed source bytes."""

import argparse
import hashlib
import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from scripts.ci_evidence import digest, read_json, restore_source_artifact, run_binding, write_json


def _process_identity(pid):
    """Read only parent PID and start ticks, never command lines or environment."""
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(") ", 1)[1].split()
        return int(fields[1]), fields[19]
    except OSError, ValueError, IndexError:
        return None


def _owned_snapshot(process):
    if os.name == "nt" or not Path("/proc").is_dir() or process.poll() is not None:
        return {}
    root = _process_identity(process.pid)
    if root is None:
        return {}
    snapshot = {}
    for path in Path("/proc").iterdir():
        if path.name.isdecimal() and (identity := _process_identity(int(path.name))):
            snapshot[int(path.name)] = identity
    owned = {process.pid: root}
    while added := {
        pid: identity
        for pid, identity in snapshot.items()
        if identity[0] in owned and pid not in owned
    }:
        owned.update(added)
    return {pid: identity[1] for pid, identity in owned.items()}


def _stop_owned(process, observed):
    """Stop only the original Windows tree or Linux descendants with proven identity."""
    errors = []
    try:
        if os.name == "nt":
            # Popen retains the original process handle. Do not target an expired PID.
            if process.poll() is None:
                result = subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20,
                    check=False,
                )
                if result.returncode and process.poll() is None:
                    errors.append(RuntimeError("Windows owned process tree cleanup failed"))
        else:
            observed.update(_owned_snapshot(process))
            for pid, started in reversed(list(observed.items())):
                current = _process_identity(pid)
                if current is not None and current[1] == started:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    except OSError as error:
                        errors.append(error)
            # No /proc on some POSIX hosts: the still-live group was created by us.
            if not Path("/proc").is_dir() and process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
    except Exception as error:
        errors.append(error)
    finally:
        try:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
        except Exception as error:
            errors.append(error)
    if errors:
        raise RuntimeError("Owned subprocess cleanup failed: " + type(errors[0]).__name__)


def run_owned(argv, *, cwd, env, timeout, check=True, report=None):
    """Preserve deadlines and clean owned descendants even across child process groups.

    This bootstrap must remain stdlib-only: importing the original workbench or its
    venv to perform cleanup would invalidate independent reconstructed acceptance.
    """
    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ValueError("A positive subprocess deadline is required")
    started, process, failure, cleanup_error = time.monotonic(), None, None, None
    observed = {}
    try:
        options = (
            {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
            if os.name == "nt"
            else {"start_new_session": True}
        )
        command = argv
        if sys.platform == "linux":
            # A dedicated subreaper owns descendants even when a target exits
            # before the first PID snapshot. It never changes this process's role.
            supervisor = Path(__file__).with_name("ci_process_supervisor.py")
            if not supervisor.is_file():
                raise FileNotFoundError("Missing owned process supervisor")
            command = [sys.executable, str(supervisor), *argv]
        process = subprocess.Popen(command, cwd=cwd, env=env, **options)
        observed.update(_owned_snapshot(process))
        deadline = started + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(argv, timeout)
            try:
                process.wait(timeout=min(remaining, 1))
                break
            except subprocess.TimeoutExpired:
                # Keep start identities before a leader exits or a child detaches.
                observed.update(_owned_snapshot(process))
        if check and process.returncode:
            raise subprocess.CalledProcessError(process.returncode, argv)
        return subprocess.CompletedProcess(argv, process.returncode)
    except BaseException as error:
        failure = error
        raise
    finally:
        if process is not None and (failure is not None or process.poll() is None):
            try:
                _stop_owned(process, observed)
            except Exception as error:
                cleanup_error = type(error).__name__
        if report is not None:
            report.update(
                timeout_seconds=timeout,
                timed_out=isinstance(failure, subprocess.TimeoutExpired),
                returncode=process.returncode if process is not None else None,
                error_type=type(failure).__name__ if failure else None,
                cleanup_error_type=cleanup_error,
                owned_processes_observed=len(observed),
                elapsed_seconds=round(time.monotonic() - started, 3),
            )
        if cleanup_error and failure is None:
            raise RuntimeError("Owned subprocess cleanup failed: " + cleanup_error)


def inside(phase, output, index, count, source_digest):
    # All runtime imports happen only in the newly reconstructed interpreter.
    if output.exists() or output.is_symlink():
        raise ValueError("Restored evidence must be fresh")
    status = {
        "phase": phase,
        "step": "verify_imports",
        "passed": False,
        "original_project_imported": None,
        "python_environment": "independent locked student-project venv",
    }
    try:
        import workbench.store
        from scripts.ci_learning_docs import (
            browser_preflight,
            verify_frontend_browser,
            verify_signup_scope_browser,
        )

        root = Path.cwd().resolve()
        status["original_project_imported"] = (
            not Path(workbench.store.__file__).resolve().is_relative_to(root)
        )
        if status["original_project_imported"]:
            raise AssertionError("Original checkout imported by restored acceptance")
        status["binding"] = {**run_binding(), "source_digest": source_digest}
        env = dict(
            os.environ,
            PYTHONPATH="",
            PYTHONUTF8="1",
            PYTHONIOENCODING="utf-8",
            PLAYWRIGHT_BROWSERS_PATH="0",
            RND_REQUIRE_NODE_TESTS="1",
        )

        def run(argv, cwd=root, timeout=900):
            status["process"] = {}
            run_owned(argv, cwd=cwd, env=env, check=True, timeout=timeout, report=status["process"])

        status["step"] = "browser_preflight"
        browser_preflight(env, run, root)
        status["step"] = "locate_npm"
        npm = shutil.which("npm")
        if not npm:
            raise RuntimeError("Restored acceptance requires Node 22/npm")
        status["step"] = "node_install"
        run([npm, "ci", "--prefix", "tools/node", "--no-audit", "--no-fund"])
        status["step"] = "node_build"
        run([npm, "run", "build", "--prefix", "tools/node"])
        if phase == "tests":
            from scripts.ci_pytest import run_shard

            status["step"] = "pytest_shard"
            run_shard(output, "restored", index, count, source_digest)
        else:
            output.mkdir(parents=True, exist_ok=False)
            if phase == "browser":
                status["step"] = "guided_browser"
                status["guided_browser"] = verify_frontend_browser(
                    root, sys.executable, run, output / "guided-browser"
                )
                status["step"] = "signup_scope_browser"
                status["signup_scope_browser"] = verify_signup_scope_browser(
                    root, sys.executable, run, output / "signup-scope-browser"
                )
            else:
                status["step"] = "independent_install"
                try:
                    run([sys.executable, "-m", "scripts.ci_clean_install"])
                finally:
                    if (root / "reports/clean-install.json").is_file():
                        shutil.copyfile(
                            root / "reports/clean-install.json", output / "clean-install.json"
                        )
        status.update(passed=True, step="complete")
    except BaseException as error:
        status["error_type"] = type(error).__name__
        raise
    finally:
        write_json(output / "restored.json", status)


RESTORED_FILES = ("complete.json", "restored.json", "bootstrap.json")


def _lifecycle_binding(binding):
    return {key: binding[key] for key in ("head", "run", "attempt", "source_digest")}


def _successful_process(value, timeout):
    return (
        isinstance(value, dict)
        and {"error_type", "cleanup_error_type"}.issubset(value)
        and value.get("timeout_seconds") == timeout
        and type(value.get("returncode")) is int
        and value["returncode"] == 0
        and value.get("timed_out") is False
        and value["error_type"] is None
        and value["cleanup_error_type"] is None
    )


def _validate_lifecycle(folder, binding):
    inner = read_json(folder / "restored.json")
    outer = read_json(folder / "bootstrap.json")
    if (
        not isinstance(inner, dict)
        or inner.get("binding") != binding
        or inner.get("phase") != "tests"
        or inner.get("passed") is not True
        or inner.get("step") != "complete"
        or inner.get("error_type") is not None
        or inner.get("original_project_imported") is not False
        or inner.get("python_environment") != "independent locked student-project venv"
        or not _successful_process(inner.get("process"), 900)
    ):
        raise ValueError("Restored shard lifecycle did not complete successfully")
    if (
        not isinstance(outer, dict)
        or outer.get("binding") != {key: binding[key] for key in ("head", "run", "attempt")}
        or outer.get("source_digest") != binding["source_digest"]
        or outer.get("phase") != "tests"
        or outer.get("passed") is not True
        or outer.get("step") != "complete"
        or outer.get("error_type") is not None
        or not _successful_process(outer.get("process"), 3300)
    ):
        raise ValueError("Restored shard bootstrap did not complete successfully")


def _restored_seal(folder, binding, index, count):
    return {
        "version": 1,
        "binding": binding,
        "phase": "tests",
        "index": index,
        "count": count,
        "files": {
            name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
            for name in RESTORED_FILES
        },
    }


def seal_restored_shard(folder, binding, index, count):
    """Only the outer stdlib bootstrap may finalize completed restored pytest evidence."""
    binding = _lifecycle_binding(binding)
    _validate_lifecycle(folder, binding)
    write_json(folder / "restored-complete.json", _restored_seal(folder, binding, index, count))


def validate_restored_completion(folder, binding, index, count):
    binding = _lifecycle_binding(binding)
    seal = read_json(folder / "restored-complete.json")
    if digest(seal) != digest(_restored_seal(folder, binding, index, count)):
        raise ValueError("Missing or changed restored completion seal")
    _validate_lifecycle(folder, binding)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--phase", choices=["tests", "browser", "install"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--inside", action="store_true")
    parser.add_argument("--source-digest")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.inside:
        inside(args.phase, output, args.index, args.count, args.source_digest)
        return
    if args.artifact is None:
        parser.error("--artifact is required")
    if output.exists() or output.is_symlink():
        raise ValueError("Restored evidence must be fresh")
    status = {"phase": args.phase, "step": "locate_uv", "passed": False}
    try:
        env = dict(
            os.environ,
            PYTHONPATH="",
            PYTHONUTF8="1",
            PYTHONIOENCODING="utf-8",
            RND_REQUIRE_NODE_TESTS="1",
        )
        env.pop("UV_PROJECT_ENVIRONMENT", None)
        env.pop("VIRTUAL_ENV", None)
        uv = shutil.which("uv")
        if not uv:
            raise RuntimeError("Restored acceptance requires uv")
        status["binding"] = run_binding()
        with tempfile.TemporaryDirectory(prefix="rnd-restored-acceptance-") as temporary:
            root = Path(temporary) / "student-project"
            status["step"] = "verify_source"
            manifest = restore_source_artifact(args.artifact.resolve(), root, status["binding"])
            status["source_digest"] = manifest["source_digest"]
            status["step"], status["process"] = "locked_install", {}
            run_owned(
                [uv, "sync", "--locked", "--all-extras"],
                cwd=root,
                env=env,
                check=True,
                timeout=900,
                report=status["process"],
            )
            python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            status["step"], status["process"] = "restored_worker", {}
            run_owned(
                [
                    str(python),
                    "-m",
                    "scripts.ci_restored",
                    "--inside",
                    "--phase",
                    args.phase,
                    "--output",
                    str(output),
                    "--index",
                    str(args.index),
                    "--count",
                    str(args.count),
                    "--source-digest",
                    manifest["source_digest"],
                ],
                cwd=root,
                env=env,
                check=True,
                timeout=3300,
                report=status["process"],
            )
        status.update(passed=True, step="complete")
        if args.phase == "tests":
            write_json(output / "bootstrap.json", status)
            seal_restored_shard(
                output,
                {**status["binding"], "source_digest": status["source_digest"]},
                args.index,
                args.count,
            )
    except BaseException as error:
        if status["passed"]:
            status["step"] = "final_evidence"
        status["passed"] = False
        status["error_type"] = type(error).__name__
        raise
    finally:
        # No output directory is created before the worker: its pytest evidence
        # still has the same strict fresh-directory contract and artifact layout.
        write_json(output / "bootstrap.json", status)


if __name__ == "__main__":
    main()
