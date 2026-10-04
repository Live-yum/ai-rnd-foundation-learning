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
