# tests/test_portable_helper_layout.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.delivery.portable`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_portable_helpers_include_package_parents`（L13–L23）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L14断言`len(HELPERS) == len(set(HELPERS))`；L15断言`"_compat/__init__.py" in HELPERS`；L16断言`"_compat/aliases.py" in HELPERS`；L17遍历`HELPERS`；L18断言`(ROOT / "workbench" / name).is_file()`；L19遍历`Path(name).parents`；L20按`str(parent) != "."`分支；L21断言`(parent / "__init__.py").as_posix() in HELPERS`。后续分支沿下方源码相同行号继续阅读。 调用`len`、`set`、`(ROOT / "workbench" / name).is_file`、`Path`、`str`、`(parent / "__init__.py").as_posix`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_portable_helpers_import_without_checkout`（L26–L74）：接收`tmp_path`。 控制顺序：L28遍历`HELPERS`；L32遍历`HELPER_RESOURCES`；L73断言`result.returncode == 0`；L74断言`"--check" in result.stdout`。 调用`target.parent.mkdir`、`shutil.copyfile`、`name[:-3].replace`、`name.endswith`、`subprocess.run`、`str`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_portable_helper_layout.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L74。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2978`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_portable_helper_layout.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b4137f533f93494fe1fc045132cb89e67f3b31f0321eb5b82071394813fa3808"} -->
````python
# tests/test_portable_helper_layout.py
"""Standalone native delivery must resolve its own deliberately bounded helpers."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from workbench.delivery.portable import HELPER_RESOURCES, HELPERS
from workbench.settings import ROOT


def test_portable_helpers_include_package_parents():
    assert len(HELPERS) == len(set(HELPERS))
    assert "_compat/__init__.py" in HELPERS
    assert "_compat/aliases.py" in HELPERS
    for name in HELPERS:
        assert (ROOT / "workbench" / name).is_file(), name
        for parent in Path(name).parents:
            if str(parent) != ".":
                assert (parent / "__init__.py").as_posix() in HELPERS
    assert "production/worker.py" not in HELPERS
    assert "interfaces/http.py" not in HELPERS


def test_portable_helpers_import_without_checkout(tmp_path):
    deployment = tmp_path / "deployment"
    for name in HELPERS:
        target = deployment / "workbench" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "workbench" / name, target)
    for name in HELPER_RESOURCES:
        target = deployment / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    shutil.copyfile(ROOT / "templates/deployment/run.py", deployment / "run.py")
    modules = [
        "workbench." + name[:-3].replace("/", ".")
        for name in HELPERS
        if not name.endswith("__init__.py")
    ]
    code = """
import importlib, importlib.abc, pathlib, runpy, sys
class NoPlatformServices(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.', 1)[0] in {'fastapi', 'langgraph', 'daytona'}:
            raise ModuleNotFoundError('Platform-only dependency in delivery: ' + fullname)
sys.meta_path.insert(0, NoPlatformServices())
root = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
for name in __import__('json').loads(sys.argv[2]):
    module = importlib.import_module(name)
    assert pathlib.Path(module.__file__).resolve().is_relative_to(root), name
from workbench.settings import ROOT
assert ROOT == root
from workbench.catalog import Selection
assert Selection(template='fastapiadmin').template == 'fastapiadmin'
from workbench.native_environment import checked_database
assert checked_database is importlib.import_module(
    'workbench.infrastructure.native.environment').checked_database
assert 'workbench.production.worker' not in sys.modules
assert 'workbench.interfaces.http' not in sys.modules
sys.argv = ['run.py', '--help']
runpy.run_path(str(root / 'run.py'), run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code, str(deployment), json.dumps(modules)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "--check" in result.stdout
````
