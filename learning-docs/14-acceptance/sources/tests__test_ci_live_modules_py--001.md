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
- `test_failure_receipt_never_publishes_raw_provider_error`（L84–L99）：接收`tmp_path`、`monkeypatch`。 控制顺序：L85遍历`dispatch().items()`；L98断言`"secret-and-untrusted" not in raw`；L99断言`json.loads(raw)["real_model_acceptance"] is False`。 调用`dispatch().items`、`dispatch`、`monkeypatch.setenv`、`monkeypatch.setattr`、`pytest.raises`、`live.main`、`live.REPORT.read_text`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_receipt_never_publishes_raw_provider_error.reject`（L91–L92）：接收`*args`。 控制顺序：L92抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reviewed_scenarios_and_consumer_preserve_isolation`（L102–L119）：接收`tmp_path`。 控制顺序：L109断言`len(plan.tasks) == 2`；L110断言`all(t.executor == "mini_swe" and t.max_steps == 8 for t in plan.tasks)`；L111断言`plan.selection.template == "python-basic" and plan.selection.database == "sqlite"`；L112遍历`plan.scenarios`；L113断言`any(s.status == 401 for s in scenario.steps)`；L114断言`any(s.body.get("status") == "resolved" for s in scenario.steps if s.body)`；L115断言`any(s.body.get("due_at", "").startswith("2099") for s in scenario.steps if s.body)`；L116断言`any(s.equals.get("$.overdue") == 0 for s in scenario.after_restart)`。后续分支沿下方源码相同行号继续阅读。 调用`live.acceptance_design`、`len`、`all`、`any`、`s.body.get`、`s.body.get("due_at", "").startswith`、`s.equals.get`、`generate_basic`、`plan.selection.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_isolation_stops_before_any_model_or_worker`（L122–L134）：接收`settings`、`tmp_path`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`live.execute`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_isolation_stops_before_any_model_or_worker.reject`（L129–L130）：接收`*args`。 控制顺序：L130抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip`（L138–L201）：接收`settings`、`tmp_path`、`monkeypatch`、`reject_proof`。 控制顺序：L187按`reject_proof`分支；L190断言`json.loads((tmp_path / "ledger/current.json").read_text())["version"] == 0`；L191断言`not (tmp_path / "delivery.zip").exists()`；L194断言`result["real_model_calls"] == 2`；L195断言`seen == [ ("sla-api-candidate", False), ("sla-dashboard-candidate", False), ("fresh-c…`；L200断言`consumers == ["fresh-consumer"]`；L201断言`result["full_workflow_crash_recovery"] is False`。 调用`monkeypatch.setattr`、`consumers.append`、`pytest.raises`、`live.execute`、`json.loads`、`(tmp_path / "ledger/current.json").read_text`、`(tmp_path / "delivery.zip").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip.mock_agent`（L152–L164）：接收`settings`、`gateway`、`run_id`、`task`、`plan`、`product`、`workspace`、`context`。 调用`gateway.store.reserve_model_call`、`authored_files`、`(product / "app.py").read_text`、`write_json`、`CapabilityEdits`、`manifest(product).get`、`manifest`、`sources.items`。 返回路径：L158的`CapabilityEdits( explanation="explicit offline fixture", files=[ {"path": name, "before_sh…`。
- `test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip.mock_verify`（L166–L173）：接收`product`、`plan`、`scenarios`、`settings`、`aggregate`、`selection`。 调用`seen.append`、`digest`、`plan.model_dump`、`manifest`。 返回路径：L168的`{ "passed": not reject_proof, "cleanup": "deleted", "plan_digest": digest(plan.model_dump(…`。
- `test_mock_orchestration_requires_proof_before_promotion_and_fresh_zip.mock_require`（L175–L178）：接收`proof`、`**kwargs`。 控制顺序：L177按`not proof["passed"]`分支；L178抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_only_exposes_key_after_preflight_and_real_security`（L204–L218）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L207断言`job["environment"] == "rnd" and job["timeout-minutes"] == 90`；L208断言`"workflow_dispatch" in job["if"] and "run_attempt == 1" in job["if"]`；L214断言`preflight < security < paid`；L215断言`"API_KEY" not in job["env"]`；L216断言`[i for i, s in enumerate(steps) if "API_KEY" in s.get("env", {})] == [paid]`；L217断言`"ALLOW_INSECURE_MODEL_HTTP" not in json.dumps(job)`；L218断言`workflow["permissions"] == {"contents": "read"}`。 调用`yaml.safe_load`、`(live.ROOT / ".github/workflows/real-model.yml").read_text`、`s.get`、`commands.index`、`enumerate`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_ci_live_modules.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L218。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9422`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_ci_live_modules.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4f9bf20305c0ebca62a07e07627bda0e2e3983f921ddea256e154acebdb502ab"} -->
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

    def reject(*args):
        raise RuntimeError("secret-and-untrusted-provider-text")

    monkeypatch.setattr(live, "execute", reject)
    with pytest.raises(SystemExit):
        live.main()
    raw = live.REPORT.read_text()
    assert "secret-and-untrusted" not in raw
    assert json.loads(raw)["real_model_acceptance"] is False


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
````
