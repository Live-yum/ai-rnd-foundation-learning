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
        # Vite's app shell is intentionally small; copy lives in the built Vue entry.
        assert '<div id="app"></div>' in html
        assert 'type="module"' in html and "/ui/app.js" in html
        entry = c.get("/ui/app.js")
        assert entry.status_code == 200
        assert "智能推荐" in entry.text and "数据库" in entry.text
        assert "1. 选择模板" in entry.text
        assert "技术选型与模板编码规范" in entry.text
        assert "创建并开始" in entry.text
        assert "批量项目" in entry.text
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


def test_workbench_examples_and_scopes_preserve_user_intent(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        html = client.get("/").text
        javascript = client.get("/ui/app.js").text
    for example in ("做一个客服管理系统", "做一个比赛报名系统", "做一个阅读书架"):
        assert example in javascript
    # Examples are explicit editable starters; interaction tests in ui/tests/workflow.test.ts
    # also verify that choosing one does not submit or prevent subsequent user edits.
    assert "填入后可自由修改" in javascript
    # Vue compiles the selected capability expression, retaining its actual scopes key.
    assert ".scopes" in javascript
    assert "模板已有的登录、数据管理和权限功能无需启用扩展" in javascript
    assert "模板外功能设置" in javascript
    assert "新闻" not in html + javascript and "资讯" not in html + javascript
