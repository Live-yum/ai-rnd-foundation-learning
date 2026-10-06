# tests/test_customer_runtime_workflow.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `workflow`（L19–L20）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`yaml.load`、`WORKFLOW.read_text`。 返回路径：L20的`yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)`。
- `test_runtime_triggers_cover_main_business_changes_and_manual_runs`（L23–L41）：接收`workflow`。 控制顺序：L25断言`triggers["push"]["branches"] == ["main"]`；L26断言`"main" in triggers["pull_request"]["branches"]`；L27断言`"workflow_dispatch" in triggers`；L28遍历`("push", "pull_request")`；L29断言`{"workbench/**", "templates/**", "examples/plans/customer-service.json"} <= set( trig…`；L33断言`"head.ref" not in gate and "head.repo" not in gate`；L34断言`"pull_request_target" not in triggers`；L39断言`"workflow_dispatch" in native["on"]`。后续分支沿下方源码相同行号继续阅读。 调用`set`、`yaml.load`、`(ROOT / ".github/workflows/native-runtime.yml").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_gate_is_cheap_read_only_and_uses_literal_sha`（L44–L70）：接收`workflow`。 控制顺序：L45断言`workflow["permissions"] == {"contents": "read"}`；L46断言`workflow["concurrency"]["cancel-in-progress"] == "false"`；L47断言`set(workflow["jobs"]) == {"gate", "runtime"}`；L49断言`gate["timeout-minutes"] == "5"`；L50断言`"services" not in gate and "strategy" not in gate`；L51断言`len(gate["steps"]) == 2`；L52断言`gate["outputs"] == { "sha": "${{ steps.head.outputs.sha }}", "eligible": "${{ steps.h…`；L57断言`runtime["needs"] == "gate"`。后续分支沿下方源码相同行号继续阅读。 调用`set`、`len`、`WORKFLOW.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_retains_all_four_cases_and_verification_budgets`（L73–L125）：接收`workflow`。 控制顺序：L75断言`runtime["strategy"] == { "fail-fast": "false", "matrix": { "include": [ { "template":…`；L106断言`runtime["timeout-minutes"] == "55"`；L108断言`verify["timeout-minutes"] == "45"`；L109断言`verify["run"] == ( 'if [ "$CUSTOMER_CASE" = approved-1d7 ]; then\n' ' uv run python -…`；L121断言`runtime["steps"][-1]["with"] == { "name": "native-runtime-${{ matrix.template }}-${{ …`。 调用`next`、`step.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_git`（L128–L142）：接收`root`、`*args`。 调用`subprocess.run( [ "git", "-c", "user.name=Runtime gate test", "-c…`、`subprocess.run`。 返回路径：L129的`subprocess.run( [ "git", "-c", "user.name=Runtime gate test", "-c", "user.email=gate@examp…`。
- `_checkout`（L145–L153）：接收`root`、`helper`。 控制顺序：L148按`helper`分支。 调用`_git`、`(root / "source.txt").write_text`、`(root / HELPER).parent.mkdir`、`(root / HELPER).write_text`。 返回路径：L153的`_git(root, "rev-parse", "HEAD")`。
- `_bash_executable`（L156–L160）：接收`windows`。 控制顺序：L159断言`executable is not None`。 调用`shutil.which`。 返回路径：L160的`executable`。
- `test_gate_uses_git_bash_on_windows_without_skipping`（L173–L188）：接收`monkeypatch`、`windows`、`available`、`expected`、`lookups`。 控制顺序：L183按`expected is None`分支；L187断言`_bash_executable(windows=windows) == f"/tools/{expected}"`；L188断言`requested == lookups`。 调用`monkeypatch.setattr`、`pytest.raises`、`_bash_executable`、`pytest.mark.parametrize`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_gate_uses_git_bash_on_windows_without_skipping.which`（L178–L180）：接收`name`。 调用`requested.append`。 返回路径：L180的`f"/tools/{name}" if name in available else None`。
- `_run_gate`（L191–L204）：接收`workflow`、`root`、`expected_sha`、`job`。 调用`subprocess.run`、`_bash_executable`、`output.exists`、`output.read_text`。 返回路径：L204的`result, output.read_text(encoding="utf-8") if output.exists() else ""`。
- `test_helper_present_skips_heavy_matrix_then_removed_final_head_is_eligible`（L207–L221）：接收`workflow`、`tmp_path`。 控制顺序：L210断言`result.returncode == 0`；L211断言`output == f"sha={source_sha}\neligible=false\n"`；L212断言`"Literal helper-free final head is eligible:" not in result.stdout`；L217断言`final_sha != source_sha`；L219断言`result.returncode == 0`；L220断言`output == f"sha={final_sha}\neligible=true\n"`；L221断言`result.stdout == f"Literal helper-free final head is eligible: {final_sha}\n"`。 调用`_checkout`、`_run_gate`、`(tmp_path / "step-output.txt").unlink`、`_git`、`HELPER.as_posix`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_head_assertion_accepts_only_literal_checked_out_sha`（L226–L240）：接收`workflow`、`tmp_path`、`job`、`expected_sha`。 控制顺序：L231按`expected_sha is None`分支；L232断言`result.returncode == 0`；L233断言`output == (f"sha={head}\neligible=true\n" if job == "gate" else "")`；L234断言`result.stdout == ( f"Literal helper-free final head is eligible: {head}\n" if job == …`；L238断言`result.returncode != 0`；L239断言`output == ""`；L240断言`"Literal helper-free final head is eligible:" not in result.stdout`。 调用`_checkout`、`_run_gate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_customer_runtime_workflow.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L240。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9202`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_customer_runtime_workflow.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "636810da8ddc3e27e96ad43182f56998b6259223a43435cbce66acea619e2eda"} -->
````python
# tests/test_customer_runtime_workflow.py
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


def test_runtime_triggers_cover_main_business_changes_and_manual_runs(workflow):
    triggers = workflow["on"]
    assert triggers["push"]["branches"] == ["main"]
    assert "main" in triggers["pull_request"]["branches"]
    assert "workflow_dispatch" in triggers
    for event in ("push", "pull_request"):
        assert {"workbench/**", "templates/**", "examples/plans/customer-service.json"} <= set(
            triggers[event]["paths"]
        )
    gate = workflow["jobs"]["gate"]["if"]
    assert "head.ref" not in gate and "head.repo" not in gate
    assert "pull_request_target" not in triggers
    native = yaml.load(
        (ROOT / ".github/workflows/native-runtime.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    assert "workflow_dispatch" in native["on"]
    for event in ("push", "pull_request"):
        assert "templates/**" in native["on"][event]["paths"]


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
````
