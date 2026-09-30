"""Native Plop/Aider safety contracts; real Java/Vue services run in native CI."""

import json

import pytest

from scripts.ci_native_generated import acceptance_spec
from workbench.domain import CustomRule
from workbench.filesystem import atomic_text, sha
from workbench.native_coding import NativeEdits, preview, region, rollback, validate_expression
from workbench.scaffolding import scaffold_native_rules
from workbench.settings import ROOT


def rule_plan():
    plan = acceptance_spec()
    plan.custom_rules = [CustomRule(description="quantity must be nonnegative", entity="device",
        accept_examples=[{"name": "device-rule", "quantity": 0, "active": False}, {"name": "device-rule-2", "quantity": 7, "active": True}],
        reject_examples=[{"name": "device-rule", "quantity": -1, "active": False}])]
    return plan


def native_product(root, template):
    if template == "fastapiadmin":
        module = root / "backend/app/plugin/module_rnd/device"
        atomic_text(module / "schema.py", "from pydantic import BaseModel\nclass DeviceCreateSchema(BaseModel):\n    quantity: int\n\nclass DeviceUpdateSchema(BaseModel):\n    quantity: int\n\nclass DeviceOutSchema(DeviceCreateSchema):\n    pass\n")
        form = root / "frontend/web/src/views/module_rnd/device/index.vue"
        body = '<script lang="ts" setup>\nasync function handleSubmit() {\n  await crud.handleSubmit();\n}\n</script>\n<template>\n        <FaForm />\n</template>\n'
    else:
        module = root / "backend/yudao-module-infra/yudao-module-infra-server/src/main/java/cn/iocoder/yudao/module/infra/controller/admin/wbdevice/vo"
        atomic_text(module / "WbDeviceSaveReqVO.java", "package cn.iocoder.yudao.module.infra.controller.admin.wbdevice.vo;\npublic class WbDeviceSaveReqVO { }\n")
        form = root / "frontend-product/apps/web-antd/src/views/infra/wbdevice/modules/form.vue"
        body = '<script lang="ts" setup>\nconst modal = {async onConfirm() {\n    try {\n      await (formData.value?.id ? update(data) : create(data));\n    } finally {}\n}};\n</script>\n<template>\n  <Modal :title="getTitle"><Form /></Modal>\n</template>\n'
    atomic_text(form, body)
    return root


@pytest.mark.parametrize("suffix,expression", [(".py", 'data["quantity"] >= 0'), (".java", "quantity == null || quantity >= 0"), (".vue", "Number(data.quantity) >= 0")])
def test_native_expression_languages(suffix, expression):
    validate_expression(expression, suffix, ["quantity"])


@pytest.mark.parametrize("suffix,expression", [(".py", "__import__('os').system('id')"), (".py", "data['unknown'] > 0"), (".java", 'Runtime.getRuntime().exec("id")'), (".java", "quantity = 0"), (".java", "quantity++ > 0"), (".java", "new Boolean(true)"), (".java", "quantity.getClass() != null"), (".vue", "globalThis.fetch('remote')"), (".vue", "data.quantity = 0"), (".vue", "data.constructor.constructor('return process')()"), (".vue", "(() => true)()"), (".vue", "Number(data.quantity) ** 999999 > 0")])
def test_native_expression_rejects_side_effects(suffix, expression):
    with pytest.raises((ValueError, SyntaxError)):
        validate_expression(expression, suffix, ["quantity"])


def test_native_file_edit_cannot_change_envelope():
    path = "business-rules.vue"
    source = (ROOT / "tools/node/templates/rule.vue.hbs").read_text()
    blocks = path + "\n<<<<<<< SEARCH\n" + source.rstrip() + "\n=======\n" + source.replace("export function", "export async function").rstrip() + "\n>>>>>>> REPLACE\n"
    with pytest.raises(ValueError, match="outside"):
        preview(path, source, blocks, ["quantity"])


def test_native_rollback_preserves_external_changes(tmp_path):
    path = tmp_path / "business-rules.vue"
    path.write_text("external edit")
    with pytest.raises(Exception, match="changed"):
        rollback(tmp_path, {"after": {"business-rules.vue": "0" * 64}}, {"business-rules.vue": "old"})
    assert path.read_text() == "external edit"


@pytest.mark.node_tools
@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_actual_plop_native_mount_and_no_overwrite(tmp_path, template):
    if not (ROOT / "tools/node/node_modules/node-plop").is_dir():
        import os
        if os.getenv("RND_REQUIRE_NODE_TESTS") == "1":
            pytest.fail("required node-plop is not installed")
        pytest.skip("optional local node-plop not installed")
    product = native_product(tmp_path / "product", template)
    report = scaffold_native_rules(template, rule_plan(), product, tmp_path / "reports")
    assert report["engine"] == "node-plop" and report["network"] == "disabled"
    assert len(report["editable"]) == 2
    for name in report["editable"]:
        assert region((product / name).read_text())[1] in {"true", "True"}
    assert scaffold_native_rules(template, rule_plan(), product, tmp_path / "reports") == report
    assert json.loads(report["log"])["actions"] >= 5
    with pytest.raises(FileExistsError):
        scaffold_native_rules(template, rule_plan(), product, tmp_path / "other-reports")


def test_native_failure_with_missing_editor_is_not_crud_success(tmp_path):
    from workbench.native_lab import run_acceptance
    with pytest.raises(ValueError, match="Aider"):
        run_acceptance("yudao-vben", tmp_path, tmp_path / "out", tmp_path, "", tmp_path, rule_plan())


def test_native_partial_patch_missing_frontend_is_rejected(tmp_path, settings):
    from workbench.native_coding import apply_native_edits
    path = "rules.py"; atomic_text(tmp_path / path, "untouched")
    value = NativeEdits(files=[{"path": path, "before_sha256": sha(tmp_path / path), "blocks": "invalid"}], explanation="test")
    with pytest.raises(ValueError, match="Every registered"):
        apply_native_edits(tmp_path, value, [path, "form.vue"], {}, settings, tmp_path / "reports", 0)
    assert (tmp_path / path).read_text() == "untouched"
