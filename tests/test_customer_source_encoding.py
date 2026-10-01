"""Keep customer acceptance source and fixture reads independent of the OS locale."""

import ast

import pytest

from workbench.settings import ROOT

# These acceptance modules consume UTF-8 repository sources, generated JSON, or
# handbooks. Runtime readers of arbitrary external files are deliberately excluded.
SOURCE_READERS = (
    "scripts/build_handbook.py",
    "scripts/ci_handbook.py",
    "scripts/ci_real_model.py",
    "scripts/handbook_notes.py",
    "scripts/rebuild_from_handbook.py",
    "templates/product/verify_business.py",
    "tests/test_business_browser_evidence.py",
    "tests/test_business_query_api.py",
    "tests/test_business_query_browser.py",
    "tests/test_business_query_evidence_contract.py",
    "tests/test_handbook.py",
    "tests/test_handbook_customer.py",
    "tests/test_native_browser_navigation.py",
    "tests/test_real_model_execution_diagnostics.py",
    "workbench/verification.py",
)


def unqualified_text_reads(source):
    """Find locale-sensitive pathlib/builtin text reads in the bounded source set."""
    missing = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        keywords = {keyword.arg: keyword.value for keyword in node.keywords}
        if isinstance(function, ast.Attribute) and function.attr == "read_text":
            encoding_position = 0
        elif (
            isinstance(function, ast.Attribute)
            and function.attr == "open"
            or isinstance(function, ast.Name)
            and function.id == "open"
        ):
            mode_position = 1 if isinstance(function, ast.Name) else 0
            mode = keywords.get("mode")
            if mode is None and len(node.args) > mode_position:
                mode = node.args[mode_position]
            if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
                if "b" in mode.value or not ("r" in mode.value or "+" in mode.value):
                    continue
            encoding_position = mode_position + 2
        else:
            continue
        encoding = keywords.get("encoding")
        if encoding is None and len(node.args) > encoding_position:
            encoding = node.args[encoding_position]
        if not (
            isinstance(encoding, ast.Constant)
            and isinstance(encoding.value, str)
            and encoding.value.lower().replace("-", "").replace("_", "") in {"utf8", "utf8sig"}
        ):
            missing.append(node.lineno)
    return missing


@pytest.mark.parametrize(
    "name",
    sorted(
        set(SOURCE_READERS)
        | {path.relative_to(ROOT).as_posix() for path in (ROOT / "tests").glob("test_customer*.py")}
    ),
)
def test_customer_source_and_fixture_reads_explicitly_use_utf8(name):
    source = (ROOT / name).read_text(encoding="utf-8")
    assert not unqualified_text_reads(source), f"{name}: unqualified text reads"


@pytest.mark.parametrize(
    "source",
    [
        "path.read_text()",
        "path.read_text(encoding=None)",
        "path.read_text(encoding='cp1252')",
        "path.open()",
        "path.open('r')",
        "open('source.py')",
        "open('source.py', mode='r')",
    ],
)
def test_encoding_guard_rejects_locale_dependent_reads(source):
    assert unqualified_text_reads(source) == [1]


@pytest.mark.parametrize(
    "source",
    [
        "path.read_text(encoding='utf-8')",
        "path.read_text('utf-8')",
        "path.open(encoding='utf-8')",
        "path.open('r', -1, 'utf-8')",
        "open('source.py', encoding='utf-8')",
        "open('source.py', 'r', -1, 'utf-8')",
        "path.open('rb')",
        "open('source.py', 'rb')",
        "path.open('wb')",
    ],
)
def test_encoding_guard_allows_explicit_utf8_and_binary_reads(source):
    assert unqualified_text_reads(source) == []
