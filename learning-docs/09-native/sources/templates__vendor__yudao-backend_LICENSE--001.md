# templates/vendor/yudao-backend.LICENSE · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：第三方源码来源与许可证。** 模板属于第三方依赖。manifest记录固定提交、归档哈希、逐文件内容摘要及排除项；LICENSE原样保留。只从教材也可以用vendor_templates --fetch重建源码归档，不需要复制本仓库已有ZIP。

**对应关系：** scripts/vendor_templates.py → manifest/ZIP → workbench/vendor.py → 原生生成器。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/vendor/yudao-backend.LICENSE`；**本文件共有 1 段**。本段覆盖源文件 L1–L20。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1078`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/vendor/yudao-backend.LICENSE", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "97a686c1ae6de87e52c50f23d032ef29e9ea7ce4ed2b4b40d9a62006f1b8329e"} -->
````text
# templates/vendor/yudao-backend.LICENSE
The MIT License (MIT)

Copyright (c) 2021 yudao-cloud

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
````
