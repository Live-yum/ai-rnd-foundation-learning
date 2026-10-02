# workbench/native_compatibility.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生事务提交时机的精确适配。** commit_before_response只在固定控制器满足预期代码形态时改变依赖生命周期，让成功响应之前提交事务。prepare_fastapi_transactions逐文件检查并记录哈希，不以sleep掩盖事务竞态。

**对应关系：** native_environment → FastapiAdmin控制器；test_native_transaction。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `prepare_java_time_imports`（L9–L76）：接收`source`。 源码说明：Repair omitted time imports using only generated field type syntax nodes. The pinned generator emits LocalDate fields while importing LocalDateTime. Preserve every generated declaration/annotation; th。 控制顺序：L23在`stack`成立时循环；L26按`node.type == "field_declaration"`分支；L28按`field_type and field_type.type == "array_type"`分支；L30按`field_type and field_type.type == "type_identifier"`分支；L32按`node.type in { "class_declaration", "interface_declaration", "enum_declaration", "rec…`分支；L40按`name is None and node.type == "type_parameter"`分支；L42按`name`分支；L45按`not types`分支。后续分支沿下方源码相同行号继续阅读。 调用`source.encode`、`Parser(Language(tree_sitter_java.language())).parse`、`Parser`、`Language`、`tree_sitter_java.language`、`set`、`stack.pop`、`stack.extend`、`node.child_by_field_name`等。 返回路径：L46的`source`；L62的`source`；L69的`source`。
- `commit_before_response`（L79–L113）：接收`controller`。 源码说明：A yielded request-scoped transaction can otherwise commit after its success response. Keep the upstream authentication, permission checks, CRUD and transaction implementation. Only give the generated 。 控制顺序：L100按`not dependencies or any(node.keywords for node in dependencies)`分支；L101抛异常，停止当前正常路径；L104按`source.count(old) != len(dependencies)`分支；L105抛异常，停止当前正常路径。 调用`Path`、`controller.read_text`、`ast.parse`、`ast.walk`、`isinstance`、`len`、`any`、`ValueError`、`sha`等。 返回路径：L107的`{ "path": controller.name, "before_sha256": before, "after_sha256": sha(controller), "chan…`。
- `prepare_fastapi_transactions`（L116–L131）：接收`backend`。 源码说明：Commit native role grants AND codegen metadata before acknowledging success. The generator imports, updates and mounts metadata across consecutive HTTP requests. Its request-scoped yield otherwise all。 控制顺序：L124遍历`( "app/modules/system/role/controller.py", "app/modules/generator…`。 调用`commit_before_response`、`Path`、`receipts.append`。 返回路径：L131的`receipts`。

</details>

**创建路径：** `workbench/native_compatibility.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L131。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5427`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_compatibility.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "686218781494dd34d5909b253fd3f6fc4992d0b2a6835cf5221ef9f825f11cd9"} -->
````python
# workbench/native_compatibility.py
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
````
