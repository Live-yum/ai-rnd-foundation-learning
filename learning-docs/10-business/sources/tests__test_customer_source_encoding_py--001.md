# tests/test_customer_source_encoding.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `unqualified_text_reads`（L70–L135）：接收`source`。 源码说明：Find locale-sensitive pathlib/builtin text reads in the bounded source set.。 控制顺序：L82遍历`ast.walk(tree)`；L83按`isinstance(node, ast.With)`分支；L84遍历`node.items`；L86按`isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and isinstance(ca…`分支；L95遍历`ast.walk(tree)`；L96按`not isinstance(node, ast.Call)`分支；L100按`isinstance(function, ast.Attribute) and function.attr == "read_text"`分支；L102按`isinstance(function, ast.Attribute) and function.attr == "open" or isinstance(functio…`分支。后续分支沿下方源码相同行号继续阅读。 调用`ast.parse`、`ast.walk`、`isinstance`、`zip_scopes.append`、`any`、`keywords.get`、`len`、`encoding.value.lower().replace("-", "").replace`、`encoding.value.lower().replace`等。 返回路径：L135的`missing`。
- `test_customer_source_and_fixture_reads_explicitly_use_utf8`（L145–L147）：接收`name`。 控制顺序：L147断言`not unqualified_text_reads(source)`。 调用`(ROOT / name).read_text`、`unqualified_text_reads`、`pytest.mark.parametrize`、`sorted`、`set`、`path.relative_to(ROOT).as_posix`、`path.relative_to`、`(ROOT / "tests").glob`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reload_fixture_decodes_utf8_child_output_independently_of_windows_locale`（L150–L165）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L161断言`len(calls) == 2`；L162遍历`calls`；L164断言`isinstance(keywords.get("encoding"), ast.Constant)`；L165断言`keywords["encoding"].value == "utf-8"`。 调用`(ROOT / "tests/test_product_reload_readiness.py").read_text`、`ast.walk`、`ast.parse`、`isinstance`、`len`、`keywords.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_encoding_guard_rejects_locale_dependent_reads`（L180–L181）：接收`source`。 控制顺序：L181断言`unqualified_text_reads(source) == [1]`。 调用`unqualified_text_reads`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_encoding_guard_allows_explicit_utf8_and_binary_reads`（L198–L199）：接收`source`。 控制顺序：L199断言`unqualified_text_reads(source) == []`。 调用`unqualified_text_reads`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_encoding_guard_distinguishes_zip_binary_open_from_path_open`（L202–L218）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L203断言`unqualified_text_reads( "import zipfile\nwith zipfile.ZipFile('source.zip') as z:\n z…`；L209断言`unqualified_text_reads( "import zipfile as zip_module\nwith zip_module.ZipFile('sourc…`；L215断言`unqualified_text_reads("path.open()") == [1]`；L216断言`unqualified_text_reads( "import zipfile\nwith zipfile.ZipFile('source.zip') as z:\n z…`。 调用`unqualified_text_reads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_customer_source_encoding.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L218。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8285`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_customer_source_encoding.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f3c0d3b047ee9d617a0b964cb30a374171c02bcad9354cdf71e69216e2148435"} -->
````python
# tests/test_customer_source_encoding.py
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
    "tests/test_native_fastapi_screenshot_readiness.py",
    "tests/test_native_login_readiness.py",
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
    "tests/test_native_projection_gate.py",
    "tests/test_requirement_clause_semantics.py",
    "tests/test_entity_group_clause_scope.py",
    "tests/test_permission_contract_equivalence.py",
    "tests/test_permission_analysis_contract.py",
    "tests/test_query_obligation_pairing.py",
    "tests/test_requirement_source_conflicts.py",
    "tests/test_real_model_source_conflict_diagnostics.py",
    "workbench/requirement_sources.py",
    "workbench/yudao_navigation.py",
    "workbench/yudao_navigation_checks.py",
    "tests/test_yudao_installed_navigation.py",
    "tests/test_yudao_navigation_evidence.py",
    "tests/test_yudao_navigation_browser.py",
    "tests/test_yudao_screenshot_readiness.py",
    "tests/test_handbook_runtime.py",
    "tests/test_product_reload_readiness.py",
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


def test_reload_fixture_decodes_utf8_child_output_independently_of_windows_locale():
    source = (ROOT / "tests/test_product_reload_readiness.py").read_text(encoding="utf-8")
    calls = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(calls) == 2
    for call in calls:
        keywords = {keyword.arg: keyword.value for keyword in call.keywords}
        assert isinstance(keywords.get("encoding"), ast.Constant)
        assert keywords["encoding"].value == "utf-8"


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
````
