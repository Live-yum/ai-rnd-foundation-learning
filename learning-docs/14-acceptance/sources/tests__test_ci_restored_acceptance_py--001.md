# tests/test_ci_restored_acceptance.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.ci_evidence`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `configure_main`（L13–L81）：接收`monkeypatch`、`tmp_path`、`phase`。 调用`monkeypatch.setenv`、`monkeypatch.setattr`、`str`。 返回路径：L81的`calls`。
- `configure_main.restore`（L40–L43）：接收`artifact`、`destination`、`binding`。先验证所有源码块与目标路径，再向空目录写入；这一步本身不执行任何写出的项目代码。 调用`calls.append`、`destination.mkdir`。 返回路径：L43的`{"source_digest": "b" * 64}`。
- `configure_main.successful_run`（L47–L78）：接收`argv`、`**kwargs`。 控制顺序：L57按`"--inside" in argv`分支。 调用`calls.append`、`kwargs["report"].update`、`Path`、`argv.index`、`write_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bootstrap_verifies_artifact_before_install_and_uses_restored_venv`（L85–L108）：接收`monkeypatch`、`tmp_path`、`phase`。 控制顺序：L90断言`len(calls) == 3`；L91断言`calls[0][0] == "restore"`；L93断言`calls[1][0] == ["/tools/uv", "sync", "--locked", "--all-extras"]`；L96断言`argv[:5] == [str(python), "-m", "scripts.ci_restored", "--inside", "--phase"]`；L97断言`argv[5] == phase`；L98断言`argv[argv.index("--source-digest") + 1] == "b" * 64`；L99断言`argv[argv.index("--index") + 1] == "2"`；L100断言`argv[argv.index("--count") + 1] == "4"`。后续分支沿下方源码相同行号继续阅读。 调用`configure_main`、`ci_restored.main`、`len`、`str`、`argv.index`、`restored.exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_artifact_failure_stops_before_install_or_project_import`（L111–L120）：接收`monkeypatch`、`tmp_path`。 控制顺序：L120断言`calls == []`。 调用`configure_main`、`monkeypatch.setattr`、`pytest.raises`、`ci_restored.main`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_artifact_failure_stops_before_install_or_project_import.fail`（L114–L115）：接收`*args`。 控制顺序：L115抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_install_or_worker_never_claims_success_and_removes_temp_project`（L124–L140）：接收`monkeypatch`、`tmp_path`、`fail_at`。 控制顺序：L137断言`error.value.returncode == 7`；L138断言`len(calls) == fail_at + 1`；L139断言`not calls[0][2].exists()`；L140断言`not (tmp_path / "evidence/restored.json").exists()`。 调用`configure_main`、`monkeypatch.setattr`、`pytest.raises`、`ci_restored.main`、`len`、`calls[0][2].exists`、`(tmp_path / "evidence/restored.json").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_install_or_worker_never_claims_success_and_removes_temp_project.run`（L129–L132）：接收`argv`、`**kwargs`。 控制顺序：L131按`len(calls) - 1 == fail_at`分支；L132抛异常，停止当前正常路径。 调用`calls.append`、`len`、`subprocess.CalledProcessError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inside_rejects_original_checkout_import_before_browser_or_node`（L143–L148）：接收`monkeypatch`、`tmp_path`。 控制顺序：L148断言`failure["passed"] is False and failure["original_project_imported"] is True`。 调用`monkeypatch.chdir`、`pytest.raises`、`ci_restored.inside`、`read_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inside_browser_keeps_failed_evidence_and_never_runs_other_phases`（L151–L185）：接收`monkeypatch`、`tmp_path`。 控制顺序：L179断言`status["passed"] is False and status["phase"] == "browser"`；L180断言`status["binding"]["source_digest"] == "b" * 64`；L181断言`(output / "guided-browser/browser.log").read_text() == "current real-browser failure"`；L182断言`calls == [ ["/tools/npm", "ci", "--prefix", "tools/node", "--no-audit", "--no-fund"],…`。 调用`monkeypatch.chdir`、`monkeypatch.setattr`、`str`、`monkeypatch.setenv`、`calls.append`、`pytest.fail`、`pytest.raises`、`ci_restored.inside`、`read_json`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inside_browser_keeps_failed_evidence_and_never_runs_other_phases.browser_failure`（L164–L167）：接收`root`、`python`、`run`、`reports`。 控制顺序：L167抛异常，停止当前正常路径。 调用`reports.mkdir`、`(reports / "browser.log").write_text`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preparation_preserves_every_original_stage_without_claiming_suite_success`（L188–L210）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L190遍历`[ "standard_library_rebuild", "locked_install", "build_vue_contro…`；L202断言`f'"{stage}"' in text`；L203断言`"if prepare_artifact is not None:" in text`；L204断言`"tests_executed=False" in text`；L205断言`"prepared_for_independent_acceptance" in text`；L206断言`text.index("manifest = create_source_artifact(") < text.index( '"vue_real_browser_acc…`；L209断言`"run_full_tests(" in text`；L210断言`"verify_frontend_browser(" in text and "verify_signup_scope_browser(" in text`。 调用`Path(ci_learning_docs.__file__).read_text`、`Path`、`text.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stdlib_owned_runner_preserves_exact_exit_and_report`（L214–L233）：接收`tmp_path`、`code`。 控制顺序：L219按`code`分支；L224断言`failure.value.returncode == code`；L229断言`result.returncode == 0`；L230断言`report["returncode"] == code`；L231断言`report["timed_out"] is False`；L232断言`report["cleanup_error_type"] is None`；L233断言`report["error_type"] == ("CalledProcessError" if code else None)`。 调用`str`、`pytest.raises`、`ci_restored.run_owned`、`dict`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_runner_rejects_missing_or_unbounded_deadline`（L237–L240）：接收`tmp_path`、`monkeypatch`、`timeout`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`ci_restored.run_owned`、`pytest.mark.parametrize`、`float`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_runner_retains_launch_failure_without_claiming_execution`（L243–L254）：接收`tmp_path`、`monkeypatch`。 控制顺序：L252断言`report["returncode"] is None`；L253断言`report["error_type"] == "OSError" and report["timed_out"] is False`；L254断言`report["cleanup_error_type"] is None`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`ci_restored.run_owned`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_runner_retains_launch_failure_without_claiming_execution.fail`（L244–L245）：接收`*args`、`**kwargs`。 控制顺序：L245抛异常，停止当前正常路径。 调用`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deadline_or_interrupt_cleans_owned_snapshot_and_never_turns_green`（L258–L287）：接收`tmp_path`、`monkeypatch`、`interrupt`。 控制顺序：L285断言`cleaned == [(process, {321: "parent", 322: "child"})]`；L286断言`report["returncode"] == 0 and report["timed_out"] is (not interrupt)`；L287断言`report["error_type"] == ("KeyboardInterrupt" if interrupt else "TimeoutExpired")`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`iter`、`next`、`pytest.raises`、`ci_restored.run_owned`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deadline_or_interrupt_cleans_owned_snapshot_and_never_turns_green.wait`（L265–L268）：接收`**kwargs`。 控制顺序：L266按`interrupt`分支；L267抛异常，停止当前正常路径；L268抛异常，停止当前正常路径。 调用`KeyboardInterrupt`、`subprocess.TimeoutExpired`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deadline_or_interrupt_cleans_owned_snapshot_and_never_turns_green.stop`（L277–L279）：接收`child`、`snapshot`。 调用`cleaned.append`、`snapshot.copy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_failure_is_recorded_without_swallowing_original_timeout`（L290–L311）：接收`tmp_path`、`monkeypatch`。 控制顺序：L311断言`report["timed_out"] is True and report["cleanup_error_type"] == "RuntimeError"`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`iter`、`next`、`pytest.raises`、`ci_restored.run_owned`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_failure_is_recorded_without_swallowing_original_timeout.wait`（L295–L296）：接收`**kwargs`。 控制顺序：L296抛异常，停止当前正常路径。 调用`subprocess.TimeoutExpired`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_failure_is_recorded_without_swallowing_original_timeout.fail`（L304–L305）：接收`*args`。 控制顺序：L305抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_posix_cleanup_uses_start_identity_after_reparenting_and_ignores_recycled_pid`（L314–L327）：接收`monkeypatch`。 控制顺序：L327断言`killed == [(322, 9)]`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`killed.append`、`ci_restored._stop_owned`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_windows_cleanup_targets_only_original_live_popen_tree`（L331–L364）：接收`monkeypatch`、`state`。 控制顺序：L354按`state == "taskkill-fails"`分支；L360断言`len(commands) == (0 if state == "expired" else 1)`；L361按`commands`分支；L362断言`commands[0][0] == ["taskkill", "/F", "/T", "/PID", "321"]`；L363断言`commands[0][1]["timeout"] == 20`；L364断言`("kill-original-handle" in calls) is (state == "taskkill-fails")`。 调用`SimpleNamespace`、`calls.append`、`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`ci_restored._stop_owned`、`isinstance`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_windows_cleanup_targets_only_original_live_popen_tree.kill`（L338–L340）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`calls.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_windows_cleanup_targets_only_original_live_popen_tree.taskkill`（L347–L351）：接收`argv`、`**kwargs`。 控制顺序：L349按`state != "taskkill-fails"`分支。 调用`calls.append`、`SimpleNamespace`。 返回路径：L351的`SimpleNamespace(returncode=1 if state == "taskkill-fails" else 0)`。
- `test_real_timeout_or_failed_leader_cleans_detached_child_without_touching_foreign`（L371–L427）：接收`tmp_path`、`exit_early`。 控制顺序：L403断言`foreign.poll() is None`；L404断言`report["cleanup_error_type"] is None`；L405断言`report["owned_processes_observed"] >= (1 if exit_early == "immediate" else 2)`；L406遍历`range(50)`；L412按`fields[0] == "Z" or fields[19] != owned["started"]`分支；L418按`child_file.is_file()`分支；L421按`identity is not None and identity[1] == owned["started"]`分支。 调用`subprocess.Popen`、`pytest.raises`、`ci_restored.run_owned`、`str`、`dict`、`json.loads`、`child_file.read_text`、`foreign.poll`、`range`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inside_early_setup_failure_always_has_structured_bound_evidence`（L432–L465）：接收`monkeypatch`、`tmp_path`、`step`、`phase`。 控制顺序：L461断言`result["passed"] is False and result["phase"] == phase and result["step"] == step`；L462断言`result["binding"]["source_digest"] == "b" * 64`；L463断言`result["original_project_imported"] is False`；L464断言`"error_type" in result`；L465断言`not (output / "complete.json").exists()`。 调用`monkeypatch.chdir`、`monkeypatch.setattr`、`str`、`pytest.raises`、`ci_restored.inside`、`read_json`、`(output / "complete.json").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inside_early_setup_failure_always_has_structured_bound_evidence.preflight`（L443–L445）：接收`*args`。 控制顺序：L444按`step == "browser_preflight"`分支；L445抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inside_early_setup_failure_always_has_structured_bound_evidence.run`（L452–L454）：接收`argv`、`**kwargs`。 控制顺序：L453按`step == "node_install" and "ci" in argv or step == "node_build" and "build" in argv`分支；L454抛异常，停止当前正常路径。 调用`subprocess.CalledProcessError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_uv_is_preserved_as_bootstrap_failure`（L468–L475）：接收`monkeypatch`、`tmp_path`。 控制顺序：L474断言`report["passed"] is False and report["step"] == "locate_uv"`；L475断言`report["error_type"] == "RuntimeError"`。 调用`configure_main`、`monkeypatch.setattr`、`pytest.raises`、`ci_restored.main`、`read_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bootstrap_timeout_has_phase_identity_and_diagnostics`（L479–L497）：接收`monkeypatch`、`tmp_path`、`fail_at`。 控制顺序：L491断言`failure.value.timeout == (900 if fail_at == 1 else 3300)`；L493断言`report["passed"] is False`；L494断言`report["step"] == ("locked_install" if fail_at == 1 else "restored_worker")`；L495断言`report["binding"]["head"] == "a" * 40 and report["source_digest"] == "b" * 64`；L496断言`report["process"]["timed_out"] is True`；L497断言`report["error_type"] == "TimeoutExpired"`。 调用`configure_main`、`monkeypatch.setattr`、`pytest.raises`、`ci_restored.main`、`read_json`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bootstrap_timeout_has_phase_identity_and_diagnostics.run`（L482–L486）：接收`argv`、`**kwargs`。 控制顺序：L484按`len(calls) - 1 == fail_at`分支；L486抛异常，停止当前正常路径。 调用`calls.append`、`len`、`kwargs["report"].update`、`subprocess.TimeoutExpired`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inside_shard_retains_original_fresh_directory_contract_and_terminal_status`（L501–L532）：接收`monkeypatch`、`tmp_path`、`failure`。 控制顺序：L526按`failure`分支；L531断言`read_json(output / "restored.json")["passed"] is (not failure)`；L532断言`(output / "pytest.log").read_text() == "current shard log"`。 调用`monkeypatch.chdir`、`monkeypatch.setattr`、`str`、`pytest.raises`、`ci_restored.inside`、`read_json`、`(output / "pytest.log").read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inside_shard_retains_original_fresh_directory_contract_and_terminal_status.shard`（L516–L522）：接收`output`、`origin`、`index`、`count`、`digest`。 控制顺序：L517断言`not output.exists()`；L518断言`(origin, index, count, digest) == ("restored", 2, 4, "b" * 64)`；L521按`failure`分支；L522抛异常，停止当前正常路径。 调用`output.exists`、`output.mkdir`、`(output / "pytest.log").write_text`、`subprocess.CalledProcessError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bootstrap_and_inside_refuse_stale_success_without_overwriting`（L535–L545）：接收`monkeypatch`、`tmp_path`。 控制顺序：L545断言`previous.read_text() == '{"passed":true}'`。 调用`configure_main`、`output.mkdir`、`previous.write_text`、`pytest.raises`、`ci_restored.main`、`ci_restored.inside`、`previous.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_ci_restored_acceptance.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L545。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`22597`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_ci_restored_acceptance.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "597e489500d4eaa3ceef1b6a1509b4538883afd916c0a5ecaf6b6bfb6db64b33"} -->
````python
# tests/test_ci_restored_acceptance.py
"""Restored workers bootstrap with stdlib, then use only their own locked project venv."""

import os
import subprocess
from pathlib import Path

import pytest

from scripts import ci_learning_docs, ci_restored
from scripts.ci_evidence import read_json


def configure_main(monkeypatch, tmp_path, phase="tests"):
    calls = []
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    monkeypatch.setenv("PYTHONPATH", "untrusted-original-checkout")
    monkeypatch.setenv("UV_PROJECT_ENVIRONMENT", "original-venv")
    monkeypatch.setenv("VIRTUAL_ENV", "original-venv")
    monkeypatch.setattr(ci_restored.shutil, "which", lambda name: "/tools/" + name)
    monkeypatch.setattr(
        ci_restored.sys,
        "argv",
        [
            "ci_restored",
            "--artifact",
            str(tmp_path / "artifact"),
            "--phase",
            phase,
            "--output",
            str(tmp_path / "evidence"),
            "--index",
            "2",
            "--count",
            "4",
        ],
    )

    def restore(artifact, destination, binding):
        calls.append(("restore", artifact, destination, binding))
        destination.mkdir(parents=True)
        return {"source_digest": "b" * 64}

    monkeypatch.setattr(ci_restored, "restore_source_artifact", restore)

    def successful_run(argv, **kwargs):
        calls.append((argv, kwargs))
        process = {
            "timeout_seconds": kwargs["timeout"],
            "returncode": 0,
            "timed_out": False,
            "error_type": None,
            "cleanup_error_type": None,
        }
        kwargs["report"].update(process)
        if "--inside" in argv:
            from scripts.ci_evidence import write_json

            output = Path(argv[argv.index("--output") + 1])
            write_json(
                output / "restored.json",
                {
                    "binding": {
                        "head": "a" * 40,
                        "run": "123",
                        "attempt": "2",
                        "source_digest": "b" * 64,
                    },
                    "phase": phase,
                    "passed": True,
                    "step": "complete",
                    "original_project_imported": False,
                    "python_environment": "independent locked student-project venv",
                    "process": {**process, "timeout_seconds": 900},
                },
            )
            write_json(output / "complete.json", {"unit_fixture": True})

    monkeypatch.setattr(ci_restored, "run_owned", successful_run)
    return calls


@pytest.mark.parametrize("phase", ["tests", "browser", "install"])
def test_bootstrap_verifies_artifact_before_install_and_uses_restored_venv(
    monkeypatch, tmp_path, phase
):
    calls = configure_main(monkeypatch, tmp_path, phase)
    ci_restored.main()
    assert len(calls) == 3
    assert calls[0][0] == "restore"
    restored = calls[0][2]
    assert calls[1][0] == ["/tools/uv", "sync", "--locked", "--all-extras"]
    python = restored / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    argv = calls[2][0]
    assert argv[:5] == [str(python), "-m", "scripts.ci_restored", "--inside", "--phase"]
    assert argv[5] == phase
    assert argv[argv.index("--source-digest") + 1] == "b" * 64
    assert argv[argv.index("--index") + 1] == "2"
    assert argv[argv.index("--count") + 1] == "4"
    for _, kwargs in calls[1:]:
        assert kwargs["cwd"] == restored
        assert kwargs["env"]["PYTHONPATH"] == ""
        assert "UV_PROJECT_ENVIRONMENT" not in kwargs["env"]
        assert "VIRTUAL_ENV" not in kwargs["env"]
        assert kwargs["env"]["RND_REQUIRE_NODE_TESTS"] == "1"
        assert kwargs["check"] is True
    assert not restored.exists(), "The independent temporary project is always cleaned up"


def test_artifact_failure_stops_before_install_or_project_import(monkeypatch, tmp_path):
    calls = configure_main(monkeypatch, tmp_path)

    def fail(*args):
        raise ValueError("wrong source identity")

    monkeypatch.setattr(ci_restored, "restore_source_artifact", fail)
    with pytest.raises(ValueError, match="wrong source identity"):
        ci_restored.main()
    assert calls == []


@pytest.mark.parametrize("fail_at", [1, 2])
def test_failed_install_or_worker_never_claims_success_and_removes_temp_project(
    monkeypatch, tmp_path, fail_at
):
    calls = configure_main(monkeypatch, tmp_path)

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        if len(calls) - 1 == fail_at:
            raise subprocess.CalledProcessError(7, argv)

    monkeypatch.setattr(ci_restored, "run_owned", run)
    with pytest.raises(subprocess.CalledProcessError) as error:
        ci_restored.main()
    assert error.value.returncode == 7
    assert len(calls) == fail_at + 1
    assert not calls[0][2].exists()
    assert not (tmp_path / "evidence/restored.json").exists()


def test_inside_rejects_original_checkout_import_before_browser_or_node(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(AssertionError, match="Original checkout imported"):
        ci_restored.inside("browser", tmp_path / "evidence", 0, 4, "b" * 64)
    failure = read_json(tmp_path / "evidence/restored.json")
    assert failure["passed"] is False and failure["original_project_imported"] is True


def test_inside_browser_keeps_failed_evidence_and_never_runs_other_phases(monkeypatch, tmp_path):
    import workbench.store

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(workbench.store, "__file__", str(tmp_path / "workbench/store.py"))
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    calls = []
    monkeypatch.setattr(ci_learning_docs, "browser_preflight", lambda *args: None)
    monkeypatch.setattr(ci_restored.shutil, "which", lambda name: "/tools/" + name)
    monkeypatch.setattr(ci_restored, "run_owned", lambda argv, **kw: calls.append(argv))

    def browser_failure(root, python, run, reports):
        reports.mkdir()
        (reports / "browser.log").write_text("current real-browser failure")
        raise RuntimeError("browser failed")

    monkeypatch.setattr(ci_learning_docs, "verify_frontend_browser", browser_failure)
    monkeypatch.setattr(
        ci_learning_docs,
        "verify_signup_scope_browser",
        lambda *args: pytest.fail("later driver ran"),
    )
    output = tmp_path / "evidence"
    with pytest.raises(RuntimeError, match="browser failed"):
        ci_restored.inside("browser", output, 0, 4, "b" * 64)
    status = read_json(output / "restored.json")
    assert status["passed"] is False and status["phase"] == "browser"
    assert status["binding"]["source_digest"] == "b" * 64
    assert (output / "guided-browser/browser.log").read_text() == "current real-browser failure"
    assert calls == [
        ["/tools/npm", "ci", "--prefix", "tools/node", "--no-audit", "--no-fund"],
        ["/tools/npm", "run", "build", "--prefix", "tools/node"],
    ]


def test_preparation_preserves_every_original_stage_without_claiming_suite_success():
    text = Path(ci_learning_docs.__file__).read_text(encoding="utf-8")
    for stage in [
        "standard_library_rebuild",
        "locked_install",
        "build_vue_control_plane",
        "exact_textbook_roundtrip",
        "fetch_pinned_upstream_templates",
        "build_real_node_tools",
        "ruff",
        "vue_real_browser_acceptance",
        "signup_scope_real_browser_acceptance",
        "full_non_postgres_tests",
    ]:
        assert f'"{stage}"' in text
    assert "if prepare_artifact is not None:" in text
    assert "tests_executed=False" in text
    assert "prepared_for_independent_acceptance" in text
    assert text.index("manifest = create_source_artifact(") < text.index(
        '"vue_real_browser_acceptance"'
    )
    assert "run_full_tests(" in text
    assert "verify_frontend_browser(" in text and "verify_signup_scope_browser(" in text


@pytest.mark.parametrize("code", [0, 7])
def test_stdlib_owned_runner_preserves_exact_exit_and_report(tmp_path, code):
    import sys

    report = {}
    argv = [sys.executable, "-c", "import sys; sys.exit(int(sys.argv[1]))", str(code)]
    if code:
        with pytest.raises(subprocess.CalledProcessError) as failure:
            ci_restored.run_owned(
                argv, cwd=tmp_path, env=dict(os.environ), timeout=5, report=report
            )
        assert failure.value.returncode == code
    else:
        result = ci_restored.run_owned(
            argv, cwd=tmp_path, env=dict(os.environ), timeout=5, report=report
        )
        assert result.returncode == 0
    assert report["returncode"] == code
    assert report["timed_out"] is False
    assert report["cleanup_error_type"] is None
    assert report["error_type"] == ("CalledProcessError" if code else None)


@pytest.mark.parametrize("timeout", [None, True, False, 0, -1, "1", float("nan"), float("inf")])
def test_owned_runner_rejects_missing_or_unbounded_deadline(tmp_path, monkeypatch, timeout):
    monkeypatch.setattr(ci_restored.subprocess, "Popen", lambda *a, **k: pytest.fail("launched"))
    with pytest.raises(ValueError, match="positive subprocess deadline"):
        ci_restored.run_owned(["unused"], cwd=tmp_path, env={}, timeout=timeout)


def test_owned_runner_retains_launch_failure_without_claiming_execution(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("launch canary")

    monkeypatch.setattr(ci_restored.subprocess, "Popen", fail)
    monkeypatch.setattr(ci_restored, "_stop_owned", lambda *args: pytest.fail("no child exists"))
    report = {}
    with pytest.raises(OSError, match="launch canary"):
        ci_restored.run_owned(["unused"], cwd=tmp_path, env={}, timeout=5, report=report)
    assert report["returncode"] is None
    assert report["error_type"] == "OSError" and report["timed_out"] is False
    assert report["cleanup_error_type"] is None


@pytest.mark.parametrize("interrupt", [False, True])
def test_deadline_or_interrupt_cleans_owned_snapshot_and_never_turns_green(
    tmp_path, monkeypatch, interrupt
):
    from types import SimpleNamespace

    process = SimpleNamespace(pid=321, returncode=None, poll=lambda: None)

    def wait(**kwargs):
        if interrupt:
            raise KeyboardInterrupt()
        raise subprocess.TimeoutExpired("unit child", kwargs["timeout"])

    process.wait = wait
    monkeypatch.setattr(ci_restored.subprocess, "Popen", lambda *a, **k: process)
    monkeypatch.setattr(ci_restored, "_owned_snapshot", lambda child: {321: "parent", 322: "child"})
    ticks = iter([0, 0, 2, 2])
    monkeypatch.setattr(ci_restored.time, "monotonic", lambda: next(ticks))
    cleaned = []

    def stop(child, snapshot):
        cleaned.append((child, snapshot.copy()))
        process.returncode = 0  # A success exit during cleanup must not erase failure.

    monkeypatch.setattr(ci_restored, "_stop_owned", stop)
    report = {}
    with pytest.raises(KeyboardInterrupt if interrupt else subprocess.TimeoutExpired):
        ci_restored.run_owned(["unit"], cwd=tmp_path, env={}, timeout=1, report=report)
    assert cleaned == [(process, {321: "parent", 322: "child"})]
    assert report["returncode"] == 0 and report["timed_out"] is (not interrupt)
    assert report["error_type"] == ("KeyboardInterrupt" if interrupt else "TimeoutExpired")


def test_cleanup_failure_is_recorded_without_swallowing_original_timeout(tmp_path, monkeypatch):
    from types import SimpleNamespace

    process = SimpleNamespace(pid=321, returncode=None, poll=lambda: None)

    def wait(**kwargs):
        raise subprocess.TimeoutExpired("unit child", kwargs["timeout"])

    process.wait = wait
    monkeypatch.setattr(ci_restored.subprocess, "Popen", lambda *a, **k: process)
    monkeypatch.setattr(ci_restored, "_owned_snapshot", lambda child: {321: "parent"})
    ticks = iter([0, 0, 2, 2])
    monkeypatch.setattr(ci_restored.time, "monotonic", lambda: next(ticks))

    def fail(*args):
        raise RuntimeError("cleanup canary")

    monkeypatch.setattr(ci_restored, "_stop_owned", fail)
    report = {}
    with pytest.raises(subprocess.TimeoutExpired):
        ci_restored.run_owned(["unit"], cwd=tmp_path, env={}, timeout=1, report=report)
    assert report["timed_out"] is True and report["cleanup_error_type"] == "RuntimeError"


def test_posix_cleanup_uses_start_identity_after_reparenting_and_ignores_recycled_pid(monkeypatch):
    from types import SimpleNamespace

    identities = {321: None, 322: (1, "child"), 323: (1, "recycled"), 999: (1, "foreign")}
    killed = []
    monkeypatch.setattr(
        ci_restored, "os", SimpleNamespace(name="posix", kill=lambda p, s: killed.append((p, s)))
    )
    monkeypatch.setattr(ci_restored, "signal", SimpleNamespace(SIGKILL=9))
    monkeypatch.setattr(ci_restored, "_owned_snapshot", lambda process: {})
    monkeypatch.setattr(ci_restored, "_process_identity", identities.get)
    process = SimpleNamespace(poll=lambda: 0, wait=lambda **kwargs: 0)
    ci_restored._stop_owned(process, {321: "parent", 322: "child", 323: "old-child"})
    assert killed == [(322, 9)]


@pytest.mark.parametrize("state", ["live", "expired", "taskkill-fails"])
def test_windows_cleanup_targets_only_original_live_popen_tree(monkeypatch, state):
    from types import SimpleNamespace

    process = SimpleNamespace(pid=321, returncode=0 if state == "expired" else None)
    calls = []
    process.poll = lambda: process.returncode

    def kill():
        calls.append("kill-original-handle")
        process.returncode = -9

    process.kill = kill
    process.wait = lambda **kwargs: calls.append(("wait", kwargs))
    monkeypatch.setattr(ci_restored, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(ci_restored, "_owned_snapshot", lambda *a: pytest.fail("no POSIX PID scan"))

    def taskkill(argv, **kwargs):
        calls.append((argv, kwargs))
        if state != "taskkill-fails":
            process.returncode = -9
        return SimpleNamespace(returncode=1 if state == "taskkill-fails" else 0)

    monkeypatch.setattr(ci_restored.subprocess, "run", taskkill)
    if state == "taskkill-fails":
        with pytest.raises(RuntimeError, match="Owned subprocess cleanup failed"):
            ci_restored._stop_owned(process, {999: "must-not-use-this-PID"})
    else:
        ci_restored._stop_owned(process, {999: "must-not-use-this-PID"})
    commands = [call for call in calls if isinstance(call, tuple) and isinstance(call[0], list)]
    assert len(commands) == (0 if state == "expired" else 1)
    if commands:
        assert commands[0][0] == ["taskkill", "/F", "/T", "/PID", "321"]
        assert commands[0][1]["timeout"] == 20
    assert ("kill-original-handle" in calls) is (state == "taskkill-fails")


@pytest.mark.skipif(
    os.name == "nt" or not Path("/proc").is_dir(), reason="Linux identity integration"
)
@pytest.mark.parametrize("exit_early", [False, True, "immediate"])
def test_real_timeout_or_failed_leader_cleans_detached_child_without_touching_foreign(
    tmp_path, exit_early
):
    import json
    import signal
    import sys
    import time

    child_file = tmp_path / "owned-child.json"
    code = """
import json, subprocess, sys, time
from pathlib import Path
child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], start_new_session=True)
started = Path(f'/proc/{child.pid}/stat').read_text().rsplit(') ',1)[1].split()[19]
Path(sys.argv[1]).write_text(json.dumps({'pid': child.pid, 'started': started}))
time.sleep(0 if sys.argv[2] == 'immediate' else 1.3 if sys.argv[2] == 'early' else 30)
raise SystemExit(7)
"""
    foreign = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    report = {}
    try:
        with pytest.raises(
            subprocess.CalledProcessError if exit_early else subprocess.TimeoutExpired
        ):
            ci_restored.run_owned(
                [sys.executable, "-c", code, str(child_file), "early" if exit_early else "wait"],
                cwd=tmp_path,
                env=dict(os.environ),
                timeout=2,
                report=report,
            )
        owned = json.loads(child_file.read_text())
        assert foreign.poll() is None
        assert report["cleanup_error_type"] is None
        assert report["owned_processes_observed"] >= (1 if exit_early == "immediate" else 2)
        for _ in range(50):
            path = Path(f"/proc/{owned['pid']}/stat")
            try:
                fields = path.read_text().rsplit(") ", 1)[1].split()
            except OSError:
                break
            if fields[0] == "Z" or fields[19] != owned["started"]:
                break
            time.sleep(0.02)
        else:
            pytest.fail("Detached owned child survived")
    finally:
        if child_file.is_file():
            owned = json.loads(child_file.read_text())
            identity = ci_restored._process_identity(owned["pid"])
            if identity is not None and identity[1] == owned["started"]:
                try:
                    os.kill(owned["pid"], signal.SIGKILL)
                except ProcessLookupError:
                    pass
        foreign.terminate()
        foreign.wait(timeout=5)


@pytest.mark.parametrize("step", ["browser_preflight", "locate_npm", "node_install", "node_build"])
@pytest.mark.parametrize("phase", ["tests", "browser", "install"])
def test_inside_early_setup_failure_always_has_structured_bound_evidence(
    monkeypatch, tmp_path, step, phase
):
    import workbench.store

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(workbench.store, "__file__", str(tmp_path / "workbench/store.py"))
    monkeypatch.setattr(
        ci_restored, "run_binding", lambda: {"head": "a" * 40, "run": "123", "attempt": "2"}
    )

    def preflight(*args):
        if step == "browser_preflight":
            raise RuntimeError("preflight canary")

    monkeypatch.setattr(ci_learning_docs, "browser_preflight", preflight)
    monkeypatch.setattr(
        ci_restored.shutil, "which", lambda name: None if step == "locate_npm" else "/tools/npm"
    )

    def run(argv, **kwargs):
        if step == "node_install" and "ci" in argv or step == "node_build" and "build" in argv:
            raise subprocess.CalledProcessError(9, argv)

    monkeypatch.setattr(ci_restored, "run_owned", run)
    output = tmp_path / "evidence"
    with pytest.raises((RuntimeError, subprocess.CalledProcessError)):
        ci_restored.inside(phase, output, 0, 4, "b" * 64)
    result = read_json(output / "restored.json")
    assert result["passed"] is False and result["phase"] == phase and result["step"] == step
    assert result["binding"]["source_digest"] == "b" * 64
    assert result["original_project_imported"] is False
    assert "error_type" in result
    assert not (output / "complete.json").exists()


def test_missing_uv_is_preserved_as_bootstrap_failure(monkeypatch, tmp_path):
    configure_main(monkeypatch, tmp_path)
    monkeypatch.setattr(ci_restored.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="requires uv"):
        ci_restored.main()
    report = read_json(tmp_path / "evidence/bootstrap.json")
    assert report["passed"] is False and report["step"] == "locate_uv"
    assert report["error_type"] == "RuntimeError"


@pytest.mark.parametrize("fail_at", [1, 2])
def test_bootstrap_timeout_has_phase_identity_and_diagnostics(monkeypatch, tmp_path, fail_at):
    calls = configure_main(monkeypatch, tmp_path)

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        if len(calls) - 1 == fail_at:
            kwargs["report"].update(timed_out=True, cleanup_error_type=None)
            raise subprocess.TimeoutExpired(argv, kwargs["timeout"])

    monkeypatch.setattr(ci_restored, "run_owned", run)
    with pytest.raises(subprocess.TimeoutExpired) as failure:
        ci_restored.main()
    assert failure.value.timeout == (900 if fail_at == 1 else 3300)
    report = read_json(tmp_path / "evidence/bootstrap.json")
    assert report["passed"] is False
    assert report["step"] == ("locked_install" if fail_at == 1 else "restored_worker")
    assert report["binding"]["head"] == "a" * 40 and report["source_digest"] == "b" * 64
    assert report["process"]["timed_out"] is True
    assert report["error_type"] == "TimeoutExpired"


@pytest.mark.parametrize("failure", [False, True])
def test_inside_shard_retains_original_fresh_directory_contract_and_terminal_status(
    monkeypatch, tmp_path, failure
):
    import workbench.store
    from scripts import ci_pytest

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(workbench.store, "__file__", str(tmp_path / "workbench/store.py"))
    monkeypatch.setattr(
        ci_restored, "run_binding", lambda: {"head": "a" * 40, "run": "123", "attempt": "2"}
    )
    monkeypatch.setattr(ci_learning_docs, "browser_preflight", lambda *a: None)
    monkeypatch.setattr(ci_restored.shutil, "which", lambda name: "/tools/npm")
    monkeypatch.setattr(ci_restored, "run_owned", lambda *a, **k: None)

    def shard(output, origin, index, count, digest):
        assert not output.exists()
        assert (origin, index, count, digest) == ("restored", 2, 4, "b" * 64)
        output.mkdir()
        (output / "pytest.log").write_text("current shard log")
        if failure:
            raise subprocess.CalledProcessError(1, ["pytest"])

    monkeypatch.setattr(ci_pytest, "run_shard", shard)
    output = tmp_path / "evidence"
    if failure:
        with pytest.raises(subprocess.CalledProcessError):
            ci_restored.inside("tests", output, 2, 4, "b" * 64)
    else:
        ci_restored.inside("tests", output, 2, 4, "b" * 64)
    assert read_json(output / "restored.json")["passed"] is (not failure)
    assert (output / "pytest.log").read_text() == "current shard log"


def test_bootstrap_and_inside_refuse_stale_success_without_overwriting(monkeypatch, tmp_path):
    configure_main(monkeypatch, tmp_path)
    output = tmp_path / "evidence"
    output.mkdir()
    previous = output / "restored.json"
    previous.write_text('{"passed":true}')
    with pytest.raises(ValueError, match="must be fresh"):
        ci_restored.main()
    with pytest.raises(ValueError, match="must be fresh"):
        ci_restored.inside("tests", output, 0, 4, "b" * 64)
    assert previous.read_text() == '{"passed":true}'
````
