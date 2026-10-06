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
