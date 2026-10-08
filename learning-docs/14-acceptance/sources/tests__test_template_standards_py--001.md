# tests/test_template_standards.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.api`、`workbench.capability_contracts`、`workbench.capability_editing`、`workbench.catalog`、`workbench.coding`、`workbench.domain`、`workbench.feature_planning`、`workbench.filesystem`、`workbench.generator`、`workbench.native_style`、`workbench.template_adapters`、`workbench.template_standards`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_catalog_and_planner_expose_selected_versioned_standards`（L23–L44）：接收`settings`。 控制顺序：L28断言`response.status_code == 200`；L30遍历`template_ids()`；L36断言`standard == catalog[template]`；L37断言`standard["version"] == 1`；L38断言`standard["path"] == f"templates/standards/{template}.md"`；L39断言`1000 < len(standard["content"]) <= 12000`；L40断言`standard["sha256"] == sha256(standard["content"].encode()).hexdigest()`；L41断言`set(standard["sources"]) == {"templates/standards/common.md", standard["path"]}`。后续分支沿下方源码相同行号继续阅读。 调用`TestClient`、`create_app`、`client.get`、`response.json`、`template_ids`、`Selection`、`planning_payload`、`selected.model_dump`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_guidance_is_source_bound_and_preserves_upstream_instructions`（L48–L59）：接收`tmp_path`、`template`。 控制顺序：L53断言`manifest(tmp_path) == first`；L54断言`"Keep existing layering." in (tmp_path / "AGENTS.md").read_text()`；L56断言`record["template"] == template`；L57断言`record["sha256"] == sha(tmp_path / "VIBECODING.md")`；L58断言`record["sha256"] == coding_standard(template)["sha256"]`；L59断言`"content" not in record`。 调用`atomic_text`、`write_coding_standard`、`manifest`、`(tmp_path / "AGENTS.md").read_text`、`json.loads`、`(tmp_path / "template-standard.json").read_text`、`sha`、`coding_standard`、`pytest.mark.parametrize`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_guidance_matches_rule_model_context`（L63–L93）：接收`tmp_path`、`plan`、`frontend`。 控制顺序：L91断言`(product / "custom_rules.py").read_text() == source.rstrip()`；L92断言`set(generation["files"]) >= {"AGENTS.md", "VIBECODING.md", "template-standard.json"}`；L93断言`(product / "web").exists() == (frontend == "simple-admin")`。 调用`generate_basic`、`Selection(frontend=frontend).model_dump`、`Selection`、`code_rules`、`Gateway`、`(product / "custom_rules.py").read_text`、`source.rstrip`、`set`、`(product / "web").exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_guidance_matches_rule_model_context.Gateway`（L68–L88）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_generated_guidance_matches_rule_model_context.Gateway.complete`（L69–L88）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L70断言`schema is Patches`；L71断言`"coding_standard" in instruction`；L72断言`payload["plan"] == plan.model_dump()`；L73断言`payload["coding_standard"]["content"] == (product / "VIBECODING.md").read_text()`；L74断言`payload["coding_standard"]["sha256"] == generation["files"]["VIBECODING.md"]`。 调用`plan.model_dump`、`(product / "VIBECODING.md").read_text`、`Patches.model_validate`。 返回路径：L75的`Patches.model_validate( { "patches": [ { "path": "custom_rules.py", "before_sha256": paylo…`。
- `test_aider_rule_model_receives_same_standard`（L96–L115）：接收`tmp_path`、`plan`、`settings`、`monkeypatch`。 调用`generate_basic`、`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`aider_tool.code_rules_with_aider`、`Gateway`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_aider_rule_model_receives_same_standard.ReachedModel`（L102–L103）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_aider_rule_model_receives_same_standard.Gateway`（L105–L111）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_aider_rule_model_receives_same_standard.Gateway.complete`（L106–L111）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L107断言`schema is aider_tool.EditBlocks`；L108断言`"coding_standard" in instruction`；L109断言`payload["coding_standard"]["sha256"] == sha(product / "VIBECODING.md")`；L110断言`set(payload["context"]["files"]) == {"custom_rules.py", "approved-spec.json"}`；L111抛异常，停止当前正常路径。 调用`sha`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rule_model_receives_selected_standard`（L119–L146）：接收`tmp_path`、`settings`、`monkeypatch`、`template`。 调用`atomic_text`、`monkeypatch.setattr`、`native_coding.native_rule_customizer`、`Gateway`、`pytest.raises`、`customize`、`rule_plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rule_model_receives_selected_standard.ReachedModel`（L133–L134）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_native_rule_model_receives_selected_standard.Gateway`（L136–L142）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_native_rule_model_receives_selected_standard.Gateway.complete`（L137–L142）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L138断言`schema is native_coding.NativeEdits`；L139断言`"coding_standard" in instruction`；L140断言`payload["coding_standard"] == coding_standard(template)`；L141断言`payload["registered_files"][path]["sha256"] == sha(product / path)`；L142抛异常，停止当前正常路径。 调用`coding_standard`、`sha`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_module_cannot_edit_or_replace_its_guidance`（L151–L160）：接收`template`、`name`。 控制顺序：L160断言`task_path_errors(task, Selection(template=template).model_dump())`。 调用`CapabilityTask`、`task_path_errors`、`Selection(template=template).model_dump`、`Selection`、`pytest.mark.parametrize`、`template_ids`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_module_boundary_uses_actual_yudao_multimodule_layout`（L165–L181）：接收`module`、`tree`。 控制顺序：L176断言`not task_path_errors(task, Selection(template="yudao-vben").model_dump())`；L177断言`not adapter.allows_module_path( path.replace("yudao-module-infra/", "yudao-module-sys…`；L180断言`not adapter.allows_module_path(path.replace("src/" + tree, "src/../.."))`；L181断言`not adapter.allows_module_path("frontend-product/apps/web-antd/src/main.ts")`。 调用`get_adapter`、`CapabilityTask`、`task_path_errors`、`Selection(template="yudao-vben").model_dump`、`Selection`、`adapter.allows_module_path`、`path.replace`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_page_contracts_handle_multiple_entities_and_shared_business_panels`（L184–L195）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L186断言`len(pages) == 6`；L187断言`"apps/web-antd/src/views/infra/wbservicecase/index.vue" in pages`；L188断言`"apps/web-antd/src/views/infra/wbloanitem/modules/form.vue" in pages`；L189断言`pages["apps/web-antd/src/views/infra/rnd-business/metric-chart.vue"] == ( {"EchartsUI…`；L193遍历`["python-basic", "unregistered-native"]`。 调用`native_page_contracts`、`iter`、`len`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_template_standards.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L195。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8850`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_template_standards.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "82122ab99a6b8b38ebd5aaa588cdbadb71e1602a64f2eaa7f9dc629262928169"} -->
````python
# tests/test_template_standards.py
"""Catalog, model and delivered guidance agree without weakening editing gates."""

import json
from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from workbench.api import create_app
from workbench.capability_contracts import CapabilityTask
from workbench.capability_editing import task_path_errors
from workbench.catalog import Selection
from workbench.coding import code_rules
from workbench.domain import Patches
from workbench.feature_planning import planning_payload
from workbench.filesystem import atomic_text, manifest, sha
from workbench.generator import generate_basic
from workbench.native_style import native_page_contracts
from workbench.template_adapters import get_adapter, template_ids
from workbench.template_standards import coding_standard, write_coding_standard


def test_catalog_and_planner_expose_selected_versioned_standards(settings):
    with TestClient(create_app(settings, start_worker=False)) as client:
        response = client.get(
            "/catalog", headers={"Authorization": "Bearer " + client.app.state.token}
        )
    assert response.status_code == 200
    catalog = {row["template"]: row["coding_standard"] for row in response.json()}
    for template in template_ids():
        selected = Selection(template=template)
        payload = planning_payload(
            {"selection": selected.model_dump(), "sources": [], "source_digest": "a" * 64}
        )
        standard = payload["adapter"]["coding_standard"]
        assert standard == catalog[template]
        assert standard["version"] == 1
        assert standard["path"] == f"templates/standards/{template}.md"
        assert 1000 < len(standard["content"]) <= 12000
        assert standard["sha256"] == sha256(standard["content"].encode()).hexdigest()
        assert set(standard["sources"]) == {"templates/standards/common.md", standard["path"]}
        assert "## 前端交互的最低要求" in standard["content"]
        assert "独立" in standard["content"]
    assert len({row["sha256"] for row in catalog.values()}) == len(template_ids())


@pytest.mark.parametrize("template", template_ids())
def test_guidance_is_source_bound_and_preserves_upstream_instructions(tmp_path, template):
    atomic_text(tmp_path / "AGENTS.md", "# Upstream\n\nKeep existing layering.\n")
    write_coding_standard(tmp_path, template)
    first = manifest(tmp_path)
    write_coding_standard(tmp_path, template)
    assert manifest(tmp_path) == first
    assert "Keep existing layering." in (tmp_path / "AGENTS.md").read_text()
    record = json.loads((tmp_path / "template-standard.json").read_text())
    assert record["template"] == template
    assert record["sha256"] == sha(tmp_path / "VIBECODING.md")
    assert record["sha256"] == coding_standard(template)["sha256"]
    assert "content" not in record


@pytest.mark.parametrize("frontend", ["simple-admin", "api-only"])
def test_generated_guidance_matches_rule_model_context(tmp_path, plan, frontend):
    product = tmp_path / "product"
    generation = generate_basic(plan, product, Selection(frontend=frontend).model_dump())
    source = "def validate(entity, data):\n    return None\n"

    class Gateway:
        def complete(self, run, key, instruction, payload, schema):
            assert schema is Patches
            assert "coding_standard" in instruction
            assert payload["plan"] == plan.model_dump()
            assert payload["coding_standard"]["content"] == (product / "VIBECODING.md").read_text()
            assert payload["coding_standard"]["sha256"] == generation["files"]["VIBECODING.md"]
            return Patches.model_validate(
                {
                    "patches": [
                        {
                            "path": "custom_rules.py",
                            "before_sha256": payload["context"]["files"]["custom_rules.py"][
                                "sha256"
                            ],
                            "content": source,
                        }
                    ],
                    "explanation": "No additional rule was requested.",
                }
            )

    code_rules("fixture", plan, product, Gateway(), 0)
    assert (product / "custom_rules.py").read_text() == source.rstrip()
    assert set(generation["files"]) >= {"AGENTS.md", "VIBECODING.md", "template-standard.json"}
    assert (product / "web").exists() == (frontend == "simple-admin")


def test_aider_rule_model_receives_same_standard(tmp_path, plan, settings, monkeypatch):
    from workbench import aider_tool

    product = tmp_path / "product"
    generate_basic(plan, product)

    class ReachedModel(Exception):
        pass

    class Gateway:
        def complete(self, run, key, instruction, payload, schema):
            assert schema is aider_tool.EditBlocks
            assert "coding_standard" in instruction
            assert payload["coding_standard"]["sha256"] == sha(product / "VIBECODING.md")
            assert set(payload["context"]["files"]) == {"custom_rules.py", "approved-spec.json"}
            raise ReachedModel

    monkeypatch.setattr(aider_tool, "command", lambda *_: pytest.fail("No model edit was returned"))
    with pytest.raises(ReachedModel):
        aider_tool.code_rules_with_aider("fixture", plan, product, Gateway(), settings, 0)


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_native_rule_model_receives_selected_standard(tmp_path, settings, monkeypatch, template):
    from test_native_tools import rule_plan

    from workbench import native_coding

    settings.enable_coding = True
    settings.coding_engine = "aider"
    product, reports = tmp_path / "product", tmp_path / "reports"
    suffix = ".py" if template == "fastapiadmin" else ".java"
    path = f"business/device/rule{suffix}"
    atomic_text(product / path, "approved-scaffold")
    atomic_text(reports / "native-front-prepared.json", "{}")
    monkeypatch.setattr(native_coding, "scaffold_native_rules", lambda *_: {"editable": [path]})

    class ReachedModel(Exception):
        pass

    class Gateway:
        def complete(self, run, key, instruction, payload, schema):
            assert schema is native_coding.NativeEdits
            assert "coding_standard" in instruction
            assert payload["coding_standard"] == coding_standard(template)
            assert payload["registered_files"][path]["sha256"] == sha(product / path)
            raise ReachedModel

    customize = native_coding.native_rule_customizer(settings, Gateway(), "fixture")
    with pytest.raises(ReachedModel):
        customize(template, rule_plan(), product, product, product, {}, [], reports)


@pytest.mark.parametrize("template", template_ids())
@pytest.mark.parametrize("name", ["AGENTS.md", "VIBECODING.md", "template-standard.json"])
def test_approved_module_cannot_edit_or_replace_its_guidance(template, name):
    task = CapabilityTask(
        id="feature",
        title="Business feature",
        requirements=["source-0"],
        files=[name],
        contract="Implement approved feature",
        scenarios=["acceptance"],
    )
    assert task_path_errors(task, Selection(template=template).model_dump())


@pytest.mark.parametrize("module", ["yudao-module-infra-server", "yudao-module-infra-api"])
@pytest.mark.parametrize("tree", ["main", "test"])
def test_native_module_boundary_uses_actual_yudao_multimodule_layout(module, tree):
    adapter = get_adapter("yudao-vben")
    path = f"backend/yudao-module-infra/{module}/src/{tree}/java/cn/iocoder/Example.java"
    task = CapabilityTask(
        id="feature",
        title="Business feature",
        requirements=["source-0"],
        files=[path],
        contract="Implement approved feature",
        scenarios=["acceptance"],
    )
    assert not task_path_errors(task, Selection(template="yudao-vben").model_dump())
    assert not adapter.allows_module_path(
        path.replace("yudao-module-infra/", "yudao-module-system/", 1)
    )
    assert not adapter.allows_module_path(path.replace("src/" + tree, "src/../.."))
    assert not adapter.allows_module_path("frontend-product/apps/web-antd/src/main.ts")


def test_native_page_contracts_handle_multiple_entities_and_shared_business_panels():
    pages = native_page_contracts("yudao-vben", iter(["service_case", "loan_item"]), business=True)
    assert len(pages) == 6
    assert "apps/web-antd/src/views/infra/wbservicecase/index.vue" in pages
    assert "apps/web-antd/src/views/infra/wbloanitem/modules/form.vue" in pages
    assert pages["apps/web-antd/src/views/infra/rnd-business/metric-chart.vue"] == (
        {"EchartsUI"},
        ["@vben/plugins/echarts"],
    )
    for template in ["python-basic", "unregistered-native"]:
        with pytest.raises(ValueError):
            native_page_contracts(template, ["record"])
````
