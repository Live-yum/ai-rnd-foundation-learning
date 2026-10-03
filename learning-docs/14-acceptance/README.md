# 14 · 全平台验收与证据阅读

[总目录](../README.md) · [上一阶段](../13-delivery/README.md)

## 现在才到“整个项目”

前面的每站都有一个小而真实的完成条件：合同能拒绝错误、事务能回滚、索引能拒绝过期、产品能运行、状态机能恢复、业务能拒绝越权、交付能在新目录重启。最后的全平台验收不是把这些文字勾选一遍，而是在最终文件集合上重跑对应检查，并核对报告属于同一个源码版本。任何后续改动都可能使旧报告失效。

## 先生成教材，再检查；先准备工具，再跑全套

如果你是从空目录手抄或还原出来的学生项目，根目录的生成版完整手册和新的 `learning-docs` 可能尚不存在。所有第14站源码和正文源文件都齐全后，先按第08站从ui源码构建静态资产，再生成它们，最后用 `--check` 检查；检查命令只核对现有输出，不替你创建缺失输出。

```bash
# .learning/commands/14-build-books.sh
npm ci --prefix ui --no-audit --no-fund
npm test --prefix ui
npm run build --prefix ui
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

该脚本复制教材到临时目录，用标准库还原全部自有文件；先按 `PLAYWRIGHT_BROWSERS_PATH=0` 真正启动并关闭Chromium，核对第06站要求的本地浏览器安装位置，再安装学生项目独立venv；用还原出的ui/package-lock.json执行npm ci、Vitest、类型检查和生产构建，并将所有新资产与教材快照逐字节比较；然后从固定上游提交重建三个模板归档，构建真实Node组件，执行还原平台的真实Vue浏览器验收，再执行真实完整非PostgreSQL回归。它还核对手册和分阶段教材能再生成一致；不是只检查文件数就打印PASS。需要公开依赖下载、Node和已安装浏览器，成功与否查看 `reports/learning-docs-clean-room.json` 和对应测试结果。超时、依赖失败、测试失败都保留原失败阶段，不能手工把报告中的passed改成true。原生服务、PostgreSQL和Daytona完整矩阵仍需各自环境与证据，这个脚本不声称验证了那些未启动服务。

## 单独执行Vue真实页面验收

在第06站安装的Playwright 1.56.1/Chromium可用、当前终端已设置PRODUCT_VERIFY_PLAYWRIGHT及PLAYWRIGHT_BROWSERS_PATH=0、tools/node已安装构建、ui已按第08站构建后，于项目根目录执行：

```bash
# .learning/commands/14-vue-browser.sh
uv run python -m scripts.ci_guided_browser
```

这条命令启动真实本机FastAPI和Chromium，用明确的本机HTTP模型夹具控制增量及结束时机，操作Vue页面、人工/委托关卡、刷新、过期冲突、设置和下载，还保留生成产品页面回归。它不使用真实供应商账号。阅读 `reports/guided-browser/summary.json`、`workbench.json`、各步骤log与 `screenshot-manifest.json`，同时检查实际桌面/窄屏截图；启动或任何断言失败都不得叫通过。单独的pytest夹具保护测试不等于执行了这条浏览器命令。

`ci_learning_docs` 也会在只从教材还原的新项目中调用同一driver，每次独立证据复制到 `reports/learning-docs-guided-browser/本次唯一编号`，当前目录记在learning-docs-clean-room.json的frontend.browser.evidence_directory中，失败重跑不混入上次成功summary或截图，再进入完整非PostgreSQL套件。源工作区浏览器成功和教材还原后浏览器成功分别记录，不能互借结果。失败时保留已经产生的日志或截图，不改场景、移除认证或写入假summary来通过。

## 建立一份不冒进的验收记录

每一层写清输入身份、命令、环境前提、实际结果、报告位置和未覆盖范围。建议按下面顺序读证据：

1. 安装与还原：Python3.14、锁文件、完整自有源码、固定第三方归档与许可证；若从教材还原，逐文件hash相等
2. 内核与操作台：合同、数据库、需求覆盖、来源冲突、真实增量协议、本机设置、幂等与审批恢复；Vue类型/组件测试和真实浏览器另有结果
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

## 怎样证明流式页面，而不是证明打字动画

后端协议测试要让受控HTTP响应先发两个有间隔的增量、最后才结束，并断言结束前已有公开delta；Vue解析器单元测试检查半帧、中文分块，状态单元测试检查认证、幂等键与锁定后的迟到请求。openRun订阅、真实刷新/重连去重、切换任务和草稿到完成的联动由浏览器验收另行操作，不能把纯函数测试当作整条页面链已通过。三层各证明一段链，不相互冒充。

失败流必须清掉未验证草稿，非流服务必须标记non_streaming，断开订阅不能额外调用模型或停止持久Worker。设置页要实际操作保留/更换/清除Key与409版本冲突，不能把“表单保存”记为“供应商连接测试”。所有测试输入用合成Key和受控协议；如未运行真实付费供应商，报告明确写未运行。

`reports/learning-docs-clean-room.json` 的frontend字段记录目录还原后的独立npm测试、类型/构建、资产字节比较，以及还原平台的真实HTTP/Chromium流式页面结果。只运行manifest校验或格式检查不能替它填写passed。UI改动后必须在最终组合源码上重生两套教材并运行受影响验证，之前文档版本或原型截图不能当新界面的验收结果。

## 报名入口与历史FAILED恢复的独立浏览器证据

在上面的真实浏览器前提全部成立后，另跑报名范围专用driver：

```bash
# .learning/commands/14-signup-scope-browser.sh
uv run python -m scripts.ci_signup_scope_browser
```

`scripts/signup_scope_browser.cjs` 操作真实Vue页面与本机API，模型使用显式进程内需求网关夹具。它先恢复一个真实旧FAILED设计检查点，核对同run身份、原始报名目标和既有delegated-ai审批，再检查桌面/窄屏能力提示、旧进度不误显示完成、范围没有默认选项、重复智能推荐不消耗模型调用，以及先选管理员后改选登录后自行提交时只发送最终选择。成功停在WAITING_REQUIREMENTS，不启动原生生成，也不宣称新建任务、显式匿名分支或全部原生全栈的浏览器验收已经完成；这些范围分支另由后端回归保护。

`ci_learning_docs` 在教材独立还原后也执行该driver，并把本次证据单独复制到 `reports/learning-docs-signup-scope-browser/本次唯一编号`。它必须先检查 `browser.json` 的真实浏览器、范围及恢复断言和进程内夹具模式，并核对ui_bundle_sha256与还原后的资产、screenshot_sha256与保留的PNG字节一致，才可进入最终全套通过；任何缺字段、假布尔值、失败或遗留summary都不能冒充成功。流式页面证据和报名范围证据分别保存，各自的失败日志/截图仍应保留。

## 本阶段源码和后续依赖

本阶段首次创建 102 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
