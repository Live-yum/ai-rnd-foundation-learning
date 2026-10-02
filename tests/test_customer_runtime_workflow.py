"""The customer runtime matrix must exercise the literal, helper-free final head."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/customer-runtime.yml"
HELPER = Path(".github/workflows/customer-handbook-once.yml")
EVENT_SHA = "${{ github.event.pull_request.head.sha || github.sha }}"
GATE_SHA = "${{ needs.gate.outputs.sha }}"


@pytest.fixture
def workflow():
    return yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_runtime_trigger_is_customer_pr_only_with_manual_compatibility(workflow):
    assert workflow["on"] == {
        "pull_request": {
            "branches": ["feat/complete-platform-acceptance"],
            "paths": [
                "从零实现AI研发平台_逐步实操手册_完整版.md",
                ".github/workflows/customer-runtime.yml",
            ],
        },
        "workflow_dispatch": "",
    }
    assert " ".join(workflow["jobs"]["gate"]["if"].split()) == (
        "(github.event_name == 'pull_request' && "
        "github.event.pull_request.head.repo.full_name == github.repository && "
        "github.event.pull_request.head.ref == 'feat/customer-service-acceptance' && "
        "github.event.pull_request.base.ref == 'feat/complete-platform-acceptance') || "
        "(github.event_name == 'workflow_dispatch' && "
        "github.ref == 'refs/heads/feat/customer-service-acceptance')"
    )


def test_runtime_gate_is_cheap_read_only_and_uses_literal_sha(workflow):
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] == "false"
    assert set(workflow["jobs"]) == {"gate", "runtime"}
    gate = workflow["jobs"]["gate"]
    assert gate["timeout-minutes"] == "5"
    assert "services" not in gate and "strategy" not in gate
    assert len(gate["steps"]) == 2
    assert gate["outputs"] == {
        "sha": "${{ steps.head.outputs.sha }}",
        "eligible": "${{ steps.head.outputs.eligible }}",
    }
    runtime = workflow["jobs"]["runtime"]
    assert runtime["needs"] == "gate"
    assert runtime["if"] == "needs.gate.outputs.eligible == 'true'"
    for job, ref in ((gate, EVENT_SHA), (runtime, GATE_SHA)):
        assert "permissions" not in job and "environment" not in job
        assert job["steps"][0] == {
            "uses": "actions/checkout@v4",
            "with": {"ref": ref, "persist-credentials": "false"},
        }
        verify = job["steps"][1]
        assert verify["shell"] == "bash"
        assert verify["env"] == {"EXPECTED_SHA": ref}
        assert '[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]]' in verify["run"]
        assert 'test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"' in verify["run"]
    assert "secrets." not in WORKFLOW.read_text(encoding="utf-8")


def test_runtime_retains_all_four_cases_and_verification_budgets(workflow):
    runtime = workflow["jobs"]["runtime"]
    assert runtime["strategy"] == {
        "fail-fast": "false",
        "matrix": {
            "include": [
                {
                    "template": template,
                    "case": case,
                    "repository": repository,
                    "revision": revision,
                    "pnpm": pnpm,
                }
                for template, cases, repository, revision, pnpm in (
                    (
                        "fastapiadmin",
                        ("canonical", "approved-0e8"),
                        "fastapiadmin/FastapiAdmin",
                        "1cd12c726ad9032c17ef85ce805ce991be60fbdf",
                        "9.15.3",
                    ),
                    (
                        "yudao-vben",
                        ("canonical", "approved-1d7"),
                        "yudaocode/yudao-cloud-mini",
                        "47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be",
                        "11.16.0",
                    ),
                )
                for case in cases
            ],
        },
    }
    assert runtime["timeout-minutes"] == "55"
    verify = next(step for step in runtime["steps"] if "ci_native_bundled" in step.get("run", ""))
    assert verify["timeout-minutes"] == "45"
    assert verify["run"] == (
        'if [ "$CUSTOMER_CASE" = approved-1d7 ]; then\n'
        '  uv run python -m scripts.ci_native_bundled "$CUSTOMER_TEMPLATE" '
        "--approved-replay yudao-1d7\n"
        'elif [ "$CUSTOMER_CASE" = approved-0e8 ]; then\n'
        '  uv run python -m scripts.ci_native_bundled "$CUSTOMER_TEMPLATE" '
        "--approved-replay fastapi-0e8\n"
        "else\n"
        '  uv run python -m scripts.ci_native_bundled "$CUSTOMER_TEMPLATE" '
        "--spec examples/plans/customer-service.json\n"
        "fi\n"
    )
    assert runtime["steps"][-1]["with"] == {
        "name": "native-runtime-${{ matrix.template }}-${{ matrix.case }}",
        "path": "reports/native/",
        "retention-days": "7",
    }


def _git(root, *args):
    return subprocess.run(
        [
            "git",
            "-c",
            "user.name=Runtime gate test",
            "-c",
            "user.email=gate@example.invalid",
            *args,
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _checkout(root, *, helper=False):
    _git(root, "init", "-q")
    (root / "source.txt").write_text("source fixture\n", encoding="utf-8")
    if helper:
        (root / HELPER).parent.mkdir(parents=True)
        (root / HELPER).write_text("name: temporary helper\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "Create fixture")
    return _git(root, "rev-parse", "HEAD")


def _bash_executable(*, windows):
    executable = shutil.which("gitbash") if windows else None
    executable = executable or shutil.which("bash")
    assert executable is not None, "Git Bash or Bash is required for runtime gate tests"
    return executable


@pytest.mark.parametrize(
    ("windows", "available", "expected", "lookups"),
    [
        (True, {"gitbash", "bash"}, "gitbash", ["gitbash"]),
        (True, {"bash"}, "bash", ["gitbash", "bash"]),
        (False, {"gitbash", "bash"}, "bash", ["bash"]),
        (True, set(), None, ["gitbash", "bash"]),
        (False, {"gitbash"}, None, ["bash"]),
    ],
)
def test_gate_uses_git_bash_on_windows_without_skipping(
    monkeypatch, windows, available, expected, lookups
):
    requested = []

    def which(name):
        requested.append(name)
        return f"/tools/{name}" if name in available else None

    monkeypatch.setattr(shutil, "which", which)
    if expected is None:
        with pytest.raises(AssertionError, match="Bash is required"):
            _bash_executable(windows=windows)
    else:
        assert _bash_executable(windows=windows) == f"/tools/{expected}"
    assert requested == lookups


def _run_gate(workflow, root, expected_sha, *, job="gate"):
    output = root / "step-output.txt"
    result = subprocess.run(
        [
            _bash_executable(windows=os.name == "nt"),
            "-c",
            workflow["jobs"][job]["steps"][1]["run"],
        ],
        cwd=root,
        env={**os.environ, "EXPECTED_SHA": expected_sha, "GITHUB_OUTPUT": output.name},
        capture_output=True,
        text=True,
    )
    return result, output.read_text(encoding="utf-8") if output.exists() else ""


def test_helper_present_skips_heavy_matrix_then_removed_final_head_is_eligible(workflow, tmp_path):
    source_sha = _checkout(tmp_path, helper=True)
    result, output = _run_gate(workflow, tmp_path, source_sha)
    assert result.returncode == 0, result.stderr
    assert output == f"sha={source_sha}\neligible=false\n"
    assert "Literal helper-free final head is eligible:" not in result.stdout
    (tmp_path / "step-output.txt").unlink()
    _git(tmp_path, "rm", HELPER.as_posix())
    _git(tmp_path, "commit", "-qm", "Finish handbook and remove helper")
    final_sha = _git(tmp_path, "rev-parse", "HEAD")
    assert final_sha != source_sha
    result, output = _run_gate(workflow, tmp_path, final_sha)
    assert result.returncode == 0, result.stderr
    assert output == f"sha={final_sha}\neligible=true\n"
    assert result.stdout == f"Literal helper-free final head is eligible: {final_sha}\n"


@pytest.mark.parametrize("job", ["gate", "runtime"])
@pytest.mark.parametrize("expected_sha", [None, "", "a" * 7, "g" * 40, "A" * 40, "0" * 40])
def test_head_assertion_accepts_only_literal_checked_out_sha(workflow, tmp_path, job, expected_sha):
    head = _checkout(tmp_path)
    result, output = _run_gate(
        workflow, tmp_path, head if expected_sha is None else expected_sha, job=job
    )
    if expected_sha is None:
        assert result.returncode == 0, result.stderr
        assert output == (f"sha={head}\neligible=true\n" if job == "gate" else "")
        assert result.stdout == (
            f"Literal helper-free final head is eligible: {head}\n" if job == "gate" else ""
        )
    else:
        assert result.returncode != 0
        assert output == ""
        assert "Literal helper-free final head is eligible:" not in result.stdout
