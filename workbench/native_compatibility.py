"""Small recorded compatibility edits in generated workspaces, never upstream checkouts."""

import ast
import re
from pathlib import Path

from workbench.filesystem import atomic_text, sha


def _java_code_mask(source: str) -> str:
    """Keep code offsets while hiding Java comments, strings, chars and text blocks."""
    out = list(source)
    index = 0
    while index < len(source):
        start = index
        if source.startswith("//", index):
            end = source.find("\n", index + 2)
            index = len(source) if end < 0 else end
        elif source.startswith("/*", index):
            end = source.find("*/", index + 2)
            if end < 0:
                raise ValueError("Unterminated generated Java comment")
            index = end + 2
        elif source[index] in "\"'":
            quote = '"""' if source.startswith('"""', index) else source[index]
            index += len(quote)
            while index < len(source):
                if source[index] == "\\":
                    index += 2
                elif source.startswith(quote, index):
                    index += len(quote)
                    break
                else:
                    index += 1
            else:
                raise ValueError("Unterminated generated Java literal")
        else:
            index += 1
            continue
        for offset in range(start, min(index, len(source))):
            if source[offset] not in "\r\n":
                out[offset] = " "
    return "".join(out)


def prepare_java_time_imports(source: str) -> str:
    """Repair omitted native date imports, only for generated field declarations.

    The pinned native generator can emit LocalDate fields while importing only
    LocalDateTime. Keep all generated declarations and annotations unchanged;
    exclude qualified types, comments/literals and existing/shadowing imports.
    The mount receipt records both the original export and transformed hashes.
    """
    code = _java_code_mask(source)
    types = set(
        re.findall(
            r"(?m)^\s*(?:(?:public|protected|private|static|final|transient|volatile)\s+)*"
            r"(LocalDate|LocalDateTime)\b\s*(?:\[\s*\]\s*)*\s+"
            r"[A-Za-z_$][\w$]*\s*(?=[;=])",
            code,
        )
    )
    if not types or re.search(r"\bimport\s+java\.time\.\*\s*;", code):
        return source
    missing = []
    for name in sorted(types):
        if re.search(r"\bimport\s+(?:[\w$]+\.)+" + name + r"\s*;", code):
            continue
        if re.search(r"\b(?:class|interface|enum|record)\s+" + name + r"\b", code):
            continue
        missing.append(name)
    if not missing:
        return source
    packages = list(re.finditer(r"(?m)^\s*package\s+[\w$.]+\s*;", code))
    if len(packages) != 1:
        raise ValueError("Unexpected generated Java package for time import repair")
    offset = packages[0].end()
    newline = "\r\n" if "\r\n" in source else "\n"
    imports = "".join(newline + f"import java.time.{name};" for name in missing)
    return source[:offset] + imports + source[offset:]


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
