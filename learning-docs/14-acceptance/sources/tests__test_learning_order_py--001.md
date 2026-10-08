# tests/test_learning_order.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_database_lesson_runs_from_only_its_documented_files`（L11–L76）：接收`tmp_path`。 控制顺序：L43遍历`names`；L64断言`probe.returncode == 0`；L74断言`result.returncode == 0`；L75断言`not (destination / "workbench/api.py").exists()`；L76断言`not (destination / "workbench/runtime.py").exists()`。 调用`names.extend`、`path.relative_to(ROOT).as_posix`、`path.relative_to`、`(ROOT / "migrations").rglob`、`path.is_file`、`target.parent.mkdir`、`shutil.copyfile`、`dict`、`str`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_learning_order.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L76。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2575`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_learning_order.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0ec7b22990475f17db68f51b36e1240fae9036c301a4ef62a9b8c9b9d6942e64"} -->
````python
# tests/test_learning_order.py
"""The first database lesson must not depend on a future API or agent module."""

import os
import shutil
import subprocess
import sys

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
        "workbench/model_settings.py",
        "workbench/business_contracts.py",
        "workbench/business_capabilities.py",
        "workbench/domain.py",
        "workbench/errors.py",
        "workbench/catalog.py",
        "workbench/template_adapters.py",
        "workbench/template_standards.py",
        "templates/standards/common.md",
        "templates/standards/python-basic.md",
        "templates/standards/fastapiadmin.md",
        "templates/standards/yudao-vben.md",
        "workbench/store.py",
        "workbench/clarification.py",
        "tests/conftest.py",
        "tests/test_contracts.py",
        "tests/test_store.py",
    ]
    names.extend(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "migrations").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    env = dict(os.environ, PYTHONPATH=str(destination), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; "
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
    assert not (destination / "workbench/api.py").exists()
    assert not (destination / "workbench/runtime.py").exists()
````
