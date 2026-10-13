"""Convert an untrusted sandbox snapshot to existing SHA-bound CapabilityEdits."""

from workbench.coding.candidates import task_path_errors
from workbench.filesystem import inside, sha
from workbench.planning.contracts import CapabilityEdits, SourceEdit


def snapshot_edits(product, snapshot, task, selection):
    errors = task_path_errors(task, selection)
    if errors:
        raise ValueError("; ".join(errors))
    if set(snapshot) != set(task.allowed_paths) or len(snapshot) > 64:
        raise ValueError("sandbox snapshot must contain exactly the approved business files")
    if any(type(value) is not str for value in snapshot.values()):
        raise ValueError("only UTF-8 text source is supported")
    if sum(len(value.encode()) for value in snapshot.values()) > 1_000_000:
        raise ValueError("sandbox diff exceeds 1MB")
    return CapabilityEdits(
        explanation="mini-SWE isolated candidate; independent acceptance pending",
        files=[
            SourceEdit(
                path=name,
                before_sha256=sha(inside(product, name))
                if inside(product, name).is_file()
                else None,
                content=snapshot[name],
            )
            for name in task.allowed_paths
        ],
    )
