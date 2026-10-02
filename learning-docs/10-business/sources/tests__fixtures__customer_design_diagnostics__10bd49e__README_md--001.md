# tests/fixtures/customer_design_diagnostics/10bd49e/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/10bd49e/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L9。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`677`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/10bd49e/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "09f8534ed548c10c05d5e02d9cd16b952aef730f7500c95e8cf4ddebf4992616"} -->
````markdown
<!-- tests/fixtures/customer_design_diagnostics/10bd49e/README.md -->
# Actual approved Plan, later rejected by customer acceptance

`python-approved-plan.json` is the exact normalized synthetic customer Plan from
DeepSeek run [36803597792](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36803597792),
job `110183065253`, source commit `10bd49e7e77e94dc8d2670fc949ef4ec9dad1876`, artifact `11136602792`.
SHA-256: `f4638440b66622db35ffd919613aa608656889eb5a1d96ee80651fbf7e0c19f0`.
The workflow reached READY but separate customer acceptance rejected the extra
`customers.published_on` field. This fixture is used only to replay that validation
failure, never as a substitute for a genuine model generation or delivery result.
````
