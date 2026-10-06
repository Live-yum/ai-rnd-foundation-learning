"""Authored counterexamples, not live model/native acceptance attestations."""

import ast
import base64
import json
import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from scripts.capability_fixture import make_plan
from workbench.capability_contracts import CapabilityPlan, coverage_errors, scope_sources
from workbench.capability_obligations import (
    SQLITE_PROBE,
    assert_physical_rows,
    obligation_identity,
    require_obligation_evidence,
    review_contract,
    reviewed_coverage,
    run_obligation_checks,
)
from workbench.capability_policy import business_coverage, contract_errors, scope_policy
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection
from workbench.domain import digest


def proposed(text="用户创建并持久化自己的资料。"):
    sources = scope_sources([text])
    scope = {"messages": [text], "source_digest": digest([text]), "sources": sources}
    plan = make_plan(
        {
            "source_units": sources,
            "source_digest": scope["source_digest"],
            "selection": Selection().model_dump(),
        }
    )
    raw = plan.model_dump()
    raw["obligations"] = [
        {
            "id": "saved-record",
            "source_id": sources[0]["id"],
            "source_sha256": sources[0]["sha256"],
            "assertion": "资料标题写入并跨进程重启保留",
            "scenario_id": "private_records",
            "physical": {
                "table": "entries",
                "key": {"id": "${entry}"},
                "values": {"title": "持久化资料-${nonce}"},
            },
        }
    ]
    raw["complete_source_ids"] = [sources[0]["id"]]
    plan = CapabilityPlan.model_validate(raw)
    return plan, scope, scope_policy(scope, plan.selection.model_dump())


def proof_for(plan):
    return {
        "obligation_checks": [
            {
                "id": o.id,
                "contract_sha256": obligation_identity(o),
                "phase": phase,
                "passed": True,
                "observation_sha256": "a" * 64,
            }
            for o in plan.obligations
            for phase in ("initial", "restart")
        ]
    }


@pytest.mark.parametrize(
    "requirement_text",
    [
        "库存不能超卖且过期订单自动释放占用。",
        "预约改期应保留原记录并通知客户。",
        "仓库批次过期时禁止出库；并发预订不得重复占用。",
    ],
)
def test_unrelated_crud_source_ids_never_complete_original_request(requirement_text):
    sources = scope_sources([requirement_text])
    scope = {
        "messages": [requirement_text],
        "source_digest": digest([requirement_text]),
        "sources": sources,
    }
    plan = make_plan(
        {
            "source_units": sources,
            "source_digest": scope["source_digest"],
            "selection": Selection().model_dump(),
        }
    )
    # Reproduces the old false-positive structural minimum deliberately.
    assert coverage_errors(plan, sources) == []
    assert contract_errors(plan) == []
    policy = scope_policy(scope, plan.selection.model_dump())
    result = business_coverage(policy, {"passed": True, "full_request_complete": True})
    assert result["full_request_complete"] is False
    assert result["complete_source_ids"] == []
    assert {row["source_id"] for row in result["obligations"]} == {s["id"] for s in sources}
    assert all(row["status"] == "remaining" for row in result["obligations"])


def test_atomic_source_binding_and_exhaustive_claim_require_exact_review():
    plan, scope, policy = proposed()
    assert coverage_errors(plan, scope["sources"]) == []
    base = business_coverage(policy, {})
    for approval in (
        {},
        {"actor": "delegated-ai"},
        {"actor": "local-operator", "contract_digest": "b" * 64},
    ):
        with pytest.raises(CheckFailure, match="人工审阅"):
            reviewed_coverage(plan, policy, proof_for(plan), approval, base)
    approval = {"actor": "local-operator", "contract_digest": digest(review_contract(plan, policy))}
    closed = reviewed_coverage(plan, policy, proof_for(plan), approval, base)
    assert closed["full_request_complete"]
    assert closed["remaining_obligations"] == []
    assert closed["remaining_source_ids"] == []
    stale = plan.model_copy(deep=True)
    stale.obligations[0].assertion = "a changed business assertion"
    with pytest.raises(CheckFailure):
        reviewed_coverage(stale, policy, proof_for(stale), approval, base)
    plan.obligations[0].source_sha256 = "0" * 64
    assert coverage_errors(plan, scope["sources"])


@pytest.mark.parametrize("phase", ["steps", "after_restart"])
def test_candidate_cannot_replace_controller_nonce_before_write_or_after_restart(phase):
    from workbench.capability_verification import CaptureBudget

    plan, _, _ = proposed()
    raw = plan.model_dump()
    raw["scenarios"][0][phase].insert(
        0,
        {
            "method": "GET",
            "path": "/constant",
            "status": 200,
            "captures": {"nonce": "$.fixed"},
        },
    )
    with pytest.raises(ValueError, match="nonce"):
        CapabilityPlan.model_validate(raw)
    variables = {"nonce": "controller-random"}
    budget = CaptureBudget({"scenario": variables})
    with pytest.raises(CheckFailure, match="随机挑战"):
        budget.store(variables, "nonce", "app-controlled-constant")
    assert variables == {"nonce": "controller-random"}


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "stale", "changed-values", "failed"])
def test_physical_receipts_cannot_be_missing_duplicated_stale_or_restart_inconsistent(mutation):
    plan, _, _ = proposed()
    proof = proof_for(plan)
    if mutation == "missing":
        proof["obligation_checks"].pop()
    elif mutation == "duplicate":
        proof["obligation_checks"].append(deepcopy(proof["obligation_checks"][0]))
    elif mutation == "stale":
        proof["obligation_checks"][0]["contract_sha256"] = "c" * 64
    elif mutation == "changed-values":
        proof["obligation_checks"][1]["observation_sha256"] = "c" * 64
    else:
        proof["obligation_checks"][0]["passed"] = False
    with pytest.raises(CheckFailure):
        require_obligation_evidence(plan, proof, aggregate=True)


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [{"title": "constant"}],
        [{"unrelated": "value"}],
        [{"title": "random"}, {"title": "random"}],
    ],
)
def test_hardcoded_responses_unrelated_writes_and_duplicate_rows_do_not_close_obligation(rows):
    with pytest.raises(CheckFailure, match="物理值"):
        assert_physical_rows(rows, {"values": {"title": "random"}})


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_fixed_trusted_sqlite_probe_observes_real_rows_without_importing_app(tmp_path, monkeypatch):
    plan, _, _ = proposed()
    database = tmp_path / plan.runtime.database_path
    database.parent.mkdir(parents=True)
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER, title TEXT)")
        connection.execute("INSERT INTO entries VALUES(?,?)", (7, "持久化资料-run-random"))
    calls = []
    private = tmp_path / "controller-private"
    private.mkdir(mode=0o700)

    def upload(data, path, *, timeout):
        assert type(data) is bytes and len(data) <= 65536
        (private / Path(path).name).write_bytes(data)

    sandbox = SimpleNamespace(fs=SimpleNamespace(upload_file=upload))

    def trusted_exec(sandbox, argv, timeout):
        if argv[:3] == ["/usr/bin/rm", "-f", "--"]:
            (private / Path(argv[3]).name).unlink(missing_ok=True)
            return SimpleNamespace(exit_code=0)
        assert argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]
        assert timeout <= 15
        # The supervisor has separate real-process tests. This transport fixture
        # runs only its fixed reader, never UID-wide signals on the test host.
        probe = argv[4] if len(argv) == 6 else argv[-1]
        if len(argv) > 6:
            assert "ApplicationPause" in argv[4]
            assert 0 < float(argv[-2]) <= 12
        code = (
            probe.replace(
                "pathlib.Path('/tmp/rnd-capability/product')", f"pathlib.Path({str(tmp_path)!r})"
            )
            .replace(
                "pathlib.Path('/tmp/rnd-module-control/private')", f"pathlib.Path({str(private)!r})"
            )
            .replace("control_uid=0", f"control_uid={os.getuid()}")
        )
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", code, str(private / Path(argv[5]).name)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        calls.append(argv)
        return SimpleNamespace(exit_code=result.returncode, result=result.stdout)

    monkeypatch.setattr("workbench.capability_obligations.control_exec", trusted_exec)
    stopped = []
    monkeypatch.setattr(
        "workbench.capability_sandbox.restart_application_identity",
        lambda *args: stopped.append(True),
    )
    saved = {"private_records": {"entry": 7, "nonce": "run-random"}}
    first = run_obligation_checks(sandbox, plan, plan.scenarios, saved, 30, phase="initial")
    second = run_obligation_checks(sandbox, plan, plan.scenarios, saved, 30, phase="restart")
    require_obligation_evidence(plan, {"obligation_checks": first + second}, aggregate=True)
    assert len(calls) == 2
    assert stopped == [True], "Only the initial probe may destroy the application generation"
    with sqlite3.connect(database) as connection:
        connection.execute("INSERT INTO entries VALUES(?,?)", (8, "持久化资料-run-random"))
    rebound = run_obligation_checks(
        sandbox,
        plan,
        plan.scenarios,
        {"private_records": {"entry": 8, "nonce": "run-random"}},
        30,
        phase="restart",
    )
    with pytest.raises(CheckFailure, match="已改变"):
        require_obligation_evidence(plan, {"obligation_checks": first + rebound}, aggregate=True)
    with sqlite3.connect(database) as connection:
        connection.execute("UPDATE entries SET title='wrong-but-row-count-is-unchanged'")
    with pytest.raises(CheckFailure, match="物理值"):
        run_obligation_checks(sandbox, plan, plan.scenarios, saved, 30, phase="restart")


@pytest.mark.parametrize(
    "shape", ["missing-columns", "virtual-generated", "stored-generated", "view"]
)
@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_sqlite_missing_or_computed_columns_cannot_masquerade_as_physical_values(tmp_path, shape):
    database = tmp_path / "owned.db"
    with sqlite3.connect(database) as connection:
        if shape == "view":
            connection.execute(
                "CREATE VIEW entries AS SELECT 'random-value' AS title, 'missing_status' AS missing_status"
            )
        elif shape.endswith("generated"):
            mode = "STORED" if shape.startswith("stored") else "VIRTUAL"
            connection.execute(
                "CREATE TABLE entries(title TEXT, missing_status TEXT GENERATED ALWAYS AS ('missing_status') "
                + mode
                + ")"
            )
            connection.execute("INSERT INTO entries(title) VALUES('random-value')")
        else:
            connection.execute("CREATE TABLE entries(title TEXT)")
            connection.execute("INSERT INTO entries VALUES('random-value')")
    assertion = {
        "table": "entries",
        "key": {"title": "random-value"},
        "values": {"title": "random-value", "missing_status": "missing_status"},
    }
    if shape == "missing-columns":
        assertion["key"] = {"nonexistent_key": "nonexistent_key"}
    result = local_sqlite_probe(tmp_path, database.name, assertion)
    assert result.returncode != 0, result.stdout


def local_sqlite_probe(root, database, assertion, *, probe=SQLITE_PROBE):
    private = root / "controller-private"
    private.mkdir(mode=0o700, exist_ok=True)
    request = private / ("obligation-" + "a" * 32 + ".json")
    request.write_text(json.dumps({"database_path": str(database), "assertion": assertion}))
    code = (
        probe.replace("pathlib.Path('/tmp/rnd-capability/product')", f"pathlib.Path({str(root)!r})")
        .replace(
            "pathlib.Path('/tmp/rnd-module-control/private')", f"pathlib.Path({str(private)!r})"
        )
        .replace("control_uid=0", f"control_uid={os.getuid()}")
    )
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", code, str(request)],
            capture_output=True,
            text=True,
            timeout=10,
        )
    finally:
        request.unlink(missing_ok=True)
    assert list(private.iterdir()) == [], "Private observations must be removed even on failure"
    return result


@pytest.mark.parametrize("shape", ["database", "directory", "wal", "journal", "hardlink", "fifo"])
@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_root_sqlite_never_follows_candidate_links_or_special_files(tmp_path, shape):
    inside = tmp_path / "data"
    inside.mkdir()
    database = inside / "owned.db"
    outside = tmp_path / "private.db"
    with sqlite3.connect(outside) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
        connection.execute("INSERT INTO entries VALUES(7,'secret')")
    if shape == "database":
        database.symlink_to(outside)
    elif shape == "hardlink":
        os.link(outside, database)
    elif shape == "fifo":
        if not hasattr(os, "mkfifo"):
            pytest.skip("POSIX FIFO fixture")
        os.mkfifo(database)
    elif shape == "directory":
        inside.rmdir()
        inside.symlink_to(tmp_path, target_is_directory=True)
        database = inside / "private.db"
    else:
        database.write_bytes(outside.read_bytes())
        database.with_name(database.name + "-" + shape).symlink_to(outside)
    result = local_sqlite_probe(
        tmp_path,
        database.relative_to(tmp_path),
        {"table": "entries", "key": {"id": 7}, "values": {"title": "secret"}},
    )
    assert result.returncode != 0
    assert "secret" not in result.stdout
    with sqlite3.connect(outside) as connection:
        assert connection.execute("SELECT title FROM entries").fetchone() == ("secret",)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
@pytest.mark.parametrize("swapped", ["database", "directory"])
def test_candidate_rename_after_open_cannot_redirect_root_sqlite(tmp_path, swapped):
    inside = tmp_path / "data"
    inside.mkdir()
    database = inside / "owned.db"
    outside = tmp_path / "outside"
    outside.mkdir()
    for path, value in ((database, "retained"), (outside / "owned.db", "secret")):
        with sqlite3.connect(path) as connection:
            connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
            connection.execute("INSERT INTO entries VALUES(7,?)", (value,))
    entry = database if swapped == "database" else inside
    target = outside / "owned.db" if swapped == "database" else outside
    # Deterministically swap the candidate pathname immediately after its
    # descriptor was opened, before fstat/copy/SQLite. The root reader must keep
    # the pinned original object, never reopen through the replacement link.
    injection = f"""
original_open=os.open
def raced_open(path,flags,*args,**kwargs):
 fd=original_open(path,flags,*args,**kwargs)
 if path=={entry.name!r}:
  os.rename({str(entry)!r},{str(entry) + ".old"!r})
  os.symlink({str(target)!r},{str(entry)!r})
 return fd
os.open=raced_open
"""
    probe = SQLITE_PROBE.replace(
        "request=payload['assertion']", "request=payload['assertion']" + injection
    )
    result = local_sqlite_probe(
        tmp_path,
        "data/owned.db",
        {"table": "entries", "key": {"id": 7}, "values": {"title": "retained"}},
        probe=probe,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [{"title": "retained"}]
    assert "secret" not in result.stdout


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_private_sqlite_snapshot_includes_committed_uncheckpointed_wal(tmp_path):
    database = tmp_path / "owned.db"
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA wal_autocheckpoint=0")
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
        connection.execute("INSERT INTO entries VALUES(7,'retained-random')")
        connection.commit()
        assert database.with_name(database.name + "-wal").stat().st_size > 0
        result = local_sqlite_probe(
            tmp_path,
            database.name,
            {"table": "entries", "key": {"id": 7}, "values": {"title": "retained-random"}},
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == [{"title": "retained-random"}]
    finally:
        connection.close()


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
def test_nonempty_rollback_journal_is_rejected_without_recovery(tmp_path):
    database = tmp_path / "owned.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
        connection.execute("INSERT INTO entries VALUES(7,'retained-random')")
    journal = database.with_name(database.name + "-journal")
    # Even a zeroed PERSIST journal, not just a recognized hot journal, fails
    # closed. The reader never needs to interpret candidate super-journal data.
    journal.write_bytes(b"\0" * 512)
    result = local_sqlite_probe(
        tmp_path,
        database.name,
        {"table": "entries", "key": {"id": 7}, "values": {"title": "retained-random"}},
    )
    assert result.returncode != 0
    assert not result.stdout
    assert journal.read_bytes() == b"\0" * 512


def test_replayed_response_cannot_replace_an_obligations_saved_physical_selector():
    plan, _, _ = proposed()
    raw = plan.model_dump()
    raw["scenarios"][0]["after_restart"][0]["captures"] = {"entry": "$.id"}
    with pytest.raises(ValueError):
        CapabilityPlan.model_validate(raw)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux no-follow sandbox reader")
@pytest.mark.parametrize("replay", ["post-nonce", "get-nonce", "alias", "token", "retained"])
def test_actual_restart_order_rejects_reconstruction_before_any_challenge_replay(
    tmp_path, monkeypatch, replay
):
    """Run the production restart block with a reset-on-start/rebuild-on-request app.

    Aliases and encoded bearer tokens deliberately retransmit the challenge
    without a literal ${nonce} in the request. Rejecting POST or that spelling
    alone would not fix this counterexample.
    """
    from workbench.capability_verification import run_scenarios

    plan, _, _ = proposed()
    raw = plan.model_dump()
    step = {"status": 200, "equals": {"$.title": "持久化资料-${nonce}"}}
    if replay in {"post-nonce", "alias"}:
        step.update(
            method="POST",
            path="/rebuild",
            body={
                "id": "${entry}",
                "title": "${alias}" if replay == "alias" else "持久化资料-${nonce}",
            },
        )
    elif replay == "get-nonce":
        step.update(method="GET", path="/rebuild?id=${entry}&title=持久化资料-${nonce}")
    else:
        step.update(method="GET", path="/entries/${entry}", headers={"Authorization": "${owner}"})
    raw["scenarios"][0]["after_restart"] = [step]
    if replay in {"post-nonce", "alias"}:
        raw["scenarios"][0]["after_restart"].append(
            {
                "method": "GET",
                "path": "/entries/${entry}",
                "status": 200,
                "equals": {"$.title": "持久化资料-${nonce}"},
            }
        )
    plan = CapabilityPlan.model_validate(raw)
    scenarios = plan.scenarios[:1]
    title = "持久化资料-run-random"
    stored = {"id": 7, "title": title}
    saved = {
        "private_records": {
            "nonce": "run-random",
            "entry": 7,
            "alias": title,
            "owner": base64.urlsafe_b64encode(json.dumps(stored).encode()).decode(),
        }
    }
    database = tmp_path / plan.runtime.database_path
    database.parent.mkdir()
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE entries(id INTEGER,title TEXT)")
        connection.execute("INSERT INTO entries VALUES(?,?)", (7, title))
    events, clients, uploads = [], [], {}
    sandbox = SimpleNamespace(
        fs=SimpleNamespace(upload_file=lambda data, path, **kwargs: uploads.__setitem__(path, data))
    )

    def trusted_exec(sandbox, argv, timeout):
        if argv[:3] == ["/usr/bin/rm", "-f", "--"]:
            uploads.pop(argv[3], None)
            return SimpleNamespace(exit_code=0)
        assert argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]
        assert argv[4] == SQLITE_PROBE or "ApplicationPause" in argv[4]
        events.append("physical")
        payload = json.loads(uploads[argv[5]])
        result = local_sqlite_probe(tmp_path, payload["database_path"], payload["assertion"])
        return SimpleNamespace(exit_code=result.returncode, result=result.stdout)

    def candidate(request):
        events.append("replay")
        if replay in {"post-nonce", "alias"}:
            recovered = json.loads(request.content) if request.method == "POST" else None
        elif replay == "get-nonce":
            recovered = dict(request.url.params)
        else:
            recovered = json.loads(base64.urlsafe_b64decode(request.headers["Authorization"]))
        with sqlite3.connect(database) as connection:
            if replay != "retained" and recovered is not None:
                connection.execute(
                    "INSERT INTO entries VALUES(?,?)", (int(recovered["id"]), recovered["title"])
                )
            found = connection.execute("SELECT title FROM entries WHERE id=7").fetchone()
        return httpx.Response(
            200,
            stream=httpx.ByteStream(json.dumps({"title": found[0]}).encode()),
            headers={"Content-Type": "application/json"},
        )

    def start():
        events.append("start-health")
        if replay != "retained":
            with sqlite3.connect(database) as connection:
                connection.execute("DELETE FROM entries")
        client = httpx.Client(transport=httpx.MockTransport(candidate), base_url="http://fixture")
        clients.append(client)
        return client, "unused", "unused"

    monkeypatch.setattr("workbench.capability_obligations.control_exec", trusted_exec)
    monkeypatch.setattr(
        "workbench.capability_sandbox.restart_application_identity", lambda *a: None
    )
    initial = run_obligation_checks(sandbox, plan, scenarios, saved, 30, phase="initial")
    # The old request-before-witness ordering really does accept this same app.
    http, _, _ = start()
    with closing(http):
        run_scenarios(http, scenarios, saved=saved, after_restart=True)
        reconstructed = run_obligation_checks(sandbox, plan, scenarios, saved, 30, phase="restart")
    require_obligation_evidence(
        plan, {"obligation_checks": initial + reconstructed}, aggregate=True
    )

    tree = ast.parse((Path(__file__).parents[1] / "workbench/capability_sandbox.py").read_text())
    block = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "aggregate"
        and any(
            isinstance(child, ast.Assign) and ast.unparse(child.targets[0]) == "(http, _, _)"
            for child in node.body
        )
    )
    first = next(
        i
        for i, child in enumerate(block.body)
        if isinstance(child, ast.Assign) and ast.unparse(child.targets[0]) == "(http, _, _)"
    )
    last = next(
        i
        for i, child in enumerate(block.body)
        if isinstance(child, ast.Assign)
        and ast.unparse(child.targets[0]) == "receipt['database']['after_restart']"
    )
    receipt = {"checks": [], "obligation_checks": initial[:], "database": {}}
    scope = {
        "start": start,
        "closing": closing,
        "plan": plan,
        "scenarios": scenarios,
        "saved": saved,
        "sandbox": sandbox,
        "settings": SimpleNamespace(tool_timeout=30),
        "native": False,
        "trusted_oracle": None,
        "run_obligation_checks": run_obligation_checks,
        "run_scenarios": run_scenarios,
        "receipt": receipt,
        "counts": {"entries": 1},
        "database_counts": lambda *a: {"entries": 1},
        "CheckFailure": CheckFailure,
    }
    compiled = compile(ast.Module(block.body[first : last + 1], []), "actual-restart-order", "exec")
    events.clear()
    if replay == "retained":
        exec(compiled, scope)
        require_obligation_evidence(plan, receipt, aggregate=True)
        assert events == ["start-health", "physical", "replay"]
    else:
        with pytest.raises(CheckFailure, match="物理值"):
            exec(compiled, scope)
        assert events == ["start-health", "physical"]
        assert receipt["checks"] == []
        assert receipt["obligation_checks"] == initial
    assert all(client.is_closed for client in clients)


@pytest.mark.parametrize(
    "mutation",
    [
        "no-nonce",
        "unknown-scenario",
        "unknown-table",
        "fixture",
        "no-restart",
        "boolean-storage",
        "unsupported-postgres",
    ],
)
def test_atomic_contract_rejects_weak_or_unrelated_evidence_shapes(mutation):
    plan, _, _ = proposed()
    raw = plan.model_dump()
    if mutation == "no-nonce":
        raw["obligations"][0]["physical"]["values"] = {"title": "hardcoded"}
    elif mutation == "unknown-scenario":
        raw["obligations"][0]["scenario_id"] = "other"
    elif mutation == "unknown-table":
        raw["obligations"][0]["physical"]["table"] = "unrelated"
    elif mutation == "fixture":
        raw["scenarios"][0].update(evidence="external_fixture", external_service="email")
    elif mutation == "boolean-storage":
        raw["obligations"][0]["physical"]["key"] = {"id": True}
    elif mutation == "unsupported-postgres":
        raw["selection"] = Selection(template="fastapiadmin").model_dump()
    else:
        raw["scenarios"][0]["after_restart"] = []
    with pytest.raises(ValueError):
        CapabilityPlan.model_validate(raw)


def test_store_requires_operator_approval_for_exact_run_stage_and_data(settings, store):
    from workbench.store import Approval, Conflict

    project = store.create_project("review fixture", "review-project")
    run = store.create_run(project["id"], {"requirement": "authored"}, "review-run")["run_id"]
    data = {"source_digest": "a" * 64, "requires_explicit_review": True}
    gate = store.gate(run, "extension_design", 1, data, ["approve"])
    with pytest.raises(Conflict):
        store.explicit_approval(run, "extension_design", data, version=1)
    with store.tx() as session:
        session.add(Approval(gate_id=gate["gate_id"], decision=True, actor="delegated-ai"))
    with pytest.raises(Conflict):
        store.explicit_approval(run, "extension_design", data, version=1)
    with store.tx() as session:
        session.get(Approval, gate["gate_id"]).actor = "local-operator"
    assert (
        store.explicit_approval(run, "extension_design", data, version=1)["gate_id"]
        == gate["gate_id"]
    )
    with pytest.raises(Conflict):
        store.explicit_approval(run, "extension_design", data, version=2)
    for stage, revised in [
        ("extension_scope", data),
        ("extension_design", {**data, "source_digest": "b" * 64}),
    ]:
        with pytest.raises(Conflict):
            store.explicit_approval(run, stage, revised, version=1)


@pytest.mark.parametrize("phase", ["initial", "restart"])
def test_private_expected_values_never_enter_submitted_command_or_environment(monkeypatch, phase):
    import shlex

    from workbench.capability_isolation import CONTROL

    plan, _, _ = proposed()
    nonce, key = "secret-nonce-that-must-not-be-in-proc", "secret-physical-key"
    saved = {"private_records": {"nonce": nonce, "entry": key}}
    files, submissions = {}, []

    def upload(data, path, *, timeout):
        assert isinstance(data, bytes) and len(data) <= 65536
        assert path.startswith(CONTROL + "/private/obligation-")
        assert nonce not in path and key not in path
        files[path] = data

    def execute(command, *, env, timeout):
        submissions.append((command, env))
        assert nonce not in command and key not in command
        assert nonce not in json.dumps(env) and key not in json.dumps(env)
        argv = shlex.split(command)
        if "/usr/bin/rm" in argv:
            files.pop(argv[-1])
            return SimpleNamespace(exit_code=0, result="")
        request_path = next(value for value in argv if value in files)
        request = json.loads(files[request_path])
        assert request["assertion"]["key"] == {"id": key}
        assert nonce in request["assertion"]["values"]["title"]
        return SimpleNamespace(exit_code=0, result=json.dumps([request["assertion"]["values"]]))

    sandbox = SimpleNamespace(
        fs=SimpleNamespace(upload_file=upload), process=SimpleNamespace(exec=execute)
    )
    monkeypatch.setattr(
        "workbench.capability_sandbox.restart_application_identity", lambda *a: None
    )
    result = run_obligation_checks(sandbox, plan, plan.scenarios, saved, 30, phase=phase)
    assert result[0]["passed"] is True
    assert len(submissions) == 2 and files == {}


@pytest.mark.parametrize("failure", ["upload", "probe", "cleanup"])
def test_private_request_cleanup_is_required_even_after_transport_failure(monkeypatch, failure):
    import shlex

    plan, _, _ = proposed()
    files = {}

    def upload(data, path, **kwargs):
        files[path] = data
        if failure == "upload":
            raise RuntimeError("injected interrupted upload")

    def execute(command, **kwargs):
        argv = shlex.split(command)
        if "/usr/bin/rm" in argv:
            if failure == "cleanup":
                return SimpleNamespace(exit_code=1)
            files.pop(argv[-1], None)
            return SimpleNamespace(exit_code=0)
        if failure == "probe":
            raise RuntimeError("injected probe interruption")
        return SimpleNamespace(exit_code=0, result=json.dumps([{"title": "持久化资料-random"}]))

    sandbox = SimpleNamespace(
        fs=SimpleNamespace(upload_file=upload), process=SimpleNamespace(exec=execute)
    )
    expected = CheckFailure if failure == "cleanup" else RuntimeError
    with pytest.raises(expected):
        run_obligation_checks(
            sandbox,
            plan,
            plan.scenarios,
            {"private_records": {"entry": 7, "nonce": "random"}},
            30,
            phase="restart",
        )
    assert bool(files) is (failure == "cleanup")


@pytest.mark.skipif(sys.platform != "linux", reason="Linux root-private request validation")
@pytest.mark.parametrize(
    "mutation",
    ["public-directory", "symlink", "hardlink", "writable-file", "oversized", "wrong-owner"],
)
def test_private_request_rejects_unsafe_sources_before_observation(tmp_path, mutation):
    private = tmp_path / "controller-private"
    private.mkdir(mode=0o700)
    request = private / ("obligation-" + "b" * 32 + ".json")
    payload = json.dumps(
        {
            "database_path": "unopened.db",
            "assertion": {
                "table": "entries",
                "key": {"id": 7},
                "values": {"title": "private-challenge"},
            },
        }
    )
    request.write_text(payload)
    if mutation == "public-directory":
        private.chmod(0o755)
    elif mutation in {"symlink", "hardlink"}:
        outside = tmp_path / "outside.json"
        outside.write_text(payload)
        request.unlink()
        if mutation == "symlink":
            request.symlink_to(outside)
        else:
            os.link(outside, request)
    elif mutation == "writable-file":
        request.chmod(0o666)
    elif mutation == "oversized":
        request.write_bytes(b" " * 65537)
    uid = os.getuid() + (mutation == "wrong-owner")
    code = SQLITE_PROBE.replace(
        "pathlib.Path('/tmp/rnd-module-control/private')", f"pathlib.Path({str(private)!r})"
    ).replace("control_uid=0", f"control_uid={uid}")
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", code, str(request)],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode != 0
    assert not result.stdout
    assert "unopened.db" not in result.stderr, (
        "Reject the private source before touching the product"
    )
