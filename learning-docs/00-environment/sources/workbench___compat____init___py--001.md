# workbench/_compat/__init__.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：旧导入名的惰性兼容注册。** 维护精确旧名到功能目录的映射；只有请求旧模块时才加载唯一实现，并共享模块对象及monkeypatch。注册本身不加载未来教材阶段。

**对应关系：** workbench包入口 → _compat注册 → 按需导入功能目录实现。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_AliasLoader`（L15–L25）：继承`importlib.abc.Loader`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `_AliasLoader.__init__`（L16–L17）：接收`target`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_AliasLoader.create_module`（L19–L21）：接收`spec`。 返回路径：L21的`None`。
- `_AliasLoader.exec_module`（L23–L25）：接收`module`。 调用`importlib.import_module`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_AliasFinder`（L28–L35）：继承`importlib.abc.MetaPathFinder`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `_AliasFinder.find_spec`（L31–L35）：接收`fullname`、`path`、`target`。 控制顺序：L33按`implementation is None`分支。 调用`ALIASES.get`、`importlib.util.spec_from_loader`、`_AliasLoader`。 返回路径：L34的`None`；L35的`importlib.util.spec_from_loader(fullname, _AliasLoader(implementation))`。
- `install`（L38–L41）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Install once, after normal finders; real modules always take precedence.。 控制顺序：L40按`not any(getattr(finder, "_workbench_legacy_aliases", False) for finder in sys.meta_pa…`分支。 调用`any`、`getattr`、`sys.meta_path.append`、`_AliasFinder`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/_compat/__init__.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L41。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1322`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/_compat/__init__.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "81b189738c1e6c28f7e056aedc0676e32f589e021b47a162ddd203325866c57c"} -->
````python
# workbench/_compat/__init__.py
"""Lazy, exact legacy module aliases with the canonical module's identity.

This is import compatibility only. Executable legacy names keep physical entry
points. No target is imported during installation, including optional runtimes.
"""

import importlib
import importlib.abc
import importlib.util
import sys

from .aliases import ALIASES


class _AliasLoader(importlib.abc.Loader):
    def __init__(self, target):
        self.target = target

    def create_module(self, spec):
        # Returning the target here would let importlib replace its canonical spec.
        return None

    def exec_module(self, module):
        implementation = importlib.import_module(self.target)
        sys.modules[module.__name__] = implementation


class _AliasFinder(importlib.abc.MetaPathFinder):
    _workbench_legacy_aliases = True

    def find_spec(self, fullname, path=None, target=None):
        implementation = ALIASES.get(fullname)
        if implementation is None:
            return None
        return importlib.util.spec_from_loader(fullname, _AliasLoader(implementation))


def install():
    """Install once, after normal finders; real modules always take precedence."""
    if not any(getattr(finder, "_workbench_legacy_aliases", False) for finder in sys.meta_path):
        sys.meta_path.append(_AliasFinder())
````
