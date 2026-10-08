# tests/test_native_tools.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_native_generated`、`workbench.domain`、`workbench.filesystem`、`workbench.native_coding`、`workbench.scaffolding`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `rule_plan`（L15–L28）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`acceptance_spec`、`CustomRule`。 返回路径：L28的`plan`。
- `native_product`（L31–L52）：接收`root`、`template`。 控制顺序：L32按`template == "fastapiadmin"`分支。 调用`atomic_text`。 返回路径：L52的`root`。
- `test_native_expression_languages`（L63–L64）：接收`suffix`、`expression`。 调用`validate_expression`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_expression_rejects_side_effects`（L84–L86）：接收`suffix`、`expression`。 调用`pytest.raises`、`validate_expression`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_file_edit_cannot_change_envelope`（L89–L101）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`(ROOT / "tools/node/templates/rule.vue.hbs").read_text`、`source.rstrip`、`source.replace("export function", "export async function").rstrip`、`source.replace`、`pytest.raises`、`preview`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_rollback_preserves_external_changes`（L104–L111）：接收`tmp_path`。 控制顺序：L111断言`path.read_text() == "external edit"`。 调用`path.write_text`、`pytest.raises`、`rollback`、`path.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_plop_native_mount_and_no_overwrite`（L116–L132）：接收`tmp_path`、`template`。 控制顺序：L117按`not (ROOT / "tools/node/node_modules/node-plop").is_dir()`分支；L120按`os.getenv("RND_REQUIRE_NODE_TESTS") == "1"`分支；L125断言`report["engine"] == "node-plop" and report["network"] == "disabled"`；L126断言`len(report["editable"]) == 2`；L127遍历`report["editable"]`；L128断言`region((product / name).read_text())[1] in {"true", "True"}`；L129断言`scaffold_native_rules(template, rule_plan(), product, tmp_path / "reports") == report`；L130断言`json.loads(report["log"])["actions"] >= 5`。 调用`(ROOT / "tools/node/node_modules/node-plop").is_dir`、`os.getenv`、`pytest.fail`、`pytest.skip`、`native_product`、`scaffold_native_rules`、`rule_plan`、`len`、`region`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_failure_with_missing_editor_is_not_crud_success`（L135–L145）：接收`tmp_path`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`run_acceptance`、`rule_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_partial_patch_missing_frontend_is_rejected`（L148–L161）：接收`tmp_path`、`settings`。 控制顺序：L161断言`(tmp_path / path).read_text() == "untouched"`。 调用`atomic_text`、`NativeEdits`、`sha`、`pytest.raises`、`apply_native_edits`、`(tmp_path / path).read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_java_unicode_escape_cannot_bypass_expression_lexer`（L164–L170）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`validate_expression`、`chr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_tools.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L170。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6864`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_tools.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b46bc8d46f89a716b62a97586fbcc8427e5a855090570c59f2f0ae049d4d13da"} -->
````python
# tests/test_native_tools.py
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
    plan.custom_rules = [
        CustomRule(
            description="quantity must be nonnegative",
            entity="device",
            accept_examples=[
                {"name": "device-rule", "quantity": 0, "active": False},
                {"name": "device-rule-2", "quantity": 7, "active": True},
            ],
            reject_examples=[{"name": "device-rule", "quantity": -1, "active": False}],
        )
    ]
    return plan


def native_product(root, template):
    if template == "fastapiadmin":
        module = root / "backend/app/plugin/module_rnd/device"
        atomic_text(
            module / "schema.py",
            "from pydantic import BaseModel\nclass DeviceCreateSchema(BaseModel):\n    quantity: int\n\nclass DeviceUpdateSchema(BaseModel):\n    quantity: int\n\nclass DeviceOutSchema(DeviceCreateSchema):\n    pass\n",
        )
        form = root / "frontend/web/src/views/module_rnd/device/index.vue"
        body = '<script lang="ts" setup>\nasync function handleSubmit() {\n  await crud.handleSubmit();\n}\n</script>\n<template>\n        <FaForm />\n</template>\n'
    else:
        module = (
            root
            / "backend/yudao-module-infra/yudao-module-infra-server/src/main/java/cn/iocoder/yudao/module/infra/controller/admin/wbdevice/vo"
        )
        atomic_text(
            module / "WbDeviceSaveReqVO.java",
            "package cn.iocoder.yudao.module.infra.controller.admin.wbdevice.vo;\npublic class WbDeviceSaveReqVO { }\n",
        )
        form = root / "frontend-product/apps/web-antd/src/views/infra/wbdevice/modules/form.vue"
        body = '<script lang="ts" setup>\nconst modal = {async onConfirm() {\n    try {\n      await (formData.value?.id ? update(data) : create(data));\n    } finally {}\n}};\n</script>\n<template>\n  <Modal :title="getTitle"><Form /></Modal>\n</template>\n'
    atomic_text(form, body)
    return root


@pytest.mark.parametrize(
    "suffix,expression",
    [
        (".py", 'data["quantity"] >= 0'),
        (".java", "quantity == null || quantity >= 0"),
        (".vue", "Number(data.quantity) >= 0"),
    ],
)
def test_native_expression_languages(suffix, expression):
    validate_expression(expression, suffix, ["quantity"])


@pytest.mark.parametrize(
    "suffix,expression",
    [
        (".py", "__import__('os').system('id')"),
        (".py", "data['unknown'] > 0"),
        (".java", 'Runtime.getRuntime().exec("id")'),
        (".java", "quantity = 0"),
        (".java", "quantity++ > 0"),
        (".java", "new Boolean(true)"),
        (".java", "quantity.getClass() != null"),
        (".vue", "globalThis.fetch('remote')"),
        (".vue", "data.quantity = 0"),
        (".vue", "data.constructor.constructor('return process')()"),
        (".vue", "(() => true)()"),
        (".vue", "Number(data.quantity) ** 999999 > 0"),
    ],
)
def test_native_expression_rejects_side_effects(suffix, expression):
    with pytest.raises((ValueError, SyntaxError)):
        validate_expression(expression, suffix, ["quantity"])


def test_native_file_edit_cannot_change_envelope():
    path = "business-rules.vue"
    source = (ROOT / "tools/node/templates/rule.vue.hbs").read_text()
    blocks = (
        path
        + "\n<<<<<<< SEARCH\n"
        + source.rstrip()
        + "\n=======\n"
        + source.replace("export function", "export async function").rstrip()
        + "\n>>>>>>> REPLACE\n"
    )
    with pytest.raises(ValueError, match="outside"):
        preview(path, source, blocks, ["quantity"])


def test_native_rollback_preserves_external_changes(tmp_path):
    path = tmp_path / "business-rules.vue"
    path.write_text("external edit")
    with pytest.raises(Exception, match="changed"):
        rollback(
            tmp_path, {"after": {"business-rules.vue": "0" * 64}}, {"business-rules.vue": "old"}
        )
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


def test_native_failure_with_missing_editor_is_not_crud_success(tmp_path, monkeypatch):
    from workbench.native_lab import run_acceptance

    monkeypatch.setattr(
        "workbench.native_lab.backend_port_lease",
        lambda *_: pytest.fail("Invalid input must fail before leasing host resources"),
    )
    with pytest.raises(ValueError, match="Aider"):
        run_acceptance(
            "yudao-vben", tmp_path, tmp_path / "out", tmp_path, "", tmp_path, rule_plan()
        )


def test_native_partial_patch_missing_frontend_is_rejected(tmp_path, settings):
    from workbench.native_coding import apply_native_edits

    path = "rules.py"
    atomic_text(tmp_path / path, "untouched")
    value = NativeEdits(
        files=[{"path": path, "before_sha256": sha(tmp_path / path), "blocks": "invalid"}],
        explanation="test",
    )
    with pytest.raises(ValueError, match="Every registered"):
        apply_native_edits(
            tmp_path, value, [path, "form.vue"], {}, settings, tmp_path / "reports", 0
        )
    assert (tmp_path / path).read_text() == "untouched"


def test_java_unicode_escape_cannot_bypass_expression_lexer():
    with pytest.raises(ValueError, match="Unicode"):
        validate_expression(
            chr(34) + chr(92) + "u0061" + chr(34) + ".equals(" + chr(34) + "a" + chr(34) + ")",
            ".java",
            [],
        )
````
