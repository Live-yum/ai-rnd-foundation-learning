"""One smart authorization covers both bounded clarification and design repair."""

import pytest
from conftest import FixtureGateway, new_run, requirement

from workbench.domain import Plan, Requirement
from workbench.runtime import Runtime


@pytest.mark.parametrize("design_converges", [True, False])
def test_clarification_does_not_spend_design_repair_allowance(
    settings, store, plan, design_converges
):
    class StagedGateway(FixtureGateway):
        def complete(self, run_id, key, instruction, payload, schema):
            self.calls.append(key)
            if schema is Requirement:
                # Exercise both clarification repairs before any planning.
                if key in {"recommend:1", "recommend:2"}:
                    return requirement(["请决定一个尚未明确的细节"])
                assert key == "recommend:3"
                return requirement()
            assert schema is Plan
            assert payload["approved_requirement"]["data_scope"] == "per_user"
            if key != "plan:3":
                assert payload["resolution_feedback"]["stage"] == "design"
                assert payload["previous_plan"]["data_scope"] == "shared"
            if design_converges and key == "plan:4":
                return plan
            return plan.model_copy(update={"data_scope": "shared"})

    run_id = new_run(store)
    store.set_automation(run_id, True, "single-smart-authorization")
    gateway = StagedGateway(plan)
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
    state = store.get_run(run_id)
    assert gateway.calls[:4] == ["recommend:1", "recommend:2", "recommend:3", "plan:3"]
    if design_converges:
        assert gateway.calls[4:] == ["plan:4"]
        assert state["status"] == "READY", state
        assert state["result"]["cleanroom"]["passed"] is True
        assert (settings.data_dir / "runs" / run_id / "delivery.zip").is_file()
    else:
        assert gateway.calls[4:] == ["plan:4", "plan:5"]
        assert state["status"] == "BLOCKED", state
        assert state["pending"]["stage"] == "design"
        assert "本阶段两轮" in state["error"]
        assert not (settings.data_dir / "runs" / run_id / "delivery.zip").exists()
    assert len(store.messages(run_id)) == 1
