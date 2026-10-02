"""Explicit model fixtures test orchestration, with real generated HTTP and browser gates."""

import uuid

from workbench.domain import ModelReview, Plan, Requirement
from workbench.runtime import Runtime
from workbench.settings import ROOT


def test_customer_smart_workflow_reaches_independent_delivery(settings, store):
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    prose = (ROOT / "examples/requirements/customer-service.md").read_text(encoding="utf-8")
    requirement = Requirement(
        summary=prose,
        users=["管理人员", "服务人员", "普通员工"],
        data_scope="shared",
        features=["客户、服务请求与协作任务，角色权限、提醒和统计"],
        acceptance=plan.acceptance,
    )

    class Fixture:
        calls = []

        def complete(self, run, key, instruction, payload, schema):
            self.calls.append(key)
            if schema is Requirement:
                return requirement
            if schema is Plan:
                return plan
            if schema is ModelReview:
                return ModelReview(
                    summary="Explicit fixture review", observations=[], uncovered_requirements=[]
                )
            raise AssertionError(schema)

    project = store.create_project("客服流程验收", str(uuid.uuid4()))
    run = store.create_run(
        project["id"],
        {"requirement": prose, "template": "python-basic", "intelligent": True},
        str(uuid.uuid4()),
    )["run_id"]
    with Runtime(settings, store, Fixture()) as worker:
        worker.tick()
    state = store.get_run(run)
    assert state["status"] == "READY", state
    assert state["auto_mode"] is True
    assert state["result"]["cleanroom"]["business"]["passed"] is True
    assert state["result"]["cleanroom"]["browser"]["real_browser"] is True
