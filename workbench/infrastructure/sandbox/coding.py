"""File-only coding session on the existing admitted private Daytona channel.

No agent command is executed, even inside the container. Generated code is run
later exclusively by the independent capability verifier.
"""

import time
import uuid
from contextlib import contextmanager

from workbench.capability_execution import (
    capability_execution_prerequisites,
    require_profile_container_binding,
)
from workbench.capability_isolation import require_container_evidence
from workbench.coding.candidates import task_path_errors
from workbench.errors import UnsupportedScope
from workbench.filesystem import inside, write_json
from workbench.sandbox import client_for, close_client, params_for

REMOTE = "/tmp/rnd-agent-business"


class DaytonaFiles:
    def __init__(self, sandbox, task, timeout, deadline=None):
        self.sandbox, self.task, self.timeout = sandbox, task, timeout
        self.deadline = deadline
        self.cleanup_record = None

    def bind_candidate(self, source):
        self.candidate_digest = source
        if self.cleanup_record is not None:
            from workbench.infrastructure.sandbox.cleanup import receipt

            write_json(
                self.cleanup_record,
                receipt(
                    {**self.cleanup_binding, "source": source}, self.cleanup_name, self.sandbox.id
                ),
            )

    def remaining(self):
        remaining = (
            self.timeout
            if self.deadline is None
            else min(self.timeout, self.deadline - time.monotonic())
        )
        remaining = int(remaining)
        if remaining <= 0:
            raise UnsupportedScope("Agent filesystem deadline exhausted")
        return remaining

    def write(self, edits):
        if {edit.path for edit in edits.files} != set(self.task.allowed_paths):
            raise ValueError("Agent files differ from approved paths")
        for edit in edits.files:
            self.remaining()
            remote = REMOTE + "/" + edit.path
            self.sandbox.fs.create_folder(remote.rsplit("/", 1)[0], "700")
            self.sandbox.fs.upload_file(edit.content.encode(), remote, timeout=self.remaining())

    def snapshot(self, paths):
        if paths != self.task.allowed_paths:
            raise ValueError("snapshot paths differ from task")
        result = {}
        for name in paths:
            # SDK 0.190.0 overloads advertise timeout=, but its implementation
            # accepts only positional arguments. Keep empty-file support too.
            content = self.sandbox.fs.download_file(REMOTE + "/" + name, self.remaining())
            if not isinstance(content, bytes) or len(content) > 100000:
                raise ValueError("sandbox file exceeds source budget")
            result[name] = content.decode("utf-8")
        return result


@contextmanager
def _local_environment(
    settings,
    task,
    selection,
    product,
    *,
    deadline=None,
    cleanup_record=None,
    cleanup_binding=None,
    owned_name=None,
    on_created=None,
    external_cleanup=False,
    on_phase=None,
):
    from scripts.daytona_capability_profile import inspect_created_sandbox
    from workbench.daytona_sessions import _DEADLINE
    from workbench.planning.contracts import CapabilityEdits, SourceEdit

    phase = on_phase or (lambda value: None)
    phase("admission")
    if task_path_errors(task, selection):
        raise UnsupportedScope("Agent task crosses the business-file boundary")
    directory, profile = capability_execution_prerequisites(settings, selection)
    phase("client")
    client = client_for(settings)
    sandbox = None
    name = None
    env = None
    token = _DEADLINE.set(None if deadline is None else deadline - 15)

    def remaining(cleanup=False):
        end = deadline if cleanup or deadline is None else deadline - 15
        available = (
            settings.tool_timeout
            if end is None
            else min(settings.tool_timeout, end - time.monotonic())
        )
        available = int(available)
        if available <= 0:
            if cleanup:
                # Never skip owned cleanup when an SDK call overruns. The caller
                # rejects any result after the module deadline, even if deletion succeeds.
                return 1
            raise UnsupportedScope("Agent sandbox deadline exhausted")
        return available

    try:
        # The admitted Runner selects strict network/resource limits by this
        # existing source prefix, shared with the independent verifier.
        prefix = "rnd-source-native-" if selection["template"] == "fastapiadmin" else "rnd-source-"
        name = owned_name or prefix + "agent-" + uuid.uuid4().hex
        if cleanup_record is not None:
            from workbench.infrastructure.sandbox.cleanup import receipt

            write_json(cleanup_record, receipt(cleanup_binding, name, None, "create_unconfirmed"))
        phase("create")
        sandbox = client.create(
            params_for(settings, name, selection["template"], selection),
            timeout=remaining(),
        )
        if on_created is not None:
            on_created(name, sandbox.id)
        remaining()
        phase("refresh")
        sandbox.refresh_data()
        if sandbox.network_block_all is not True or sandbox.public is not False:
            raise UnsupportedScope("Agent sandbox is not private and network-blocked")
        phase("inspection")
        evidence = require_container_evidence(
            inspect_created_sandbox(
                directory, sandbox.id, require_resources=True, selection=selection
            ),
            sandbox.id,
        )
        require_profile_container_binding(profile, evidence)
        env = DaytonaFiles(
            sandbox, task, settings.tool_timeout, None if deadline is None else deadline - 15
        )
        if cleanup_record is not None:
            write_json(cleanup_record, receipt(cleanup_binding, name, sandbox.id))
            env.cleanup_record, env.cleanup_binding, env.cleanup_name = (
                cleanup_record,
                cleanup_binding,
                name,
            )
        phase("initial_upload")
        env.write(
            CapabilityEdits(
                explanation="Approved before-images",
                files=[
                    SourceEdit(
                        path=name,
                        content=inside(product, name).read_bytes().decode("utf-8")
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
            _DEADLINE.reset(token)
            if external_cleanup:
                pass  # The supervising parent owns deletion, including a killed SDK worker.
            elif cleanup_record is not None and name is not None:
                from workbench.infrastructure.sandbox.cleanup import delete_owned

                binding = {
                    **cleanup_binding,
                    "source": getattr(env, "candidate_digest", cleanup_binding["source"]),
                }
                delete_owned(
                    settings,
                    name,
                    sandbox.id if sandbox is not None else None,
                    binding,
                    cleanup_record,
                    deadline,
                )
            elif sandbox is not None:
                client.delete(sandbox, timeout=remaining(cleanup=True))
        finally:
            try:
                close_client(client)
            except Exception:
                if cleanup_record is not None and cleanup_record.exists():
                    import json

                    value = json.loads(cleanup_record.read_text())
                    value.update(status="unconfirmed", reason="transport_cleanup")
                    write_json(cleanup_record, value)
                raise


def coding_environment(
    settings, task, selection, product, *, deadline, cleanup_record, cleanup_binding
):
    """All production SDK work runs in a process supervised until owned cleanup ends."""
    from workbench.infrastructure.sandbox.file_session import supervised_environment

    return supervised_environment(
        settings,
        task,
        selection,
        product,
        deadline=deadline,
        cleanup_record=cleanup_record,
        cleanup_binding=cleanup_binding,
    )
