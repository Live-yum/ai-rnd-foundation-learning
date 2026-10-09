# tests/test_guided_selection.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.api`、`workbench.catalog`、`workbench.domain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_incompatible_stack_is_rejected_before_a_model_call`（L18–L20）：接收`bad`。 调用`pytest.raises`、`Selection.model_validate`、`pytest.mark.parametrize`、`dict`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_selection_capabilities_include_user_reported_search_and_dates`（L23–L28）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L25断言`{"keyword-search", "exact-filter", "date-range", "enum"} <= set(c["features"])`；L26断言`c["defaults"]["title_max_length"] == 250`；L27断言`c["defaults"]["body_max_length"] == 3000`；L28断言`c["date_range_inclusive"] is True`。 调用`Selection().capabilities`、`Selection`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_control_page_has_template_first_and_smart_button`（L31–L48）：接收`settings`。 控制顺序：L35断言`'<div id="app"></div>' in html`；L36断言`'type="module"' in html and "/ui/app.js" in html`；L38断言`entry.status_code == 200`；L39断言`"智能推荐" in entry.text and "数据库" in entry.text`；L40断言`"1. 选择模板" in entry.text`；L41断言`"技术选型与模板编码规范" in entry.text`；L42断言`"创建并开始" in entry.text`；L43断言`"批量项目" in entry.text`。后续分支沿下方源码相同行号继续阅读。 调用`TestClient`、`create_app`、`c.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bad_selection_mismatch_is_not_silently_replaced`（L51–L55）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`RunInput`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_catalog_publishes_business_scope_without_losing_stack_choices`（L58–L80）：接收`settings`。 控制顺序：L62断言`{row["template"] for row in catalog} == { "python-basic", "fastapiadmin", "yudao-vben…`；L67遍历`catalog`；L69断言`row == original`；L70断言`row["backend"]`；L71断言`row["frontends"] and row["databases"]`；L72断言`"shared" in row["scopes"]`；L73断言`row["business_contract"]["scope"] == "shared"`；L74断言`"named-state-transitions" in row["business_contract"]["features"]`。后续分支沿下方源码相同行号继续阅读。 调用`TestClient`、`create_app`、`client.get("/catalog").json`、`client.get`、`Selection(template=row["template"]).capabilities`、`Selection`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workbench_examples_and_scopes_preserve_user_intent`（L83–L96）：接收`settings`。 控制顺序：L87遍历`("做一个客服管理系统", "做一个比赛报名系统", "做一个阅读书架")`；L88断言`example in javascript`；L91断言`"填入后可自由修改" in javascript`；L93断言`".scopes" in javascript`；L94断言`"模板已有的登录、数据管理和权限功能无需启用扩展" in javascript`；L95断言`"模板外功能设置" in javascript`；L96断言`"新闻" not in html + javascript and "资讯" not in html + javascript`。 调用`TestClient`、`create_app`、`client.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_guided_selection.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L96。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4330`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_guided_selection.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "686e8124fe31722128a41c96a9cb228871f3e1ab8337e66ed35aeaf643e20560"} -->
````python
# tests/test_guided_selection.py
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
````
