# tests/test_capability_orchestration.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_fixture`、`workbench.capability_contracts`、`workbench.errors`、`workbench.filesystem`、`workbench.orchestration`、`workbench.runtime`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Gateway`（L15–L39）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Gateway.__init__`（L16–L19）：接收`permission_changes`。 调用`CapabilityFixture`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Gateway.complete`（L21–L39）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L23按`schema is ExtensionDesign`分支；L29断言`schema is CapabilityEdits`。 调用`self.calls.append`、`ExtensionDesign`、`fixture_baseline`、`make_plan`、`self.coder.complete`、`payload["context"].items`。 返回路径：L24的`ExtensionDesign( baseline=fixture_baseline(), implementation=make_plan(payload), permissio…`；L30的`self.coder.complete( run_id, key, instruction, { **payload, "file_manifest": {name: row["s…`。
- `create`（L42–L46）：接收`store`、`request`。 调用`store.create_project`、`store.create_run`。 返回路径：L44的`store.create_run(project["id"], {"requirement": request, "intelligent": True}, "run")[ "ru…`。
- `test_explicit_extension_reaches_code_and_preserves_candidate_on_missing_sandbox`（L49–L77）：接收`settings`、`store`、`monkeypatch`。 控制顺序：L66断言`first["status"] == "BLOCKED"`；L67断言`first["pending"] is None`；L68断言`[schema for _, schema in gateway.calls] == ["ExtensionDesign", "CapabilityEdits"]`；L70断言`(candidate / "app.py").read_text() == APP`；L74断言`len(gateway.calls) == 2`；L75断言`calls == [str(candidate), str(candidate)]`；L76断言`manifest(candidate) == before`；L77断言`not list((settings.data_dir / "runs" / run).glob("*delivery.zip"))`。 调用`monkeypatch.setattr`、`create`、`Gateway`、`Runtime`、`runtime.tick`、`store.get_run`、`Path`、`(candidate / "app.py").read_text`、`manifest`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_extension_reaches_code_and_preserves_candidate_on_missing_sandbox.unavailable`（L56–L58）：接收`product`、`*args`、`**kwargs`。 控制顺序：L58抛异常，停止当前正常路径。 调用`calls.append`、`str`、`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permission_changes_cannot_be_auto_approved_or_recommended`（L80–L94）：接收`settings`、`store`。 控制顺序：L88断言`saved["status"] == "WAITING_EXTENSION_DESIGN"`；L89断言`len(gateway.calls) == 1`。 调用`create`、`Gateway`、`Runtime`、`runtime.tick`、`store.get_run`、`len`、`pytest.raises`、`store.submit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_atomic_completeness_proposal_always_stops_for_exact_human_review`（L97–L139）：接收`settings`、`store`。 控制顺序：L130断言`saved["status"] == "WAITING_EXTENSION_DESIGN"`；L131断言`len(gateway.calls) == 1`；L133断言`gate["data"]["atomic_review"]["complete_source_ids"]`。 调用`create`、`AtomicGateway`、`Runtime`、`runtime.tick`、`store.get_run`、`len`、`pytest.raises`、`store.submit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_atomic_completeness_proposal_always_stops_for_exact_human_review.AtomicGateway`（L101–L123）：继承`Gateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_model_atomic_completeness_proposal_always_stops_for_exact_human_review.AtomicGateway.complete`（L102–L123）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L104按`schema is ExtensionDesign`分支。 调用`super().complete`、`super`、`result.implementation.model_dump`、`CapabilityPlan.model_validate`。 返回路径：L123的`result`。
- `test_source_coverage_cannot_discard_contest_requirements`（L142–L161）：接收`settings`、`store`。 控制顺序：L156断言`saved["status"] == "WAITING_EXTENSION_DESIGN"`；L157断言`saved["pending"]["can_approve"] is False`；L158断言`not any(schema == "CapabilityEdits" for _, schema in gateway.calls)`；L160断言`"加权评分和盲审" in "".join(row["text"] for row in data["source_units"])`；L161断言`any("来源" in error for error in data["blocked"])`。 调用`create`、`DropsSource`、`Runtime`、`runtime.tick`、`store.get_run`、`any`、`"".join`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_coverage_cannot_discard_contest_requirements.DropsSource`（L145–L149）：继承`Gateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_coverage_cannot_discard_contest_requirements.DropsSource.complete`（L146–L149）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 调用`super().complete`、`super`。 返回路径：L149的`result`。
- `test_custom_route_requires_human_intent_and_honors_later_cancellation`（L164–L167）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L165断言`custom_requested(["模板不支持跨记录规则", "全部自己实现"])`；L166断言`not custom_requested(["全部自己实现", "不要自定义实现，仅使用模板"])`；L167断言`not custom_requested(["竞赛报名网站"])`。 调用`custom_requested`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_automation_endpoint_cannot_consume_explicit_extension_gate`（L170–L216）：接收`settings`、`store`。 控制顺序：L191断言`response.status_code == 202`；L192断言`store.get_run(run)["pending"] == gate`；L193遍历`({"version": gate["version"] + 1}, {"digest": "0" * 64})`；L199断言`response.status_code == 409`；L210断言`first.status_code == 202`；L214断言`replay.json() == first.json()`。 调用`SecretStr`、`create`、`Runtime`、`Gateway`、`runtime.tick`、`store.get_run`、`TestClient`、`create_app`、`client.post`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_orchestration.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L216。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8953`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_orchestration.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5b56dcd8ab6d92ac813dc38328d01da7d78686d052e53b622a2301f969b82213"} -->
````python
# tests/test_capability_orchestration.py
"""Authored routing fixtures, never evidence of real model/sandbox acceptance."""

from pathlib import Path

import pytest

from scripts.capability_fixture import APP, GOAL, CapabilityFixture, fixture_baseline, make_plan
from workbench.capability_contracts import CapabilityEdits, custom_requested
from workbench.errors import UnsupportedScope
from workbench.filesystem import manifest
from workbench.orchestration import ExtensionDesign
from workbench.runtime import Runtime


class Gateway:
    def __init__(self, *, permission_changes=None):
        self.calls = []
        self.permission_changes = permission_changes or []
        self.coder = CapabilityFixture()

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append((key, schema.__name__))
        if schema is ExtensionDesign:
            return ExtensionDesign(
                baseline=fixture_baseline(),
                implementation=make_plan(payload),
                permission_changes=self.permission_changes,
            )
        assert schema is CapabilityEdits
        return self.coder.complete(
            run_id,
            key,
            instruction,
            {
                **payload,
                "file_manifest": {name: row["sha256"] for name, row in payload["context"].items()},
            },
            schema,
        )


def create(store, request=GOAL):
    project = store.create_project("extension fixture", "project")
    return store.create_run(project["id"], {"requirement": request, "intelligent": True}, "run")[
        "run_id"
    ]


def test_explicit_extension_reaches_code_and_preserves_candidate_on_missing_sandbox(
    settings, store, monkeypatch
):
    import workbench.capability_sandbox as sandbox

    calls = []

    def unavailable(product, *args, **kwargs):
        calls.append(str(product))
        raise UnsupportedScope("fixture: isolated execution unavailable")

    monkeypatch.setattr(sandbox, "verify_capabilities", unavailable)
    run = create(store)
    gateway = Gateway()
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
        first = store.get_run(run)
        assert first["status"] == "BLOCKED", first
        assert first["pending"] is None
        assert [schema for _, schema in gateway.calls] == ["ExtensionDesign", "CapabilityEdits"]
        candidate = Path(calls[0])
        assert (candidate / "app.py").read_text() == APP
        before = manifest(candidate)
        store.retry(run, "retry-existing-candidate")
        runtime.tick()
        assert len(gateway.calls) == 2, "Retry must resume verification, not pay to regenerate"
        assert calls == [str(candidate), str(candidate)]
        assert manifest(candidate) == before
        assert not list((settings.data_dir / "runs" / run).glob("*delivery.zip"))


def test_permission_changes_cannot_be_auto_approved_or_recommended(settings, store):
    from workbench.store import Conflict

    run = create(store)
    gateway = Gateway(permission_changes=["新增团队管理员跨记录授权"])
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
    saved = store.get_run(run)
    assert saved["status"] == "WAITING_EXTENSION_DESIGN"
    assert len(gateway.calls) == 1
    gate = saved["pending"]
    with pytest.raises(Conflict, match="人工审阅"):
        store.submit(
            run, {"gate_id": gate["gate_id"], "action": "recommend", "approved": True}, "no-bypass"
        )


def test_model_atomic_completeness_proposal_always_stops_for_exact_human_review(settings, store):
    from workbench.capability_contracts import CapabilityPlan
    from workbench.store import Conflict

    class AtomicGateway(Gateway):
        def complete(self, run_id, key, instruction, payload, schema):
            result = super().complete(run_id, key, instruction, payload, schema)
            if schema is ExtensionDesign:
                source = payload["source_units"][0]
                raw = result.implementation.model_dump()
                raw["obligations"] = [
                    {
                        "id": "private-record",
                        "source_id": source["id"],
                        "source_sha256": source["sha256"],
                        "assertion": "标题持久化",
                        "scenario_id": "private_records",
                        "physical": {
                            "table": "entries",
                            "key": {"id": "${entry}"},
                            "values": {"title": "持久化资料-${nonce}"},
                        },
                    }
                ]
                raw["complete_source_ids"] = [source["id"]]
                result.implementation = CapabilityPlan.model_validate(raw)
            return result

    run = create(store)
    gateway = AtomicGateway()
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
    saved = store.get_run(run)
    assert saved["status"] == "WAITING_EXTENSION_DESIGN"
    assert len(gateway.calls) == 1, "No coding or paid regeneration before semantic review"
    gate = saved["pending"]
    assert gate["data"]["atomic_review"]["complete_source_ids"]
    with pytest.raises(Conflict, match="人工审阅"):
        store.submit(
            run,
            {"gate_id": gate["gate_id"], "action": "recommend", "approved": True},
            "atomic-no-model-self-approval",
        )


def test_source_coverage_cannot_discard_contest_requirements(settings, store):
    request = "竞赛报名；队伍人数限制和邀请；跨校报名；随机分配评委；加权评分和盲审；教师确认；并发唯一编号；邮件SMS和云文件。全部自己实现"

    class DropsSource(Gateway):
        def complete(self, run_id, key, instruction, payload, schema):
            result = super().complete(run_id, key, instruction, payload, schema)
            result.implementation.tasks[0].requirements = ["invented-source"]
            return result

    run = create(store, request)
    gateway = DropsSource()
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
    saved = store.get_run(run)
    assert saved["status"] == "WAITING_EXTENSION_DESIGN"
    assert saved["pending"]["can_approve"] is False
    assert not any(schema == "CapabilityEdits" for _, schema in gateway.calls)
    data = saved["pending"]["data"]
    assert "加权评分和盲审" in "".join(row["text"] for row in data["source_units"])
    assert any("来源" in error for error in data["blocked"])


def test_custom_route_requires_human_intent_and_honors_later_cancellation():
    assert custom_requested(["模板不支持跨记录规则", "全部自己实现"])
    assert not custom_requested(["全部自己实现", "不要自定义实现，仅使用模板"])
    assert not custom_requested(["竞赛报名网站"])


def test_automation_endpoint_cannot_consume_explicit_extension_gate(settings, store):
    from fastapi.testclient import TestClient
    from pydantic import SecretStr

    from workbench.api import create_app
    from workbench.store import Conflict

    settings.base_url = "https://model.example.test/v1"
    settings.model = "authored-test-model"
    settings.api_key = SecretStr("dummy-test-only-key")
    run = create(store)
    with Runtime(settings, store, Gateway(permission_changes=["扩大数据访问权限"])) as runtime:
        runtime.tick()
    gate = store.get_run(run)["pending"]
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        response = client.post(
            f"/runs/{run}/automation",
            json={"enabled": True, "accepted": True},
            headers={"Idempotency-Key": "explicit-still-required"},
        )
        assert response.status_code == 202
        assert store.get_run(run)["pending"] == gate
        for change in ({"version": gate["version"] + 1}, {"digest": "0" * 64}):
            response = client.post(
                f"/runs/{run}/resume",
                json={"gate_id": gate["gate_id"], "action": "approve", "approved": True, **change},
                headers={"Idempotency-Key": "stale-" + next(iter(change))},
            )
            assert response.status_code == 409
        body = {
            "gate_id": gate["gate_id"],
            "action": "approve",
            "approved": True,
            "version": gate["version"],
            "digest": gate["digest"],
        }
        first = client.post(
            f"/runs/{run}/resume", json=body, headers={"Idempotency-Key": "current-approval"}
        )
        assert first.status_code == 202
        replay = client.post(
            f"/runs/{run}/resume", json=body, headers={"Idempotency-Key": "current-approval"}
        )
        assert replay.json() == first.json()
    with pytest.raises(Conflict):
        store.auto_approve(run, gate)
````
