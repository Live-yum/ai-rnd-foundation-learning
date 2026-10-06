# tests/test_planning_model_contracts.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.catalog`、`workbench.domain`、`workbench.feature_planning`、`workbench.llm`、`workbench.model_diagnostics`、`workbench.model_protocol`、`workbench.orchestration`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `competition`（L26–L125）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L124断言`feature_design_errors(value, scope, scope["selection"]) == []`。 调用`scope_sources`、`digest`、`Selection().model_dump`、`Selection`、`FeatureDesign.model_validate`、`feature_design_errors`。 返回路径：L125的`scope, value`。
- `gateway`（L128–L148）：接收`store`、`contents`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`。 返回路径：L148的`ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=True), seen`。
- `gateway.handler`（L134–L146）：接收`request`。 调用`seen.append`、`json.loads`、`httpx.Response`、`min`、`len`。 返回路径：L136的`httpx.Response( 200, json={ "choices": [ { "finish_reason": "stop", "message": {"content":…`。
- `test_reported_planning_errors_repair_with_actionable_feedback_and_preserve_scope`（L152–L189）：接收`store`、`competition`、`failure`。 控制顺序：L158按`failure == "invalid_json"`分支；L161按`failure == "id"`分支；L173断言`result == expected`；L174断言`len(seen) == store.get_run(run)["model_calls"] == 2`；L175断言`seen[0]["response_format"] == seen[1]["response_format"] == {"type": "json_object"}`；L176断言`json.loads(seen[1]["messages"][1]["content"]) == payload`；L177断言`seen[1]["messages"][-2]["content"] == bad`；L178断言`hint in seen[1]["messages"][-1]["content"]`。后续分支沿下方源码相同行号继续阅读。 调用`expected.model_dump_json`、`json.loads`、`json.dumps`、`gateway`、`new_run`、`planning_payload`、`model.complete`、`len`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unrepaired_planning_error_never_becomes_an_approved_result`（L192–L204）：接收`store`、`competition`。 控制顺序：L202断言`len(seen) == 2`；L203断言`all(record["status"] == "failed" for record in store.model_records(run))`；L204断言`not any(event["kind"] == "assistant_completed" for event in store.events(run))`。 调用`expected.model_dump`、`gateway`、`json.dumps`、`new_run`、`pytest.raises`、`model.complete`、`planning_payload`、`len`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_template_only_rule_plan_receives_consistent_instructions_without_fake_module_tasks`（L207–L277）：接收`store`、`plan`。 控制顺序：L260断言`len(seen) == 1`；L261断言`result == expected and result.implementation is None`；L262断言`result.baseline.custom_rules[0].reject_examples[0]["priority"] == 0`；L263断言`feature_design_errors(result, scope, scope["selection"]) == []`；L266断言`instruction.startswith(FEATURE_DESIGN)`；L267断言`DESIGN not in instruction`；L268断言`"baseline不得包含unsupported或custom_rules" not in instruction`；L272断言`"implementation必须为null" in baseline_branch`。后续分支沿下方源码相同行号继续阅读。 调用`scope_sources`、`digest`、`Selection().model_dump`、`Selection`、`plan.model_dump`、`baseline["acceptance"].append`、`FeatureDesign.model_validate`、`gateway`、`expected.model_dump_json`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_planning_hints_follow_the_selected_adapter_and_unknown_keys_remain_invalid`（L280–L295）：接收`competition`。 控制顺序：L282遍历`("python-basic", "fastapiadmin", "yudao-vben")`；L287断言`payload["rules"]["capability_choices"] == { "native": layers["native_generator"]["fea…`；L293断言`"sign-in不是当前确定性生成器能力" in feature_design_errors( invalid_route, scope, scope["selectio…`。 调用`planning_payload`、`Selection(template=template).model_dump`、`Selection`、`deepcopy`、`feature_design_errors`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_constraints_come_from_schema_not_untrusted_validator_context`（L298–L327）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L322断言`details[0]["constraints"] == {"pattern": "^[a-z][a-z0-9_-]{0,63}$"}`；L323断言`"registration-submit" in details[0]["message"]`；L324断言`details[1]["constraints"] == {"maxLength": 100}`；L325断言`details[2]["path"] == ["outline", "[field]"]`；L326断言`"private-" not in json.dumps(details)`；L327断言`"999999" not in json.dumps(details)`。 调用`ValidationError.from_exception_data`、`schema_diagnostics`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_diagnostics_resolve_nullable_implementation_and_nested_task_refs`（L330–L345）：接收`competition`。 控制顺序：L341断言`details[("implementation", "tasks", 0, "id")]["constraints"] == { "pattern": "^[a-z][…`；L344断言`details[("implementation", "tasks", 0, "title")]["constraints"] == {"maxLength": 300}`；L345断言`"private-" not in json.dumps(list(details.values()))`。 调用`expected.model_dump`、`pytest.raises`、`FeatureDesign.model_validate`、`tuple`、`schema_diagnostics`、`json.dumps`、`list`、`details.values`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_diagnostics_do_not_guess_between_ambiguous_union_limits`（L348–L374）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L371断言`details[0]["path"] == ["item", "value"]`；L372断言`"constraints" not in details[0]`；L373断言`details[0]["message"] == "字段结构或类型不符合约定"`；L374断言`"private-" not in json.dumps(details)`。 调用`ValidationError.from_exception_data`、`schema_diagnostics`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_diagnostics_do_not_guess_between_ambiguous_union_limits.ShortText`（L349–L350）：继承`BaseModel`。声明的数据项为`value`；类型约束/数据库列参数以完整定义为准。
- `test_schema_diagnostics_do_not_guess_between_ambiguous_union_limits.LongText`（L352–L353）：继承`BaseModel`。声明的数据项为`value`；类型约束/数据库列参数以完整定义为准。
- `test_schema_diagnostics_do_not_guess_between_ambiguous_union_limits.Choice`（L355–L356）：继承`BaseModel`。声明的数据项为`item`；类型约束/数据库列参数以完整定义为准。
- `test_json_repair_diagnostics_explain_strict_rejection_without_copying_response`（L386–L391）：接收`content`、`kind`。 控制顺序：L390断言`details[0]["type"] == kind`；L391断言`"private-json-canary" not in json.dumps(details)`。 调用`pytest.raises`、`validate_content`、`json_diagnostics`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_planning_model_contracts.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L391。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16153`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_planning_model_contracts.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "bf5650b43f70a505d5d726ee3cf43a84d6ef04a81e9538b3db063fbae1f6c415"} -->
````python
# tests/test_planning_model_contracts.py
"""Offline registration-planning responses: strict repair, never delivery evidence."""

import json
from copy import deepcopy

import httpx
import pytest
from conftest import new_run
from pydantic import BaseModel, Field, SecretStr, ValidationError

from workbench.capability_contracts import scope_sources
from workbench.catalog import Selection
from workbench.domain import digest
from workbench.feature_planning import (
    FeatureDesign,
    feature_design_errors,
    planning_payload,
)
from workbench.llm import ModelFailure, ModelGateway
from workbench.model_diagnostics import json_diagnostics, schema_diagnostics
from workbench.model_protocol import validate_content
from workbench.orchestration import DESIGN, FEATURE_DESIGN


@pytest.fixture
def competition():
    messages = ["大学生计算机设计大赛：学生登录后提交和查看本人报名，管理员管理全部报名并审核。"]
    scope = {
        "sources": scope_sources(messages),
        "source_digest": digest(messages),
        "selection": Selection().model_dump(),
    }
    refs = [source["id"] for source in scope["sources"]]
    features = [
        ("sign-in", "登录后使用", "native", "authentication"),
        ("registration-submit", "提交报名", "native", "typed-crud"),
        (
            "registration-access",
            "学生查看本人报名，管理员查看全部",
            "declarative",
            "role-row-permissions",
        ),
        ("registration-review", "管理员审核报名", "declarative", "named-state-transitions"),
    ]
    value = FeatureDesign.model_validate(
        {
            "outline": {
                "summary": messages[0],
                "selection": scope["selection"],
                "source_digest": scope["source_digest"],
                "features": [
                    {
                        "id": key,
                        "title": title,
                        "requirements": refs,
                        "route": route,
                        "capability": capability,
                        "entity": "registration",
                    }
                    for key, title, route, capability in features
                ],
            },
            "baseline": {
                "title": "大学生计算机设计大赛报名",
                "data_scope": "shared",
                "acceptance": ["学生只能查看本人报名", "管理员审核报名，学生不能审核"],
                "entities": [
                    {
                        "name": "registration",
                        "description": "报名记录",
                        "fields": [
                            {"name": "project_title", "kind": "text", "max_length": 120},
                            {
                                "name": "review_state",
                                "kind": "enum",
                                "choices": ["pending", "approved", "rejected"],
                            },
                        ],
                    }
                ],
                "business": {
                    "roles": [
                        {"name": "student", "label": "参赛学生"},
                        {"name": "manager", "label": "管理员"},
                    ],
                    "registration": {"enabled": True, "default_role": "student"},
                    "bootstrap_role": "manager",
                    "role_admin_roles": ["manager"],
                    "resources": [{"entity": "registration"}],
                    "permissions": [
                        {
                            "role": "student",
                            "entity": "registration",
                            "actions": ["create", "read"],
                            "scope": "own",
                        },
                        {
                            "role": "manager",
                            "entity": "registration",
                            "actions": ["read", "update", "transition"],
                            "scope": "all",
                        },
                    ],
                    "workflows": [
                        {
                            "entity": "registration",
                            "status_field": "review_state",
                            "initial": "pending",
                            "transitions": [
                                {
                                    "name": state,
                                    "from_states": ["pending"],
                                    "to_state": state,
                                    "roles": ["manager"],
                                }
                                for state in ("approved", "rejected")
                            ],
                        }
                    ],
                },
            },
        }
    )
    assert feature_design_errors(value, scope, scope["selection"]) == []
    return scope, value


def gateway(store, contents):
    store.settings.base_url = "https://api.openai.com/v1"
    store.settings.model = "offline-planning-fixture"
    store.settings.api_key = SecretStr("offline-fixture-key")
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": contents[min(len(seen), len(contents)) - 1]},
                    }
                ]
            },
        )

    return ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=True), seen


@pytest.mark.parametrize("failure", ["invalid_json", "id", "capability"])
def test_reported_planning_errors_repair_with_actionable_feedback_and_preserve_scope(
    store, competition, failure
):
    scope, expected = competition
    valid = expected.model_dump_json()
    candidate = json.loads(valid)
    if failure == "invalid_json":
        bad = "```json\n" + valid + "\n```"
        hint, path = "json_syntax", []
    elif failure == "id":
        candidate["outline"]["features"][0]["id"] = "报名功能"
        bad = json.dumps(candidate, ensure_ascii=False)
        hint, path = "^[a-z][a-z0-9_-]{0,63}$", ["outline", "features", 0, "id"]
    else:
        candidate["outline"]["features"][3]["capability"] = "private-candidate-canary" * 10
        bad = json.dumps(candidate, ensure_ascii=False)
        hint, path = "单个能力技术键", ["outline", "features", 3, "capability"]
    model, seen = gateway(store, [bad, valid])
    run = new_run(store)
    payload = planning_payload(scope)
    result = model.complete(run, "plan:features:fixture", FEATURE_DESIGN, payload, FeatureDesign)
    assert result == expected
    assert len(seen) == store.get_run(run)["model_calls"] == 2
    assert seen[0]["response_format"] == seen[1]["response_format"] == {"type": "json_object"}
    assert json.loads(seen[1]["messages"][1]["content"]) == payload
    assert seen[1]["messages"][-2]["content"] == bad
    assert hint in seen[1]["messages"][-1]["content"]
    assert "不要删除需求" in seen[1]["messages"][-1]["content"]
    failures = [event for event in store.events(run) if event["kind"] == "assistant_failed"]
    diagnostic = failures[0]["data"]["diagnostic"]
    assert diagnostic["code"] == (
        "invalid_json" if failure == "invalid_json" else "schema_validation"
    )
    assert diagnostic["details"][0]["path"] == path
    assert "private-candidate-canary" not in json.dumps(failures)
    if failure == "capability":
        assert diagnostic["details"][0]["constraints"] == {"maxLength": 100}
        assert "100" in diagnostic["details"][0]["message"]


def test_unrepaired_planning_error_never_becomes_an_approved_result(store, competition):
    scope, expected = competition
    candidate = expected.model_dump()
    candidate["outline"]["features"][0]["id"] = "invalid feature identifier"
    model, seen = gateway(store, [json.dumps(candidate)])
    run = new_run(store)
    with pytest.raises(ModelFailure, match="两次尝试"):
        model.complete(
            run, "plan:features:fixture", FEATURE_DESIGN, planning_payload(scope), FeatureDesign
        )
    assert len(seen) == 2
    assert all(record["status"] == "failed" for record in store.model_records(run))
    assert not any(event["kind"] == "assistant_completed" for event in store.events(run))


def test_template_only_rule_plan_receives_consistent_instructions_without_fake_module_tasks(
    store, plan
):
    messages = ["个人任务 CRUD，已完成任务的优先级必须大于零。"]
    scope = {
        "sources": scope_sources(messages),
        "source_digest": digest(messages),
        "selection": Selection().model_dump(),
    }
    baseline = plan.model_dump()
    baseline["custom_rules"] = [
        {
            "description": "已完成任务的优先级必须大于零",
            "entity": "task",
            "accept_examples": [{"title": "验收任务", "priority": 1, "done": True}],
            "reject_examples": [{"title": "验收任务", "priority": 0, "done": True}],
        }
    ]
    baseline["acceptance"].append("拒绝完成状态为true但优先级为零的记录")
    expected = FeatureDesign.model_validate(
        {
            "outline": {
                "summary": messages[0],
                "selection": scope["selection"],
                "source_digest": scope["source_digest"],
                "features": [
                    {
                        "id": "task-crud" if capability == "typed-crud" else "completed-priority",
                        "title": title,
                        "requirements": [source["id"] for source in scope["sources"]],
                        "route": "native",
                        "capability": capability,
                        "entity": "task",
                    }
                    for title, capability in [
                        ("任务管理", "typed-crud"),
                        ("完成约束", "single-record-rules"),
                    ]
                ],
                "modules": [],
            },
            "baseline": baseline,
            "implementation": None,
        }
    )
    model, seen = gateway(store, [expected.model_dump_json()])
    result = model.complete(
        new_run(store),
        "plan:features:rules",
        FEATURE_DESIGN,
        planning_payload(scope),
        FeatureDesign,
    )
    assert len(seen) == 1
    assert result == expected and result.implementation is None
    assert result.baseline.custom_rules[0].reject_examples[0]["priority"] == 0
    assert feature_design_errors(result, scope, scope["selection"]) == []

    instruction = seen[0]["messages"][0]["content"]
    assert instruction.startswith(FEATURE_DESIGN)
    assert DESIGN not in instruction
    assert "baseline不得包含unsupported或custom_rules" not in instruction
    baseline_branch = instruction.split("无模块分支（outline.modules为空）：", 1)[1].split(
        "有模块分支（outline.modules非空）：", 1
    )[0]
    assert "implementation必须为null" in baseline_branch
    assert "不构造implementation.tasks、scenarios、runtime" in baseline_branch
    assert "custom_rules允许按普通Plan契约" in baseline_branch
    assert "tasks及其场景覆盖" not in baseline_branch
    # The separate extension workflow still enforces its original rule/module separation.
    assert "baseline不得包含unsupported或custom_rules" in DESIGN


def test_planning_hints_follow_the_selected_adapter_and_unknown_keys_remain_invalid(competition):
    scope, expected = competition
    for template in ("python-basic", "fastapiadmin", "yudao-vben"):
        payload = planning_payload(
            {**scope, "selection": Selection(template=template).model_dump()}
        )
        layers = payload["adapter"]["capability_layers"]
        assert payload["rules"]["capability_choices"] == {
            "native": layers["native_generator"]["features"],
            "declarative": layers["declarative_business"]["features"],
        }
    invalid_route = deepcopy(expected)
    invalid_route.outline.features[0].capability = "unsupported-capability"
    assert "sign-in不是当前确定性生成器能力" in feature_design_errors(
        invalid_route, scope, scope["selection"]
    )


def test_diagnostic_constraints_come_from_schema_not_untrusted_validator_context():
    error = ValidationError.from_exception_data(
        "FeatureDesign",
        [
            {
                "type": "string_pattern_mismatch",
                "loc": ("outline", "features", 0, "id"),
                "input": "private-input-canary",
                "ctx": {"pattern": "private-pattern-canary"},
            },
            {
                "type": "string_too_long",
                "loc": ("outline", "features", 3, "capability"),
                "input": "private-input-canary",
                "ctx": {"max_length": 999999},
            },
            {
                "type": "extra_forbidden",
                "loc": ("outline", "private-field-canary"),
                "input": "private-input-canary",
            },
        ],
    )
    details = schema_diagnostics(error, FeatureDesign)
    assert details[0]["constraints"] == {"pattern": "^[a-z][a-z0-9_-]{0,63}$"}
    assert "registration-submit" in details[0]["message"]
    assert details[1]["constraints"] == {"maxLength": 100}
    assert details[2]["path"] == ["outline", "[field]"]
    assert "private-" not in json.dumps(details)
    assert "999999" not in json.dumps(details)


def test_schema_diagnostics_resolve_nullable_implementation_and_nested_task_refs(competition):
    _, expected = competition
    candidate = expected.model_dump()
    candidate["implementation"] = {
        "tasks": [{"id": "private-invalid id", "title": "private-title-canary" * 30}]
    }
    with pytest.raises(ValidationError) as error:
        FeatureDesign.model_validate(candidate)
    details = {
        tuple(detail["path"]): detail for detail in schema_diagnostics(error.value, FeatureDesign)
    }
    assert details[("implementation", "tasks", 0, "id")]["constraints"] == {
        "pattern": "^[a-z][a-z0-9_-]{0,63}$"
    }
    assert details[("implementation", "tasks", 0, "title")]["constraints"] == {"maxLength": 300}
    assert "private-" not in json.dumps(list(details.values()))


def test_schema_diagnostics_do_not_guess_between_ambiguous_union_limits():
    class ShortText(BaseModel):
        value: str = Field(max_length=5)

    class LongText(BaseModel):
        value: str = Field(max_length=10)

    class Choice(BaseModel):
        item: ShortText | LongText

    # A diagnostic without a union-branch discriminator cannot establish one limit.
    error = ValidationError.from_exception_data(
        "Choice",
        [
            {
                "type": "string_too_long",
                "loc": ("item", "value"),
                "input": "private-input-canary",
                "ctx": {"max_length": 5},
            }
        ],
    )
    details = schema_diagnostics(error, Choice)
    assert details[0]["path"] == ["item", "value"]
    assert "constraints" not in details[0]
    assert details[0]["message"] == "字段结构或类型不符合约定"
    assert "private-" not in json.dumps(details)


@pytest.mark.parametrize(
    "content,kind",
    [
        ('{"private-json-canary": "incomplete', "json_syntax"),
        ('{"private-json-canary":1,"private-json-canary":2}', "duplicate_json_key"),
        ('{"private-json-canary":NaN}', "non_finite_json_number"),
        ('["private-json-canary"]', "response_must_be_json_object"),
    ],
)
def test_json_repair_diagnostics_explain_strict_rejection_without_copying_response(content, kind):
    with pytest.raises(ValueError) as error:
        validate_content(content, FeatureDesign, mode="json_object")
    details = json_diagnostics(error.value)
    assert details[0]["type"] == kind
    assert "private-json-canary" not in json.dumps(details)
````
