# scripts/ci_native_sources.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：固定原生模板源码完整性检查。** 核对所有已登记归档、许可证、固定提交及关键原生生成器文件，确认仓库真带框架源码。只检查来源的通过不代表服务器或浏览器通过。

**对应关系：** native-sources/verify-bundles → vendor清单与归档 → 来源报告。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.native`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `scripts/ci_native_sources.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L28。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`875`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_native_sources.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "023e7e7808dbaadba040cdce63afa31baa629a860fe1bbbb09635d1d07d10d85"} -->
````python
# scripts/ci_native_sources.py
"""Verify actual fixed upstream commits and indexes; this is NOT native runtime acceptance."""

import json

from workbench.native import prepare_sources
from workbench.settings import ROOT, Settings

settings = Settings(data_dir=ROOT / ".data" / "ci-native", tool_timeout=600, _env_file=None)
results = {
    template: prepare_sources(settings, template, prefer_github=True)
    for template in ("fastapiadmin", "yudao-vben")
}
(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports/native-sources.json").write_text(
    json.dumps(
        {
            "scope": "pinned-source-and-index-only",
            "runtime_verified": False,
            "sources": results,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
print(
    "PASS: fixed source commits, required paths, clean checkout and local index; not runtime certification"
)
````
