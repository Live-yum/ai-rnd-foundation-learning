"""Keep customer acceptance source and fixture reads independent of the OS locale."""

import ast

import pytest

from workbench.settings import ROOT

# These acceptance modules consume UTF-8 repository sources, generated JSON, or
# handbooks. Runtime readers of arbitrary external files are deliberately excluded.
SOURCE_READERS = (
    "scripts/build_handbook.py",
    "scripts/ci_handbook.py",
    "scripts/ci_native_bundled.py",
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
    "tests/test_native_business_query_browser.py",
    "tests/test_native_backend_failure_diagnostics.py",
    "tests/test_native_delivery_diagnostics.py",
    "tests/test_native_relation_picker_browser.py",
    "tests/test_real_model_execution_diagnostics.py",
    "workbench/verification.py",
    "workbench/filesystem.py",
    "workbench/native_delivery.py",
    "workbench/native_environment.py",
    "workbench/native_lab.py",
    "workbench/portable.py",
    "tests/test_native_archive_limits.py",
    "tests/test_native_approved_replay.py",
    "tests/test_semantic_fact_domains.py",
    "tests/test_semantic_fact_namespace_aliases.py",
    "workbench/model_protocol.py",
    "workbench/native_business_probe.py",
    "workbench/native_evidence.py",
    "tests/test_native_business_probes.py",
    "tests/test_native_review_evidence.py",
    "tests/test_yudao_business_queries.py",
    "workbench/llm.py",
)


def unqualified_text_reads(source):
    """Find locale-sensitive pathlib/builtin text reads in the bounded source set."""
    missing = []
    tree = ast.parse(source)
    zip_modules = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name == "zipfile"
    }
    zip_scopes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            for item in node.items:
                call = item.context_expr
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id in zip_modules
                    and call.func.attr == "ZipFile"
                    and isinstance(item.optional_vars, ast.Name)
                ):
                    zip_scopes.append((item.optional_vars.id, node.lineno, node.end_lineno))
    for node in ast.walk(tree):
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
            # ZipFile.open returns bytes and has no encoding parameter. Limit
            # the exception to a directly identified constructor's with-scope.
            if isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name):
                if any(
                    function.value.id == name and start <= node.lineno <= end
                    for name, start, end in zip_scopes
                ):
                    continue
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


def test_encoding_guard_distinguishes_zip_binary_open_from_path_open():
    assert (
        unqualified_text_reads(
            "import zipfile\nwith zipfile.ZipFile('source.zip') as z:\n z.open('app.py')"
        )
        == []
    )
    assert (
        unqualified_text_reads(
            "import zipfile as zip_module\nwith zip_module.ZipFile('source.zip') as z:\n z.open('app.py')"
        )
        == []
    )
    assert unqualified_text_reads("path.open()") == [1]
    assert unqualified_text_reads(
        "import zipfile\nwith zipfile.ZipFile('source.zip') as z:\n z.open('app.py')\nz.open()"
    ) == [4]
