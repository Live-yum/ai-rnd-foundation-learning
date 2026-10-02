# 06 · 确定性生成与独立验证

[总目录](../README.md) · [上一阶段](../05-product/README.md) · [下一阶段](../07-orchestration/README.md)

## 一份批准设计怎样变成可运行项目

`generator.generate_basic` 首先校验模板选择与数据范围，再检查目标目录是否为危险链接或已经存在。新目录中复制产品模板、规则解释器和所选前端，冻结 `approved-spec.json` 与 `selection.json`，生成固定迁移并导出参考DDL。最后把设计摘要、选择和完整文件指纹写入目录外的 `generation.json`。参考SQL用于阅读和核对；正常启动由版本化迁移执行，不要再手工把参考SQL执行第二遍。

已存在的产品不是可随时删掉的临时产物。只有相符生成回执时才允许安全重用；缺回执、计划改变、选择改变或目录身份异常都应保留现场并拒绝。这个分支保护产品数据库、用户笔记和人工维护的文件。幂等的含义是“重做同一请求不损坏结果”，不是“每次清空再生成看起来一样”。

`verification.verify_basic` 先将当前manifest与生成回执对比。可信模板、验证器和启动器不能被编码器改动；只允许规则文件走指定路径。然后解析源码、运行正反规则样例、安装产品自己的锁定依赖，调用 `run_probe → verify.py` 进行迁移、真实HTTP、重启和浏览器检查。最后把源码摘要绑定到报告，防止测试过后换一份文件仍拿旧报告交付。

## 先检验保护，再准备浏览器

```bash
# .learning/commands/06-generator-contracts.sh
uv run pytest tests/test_generation_preservation.py -q
```

应无 failed/error。该组测试故意破坏回执并放入用户文件哨兵，验证失败后每个字节仍在；它并不证明产品已经启动。

完整 simple-admin 产品需要真实浏览器。先打开 [Node.js官方下载页](https://nodejs.org/en/download)，在版本选择中明确选22.x（至少22.13），再选你的系统与架构，使用官方安装器/预编译包；不要直接采用页面默认的另一个主版本。也可在 [官方版本归档](https://nodejs.org/en/download/archive) 查找22.x。安装后重开终端，运行 `node --version` 和 `npm --version`；前者应是v22.x且不低于22.13。安装到其他终端的Node不一定进入当前PATH。

Linux/WSL在项目根目录执行：

```bash
# .learning/commands/06-browser-linux.sh
npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
export PLAYWRIGHT_BROWSERS_PATH=0
node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
export PRODUCT_VERIFY_PLAYWRIGHT="$PWD/.native/browser/node_modules/playwright"
```

Windows PowerShell执行对应版本：

```powershell
# .learning/commands/06-browser-windows.ps1
npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
$env:PLAYWRIGHT_BROWSERS_PATH = '0'
node .native/browser/node_modules/playwright/cli.js install chromium
$env:PRODUCT_VERIFY_PLAYWRIGHT = (Resolve-Path '.native/browser/node_modules/playwright').Path
```

Linux `--with-deps` 可能需要本机管理员安装系统库，按系统提示由你处理。环境变量仅对当前终端及子进程有效，后续平台和测试从同一终端启动。模块路径不是浏览器URL，也不是Chromium可执行文件。安装失败要先修复环境，不通过改成 api-only 来规避本来选择的页面验收。

## 保存一个真正运行的生成练习

保存为 `.learning/checks/06_generate.py`：

```python
# .learning/checks/06_generate.py
from pathlib import Path
from tempfile import TemporaryDirectory
from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.settings import Settings
from workbench.verification import verify_basic

plan = Plan(
    title="请求标题练习",
    data_scope="per_user",
    acceptance=["CRUD与两用户隔离"],
    entities=[
        {
            "name": "request",
            "description": "请求",
            "fields": [{"name": "title", "kind": "text", "max_length": 80, "searchable": True}],
        }
    ],
)
with TemporaryDirectory(prefix="rnd-learning-generation-") as temporary:
    root = Path(temporary)
    product = root / "run/product"
    settings = Settings(
        data_dir=root / "state",
        database_url="",
        install_products=True,
        tool_timeout=600,
        _env_file=None,
    )
    generation = generate_basic(
        plan,
        product,
        {"template": "python-basic", "frontend": "simple-admin", "database": "sqlite"},
    )
    assert "approved-spec.json" in generation["files"]
    report = verify_basic(plan, product, settings)
    assert report["passed"] is True and report["http"] and report["restart"]
    assert report["browser"]["real_browser"] is True
    assert report["isolated_dependencies"] is True
print("06 PASS: generated files, isolated dependencies, real HTTP/browser and restart")
```

```bash
# .learning/commands/06-runtime.sh
uv run python .learning/checks/06_generate.py
uv run pytest tests/test_product_browser_gate.py -q
```

只有实际执行并出现 `06 PASS` 才能记“产品运行通过”。这个Plan是公开写在练习里的确定性输入，不是假装来自模型。还没有测试后续流程图；下一站才让需求、审批和这些工具衔接起来。

## 本阶段源码和后续依赖

本阶段首次创建 6 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
