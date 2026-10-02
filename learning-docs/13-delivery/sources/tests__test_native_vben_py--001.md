# tests/test_native_vben.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.native_environment`、`workbench.native_vben`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_checked_replacement_is_exact_and_preserves_unrelated_source`（L21–L24）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L23断言`checked_replacement(source, "old", "new", 1, "fixture") == "before; new; after;"`；L24断言`source == "before; old; after;"`。 调用`checked_replacement`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changed_or_ambiguous_upstream_context_fails_closed`（L28–L30）：接收`source`。 调用`pytest.raises`、`checked_replacement`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_vben_boundary_is_local_and_excluded_from_delivery`（L33–L51）：接收`tmp_path`。 控制顺序：L43断言`manifest(destination) == before`；L44断言`not (destination / ".env").exists()`；L46断言`"remote" not in config and "never-copy" not in config`；L47断言`not (destination / ".git/hooks").exists()`；L49断言`Path(result["log"].strip()).resolve() == destination.resolve()`。 调用`(source / ".git").mkdir`、`(source / ".git/config").write_text`、`(source / ".env").write_text`、`(source / "package.json").write_text`、`json.dumps`、`copy_source`、`manifest`、`initialize_vben_boundary`、`(destination / ".env").exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_modal_keeps_precise_dto_and_optional_create_payload`（L55–L67）：接收`class_name`。 控制顺序：L63断言`f"useVbenModal<Partial<{dto}>>(" in result`；L64断言`"modalApi.getData()" in result`；L65断言`"if (!data \|\| !data.id) return;" in result`；L66断言`"getData<" in source`；L67断言`"@ts-ignore" not in result and "any" not in result`。 调用`adapt_generated_form`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generated_modal_contract_drift_is_not_silently_accepted`（L70–L72）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`adapt_generated_form`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pruning_never_removes_an_import_still_used`（L82–L90）：接收`identifier`、`line`。 控制顺序：L83断言`prune_generated_import(line + "const unrelated = 1;", identifier, line) == "const unr…`；L88断言`prune_generated_import(used, identifier, line) == used`。 调用`prune_generated_import`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `schema_field`（L93–L100）：接收`name`、`component`、`options`。 返回路径：L94的`" {\n" + f" fieldName: '{name}',\n label: '{name}',\n" + f" component: '{component}',\n co…`。
- `test_generated_schema_preserves_zero_false_and_all_fields`（L103–L126）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L120断言`result.count("fieldName:") == source.count("fieldName:") == 4`；L121断言`result.count("component: 'InputNumber'") == 2`；L122断言`result.count("precision: 0") == 2`；L123断言`result.count("component: 'RadioGroup'") == 2`；L124断言`result.count("value: false") == result.count("value: true") == 2`；L125断言`"value: 'false'" not in result`；L126断言`"options: []" in source and "options: []" not in result`。 调用`schema_field`、`adapt_generated_schema`、`FieldSpec`、`result.count`、`source.count`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_generated_boolean_shape_fails_closed`（L130–L132）：接收`source`。 调用`pytest.raises`、`adapt_generated_schema`、`FieldSpec`、`pytest.mark.parametrize`、`schema_field`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_scalar_controls_are_not_misclassified_as_boolean`（L139–L147）：接收`kind`、`component`。 控制顺序：L147断言`adapt_generated_schema(original, [field]) == original`。 调用`FieldSpec`、`schema_field`、`adapt_generated_schema`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_fields_preserved_while_classic_boolean_guard_still_runs`（L150–L164）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L159断言`schema_field("category", "Input") in result`；L160断言`result.count("component: 'RadioGroup'") == 1`。 调用`schema_field`、`adapt_generated_schema`、`FieldSpec`、`result.count`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_vben.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L164。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6550`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_vben.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6ebfa7ae003951f2cb572539e621c8f4c549742542b420be2e6eecef75b1ca56"} -->
````python
# tests/test_native_vben.py
"""Small regression contracts; full Vben verification uses the real pinned application."""

import json
from pathlib import Path

import pytest

from workbench.domain import FieldSpec
from workbench.filesystem import manifest
from workbench.native_environment import copy_source
from workbench.native_vben import (
    adapt_generated_form,
    adapt_generated_schema,
    checked_replacement,
    initialize_vben_boundary,
    prune_generated_import,
)
from workbench.tools import run_command


def test_checked_replacement_is_exact_and_preserves_unrelated_source():
    source = "before; old; after;"
    assert checked_replacement(source, "old", "new", 1, "fixture") == "before; new; after;"
    assert source == "before; old; after;"


@pytest.mark.parametrize("source", ["missing", "old old"])
def test_changed_or_ambiguous_upstream_context_fails_closed(source):
    with pytest.raises(ValueError, match="compatibility contract changed"):
        checked_replacement(source, "old", "new", 1, "fixture")


def test_vben_boundary_is_local_and_excluded_from_delivery(tmp_path):
    source = tmp_path / "upstream"
    (source / ".git").mkdir(parents=True)
    (source / ".git/config").write_text("never-copy-upstream-credentials", encoding="utf-8")
    (source / ".env").write_text("API_KEY=never-copy-me", encoding="utf-8")
    (source / "package.json").write_text(json.dumps({"name": "boundary-fixture"}), encoding="utf-8")
    destination = tmp_path / "product"
    copy_source(source, destination)
    before = manifest(destination)
    initialize_vben_boundary(destination)
    assert manifest(destination) == before
    assert not (destination / ".env").exists()
    config = (destination / ".git/config").read_text(encoding="utf-8")
    assert "remote" not in config and "never-copy" not in config
    assert not (destination / ".git/hooks").exists()
    result = run_command(["git", "rev-parse", "--show-toplevel"], destination, 30)
    assert Path(result["log"].strip()).resolve() == destination.resolve()
    with pytest.raises(ValueError, match="fresh source copy"):
        initialize_vben_boundary(destination)


@pytest.mark.parametrize("class_name", ["WbDevice", "WbCategory", "WbAssetItem"])
def test_generated_modal_keeps_precise_dto_and_optional_create_payload(class_name):
    dto = f"Infra{class_name}Api.{class_name}"
    source = (
        "const [Modal, modalApi] = useVbenModal({\n"
        f"const data = modalApi.getData<{dto}>();\n"
        "if (!data || !data.id) return;\n});"
    )
    result = adapt_generated_form(source, class_name)
    assert f"useVbenModal<Partial<{dto}>>(" in result
    assert "modalApi.getData()" in result
    assert "if (!data || !data.id) return;" in result
    assert "getData<" in source
    assert "@ts-ignore" not in result and "any" not in result


def test_generated_modal_contract_drift_is_not_silently_accepted():
    with pytest.raises(ValueError, match="compatibility contract changed"):
        adapt_generated_form("const [Modal, modalApi] = useVbenModal({});", "WbDevice")


@pytest.mark.parametrize(
    "identifier,line",
    [
        ("Dayjs", "import type { Dayjs } from 'dayjs';\n"),
        ("getDictOptions", "import { getDictOptions } from '@vben/hooks';\n"),
    ],
)
def test_pruning_never_removes_an_import_still_used(identifier, line):
    assert (
        prune_generated_import(line + "const unrelated = 1;", identifier, line)
        == "const unrelated = 1;"
    )
    used = line + f"const value = {identifier};"
    assert prune_generated_import(used, identifier, line) == used
    with pytest.raises(ValueError, match="Duplicate"):
        prune_generated_import(line + line, identifier, line)


def schema_field(name, component, options=False):
    return (
        "    {\n"
        + f"      fieldName: '{name}',\n      label: '{name}',\n"
        + f"      component: '{component}',\n      componentProps: {{\n"
        + ("        options: [],\n" if options else "        placeholder: 'value',\n")
        + "      },\n    },"
    )


def test_generated_schema_preserves_zero_false_and_all_fields():
    source = (
        schema_field("itemCount", "Input")
        + "\n"
        + schema_field("enabled", "RadioGroup", True)
        + "\n"
        + schema_field("itemCount", "Input")
        + "\n"
        + schema_field("enabled", "Select", True)
    )
    result = adapt_generated_schema(
        source,
        [
            FieldSpec(name="item_count", kind="integer"),
            FieldSpec(name="enabled", kind="boolean"),
        ],
    )
    assert result.count("fieldName:") == source.count("fieldName:") == 4
    assert result.count("component: 'InputNumber'") == 2
    assert result.count("precision: 0") == 2
    assert result.count("component: 'RadioGroup'") == 2
    assert result.count("value: false") == result.count("value: true") == 2
    assert "value: 'false'" not in result
    assert "options: []" in source and "options: []" not in result


@pytest.mark.parametrize("source", ["", schema_field("enabled", "Switch", True)])
def test_unknown_generated_boolean_shape_fails_closed(source):
    with pytest.raises(ValueError, match="Unsupported generated"):
        adapt_generated_schema(source, [FieldSpec(name="enabled", kind="boolean")])


@pytest.mark.parametrize(
    "kind,component",
    [("enum", "Input"), ("enum", "Select"), ("date", "DatePicker"), ("datetime", "DatePicker")],
)
def test_business_scalar_controls_are_not_misclassified_as_boolean(kind, component):
    field = FieldSpec(
        name="category" if kind == "enum" else "due_at",
        kind=kind,
        choices=["a", "b"] if kind == "enum" else [],
    )
    name = "category" if kind == "enum" else "dueAt"
    original = schema_field(name, component, component == "Select")
    assert adapt_generated_schema(original, [field]) == original


def test_business_fields_preserved_while_classic_boolean_guard_still_runs():
    source = schema_field("category", "Input") + "\n" + schema_field("enabled", "Select", True)
    result = adapt_generated_schema(
        source,
        [
            FieldSpec(name="category", kind="enum", choices=["a", "b"]),
            FieldSpec(name="enabled", kind="boolean"),
        ],
    )
    assert schema_field("category", "Input") in result
    assert result.count("component: 'RadioGroup'") == 1
    with pytest.raises(ValueError, match="Unsupported generated boolean control"):
        adapt_generated_schema(
            schema_field("enabled", "Input"), [FieldSpec(name="enabled", kind="boolean")]
        )
````
