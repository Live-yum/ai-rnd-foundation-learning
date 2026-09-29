import ast
import sys

import pytest

from workbench.native_compatibility import commit_before_response, prepare_fastapi_transactions
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


def test_updates_exercise_integer_and_boolean_changes():
    from scripts.ci_native_generated import acceptance_spec
    from workbench.native_acceptance import sample_record

    entity = acceptance_spec().entities[0]
    initial = sample_record(entity)
    changed = sample_record(entity, "updated")
    assert initial["name"] != changed["name"]
    assert initial["quantity"] != changed["quantity"]
    assert initial["active"] is True
    assert changed["active"] is False


def test_native_role_and_codegen_both_commit_before_their_success_response(tmp_path):
    paths = [
        "app/modules/system/role/controller.py",
        "app/modules/generator/gencode/controller.py",
    ]
    source = (
        "from fastapi import Depends, Security\n"
        "async def operation(auth=Security(native_auth), db=Depends(db_getter)):\n"
        "    return await native_service(db)\n"
    )
    for relative in paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text(source, encoding="utf-8")
    receipts = prepare_fastapi_transactions(tmp_path)
    assert [r["path"] for r in receipts] == paths
    assert all(r["before_sha256"] != r["after_sha256"] for r in receipts)
    for relative in paths:
        actual = (tmp_path / relative).read_text(encoding="utf-8")
        assert actual == source.replace(
            "Depends(db_getter)", 'Depends(db_getter, scope="function")'
        )
        ast.parse(actual)
