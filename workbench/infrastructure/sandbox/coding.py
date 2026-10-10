"""File-only coding session on the existing admitted private Daytona channel.

No agent command is executed, even inside the container. Generated code is run
later exclusively by the independent capability verifier.
"""

import uuid
from contextlib import contextmanager

from workbench.capability_execution import (
    capability_execution_prerequisites,
    require_profile_container_binding,
)
from workbench.capability_isolation import require_container_evidence
from workbench.coding.candidates import task_path_errors
from workbench.errors import UnsupportedScope
from workbench.filesystem import inside
from workbench.sandbox import client_for, close_client, params_for

REMOTE = "/tmp/rnd-agent-business"


class DaytonaFiles:
    def __init__(self, sandbox, task, timeout):
        self.sandbox, self.task, self.timeout = sandbox, task, timeout

    def write(self, edits):
        if {edit.path for edit in edits.files} != set(self.task.allowed_paths):
            raise ValueError("Agent files differ from approved paths")
        for edit in edits.files:
            remote = REMOTE + "/" + edit.path
            self.sandbox.fs.create_folder(remote.rsplit("/", 1)[0], "700")
            self.sandbox.fs.upload_file(edit.content.encode(), remote, timeout=self.timeout)

    def snapshot(self, paths):
        if paths != self.task.allowed_paths:
            raise ValueError("snapshot paths differ from task")
        result = {}
        for name in paths:
            content = self.sandbox.fs.download_file(REMOTE + "/" + name, timeout=self.timeout)
            if not isinstance(content, bytes) or len(content) > 100000:
                raise ValueError("sandbox file exceeds source budget")
            result[name] = content.decode("utf-8")
        return result


@contextmanager
def coding_environment(settings, task, selection, product):
    from scripts.daytona_capability_profile import inspect_created_sandbox
    from workbench.planning.contracts import CapabilityEdits, SourceEdit

    if task_path_errors(task, selection):
        raise UnsupportedScope("Agent task crosses the business-file boundary")
    directory, profile = capability_execution_prerequisites(settings, selection)
    client = client_for(settings)
    sandbox = None
    try:
        sandbox = client.create(
            params_for(settings, "rnd-agent-" + uuid.uuid4().hex, selection["template"], selection),
            timeout=settings.tool_timeout,
        )
        sandbox.refresh_data()
        if sandbox.network_block_all is not True or sandbox.public is not False:
            raise UnsupportedScope("Agent sandbox is not private and network-blocked")
        evidence = require_container_evidence(
            inspect_created_sandbox(
                directory, sandbox.id, require_resources=True, selection=selection
            ),
            sandbox.id,
        )
        require_profile_container_binding(profile, evidence)
        env = DaytonaFiles(sandbox, task, settings.tool_timeout)
        env.write(
            CapabilityEdits(
                explanation="Approved before-images",
                files=[
                    SourceEdit(
                        path=name,
                        content=inside(product, name).read_text()
                        if inside(product, name).is_file()
                        else "",
                    )
                    for name in task.allowed_paths
                ],
            )
        )
        yield env
    finally:
        try:
            if sandbox is not None:
                client.delete(sandbox, timeout=settings.tool_timeout)
        finally:
            close_client(client)
