import json

from conftest import FixtureGateway, new_run, requirement

from workbench.flow import Workflow


def test_planner_receives_real_source_backed_template_context(settings, store, plan):
    gateway = FixtureGateway(plan)
    seen = []
    complete = gateway.complete

    def capture(run_id, key, instruction, payload, schema):
        seen.append(payload)
        return complete(run_id, key, instruction, payload, schema)

    gateway.complete = capture
    workflow = Workflow(settings, store, gateway)
    run_id = new_run(store)
    state = {
        "run_id": run_id,
        "template": "python-basic",
        "round": 1,
        "requirement": requirement().model_dump(),
    }
    result = workflow.plan(state)
    assert result["plan"] == plan.model_dump()
    context = seen[0]["template_source_context"]["product"]
    assert context["source_digest"] and context["map"]["text"]
    assert context["untrusted_source"]
    saved = settings.data_dir / "runs" / run_id / "design/template-context.json"
    assert json.loads(saved.read_text(encoding="utf-8"))["product"] == context
