# tools/aider/.python-version · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Aider独立运行环境。** 固定Python3.12和Aider版本，避免它的依赖影响Python3.14平台；平台通过子进程运行这个环境的CLI，不把它导入平台解释器。

**对应关系：** uv sync --locked --project tools/aider --python 3.12 → workbench.aider_tool。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/aider/.python-version`；**本文件共有 1 段**。本段覆盖源文件 L1–L1。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/aider/.python-version", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7b55f8e67b5623c4bef3fa691288da9437d79d3aba156de48d481db32ac7d16d"} -->
````text
# tools/aider/.python-version
3.12
````
