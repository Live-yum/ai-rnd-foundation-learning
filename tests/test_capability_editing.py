"""Candidate editing must not mutate baselines or execute product code."""

import pytest

from workbench.capability_contracts import CapabilityEdits, CapabilityTask
from workbench.capability_editing import apply_candidate
from workbench.filesystem import sha


def task(files):
    return CapabilityTask(
        id="team",
        title="Team rules",
        requirements=["source-0-0"],
        files=files,
        contract="Cross-record bounded team module",
        scenarios=["teams"],
    )


def edits(path, before=None, content="raise RuntimeError('never import generated code')\n"):
    return CapabilityEdits(
        explanation="test fixture",
        files=[{"path": path, "before_sha256": before, "content": content}],
    )


def test_candidate_is_separate_and_replay_is_hash_bound(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("original\n")
    before = sha(product / "app.py")
    value = edits("app.py", before)
    candidate = tmp_path / "candidate"
    receipt = apply_candidate(
        product, value, task(["app.py"]), {"template": "python-basic"}, candidate
    )
    assert receipt["host_execution"] is False
    assert (product / "app.py").read_text() == "original\n"
    assert "never import" in (candidate / "app.py").read_text()
    assert (
        apply_candidate(product, value, task(["app.py"]), {"template": "python-basic"}, candidate)
        == receipt
    )
    (candidate / "app.py").write_text("tampered")
    with pytest.raises(ValueError, match="身份"):
        apply_candidate(product, value, task(["app.py"]), {"template": "python-basic"}, candidate)


@pytest.mark.parametrize(
    "path",
    [
        "pyproject.toml",
        "verify.py",
        "workbench/flow.py",
        "deployment/run.py",
        "start.py",
        "package.json",
    ],
)
def test_protected_paths_cannot_be_approved_by_model(tmp_path, path):
    product = tmp_path / "product"
    product.mkdir()
    with pytest.raises(ValueError):
        apply_candidate(
            product, edits(path), task([path]), {"template": "python-basic"}, tmp_path / "candidate"
        )
    assert not (tmp_path / "candidate").exists()


def test_stale_and_extra_edits_fail_before_copy(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("original")
    with pytest.raises(ValueError, match="前像"):
        apply_candidate(
            product,
            edits("app.py"),
            task(["app.py"]),
            {"template": "python-basic"},
            tmp_path / "candidate",
        )
    with pytest.raises(ValueError, match="全部文件"):
        apply_candidate(
            product,
            edits("extra.py"),
            task(["app.py"]),
            {"template": "python-basic"},
            tmp_path / "candidate",
        )


@pytest.mark.parametrize(
    "names,missing,extra,duplicates",
    [
        (["app.py"], 1, 0, 0),
        (["app.py", "app.py"], 1, 0, 1),
        (["app.py", "sla.py", "private.py"], 0, 1, 0),
        (["app.py", "App.py", "sla.py"], 0, 1, 1),
    ],
)
def test_invalid_agent_file_sets_are_classified_without_mutation_or_private_paths(
    tmp_path, names, missing, extra, duplicates
):
    import json

    from scripts.ci_live_modules import failure_diagnostic
    from workbench.coding.candidates import CandidateFileSetError
    from workbench.coding.ports import AgentTurn

    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("# private unchanged source\n")
    action = AgentTurn.model_validate(
        {
            "operation": "edit",
            "edits": {
                "explanation": "private model explanation",
                "files": [
                    {"path": name, "content": "# private generated source"} for name in names
                ],
            },
        }
    )
    assert [
        edit.path for edit in action.edits.files
    ] == names  # Adapter preserves order/duplicates.
    destination = tmp_path / "candidate"
    with pytest.raises(CandidateFileSetError) as captured:
        apply_candidate(
            product,
            action.edits,
            task(["app.py", "sla.py"]),
            {"template": "python-basic"},
            destination,
        )
    diagnostic = failure_diagnostic(captured.value)
    assert diagnostic["candidate_files"] == {
        "approved_count": 2,
        "returned_count": len(names),
        "missing_count": missing,
        "unapproved_count": extra,
        "casefold_duplicate_count": duplicates,
    }
    assert "private" not in json.dumps(diagnostic)
    assert not destination.exists()
    assert (product / "app.py").read_text() == "# private unchanged source\n"


def test_agent_must_explicitly_preserve_unchanged_approved_files(tmp_path):
    from workbench.coding.ports import AgentTurn

    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("# preserved\n")
    action = AgentTurn.model_validate(
        {
            "operation": "edit",
            "edits": {
                "explanation": "authored full-set action",
                "files": [
                    {
                        "path": "app.py",
                        "content": "# preserved\n",
                        "before_sha256": sha(product / "app.py"),
                    },
                    {"path": "sla.py", "content": "# new business file\n", "before_sha256": None},
                ],
            },
        }
    )
    candidate = tmp_path / "candidate"
    apply_candidate(
        product, action.edits, task(["app.py", "sla.py"]), {"template": "python-basic"}, candidate
    )
    assert (candidate / "app.py").read_bytes() == (product / "app.py").read_bytes()
    assert (candidate / "sla.py").read_text() == "# new business file\n"


@pytest.mark.parametrize(
    "names",
    [
        ["app.py"],
        ["app.py", "app.py"],
        ["app.py", "sla.py", "private.py"],
        ["app.py", "App.py", "sla.py"],
    ],
)
@pytest.mark.parametrize("repair", [True, False])
def test_task_bound_gateway_repairs_invalid_sets_only_within_existing_two_attempts(
    store, names, repair
):
    import json

    import httpx
    from conftest import new_run
    from test_llm import gateway

    from scripts.ci_live_modules import acceptance_design
    from workbench.coding.ports import approved_turn_schema
    from workbench.llm import ModelFailure

    calls = []
    approved = acceptance_design().implementation.tasks[0]
    store.settings.max_model_calls = 2

    def respond(request):
        calls.append(json.loads(request.content))
        paths = approved.allowed_paths if repair and len(calls) == 2 else names
        turn = {
            "operation": "edit",
            "edits": {
                "explanation": "offline",
                "files": [{"path": name, "content": "# fixture\n"} for name in paths],
            },
        }
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": json.dumps(turn),
                        }
                    }
                ]
            },
        )

    model = gateway(store, respond)
    run = new_run(store)
    schema = approved_turn_schema(approved)
    if repair:
        result = model.complete(
            run, "coding:approved-edit", "return full approved files", {}, schema
        )
        assert [edit.path for edit in result.edits.files] == approved.allowed_paths
    else:
        with pytest.raises(ModelFailure):
            model.complete(run, "coding:approved-edit", "return full approved files", {}, schema)
    assert len(calls) == store.get_run(run)["model_calls"] == 2
    repair_message = calls[1]["messages"][-1]["content"]
    assert "every approved" in repair_message
    assert "private.py" not in repair_message and "# fixture" not in repair_message
