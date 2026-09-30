import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from workbench.api import create_app
from workbench.catalog import Selection
from workbench.domain import RunInput


@pytest.mark.parametrize(
    "bad",
    [
        dict(template="yudao-vben", database="sqlite"),
        dict(template="python-basic", frontend="vben-antd"),
        dict(template="fastapiadmin", backend="yudao-java"),
    ],
)
def test_incompatible_stack_is_rejected_before_a_model_call(bad):
    with pytest.raises(ValidationError):
        Selection.model_validate(bad)


def test_selection_capabilities_include_user_reported_search_and_dates():
    c = Selection().capabilities()
    assert {"keyword-search", "exact-filter", "date-range", "enum"} <= set(c["features"])
    assert c["defaults"]["title_max_length"] == 250
    assert c["defaults"]["body_max_length"] == 3000
    assert c["date_range_inclusive"] is True


def test_actual_control_page_has_template_first_and_smart_button(settings):
    with TestClient(create_app(settings, start_worker=False)) as c:
        html = c.get("/").text
        assert "智能推荐" in html and "数据库" in html
        assert c.get("/ui/app.js").status_code == 200
        assert c.get("/ui/not-allowed.txt").status_code == 404
        assert c.get("/models").status_code == 401
        c.headers["Authorization"] = "Bearer " + c.app.state.token
        assert c.get("/catalog").status_code == 200
        assert c.get("/models").status_code == 200


def test_bad_selection_mismatch_is_not_silently_replaced():
    with pytest.raises(ValidationError):
        RunInput(
            requirement="测试", template="python-basic", selection={"template": "fastapiadmin"}
        )


def test_catalog_publishes_business_scope_without_losing_stack_choices(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        client.headers["Authorization"] = "Bearer " + client.app.state.token
        catalog = client.get("/catalog").json()
    assert {row["template"] for row in catalog} == {
        "python-basic",
        "fastapiadmin",
        "yudao-vben",
    }
    for row in catalog:
        original = Selection(template=row["template"]).capabilities()
        assert row == original
        assert row["backend"]
        assert row["frontends"] and row["databases"]
        assert "shared" in row["scopes"]
        assert row["business_contract"]["scope"] == "shared"
        assert "named-state-transitions" in row["business_contract"]["features"]
        assert "no arbitrary scripts or network side effects" in row["business_contract"]["limits"]
    basic = next(row for row in catalog if row["template"] == "python-basic")
    assert basic["scope"] == "per_user"
    assert basic["scopes"] == ["per_user", "shared"]
    assert basic["frontends"] == ["simple-admin", "api-only"]
    assert basic["databases"] == ["sqlite", "postgresql"]


def test_workbench_hints_use_customer_case_without_replacing_user_input(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        html = client.get("/").text
        javascript = client.get("/ui/app.js").text
    assert "内部客户服务管理平台" in html
    for name in (
        "customer-service.md",
        "customer-service-decisions.md",
        "customer-service-contract.md",
    ):
        assert name in html
    assert "chosen.scopes" in javascript
    assert "声明式业务合同" in javascript
    assert "新闻" not in html and "资讯" not in html
