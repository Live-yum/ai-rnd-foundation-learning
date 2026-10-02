"""Presentation provenance survives provider spelling variations without field exemptions."""

import json
from copy import deepcopy

import pytest

from workbench.business_capabilities import business_gaps
from workbench.domain import Plan, Requirement
from workbench.requirement_coverage import coverage_gaps
from workbench.settings import ROOT

ALIASES = [
    "ui_metadata",
    "UI_Metadata",
    "uiMetadata",
    "ui-metadata",
    "ui metadata",
    "ui.labels",
    "uiFieldLabels",
    "UIFieldLabels",
    "field_labels",
    "fieldLabels",
    "display_names",
    "displayNames",
    "display-names",
    "customer_labels",
    "customerLabels",
    "localized_labels",
    "i18n_fields",
    "translationLabels",
    "字段中文名",
    "字段显示标签",
    "界面文案",
]


def recorded():
    envelope = json.loads(
        (ROOT / "tests/fixtures/customer_design_diagnostics/1d7c70b/fastapiadmin.json").read_text(
            encoding="utf-8"
        )
    )
    assert envelope["approval_status"] == "unapproved" and envelope["execution_authorized"] is False
    return deepcopy(envelope["requirement"]), Plan.model_validate(envelope["candidate_plan"])


@pytest.mark.parametrize("namespace", ALIASES)
@pytest.mark.parametrize("encoding", ["native", "json", "nested"])
def test_exact_recorded_display_namespace_spellings_never_create_contracts(namespace, encoding):
    data, plan = recorded()
    display = data["facts"].pop("labels")
    if encoding == "json":
        display = json.dumps(display, ensure_ascii=False)
    elif encoding == "nested":
        display = [{"wrapper": [json.dumps(display, ensure_ascii=False)]}]
    data["facts"][namespace] = display
    requirement = Requirement.model_validate(data)
    assert coverage_gaps(requirement, plan) == []
    assert business_gaps(requirement, plan) == []


@pytest.mark.parametrize("namespace", ALIASES)
def test_business_display_aliases_do_not_invent_metrics_or_permissions(namespace):
    data, plan = recorded()
    data.update(features=[], acceptance=[])
    data["facts"] = {
        namespace: {
            "metrics": {"name": "指标名称", "kind": "指标类型", "entity": "业务实体"},
            "permissions": {"role": "角色", "entity": "实体", "actions": "操作", "scope": "范围"},
        }
    }
    requirement = Requirement.model_validate(data)
    assert coverage_gaps(requirement, plan) == []
    assert business_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "name",
    [
        "ui_metadata",
        "field_labels",
        "display_names",
        "customer_labels",
        "localized_labels",
        "i18n_fields",
    ],
)
def test_real_fields_named_like_display_aliases_keep_explicit_constraints(name):
    plan = Plan(
        title="Field collision",
        data_scope="shared",
        entities=[
            {
                "name": "records",
                "description": "Real field namespace collision",
                "fields": [{"name": name, "kind": "text", "required": False}],
            }
        ],
        acceptance=["Preserve field constraints"],
    )
    requirement = Requirement(
        summary="Explicit constraint",
        users=["Reader"],
        data_scope="shared",
        features=[],
        acceptance=[],
        facts={"records": {name: {"required": True}}},
    )
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[0].required = True
    assert coverage_gaps(requirement, plan) == []
