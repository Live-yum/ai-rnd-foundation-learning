"""The only OpenSpec commands permitted by production are document operations."""

import json
import shutil
import subprocess
from pathlib import Path

from workbench.infrastructure.processes.tools import clean_env
from workbench.settings import ROOT

VERSION = "1.14.1"
SCHEMA = "rnd-factory"
ARTIFACTS = ("proposal", "specs", "design", "tasks")


class OpenSpecCLI:
    def __init__(self, workspace, *, executable=None, timeout=30):
        self.workspace = Path(workspace).resolve()
        self.timeout = timeout
        self.executable = (
            executable or ROOT / "tools/openspec/node_modules/@fission-ai/openspec/bin/openspec.js"
        )

    def _run(self, args, *, json_output=True):
        node = shutil.which("node")
        if not node or not Path(self.executable).is_file():
            raise ValueError("OpenSpec pinned runtime missing; run npm ci --prefix tools/openspec")
        with __import__("tempfile").TemporaryFile() as output:
            result = subprocess.run(
                [node, str(self.executable), *args],
                cwd=self.workspace,
                env=clean_env({"OPENSPEC_TELEMETRY": "0", "DO_NOT_TRACK": "1", "CI": "1"}),
                stdout=output,
                stderr=subprocess.DEVNULL,
                timeout=self.timeout,
                check=False,
            )
            if result.returncode:
                raise ValueError("OpenSpec document command failed")
            output.seek(0)
            raw = output.read(200001)
        if len(raw) > 200000:
            raise ValueError("OpenSpec JSON exceeds budget")
        return json.loads(raw) if json_output else raw.decode().strip()

    def check_version(self):
        if self._run(["--version"], json_output=False) != VERSION:
            raise ValueError("OpenSpec version differs from reviewed lock")

    def validate_schema(self):
        return self._run(["schema", "validate", SCHEMA, "--json"])

    def new_change(self):
        return self._run(["new", "change", "product", "--schema", SCHEMA, "--json"])

    def instructions(self, artifact):
        if artifact not in ARTIFACTS:
            raise ValueError("Only proposal/specs/design/tasks instructions are allowed")
        return self._run(["instructions", artifact, "--change", "product", "--json"])

    def status(self):
        return self._run(["status", "--change", "product", "--json"])
