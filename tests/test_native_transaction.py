import ast
import sys

import pytest

from workbench.native_compatibility import commit_before_response
from workbench.tools import ToolFailure, run_command


def test_generated_transaction_scope_is_recorded(tmp_path):
    file = tmp_path / "controller.py"
    file.write_text(
        """from fastapi import Depends, Security
async def create(auth=Security(AuthPermission(["module_rnd:device:create"])), db=Depends(db_getter)):
    return await service.create(db)
""",
        encoding="utf-8",
    )
    receipt = commit_before_response(file)
    text = file.read_text(encoding="utf-8")
    ast.parse(text)
    assert 'scope="function"' in text
    assert 'Security(AuthPermission(["module_rnd:device:create"]))' in text
    assert receipt["before_sha256"] != receipt["after_sha256"]
    assert receipt["dependencies"] == 1
    with pytest.raises(ValueError):
        commit_before_response(file)


def test_tool_failure_retains_end_of_large_log(tmp_path):
    with pytest.raises(ToolFailure) as error:
        run_command(
            [
                sys.executable,
                "-c",
                "print('start');print('x'*80000);print('specific failure');raise SystemExit(9)",
            ],
            tmp_path,
        )
    assert error.value.log.startswith("start")
    assert "specific failure" in error.value.log
    assert len(error.value.log) < 65000


def test_timeout_preserves_diagnostics(tmp_path):
    with pytest.raises(ToolFailure) as error:
        run_command(
            [sys.executable, "-u", "-c", "import time;print('before timeout');time.sleep(10)"],
            tmp_path,
            timeout=0.5,
        )
    assert error.value.timed_out is True
    assert "before timeout" in error.value.log
