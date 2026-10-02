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
