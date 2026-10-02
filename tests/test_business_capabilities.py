import pytest

from workbench.business_capabilities import business_gaps
from workbench.catalog import Selection
from workbench.domain import Plan, Requirement
from workbench.settings import ROOT


def customer():
    prose = (ROOT / "examples/requirements/customer-service.md").read_text(encoding="utf-8")
    return Requirement(
        summary=prose,
        users=["管理人员", "服务人员", "普通员工"],
        data_scope="shared",
        features=["内部客户服务管理"],
        acceptance=["完整实现原始需求"],
    )


def test_customer_contract_satisfies_recognized_required_business_behaviors():
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    assert business_gaps(customer(), plan) == []


@pytest.mark.parametrize("kind", ["count", "average_duration", "group_count", "time_count"])
def test_requested_metric_cannot_be_replaced_by_crud_or_other_aggregate(kind):
    raw = __import__("json").loads(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    raw["business"]["metrics"] = [m for m in raw["business"]["metrics"] if m["kind"] != kind]
    assert business_gaps(customer(), Plan.model_validate(raw))


def test_plain_crud_does_not_satisfy_customer_case():
    raw = __import__("json").loads(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    raw.pop("business")
    assert business_gaps(customer(), Plan.model_validate(raw))


def test_catalog_separates_default_crud_from_declarative_business_mode():
    for template in ["python-basic", "fastapiadmin", "yudao-vben"]:
        capabilities = Selection(template=template).capabilities()
        assert "shared" in capabilities["scopes"]
        assert capabilities["business_contract"]["scope"] == "shared"
        assert "datetime" in capabilities["business_contract"]["field_kinds"]
