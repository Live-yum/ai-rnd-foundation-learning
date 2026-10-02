# 14 · 全平台验收与证据阅读

[总目录](../README.md) · [上一阶段](../13-delivery/README.md)

## 现在才到“整个项目”

前面的每站都有一个小而真实的完成条件：合同能拒绝错误、事务能回滚、索引能拒绝过期、产品能运行、状态机能恢复、业务能拒绝越权、交付能在新目录重启。最后的全平台验收不是把这些文字勾选一遍，而是在最终文件集合上重跑对应检查，并核对报告属于同一个源码版本。任何后续改动都可能使旧报告失效。

## 先生成教材，再检查；先准备工具，再跑全套

如果你是从空目录手抄或还原出来的学生项目，根目录的生成版完整手册和新的 `learning-docs` 可能尚不存在。所有第14站源码和正文源文件都齐全后，先生成它们，再用 `--check` 检查；检查命令只核对现有输出，不替你创建缺失输出。

```bash
# .learning/commands/14-build-books.sh
uv run python -m scripts.build_handbook
uv run python -m scripts.build_learning_docs
uv run python -m scripts.build_handbook --check
uv run python -m scripts.build_learning_docs --check
```

完整非PostgreSQL回归也需要第06站的Playwright/Chromium和当前终端的 `PRODUCT_VERIFY_PLAYWRIGHT`、`PLAYWRIGHT_BROWSERS_PATH=0`，以及第11站真实Node组件。先运行 `npm ci --prefix tools/node --no-audit --no-fund` 和 `npm run build --prefix tools/node`。测试必须强制实际Node组件存在，Linux/WSL在同一终端设置：

```bash
# .learning/commands/14-node-required-linux.sh
export RND_REQUIRE_NODE_TESTS=1
```

Windows PowerShell设置：

```powershell
# .learning/commands/14-node-required-windows.ps1
$env:RND_REQUIRE_NODE_TESTS = '1'
```

没有这些前提时先标记阻塞，不把可选工具skip当作全平台通过。然后执行最广的静态与基础回归：

```bash
# .learning/commands/14-base-regression.sh
uv sync --locked --all-extras
uv run ruff check .
uv run ruff format --check .
uv run pytest -m "not postgres" -q
uv run python -m scripts.build_handbook --check
uv run python -m scripts.build_learning_docs --check
```

`ruff` 要真实通过，不能因返回非零就自动改成忽略规则。非PostgreSQL套件包含需要浏览器和若干可选工具的测试，先查看test markers与skip原因；“not postgres”不代表“只需Python且所有工具都模拟”。原有完整手册一致性检查应输出 `Single handbook source consistency PASS`；新分阶段教材的检查命令同样必须退出码为0，二者各自证明对应文档与源码一致，不能互相替代。

最后验证“只带教材目录”的完整重建，而不是从原仓库偷借依赖或ZIP：

```bash
# .learning/commands/14-textbook-clean-room.sh
uv run python -m scripts.ci_learning_docs
```

该脚本复制教材到临时目录，用标准库还原全部自有文件；先按 `PLAYWRIGHT_BROWSERS_PATH=0` 真正启动并关闭Chromium，核对第06站要求的本地浏览器安装位置，再安装学生项目独立venv，从固定上游提交重建三个模板归档，构建真实Node组件，再执行真实完整非PostgreSQL回归。它还核对手册和分阶段教材能再生成一致；不是只检查文件数就打印PASS。需要公开依赖下载、Node和已安装浏览器，成功与否查看 `reports/learning-docs-clean-room.json` 和对应测试结果。超时、依赖失败、测试失败都保留原失败阶段，不能手工把报告中的passed改成true。原生服务、PostgreSQL和Daytona完整矩阵仍需各自环境与证据，这个脚本不声称验证了那些未启动服务。

## 建立一份不冒进的验收记录

每一层写清输入身份、命令、环境前提、实际结果、报告位置和未覆盖范围。建议按下面顺序读证据：

1. 安装与还原：Python3.14、锁文件、完整自有源码、固定第三方归档与许可证；若从教材还原，逐文件hash相等
2. 内核：合同、数据库、需求覆盖、来源冲突、模型协议、幂等与审批恢复
3. 基础产品：生成回执、独立依赖、HTTP、真实浏览器、两用户隔离与重启
4. 客服业务：三角色动作/行范围、关联、分配、命名状态、历史、审计、提醒、指标与查询
5. 原生模板：分别记录FastapiAdmin和Yudao的生成、SQL、编译、类型检查、原生页面与独立新库启动
6. 工具链：实际Continue、Plop、Aider、MCP及可选本机向量；不能只记录安装版本
7. Daytona：对应profile的真实离线执行、重启、端口与沙箱清理；基本镜像不代表全部矩阵
8. 真实模型：服务商实际响应与完整需求流程；不能拿协议夹具或确定性Plan重放来代替

每项只能写passed、failed、pending、skipped或未运行的真实状态。一个总passed不能抵消缺少必须的逐实体/逐字段浏览器checks；一张旧截图不能证明当前提交；某个模板成功不代表另一个模板成功。源码包中的业务数据为空是正确交付边界，不能因此声称真实业务备份恢复已被验证。

## 真实模型与CI有自己的权限边界

`scripts/ci_real_model.py` 是仓库专门的受限真实供应商验收，代码检查固定仓库、允许ref、手动dispatch、地址与模型，不是给任意本地模型的通用命令。不要在本机伪造GITHUB_ACTIONS等变量绕过门禁，也不要改服务商或预算后继续沿用原来的验收名称。普通本机体验使用已完成的 `rnd start/chat` 和你自己的配置；正式真实供应商证明按该工作流的实际授权与证据要求执行。

批准的合成Plan可做确定性重放；失败时保存的Requirement/Plan诊断明确未批准，不能被当作备用生成答案。模型语义审阅同样只提供有依据的额外意见，不能把HTTP或浏览器失败改成成功。

## 完成后能够独立解释的十个问题

不要背文件名，试着从输入走到结果：为什么改模型地址必须换Key？为什么下一轮遗漏不删除事实？为什么批准绑定gate_id？为什么生成器保留旧目录？为什么搜索索引要核对SHA？为什么隐藏按钮不等于权限？为什么状态、审计和提醒同事务？为什么模型不能改测试？为什么新目录要再装依赖？为什么沙箱删除也会阻止交付？

能用本项目的真实函数、调用方和失败测试回答这些问题，才说明你掌握了平台的构造，而不只是拥有一份源码。所有缺失服务与未运行矩阵继续明确列出；完整实现、可运行基础链路、全面环境验收是三个相关但不同的结论。

## 本阶段源码和后续依赖

本阶段首次创建 76 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
