# workbench/symbols.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：从真实语法树提取代码符号。** Python使用标准库AST；Java、TS、JS使用固定grammar的Tree-sitter。Vue先定位SFC中的script与模板标签，再给script节点补上原文件行偏移。提取的是声明、继承和注解等结构，不把文件名当作函数解析结果。

**对应关系：** knowledge.build_index → parse_file → declarations；test_toolchain及ci_toolchain。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `parser_identity`（L48–L49）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`version`、`lru_cache`。 返回路径：L49的`{name: version(name) for name in PACKAGES}`。
- `parser`（L52–L58）：接收`language`。 调用`importlib.import_module`、`{"typescript": "language_typescript", "tsx": "language_tsx"}.get`、`Parser`、`Language`、`getattr(module, factory)`、`getattr`。 返回路径：L58的`Parser(Language(getattr(module, factory)()))`。
- `walk`（L61–L66）：接收`node`。 控制顺序：L63在`stack`成立时循环。 调用`stack.pop`、`stack.extend`、`reversed`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `text`（L69–L72）：接收`node`、`data`、`limit`。 控制顺序：L70按`node is None`分支。 调用`data[node.start_byte : node.end_byte].decode`。 返回路径：L71的`""`；L72的`data[node.start_byte : node.end_byte].decode("utf-8", errors="replace")[:limit]`。
- `declarations`（L75–L120）：接收`data`、`language`、`offset`。 控制顺序：L78遍历`walk(tree.root_node)`；L79按`node.type in IMPORTS`分支；L81按`node.type not in DECLARATIONS`分支；L84按`node.type == "field_declaration"`分支；L89按`name is None`分支。 调用`parser(language).parse`、`parser`、`walk`、`imports.append`、`text`、`node.child_by_field_name`、`next`、`declarator.child_by_field_name`、`data[node.start_byte : end].decode`等。 返回路径：L120的`{"symbols": symbols, "imports": imports, "parse_error": tree.root_node.has_error}`。
- `parse_file`（L123–L186）：接收`path`。 控制顺序：L125按`not language`分支；L128按`len(data) > 2_000_000`分支；L130按`language != "vue"`分支；L134遍历`walk(tree.root_node)`；L135按`node.type == "script_element"`分支；L138按`start`分支；L139遍历`start.named_children`；L140按`child.type == "attribute"`分支。后续分支沿下方源码相同行号继续阅读。 调用`LANGUAGES.get`、`Path`、`Path(path).read_bytes`、`len`、`declarations`、`parser("html").parse`、`parser`、`walk`、`next`等。 返回路径：L126的`{}`；L129的`{"language": language, "skipped": "source exceeds 2 MB parse budget"}`；L131的`{"language": language, "parser": "tree-sitter", **declarations(data, language)}`。

</details>

**创建路径：** `workbench/symbols.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L186。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6628`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/symbols.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "634f5146eb97ae12083d6589940cd75d3ca6ac698b6ae8301c35febeaf333fc4"} -->
````python
# workbench/symbols.py
"""Deterministic Tree-sitter declarations; Vue scripts use their real SFC line offsets.

This is a syntax index, not Java/TypeScript type resolution. No grammar downloads,
code execution, or model calls occur while indexing.
"""

import importlib
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path

LANGUAGES = {
    ".java": "java",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".jsx": "javascript",
    ".vue": "vue",
}
PACKAGES = (
    "tree-sitter",
    "tree-sitter-java",
    "tree-sitter-typescript",
    "tree-sitter-javascript",
    "tree-sitter-html",
)
DECLARATIONS = {
    "class_declaration",
    "interface_declaration",
    "enum_declaration",
    "record_declaration",
    "annotation_type_declaration",
    "method_declaration",
    "constructor_declaration",
    "field_declaration",
    "function_declaration",
    "generator_function_declaration",
    "method_definition",
    "abstract_method_signature",
    "method_signature",
    "type_alias_declaration",
    "variable_declarator",
}
IMPORTS = {"import_declaration", "import_statement", "package_declaration"}


@lru_cache(maxsize=1)
def parser_identity():
    return {name: version(name) for name in PACKAGES}


def parser(language):
    from tree_sitter import Language, Parser

    package = "typescript" if language == "tsx" else language
    module = importlib.import_module("tree_sitter_" + package)
    factory = {"typescript": "language_typescript", "tsx": "language_tsx"}.get(language, "language")
    return Parser(Language(getattr(module, factory)()))


def walk(node):
    stack = [node]
    while stack:
        item = stack.pop()
        yield item
        stack.extend(reversed(item.named_children))


def text(node, data, limit=500):
    if node is None:
        return ""
    return data[node.start_byte : node.end_byte].decode("utf-8", errors="replace")[:limit]


def declarations(data, language, offset=0):
    tree = parser(language).parse(data)
    symbols, imports = [], []
    for node in walk(tree.root_node):
        if node.type in IMPORTS:
            imports.append(text(node, data))
        if node.type not in DECLARATIONS:
            continue
        name = node.child_by_field_name("name")
        if node.type == "field_declaration":
            declarator = next(
                (n for n in node.named_children if n.type == "variable_declarator"), None
            )
            name = declarator.child_by_field_name("name") if declarator else None
        if name is None:
            continue
        body = node.child_by_field_name("body")
        end = body.start_byte if body else node.end_byte
        header = data[node.start_byte : end].decode("utf-8", errors="replace")
        modifiers = next((n for n in node.named_children if n.type == "modifiers"), None)
        annotations = (
            [
                text(n, data)
                for n in walk(modifiers)
                if n.type in {"annotation", "marker_annotation"}
            ]
            if modifiers
            else []
        )
        symbols.append(
            {
                "name": text(name, data, 200),
                "kind": node.type,
                "line": node.start_point.row + offset + 1,
                "end_line": node.end_point.row + offset + 1,
                "signature": " ".join(header.split())[:500],
                "annotations": annotations[:16],
                "bases": [
                    text(n, data)
                    for n in node.named_children
                    if n.type
                    in {"superclass", "super_interfaces", "extends_type_clause", "class_heritage"}
                ],
            }
        )
    return {"symbols": symbols, "imports": imports, "parse_error": tree.root_node.has_error}


def parse_file(path):
    language = LANGUAGES.get(Path(path).suffix)
    if not language:
        return {}
    data = Path(path).read_bytes()
    if len(data) > 2_000_000:
        return {"language": language, "skipped": "source exceeds 2 MB parse budget"}
    if language != "vue":
        return {"language": language, "parser": "tree-sitter", **declarations(data, language)}
    tree = parser("html").parse(data)
    symbols, imports, errors = [], [], []
    for node in walk(tree.root_node):
        if node.type == "script_element":
            start = next((n for n in node.named_children if n.type == "start_tag"), None)
            attributes = {}
            if start:
                for child in start.named_children:
                    if child.type == "attribute":
                        parts = child.named_children
                        if parts:
                            attributes[text(parts[0], data)] = text(parts[-1], data).strip("\"'")
            script_language = {
                "ts": "typescript",
                "tsx": "tsx",
                "js": "javascript",
                "jsx": "javascript",
            }.get(attributes.get("lang", "js"))
            if not script_language:
                errors.append("unsupported Vue script language")
                continue
            body = next((n for n in node.named_children if n.type == "raw_text"), None)
            if body:
                parsed = declarations(
                    data[body.start_byte : body.end_byte], script_language, body.start_point.row
                )
                symbols.extend(parsed["symbols"])
                imports.extend(parsed["imports"])
                if parsed["parse_error"]:
                    errors.append("Vue script syntax error")
            elif "src" in attributes:
                imports.append("script src=" + attributes["src"])
        if node.type in {"start_tag", "self_closing_tag"}:
            tag = next((n for n in node.named_children if n.type == "tag_name"), None)
            name = text(tag, data)
            if name and (name[0].isupper() or "-" in name):
                symbols.append(
                    {
                        "name": name,
                        "kind": "vue_component_usage",
                        "line": node.start_point.row + 1,
                        "end_line": node.end_point.row + 1,
                        "signature": text(node, data),
                        "annotations": [],
                        "bases": [],
                    }
                )
    return {
        "language": "vue",
        "parser": "tree-sitter-html+script",
        "symbols": symbols,
        "imports": imports,
        "parse_error": bool(errors) or tree.root_node.has_error,
        "diagnostics": errors,
    }
````
