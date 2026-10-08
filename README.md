# AI 研发工作台 · Python 3.14

**主线：用 LangChain + LangGraph，从稳定模板批量定制可运行的前后端项目，并能照文档从零实现。**

从 [模板平台实现指南](docs/template-platform.md) 开始：先理解技术模板、业务需求和运行队列，再实现批量提交、编码规范、过程与验收。完整源码教材仍在 [learning-docs](learning-docs/README.md)。

新建区支持一次提交 1–10 个独立项目，复用已有持久 Worker，每个项目保留自己的审批、进度、失败恢复与交付。三套模板各有版本化 VIBECODING 规范，随模型上下文和生成产物一起交付。跨场景真实模型验收采用个人阅读书架、库存采购协作、设施维护运营三个递增案例，均固定使用 `python-basic` / `simple-admin` / SQLite，三项全部通过才算该套件验收成功；该套件不代表原生多技术栈或生产压测覆盖。

从需求到可启动产品的本地工作台：**先选择后端、前端与数据库 → 描述需求 → 人工确认或一键智能推荐 → 原生/确定性生成 → 独立测试 → 可选模型审阅 → 打包下载**。

平台使用 Python、uv、FastAPI、SQLite、LangGraph，以及本地打包的 Vue 3 + Ant Design Vue 操作界面。**仅聊天大模型允许使用外部推理服务；其余工具均为本机运行。** 基础代码、迁移、索引、测试与打包由工具执行。测试失败不能由模型“宣布通过”。

首页可勾选「允许受控自定义扩展」进入逐功能分派：先独立分析需求，再审批基础契约与原生、声明式、模块或阻塞路由。源码模块复用受限候选和隔离验收；仅有来源 ID 或路由标签不能证明功能完成。`batch-import-v1` 当前缺少实际模板，设计会明确阻塞。每个项目的「新一轮」仍从零生成独立产品，已有代码和数据升级尚未接入。

普通 `integer` 明确使用有符号 32 位范围，并支持 `minimum`、`maximum`、`exclusive_minimum`、`exclusive_maximum`。声明式数值边界参与需求覆盖、API 校验、SQL CHECK 与独立边界测试，不需要模型写规则代码。Python 文本 `pattern` 需同时提供合法 `example`；原生模板暂不支持跨语言正则。优化范围与验证说明见 [流程优化说明](docs/workflow-optimization.md)。

登录后的比赛报名、学生本人记录权限和管理员审核可优先使用现有模板能力，通常无需勾选自定义扩展。首页提供可编辑的报名需求示例。规划失败会保留原运行，并显示具体格式、长度等约束以便重试；技术模板与后续业务预设的区别、报名配置和实施路线见 [模板定制流程审查](docs/template-customization-roadmap.md)。

## 从零学习：推荐新的分阶段教材

从 [learning-docs/README.md](learning-docs/README.md) 开始：15个依赖有序阶段，每站有实现解释、小实验、预期结果与排错。每个代码块首行标注相对路径，大文件按模块分为连续小页。只保存整个 `learning-docs` 目录就能在空目录重建自有源码、测试、锁文件和截图，第三方模板按固定上游提交自行下载处理；无需先下载本仓库骨架。

旧版完整手册仍保留兼容。新教材的还原与验收方式见 [learning-docs 最后一站](learning-docs/14-acceptance/README.md)。

## 1. 初始化完整演示源码

安装下方的Git和uv后，在准备存放项目的文件夹打开终端。取得完整演示源码：

```powershell
git clone https://github.com/Live-yum/ai-rnd-foundation-learning.git
cd ai-rnd-foundation-learning
```

也可以使用GitHub的Code菜单下载ZIP并解压。以下命令均在含`pyproject.toml`的项目根目录执行：

```powershell
uv python install 3.14
uv sync --locked
uv run rnd init
```

**从零学习不需要先取得这些源码。** 兼容版教材`从零实现AI研发平台_逐步实操手册_完整版.md`从空文件夹讲解每个自有文件、调用关系和逻辑，包含所有文本源码及锁文件；书中给出的脚本可从固定第三方提交生成原生模板ZIP。没有本项目骨架也能照书实现。

需要先安装 Git、uv。Windows 的 uv 官方安装器：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

`rnd init` 创建本地数据库和访问令牌，不覆盖已有 `.env` 或删除数据，并从仓库内的 `templates/vendor/` 解压 FastapiAdmin、芋道后端与 Vben 源码。**普通 git clone 已包含模板代码快照，不用再 clone 上游仓库、初始化 submodule 或下载 LFS 文件。** 源码压缩包、许可证、固定 commit 和 SHA-256 清单一起提交。安装第三方依赖、下载浏览器等仍需网络；包含源码不等于完全离线运行。

带`simple-admin`的产品在交付前必须通过真实浏览器验收。先按完整手册“从空目录到可信交付”的站点4安装本机Node22、Playwright1.56.1及Chromium，再从同一终端启动平台；缺少浏览器会明确阻塞，不能只用HTTP测试代替。原生框架同样保留真实浏览器关卡。

## 2. 单模型配置：只填三项

推荐先执行 `uv run rnd start`，即使还没填模型也能打开页面。输入本机访问令牌后，进入「模型与配置」，填写默认 BaseURL、模型名称和 API Key。也可以继续编辑仓库根 `.env`：

```dotenv
BASE_URL=https://你的兼容服务/v1
API_KEY=你的密钥
MODE=你的模型名称
```

`MODE` 是模型 ID，也兼容 `MODEL` 别名；不是运行模式。`BASE_URL` 是 Chat Completions API 根地址，不包含 `/chat/completions` 后缀。只支持兼容该协议的服务。远端默认必须 HTTPS，本机模型服务可以使用回环 HTTP。明确使用可信 HTTP 网关时，可在进程配置中设 `ALLOW_INSECURE_MODEL_HTTP=true`；HTTP 会明文传输凭据，应优先使用 HTTPS。不要上传 `.env` 或分享密钥。

## 3. 可选：不同阶段使用不同模型

不配置阶段变量时全部继承上述默认模型。可以只改模型名称，也可以按阶段配置独立服务商：

```dotenv
# 需求澄清及智能推荐，未填则使用默认模型
REQUIREMENTS_MODE=需求模型名

# 设计/规划
PLANNING_MODE=规划模型名

# 仅在确实需要定制字段规则时调用
CODING_BASE_URL=https://另一个服务商/v1
CODING_API_KEY=该服务商密钥
CODING_MODE=编码模型名

# 可选语义审阅；不替代独立代码测试
MODEL_REVIEW=true
REVIEW_MODE=审阅模型名
```

四个前缀为 `REQUIREMENTS_`、`PLANNING_`、`CODING_`、`REVIEW_`，每个都支持 `BASE_URL`、`API_KEY`、`MODE`。同服务商可继承默认密钥；**更换地址必须显式填写该阶段 API_KEY**，不会把默认密钥发到另一个地址。修改 `.env` 后重启服务。

```powershell
uv run rnd doctor
uv run rnd models
```

命令只显示有效阶段、地址、模型名和是否配置密钥，不显示密钥。运行详情也保留各阶段实际模型与用量回执。验证阶段中的编译、数据库、API、浏览器测试始终是确定性工具；`REVIEW_*` 负责额外语义审阅，不能篡改测试结果。

## 4. 启动与操作

终端 A：

```powershell
uv run rnd start
```

浏览器打开 **http://127.0.0.1:8000/**。另开同目录终端：

```powershell
uv run rnd token
```

将本机访问令牌填入页面。它不是模型 API_KEY，也不是生成产品的用户登录令牌。令牌仅保留在当前页面内存，刷新后重新输入。从工作台描述目标，在技术栈设置中确认模板、兼容前端和数据库后开始；页面组件使用的 Vue 3 + Ant Design Vue 与最终生成产品的技术栈是两件事。

### 对话、进度与恢复

- 对话展示同一次真实模型响应中的用户可见摘要。支持流式协议的供应商会逐步显示实际内容；不支持流式时明确显示等待完整响应，不用定时器伪造打字
- 生成中的文字标为待校验草稿；完整响应通过严格 Schema 校验后才成为确认内容。模型推理过程、系统提示词和源文件补丁不会通过对话流展示
- 需求澄清支持真实模型生成的单选、多选和自定义回答；没有结构化选项时使用文字回答。选项不是已批准需求，服务器按当前问题版本验证并保留用户选择与补充
- 需求、设计、交付三道关卡仍使用 gate_id、版本和内容摘要。遇到 409 过期版本须重新查看与审阅，不自动重发批准
- 研发进度来自串行 LangGraph 节点的实际开始、等待、完成和失败事件，不展示虚构并行工作或估算百分比
- 关闭页面或切换运行只断开该页面的流订阅，后台任务继续。重新连接从持久事件编号续传并去重；失败或预算暂停时修复原因后重试同一运行
- `READY` 表示通过运行级验收并获交付批准；`SOURCE_READY` 表示源码级或明确批准的部分成果，须查看覆盖报告，不能当作全部原始需求完成

### 页面内模型设置

默认配置和需求、规划、编码、审阅四阶段可分别设置。空阶段字段表示继承；已有 Key 只显示「已配置」，服务器不回传原文。修改 BaseURL 必须同时为新地址输入独立 Key；不会将旧 Key 自动发到新地址。保存前检查配置版本，其他窗口已修改时先重新加载。

页面保存到本机 `.data/model-settings.json`，优先于 `.env`；POSIX 下原子写入且文件权限为 0600。保存后下一次模型调用读取新配置，进行中的调用及其重试继续使用原快照。保存只做格式检查，不验证账号可用性。保存后可在所选默认/阶段页点击「测试连接」：确认费用后，仅对该已保存版本发送一次最多128输出Token的结构化探测，不自动重试。结果独立显示配置版本、阶段、错误码和追踪ID；保存成功不等于连接成功，推理模型的探测也可能因输出上限被截断。请勿提交配置文件、访问令牌或 API Key。

任务失败时可在对话查看阶段、错误码、追踪ID及脱敏字段校验详情。已回答的澄清问题和模板能力提示保留为只读历史；不会重新作为需求或自动批准。修复验证范围与本地环境限制见 [模型反馈验证记录](docs/model-feedback-verification.md)。

也可以用 CLI 操作（仍需保持终端 A 的 `rnd start` 运行，在另一个终端执行）：

```powershell
uv run rnd chat
```

CLI 同样先选择模板/前端/数据库，再描述需求。明确配置可直接传入：

```powershell
uv run rnd chat --template python-basic --frontend simple-admin --database sqlite
```

| 后端模板 | 可选前端 | 交付数据库 | 运行前提 |
|---|---|---|---|
| `python-basic` / FastAPI | `simple-admin`、`api-only` | SQLite 或 PostgreSQL | SQLite 只需 Python3.14/uv；PG另需数据库或Docker |
| `fastapiadmin` | `fastapiadmin-vue` | PostgreSQL | Linux/WSL、Node22、pnpm9.15.3、Redis/PG、浏览器验证工具 |
| `yudao-vben` / Java | `vben-antd` | PostgreSQL | 上述服务 + JDK17/Maven、pnpm11.16.0 |

Windows 可以先分析原生模板的需求和设计，基础安装不会因缺少可选 PostgreSQL 驱动而在导入阶段崩溃。原生全栈的实际执行仍须使用 WSL 2/Linux，平台与驱动检查会在创建数据库或生成产品之前给出准确提示；选择默认 Python/SQLite 通道则不要求安装 PostgreSQL 驱动。

界面只允许已适配的组合，不任意混接一个框架的前端和另一个框架的鉴权 API。**所选数据库是交付产品的数据库；平台控制库仍可用 SQLite。** 完整原生环境准备见手册第二部分。

## 5. 不再被澄清轮数卡死

默认 `MAX_ROUNDS=0`、`MAX_MODEL_CALLS=0`：没有累计人工会话轮数或模型调用数量上限。HTTP重试与自动代码修复仍有限，避免单次故障无限调用。按需设正整数限制预算，达到后为 `PAUSED_LIMIT`，保留原回答与断点，不要求新建项目。

普通细节给推荐默认值；每轮最多要求模型提出两个阻塞问题，已经明确的事实随结构化需求保存。客服的站内提醒、角色范围、统计口径及字段命名以三份需求文本为准；字段、枚举与日期范围经过合同校验，用户明确指定优先。

`批准`、`“批准”` 等控制指令不会被当作需求文本再次发送给模型。不满足批准条件时保持原等待点，提示回答或智能推荐，不消耗一轮。

## 6. “智能推荐”是持续委托，不是再问一次

页面支持委托的非终态可点击 **智能推荐**，或在新建时选择智能推荐；需要你明确范围的关卡会解释为何暂不可委托。CLI 可输入 `智能推荐`，或者：

```powershell
uv run rnd recommend 运行UUID
uv run rnd chat --smart
```

这是你授权：**从现在起，剩余不明确细节按 AI 推荐补齐；后续需求/设计/交付不再逐项询问。** 它保留你已明确的要求，记录推荐与 `delegated-ai` 决定。可以随时点“恢复人工确认”或执行 `uv run rnd manual UUID`，在后续关卡恢复人工模式。

自定义扩展的原子业务完整分解和部分交付范围始终需要明确人工审阅；自动模式不能替你确认来源相关性、取消未完成要求或证明外部服务。已验收候选的范围/最终交付批准不调用模型，移除模型配置后仍可继续这些准确关卡。详见[原子验收与部分交付](docs/extension-acceptance-lifecycle.md)。

智能推荐不允许跳过独立测试、覆盖生产库、伪造成功或删掉你明确要求的功能。确实超出模板能力时关卡不可批准，智能推荐会暂停为 `BLOCKED`；人工模式保留不可批准的澄清关卡，不会偷偷生成缩水产品。

“报名网站”不会自动解释为匿名网站，也不会自动缩减为管理员录入。若报名入口尚不明确，平台会保留原始目标，请你选择登录后的参赛者自行提交、保留独立公众门户需求并暂停扩展，或明确同意仅管理员维护。登录后的自行提交须使用真实非管理员业务角色与本人记录权限；独立公众门户与匿名提交当前不能自动交付。已知入口选择未解决时，重复智能推荐不会再次调用模型，也不能代替你的决定。

旧运行若曾在原生设计的可选依赖导入处失败，可在升级后重试同一运行。运行 ID、回答、已保存设计与历史审批保留；若检测到原始报名目标曾被缩减，会建立新的澄清版本，旧审批不能批准新版本。无需删除 `.data` 或重新创建项目。

本仓库还保留**内部客户服务管理系统**作为深入学习与原生技术栈验收案例；新的批量跨场景主线见[模板平台实现指南](docs/template-platform.md)：

> 建设公司内部客户服务管理平台：维护客户档案和历史服务记录；创建服务请求、分配负责人、按批准流程改变状态并追加处理记录；支持协作任务、站内提醒和不可修改的操作审计；提供服务数量、创建到解决的时长、客户分组和每日趋势统计。管理员、客服、普通员工按角色及负责/创建范围访问数据。沿用所选框架的原生认证、ORM、事务与UI组件，并交付可在新目录和新数据库独立启动的产品。

完整原始需求在`examples/requirements/customer-service.md`，演示默认决策在`customer-service-decisions.md`，明确字段与命名约定在`customer-service-contract.md`（后两份同在`examples/requirements/`）。按此顺序把三份文本一起输入平台：原始需求不改写、不删减，补充文件只明确可执行约定。由所选模型形成并校验`Plan.business`；`examples/plans/customer-service.json`只用于确定性工具验收，不作为模型失败的隐藏答案。分别验证`python-basic/simple-admin/SQLite`、`fastapiadmin/fastapiadmin-vue/PostgreSQL`与`yudao-vben/vben-antd/PostgreSQL`，每种组合都要保留自己当前提交的证据，不能用一个模板成功代表其余模板。

## 7. 得到和启动最终产品

页面 `READY` 后点击下载，或：

```powershell
uv run rnd show 运行UUID
uv run rnd download 运行UUID
```

ZIP 位于 `deliveries/`，解压到新目录。**在解压后的产品根目录**执行：

```powershell
uv run --no-project --python 3.14 python start.py
```

- 默认产品：自动安装产品自身锁定依赖、执行Alembic迁移、启动；轻量界面在 `http://127.0.0.1:8001/`，API文档在 `/docs`。客服产品先在产品目录执行`uv run python manage.py bootstrap-admin --username manager`，通过隐藏终端输入设置初始管理员密码；随后登录并创建或分配客服/员工业务角色。普通注册只得到员工角色。SQLite无需外部服务。
- 默认产品选PostgreSQL：启动器使用该产品独立Docker Compose、随机密码、回环端口和持久卷；或显式提供 `PRODUCT_DATABASE_URL`。
- 原生产品：包含原生源码、独立启动器、原生种子、业务DDL和菜单SQL。在Linux/WSL准备其语言工具和Docker后，同一启动命令自动初始化**新的独立数据库**并启动前后端；无需原研发平台、模型Key或原开发数据库。可用本机专用空库 `NATIVE_DELIVERY_DATABASE_URL` 和Redis替代Docker。浏览器地址由启动器打印。

源码包含初始化/迁移语句，不包含用户实际业务数据。重复启动不重置记录或密码。原生 `--check` 会完整验证数据库、菜单、CRUD和前端启动后退出；`--skip-build` 仅用于之前已成功构建的同一产品。不要删除数据库排错，不把源码包当作用户数据备份。

## 8. 测试、证据、手册

```powershell
npm ci --prefix ui --no-audit --no-fund
npm test --prefix ui
npm run build --prefix ui
uv run ruff check .
uv run ruff format --check .
uv run pytest -m "not postgres" -q
uv run python -m scripts.build_handbook --check
uv run python -m scripts.build_learning_docs --check
```

Actions 覆盖Windows/Linux、真实PostgreSQL、独立产品安装、原生新数据库交付、真实Chromium智能推荐与产品页面回归，并由客服矩阵验证三角色、关系、流程、提醒和统计。上述普通确定性CI的模型调用采用显式协议夹具，不消耗真实Key，也不声称已验证你的供应商账号。显式触发的 **Three-project live acceptance** 使用 `rnd` 环境的 `API_KEY` 调用真实模型，会消耗所配置账号的额度。

详细从零实现手册：**`从零实现AI研发平台_逐步实操手册_完整版.md`**。从空目录创建文件、数据流讲解、完整代码、数据库迁移、前端、测试、CI与锁文件均包含在同一份教材。第三方模板不是自行编写的代码：教材提供固定提交和打包脚本，读者可以从公开上游重建三个归档，不需要先取得本仓库骨架。演示仓库附带这些归档以便直接体验；源码附录逐文件讲解职责与对应关系。

当前是仅监听本机、单操作人和单Worker的研发工作台。没有公网生产身份体系。请勿公开 `.env`、`.data`、`.deployment` 或访问令牌。更多环境条件、SQL步骤、预算恢复、原生部署与故障定位见完整手册。

## 9. 本机工具链与完整教材

默认使用本机Tree-sitter/Python AST、FTS5和符号Repo Map。Aider使用独立Python3.12环境：

```powershell
uv sync --locked --project tools/aider --python 3.12
uv run rnd index workbench .data/platform-index
uv run rnd tools search workbench .data/platform-index "model_for"
uv run rnd tools continue-config . workbench .data/platform-index
```

设置`CODING_ENGINE=aider`和`REPO_MAP_PROVIDER=aider`可启用实际本机编辑/Repo Map。真实模型Key只交给平台网关，Aider不取得它；登记的CLI入口禁用网络，Token编码和模型元数据来自经过SHA校验的锁定依赖，不在生成任务中下载。

实际Continue全文索引组件已随仓库包含源码和Apache-2.0许可证，固定提交为`5522c6f44ca0ac3528b37244818fbfa39b5af470`。使用Node22（至少22.13）在本机准备：

```powershell
node --version
npm ci --prefix tools/node --no-audit --no-fund
npm run build --prefix tools/node
```

在项目`.env`设置`RETRIEVAL_ENGINE=continue`并重启平台。规划、CLI和只读MCP都会实际执行上游`FullTextSearchCodebaseIndex.update/retrieve`，与本机AST、FTS5和可选向量融合；不是把自写索引重命名为Continue。查询进程禁用网络，不读取IDE私有缓存。`RETRIEVAL_ENGINE=local`仍是无需Node的默认基础方案。Continue IDE可以通过本机stdio MCP访问同一套只读search_code/repository_map，不要求云账号。

向量服务仅接受回环地址，使用本机模型并显式`EMBEDDING_ENABLED=true`。工具端点拒绝云端/局域网、代理与重定向，数据库和Docker执行也限定本机；继承的LangSmith/OTEL遥测关闭。公开依赖下载不等于云端执行工具。

Daytona固定为**v0.190.0自托管开发部署**，没有云端模式。Linux/WSL准备Docker后：

```bash
uv sync --locked --all-extras
uv run python -m scripts.daytona_local prepare
uv run python -m scripts.daytona_local images
uv run python -m scripts.daytona_local snapshot-image
uv run python -m scripts.daytona_local up
uv run python -m scripts.daytona_bootstrap auth
uv run python -m scripts.daytona_bootstrap snapshot
uv run python -m scripts.ci_daytona_local
```

最后一条保留历史工具接线回归，使用明确的测试模型夹具，不是客服全流程或真实供应商通过证明。客服标准验收以`examples/plans/customer-service.json`、各模板业务测试及`customer-runtime.yml`为准；DeepSeek必须另用同一最终提交的真实客服需求完成验证。需先按上方准备Node组件与Aider环境。

本机随机凭据及平台配置保存在`.data/daytona-local`，不得提交Git。完整教材第20章解释Dex、API、Runner、镜像摘要、离线快照、每一步预期结果和清理。默认Python/SQLite快照不冒充Java/Vue通用镜像；原生完整验收仍在本机进行。Daytona上游Compose仅供开发，privileged Runner不是生产强隔离保证。

仓库保留`从零实现AI研发平台_逐步实操手册_完整版.md`作为兼容完整手册；分阶段`learning-docs`是推荐学习入口，两者从同一源码重生。源码块带SHA，逐文件讲解与源码同步，标准库重建脚本可只从文档建立全部自有文件：

```powershell
uv run python -m scripts.build_handbook
uv run python -m scripts.build_handbook --check
uv run python -m scripts.ci_handbook
```

真实模型联调需要你自己的大模型配置。普通确定性CI使用显式模型协议夹具；显式触发的真实模型三案会调用所配置服务并消耗账号额度。真实CLI、数据库、浏览器、本机服务测试的证据分别保存，不把SDK模拟响应当成本机完整部署成功。

### 本机Daytona的安装边界

Daytona固定v0.190.0；API/Proxy从固定SHA在本机Docker构建，Runner使用同版本、固定SHA256的发布文件。服务运行在本机internal网络，端口仅绑定回环，SDK也禁止非回环连接；不申请Daytona云账号。完整安装顺序为`prepare → images → snapshot-image → up → auth → snapshot → ci_daytona_local`，每一步的完整代码、用途、预期结果及失败处理见兼容手册第20章及新教材第12阶段。此安装通道使用Linux x86_64或Windows x86_64 WSL2；默认平台与普通本机验收不要求安装Daytona。安装时下载公开依赖，不等于把生成代码交给云端运行。

### 原生业务规则、Plop、Aider 与完整本机 Daytona

原生新增/修改规则可由实际 Plop 挂载，再由独立 Aider 应用精确补丁；编译、正反例、浏览器失败会回滚候选并进入有界修复。原生与基础 PostgreSQL 使用单独的本机 Daytona 离线快照，数据库和 Redis 在沙箱内初始化，不复制主机数据库凭据。完整安装、文件对应关系、支持矩阵、配置与排错见 [原生工具链实操](docs/native-toolchain.md)。基础生成仍优先原生生成器；不是让 Agent 自由修改权限或执行 shell。


## 10. 客服标准流程的验收与截图

先完成教材中的本机依赖和专用空测试库准备，再运行基础模板业务测试与两个原生完整入口：

```bash
uv run pytest tests/test_business_contracts.py tests/test_business_capabilities.py tests/test_business_python.py tests/test_business_python_browser.py tests/test_customer_workflow.py -q
uv run python -m scripts.ci_native_bundled fastapiadmin --spec examples/plans/customer-service.json
uv run python -m scripts.ci_native_bundled yudao-vben --spec examples/plans/customer-service.json
```

原生两条命令各用自己的干净测试环境/空库，不能连续指向一个已有业务数据的库。正式结论须核对同一提交的Actions、实际DeepSeek客服运行及下载后独立启动结果。完成后还要打开列表、表单、关联选择、处理流程、提醒和统计截图，检查原生UI一致性、文字/控件布局和业务信息完整性；“截图生成成功”不等于视觉检查已完成。未通过的项保持失败或未验证，不写“DeepSeek全流程没问题”。

真实模型的手动入口和证据解释见`docs/real-model-acceptance.md`。当前客服分支运行`.github/workflows/native-probe.yml`时选择`feat/customer-service-acceptance`，明确设置`real_model=true`，`expected_sha`填写已审查的完整40位提交SHA。`rnd`环境的`API_KEY`仅注入模型调用步骤，不打印或复制到源码；三个模板分别执行smoke与完整客服交付，任何一行未完成都仍是未验证。
