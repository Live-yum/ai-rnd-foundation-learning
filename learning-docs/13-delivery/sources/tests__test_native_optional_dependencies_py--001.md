# tests/test_native_optional_dependencies.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `without_postgres`（L24–L34）：接收`source`、`*args`。 控制顺序：L34断言`result.returncode == 0`。 调用`subprocess.run`、`textwrap.dedent`、`map`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_config_inspection_does_not_import_postgres_runtime`（L37–L54）：接收`tmp_path`。 调用`without_postgres`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_execution_checks_platform_and_driver_before_side_effects`（L58–L96）：接收`tmp_path`、`platform`。 调用`without_postgres`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_failed_native_design_resumes_same_persisted_run`（L99–L188）：接收`tmp_path`。 调用`without_postgres`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_optional_dependencies.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L188。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8135`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_optional_dependencies.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "aa641db46683f20705ec09b0b41c1fb09303ea309d9bfca72aa68e5ac3934073"} -->
````python
# tests/test_native_optional_dependencies.py
"""Base installs can inspect native plans; execution still requires its real tools."""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NO_POSTGRES = """
import sys
from importlib.abc import MetaPathFinder

class NoPostgres(MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "psycopg" or fullname.startswith("psycopg."):
            raise ModuleNotFoundError("No module named 'psycopg'", name="psycopg")

sys.meta_path.insert(0, NoPostgres())
"""


def without_postgres(source, *args):
    # A fresh interpreter prevents the all-extras CI environment or another test's
    # cached native modules from concealing an eager optional-dependency import.
    result = subprocess.run(
        [sys.executable, "-c", NO_POSTGRES + textwrap.dedent(source), *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_native_config_inspection_does_not_import_postgres_runtime(tmp_path):
    without_postgres(
        """
        from pathlib import Path
        from workbench.native_delivery import runtime_enabled, runtime_path
        from workbench.settings import Settings

        settings = Settings(data_dir=Path(sys.argv[1]), _env_file=None)
        for template in ("fastapiadmin", "yudao-vben"):
            assert not runtime_enabled(settings, template)
            assert runtime_path(settings, template).name == template + ".runtime.json"
        assert "workbench.native_lab" not in sys.modules
        assert "workbench.portable" not in sys.modules
        assert "psycopg" not in sys.modules
        assert not settings.data_dir.exists()
        """,
        tmp_path / "untouched",
    )


@pytest.mark.parametrize("platform", ["nt", "posix"])
def test_execution_checks_platform_and_driver_before_side_effects(tmp_path, platform):
    without_postgres(
        """
        from pathlib import Path
        from types import SimpleNamespace
        from workbench import native_delivery
        from workbench.domain import Plan
        from workbench.generator import PrerequisiteError
        from workbench.settings import Settings

        native_delivery.os = SimpleNamespace(name=sys.argv[2])
        def unexpected(*args, **kwargs):
            raise AssertionError("Tool discovery must follow platform/driver checks")
        native_delivery.shutil.which = unexpected
        settings = Settings(data_dir=Path(sys.argv[1]), _env_file=None)
        product = settings.data_dir / "runs/existing/product"
        plan = Plan(title="任务", data_scope="shared", acceptance=["CRUD"], entities=[{
            "name": "task", "description": "任务", "fields": [{"name": "title", "kind": "text"}]
        }])
        try:
            native_delivery.managed_generate(settings, "fastapiadmin", plan, product)
        except PrerequisiteError as exc:
            message = str(exc)
            assert "WSL 2/Linux" in message
            if sys.argv[2] == "nt":
                assert "默认 Python 通道支持 Windows" in message
                assert "uv sync" not in message
            else:
                assert "uv sync --locked --extra postgres" in message
                assert "重试同一运行" in message
        else:
            raise AssertionError("Missing native prerequisites must fail closed")
        assert "workbench.native_lab" not in sys.modules
        assert "workbench.portable" not in sys.modules
        assert not settings.data_dir.exists()
        """,
        tmp_path / "untouched",
        platform,
    )


def test_legacy_failed_native_design_resumes_same_persisted_run(tmp_path):
    without_postgres(
        """
        from pathlib import Path
        from workbench.domain import Plan, Requirement
        from workbench.flow import Workflow
        from workbench.runtime import Runtime
        from workbench.settings import Settings
        from workbench.store import Store

        plan = Plan(title="共享任务", data_scope="shared", acceptance=["CRUD"], entities=[{
            "name": "task", "description": "任务", "fields": [{"name": "title", "kind": "text"}]
        }])
        class FixtureGateway:
            def __init__(self):
                self.calls = []
            def complete(self, run, key, instruction, payload, schema):
                self.calls.append(key)
                if schema is Requirement:
                    return Requirement(summary="共享任务", users=["团队"], data_scope="shared",
                                       features=["CRUD"], acceptance=["CRUD"])
                assert schema is Plan
                return plan

        settings = Settings(data_dir=Path(sys.argv[1]), install_products=False, _env_file=None)
        store = Store(settings)
        store.migrate()
        project = store.create_project("保留项目", "project")
        selection = {"template": "fastapiadmin", "frontend": "fastapiadmin-vue",
                     "database": "postgresql"}
        run = store.create_run(project["id"], {"requirement": "共享任务 CRUD",
                               "template": "fastapiadmin", "selection": selection}, "start")["run_id"]
        gateway = FixtureGateway()
        current_design = Workflow.design
        def old_design(self, state):
            # The pre-fix native_delivery -> native_lab import reached exactly
            # this portable import during design, before any runtime checks.
            try:
                from workbench.portable import menu_snapshot
            except ModuleNotFoundError as exc:
                assert exc.name == "psycopg"
                raise
            raise AssertionError("The base install must reproduce the old import error")
        Workflow.design = old_design
        try:
            with Runtime(settings, store, gateway) as worker:
                assert worker.tick()
                gate = store.get_run(run)["pending"]
                store.submit(run, {"gate_id": gate["gate_id"], "action": "approve",
                                   "approved": True}, "approve-requirements")
                assert worker.tick()
            failed = store.get_run(run)
            assert failed["status"] == "FAILED", failed
            assert "ModuleNotFoundError" in failed["error"]
        finally:
            Workflow.design = current_design
        assert gateway.calls == ["requirement:1", "plan:1"]
        saved_messages = store.messages(run)
        store.engine.dispose()

        class NoMoreModelCalls:
            def complete(self, *args, **kwargs):
                raise AssertionError("Retry must use the saved requirement and plan")

        # Reopen both durable store and checkpoint worker, exactly as a restart.
        store = Store(settings)
        try:
            store.retry(run, "retry-existing")
            with Runtime(settings, store, NoMoreModelCalls()) as worker:
                assert worker.tick()
                snapshot = worker.graph.get_state({"configurable": {"thread_id": run}})
                assert snapshot.values["plan"] == plan.model_dump()
            recovered = store.get_run(run)
            assert recovered["id"] == run
            assert recovered["project_id"] == failed["project_id"]
            assert recovered["created_at"] == failed["created_at"]
            assert recovered["status"] == "WAITING_DESIGN", recovered
            assert recovered["error"] is None
            assert recovered["options"] == failed["options"]
            assert all(recovered["options"][key] == value for key, value in selection.items())
            assert recovered["pending"]["can_approve"] is True
            assert store.messages(run) == saved_messages
            assert not (settings.data_dir / "runs" / run / "product").exists()
            assert "workbench.native_lab" not in sys.modules
            assert "psycopg" not in sys.modules
        finally:
            store.engine.dispose()
        """,
        tmp_path / "state",
    )
````
