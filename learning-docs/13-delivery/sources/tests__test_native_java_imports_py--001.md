# tests/test_native_java_imports.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.native_compatibility`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_actual_native_date_exports_keep_provenance_and_declarations`（L13–L20）：接收`path`。 控制顺序：L15断言`"private LocalDate publishedOn;" in source`；L16断言`"import java.time.LocalDate;" not in source`；L18断言`fixed.count("import java.time.LocalDate;") == 1`；L19断言`fixed.replace("\nimport java.time.LocalDate;", "") == source`；L20断言`prepare_java_time_imports(fixed) == fixed`。 调用`path.read_text`、`prepare_java_time_imports`、`fixed.count`、`fixed.replace`、`pytest.mark.parametrize`、`sorted`、`FIXTURES.glob`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_date_types_are_repaired_only_as_unqualified_field_declarations`（L25–L30）：接收`type_name`、`array`。 控制顺序：L28断言`f"import java.time.{type_name};" in fixed`；L29断言`fixed.replace(f"\nimport java.time.{type_name};", "") == source`；L30断言`prepare_java_time_imports(fixed) == fixed`。 调用`prepare_java_time_imports`、`fixed.replace`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_no_imports_from_non_code_or_qualified_types`（L45–L47）：接收`body`。 控制顺序：L47断言`prepare_java_time_imports(source) == source`。 调用`prepare_java_time_imports`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_or_shadowed_types_are_not_overridden`（L61–L63）：接收`imports`。 控制顺序：L63断言`prepare_java_time_imports(source) == source`。 调用`prepare_java_time_imports`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_literal_with_escaped_quotes_does_not_introduce_import`（L66–L68）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L68断言`prepare_java_time_imports(source) == source`。 调用`prepare_java_time_imports`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_crlf_is_preserved_and_missing_package_fails_closed`（L71–L77）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L73断言`prepare_java_time_imports(source) == source.replace( "package demo;", "package demo;\…`。 调用`prepare_java_time_imports`、`source.replace`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ast_handles_inline_declarations_and_multibyte_prefix_offsets`（L80–L84）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L82断言`prepare_java_time_imports(source) == source.replace( "package demo;", "package demo;\…`。 调用`prepare_java_time_imports`、`source.replace`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generic_type_shadow_is_not_rebound_to_java_time`（L87–L89）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L89断言`prepare_java_time_imports(source) == source`。 调用`prepare_java_time_imports`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_generated_java_does_not_get_silently_repaired`（L92–L94）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`prepare_java_time_imports`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_java_imports.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L94。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3800`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_java_imports.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "90bdff600d22f499be1a4aab80216388662f6cb0811af9a4e4165061fa787c28"} -->
````python
# tests/test_native_java_imports.py
"""Actual native date export and lexical boundaries for a recorded import repair."""

from pathlib import Path

import pytest

from workbench.native_compatibility import prepare_java_time_imports

FIXTURES = Path(__file__).parent / "fixtures/yudao-native-date"


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("*.java")), ids=lambda p: p.name)
def test_actual_native_date_exports_keep_provenance_and_declarations(path):
    source = path.read_text(encoding="utf-8")
    assert "private LocalDate publishedOn;" in source
    assert "import java.time.LocalDate;" not in source
    fixed = prepare_java_time_imports(source)
    assert fixed.count("import java.time.LocalDate;") == 1
    assert fixed.replace("\nimport java.time.LocalDate;", "") == source
    assert prepare_java_time_imports(fixed) == fixed


@pytest.mark.parametrize("type_name", ["LocalDate", "LocalDateTime"])
@pytest.mark.parametrize("array", ["", "[]", " [] "])
def test_date_types_are_repaired_only_as_unqualified_field_declarations(type_name, array):
    source = f"package demo;\nclass Entry {{\n    private {type_name}{array} value;\n}}\n"
    fixed = prepare_java_time_imports(source)
    assert f"import java.time.{type_name};" in fixed
    assert fixed.replace(f"\nimport java.time.{type_name};", "") == source
    assert prepare_java_time_imports(fixed) == fixed


@pytest.mark.parametrize(
    "body",
    [
        "// private LocalDate value;",
        "/*\nprivate LocalDate value;\n*/",
        'String text = "private LocalDate value;";',
        'String text = """\nprivate LocalDate value;\n""";',
        "char quote = '\"'; // LocalDate value;",
        "private java.time.LocalDate value;",
        "private LocalDateTime value;",
    ],
)
def test_no_imports_from_non_code_or_qualified_types(body):
    source = "package demo;\nimport java.time.LocalDateTime;\nclass Entry {\n" + body + "\n}\n"
    assert prepare_java_time_imports(source) == source


@pytest.mark.parametrize(
    "imports",
    [
        "import java.time.LocalDate;",
        "import java.time.*;",
        "import example.LocalDate;",
        "import java.time./* native comment */LocalDate;",
        "import static example.Types.LocalDate;",
        "class LocalDate {}",
    ],
)
def test_existing_or_shadowed_types_are_not_overridden(imports):
    source = f"package demo;\n{imports}\nclass Entry {{\nprivate LocalDate value;\n}}"
    assert prepare_java_time_imports(source) == source


def test_literal_with_escaped_quotes_does_not_introduce_import():
    source = 'package demo;\nclass Entry { String x = "\\"\\nprivate LocalDate value;"; }'
    assert prepare_java_time_imports(source) == source


def test_crlf_is_preserved_and_missing_package_fails_closed():
    source = "package demo;\r\nclass Entry {\r\nprivate LocalDate value;\r\n}\r\n"
    assert prepare_java_time_imports(source) == source.replace(
        "package demo;", "package demo;\r\nimport java.time.LocalDate;"
    )
    with pytest.raises(ValueError, match="package"):
        prepare_java_time_imports("class Entry {\nprivate LocalDate value;\n}")


def test_ast_handles_inline_declarations_and_multibyte_prefix_offsets():
    source = "/* 客服 */ package demo; class Entry { private LocalDate value; }"
    assert prepare_java_time_imports(source) == source.replace(
        "package demo;", "package demo;\nimport java.time.LocalDate;"
    )


def test_generic_type_shadow_is_not_rebound_to_java_time():
    source = "package demo; class Entry<LocalDate> { private LocalDate value; }"
    assert prepare_java_time_imports(source) == source


def test_invalid_generated_java_does_not_get_silently_repaired():
    with pytest.raises(ValueError, match="syntax"):
        prepare_java_time_imports("package demo; class Entry { private LocalDate value;")
````
