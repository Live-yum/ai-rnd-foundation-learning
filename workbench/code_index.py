"""Tree-sitter structural extraction. Vue SFC = HTML shell + script grammar, not vue-tsc."""

from functools import lru_cache
from importlib import import_module
from importlib.metadata import version

from tree_sitter import Language, Parser

GRAMMARS = {
    ".java": ("tree_sitter_java", "language"),
    ".ts": ("tree_sitter_typescript", "language_typescript"),
    ".tsx": ("tree_sitter_typescript", "language_tsx"),
    ".js": ("tree_sitter_javascript", "language"),
    ".jsx": ("tree_sitter_javascript", "language"),
    ".vue": ("tree_sitter_html", "language"),
}
DEFINITIONS = {
    "class_declaration",
    "interface_declaration",
    "enum_declaration",
    "record_declaration",
    "annotation_type_declaration",
    "method_declaration",
    "constructor_declaration",
    "function_declaration",
    "generator_function_declaration",
    "method_definition",
    "variable_declarator",
    "type_alias_declaration",
    "public_field_definition",
    "required_parameter",
    "optional_parameter",
}
MAX_BYTES = 1_000_000
MAX_NODES = 200_000


def parser_identity():
    return {
        name: version(name)
        for name in (
            "tree-sitter",
            "tree-sitter-java",
            "tree-sitter-typescript",
            "tree-sitter-javascript",
            "tree-sitter-html",
        )
    }


@lru_cache(maxsize=8)
def grammar(suffix):
    module, function = GRAMMARS[suffix]
    return Language(getattr(import_module(module), function)())


def walk(root):
    stack, count = [root], 0
    while stack:
        node = stack.pop()
        count += 1
        if count > MAX_NODES:
            raise ValueError("AST节点超过上限")
        yield node
        stack.extend(reversed(node.named_children))


def text(node, data, limit=240):
    return " ".join(data[node.start_byte : node.end_byte].decode("utf-8").split())[:limit]


def extract(data, suffix, offset=0):
    """Return bounded syntax facts with 1-based original-file line positions."""
    if len(data) > MAX_BYTES:
        return {"symbols": [], "imports": [], "references": [], "parse_error": "file_too_large"}
    data.decode("utf-8")  # Do not replace undecodable bytes with invented source.
    tree = Parser(grammar(suffix)).parse(data)
    symbols, imports, refs, errors = [], set(), set(), []
    if tree.root_node.has_error:
        errors.append("syntax_error")
    for node in walk(tree.root_node):
        if suffix == ".vue":
            if node.type == "script_element":
                start = next((n for n in node.named_children if n.type == "start_tag"), None)
                raw = next((n for n in node.named_children if n.type == "raw_text"), None)
                if raw is not None and start is not None:
                    attrs = {}
                    for attr in start.named_children:
                        if attr.type != "attribute":
                            continue
                        parts = attr.named_children
                        if parts:
                            attrs[text(parts[0], data)] = text(parts[-1], data).strip("\"'")
                    lang = attrs.get("lang", "js")
                    if "src" in attrs:
                        imports.add(attrs["src"])
                    if lang not in {"js", "ts", "jsx", "tsx", "javascript", "typescript"}:
                        errors.append("unsupported_script_language:" + lang)
                        continue
                    script_suffix = {"javascript": ".js", "typescript": ".ts"}.get(lang, "." + lang)
                    part = extract(
                        data[raw.start_byte : raw.end_byte],
                        script_suffix,
                        offset + raw.start_point.row,
                    )
                    symbols.extend(part["symbols"])
                    imports.update(part["imports"])
                    refs.update(part["references"])
                    if part.get("parse_error"):
                        errors.append(part["parse_error"])
            elif node.type == "tag_name":
                name = text(node, data)
                if name and (name[0].isupper() or "-" in name):
                    symbols.append(
                        {
                            "name": name,
                            "kind": "vue_component",
                            "line": offset + node.start_point.row + 1,
                            "end_line": offset + node.end_point.row + 1,
                            "signature": name,
                        }
                    )
            continue
        if node.type in DEFINITIONS:
            name = node.child_by_field_name("name") or node.child_by_field_name("pattern")
            if name is not None:
                body = node.child_by_field_name("body")
                stop = min(
                    body.start_byte if body is not None else node.end_byte, node.start_byte + 480
                )
                signature = " ".join(
                    data[node.start_byte : stop].decode("utf-8", errors="ignore").split()
                )[:240]
                symbols.append(
                    {
                        "name": text(name, data),
                        "kind": node.type,
                        "line": offset + node.start_point.row + 1,
                        "end_line": offset + node.end_point.row + 1,
                        "signature": signature,
                    }
                )
        elif node.type in {"annotation", "marker_annotation", "decorator"}:
            name = node.child_by_field_name("name")
            symbols.append(
                {
                    "name": text(name if name is not None else node, data),
                    "kind": "annotation",
                    "line": offset + node.start_point.row + 1,
                    "end_line": offset + node.end_point.row + 1,
                    "signature": text(node, data),
                }
            )
        elif node.type in {"import_declaration", "import_statement", "import_require_clause"}:
            imports.add(text(node, data))
        elif node.type in {"identifier", "type_identifier"}:
            refs.add(text(node, data, 100))
    result = {
        "symbols": sorted(symbols, key=lambda s: (s["line"], s["name"], s["kind"])),
        "imports": sorted(imports),
        "references": sorted(refs),
    }
    if errors:
        result["parse_error"] = ";".join(sorted(set(errors)))
    return result
