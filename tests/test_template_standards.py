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
