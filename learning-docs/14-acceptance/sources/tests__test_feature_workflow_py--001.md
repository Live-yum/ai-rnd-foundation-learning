# tests/test_feature_workflow.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_fixture`、`workbench.capability_contracts`、`workbench.catalog`、`workbench.domain`、`workbench.errors`、`workbench.feature_planning`、`workbench.flow`、`workbench.orchestration`、`workbench.runtime`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `create`（L28–L41）：接收`store`、`template`、`request`。 调用`store.create_project`、`store.create_run`、`Selection( template=template, frontend="api-only" if template == …`、`Selection`。 返回路径：L30的`store.create_run( project["id"], { "requirement": request, "template": template, "allow_cu…`。
- `outline`（L44–L76）：接收`payload`、`modules`、`entity`。 调用`FeatureOutline.model_validate`。 返回路径：L48的`FeatureOutline.model_validate( { "summary": "Retain baseline and route individual capabili…`。
- `FeatureGateway`（L79–L88）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `FeatureGateway.__init__`（L80–L81）：接收`baseline`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `FeatureGateway.complete`（L83–L88）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L85按`schema is Requirement`分支；L87断言`schema is FeatureDesign`。 调用`self.calls.append`、`requirement`、`FeatureDesign`、`outline`。 返回路径：L86的`requirement()`；L88的`FeatureDesign(outline=outline(payload), baseline=self.baseline)`。
- `test_explicit_option_reuses_crud_generator_and_cleanroom`（L91–L110）：接收`settings`、`store`、`plan`。 控制顺序：L94断言`options_for_run(store.get_run(run)) == Selection(frontend="api-only")`；L98断言`saved["status"] == "WAITING_DESIGN"`；L99断言`saved["pending"]["data"]["feature_outline"]["features"][0]["route"] == "native"`；L102断言`store.get_run(run)["status"] == "WAITING_DELIVERY"`；L106断言`saved["status"] == "READY"`；L107断言`saved["result"]["cleanroom"]["passed"] is True`；L108断言`saved["result"]["cleanroom"]["restart"] is True`；L109断言`[schema for _, schema in gateway.calls] == ["Requirement", "FeatureDesign"]`。后续分支沿下方源码相同行号继续阅读。 调用`create`、`FeatureGateway`、`options_for_run`、`store.get_run`、`Selection`、`Runtime`、`worker.tick`、`decision`、`gateway.calls[1][0].startswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_module_uses_existing_candidate_and_blocks_missing_executor`（L113–L165）：接收`settings`、`store`、`monkeypatch`。 控制顺序：L155断言`store.get_run(run)["status"] == "WAITING_EXTENSION_DESIGN"`；L158断言`store.get_run(run)["status"] == "BLOCKED"`；L159断言`[name for _, name in gateway.calls] == [ "Requirement", "FeatureDesign", "CapabilityE…`；L164断言`calls and (calls[0] / "app.py").is_file()`；L165断言`not list((settings.data_dir / "runs" / run).glob("*delivery.zip"))`。 调用`monkeypatch.setattr`、`create`、`SourceGateway`、`Runtime`、`worker.tick`、`store.get_run`、`decision`、`(calls[0] / "app.py").is_file`、`list`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_module_uses_existing_candidate_and_blocks_missing_executor.unavailable`（L120–L122）：接收`product`、`*args`、`**kwargs`。 控制顺序：L122抛异常，停止当前正常路径。 调用`calls.append`、`Path`、`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_module_uses_existing_candidate_and_blocks_missing_executor.SourceGateway`（L126–L149）：继承`Gateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_module_uses_existing_candidate_and_blocks_missing_executor.SourceGateway.complete`（L127–L149）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L128按`schema is Requirement`分支；L131按`schema is FeatureDesign`分支；L148断言`schema is CapabilityEdits`。 调用`self.calls.append`、`requirement`、`make_plan`、`t.model_dump`、`FeatureDesign`、`outline`、`fixture_baseline`、`super().complete`、`super`。 返回路径：L130的`requirement()`；L143的`FeatureDesign( outline=outline(payload, modules=modules, entity=None), baseline=fixture_ba…`；L149的`super().complete(run_id, key, instruction, payload, schema)`。
- `test_batch_import_missing_assets_is_design_blocker`（L168–L203）：接收`settings`、`store`。 控制顺序：L202断言`any("缺少实际运行时" in e for e in errors)`；L203断言`any("独立CapabilityPlan" in e for e in errors)`。 调用`create`、`human_scope`、`options_for_run(store.get_run(run)).model_dump`、`options_for_run`、`store.get_run`、`Plan.model_validate`、`business_plan`、`CapabilityTask`、`import_files`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_feature_source_and_baseline_must_match_before_generation`（L206–L214）：接收`settings`、`store`、`plan`。 调用`create`、`Workflow`、`FeatureGateway`、`state.update`、`workflow.feature_plan`、`workflow.checked_feature`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_constraints_block_unsupported_regular_expression`（L217–L227）：接收`plan`。 调用`pytest.raises`、`validate_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_feature_baseline_cannot_drop_independently_analyzed_obligations`（L231–L282）：接收`settings`、`store`、`plan`、`missing`。 控制顺序：L240按`missing == "numeric"`分支；L280断言`saved["pending"]["can_approve"] is False`；L281断言`saved["pending"]["data"]["blocked"]`；L282断言`not (settings.data_dir / "runs" / run / "product").exists()`。 调用`create`、`Requirement`、`business_plan`、`next`、`Plan.model_validate`、`Runtime`、`DropsObligation`、`worker.tick`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_feature_baseline_cannot_drop_independently_analyzed_obligations.DropsObligation`（L267–L275）：继承`FeatureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_feature_baseline_cannot_drop_independently_analyzed_obligations.DropsObligation.complete`（L268–L275）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L269按`schema is Requirement`分支。 调用`self.calls.append`、`FeatureDesign`、`outline`。 返回路径：L271的`approved`；L272的`FeatureDesign( outline=outline(payload, entity="task" if missing == "numeric" else "custom…`。
- `test_native_business_numeric_bounds_reach_physical_ddl`（L286–L311）：接收`template`。 控制顺序：L311断言`'"quantity" >= 1 AND "quantity" <= 9' in ddl`。 调用`business_plan`、`raw["entities"][0]["fields"].append`、`native_metadata`、`Plan.model_validate`、`next`、`str`、`CreateTable(table).compile`、`CreateTable`、`postgresql.dialect`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_feature_native_baseline_normalizes_reserved_fields_and_keeps_source_obligations`（L315–L397）：接收`settings`、`store`、`template`、`monkeypatch`。 控制顺序：L374断言`state["extension_errors"] == []`；L376断言`normalized.outline.features[0].entity == "customers"`；L377断言`normalized.baseline.entities[0].fields[0].name == "customers_description"`；L378断言`normalized.baseline.business.workflows[0].status_field == "requests_status"`；L379断言`source_plan(normalized.baseline, state["native_normalization"]) == Plan.model_validat…`；L382断言`approved.model_dump() == before[1]`；L386断言`report["design"]["baseline"] == state["plan"]`；L387断言`report["native_normalization"] == state["native_normalization"]`。后续分支沿下方源码相同行号继续阅读。 调用`business_plan`、`Plan.model_validate`、`Requirement`、`deepcopy`、`baseline.model_dump`、`approved.model_dump`、`create`、`Workflow`、`NativeGateway`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_feature_native_baseline_normalizes_reserved_fields_and_keeps_source_obligations.NativeGateway`（L365–L369）：继承`FeatureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_feature_native_baseline_normalizes_reserved_fields_and_keeps_source_obligations.NativeGateway.complete`（L366–L369）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L367按`schema is Requirement`分支。 调用`FeatureDesign`、`outline`。 返回路径：L368的`approved`；L369的`FeatureDesign(outline=outline(payload, entity="customers"), baseline=baseline)`。
- `test_feature_native_baseline_normalizes_reserved_fields_and_keeps_source_obligations.gate`（L390–L392）：接收`state`、`stage`、`data`、`actions`、`can_approve`。 调用`captured.update`。 返回路径：L392的`{"decision": "approve"}`。

</details>

**创建路径：** `tests/test_feature_workflow.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L397。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14948`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_feature_workflow.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ce855afc9d94428cabbd308d03f630e1b9962496f02fe39e864aee05eeec9ea0"} -->
````python
# tests/test_feature_workflow.py
"""Authored routing regressions; model plans alone never prove module delivery."""

import json
from copy import deepcopy
from pathlib import Path

import pytest
from conftest import decision, requirement
from test_business_contracts import business_plan
from test_capability_orchestration import Gateway

from scripts.capability_fixture import fixture_baseline, make_plan
from workbench.capability_contracts import CapabilityEdits, CapabilityTask
from workbench.catalog import Selection, options_for_run
from workbench.domain import Plan, Requirement
from workbench.errors import UnsupportedScope
from workbench.feature_planning import (
    FeatureDesign,
    FeatureOutline,
    feature_design_errors,
    import_files,
)
from workbench.flow import Workflow
from workbench.orchestration import human_scope
from workbench.runtime import Runtime


def create(store, template="python-basic", request="个人任务CRUD"):
    project = store.create_project("features", "features-project")
    return store.create_run(
        project["id"],
        {
            "requirement": request,
            "template": template,
            "allow_custom_extensions": True,
            "selection": Selection(
                template=template, frontend="api-only" if template == "python-basic" else ""
            ).model_dump(),
        },
        "features-run",
    )["run_id"]


def outline(payload, *, modules=None, entity="task"):
    refs = [s["id"] for s in payload["source_units"]]
    template = payload["selection"]["template"]
    native = "typed-crud" if template == "python-basic" else "native-crud"
    return FeatureOutline.model_validate(
        {
            "summary": "Retain baseline and route individual capabilities",
            "selection": payload["selection"],
            "source_digest": payload["source_digest"],
            "features": [
                {
                    "id": "crud",
                    "title": "CRUD",
                    "requirements": refs,
                    "route": "native",
                    "capability": native,
                    "entity": entity,
                },
                *[
                    {
                        "id": m["id"],
                        "title": m["title"],
                        "requirements": m["requirements"],
                        "route": "module",
                        "capability": m["extension"],
                        "module_id": m["id"],
                    }
                    for m in modules or []
                ],
            ],
            "modules": modules or [],
        }
    )


class FeatureGateway:
    def __init__(self, baseline):
        self.baseline, self.calls = baseline, []

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append((key, schema.__name__))
        if schema is Requirement:
            return requirement()
        assert schema is FeatureDesign
        return FeatureDesign(outline=outline(payload), baseline=self.baseline)


def test_explicit_option_reuses_crud_generator_and_cleanroom(settings, store, plan):
    run = create(store)
    gateway = FeatureGateway(plan)
    assert options_for_run(store.get_run(run)) == Selection(frontend="api-only")
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        saved = store.get_run(run)
        assert saved["status"] == "WAITING_DESIGN", saved
        assert saved["pending"]["data"]["feature_outline"]["features"][0]["route"] == "native"
        decision(store, run)
        worker.tick()
        assert store.get_run(run)["status"] == "WAITING_DELIVERY", store.get_run(run)
        decision(store, run)
        worker.tick()
    saved = store.get_run(run)
    assert saved["status"] == "READY", saved
    assert saved["result"]["cleanroom"]["passed"] is True
    assert saved["result"]["cleanroom"]["restart"] is True
    assert [schema for _, schema in gateway.calls] == ["Requirement", "FeatureDesign"]
    assert gateway.calls[1][0].startswith("plan:features:")


def test_source_module_uses_existing_candidate_and_blocks_missing_executor(
    settings, store, monkeypatch
):
    import workbench.capability_sandbox as sandbox

    calls = []

    def unavailable(product, *args, **kwargs):
        calls.append(Path(product))
        raise UnsupportedScope("fixture: isolated executor unavailable")

    monkeypatch.setattr(sandbox, "verify_capabilities", unavailable)

    class SourceGateway(Gateway):
        def complete(self, run_id, key, instruction, payload, schema):
            if schema is Requirement:
                self.calls.append((key, schema.__name__))
                return requirement()
            if schema is FeatureDesign:
                self.calls.append((key, schema.__name__))
                implementation = make_plan(payload)
                modules = [
                    {
                        **t.model_dump(),
                        "adapter": "python-basic",
                        "extension": "approved-source-module",
                        "interfaces": [t.contract],
                    }
                    for t in implementation.tasks
                ]
                return FeatureDesign(
                    outline=outline(payload, modules=modules, entity=None),
                    baseline=fixture_baseline(),
                    implementation=implementation,
                )
            assert schema is CapabilityEdits
            return super().complete(run_id, key, instruction, payload, schema)

    run = create(store, request="用户登录后保存自己的资料，并可只读共享")
    gateway = SourceGateway()
    with Runtime(settings, store, gateway) as worker:
        worker.tick()
        assert store.get_run(run)["status"] == "WAITING_EXTENSION_DESIGN", store.get_run(run)
        decision(store, run)
        worker.tick()
    assert store.get_run(run)["status"] == "BLOCKED", store.get_run(run)
    assert [name for _, name in gateway.calls] == [
        "Requirement",
        "FeatureDesign",
        "CapabilityEdits",
    ]
    assert calls and (calls[0] / "app.py").is_file()
    assert not list((settings.data_dir / "runs" / run).glob("*delivery.zip"))


def test_batch_import_missing_assets_is_design_blocker(settings, store):
    run = create(store, "fastapiadmin", "内部业务CRUD与批量导入客户")
    scope = human_scope(store, run)
    selection = options_for_run(store.get_run(run)).model_dump()
    baseline = Plan.model_validate(business_plan())
    refs = [s["id"] for s in scope["sources"]]
    task = CapabilityTask(
        id="import",
        title="Batch import",
        requirements=refs,
        files=import_files(baseline),
        contract="Import customers atomically",
        scenarios=["import-test"],
    )
    module = {
        **task.model_dump(),
        "adapter": "fastapiadmin",
        "extension": "batch-import-v1",
        "interfaces": [task.contract],
        "import_spec": {"entity": "customers"},
    }
    value = FeatureDesign(
        outline=outline(
            {
                "selection": selection,
                "source_units": scope["sources"],
                "source_digest": scope["source_digest"],
            },
            modules=[module],
            entity="customers",
        ),
        baseline=baseline,
    )
    errors = feature_design_errors(value, scope, selection)
    assert any("缺少实际运行时" in e for e in errors)
    assert any("独立CapabilityPlan" in e for e in errors)


def test_feature_source_and_baseline_must_match_before_generation(settings, store, plan):
    run = create(store)
    workflow = Workflow(settings, store, FeatureGateway(plan))
    state = {"run_id": run, "template": "python-basic", "round": 1}
    state.update(workflow.feature_plan(state))
    workflow.checked_feature(state)
    state["plan"]["entities"][0]["fields"][0]["max_length"] = 40
    with pytest.raises(UnsupportedScope, match="基础契约"):
        workflow.checked_feature(state)


def test_native_constraints_block_unsupported_regular_expression(plan):
    from workbench.native_modules import validate_plan

    plan.data_scope = "shared"
    plan.entities[0].fields[0].pattern = "^[a-z]+$"
    with pytest.raises(ValueError, match="pattern"):
        validate_plan(plan)
    plan.entities[0].fields[0].pattern = None
    plan.entities[0].fields[1].minimum = 0
    with pytest.raises(ValueError, match="numeric bounds"):
        validate_plan(plan)


@pytest.mark.parametrize("missing", ["numeric", "permissions"])
def test_feature_baseline_cannot_drop_independently_analyzed_obligations(
    settings, store, plan, missing
):
    request = (
        "quantity必须大于0"
        if missing == "numeric"
        else "经理可创建并读取客户，员工只能读取本人客户"
    )
    run = create(store, request=request)
    if missing == "numeric":
        plan.entities[0].fields[1].name = "quantity"
        approved = Requirement(
            summary=request,
            users=["个人用户"],
            data_scope="per_user",
            features=[request],
            acceptance=[request],
        )
    else:
        raw = business_plan()
        approved = Requirement(
            summary=request,
            users=["manager", "employee"],
            data_scope="shared",
            facts={"business": {"permissions": raw["business"]["permissions"]}},
            features=[request],
            acceptance=[request],
        )
        manager = next(
            p
            for p in raw["business"]["permissions"]
            if p["role"] == "manager" and p["entity"] == "customers"
        )
        manager["actions"] = [a for a in manager["actions"] if a != "create"]
        plan = Plan.model_validate(raw)

    class DropsObligation(FeatureGateway):
        def complete(self, run_id, key, instruction, payload, schema):
            if schema is Requirement:
                self.calls.append((key, schema.__name__))
                return approved
            return FeatureDesign(
                outline=outline(payload, entity="task" if missing == "numeric" else "customers"),
                baseline=plan,
            )

    with Runtime(settings, store, DropsObligation(plan)) as worker:
        worker.tick()
    saved = store.get_run(run)
    assert saved["pending"]["can_approve"] is False, saved
    assert saved["pending"]["data"]["blocked"], saved
    assert not (settings.data_dir / "runs" / run / "product").exists()


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_native_business_numeric_bounds_reach_physical_ddl(template):
    from sqlalchemy.dialects import postgresql
    from sqlalchemy.schema import CreateTable

    from workbench.native_modules import native_metadata

    raw = business_plan()
    raw["entities"][0]["fields"].append(
        {
            "name": "quantity",
            "kind": "integer",
            "minimum": 0,
            "maximum": 10,
            "exclusive_minimum": 0,
            "exclusive_maximum": 10,
        }
    )
    _, tables, names = native_metadata(
        template,
        Plan.model_validate(raw),
        "postgresql+psycopg://native:lab@127.0.0.1/native_codegen",
        "bounds",
    )
    table = next(t for t in tables if t.name == names["customers"])
    ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))
    assert '"quantity" >= 1 AND "quantity" <= 9' in ddl


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_feature_native_baseline_normalizes_reserved_fields_and_keeps_source_obligations(
    settings, store, template, monkeypatch
):
    from workbench.native_plan_normalization import source_plan

    raw = business_plan()
    raw["entities"][0]["fields"][0] = {"name": "description", "kind": "text", "max_length": 80}
    raw["entities"][1]["fields"][2]["name"] = "status"
    raw["business"]["workflows"][0]["status_field"] = "status"
    raw["business"]["metrics"][1]["filters"][0]["field"] = "status"
    raw["acceptance"] = ["CRUD"]
    baseline = Plan.model_validate(raw)
    approved = Requirement(
        summary="内部客户与请求管理",
        users=["manager", "service", "employee"],
        data_scope="shared",
        features=["CRUD"],
        acceptance=["CRUD"],
        facts={"business": raw["business"]},
        field_requirements=[
            {
                "entity": "customers",
                "field": "description",
                "kind": "text",
                "required": True,
                "max_length": 80,
            },
            {
                "entity": "requests",
                "field": "status",
                "kind": "enum",
                "choices": ["new", "active", "resolved"],
            },
        ],
        entity_requirements=[
            {
                "entity": e["name"],
                "fields": [f["name"] for f in e["fields"]],
                "additional_fields": False,
            }
            for e in raw["entities"]
        ],
    )
    before = deepcopy((baseline.model_dump(), approved.model_dump()))
    run = create(
        store,
        template,
        "内部客户与请求管理，description必填且最多80字，status为new/active/resolved",
    )

    class NativeGateway(FeatureGateway):
        def complete(self, run_id, key, instruction, payload, schema):
            if schema is Requirement:
                return approved
            return FeatureDesign(outline=outline(payload, entity="customers"), baseline=baseline)

    workflow = Workflow(settings, store, NativeGateway(baseline))
    state = {"run_id": run, "template": template, "round": 1}
    state.update(workflow.feature_plan(state))
    assert state["extension_errors"] == []
    normalized = workflow.checked_feature(state)
    assert normalized.outline.features[0].entity == "customers"
    assert normalized.baseline.entities[0].fields[0].name == "customers_description"
    assert normalized.baseline.business.workflows[0].status_field == "requests_status"
    assert source_plan(normalized.baseline, state["native_normalization"]) == Plan.model_validate(
        before[0]
    )
    assert approved.model_dump() == before[1]
    report = json.loads(
        (settings.data_dir / "runs" / run / "feature-design.json").read_text(encoding="utf-8")
    )
    assert report["design"]["baseline"] == state["plan"]
    assert report["native_normalization"] == state["native_normalization"]
    captured = {}

    def gate(state, stage, data, actions, can_approve=True):
        captured.update(data=data, can_approve=can_approve)
        return {"decision": "approve"}

    monkeypatch.setattr(workflow, "gate", gate)
    workflow.feature_design(state)
    assert captured["can_approve"] is True, captured["data"]["blocked"]
    assert captured["data"]["native_normalization"] == state["native_normalization"]
````
