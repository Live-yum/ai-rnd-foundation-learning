# 原生业务规则、Plop 与本机 Daytona 的完整实现

本章把原生框架生成的 CRUD 接到真正的代码编辑与执行环境。先保留原生生成器负责目录、数据库表、权限菜单和基本接口；再用 Plop 创建可定制的业务规则文件、可见的 Vue 规则说明组件和表单调用入口；最后用 Aider 修改明确批准的业务表达式。不能让模型修改鉴权、数据库连接、依赖锁、验收脚本，或通过删除失败测试获得通过。

## 从空目录接着创建哪些文件

本章所有文件的完整内容均在附录同名路径，不能把说明段落当成代码粘进文件。已经完成前面平台、原生生成器和基本本机 Daytona 的章节后，依次创建下表文件。没有 Git 仓库骨架时，可以手工按路径新建，也可以执行教材中的标准库提取程序；两种方式得到相同文件。

| 创建顺序与文件 | 为什么创建、连接到哪里 | 完成后的检查 |
|---|---|---|
| `tools/node/package.json`、`package-lock.json` | 锁定真实 `node-plop==0.32.3`。它是 Plop 的生成引擎，而不是本平台重新实现的模板工具。 | `npm ci --prefix tools/node --no-audit --no-fund`。安装应成功且不得改锁文件。 |
| `tools/node/templates/rule.py.hbs`、`rule.java.hbs`、`rule.vue.hbs` | Plop 的受信任模板。Python/Java 模板提供布尔规则入口，Vue 模板同时导出校验函数和显示业务说明的组件。 | `tests/test_native_tools.py` 检查模板、实际 Plop 执行及禁止覆盖。 |
| `tools/node/plop-runner.mjs` | Node 调用实际 Plop `runActions` 执行新增和精确修改；不接受用户 plopfile 或 shell。 | Python 适配器使用禁网入口调用，输出实际安装版本与动作数。 |
| `workbench/scaffolding.py` | 从批准后的实体名和真实原生生成文件计算路径和锚点；在临时目录完整执行 Plop，再核对源文件身份和输出集合后写回。失败恢复已写入文件，不覆盖旧业务文件。 | 原生 `schema.py`/SaveReqVO 和表单导入新的业务规则入口，`plop.json` 保存来源和哈希。 |
| `workbench/native_coding.py` | 把注册文件及 SHA 发给平台模型网关，接受完整 SEARCH/REPLACE。Aider 在独立 Git 工作区实际应用；前像、唯一匹配、输出、表达式范围和文件集合必须全部一致。 | `coding-N.json`、Git journal 和原生正反例验收；失败候选回滚。 |
| `workbench/native_business_checks.py` | 实际创建、读取、修改、删除批准的正反例。负例必须是业务校验拒绝，不能是服务器崩溃、权限失败或字段格式错误。 | 检查拒绝的新增没有记录，拒绝的修改不改变原记录，合法修改仍成功。 |
| `scripts/native_browser.cjs` | 真正打开原生登录页和业务表单；验证 Plop 组件可见、负例在前端拦截且没有发送写请求、正例提交成功。 | Chromium 报告、截图、实际网络响应。没有注入登录令牌或模拟路由。 |
| `workbench/daytona_profiles.py` | 登记模板/数据库矩阵、快照依赖身份及严格运行报告。 | 不匹配快照、缺失字段、整数/字符串冒充布尔通过均拒绝。 |
| `tools/daytona/matrix.Dockerfile`、`warm.py` | 显式安装公开工具依赖，预热 uv/pnpm/Maven/Chromium；运行时不下载，不依赖云端账户。 | 使用锁文件构建，镜像 ID、输入哈希和 profile 写入本机。 |
| `scripts/daytona_matrix_image.py` | 从已生成项目制作受限构建上下文，排除凭据、数据库、缓存和用户环境，然后推送至本机 registry。 | `snapshot-image.json`，其名称、资源、镜像身份均须符合登记规则。 |
| `scripts/daytona_matrix_probe.py`、`workbench/owned_lifecycle.py` | 在无外网沙箱内创建独立 PostgreSQL/Redis，执行独立项目启动器、编译、类型检查、权限/CRUD/规则/浏览器/重启。先正常结束启动器并确认全部应用端口关闭，再启动第二次。 | 数据库凭据随机生成且只在沙箱内使用；旧服务残留、退出超时都阻止通过，不能用旧进程冒充重启。 |
| `scripts/ci_native_tools.py`、`ci_daytona_matrix.py`、对应 Actions | 用明确测试模型响应，故意提供错误规则，再验证自动修复、回滚和真实完整运行。测试夹具不是生产模型的后备答案。 | 各阶段执行命令成功，最后才允许 `passed=true`。 |

## 业务规则是如何从需求进入原生代码的

`Plan.custom_rules` 中每个原生实体登记一个合并后的规则，以及完整正例和反例。例如“设备数量不能为负”，正例数量 0、7，反例数量 -1，同时给出其他必填字段。规则必须作用于同一条记录，当前字段类型是原生模板实际支持的文本、整数和布尔。支付、外部采集、跨记录事务等不能伪装成单条布尔校验。

`Workflow.design → generate → native_delivery.managed_generate → native_lab.run_acceptance` 使用同一批准 Plan。原生生成器先创建真实模块，然后调用 `native_rule_customizer`。该回调先执行 Plop，随后每轮调用编码阶段的模型配置，Aider 只应用 `RND_RULE_BEGIN` 与 `RND_RULE_END` 之间的表达式；Python 使用受限 AST，Java/TypeScript 使用语法树和允许的名称/操作符检查。路径、导入、类、校验挂载、身份验证、数据库配置和测试不交给模型自由修改。

FastapiAdmin 的 `DeviceCreateSchema`、`DeviceUpdateSchema` 使用 Pydantic after validator 调用 `business_rules.py`。Yudao 的 `WbDeviceSaveReqVO` 用 `AssertTrue` 调用相邻的 `WbDeviceBusinessRules.java`，JSON 序列化忽略这个计算属性。Vue 的原生表单导入 `business-rules.vue` 的函数和组件，在发送新增/修改请求之前先校验。

每一轮 Aider 都使用完整独立 Python 3.12 工具环境，平台仍为 Python 3.14。LiteLLM 仅作为完整 Aider 的间接依赖保留；真实模型 Key 只交给平台 `ModelGateway`，不会传入 Aider。Aider 禁网执行，Git 保存修改前后提交。只有全部注册的前后端规则文件被正确处理才继续；部分补丁、过期 SHA、非法表达式、未知路径会被拒绝。

随后运行真实后端正反例、完整前端构建/类型检查和浏览器。失败会保存错误，回滚本轮候选，再把脱敏失败反馈交给模型，最多 `MAX_REPAIR_ATTEMPTS + 1` 个候选。达到限制不交付伪造成功；保留诊断和 Git 记录。后面的标准 CRUD、权限、重启、独立新库恢复仍须通过。这是受控的原生单记录业务规则编辑与修复，不是开放任意 Java/Vue 文件或任意 shell 的自主 Agent。

在 `.env` 明确启用：

```dotenv
ENABLE_CODING=true
CODING_ENGINE=aider
MAX_REPAIR_ATTEMPTS=2
```

在项目根目录安装工具和执行契约测试：

```bash
uv sync --locked --all-extras
uv sync --locked --project tools/aider --python 3.12
npm ci --prefix tools/node --no-audit --no-fund
npm run build --prefix tools/node
uv run pytest tests/test_native_tools.py tests/test_daytona_matrix.py tests/test_owned_lifecycle.py -q
```

没有 node-plop、Aider、JDK、pnpm 或 Chromium 时应显示明确错误，不会用自写工具或伪造报告代替。仅运行单元测试不代表真实框架验收完成；原生 Actions 还必须启动服务器和浏览器。

## 本机 Daytona 的数据库与模板矩阵

| 模板 | 数据库 | 沙箱中的实际验收 |
|---|---|---|
| python-basic | SQLite | 保留独立离线安装、迁移、认证/数据隔离、CRUD、搜索筛选和重启检查。 |
| python-basic | PostgreSQL | 在沙箱内初始化新的 PostgreSQL 集群，再执行产品自身安装和同样的 HTTP 验收。 |
| FastapiAdmin | PostgreSQL | 本机镜像准备；沙箱内新 PG/Redis；独立 start.py 初始化、后端启动、完整 Vue 构建/类型检查、规则正反例、权限、真实表单和重启。 |
| Yudao + Vben | PostgreSQL | 本机镜像准备；沙箱内新 PG/Redis；Maven 离线构建、完整 Vben 构建/类型检查、独立启动、业务规则、权限、浏览器与重启。 |

“其他数据库”指当前选择器实际支持的 PostgreSQL，不代表已经支持 MySQL、Oracle 等未登记产品选项。原生模板不支持 SQLite；不能绕过模板兼容性。

Daytona 控制面固定 v0.190.0。Windows 使用 Linux x86_64 的 WSL2/Docker。Java/Vue 构建需要足够内存、交换空间和磁盘；大型快照资源为明确登记值，不在失败后静默取消检查。上游开发架构使用 privileged Docker-in-Docker，不是面向恶意内核攻击的强隔离生产平台。所有端口绑定本机，镜像 registry、数据库、身份认证和存储都在本机。

先按照前章完成基本本机服务的 `prepare → images → snapshot-image → up → auth → snapshot`。对于已完成本机生成验收的原生项目，用它的实际输出目录准备快照；下面把路径写成 `生成项目目录`，执行时替换为你的真实目录，而不是复制这几个汉字：

```bash
uv run python -m scripts.daytona_matrix_image yudao-vben --database postgresql --product 生成项目目录
uv run python -m scripts.daytona_bootstrap snapshot
```

FastapiAdmin 将 `yudao-vben` 改为 `fastapiadmin`；基础 PostgreSQL 项目改为 `python-basic`。`snapshot-image.json` 记录创建的快照名称与所有依赖锁身份。公开依赖只在这一步明确下载。不同源码但相同依赖锁可以复用已登记快照；新增依赖必须显式重新预热，运行时缺包会失败而不是偷偷联网。

把 `.data/daytona-local/workbench.env` 中本机连接信息合并到项目 `.env`，不要上传其中的本机 API Key。只使用一个 profile 时 `DAYTONA_SNAPSHOT` 即可；多个 profile 用 JSON 映射准确选择：

```dotenv
SANDBOX_PROVIDER=daytona
DAYTONA_ALLOW_LOCAL_EXECUTION=true
DAYTONA_API_URL=http://127.0.0.1:3000/api
DAYTONA_TARGET=local
DAYTONA_RUNTIME_TIMEOUT=3600
DAYTONA_SNAPSHOTS={"python-basic/postgresql":"填写该profile实际快照名","fastapiadmin/postgresql":"填写该profile实际快照名","yudao-vben/postgresql":"填写该profile实际快照名"}
```

映射值来自本机快照回执，不能照抄占位词。生产工作流的 sandbox 节点根据真实产品选择 profile。上传的只有过滤后的源码和受信任验收器，没有主机 PostgreSQL URL、密码、模型 Key、`.env` 或运行数据库。沙箱内 PG/Redis 由验收器创建并清理；原生产品启动器是独立进程，不把测试工作台当成产品依赖。

`RND_OFFLINE_TOOLS=1` 是预热快照内的固定执行策略：uv 离线、pnpm 离线、Maven 离线，缺失依赖不能联网补装。`network_block_all=true` 是沙箱运行网络设置。长时间编译使用单独的有界运行期限；创建、传输、下载、删除仍有各自期限。任何运行报告缺失、错误布尔值、模板/数据库/源码身份不匹配、服务未停止或沙箱删除失败，都会阻止交付。

## 完整验收与排错

执行 `.github/workflows/native-toolchain-daytona.yml` 的三组矩阵，加上 SQLite Daytona 工作流，才覆盖上述四种组合。原生矩阵故意先输出总为 true 的错误候选，真实反例必须失败、候选必须回滚；第二轮输出合法规则，必须通过编译、真实接口和浏览器，然后在另一个新数据库恢复。随后才准备快照，在 Daytona 内再从全新数据库验证交付项目。

`reports/native-tools/plop.json` 是实际模板动作，`coding-0.json` 记录失败回滚，`native-coding.json` 记录修复结果；`toolchain-acceptance.json` 是原生整体验收；`daytona-matrix.json` 包含沙箱运行及删除结果。`daytona-verification.json` 在创建沙箱前就保存随机名称，因此创建超时也能定向检查自己的资源；不删除别人的沙箱。

构建失败先看 `daytona-matrix-image-build.log`；运行失败看 `daytona-verification.json` 中具体命令和脱敏输出；浏览器失败看 `browser.json` 与 `browser-failure.png`。快照依赖身份不符时重新显式准备对应 profile，不关闭校验。代码失败时修改规则实现，不修改批准的反例、不删除权限测试。只有证据真实通过，才进入打包和交付。

## 原生生成中断后如何恢复

原生初始化包含建表、菜单挂载和源码写入，不能把整个过程无条件重跑。`workbench/native_recovery.py`把批准Plan、模板来源、专用数据库身份以及生成文件清单绑定到检查点。实际生成完成后保存可恢复阶段；后续规则编辑、构建或验收失败，再次重试先核对这份检查点，复用同一生成目录和数据库，不重新初始化种子或创建第二套菜单。

已有失败候选的日志和Git记录保留，继续尝试使用新的编号。只允许恢复程序明确标记可恢复的阶段。若进程在不可重放的生成步骤中被强制终止、检查点缺失、源码被手工改过或数据库/Plan已改变，就保留现场并明确阻塞，先检查该阶段；不能自动清库，也不要求靠新建任务掩盖旧现场。

学习时先运行`tests/test_native_recovery.py`理解身份和文件清单拒绝分支；真实原生CI还会分别在实际生成完成后、权限验证后故意中断，再在同一目录和数据库恢复。权限验证每次创建带随机标识的自有测试角色/用户，不接管或修改已存在的无关账号，避免重试碰撞。两次恢复都必须通过后续检查，才验证重试不会破坏已完成的生成。合同测试、可恢复阶段的真实中断验证与任意时刻硬杀恢复是不同范围，不能互相代称。

## 本机沙箱启动失败时保留最少诊断

`DAYTONA_CAPTURE_STARTUP_DIAGNOSTICS`默认关闭。明确启用后，只在创建失败且SDK按本次随机名称找到确切自有沙箱时，在删除前采集其有限容器状态（含OOM/退出码）、标准输出尾部及`/tmp/daytona-daemon.log`尾部。每项最多5秒、总计最多15秒，保存文本每项最多8192字符；先过滤配置中的秘密、Bearer/token/password字段和连接URL密码。诊断只写入该次`daytona-verification.json`的`startup_diagnostics`，不遍历其他容器、不转储环境、不改网络或容器配置。读取失败会标记不可用，随后仍执行原清理路径；诊断成功绝不会把创建超时或原验收失败改成通过。需要排查本机启动问题时才显式开启，普通运行不额外采集这些日志。

## 长时间矩阵命令只提交一次

`workbench/daytona_sessions.py`为非SQLite的长时间矩阵验收建立独立会话，再用一次异步命令提交启动检查；随后在原总运行期限内用短GET请求轮询状态，结束后读取日志一次。会话创建、命令提交、状态与日志请求均有最多30秒的单请求期限；SDK传输层关闭透明重试，尤其不自动重发可能已经执行的POST。回执保存mode、session_id及取得的command_id，便于定位本次操作。

响应丢失不证明命令没执行，因此提交结果不确定、超时或缺少命令ID时直接失败并进入自有沙箱清理，不改用同步exec重新运行。输出目录的重复保护仍保持严格，不因发现目录已存在就跳过验收或宣布通过。这个处理改变请求组织方式，不延长网关空闲超时，不放开网络，也不减少矩阵检查。
