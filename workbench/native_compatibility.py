"""Small recorded compatibility edits in generated workspaces, never upstream checkouts."""

import ast
from pathlib import Path

from workbench.filesystem import atomic_text, sha


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
