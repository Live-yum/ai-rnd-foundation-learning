"""Small recorded compatibility edits in generated workspaces, never upstream checkouts."""

import ast
from pathlib import Path

from workbench.filesystem import atomic_text, sha


def prepare_java_time_imports(source: str) -> str:
    """Repair omitted time imports using only generated field type syntax nodes.

    The pinned generator emits LocalDate fields while importing LocalDateTime.
    Preserve every generated declaration/annotation; the mount receipt retains
    both original export and adapted hashes. Comments and literals are not types.
    """
    import tree_sitter_java
    from tree_sitter import Language, Parser

    encoded = source.encode("utf-8")
    tree = Parser(Language(tree_sitter_java.language())).parse(encoded)
    types, declared = set(), set()
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        stack.extend(node.named_children)
        if node.type == "field_declaration":
            field_type = node.child_by_field_name("type")
            if field_type and field_type.type == "array_type":
                field_type = field_type.child_by_field_name("element")
            if field_type and field_type.type == "type_identifier":
                types.add(field_type.text.decode("utf-8"))
        elif node.type in {
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
            "record_declaration",
            "type_parameter",
        }:
            name = node.child_by_field_name("name")
            if name is None and node.type == "type_parameter":
                name = next((n for n in node.named_children if n.type == "type_identifier"), None)
            if name:
                declared.add(name.text.decode("utf-8"))
    types &= {"LocalDate", "LocalDateTime"}
    if not types:
        return source
    if tree.root_node.has_error:
        raise ValueError("Invalid generated Java syntax for time import repair")
    imports = []
    for declaration in tree.root_node.named_children:
        if declaration.type != "import_declaration":
            continue
        parts, pending = [], [declaration]
        while pending:
            node = pending.pop()
            if node.type in {"identifier", "asterisk"}:
                parts.append(node.text.decode("utf-8"))
            else:
                pending.extend(reversed(node.named_children))
        imports.append(parts)
    if ["java", "time", "*"] in imports:
        return source
    missing = [
        name
        for name in sorted(types - declared)
        if not any(parts and parts[-1] == name for parts in imports)
    ]
    if not missing:
        return source
    packages = [n for n in tree.root_node.named_children if n.type == "package_declaration"]
    if len(packages) != 1:
        raise ValueError("Unexpected generated Java package for time import repair")
    offset = packages[0].end_byte
    newline = "\r\n" if "\r\n" in source else "\n"
    additions = "".join(newline + f"import java.time.{name};" for name in missing).encode("utf-8")
    return (encoded[:offset] + additions + encoded[offset:]).decode("utf-8")


def commit_before_response(controller):
    """A yielded request-scoped transaction can otherwise commit after its success response.

    Keep the upstream authentication, permission checks, CRUD and transaction implementation.
    Only give the generated handler's database dependency function scope, so a commit error
    cannot follow a successful response. Reject unfamiliar controller shapes rather than
    silently doing a broad replacement in arbitrary source.
    """
    controller = Path(controller)
    source = controller.read_text(encoding="utf-8")
    tree = ast.parse(source)
    dependencies = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Depends"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "db_getter"
    ]
    if not dependencies or any(node.keywords for node in dependencies):
        raise ValueError("Unexpected native generated database dependency contract")
    before = sha(controller)
    old = "Depends(db_getter)"
    if source.count(old) != len(dependencies):
        raise ValueError("Unexpected generated controller formatting")
    atomic_text(controller, source.replace(old, 'Depends(db_getter, scope="function")'))
    return {
        "path": controller.name,
        "before_sha256": before,
        "after_sha256": sha(controller),
        "change": "commit-before-response",
        "dependencies": len(dependencies),
    }


def prepare_fastapi_transactions(backend: Path) -> list[dict]:
    """Commit native role grants AND codegen metadata before acknowledging success.

    The generator imports, updates and mounts metadata across consecutive HTTP requests.
    Its request-scoped yield otherwise allows an immediate list/export/login to race a commit.
    No retry hides an import failure; preserve native auth, CRUD and transaction handling.
    """
    receipts = []
    for relative in (
        "app/modules/system/role/controller.py",
        "app/modules/generator/gencode/controller.py",
    ):
        receipt = commit_before_response(Path(backend) / relative)
        receipt["path"] = relative
        receipts.append(receipt)
    return receipts
