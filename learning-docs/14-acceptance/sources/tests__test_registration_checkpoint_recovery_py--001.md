# tests/test_registration_checkpoint_recovery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.flow`、`workbench.requirement_intent`、`workbench.runtime`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `polluted_requirement`（L16–L63）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Requirement.model_validate`。 返回路径：L17的`Requirement.model_validate( { "summary": "大学生计算机设计大赛管理网站", "users": [ "赛事管理人员", "团队队长（提交报名…`。
- `test_real_legacy_polluted_clarification_repairs_same_run_and_keeps_full_audit`（L66–L145）：接收`settings`、`store`、`monkeypatch`。 控制顺序：L86断言`worker.tick()`；L90断言`worker.tick()`；L92断言`blocked["status"] == "BLOCKED"`；L94断言`gate["gate_id"] != old_gate["gate_id"]`；L96断言`value["summary"] == ORIGINAL`；L97断言`value["facts"] == {}`；L98断言`value["field_requirements"] == old["field_requirements"]`；L99断言`value["entity_requirements"] == old["entity_requirements"]`。后续分支沿下方源码相同行号继续阅读。 调用`polluted_requirement().gate_dump`、`polluted_requirement`、`store.create_project`、`str`、`uuid.uuid4`、`store.create_run`、`monkeypatch.context`、`patch.setattr`、`Runtime`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_legacy_polluted_clarification_repairs_same_run_and_keeps_full_audit.legacy_analyse`（L76–L77）：接收`state`。 返回路径：L77的`{"requirement": old, "requirement_ledger": [old_entry]}`。
- `test_real_legacy_polluted_clarification_repairs_same_run_and_keeps_full_audit.NoModel`（L79–L81）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_legacy_polluted_clarification_repairs_same_run_and_keeps_full_audit.NoModel.complete`（L80–L81）：接收`*args`。 控制顺序：L81抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_legacy_polluted_clarification_repairs_same_run_and_keeps_full_audit.Grounded`（L105–L119）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_legacy_polluted_clarification_repairs_same_run_and_keeps_full_audit.Grounded.complete`（L108–L119）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L110断言`rid == run and schema is Requirement`；L111断言`payload["original_request"] == ORIGINAL`；L112断言`payload["fresh_user_corrections"] == [AUTHENTICATED_SCOPE]`。 调用`Requirement`。 返回路径：L113的`Requirement( summary="管理员维护报名记录", # Headline drift is restored deterministically. users=["…`。

</details>

**创建路径：** `tests/test_registration_checkpoint_recovery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L145。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6026`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_registration_checkpoint_recovery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5625fe3066caf82eeddeae3483a41e7dcb24e1de963f9c81edd2a7d1e1d485c4"} -->
````python
# tests/test_registration_checkpoint_recovery.py
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
````
