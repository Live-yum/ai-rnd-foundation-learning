"""CI source handoff contracts only; no live container/native acceptance claims."""

import copy
import json
import os
import shutil

import pytest
from capability_dependency_fixtures import profile_record
from test_ci_native_capability_security import product as baseline_product  # noqa: F401

from scripts import ci_contest_capability as contest_ci
from scripts import ci_native_capability_source as handoff
from scripts import ci_native_tools as native_tools
from scripts.ci_native_capability_security import fixed_plan
from scripts.daytona_native_capability_profile import DESCRIPTORS, product_inputs
from scripts.extension_oracles import contest
from workbench import filesystem, native_lab, portable, tools
from workbench.capability_dependencies import require_dependency_descriptors
from workbench.capability_verification import CheckFailure
from workbench.domain import digest
from workbench.filesystem import atomic_text, manifest, write_json

posix_filesystem = pytest.mark.skipif(
    not hasattr(os, "O_NOFOLLOW"), reason="CI native source handoff requires POSIX no-follow FDs"
)
URL = "postgresql+psycopg://native:ci-only@127.0.0.1/native_codegen"


@pytest.fixture
def product(baseline_product):  # noqa: F811 - imported pytest fixture
    for name in DESCRIPTORS:
        atomic_text(baseline_product / name, "{}\n" if name.endswith(".json") else "# exact lock\n")
    atomic_text(baseline_product / "frontend/web/.env.production.example", "VITE_PUBLIC=example\n")
    atomic_text(baseline_product / "start.py", "# authored CI source, never run by these tests\n")
    return baseline_product


def accepted(archive="a" * 64):
    return {
        "generated_runtime_verified": True,
        "portable_restored": {
            "passed": True,
            "fresh_database": True,
            "standalone_launcher": True,
            "archive_round_trip": True,
            "source_archive_sha256": archive,
            "business_rules": {"passed": True},
        },
    }


def ready(product, tmp_path):
    state = handoff.SourceHandoff(tmp_path / "clean-ci", tmp_path / "source-ready.json")
    state.capture(product, manifest(product), "a" * 64)
    state.complete(accepted(), product)
    return state


@posix_filesystem
def test_exact_source_handoff_preserves_all_bytes_descriptors_and_public_examples(
    product, tmp_path
):
    original = manifest(product)
    state = ready(product, tmp_path)
    receipt = handoff.require_handoff(state.product, state.receipt)
    assert receipt["inventory"] == original == manifest(state.product) == manifest(product)
    assert receipt["source_identity"] == digest(original)
    inputs = product_inputs(state.product)
    assert inputs["source_identity"] == receipt["source_identity"]
    assert inputs["descriptors"] == receipt["descriptors"]
    assert receipt["source_archive_sha256"] == "a" * 64
    assert (state.product / "frontend/web/.env.production.example").exists()
    record = profile_record(state.product, "fastapiadmin")
    require_dependency_descriptors(state.product, fixed_plan(state.product), record)


@pytest.mark.parametrize(
    "relative", [".venv", "backend/.venv", "node_modules", "frontend/web/node_modules"]
)
@posix_filesystem
def test_dirty_candidate_stays_rejected_while_independent_clean_handoff_is_admitted(
    product, tmp_path, relative
):
    state = ready(product, tmp_path)
    (product / relative).mkdir(parents=True)
    record = profile_record(product, "fastapiadmin")
    with pytest.raises(CheckFailure, match="虚拟环境或依赖目录"):
        require_dependency_descriptors(product, fixed_plan(product), record)
    with pytest.raises(ValueError, match="extra directory"):
        handoff.copy_exact_source(product, tmp_path / "must-not-exist", state.inventory)
    assert not (tmp_path / "must-not-exist").exists()
    require_dependency_descriptors(state.product, fixed_plan(state.product), record)
    assert (product / relative).is_dir()


@pytest.mark.parametrize(
    "mutation",
    [
        "extra",
        "missing",
        "bytes",
        "empty-dir",
        "ignored-dir",
        "secret",
        "symlink",
        "hardlink",
        "fifo",
    ],
)
@posix_filesystem
def test_capture_rejects_every_uninventoried_physical_entry(product, tmp_path, mutation):
    inventory = manifest(product)
    path = product / "backend/app/__init__.py"
    if mutation == "extra":
        atomic_text(product / "backend/app/new_import.py", "extra")
    elif mutation == "missing":
        path.unlink()
    elif mutation == "bytes":
        path.write_text("changed")
    elif mutation == "empty-dir":
        (product / "empty").mkdir()
    elif mutation == "ignored-dir":
        atomic_text(product / "backend/logs/hidden.py", "extra")
    elif mutation == "secret":
        atomic_text(product / ".env", "DUMMY=not-a-credential")
    elif mutation == "symlink":
        path.unlink()
        path.symlink_to(product / "start.py")
    elif mutation == "hardlink":
        os.link(path, tmp_path / "hardlink")
    else:
        path.unlink()
        os.mkfifo(path)
    state = handoff.SourceHandoff(tmp_path / "clean", tmp_path / "receipt.json")
    with pytest.raises((ValueError, OSError)):
        state.capture(product, inventory, "a" * 64)
    assert json.loads(state.receipt.read_text())["passed"] is False
    assert not state.product.exists()


@pytest.mark.parametrize(
    "mutation", ["source-byte", "source-link", "source-directory-link", "destination-extra"]
)
@posix_filesystem
def test_copy_detects_mutations_between_preflight_and_copy(
    product, tmp_path, monkeypatch, mutation
):
    inventory = manifest(product)
    destination = tmp_path / "new"
    real = handoff.require_exact_source
    calls = 0

    def changing(root, expected):
        nonlocal calls
        result = real(root, expected)
        calls += 1
        if calls == 1:
            path = product / "backend/app/__init__.py"
            if mutation == "source-byte":
                path.write_text("changed after preflight")
            elif mutation == "source-link":
                path.unlink()
                path.symlink_to(tmp_path / "outside")
            elif mutation == "source-directory-link":
                old = product / "backend/app"
                old.rename(tmp_path / "original-app")
                old.symlink_to(tmp_path / "original-app", target_is_directory=True)
        if calls == 2 and mutation == "destination-extra":
            atomic_text(destination / "hidden.py", "extra")
        return result

    monkeypatch.setattr(handoff, "require_exact_source", changing)
    with pytest.raises((ValueError, OSError)):
        handoff.copy_exact_source(product, destination, inventory)


@posix_filesystem
def test_fd_read_rejects_link_swap_after_stat_without_reading_target(
    product, tmp_path, monkeypatch
):
    target = tmp_path / "outside"
    target.write_text("must not be copied")
    path = product / "backend/app/__init__.py"
    real = handoff.read_regular
    changed = False

    def swap(directory, name, expected=None):
        nonlocal changed
        if name == "__init__.py" and not changed:
            changed = True
            path.unlink()
            path.symlink_to(target)
        return real(directory, name, expected)

    inventory = manifest(product)
    monkeypatch.setattr(handoff, "read_regular", swap)
    with pytest.raises(OSError):
        handoff.require_exact_source(product, inventory)
    assert target.read_text() == "must not be copied"


@pytest.mark.parametrize(
    "mutation", ["source", "descriptor", "archive", "different-archive", "acceptance", "uncaptured"]
)
@posix_filesystem
def test_failed_completion_never_publishes_readiness(product, tmp_path, mutation):
    state = handoff.SourceHandoff(tmp_path / "clean", tmp_path / "receipt.json")
    if mutation != "uncaptured":
        state.capture(product, manifest(product), "a" * 64)
    report = accepted()
    if mutation == "source":
        atomic_text(product / "new.py", "changed source")
    elif mutation == "descriptor":
        (state.product / "backend/uv.lock").write_text("changed lock")
    elif mutation == "archive":
        report["portable_restored"]["source_archive_sha256"] = "not a hash"
    elif mutation == "different-archive":
        report["portable_restored"]["source_archive_sha256"] = "b" * 64
    elif mutation == "acceptance":
        report["portable_restored"]["passed"] = False
    with pytest.raises(ValueError):
        state.complete(report, product)
    assert json.loads(state.receipt.read_text())["passed"] is False


@posix_filesystem
def test_stale_receipt_invalidated_without_overwriting_or_deleting_existing_source(
    product, tmp_path
):
    state = ready(product, tmp_path)
    original = manifest(state.product)
    with pytest.raises(FileExistsError):
        handoff.SourceHandoff(state.product, state.receipt)
    assert manifest(state.product) == original
    assert json.loads(state.receipt.read_text())["passed"] is False
    with pytest.raises(ValueError):
        handoff.require_handoff(state.product, state.receipt)


@pytest.mark.parametrize(
    "mutation",
    [
        "run",
        "receipt-hash",
        "receipt-descriptor",
        "source",
        "dependencies",
        "receipt-fifo",
        "receipt-hardlink",
        "duplicate-key",
    ],
)
@posix_filesystem
def test_consumer_rejects_stale_or_tampered_readiness(product, tmp_path, monkeypatch, mutation):
    state = ready(product, tmp_path)
    value = json.loads(state.receipt.read_text())
    if mutation == "run":
        monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "changed")
    elif mutation.startswith("receipt-") and mutation in {"receipt-hash", "receipt-descriptor"}:
        if mutation == "receipt-hash":
            value["source_identity"] = "f" * 64
        else:
            value["descriptors"]["backend/uv.lock"] = "f" * 64
        write_json(state.receipt, value)
    elif mutation == "source":
        (state.product / "backend/app/__init__.py").write_text("tampered")
    elif mutation == "dependencies":
        (state.product / "backend/.venv").mkdir()
    elif mutation == "receipt-fifo":
        state.receipt.unlink()
        os.mkfifo(state.receipt)
    elif mutation == "receipt-hardlink":
        os.link(state.receipt, tmp_path / "linked-receipt")
    else:
        state.receipt.write_text('{"passed":false,' + state.receipt.read_text()[1:])
    with pytest.raises((ValueError, OSError)):
        handoff.require_handoff(state.product, state.receipt)


@pytest.fixture
def portable_runtime(monkeypatch):
    operations = []

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, statement):
            operations.append(statement.as_string())

    monkeypatch.setattr(portable.psycopg, "connect", lambda *args, **kwargs: Connection())
    return operations


@pytest.mark.parametrize(
    "failure", [None, "launch", "archive-drift", "original-drift", "roundtrip-extra"]
)
@posix_filesystem
def test_capture_precedes_independent_build_and_never_readies_failed_acceptance(
    product, tmp_path, monkeypatch, portable_runtime, failure
):
    inventory = manifest(product)
    state = handoff.SourceHandoff(tmp_path / "clean-ci", tmp_path / "ready.json")
    events, copies = [], []
    # The native generator's existing buildtree is intentionally dirty.
    atomic_text(product / "backend/.venv/leave-intact", "installed")
    atomic_text(product / "frontend/web/node_modules/leave-intact", "installed")

    def capture(clean, expected, archive_sha256):
        assert expected == inventory
        if failure != "roundtrip-extra":
            assert not (clean / "backend/.venv").exists()
            assert not (clean / "frontend/web/node_modules").exists()
        state.capture(clean, expected, archive_sha256)
        assert json.loads(state.receipt.read_text())["passed"] is False
        events.append("capture")

    def run(command, cwd, *args, **kwargs):
        copies.append(cwd)
        assert events == ["capture"]
        events.append("independent-build")
        atomic_text(cwd / "backend/.venv/created-by-launcher", "installed")
        atomic_text(cwd / "frontend/web/node_modules/created-by-launcher", "installed")
        if failure == "launch":
            raise RuntimeError("explicit independent launcher failure")
        if failure == "archive-drift":
            (cwd.parent / "delivery.zip").write_bytes(b"changed archive")
        if failure == "original-drift":
            (product / "backend/uv.lock").write_text("changed lock")
        write_json(
            cwd / ".deployment/reports/portable-start.json",
            {"passed": True, "frontend_started": True, "restart": True},
        )
        return {"log": "mocked launcher evidence only"}

    monkeypatch.setattr(tools, "run_command", run)
    if failure == "roundtrip-extra":
        original_unpack = filesystem.unpack

        def extra(archive, destination, **kwargs):
            result = original_unpack(archive, destination, **kwargs)
            (destination / "backend/.venv").mkdir()
            return result

        monkeypatch.setattr(filesystem, "unpack", extra)
    if failure is None:
        result = portable.verify_native_delivery(
            product, URL, tmp_path / "reports", template="fastapiadmin", source_handoff=capture
        )
        assert events == ["capture", "independent-build"]
        report = accepted()
        report["portable_restored"].update(result)
        state.complete(report, product)
        handoff.require_handoff(state.product, state.receipt)
        assert manifest(state.product) == inventory
        assert (product / "backend/.venv/leave-intact").exists()
    else:
        with pytest.raises((ValueError, RuntimeError)):
            portable.verify_native_delivery(
                product, URL, tmp_path / "reports", template="fastapiadmin", source_handoff=capture
            )
        assert json.loads(state.receipt.read_text())["passed"] is False
    assert len(portable_runtime) == 2
    assert portable_runtime[0].startswith('CREATE DATABASE "restore_')
    assert portable_runtime[1].startswith('DROP DATABASE "restore_')
    assert all(not path.exists() for path in copies)


@pytest.mark.parametrize(
    "failure", [None, "before-capture", "after-capture", "final-assertion", "outcome-write"]
)
def test_native_tools_finalizes_only_after_all_acceptance_and_outcome_write(
    product, tmp_path, monkeypatch, failure
):
    root = tmp_path / "ci"
    reports = root / "reports/native-tools"
    destination = root / "clean-ci"
    receipt = reports / "capability-source.json"

    # Cross-platform CLI ordering test. POSIX physical safety is tested above;
    # this fixture copies only its known synthetic inputs without native tools.
    def fixture_copy(source, destination, inventory):
        assert manifest(source) == inventory
        shutil.copytree(source, destination)
        return destination

    def fixture_inventory(source, inventory):
        assert manifest(source) == inventory
        return inventory

    monkeypatch.setattr(handoff, "copy_exact_source", fixture_copy)
    monkeypatch.setattr(handoff, "require_exact_source", fixture_inventory)
    write_json(receipt, {"passed": True, "stale": True})
    monkeypatch.setattr(native_tools, "ROOT", root)
    monkeypatch.setattr(
        native_tools, "prepare_sources", lambda *a: [{"slot": "fastapiadmin", "path": product}]
    )
    monkeypatch.setattr(native_tools, "native_rule_customizer", lambda *a: lambda *args: None)
    monkeypatch.setattr(
        native_lab, "generated_permissions", lambda *a: {"attempt_id": "interrupted"}
    )
    monkeypatch.setenv("NATIVE_TEST_DATABASE_URL", URL)
    monkeypatch.setattr(
        "sys.argv",
        [
            "ci-native-tools",
            "fastapiadmin",
            "--output",
            str(product),
            "--capability-source",
            str(destination),
        ],
    )
    calls = 0

    def run(*args, **kwargs):
        nonlocal calls
        calls += 1
        assert json.loads(receipt.read_text())["passed"] is False
        if calls == 1:
            write_json(reports / "recovery.json", {"resumable": True, "targets": ["device"]})
            kwargs["customization"]()
        if calls == 2:
            native_lab.generated_permissions()
        if failure == "before-capture":
            raise RuntimeError("before capture")
        kwargs["source_handoff"](product, manifest(product), "a" * 64)
        if failure == "after-capture":
            raise RuntimeError("after capture")
        write_json(reports / "generated/permissions.json", {"attempt_id": "final"})
        write_json(
            reports / "native-coding.json",
            {"passed": True, "repaired": failure != "final-assertion", "attempts": 2},
        )
        write_json(reports / "coding-0.json", {"rolled_back": True, "verified": False})
        return accepted()

    monkeypatch.setattr(native_tools, "run_acceptance", run)
    if failure == "outcome-write":

        def write(path, value):
            if path.name == "toolchain-acceptance.json":
                raise OSError("explicit outcome write failure")
            write_json(path, value)

        monkeypatch.setattr(native_tools, "write_json", write)
    if failure is None:
        native_tools.main()
        handoff.validate_receipt(json.loads(receipt.read_text()), destination)
        assert json.loads((reports / "toolchain-acceptance.json").read_text())["passed"] is True
    else:
        with pytest.raises((RuntimeError, AssertionError, OSError)):
            native_tools.main()
        assert json.loads(receipt.read_text())["passed"] is False
    assert manifest(product)


@posix_filesystem
def test_contest_adds_only_authored_inventory_and_keeps_registered_baseline_exact(
    product, tmp_path
):
    state = ready(product, tmp_path)
    baseline = handoff.require_handoff(state.product, state.receipt)
    target = tmp_path / "contest"
    handoff.copy_exact_source(state.product, target, baseline["inventory"])
    augmented = contest_ci.install_authored_fixture(target)
    assert set(augmented) - set(baseline["inventory"]) == {
        "backend/app/plugin/module_rnd/__init__.py",
        *("backend/app/plugin/module_rnd/contest/" + name for name in manifest(contest_ci.FIXTURE)),
    }
    assert handoff.descriptors(augmented) == baseline["descriptors"]
    assert manifest(state.product) == baseline["inventory"]
    assert (target / "frontend/web/.env.production.example").exists()
    require_dependency_descriptors(
        target, fixed_plan(target), profile_record(state.product, "fastapiadmin")
    )


@pytest.mark.parametrize(
    "mutation", [None, "wrong-profile-source", "dirty-baseline", "proof-drift"]
)
@posix_filesystem
def test_contest_consumer_uses_same_ready_profile_source_without_filtering(
    product, tmp_path, monkeypatch, mutation
):
    state = ready(product, tmp_path)
    record = profile_record(state.product, "fastapiadmin")
    record["inputs"] = product_inputs(state.product)
    if mutation == "wrong-profile-source":
        record["inputs"]["product"] = str(product)
    elif mutation == "dirty-baseline":
        (state.product / "backend/.venv").mkdir()
    events = []
    monkeypatch.setattr(contest_ci, "ROOT", tmp_path)
    monkeypatch.setattr(contest_ci, "install_loopback_guard", lambda: None)
    monkeypatch.setattr(
        contest_ci,
        "capability_execution_prerequisites",
        lambda *a: (tmp_path, copy.deepcopy(record)),
    )
    monkeypatch.setattr(contest_ci, "require_native_profile", lambda *a: record)
    monkeypatch.setattr(contest_ci, "client_for", lambda *a: events.append("client") or object())
    monkeypatch.setattr(contest_ci, "close_client", lambda *a: events.append("close"))
    monkeypatch.setattr(contest_ci, "security_probe_for_profile", lambda *a: None)
    monkeypatch.setattr(
        "sys.argv",
        ["contest", "--product", str(state.product), "--source-receipt", str(state.receipt)],
    )

    def verify(root, plan, *args, **kwargs):
        events.append("verify")
        inventory = manifest(root)
        handoff.require_exact_source(root, inventory)
        require_dependency_descriptors(root, plan, record)
        assert handoff.descriptors(inventory) == record["inputs"]["descriptors"]
        return {
            "passed": True,
            "cleanup": "deleted",
            "source_digest": "f" * 64 if mutation == "proof-drift" else digest(inventory),
            "business_oracle": {
                "protocol": contest.CONTRACT_VERSION,
                "full_request_complete": False,
                "remaining_obligations": list(contest.REMAINING),
                "fresh_replay": True,
                "same_cluster": True,
                "distinct_database_oid": True,
                "witnesses": dict.fromkeys(contest.SEMANTICS, True),
            },
        }

    monkeypatch.setattr(contest_ci, "_verify", verify)
    if mutation is None:
        contest_ci.main()
        assert events == ["client", "verify", "close"]
        assert (
            json.loads((tmp_path / "reports/contest-capability.json").read_text())["passed"] is True
        )
    else:
        with pytest.raises(ValueError):
            contest_ci.main()
        assert (
            json.loads((tmp_path / "reports/contest-capability.json").read_text())["passed"]
            is False
        )
        if mutation in {"wrong-profile-source", "dirty-baseline"}:
            assert events == []


def test_workflow_binds_all_consumers_to_one_clean_product_and_receipt():
    workflow = (handoff.ROOT / ".github/workflows/native-capability-profile.yml").read_text()
    assert "ci_native_tools fastapiadmin --capability-source .native/capability-source" in workflow
    for command in (
        "ci_native_capability_source",
        "daytona_native_capability_profile prepare",
        "ci_native_capability_security",
        "ci_contest_capability",
    ):
        assert command + " --product .native/capability-source" in workflow
    assert workflow.count("--source-receipt reports/native-tools/capability-source.json") == 2
    assert "prepare --product .native/tool-product" not in workflow


@pytest.mark.parametrize(
    "inventory",
    [
        {},
        [],
        {"../escape": "a" * 64},
        {"x": "bad"},
        {"node_modules/a": "a" * 64},
        {"backend/.venv/a": "a" * 64},
        {".env": "a" * 64},
        {"a.pyc": "a" * 64},
        {"a\\x": "a" * 64},
        {"a\x00x": "a" * 64},
        {"a\nx": "a" * 64},
        {"a": "a" * 64, "a/x": "b" * 64},
        {"A": "a" * 64, "a/x": "b" * 64},
        {"A/x": "a" * 64, "a/y": "b" * 64},
        {"A": "a" * 64, "a": "b" * 64},
        {"x" * 4097: "a" * 64},
    ],
)
def test_inventory_schema_rejects_non_source_and_ambiguous_paths_on_all_platforms(inventory):
    with pytest.raises(ValueError):
        handoff.validate_inventory(inventory)


@pytest.mark.parametrize(
    "mutation",
    [None, "schema", "passed", "path", "run", "identity", "descriptor", "archive", "extra"],
)
def test_receipt_schema_and_binding_are_portable(product, monkeypatch, mutation):
    inventory = manifest(product)
    value = {
        "schema": 1,
        "passed": True,
        "provenance": handoff.PROVENANCE,
        "product": str(product),
        "source_identity": digest(inventory),
        "source_archive_sha256": "a" * 64,
        "inventory": inventory,
        "descriptors": handoff.descriptors(inventory),
        "run": handoff.run_identity(),
    }
    if mutation == "schema":
        value["schema"] = True
    elif mutation == "passed":
        value["passed"] = 1
    elif mutation == "path":
        value["product"] += "-different"
    elif mutation == "run":
        monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "a-different-attempt")
    elif mutation == "identity":
        value["source_identity"] = "b" * 64
    elif mutation == "descriptor":
        value["descriptors"]["backend/uv.lock"] = "b" * 64
    elif mutation == "archive":
        value["source_archive_sha256"] = "a" * 63
    elif mutation == "extra":
        value["untrusted"] = True
    if mutation is None:
        assert handoff.validate_receipt(value, product) == value
    else:
        with pytest.raises(ValueError):
            handoff.validate_receipt(value, product)


def test_unsupported_platform_fails_closed_before_opening_source(tmp_path, monkeypatch):
    monkeypatch.delattr(os, "O_NOFOLLOW", raising=False)
    with pytest.raises(ValueError, match="no-follow"):
        with handoff.directory_fd(tmp_path):
            pytest.fail("unsupported platform opened source")


def test_parent_traversal_roots_fail_before_any_write(product, tmp_path):
    inventory = manifest(product)
    path = product / "unused/../new-source"
    with pytest.raises(ValueError, match="parent traversal"):
        handoff.copy_exact_source(product, path, inventory)
    assert manifest(product) == inventory
    assert not (product / "unused").exists()
    assert not (product / "new-source").exists()
    receipt = tmp_path / "unchanged.json"
    receipt.write_text("existing receipt")
    with pytest.raises(ValueError, match="parent traversal"):
        handoff.SourceHandoff(path, receipt)
    assert receipt.read_text() == "existing receipt"


@pytest.mark.parametrize("relation", ["same", "inside-buildtree", "contains-buildtree"])
def test_cli_rejects_overlapping_original_and_handoff_before_any_writes(
    product, tmp_path, monkeypatch, relation
):
    destination = {
        "same": product,
        "inside-buildtree": product / "new-handoff",
        "contains-buildtree": product.parent,
    }[relation]
    inventory = manifest(product)
    root = tmp_path / "controller"
    monkeypatch.setattr(native_tools, "ROOT", root)
    monkeypatch.setattr(
        "sys.argv",
        [
            "ci-native-tools",
            "fastapiadmin",
            "--output",
            str(product),
            "--capability-source",
            str(destination),
        ],
    )
    monkeypatch.setattr(
        native_tools,
        "prepare_sources",
        lambda *a: pytest.fail("native build started before output preflight"),
    )
    with pytest.raises(ValueError, match="independent"):
        native_tools.main()
    assert manifest(product) == inventory
    assert not root.exists()
    assert not (product / "new-handoff").exists()
