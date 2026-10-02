# templates/deployment/.python-version · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生独立交付启动器。** 该文件随成品复制，负责本机数据库初始化、业务/菜单SQL恢复和前后端启动。helper文件来自portable.HELPERS的明确清单，不允许从原开发目录隐式导入。

**对应关系：** portable.build_native_delivery → 新目录运行start.py → 新数据库复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/deployment/.python-version`；**本文件共有 1 段**。本段覆盖源文件 L1–L1。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/deployment/.python-version", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a876e0b10411037a012498b9fe18d9bc1df32ed8b722a13564dc944ddcfd9135"} -->
````text
# templates/deployment/.python-version
3.14
````
