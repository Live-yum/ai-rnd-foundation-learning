# tests/test_capability_contest_integration.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_capability_profile`、`scripts.ci_contest_capability`、`scripts.extension_oracles`、`workbench`、`workbench.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_native_oracle_runs_initial_restart_and_fresh_replay`（L16–L145）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L49遍历`("inspect_stack", "require_container_evidence", "prepare_identity…`；L69遍历`("prepare_readonly_dependencies", "verify_readonly_dependencies")`；L144断言`events.index("restart-oracle") < events.index("fresh-db") < events.index("empty-oracl…`；L145断言`events.count("initial") == 2 and events[-1] == "deleted"`。 调用`fixed_application`、`Selection`、`SimpleNamespace`、`events.append`、`monkeypatch.setattr`、`real_client`、`httpx.MockTransport`、`httpx.Response`、`profile_record`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_oracle_runs_initial_restart_and_fresh_replay.Adapter`（L102–L110）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_native_oracle_runs_initial_restart_and_fresh_replay.Adapter.__init__`（L103–L107）：接收`*a`。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_oracle_runs_initial_restart_and_fresh_replay.Adapter.close`（L109–L110）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_oracle_runs_initial_restart_and_fresh_replay.initial`（L114–L116）：接收`*a`。 调用`events.append`、`object`。 返回路径：L116的`object(), {key: True for key in contest.SEMANTICS[:5]}`。
- `test_business_proof_rejects_incomplete_or_self_reported_results`（L151–L174）：接收`mutation`。 控制顺序：L165按`mutation == "self-report"`分支；L167按`mutation == "missing-replay"`分支；L169按`mutation == "full-complete"`分支；L171按`mutation == "missing-cleanup"`分支。 调用`list`、`pytest.raises`、`require_business_proof`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_contest_integration.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L174。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7090`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_contest_integration.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8006e8bbf8cbb2dd7378a814b610acb0e7c6191646da048add7afad468f54457"} -->
````python
# tests/test_capability_contest_integration.py
"""Mocked lifecycle wiring only; real CI must prove application/business behavior."""

from types import SimpleNamespace

import httpx
import pytest
from capability_dependency_fixtures import container_binding, dependency_evidence, profile_record

from scripts.ci_capability_profile import fixed_application
from scripts.ci_contest_capability import require_business_proof
from scripts.extension_oracles import contest
from workbench import capability_sandbox as verifier
from workbench.catalog import Selection


def test_native_oracle_runs_initial_restart_and_fresh_replay(settings, tmp_path, monkeypatch):
    product = tmp_path / "product"
    plan = fixed_application(product)
    plan.selection = Selection(template="fastapiadmin")
    plan.runtime.prepare = []
    settings.daytona_snapshot = "owned-native"
    identifier = "00000000-0000-0000-0000-000000000001"
    events = []
    sandbox = SimpleNamespace(
        id=identifier,
        network_block_all=True,
        public=False,
        refresh_data=lambda: None,
        fs=SimpleNamespace(create_folder=lambda *a: None, upload_file=lambda *a, **kw: None),
        process=SimpleNamespace(
            create_session=lambda *a: None,
            execute_session_command=lambda *a, **kw: SimpleNamespace(cmd_id="owned-command"),
        ),
        get_preview_link=lambda port: SimpleNamespace(
            url=f"http://{port}-{identifier}.proxy.localhost", token="owned"
        ),
    )
    daytona = SimpleNamespace(
        create=lambda *a, **kw: sandbox, delete=lambda *a, **kw: events.append("deleted")
    )
    real_client = httpx.Client
    monkeypatch.setattr(
        verifier.httpx,
        "Client",
        lambda **kw: real_client(
            **kw, transport=httpx.MockTransport(lambda req: httpx.Response(200))
        ),
    )
    for name in ("inspect_stack", "require_container_evidence", "prepare_identity"):
        monkeypatch.setattr(verifier, name, lambda *a: {})
    admitted = profile_record(template="fastapiadmin")
    monkeypatch.setattr(
        verifier, "require_container_evidence", lambda *a: container_binding(admitted)
    )
    # This authored business-oracle wiring fixture is not dependency admission.
    # Separate dependency contract tests exercise the strict real validators.
    from workbench import capability_dependencies as dependencies

    monkeypatch.setattr(dependencies, "require_dependency_descriptors", lambda *a: None)
    monkeypatch.setattr(dependencies, "readonly_prepare_commands", lambda *a: [])
    monkeypatch.setattr(
        dependencies,
        "readonly_start_command",
        lambda plan, command=None: command or plan.runtime.start,
    )
    proof = dependency_evidence(
        admitted["snapshot"]["dependency_manifest"], verifier.manifest(product)
    )
    for name in ("prepare_readonly_dependencies", "verify_readonly_dependencies"):
        monkeypatch.setattr(dependencies, name, lambda *a, **k: proof.copy())
    monkeypatch.setattr(verifier, "control_exec", lambda *a: SimpleNamespace(exit_code=0))
    monkeypatch.setattr(verifier, "prepare_database", lambda *a: "synthetic")
    monkeypatch.setattr(verifier, "database_environment", lambda *a: {})
    monkeypatch.setattr("workbench.capability_services.prepare_native_services", lambda *a: {})
    monkeypatch.setattr(
        "workbench.capability_services.reset_owned_native_cache",
        lambda *a: events.append("fresh-cache"),
    )
    monkeypatch.setattr("workbench.capability_native_runtime.native_start_command", lambda *a: None)
    monkeypatch.setattr("workbench.capability_native_runtime.native_prepare_commands", lambda: [])
    monkeypatch.setattr(
        "workbench.capability_native_runtime.verify_and_freeze_native_sources", lambda *a: None
    )
    monkeypatch.setattr(
        "workbench.capability_stack.owned_database_identity",
        lambda *a: {"cluster": "owned", "database_oid": 1},
    )
    monkeypatch.setattr(
        "workbench.capability_stack.recreate_owned_native_database",
        lambda *a: events.append("fresh-db") or {"cluster": "owned", "database_oid": 2},
    )
    monkeypatch.setattr(
        verifier, "restart_application_identity", lambda *a, **kw: events.append("drain")
    )
    counts = iter([0, 1, 1])
    monkeypatch.setattr(verifier, "database_counts", lambda *a: {"rows": next(counts)})
    monkeypatch.setattr(verifier, "run_scenarios", lambda *a, **kw: ([], {}))
    monkeypatch.setattr(
        "workbench.capability_browser_isolation.run_isolated_browser", lambda *a, **kw: []
    )

    class Adapter:
        def __init__(self, *a):
            self.actor_ids = {}
            self.http = lambda *a: None
            self.probe = lambda *a: None
            events.append("adapter")

        def close(self):
            events.append("closed")

    monkeypatch.setattr("workbench.capability_contest_oracle.ContestOracleAdapter", Adapter)

    def initial(*a):
        events.append("initial")
        return object(), {key: True for key in contest.SEMANTICS[:5]}

    monkeypatch.setattr(contest, "initial", initial)
    monkeypatch.setattr(
        contest,
        "after_restart",
        lambda *a: events.append("restart-oracle") or {"postgres.restart_retention": True},
    )
    monkeypatch.setattr(
        contest,
        "fresh_database",
        lambda *a: events.append("empty-oracle") or {"postgres.fresh_database": True},
    )
    result = verifier._verify(
        product,
        plan,
        plan.scenarios,
        settings,
        plan.selection.model_dump(),
        tmp_path / "receipt.json",
        client=daytona,
        aggregate=True,
        profile_record=admitted,
        control_observer=lambda _: {},
        security_probe=lambda *a: {},
        trusted_oracle=contest.CONTRACT_VERSION,
    )
    require_business_proof(result)
    assert events.index("restart-oracle") < events.index("fresh-db") < events.index("empty-oracle")
    assert events.count("initial") == 2 and events[-1] == "deleted"


@pytest.mark.parametrize(
    "mutation", ["self-report", "missing-replay", "full-complete", "missing-cleanup"]
)
def test_business_proof_rejects_incomplete_or_self_reported_results(mutation):
    proof = {
        "passed": True,
        "cleanup": "deleted",
        "business_oracle": {
            "protocol": contest.CONTRACT_VERSION,
            "full_request_complete": False,
            "remaining_obligations": list(contest.REMAINING),
            "fresh_replay": True,
            "same_cluster": True,
            "distinct_database_oid": True,
            "witnesses": {key: True for key in contest.SEMANTICS},
        },
    }
    if mutation == "self-report":
        proof["business_oracle"]["witnesses"] = {"passed": True}
    if mutation == "missing-replay":
        proof["business_oracle"]["fresh_replay"] = False
    if mutation == "full-complete":
        proof["business_oracle"]["full_request_complete"] = True
    if mutation == "missing-cleanup":
        proof["cleanup"] = "unknown"
    with pytest.raises(ValueError):
        require_business_proof(proof)
````
