# tests/test_learning_order.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.build_learning_docs`、`scripts.handbook_notes`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_database_lesson_runs_from_only_its_documented_files`（L13–L99）：接收`tmp_path`。 控制顺序：L58遍历`names`；L59按`name.startswith("workbench/")`分支；L60断言`stage_for(name) <= 2`；L87断言`probe.returncode == 0`；L97断言`result.returncode == 0`；L98断言`not (destination / "workbench/interfaces/http.py").exists()`；L99断言`not (destination / "workbench/production/worker.py").exists()`。 调用`names.extend`、`path.relative_to(ROOT).as_posix`、`path.relative_to`、`(ROOT / "workbench").rglob`、`stage_for`、`names.append`、`(ROOT / "migrations").rglob`、`path.is_file`、`name.startswith`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_relocated_implementations_keep_their_original_learning_stage`（L102–L111）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L103遍历`RELOCATED_MODULES.items()`；L104断言`stage_for(f"workbench/{relative}.py") == MODULE_STAGE[original]`；L105遍历`(ROOT / "workbench").rglob("__init__.py")`；L107断言`stage_for(name) == (7 if name == "workbench/coding/__init__.py" else 0)`；L108断言`stage_for("workbench/_compat/aliases.py") == 0`；L109断言`stage_for("workbench/cli.py") == 8`；L110断言`stage_for("workbench/capability_sandbox.py") == 7`；L111断言`stage_for("workbench/daytona_worker.py") == 12`。 调用`RELOCATED_MODULES.items`、`stage_for`、`(ROOT / "workbench").rglob`、`path.relative_to(ROOT).as_posix`、`path.relative_to`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_learning_order.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L111。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4502`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_learning_order.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2e0667fcd1fff42396cef99b9fdc95c8f9ab4ef2db8300ddda7258dd7bc05649"} -->
````python
# tests/test_learning_order.py
"""The first database lesson must not depend on a future API or agent module."""

import os
import shutil
import subprocess
import sys

from scripts.build_learning_docs import MODULE_STAGE, stage_for
from scripts.handbook_notes import RELOCATED_MODULES
from workbench.settings import ROOT


def test_database_lesson_runs_from_only_its_documented_files(tmp_path):
    destination = tmp_path / "lesson"
    names = [
        "pyproject.toml",
        "alembic.ini",
        "README.md",
        "workbench/__init__.py",
        "workbench/local_only.py",
        "workbench/settings.py",
        "workbench/models/settings.py",
        "workbench/business/contracts.py",
        "workbench/core/contracts.py",
        "workbench/core/__init__.py",
        "workbench/errors.py",
        "workbench/templates/catalog.py",
        "workbench/templates/adapters.py",
        "workbench/templates/standards.py",
        "templates/standards/common.md",
        "templates/standards/python-basic.md",
        "templates/standards/fastapiadmin.md",
        "templates/standards/yudao-vben.md",
        "workbench/infrastructure/persistence/store.py",
        "workbench/projects/__init__.py",
        "workbench/projects/models.py",
        "workbench/infrastructure/__init__.py",
        "workbench/infrastructure/persistence/__init__.py",
        "workbench/requirements/clarification.py",
        "workbench/requirements/__init__.py",
        "tests/conftest.py",
        "tests/test_contracts.py",
        "tests/test_store.py",
    ]
    # Include only inert package scaffolding, never future implementation code.
    names.extend(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "workbench").rglob("__init__.py")
        if path.relative_to(ROOT).as_posix() not in names
        and stage_for(path.relative_to(ROOT).as_posix()) == 0
    )
    names.append("workbench/_compat/aliases.py")
    names.extend(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "migrations").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    for name in names:
        if name.startswith("workbench/"):
            assert stage_for(name) <= 2, name
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    env = dict(os.environ, PYTHONPATH=str(destination), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; import sys; "
            "import workbench; import importlib; "
            '[importlib.import_module(".".join(path.parent.parts)) '
            'for path in Path("workbench").rglob("__init__.py")]; '
            "assert not any(name in sys.modules for name in "
            '("workbench.interfaces.http", "workbench.production.worker", '
            '"workbench.infrastructure.llm.gateway")); '
            "from workbench import store, model_settings, clarification; "
            "assert all(Path(module.__file__).resolve().is_relative_to(Path.cwd()) "
            "for module in (store, model_settings, clarification))",
        ],
        cwd=destination,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert probe.returncode == 0, probe.stderr
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_contracts.py", "tests/test_store.py", "-q"],
        cwd=destination,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (destination / "workbench/interfaces/http.py").exists()
    assert not (destination / "workbench/production/worker.py").exists()


def test_relocated_implementations_keep_their_original_learning_stage():
    for relative, original in RELOCATED_MODULES.items():
        assert stage_for(f"workbench/{relative}.py") == MODULE_STAGE[original], relative
    for path in (ROOT / "workbench").rglob("__init__.py"):
        name = path.relative_to(ROOT).as_posix()
        assert stage_for(name) == (7 if name == "workbench/coding/__init__.py" else 0)
    assert stage_for("workbench/_compat/aliases.py") == 0
    assert stage_for("workbench/cli.py") == 8
    assert stage_for("workbench/capability_sandbox.py") == 7
    assert stage_for("workbench/daytona_worker.py") == 12
````
