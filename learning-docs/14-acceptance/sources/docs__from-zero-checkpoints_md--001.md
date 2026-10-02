# docs/from-zero-checkpoints.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本教材正文的源文件。** 上文正文就是这些源文件拼接后的内容。它们也收录在附录中，使从教材还原出的项目能再次生成逐字一致的完整教材，而不是只有一次性的代码快照。

**对应关系：** scripts/build_handbook.py的GUIDES → 正文 → 完整源码附录。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `docs/from-zero-checkpoints.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L138。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12983`。本段原文以LF换行结束。

<!-- learning-source: {"path": "docs/from-zero-checkpoints.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1ea5bb1ed41c5a4037c5c0335e8c84cd9950a5d1a869467d05ffa4c42f86d952"} -->
````markdown
<!-- docs/from-zero-checkpoints.md -->
# 从空目录到可信交付：逐站实操与证据阅读

这一章是学习过程的检查路线。完整源码附录给出最终实现；这里说明每站先准备什么、亲手执行什么、看到什么才可以继续。命令默认在含`pyproject.toml`的项目根目录执行。终端出现绿色文字、页面出现下载按钮、模型说“完成”，都不能单独证明验收通过。

## 一、先分清四个目录与三种数据库

- **教材存放目录**：只放这份Markdown和手写的`rebuild_book.py`，不要与还原目标混用。
- **平台源码目录**：自己按文件路径逐个创建的代码，或者由教材源码块还原出的空目标目录。这里运行`uv sync`、`rnd`和测试。
- **平台运行目录**：默认`.data/`，保存会话、检查点、索引、任务输出和本机工具配置。它不是供交付的源码，也不能整个上传。
- **独立产品目录**：把最终ZIP解压到全新目录。这里运行产品的`start.py`，不能靠把平台目录加入PYTHONPATH来补缺文件。

平台控制数据库存项目、消息与审批；检查点数据库存流程暂停位置；产品数据库存最终用户和业务记录。原生模板代码生成时使用的临时数据库、Daytona沙箱内的数据库，也不等于你的正式产品数据库。遇到“数据库非空”要换专用空库或调查归属，不要先DROP再说。

## 二、站点0：只有一本书，也能得到完整自有源码

先完成“逐文件实现讲解”的A节，理解缩进、函数、模块、路径与JSON。随后从空文件夹按B节的顺序新建文件；每个附录标题就是相对路径，代码块必须完整保存。手工输入的好处是理解依赖，代价是容易漏字符；不能用省略号、`pass`或从别处借一个骨架替代缺失实现。

也可以先手写书中给出的标准库提取程序`rebuild_book.py`，把这本书放在旁边。它验证每块源码的SHA、拒绝危险路径和非空目标，只写文件，不执行所还原的源码。按该节命令还原后，仍按下列站点学习和验证。还原不是证明代码安全；读清将执行的安装与资源创建操作后再运行。

全部文件写齐后检查：

```powershell
uv python install 3.14
uv sync --locked --all-extras
uv run python -m compileall -q workbench
uv run python -m scripts.build_handbook --check
```

最后一条必须输出`Single handbook source consistency PASS`。如果只有你手写的源码而没有根目录生成手册，先运行不带`--check`的`build_handbook`生成它，再检查。这里验证源码与正文一致，不代表数据库、浏览器或Daytona已经运行过。

独立的 `handbook-only` Actions 会把这一本书复制到临时目录，重建自有源码、固定第三方
归档和 Continue，再实际执行完整非 PostgreSQL 套件。整套测试子进程的明确预算为
1800 秒，外层 job 仍限制 40 分钟；安装等其他步骤沿用自己的预算，单项测试和浏览器等待
没有因此放宽。超时始终失败，只中断和清理本次启动的测试进程，尽量让 pytest 写出 JUnit。
`handbook-test-status.json` 记录阶段、预算、退出码、超时与清理状态，已产生的 JUnit 也会
保留；这些诊断不能替代完整测试通过后的 `handbook-clean-room.json`。

普通全套测试的 job 总预算按平台区分：Linux 为 35 分钟，Windows 为 60 分钟，包含安装
依赖和运行完整测试。Windows 的冷安装会占用较长前置时间；这个外层预算不修改任何
浏览器、接口或单个测试的超时，也不会让被中断的套件变成通过。捕获子进程文本明确按
UTF-8 解码，不能依赖 Windows 当前的 cp1252 等本地编码。

第三方框架不由你从零重写。按书中完整的`vendor_templates.py`、manifest和许可证重建固定上游源码归档，再运行`rnd init`。`uv.lock`、Node的`package-lock.json`和模板固定提交各自约束不同依赖，不可互相替代。

## 三、站点1：先让合同与数据库独立成立

```powershell
uv run pytest tests/test_contracts.py tests/test_business_contracts.py tests/test_business_capabilities.py tests/test_store.py tests/test_learning_order.py -q
```

看源码时跟随这条链：输入字典 → Pydantic合同 → Store事务 → 数据库记录。试着指出字段名拼错在哪里被拒绝、事务失败在哪里回滚、重复请求为什么不多创建一次任务。这里用临时数据库，不需要你的模型密钥。不要提前启动网页掩盖尚未写齐的数据库模块。

控制面可启动之后再执行：

```powershell
uv run rnd init
uv run rnd doctor
uv run rnd start
```

`doctor`报告真实模型缺项时，到本机`.env`填写`BASE_URL`、`API_KEY`、`MODE`。不同阶段改服务地址，必须同时填那个服务的专用密钥。不要把测试夹具当作未配置模型时的生产答案。

## 四、站点2：先检索真实源码，再把上下文交给模型

默认检索只需平台Python依赖，Java/TypeScript/JavaScript的Tree-sitter grammar已在锁文件中声明，不需要另装一个云端解析服务。先运行第20章的`rnd index`与`rnd tools search`。打开结果中的文件，核对起止行和符号；修改一行后，旧索引应要求重建，而不是继续给模型过期代码。

真实Continue全文索引另需Node 22.13或更新的22.x：先`npm ci --prefix tools/node`，再`npm run build --prefix tools/node`，最后在`.env`选择`RETRIEVAL_ENGINE=continue`。它与VS Code扩展是两件事：前者是平台调用的固定原生组件，后者是可选的人机界面。MCP只提供同一套只读检索，不新增任意写文件能力。

向量检索也是独立选择。启用前先按第20章运行本机embedding端点的最小请求；成功后再建向量。模型权重安装成功不等于请求实际在本机推理，更不能因为本机端点连不上就改成公网工具地址。

## 五、站点3：生成器、Plop、Aider各做一件可核查的事

先学习客服确定性生成：已批准Plan.business → generator/native generator → 框架专用业务适配 → 实际文件 → 角色、关联、流程、提醒和统计的独立验证。声明式客服合同无须调用编码模型。只有额外的单记录业务规则需要编码时，才准备独立Aider环境：

```powershell
uv sync --locked --project tools/aider --python 3.12
uv run --locked --project tools/aider --python 3.12 python tools/aider/offline_runner.py --check-local-deps
```

输出必须说明固定Aider版本和禁网状态。平台的Python 3.14环境仍独立存在；不要为了解决依赖冲突，把两套环境合并。

原生模板的对应关系是：原生生成器创建可运行模块及菜单权限 → node-plop按受信任模板添加规则文件和表单入口 → 平台模型网关提出规则表达式 → 本机Aider在受限Git副本里实际应用补丁 → 编译/API/浏览器验证决定是否接受。任何一步缺失都不能只写一份同名JSON冒充执行。

从代码学习失败路径尤其重要：未知文件、过期前像、匹配多处、修改鉴权或锁文件应拒绝；不通过反例的候选要回滚并保留诊断；超过修复次数应阻塞。失败不能通过删除反例或把前端从simple-admin改成api-only来消失。

## 六、站点4：给浏览器验收准备真实环境

`simple-admin`是可交互产品，HTTP接口通过后还必须由真实浏览器检查页面。先安装Node22，再在平台根目录安装固定Playwright。Windows PowerShell：

```powershell
npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
$env:PLAYWRIGHT_BROWSERS_PATH = '0'
node .native/browser/node_modules/playwright/cli.js install chromium
$env:PRODUCT_VERIFY_PLAYWRIGHT = (Resolve-Path '.native/browser/node_modules/playwright').Path
```

Linux/WSL Bash：

```bash
npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
export PLAYWRIGHT_BROWSERS_PATH=0
node .native/browser/node_modules/playwright/cli.js install --with-deps chromium
export PRODUCT_VERIFY_PLAYWRIGHT="$PWD/.native/browser/node_modules/playwright"
```

`--with-deps`会安装Linux浏览器所需系统库；普通用户的机器可能提示输入本机管理员密码，由你在终端按系统提示处理。运行时不应自动下载安装浏览器。环境变量只对当前终端及其子进程生效，从同一终端启动平台和测试；重开终端后重新设置。`PRODUCT_VERIFY_PLAYWRIGHT`指向工具模块目录，不是Chromium可执行文件，更不是远程浏览器URL。

产品独立验收也可以在产品根目录安装同一工具，或显式使用上述已安装模块的绝对路径。复用的是测试工具，不是平台业务代码或平台数据库。缺Node、模块或Chromium应明确失败；api-only没有前端，报告标记不适用，但不能把带前端的任务改成api-only以绕过验收。

客服源码连接关系是`workbench.verification.run_probe → templates/product/verify.py → verify_business.py → verify-business-browser.cjs`；无business合同的普通实体测试使用`verify-browser.cjs`。`require_browser_evidence`再次按approved-spec核对全部实体、字段对应的检查名称以及零页面错误；缺少一个应有的检查也不能通过。`verify.py`和CJS脚本一同进入产品ZIP，干净解压后再次运行同一验证链。

客服测试不仅看首屏，还应覆盖客户/请求/任务新增编辑、关联选择、分配、状态转换、备注、归档、历史、提醒、统计、越权拒绝及重启后的数据；普通字段查询继续覆盖关键词、筛选、清除条件与分页。真实表单测试要走页面操作，不靠注入登录令牌、替换接口结果或只截一张静态图。相同源码生成的独立解压目录需要再验证，不能拿生成目录的报告当作解压目录已经通过。

## 七、站点5：启动原生框架，再准备对应Daytona快照

按原生章节安装Linux/WSL本机PostgreSQL/Redis、Node22、模板对应pnpm；芋道还需JDK17/Maven。先完成无Daytona的原生生成、权限、编译、类型检查、浏览器和独立新库启动。只有项目本来可运行，制作离线快照才有意义。

Daytona固定0.190.0。按第20章依次执行`prepare → images → snapshot-image → up → auth → snapshot`；每条成功才运行下一条。控制面服务、Runner、Registry、Dex与存储都在本机。CLI安装好、API健康正常、快照active、业务运行通过、沙箱删除成功是五项不同事实。

Python/SQLite用基础快照；Python/PostgreSQL、FastapiAdmin/PostgreSQL、Yudao/PostgreSQL使用各自登记的matrix快照。根据实际生成目录预热依赖后，把回执中的准确名称配置进`DAYTONA_SNAPSHOTS`。不能把未安装Java依赖的Python快照改名，或把主机测试库的密码传进沙箱。

沙箱验证在禁外网情况下执行。缺依赖就回到显式准备阶段，失败不自动开放网络。退出应用后先确认本次端口都关闭，再验证重启；删除本次沙箱是交付条件，不是可选的收尾动作。

## 八、怎样阅读“完成”的证据

| 证据层 | 可以证明什么 | 单独不能证明什么 |
|---|---|---|
| 源码和锁文件 | 实现与依赖被固定、可复查 | 程序在某台机器真正运行过 |
| 单元/合同测试 | 给定输入和边界处理符合断言 | 真实浏览器、第三方服务或用户模型已验证 |
| 本机完整运行报告 | 本次源码通过实际运行的对应检查 | 另一个提交、另一数据库或另一产品也通过 |
| 浏览器报告与截图 | 本次真实页面流程、断言和错误记录 | 任意浏览器/任意设备帧率，或未覆盖业务 |
| 独立解压与新库复验 | 包内自有代码足够启动，初始数据库迁移可运行 | 正式用户数据的备份恢复已验证 |
| Daytona报告与清理回执 | 已登记本机沙箱内的对应关卡及资源清理 | 托管云服务、未登记矩阵或生产级强隔离 |
| 同一提交的正式Actions | 当前提交在相应Runner与任务上的结果 | 本地修改后还未推送的新源码已通过 |

报告写着失败、pending或没有报告，就按其原样记录。测试模型夹具明确验证编排，不证明你填写的真实供应商质量。可选向量服务未启动、原生服务未运行、Daytona未准备时，都应写“未验证”或说明具体阻塞，不使用“全部完成”。

最后执行源码一致性检查与对应回归，保留同一提交的真实日志。修改自有源码或正文后重新生成唯一的`从零实现AI研发平台_逐步实操手册_完整版.md`；不要另外维护带版本后缀的手册，也不要仅手改生成结果而让教材与代码分叉。
````
