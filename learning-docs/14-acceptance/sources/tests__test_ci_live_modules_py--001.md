# tests/test_ci_live_modules.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.sla_fixture`、`workbench.core.contracts`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `dispatch`（L14–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L15的`{ "GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": live.REPOSITORY, "GITHUB_EVENT_NAME": "wo…`。
- `test_preflight_rejects_unreviewed_or_unbounded_dispatch`（L51–L53）：接收`key`、`value`。 调用`pytest.raises`、`live.configuration`、`dispatch`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preflight_needs_no_key_and_cannot_report_real_acceptance`（L56–L67）：接收`tmp_path`、`monkeypatch`。 控制顺序：L57遍历`dispatch().items()`；L65断言`summary["configuration_valid"] is True`；L66断言`summary["passed"] is summary["real_model_acceptance"] is False`；L67断言`summary["limits"]["max_model_calls"] == 32`。 调用`dispatch().items`、`dispatch`、`monkeypatch.setenv`、`monkeypatch.delenv`、`monkeypatch.setattr`、`pytest.fail`、`live.main`、`json.loads`、`live.REPORT.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_profile_pins_https_costs_and_coding_stage`（L70–L81）：接收`tmp_path`、`monkeypatch`。 控制顺序：L74断言`settings.allow_insecure_model_http is False`；L75断言`settings.mini_swe_enabled is True`；L76断言`settings.mini_swe_max_cost_usd * 2 == 5`；L77断言`settings.mini_swe_usd_per_million_tokens == 1`；L78断言`settings.max_model_calls == 32`；L80断言`profile.base_url == env["BASE_URL"]`；L81断言`profile.max_output_tokens == 8192`。 调用`monkeypatch.setattr`、`dispatch`、`live.live_settings`、`live.configuration`、`settings.model_for`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_receipt_never_publishes_raw_provider_error`（L84–L100）：接收`tmp_path`、`monkeypatch`。 控制顺序：L85遍历`dispatch().items()`；L98断言`"secret-and-untrusted" not in raw`；L99断言`json.loads(raw)["real_model_acceptance"] is False`；L100断言`json.loads(raw)["failure_diagnostic"]["exception_type"] == "RuntimeError"`。 调用`dispatch().items`、`dispatch`、`monkeypatch.setenv`、`monkeypatch.setattr`、`pytest.raises`、`live.main`、`live.REPORT.read_text`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_receipt_never_publishes_raw_provider_error.reject`（L91–L92）：接收`*args`、`**kwargs`。 控制顺序：L92抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_locates_real_sandbox_boundary_without_sdk_text`（L103–L128）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L124断言`diagnostic["stage"] == "coding_sandbox"`；L125断言`diagnostic["exception_type"] == "RuntimeError"`；L126断言`type(diagnostic["trusted_source_line"]) is int`；L127断言`"private" not in json.dumps(diagnostic)`；L128断言`closed == [client]`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`closed.append`、`live.acceptance_design`、`pytest.raises`、`coding.coding_environment`、`plan.selection.model_dump`、`pytest.fail`、`live.failure_diagnostic`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_locates_real_sandbox_boundary_without_sdk_text.reject`（L110–L111）：接收`*args`、`**kwargs`。 控制顺序：L111抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_suppresses_unknown_exception_names_and_untrusted_frames`（L131–L137）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L134抛异常，停止当前正常路径；L137断言`diagnostic == {"exception_type": "other", "stage": "other"}`。 调用`type("private-provider-content", (Exception,), {})`、`type`、`live.failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_retains_only_bounded_inspector_facts`（L140–L153）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L149断言`diagnostic["container"] == { "container_rejection": "container_policy", "network_mode…`；L153断言`"private" not in json.dumps(diagnostic)`。 调用`ContainerInspectionRejected`、`live.failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_worker_and_live_context_reach_offline_transport`（L157–L203）：接收`tmp_path`、`monkeypatch`、`receipt_read_fails`。 源码说明：Exercise pre-call orchestration; this supplies no real sandbox/model evidence.。 控制顺序：L169按`not worker_python().is_file()`分支；L191按`receipt_read_fails`分支；L201断言`seen == ["/v1/chat/completions"]`；L202断言`progress["model_call_reservations"] == 1`；L203断言`progress["model_failure_receipts"] == (None if receipt_read_fails else [])`。 调用`worker_python().is_file`、`worker_python`、`pytest.skip`、`monkeypatch.setattr`、`dispatch`、`live.live_settings`、`live.configuration`、`OfflineTransport`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_worker_and_live_context_reach_offline_transport.offline_environment`（L173–L174）：接收`*args`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_real_worker_and_live_context_reach_offline_transport.stop`（L183–L185）：接收`request`。 控制顺序：L185抛异常，停止当前正常路径。 调用`seen.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_worker_and_live_context_reach_offline_transport.OfflineTransport`（L187–L189）：继承`httpx.MockTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_worker_and_live_context_reach_offline_transport.unavailable`（L194–L195）：接收`*args`。 控制顺序：L195抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reviewed_scenarios_and_consumer_preserve_isolation`（L206–L223）：接收`tmp_path`。 控制顺序：L213断言`len(plan.tasks) == 2`；L214断言`all(t.executor == "mini_swe" and t.max_steps == 8 for t in plan.tasks)`；L215断言`plan.selection.template == "python-basic" and plan.selection.database == "sqlite"`；L216遍历`plan.scenarios`；L217断言`any(s.status == 401 for s in scenario.steps)`；L218断言`any(s.body.get("status") == "resolved" for s in scenario.steps if s.body)`；L219断言`any(s.body.get("due_at", "").startswith("2099") for s in scenario.steps if s.body)`；L220断言`any(s.equals.get("$.overdue") == 0 for s in scenario.after_restart)`。后续分支沿下方源码相同行号继续阅读。 调用`live.acceptance_design`、`len`、`all`、`any`、`s.body.get`、`s.body.get("due_at", "").startswith`、`s.equals.get`、`generate_basic`、`plan.selection.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_isolation_stops_before_any_model_or_worker`（L226–L238）：接收`settings`、`tmp_path`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`live.execute`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_isolation_stops_before_any_model_or_worker.reject`（L233–L234）：接收`*args`。 控制顺序：L234抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip`（L242–L305）：接收`settings`、`tmp_path`、`monkeypatch`、`reject_proof`。 控制顺序：L291按`reject_proof`分支；L294断言`json.loads((tmp_path / "ledger/current.json").read_text())["version"] == 0`；L295断言`not (tmp_path / "delivery.zip").exists()`；L298断言`result["real_model_calls"] == 2`；L299断言`seen == [ ("sla-api-candidate", False), ("sla-dashboard-candidate", False), ("fresh-c…`；L304断言`consumers == ["fresh-consumer"]`；L305断言`result["full_workflow_crash_recovery"] is False`。 调用`monkeypatch.setattr`、`consumers.append`、`pytest.raises`、`live.execute`、`json.loads`、`(tmp_path / "ledger/current.json").read_text`、`(tmp_path / "delivery.zip").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip.mock_agent`（L256–L268）：接收`settings`、`gateway`、`run_id`、`task`、`plan`、`product`、`workspace`、`context`。 调用`gateway.store.reserve_model_call`、`authored_files`、`(product / "app.py").read_text`、`write_json`、`CapabilityEdits`、`manifest(product).get`、`manifest`、`sources.items`。 返回路径：L262的`CapabilityEdits( explanation="explicit offline fixture", files=[ {"path": name, "before_sh…`。
- `test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip.mock_verify`（L270–L277）：接收`product`、`plan`、`scenarios`、`settings`、`aggregate`、`selection`。 调用`seen.append`、`digest`、`plan.model_dump`、`manifest`。 返回路径：L272的`{ "passed": not reject_proof, "cleanup": "deleted", "plan_digest": digest(plan.model_dump(…`。
- `test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip.mock_require`（L279–L282）：接收`proof`、`**kwargs`。 控制顺序：L281按`not proof["passed"]`分支；L282抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_only_exposes_key_after_preflight_and_real_security`（L308–L322）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L311断言`job["environment"] == "rnd" and job["timeout-minutes"] == 90`；L312断言`"workflow_dispatch" in job["if"] and "run_attempt == 1" in job["if"]`；L318断言`preflight < security < paid`；L319断言`"API_KEY" not in job["env"]`；L320断言`[i for i, s in enumerate(steps) if "API_KEY" in s.get("env", {})] == [paid]`；L321断言`"ALLOW_INSECURE_MODEL_HTTP" not in json.dumps(job)`；L322断言`workflow["permissions"] == {"contents": "read"}`。 调用`yaml.safe_load`、`(live.ROOT / ".github/workflows/real-model.yml").read_text`、`s.get`、`commands.index`、`enumerate`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_receipts_are_bounded_and_drop_all_unapproved_fields`（L325–L352）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L344断言`live.model_failure_receipts(records) == [ {"code": "other", "attempt": None}, {"code"…`；L351断言`len(result) == live.MODEL_CALLS`；L352断言`"private" not in json.dumps(result)`。 调用`live.model_failure_receipts`、`len`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_failure_reaches_final_artifact_after_workspace_deletion`（L355–L413）：接收`tmp_path`、`monkeypatch`。 控制顺序：L359遍历`dispatch().items()`；L401断言`error.value.code == 1`；L402断言`all(not path.exists() for path in directories)`；L405断言`report["passed"] is report["real_model_acceptance"] is False`；L406断言`report["failure_diagnostic"]["exception_type"] == "PrerequisiteError"`；L408断言`node["exception_type"] == "ValueError"`；L409断言`node["cleanup"] == "deleted" and node["checks_count"] == 1`；L410断言`node["startup"]["http_status"] == 502`。后续分支沿下方源码相同行号继续阅读。 调用`dispatch().items`、`dispatch`、`monkeypatch.setenv`、`monkeypatch.setattr`、`pytest.raises`、`live.main`、`all`、`path.exists`、`live.REPORT.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_failure_reaches_final_artifact_after_workspace_deletion.execute`（L366–L396）：接收`settings`、`directory`、`progress`、`**kwargs`。 调用`directories.append`、`write_json`、`live.verify_with_diagnostics`。 返回路径：L396的`live.verify_with_diagnostics(reject, product, aggregate=False, progress=progress)`。
- `test_node_failure_reaches_final_artifact_after_workspace_deletion.execute.reject`（L389–L394）：接收`*args`、`**kwargs`。 控制顺序：L391抛异常，停止当前正常路径；L394抛异常，停止当前正常路径。 调用`ValueError`、`record_failure`、`PrerequisiteError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_diagnostic_read_failure_preserves_original_oracle_error`（L416–L432）：接收`monkeypatch`、`tmp_path`。 控制顺序：L431断言`error.value is original`；L432断言`progress["verification_diagnostic_unavailable"] is True`。 调用`monkeypatch.setattr`、`ValueError`、`pytest.raises`、`live.verify_with_diagnostics`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_diagnostic_read_failure_preserves_original_oracle_error.unavailable`（L419–L420）：接收`*args`、`**kwargs`。 控制顺序：L420抛异常，停止当前正常路径。 调用`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_diagnostic_read_failure_preserves_original_oracle_error.reject`（L425–L426）：接收`*args`、`**kwargs`。 控制顺序：L426抛异常，停止当前正常路径。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_ci_live_modules.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L432。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17904`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_ci_live_modules.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2019be8fd7bdb7e37dc754ba026e6a0486bba68e90a63bb0605fc157d77e31a6"} -->
````python
# tests/test_ci_live_modules.py
"""Offline contracts only: no paid models, Docker, Daytona or live evidence."""

import json

import pytest
import yaml

from scripts import ci_live_modules as live
from scripts.sla_fixture import authored_files
from workbench.core.contracts import digest
from workbench.filesystem import manifest, write_json


def dispatch():
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": live.REPOSITORY,
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "a" * 40,
        "REVIEWED_SHA": "a" * 40,
        "LIVE_SCENARIO": live.SCENARIO,
        "BASE_URL": "https://model.invalid/v1",
        "MODE": "offline-contract",
        "LIVE_MAX_COST_USD": "5",
        "LIVE_USD_PER_MILLION_TOKENS": "1",
    }


@pytest.mark.parametrize(
    "key,value",
    [
        ("GITHUB_REPOSITORY", "other/repo"),
        ("GITHUB_EVENT_NAME", "pull_request"),
        ("GITHUB_RUN_ATTEMPT", "2"),
        ("REVIEWED_SHA", "b" * 40),
        ("LIVE_SCENARIO", "yudao-mini-swe"),
        ("BASE_URL", "http://model.invalid/v1"),
        ("BASE_URL", "https://user:password@model.invalid/v1"),
        ("BASE_URL", "https://model.invalid/v1?key=bad"),
        ("LIVE_MAX_COST_USD", "0"),
        ("LIVE_MAX_COST_USD", "11"),
        ("LIVE_MAX_COST_USD", "NaN"),
        ("LIVE_MAX_COST_USD", "Infinity"),
        ("LIVE_MAX_COST_USD", "0.0001"),
        ("LIVE_USD_PER_MILLION_TOKENS", "0"),
        ("LIVE_USD_PER_MILLION_TOKENS", "garbage"),
        ("MODE", ""),
    ],
)
def test_preflight_rejects_unreviewed_or_unbounded_dispatch(key, value):
    with pytest.raises(ValueError):
        live.configuration({**dispatch(), key: value})


def test_preflight_needs_no_key_and_cannot_report_real_acceptance(tmp_path, monkeypatch):
    for key, value in dispatch().items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.setattr(live, "REPORT", tmp_path / "summary.json")
    monkeypatch.setattr("sys.argv", ["ci_live_modules", "--preflight"])
    monkeypatch.setattr(live, "execute", lambda *a: pytest.fail("preflight called executor"))
    live.main()
    summary = json.loads(live.REPORT.read_text())
    assert summary["configuration_valid"] is True
    assert summary["passed"] is summary["real_model_acceptance"] is False
    assert summary["limits"]["max_model_calls"] == 32


def test_live_profile_pins_https_costs_and_coding_stage(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.daytona_capability_profile.HOME", tmp_path / "local-profile")
    env = {**dispatch(), "API_KEY": "offline-fixture-only"}
    settings = live.live_settings(env, live.configuration(env), tmp_path)
    assert settings.allow_insecure_model_http is False
    assert settings.mini_swe_enabled is True
    assert settings.mini_swe_max_cost_usd * 2 == 5
    assert settings.mini_swe_usd_per_million_tokens == 1
    assert settings.max_model_calls == 32
    profile = settings.model_for("coding")
    assert profile.base_url == env["BASE_URL"]
    assert profile.max_output_tokens == 8192


def test_failure_receipt_never_publishes_raw_provider_error(tmp_path, monkeypatch):
    for key, value in dispatch().items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(live, "REPORT", tmp_path / "summary.json")
    monkeypatch.setattr("sys.argv", ["ci_live_modules"])
    monkeypatch.setattr(live, "live_settings", lambda *a: None)

    def reject(*args, **kwargs):
        raise RuntimeError("secret-and-untrusted-provider-text")

    monkeypatch.setattr(live, "execute", reject)
    with pytest.raises(SystemExit):
        live.main()
    raw = live.REPORT.read_text()
    assert "secret-and-untrusted" not in raw
    assert json.loads(raw)["real_model_acceptance"] is False
    assert json.loads(raw)["failure_diagnostic"]["exception_type"] == "RuntimeError"


def test_diagnostic_locates_real_sandbox_boundary_without_sdk_text(settings, tmp_path, monkeypatch):
    from types import SimpleNamespace

    from workbench.infrastructure.sandbox import coding

    closed = []

    def reject(*args, **kwargs):
        raise RuntimeError("private endpoint key headers prompt")

    client = SimpleNamespace(create=reject)
    monkeypatch.setattr(coding, "capability_execution_prerequisites", lambda *a: (tmp_path, {}))
    monkeypatch.setattr(coding, "client_for", lambda *a: client)
    monkeypatch.setattr(coding, "close_client", lambda value: closed.append(value))
    plan = live.acceptance_design().implementation
    with pytest.raises(RuntimeError) as captured:
        with coding.coding_environment(
            settings, plan.tasks[0], plan.selection.model_dump(), tmp_path
        ):
            pytest.fail("unadmitted sandbox yielded")
    diagnostic = live.failure_diagnostic(captured.value)
    assert diagnostic["stage"] == "coding_sandbox"
    assert diagnostic["exception_type"] == "RuntimeError"
    assert type(diagnostic["trusted_source_line"]) is int
    assert "private" not in json.dumps(diagnostic)
    assert closed == [client]


def test_diagnostic_suppresses_unknown_exception_names_and_untrusted_frames():
    error = type("private-provider-content", (Exception,), {})("private-message")
    try:
        raise error
    except Exception as exc:
        diagnostic = live.failure_diagnostic(exc)
    assert diagnostic == {"exception_type": "other", "stage": "other"}


def test_diagnostic_retains_only_bounded_inspector_facts():
    from workbench.capability_isolation import ContainerInspectionRejected

    error = ContainerInspectionRejected(
        "private docker inspect output",
        category="container_policy",
        facts={"network_mode": "private-network-name", "secret": "private-key"},
    )
    diagnostic = live.failure_diagnostic(error)
    assert diagnostic["container"] == {
        "container_rejection": "container_policy",
        "network_mode": "other",
    }
    assert "private" not in json.dumps(diagnostic)


@pytest.mark.parametrize("receipt_read_fails", [False, True])
def test_real_worker_and_live_context_reach_offline_transport(
    tmp_path, monkeypatch, receipt_read_fails
):
    """Exercise pre-call orchestration; this supplies no real sandbox/model evidence."""
    from contextlib import contextmanager

    import httpx

    import workbench.capability_execution as admission
    from workbench.coding.mini_swe import worker_python
    from workbench.infrastructure.sandbox import coding

    if not worker_python().is_file():
        pytest.skip("optional locked Python3.12 worker not installed")

    @contextmanager
    def offline_environment(*args):
        yield None  # Stop at the first transport call, before any edits.

    monkeypatch.setattr(admission, "capability_execution_prerequisites", lambda *a: None)
    monkeypatch.setattr(coding, "coding_environment", offline_environment)
    monkeypatch.setattr("scripts.daytona_capability_profile.HOME", tmp_path / "absent-profile")
    env = {**dispatch(), "API_KEY": "offline-fixture-only"}
    settings = live.live_settings(env, live.configuration(env), tmp_path)
    seen = []

    def stop(request):
        seen.append(request.url.path)
        raise RuntimeError("offline pre-call boundary reached")

    class OfflineTransport(httpx.MockTransport):
        calls = 0
        responses = 0

    if receipt_read_fails:
        from workbench.store import Store

        def unavailable(*args):
            raise RuntimeError("private-receipt-error")

        monkeypatch.setattr(Store, "model_records", unavailable)
    progress = {}
    with OfflineTransport(stop) as transport, pytest.raises(Exception):
        live.execute(settings, tmp_path, transport=transport, progress=progress)
    assert seen == ["/v1/chat/completions"]
    assert progress["model_call_reservations"] == 1
    assert progress["model_failure_receipts"] == (None if receipt_read_fails else [])


def test_reviewed_scenarios_and_consumer_preserve_isolation(tmp_path):
    from workbench.capability_consumer import prepare_consumer
    from workbench.capability_dependencies import readonly_start_command
    from workbench.generator import generate_basic

    selected = live.acceptance_design()
    plan = selected.implementation
    assert len(plan.tasks) == 2
    assert all(t.executor == "mini_swe" and t.max_steps == 8 for t in plan.tasks)
    assert plan.selection.template == "python-basic" and plan.selection.database == "sqlite"
    for scenario in plan.scenarios:
        assert any(s.status == 401 for s in scenario.steps)
        assert any(s.body.get("status") == "resolved" for s in scenario.steps if s.body)
        assert any(s.body.get("due_at", "").startswith("2099") for s in scenario.steps if s.body)
        assert any(s.equals.get("$.overdue") == 0 for s in scenario.after_restart)
    generate_basic(selected.baseline, tmp_path / "product", plan.selection.model_dump())
    prepare_consumer(tmp_path / "product", plan)
    assert readonly_start_command(plan).argv[3] == "app:app"


def test_missing_isolation_stops_before_any_model_or_worker(settings, tmp_path, monkeypatch):
    import workbench.capability_execution as admission
    import workbench.coding.mini_swe as controller

    monkeypatch.setattr(controller, "worker_python", lambda: live.ROOT / "pyproject.toml")
    monkeypatch.setattr(controller, "run_agent", lambda *a: pytest.fail("agent started"))

    def reject(*args):
        raise ValueError("missing same-job security proof")

    monkeypatch.setattr(admission, "capability_execution_prerequisites", reject)
    with pytest.raises(ValueError, match="same-job"):
        live.execute(settings, tmp_path)


@pytest.mark.parametrize("reject_proof", [False, True])
def test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip(
    settings, tmp_path, monkeypatch, reject_proof
):
    import workbench.capability_consumer as consumer
    import workbench.capability_execution as admission
    import workbench.capability_sandbox as verifier
    import workbench.coding.mini_swe as controller
    import workbench.production.candidates as ledger
    from workbench.planning.contracts import CapabilityEdits

    monkeypatch.setattr(controller, "worker_python", lambda: live.ROOT / "pyproject.toml")
    monkeypatch.setattr(admission, "capability_execution_prerequisites", lambda *a: None)
    seen = []

    def mock_agent(settings, gateway, run_id, task, plan, product, workspace, context):
        gateway.store.reserve_model_call(run_id)
        sources = authored_files(task, (product / "app.py").read_text())
        write_json(
            workspace / "agent-budget.json", {"tokens_reserved": 1, "cost_reserved_usd": 0.1}
        )
        return CapabilityEdits(
            explanation="explicit offline fixture",
            files=[
                {"path": name, "before_sha256": manifest(product).get(name), "content": content}
                for name, content in sources.items()
            ],
        )

    def mock_verify(product, plan, scenarios, settings, *, aggregate, selection):
        seen.append((product.name, aggregate))
        return {
            "passed": not reject_proof,
            "cleanup": "deleted",
            "plan_digest": digest(plan.model_dump()),
            "source_digest": digest(manifest(product)),
        }

    def mock_require(proof, **kwargs):
        # Testing sequencing only; never substitutes for real require_evidence in the CLI.
        if not proof["passed"]:
            raise ValueError("independent rejection")

    monkeypatch.setattr(controller, "run_agent", mock_agent)
    monkeypatch.setattr(verifier, "verify_capabilities", mock_verify)
    monkeypatch.setattr(ledger, "require_evidence", mock_require)
    consumers = []
    monkeypatch.setattr(
        consumer, "require_consumer_evidence", lambda *a: consumers.append(a[0].name)
    )
    if reject_proof:
        with pytest.raises(ValueError, match="independent rejection"):
            live.execute(settings, tmp_path)
        assert json.loads((tmp_path / "ledger/current.json").read_text())["version"] == 0
        assert not (tmp_path / "delivery.zip").exists()
    else:
        result = live.execute(settings, tmp_path)
        assert result["real_model_calls"] == 2  # Simulated Store reservations, NOT real calls.
        assert seen == [
            ("sla-api-candidate", False),
            ("sla-dashboard-candidate", False),
            ("fresh-consumer", True),
        ]
        assert consumers == ["fresh-consumer"]
        assert result["full_workflow_crash_recovery"] is False


def test_workflow_only_exposes_key_after_preflight_and_real_security():
    workflow = yaml.safe_load((live.ROOT / ".github/workflows/real-model.yml").read_text())
    job = workflow["jobs"]["mini-swe-sla"]
    assert job["environment"] == "rnd" and job["timeout-minutes"] == 90
    assert "workflow_dispatch" in job["if"] and "run_attempt == 1" in job["if"]
    steps = job["steps"]
    commands = [s.get("run", "") for s in steps]
    preflight = commands.index("uv run python -m scripts.ci_live_modules --preflight")
    security = commands.index("uv run python -m scripts.ci_capability_security")
    paid = commands.index("uv run python -m scripts.ci_live_modules")
    assert preflight < security < paid
    assert "API_KEY" not in job["env"]
    assert [i for i, s in enumerate(steps) if "API_KEY" in s.get("env", {})] == [paid]
    assert "ALLOW_INSECURE_MODEL_HTTP" not in json.dumps(job)
    assert workflow["permissions"] == {"contents": "read"}


def test_model_receipts_are_bounded_and_drop_all_unapproved_fields():
    poison = {
        "status": "failed",
        "code": "private-provider-code",
        "attempt": True,
        "transport_kind": "private-kind",
        "endpoint": "private-url",
        "model": "private-model",
        "diagnostic": {"details": [{"path": ["private-path"], "message": "private-message"}]},
        "headers": {"Authorization": "private-key"},
        "prompt": "private-prompt",
    }
    records = [
        poison,
        {**poison, "code": "transport_error", "attempt": 2},
        {**poison, "code": "http_429", "attempt": 1},
        {**poison, "code": "http_999", "attempt": 900},
        {**poison, "status": "validated"},
    ]
    assert live.model_failure_receipts(records) == [
        {"code": "other", "attempt": None},
        {"code": "transport_error", "attempt": 2, "transport_kind": "other"},
        {"code": "http_429", "attempt": 1},
        {"code": "other", "attempt": None},
    ]
    result = live.model_failure_receipts(records * 20)
    assert len(result) == live.MODEL_CALLS
    assert "private" not in json.dumps(result)


def test_node_failure_reaches_final_artifact_after_workspace_deletion(tmp_path, monkeypatch):
    from workbench.capability_diagnostics import record_failure
    from workbench.generator import PrerequisiteError

    for key, value in dispatch().items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(live, "REPORT", tmp_path / "summary.json")
    monkeypatch.setattr("sys.argv", ["ci_live_modules"])
    monkeypatch.setattr(live, "live_settings", lambda *a: None)
    directories = []

    def execute(settings, directory, *, progress, **kwargs):
        directories.append(directory)
        product = directory / "node"
        path = directory / "node-node-verification.json"
        write_json(
            path,
            {
                "passed": False,
                "cleanup": "deleted",
                "checks": ["private-source"],
                "error": "private-key-prompt",
                "sandbox_name": "private-path",
                "startup_diagnostic": {
                    "phase": "health_deadline",
                    "http_status": 502,
                    "command_exit_code": 1,
                    "command_exit_status": "nonzero",
                    "output_hints": ["missing-module", "private-module"],
                    "raw_output": "private",
                },
            },
        )

        def reject(*args, **kwargs):
            try:
                raise ValueError("private-headers-response")
            except ValueError as exc:
                record_failure(path, exc)
                raise PrerequisiteError("private-child-message") from None

        return live.verify_with_diagnostics(reject, product, aggregate=False, progress=progress)

    monkeypatch.setattr(live, "execute", execute)
    with pytest.raises(SystemExit) as error:
        live.main()
    assert error.value.code == 1
    assert all(not path.exists() for path in directories)
    raw = live.REPORT.read_text()
    report = json.loads(raw)
    assert report["passed"] is report["real_model_acceptance"] is False
    assert report["failure_diagnostic"]["exception_type"] == "PrerequisiteError"
    node = report["verification_receipts"][0]
    assert node["exception_type"] == "ValueError"
    assert node["cleanup"] == "deleted" and node["checks_count"] == 1
    assert node["startup"]["http_status"] == 502
    assert node["startup"]["command_exit_code"] == 1
    assert node["startup"]["output_hints"] == ["missing-module"]
    assert "private" not in raw


def test_node_diagnostic_read_failure_preserves_original_oracle_error(monkeypatch, tmp_path):
    import workbench.capability_diagnostics as diagnostics

    def unavailable(*args, **kwargs):
        raise OSError("private-path")

    monkeypatch.setattr(diagnostics, "node_diagnostic", unavailable)
    original = ValueError("original independent rejection")

    def reject(*args, **kwargs):
        raise original

    progress = {}
    with pytest.raises(ValueError) as error:
        live.verify_with_diagnostics(reject, tmp_path / "node", aggregate=False, progress=progress)
    assert error.value is original
    assert progress["verification_diagnostic_unavailable"] is True
````
