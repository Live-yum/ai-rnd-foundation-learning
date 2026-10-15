# workbench/capability_sandbox.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.acceptance`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `workbench/capability_sandbox.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L10。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`279`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_sandbox.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4f0795900a936bcc2a68ec81b927594edd16a9f2ceb684a0171ccbc4a3cfe468"} -->
````python
# workbench/capability_sandbox.py
"""Compatible import and executable entry for workbench.acceptance.capability_sandbox."""

import sys

from workbench.acceptance import capability_sandbox as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation
````
