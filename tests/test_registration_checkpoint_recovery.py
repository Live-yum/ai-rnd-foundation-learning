"""Reported polluted legacy requirement survives restart and real source correction."""

import json
import uuid

from conftest import decision

from workbench.domain import Requirement
from workbench.flow import Workflow
from workbench.requirement_intent import AUTHENTICATED_SCOPE
from workbench.runtime import Runtime

ORIGINAL = "大学生计算机设计大赛报名网站"


def polluted_requirement():
    return Requirement.model_validate(
        {
            "summary": "大学生计算机设计大赛管理网站",
            "users": [
                "赛事管理人员",
                "团队队长（提交报名信息）",
                "团队队长（仅作为联系人）",
                "团队队长（仅联系人）",
            ],
            "data_scope": "shared",
            "facts": {},
            "features": [
                "提供" + ORIGINAL,
                "支持报名记录的增删改查",
                "对报名记录进行新增、查询、修改、删除",
                "仅管理员创建报名记录",
            ],
            "acceptance": ["支持报名记录的增删改查", "对报名记录进行新增、查询、修改、删除"],
            "assumptions": ["默认管理员创建报名记录，队长仅是联系人"],
            "unsupported": [
                "原始目标包含参赛报名，当前模板仅FastapiAdmin管理端，不支持公开页面公开提交"
            ],
            "field_requirements": [
                {"entity": "registration", "field": name, "kind": "text", "required": True}
                for name in [
                    "team_name",
                    "category",
                    "captain_name",
                    "captain_contact",
                    "member_info",
                ]
            ],
            "entity_requirements": [
                {
                    "entity": "registration",
                    "fields": [
                        "team_name",
                        "category",
                        "captain_name",
                        "captain_contact",
                        "member_info",
                    ],
                    "additional_fields": False,
                }
            ],
        }
    )


def test_real_legacy_polluted_clarification_repairs_same_run_and_keeps_full_audit(
    settings, store, monkeypatch
):
    old = polluted_requirement().gate_dump()
    old_entry = {"round": 1, "before": {}, "after": old, "source_count": 1}
    project = store.create_project("legacy signup", str(uuid.uuid4()))
    run = store.create_run(
        project["id"], {"template": "fastapiadmin", "requirement": ORIGINAL}, str(uuid.uuid4())
    )["run_id"]

    def legacy_analyse(self, state):
        return {"requirement": old, "requirement_ledger": [old_entry]}

    class NoModel:
        def complete(self, *args):
            raise AssertionError("Known scope conflict must not spend model calls")

    with monkeypatch.context() as patch:
        patch.setattr(Workflow, "analyse", legacy_analyse)
        with Runtime(settings, store, NoModel()) as worker:
            assert worker.tick()
    old_gate = store.get_run(run)["pending"]
    store.set_automation(run, True, "recover-same-run")
    with Runtime(settings, store, NoModel()) as worker:
        assert worker.tick()
        blocked = store.get_run(run)
        assert blocked["status"] == "BLOCKED", blocked
        gate = blocked["pending"]
        assert gate["gate_id"] != old_gate["gate_id"]
        value = gate["data"]["requirement"]
        assert value["summary"] == ORIGINAL
        assert value["facts"] == {}
        assert value["field_requirements"] == old["field_requirements"]
        assert value["entity_requirements"] == old["entity_requirements"]
        assert value["unsupported"] == []  # Never infer anonymous from the old model claim.
        assert len(value["features"]) == 3
        assert len(value["acceptance"]) == 1
        assert len(value["users"]) == 3

    class Grounded:
        calls = 0

        def complete(self, rid, key, instruction, payload, schema):
            self.calls += 1
            assert rid == run and schema is Requirement
            assert payload["original_request"] == ORIGINAL
            assert payload["fresh_user_corrections"] == [AUTHENTICATED_SCOPE]
            return Requirement(
                summary="管理员维护报名记录",  # Headline drift is restored deterministically.
                users=["参赛者", "赛事管理人员"],
                data_scope="shared",
                features=[AUTHENTICATED_SCOPE],
                acceptance=["参赛者可自行提交报名，仅管理本人记录"],
            )

    gateway = Grounded()
    store.set_automation(run, False, "manual-review")
    decision(store, run, "answer", AUTHENTICATED_SCOPE)
    with Runtime(settings, store, gateway) as worker:
        assert worker.tick()
        state = worker.graph.get_state({"configurable": {"thread_id": run}}).values
    result = store.get_run(run)
    assert result["status"] == "WAITING_REQUIREMENTS", result
    current = result["pending"]["data"]["requirement"]
    assert current["summary"] == ORIGINAL
    assert all("仅联系人" not in user and "仅作为联系人" not in user for user in current["users"])
    assert "仅管理员创建报名记录" not in current["features"]
    assert current["field_requirements"] == old["field_requirements"]
    assert current["entity_requirements"] == old["entity_requirements"]
    assert state["requirement_ledger"][0] == old_entry
    assert state["requirement_ledger"][-1]["scope_changes"]
    assert gateway.calls == 1
    on_disk = json.loads(
        (settings.data_dir / "runs" / run / "requirement-ledger.json").read_text(encoding="utf-8")
    )
    assert on_disk == state["requirement_ledger"]
    assert store.messages(run) == [
        {"role": "user", "content": ORIGINAL},
        {"role": "user", "content": AUTHENTICATED_SCOPE},
    ]
