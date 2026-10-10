"""Stable serial DAG order used by planners and durable dispatchers."""


def serial_order(tasks):
    by_id = {task.id: task for task in tasks}
    if len(by_id) != len(tasks):
        raise ValueError("duplicate task identifier")
    pending = list(tasks)
    done = set()
    result = []
    while pending:
        task = next((task for task in pending if set(task.depends_on) <= done), None)
        if task is None:
            raise ValueError("cyclic or unknown dependency")
        result.append(task)
        done.add(task.id)
        pending.remove(task)
    return result
