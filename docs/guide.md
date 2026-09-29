# 从零实现 AI 研发平台：逐步实操手册

**Python 3.14 · uv · FastAPI · SQLite/可选PostgreSQL · LangGraph · 可选多模型 · 智能推荐 · 自带原生模板**

这是一份完整的实现与操作手册：前半部分按学习顺序说明创建什么、连接到哪里、如何运行与测试；后半部分直接包含同一提交中的全部文本源码、配置、数据库迁移、前端、测试和依赖锁。不要把旧手册里同名文件的部分代码混入当前实现。

本手册的正式文件为 `从零实现AI研发平台_逐步实操手册_完整版.md`，保留兼容路径 `_完整版_v3.md`，两者内容完全一致。修改源码或正文后自动重新生成整本，不维护一堆互相矛盾的补丁章节。

## 1. 认识最终系统，再决定使用方式

平台接收你的需求，帮助你澄清或推荐默认方案，确认设计，使用已验证的模板生成产品，再独立运行测试和打包。平台不是“一个提示词写出一切”的无限Agent：模型负责理解、规划及必要规则；程序负责迁移、文件、权限边界、生成器、测试和交付。

你可以选择两种操作模式：

- **人工模式**：重要节点由你确认；未明确的普通细节给推荐值，避免拆成十几轮追问。默认没有累计人工对话轮数上限。
- **智能推荐模式**：在任意非终态点击“智能推荐”，或新建时启用。此后未明确的细节由AI推荐补齐，后续需求/设计/交付由受记录的委托决策自动推进，不再要求逐项回答。测试与安全边界不受这个开关影响。

模型也有两种配置方式：只填一组默认模型就能运行；或给需求、规划、编码、语义审阅分别配置模型。没有必要的任务不调用模型，例如基础CRUD不会为了“多Agent”而额外生成一遍。

### 1.1 能力矩阵是程序事实，不让模型随口改变

| 后端模板 | 前端选择 | 交付数据库 | 数据范围与支持项 |
|---|---|---|---|
| `python-basic` / FastAPI | `simple-admin` 或 `api-only` | SQLite、PostgreSQL | 按登录用户隔离；text/integer/boolean/date/enum；长度、枚举、真实日期校验；关键词搜索、精确筛选、含两端日期区间；简单额外单记录规则 |
| `fastapiadmin` | `fastapiadmin-vue` | PostgreSQL | 原生插件模块、菜单、角色权限和共享CRUD；text/integer/boolean；保留原框架 |
| `yudao-vben` / Java | `vben-antd` | PostgreSQL | 原生Java模块、Vben5 Ant Design页面、菜单、角色权限与共享CRUD；text/integer/boolean |

后端、前端、数据库必须先选，再输入需求。不同框架的登录与路由并不天然兼容，页面和API会拒绝未适配的混搭。产品数据库与平台控制数据库独立；平台即使用SQLite，也可以生成PostgreSQL产品。

没有实现的外部采集、支付、跨实体事务等必须明确阻塞，不能换个模型就宣称完成。智能推荐允许补齐未明确细节，不允许删除你已经明确要求的功能或擅自把“各自数据”改成“共享数据”。

## 2. 安装工具与取得代码

### 2.1 Windows准备

安装Git和VS Code。用PowerShell安装uv，关闭并重新打开终端后检查：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
git --version
uv --version
```

本PR合并前使用实现分支：

```powershell
cd D:\Code
git clone --branch feat/controlled-toolchain-integration https://github.com/Live-yum/ai-rnd-foundation-learning.git
cd ai-rnd-foundation-learning
uv python install 3.14
uv sync --locked
uv run python -c "import sys; print(sys.executable); print(sys.version)"
```

预期为仓库 `.venv` 和 Python3.14.x。`uv run` 自动选择项目环境；终端显示Conda `(base)` 不足以判断实际运行解释器。不要在系统Python里pip一套、uv里又装一套，也不要因旧测试的import错误而降到3.12。

合并后main具有同一功能时可直接clone main。已存在目录不要再clone覆盖；先`git status`检查并保存自己的改动。不要用`git reset --hard`、删除数据库或删除整个学习目录排错。

### 2.2 普通clone已经带模板代码

`templates/vendor/`包含三个实际源码ZIP：FastapiAdmin、芋道后端、Vben前端；同时包含 `manifest.json` 和各自LICENSE。它们是普通Git文件，不是submodule、Git LFS指针或只有URL的清单。

```powershell
uv run rnd init
```

这个命令创建 `.env`、平台数据库、本机访问令牌，并验证和解压仓库内的模板快照到 `.data/sources`。不重新从GitHub/Gitee克隆、不覆盖已有 `.env`、不清空数据库。默认只需Python/uv即可完成解压；真正运行Java或原生前端时才需要对应语言环境。

锁文件安装、浏览器下载、Maven/pnpm依赖下载仍需要网络，不能把“源码已经在本地”描述成“全部离线”。源码快照排除依赖缓存、Git历史、密钥、数据库和字体二进制；许可证及原始commit保留。

### 2.3 从已合并版本升级

停止旧服务，备份 `.data/`、`.env` 和未提交的源码改动，随后在仓库根执行：

```powershell
git fetch origin
git switch feat/controlled-toolchain-integration
uv sync --locked
uv run rnd init
```

数据库迁移给旧表新增必要列，旧项目、消息和运行ID保留；不通过删除库绕过迁移。如果旧 `.env` 中显式填写 `MAX_ROUNDS=10` 或 `MAX_MODEL_CALLS=16`，新默认不会覆盖它，请主动改成0。旧运行因为轮数失败时可修正配置并重启，再 `uv run rnd retry 原UUID`。没有生成到不可恢复外部副作用阶段的澄清运行可以继续；原生初始化中途失败则应保留现场并使用新的独立库，不自动DROP原数据。

## 3. 配置模型：单模型先跑通，多模型按需启用

编辑根目录 `.env`：

```dotenv
BASE_URL=https://你的服务商API根地址/v1
API_KEY=真实密钥
MODE=实际模型名称
MAX_ROUNDS=0
MAX_MODEL_CALLS=0
```

BASE_URL不要填网页聊天地址，不要带 `/chat/completions`；程序追加这个路径。MODE是模型ID，与MODEL别名兼容，不是dev/prod或推理强度。本实现使用OpenAI-compatible Chat Completions响应结构，不自动假装兼容完全不同的协议。远端使用HTTPS，本机服务只允许回环HTTP。

### 3.1 有效模型的继承规则

| 阶段 | 环境变量前缀 | 何时调用 |
|---|---|---|
| 澄清、智能推荐 | `REQUIREMENTS_` | 提取事实、提出少量核心问题、补齐未明确内容 |
| 设计/任务规划 | `PLANNING_` | 输出可校验Plan及字段/验收条件 |
| 特殊规则编码 | `CODING_` | 仅在Plan确实需要额外单记录规则时 |
| 语义审阅 | `REVIEW_` | 可选；只能解释已产生的独立测试证据，不伪装执行测试 |

每个前缀后都可接BASE_URL、API_KEY、MODE。未指定时逐字段继承默认；只改MODE就是同服务商换模型。更换BASE_URL却没给该阶段API_KEY会明确报错，防止把默认密钥泄漏给另一服务。

```dotenv
REQUIREMENTS_MODE=擅长需求理解的模型
PLANNING_MODE=擅长结构化规划的模型
CODING_BASE_URL=https://另一个兼容服务/v1
CODING_API_KEY=该服务专用密钥
CODING_MODE=规则编码模型
MODEL_REVIEW=true
REVIEW_MODE=审阅模型
```

如果不需要额外审阅，删除REVIEW_*并保持MODEL_REVIEW=false。配置了任一REVIEW覆盖项会启用审阅。普通数据库检查、编译、代码格式、浏览器验收、打包始终用工具，不因为配置REVIEW模型而绕开它们。

```powershell
uv run rnd doctor
uv run rnd models
```

两条命令只显示非敏感信息，不调用付费模型，不证明账号权限；首次实际请求会验证账号。`.env`修改后重新启动服务。已保存运行的模型用量回执保留实际阶段/地址/模型/usage，不公开API_KEY。

### 3.2 限额与恢复

MAX_ROUNDS=0和MAX_MODEL_CALLS=0表示不设累计上限，不是无限网络重试。每次HTTP/结构解析仍只有有界尝试，代码修复最多两轮。设置正整数时达到预算会PAUSED_LIMIT，原回答和checkpoint保留。

上下文不能无限增长。数据库保留完整消息；模型上下文使用原始目标、当前结构化事实和最近修正。MAX_CONTEXT_CHARS控制请求大小，超出明确停止，不静默截断最关键需求。开放无限轮数不等于无限免费额度，供应商仍按实际调用收费。

## 4. 启动平台与第一次完整体验

终端一：

```powershell
uv run rnd start
```

打开 `http://127.0.0.1:8000/`。另一个同目录终端：

```powershell
uv run rnd token
```

将输出填入平台页面的访问令牌。平台令牌、模型Key、产品用户token各自独立，不互相代用。程序仅绑定本机，Swagger在 `/docs`，不需要定制UI也能通过API使用。

界面先展示后端/模板、对应前端、对应数据库。点“确认选择”以后才出现项目名称和需求输入框。选择后若重新换前端/数据库，必须再次确认，不把修改悄悄应用到旧运行。

第一次输入：

> 个人泰拉瑞亚游戏资讯管理。手工录入。标题250字、正文3000字、发布日期YYYY-MM-DD必填；分类可选，选项为资讯、攻略、大神。搜索标题和正文，按分类、单日及含起止日的日期区间筛选。需要增删改查，各用户只看自己的数据。

选择 `python-basic / simple-admin / sqlite`。这个例子是回归目标：不能再一轮声称搜索支持、下一轮说不支持，也不要求把日期永远退化成未经校验的普通字符串。

### 4.1 人工交互

页面会显示结构化摘要、真正的问题、推荐默认值、状态和模型回执。必要时回答；完整以后可批准、修改或拒绝。控制指令`批准`、`“批准”`、`"批准"`会先被CLI识别，不被送进模型当成自然语言。一轮不能批准时不消耗轮数，保持原关卡。

CLI同样可以使用：

```powershell
uv run rnd chat
```

依次选择模板编号、前端、数据库，然后才问项目名和需求。提前指定组合：

```powershell
uv run rnd chat --template python-basic --frontend simple-admin --database sqlite
```

### 4.2 智能推荐与撤销

任何尚未完成的运行均可点“智能推荐”，新建时也有勾选项。等价CLI：

```powershell
uv run rnd recommend 运行UUID
uv run rnd chat --smart
```

它是对后续未确定事项的持续委托：AI自行选择可支持的默认值、保存建议，后续需求/设计/交付自动决定，不再让你点击一串批准。审批审计记录为delegated-ai，不冒充你手动批准。一个模型既不会替你执行任意shell，也不会替你允许覆盖非空数据库。

恢复人工：点击“恢复人工确认”，或 `uv run rnd manual UUID`。当前已经运行的工具不会因这个开关倒退，后续关卡恢复等待。退出浏览器或CLI并不取消后台保存的job；重新 `rnd chat --run UUID` 可继续。

确实不支持的要求不能被AI删除后假装完成。自动模式有小规模、有界的内部补全次数，仍不能形成可执行规格时BLOCKED并记录原因，不再次提问拖到无穷，也不标READY。人工可以调整或新建更合适的模板运行。

## 5. 下载、启动、检查最终产品

当本次验证和交付决定通过后显示READY。通过页面下载，或：

```powershell
uv run rnd show 运行UUID
uv run rnd download 运行UUID
```

文件在 `deliveries/运行UUID.zip`。下载接口复核文件哈希；未批准或被篡改的包不能下载。

### 5.1 默认FastAPI产品（SQLite）

将ZIP解压到新的独立目录，进入包含 `start.py`、`pyproject.toml` 的产品根目录，执行：

```powershell
uv run --no-project --python 3.14 python start.py
```

启动器安装该产品的锁定依赖、应用Alembic迁移、启动产品。`simple-admin`前端在 `http://127.0.0.1:8001/`；api-only只提供接口及 `/docs`。先注册一个产品用户，再操作自己的实体。完成后退出并重启，记录与登录数据库仍保留。

需要只初始化不启动：同一命令后追加 `--init-only`。需要换端口：追加 `--port 8002`。`--no-install`仅用于你确实已安装对应依赖的环境或测试，不推荐新手首次使用。

包内 `database/schema.sqlite.sql`、冻结Alembic迁移、approved-spec.json说明表结构。SQL文件供检查和审计；正常启动走版本迁移，**不要手工执行一遍DDL后又让迁移重复建表**。后续产品结构升级应新增迁移，不覆盖已经部署的0001或删除库。

### 5.2 默认FastAPI产品（PostgreSQL）

首次任务开始前必须选择postgresql，这个选择写入selection.json。平台验证该产品需要Docker或PRODUCT_POSTGRES_URL指定的本机测试数据库管理连接。

独立产品同样执行start.py。没有PRODUCT_DATABASE_URL时自动创建只属于该产品的Docker Compose项目、随机数据库密码、回环端口和持久卷。服务配置保存在产品`.data/deployment.json`，不是平台`.env`。已自行准备数据库时可显式设置PRODUCT_DATABASE_URL，再用start.py执行迁移。不要用生产库测试，也不默认覆盖已有业务表。

PostgreSQL产品包还含 `database/schema.postgresql.sql` 与对应迁移。Ctrl+C只停止应用，不删数据库卷。再次启动复用相同配置。备份业务数据需另做数据库备份；源码ZIP不含你的实际记录。

### 5.3 原生FastapiAdmin或芋道产品

在Linux/WSL准备Python3.14、uv、Node22和该模板的pnpm，芋道另需JDK17/Maven。安装Docker Compose后同样执行：

```bash
uv run --no-project --python 3.14 python start.py
```

产品包包括自己的部署依赖锁、启动器、原生种子、业务建表SQL、菜单SQL和哈希清单。启动器不再依赖原平台数据库、模型Key或原开发库：创建独立PG/Redis → 验证空库/归属 → 初始化原框架 → 业务DDL → 菜单 → 后端 → 前端构建 → 前后端启动。详细步骤在第二部分。

原生的 `--check` 必须到前后端都启动且新库菜单/CRUD通过后退出，不允许在前端之前提前报成功。首次完整安装可能较慢；已有同一产品的成功构建可用 `--skip-build`。更改默认管理员密码后普通重启不会要求旧密码或重置账号；显式`--check`用于开发验收，要使用其定义的测试身份前提。

## 6. 从空目录逐组创建代码

这是学习路径，与上面的clone体验路径分开。另建空目录，不在已安装项目内重复uv init：

```powershell
mkdir D:\Code\rnd-rebuild
cd D:\Code\rnd-rebuild
uv python install 3.14
uv init --bare --no-package --no-workspace --python 3.14
uv python pin 3.14
```

在VS Code中先创建 `.python-version`、`pyproject.toml`、`uv.lock`、`.gitignore`、`.gitattributes`、`.env.example`、`workbench/__init__.py`，逐字使用附录里的相应文件。确保 `.py` 不是 `.py.txt`，编码UTF-8。覆盖初始化的pyproject为本提交版本，再运行 `uv sync --locked`。

文件路径有斜线意味着先创建目录，例如 `workbench/settings.py`。每个模块创建后可 `uv run python -m py_compile workbench/settings.py`；它只是语法检查。等其依赖组齐全再执行对应测试，不提前import尚未创建的API模块。

二进制模板ZIP不能放进Markdown代码块；学习还原时从同一Git提交复制 `templates/vendor/*.zip`，随后用manifest核对。它们已经在clone内，不再要求对未来的上游master重新解析。纯源码附录还原脚本不执行代码、不会联网下载模板；复制三份已验证ZIP后即可使用完整仓库能力。

## 7. 第一组：配置、输入契约和数据库

创建 `workbench/settings.py`、`catalog.py`、`domain.py`、`errors.py`、`store.py`、`alembic.ini` 和 `migrations/`中的完整文件。settings依赖Pydantic Settings，domain和catalog不依赖HTTP；store读取配置并提供短事务，禁止反向import api。

| 文件 | 负责什么 |
|---|---|
| settings.py | 固定数据目录、默认/阶段模型、安全继承、预算；工作目录变化不能移动数据库 |
| catalog.py | 真实后端/前端/数据库组合和支持能力；模型无法通过输出一个supported=true创造功能 |
| domain.py | 输入、结构化需求、计划、规则补丁、智能委托和模型审阅格式；拒绝未知字段 |
| errors.py | 可恢复预算暂停等错误类型，与不可恢复失败区分 |
| store.py | 项目、运行、消息、审批、job、阶段回执、幂等键、委托状态、事件及模型调用记录 |
| migrations | 冻结数据库演进；现有用户不删除库也能升级 |

SQLite开启foreign_keys、WAL、busy_timeout；Python3.14显式事务设置。事务中只做数据库工作，不把LLM调用、Git或前端构建包进数据库事务。Engine长期复用、Session每次独立。时间使用明确带UTC偏移的字符串，避免读回无时区对象。

迁移现有库：

```powershell
uv run alembic upgrade head
uv run alembic current
uv run alembic check
```

首次使用已提交revision，不再另造0001。改变模型才用 `revision --autogenerate -m "具体变更"`，人工阅读增加/删除项再upgrade。自动生成是候选，不自动理解数据重命名与搬迁。测试里可对临时库create_all，生产和真实学习数据用迁移。

创建 tests/conftest.py、test_contracts.py、test_store.py，运行：

```powershell
uv run pytest tests/test_contracts.py tests/test_store.py -q
```

通关：提交/回滚、真实外键、幂等、时间/路径、旧库升级、输入不伪造身份都通过。`test_learning_order.py`还验证这一数据库学习阶段不依赖未来的API或Agent模块。

## 8. 第二组：消息、长期会话、审批与智能委托

创建 `workbench/conversation.py`，继续阅读store的 `request/create_run/submit/set_automation/auto_approve`。

一个请求在同一事务保存原始消息、运行和待处理job，不出现“成功保存了需求却没有任务”。Idempotency-Key绑定请求指纹：同一个请求重试返回同一结果，不同内容重用同键返回409。并发控制由文件锁/PG事务锁保证，而不是让模型决定。

需求和设计的gate_id绑定run、阶段、轮次与内容摘要。普通审批必须来自当前等待点、显式布尔值。智能推荐是另一种显式授权，保存auto_mode、授权事件与delegated-ai审批；不能把“模型说批准”当作用户动作。

conversation先识别去引号的控制词，再拼模型上下文。上下文保留原始目标、当前结构化需求、最近明确修正和真实模板能力。新的明确修正优先；日期区间边界、长度默认值等不再拆成很多不必要轮次。LLM仍可能给出不良问题，用户可持续委托或人工修正，不承诺任意模型永远一次正确。

```powershell
uv run pytest tests/test_guided_workflow.py tests/test_guided_completion.py -q
```

测试应覆盖超过13个人工轮次仍正常、四个不同关卡启用智能推荐后无后续人工输入、关闭并重开Runtime仍保留委托、正数预算暂停后同run恢复、真正不支持项BLOCKED而非无限循环、控制指令不能被当作新回答。

## 9. 第三组：多模型边界和运行回执

创建 `workbench/llm.py`、阅读settings.ModelProfile与 `tests/test_guided_models.py`。

调用key将任务映射到requirements/planning/coding/review，解析有效地址、密钥、模型名；缓存身份包括阶段/地址/模型，不包含明文密钥。更改模型不会错误复用另一模型的响应。响应必须经过Pydantic严格验证；未知字段、错误JSON、超长响应、鉴权失败或超时明确报错。调用前记录预算尝试，外部服务失败也不免费假装成功。

每个完成调用的回执保存实际模型配置（不含密钥）、阶段、usage和结果引用。`GET /runs/{id}/models`及页面用于确认实际用了哪个模型，而不是只看.env猜。

```powershell
uv run pytest tests/test_llm.py tests/test_guided_models.py -q
```

单元测试用显式HTTP transport夹具验证不同服务/模型、Key隔离、默认继承和计数；真实供应商由自己的.env联调，CI不使用用户真实Key。

## 10. 第四组：文件、模板快照、索引与规则

在workbench目录创建filesystem.py、vendor.py、tools.py、symbols.py、knowledge.py、retrieval.py、context_mcp.py、toolchain.py、rules.py、coding.py、aider_tool.py和sandbox.py，全部内容见源码附录。第20章逐项说明解析、检索、Continue、Aider和Daytona的安装、接线与测试。

filesystem负责原子写、路径边界、普通文件与ZIP大小、符号链接/路径遍历/重复文件检查及哈希。API不能接收任意shell命令或任意主机路径。tools的命令来自可信代码参数数组，shell=False；环境只透传必需路径和显式配置，排除平台模型密钥；超时停止进程组并保留有界首尾日志。

vendor读取manifest，核对ZIP整体SHA和解压后的文件指纹与LICENSE。重复init复用有效缓存，篡改立即拒绝。三份模板在仓库内，源码未变化就不反复解析。knowledge记录文件SHA、符号起止行与增量状态；Python使用标准库AST，Java/TypeScript/JavaScript以及Vue内嵌script通过symbols中的Tree-sitter解析。Java类、方法、字段、注解和继承，TS声明，以及Vue组件标签与真实源码行号进入符号索引；这不是完整的跨模块类型推导或调用图，编译和类型检查仍然必需。retrieval提供SQLite FTS5与可选独立授权向量检索，context_mcp向Continue开放只读查询，toolchain把同一上下文接入规划。输出目录必须位于被索引源码之外。

```powershell
uv run rnd index workbench .data/platform-knowledge
```

第二次应显示reused增长。读取任务上下文前再核对指纹，过期或超预算时明确失败；不把.env、数据库、依赖缓存或全仓库默认发给模型。

rules只解释白名单AST，不能import/exec模型文件。coding只修改custom_rules.py，携带当前原文件SHA；日期/枚举/搜索本来由模板支持，不能每个项目都交给编码Agent重写。类型不合或前像不匹配拒绝；不允许改认证、数据库迁移和可信测试来蒙混。

```powershell
uv run pytest tests/test_safety.py tests/test_vendor.py tests/test_tools_cli.py -q
```

设计图由规格生成。date/enum必须正确出现在ER图，所选PG产品不能画成SQLite。图旁标记设计来源，不冒充生产反射；`test_guided_completion`覆盖用户资讯规格。

## 11. 第五组：默认生成产品的完整后端与轻量前端

按附录创建 `templates/product/` 全部源码及锁文件、`templates/frontends/simple-admin/` HTML/CSS/JS，再创建generator.py。

schema读取冻结规格建立ORM结构，app提供登录、用户隔离、CRUD、搜索和筛选，manage/start负责迁移和运行。search/filter的字段来自已批准Plan白名单，不拼接任意用户SQL列名，所有值通过SQLAlchemy参数绑定。date用真实日历校验，YYYY-MM-DD只是格式不是闰日正确性的替代；enum验证固定选项，optional空值有明确含义。

schema-spec和SQL DDL由同一元数据生成，SQLite和PostgreSQL分别输出。分类和日期作为原生类型支持，长度限制在API和HTML表单双层体现。输入 `0` 或 `false` 不能因truthy判断变成空值。

simple-admin不是框架原生UI的假替身，它是明确可选的轻量前端。用户可选择api-only不用它。页面通过真正fetch操作产品API，有登录、列表、新增/编辑、删除、搜索、分类/日期筛选和分页。采用textContent避免把需求文字当HTML执行。清除筛选必须恢复所有控件，并丢弃旧请求的晚到响应；浏览器回归会连续切换关键词、分类、单日和区间。

```powershell
uv run pytest tests/test_news_delivery.py tests/test_guided_selection.py -q
```

这组测试验证用户日志里的具体案例，不以一个最简单的hello接口替代复杂字段和过滤要求。

## 12. 第六组：独立验证、修复、模型审阅与打包

创建verification.py并阅读templates/product/verify.py、product_database.py。产品以独立进程真实启动，不从Agent的“我测过了”获取结论。测试账号、登录、越权、字段、CRUD、搜索筛选、进程重启全部通过才继续。

平台默认给产品创建自己的uv环境；集成测试可显式用已有依赖减少下载，但另有ci_clean_install真实安装验证。PG产品验证用独立数据库，不能替换成SQLite后仍声称PG已测。

测试失败归类：业务规则问题最多两轮修复，再失败停止；环境安装/密码/服务问题不交给模型乱改业务。审阅模型只看到需求、规格与已有测试证据；额外缺口报告不能伪造执行日志或覆盖failed结果。

打包前冻结文件SHA，打包后在全新目录验证ZIP清单、安装/迁移/启动/再测，最后等待人工交付或已授权的智能推荐决定。默认产品下载不需要平台继续在线。产物包含源码及SQL，不包含测试用户或真实数据文件。

```powershell
uv run python -m scripts.ci_clean_install
```

这条集成命令不消费模型Key，但真的新建产品环境和干净解压环境。测试夹具的事实必须在报告中明确区分。

## 13. 第七组：LangGraph、Worker和HTTP

创建flow.py、runtime.py、api.py、cli.py、workbench/web/所有页面文件。前面的已测试函数由图连接，不在一个庞大节点里混合调用模型、等待用户和扣费写库。

实际流程节点：analyse → requirements gate → source_context（索引、检索与Repo Map）→ plan → design gate → generate → code（需要时）→ verify；可修复失败经repair回到code，再次verify；验证通过后进入sandbox（已授权时执行Daytona，否则记录未启用）→ model_review（可选）→ package（含独立解压复验）→ delivery gate。source_context不调用聊天模型，也不默认上传向量；code按CODING_ENGINE使用原有受限引擎或真实Aider；sandbox失败不能跳到交付。状态主要保存runID、版本、结构化规格、有界上下文与回执，不保存ZIP字节或整个仓库。

interrupt恢复时节点重入，所以副作用需要回执和幂等。runUUID是稳定thread_id；数据库已保存的授权再次在图层校验。Worker保存last_job_id，崩溃时不会把同一回答消费到下一道审批。单Worker由本地文件锁及PG锁限制；并行HTTP和多个原生重型任务不等于已经实现分布式执行器。

API快速写入job然后返回，不让长时间Maven构建占住HTTP请求。lifespan启动和停止连接；`/health`表示进程活着，`/ready`检查数据库与Worker。所有用户数据、运行、模型回执和下载使用本机Bearer令牌。

| 接口 | 功能 |
|---|---|
| GET /catalog、/models | 当前实际模板组合与阶段模型，无密钥 |
| POST /projects、POST /projects/{id}/runs | 创建项目、选项/需求同事务入队 |
| GET /runs/{id}、/messages、/events、/models | 状态、完整消息、事件、实际模型使用 |
| POST /runs/{id}/resume | 当前gate的回答、批准、拒绝、修改 |
| POST /runs/{id}/automation | 显式开启智能推荐或恢复人工 |
| POST /runs/{id}/retry | 可恢复的失败/暂停保留原ID重试 |
| GET /runs/{id}/report、/download | 真实验证证据及已批准且哈希正确的包 |

```powershell
uv run pytest tests/test_api.py tests/test_workflow.py tests/test_guided_workflow.py -q
uv run python -m scripts.ci_guided_browser
```

浏览器集成需预先安装独立Playwright1.56.1/Chromium；普通使用轻量页面不需要本机安装Playwright。该脚本使用三个明确的本机HTTP模型夹具，真正打开平台页面，先选模板，再输入用户资讯需求，点智能推荐后不再人工确认，下载并打开独立产品，真实搜索筛选；不是mock页面请求。

## 14. 运行状态、预算、恢复与升级

QUEUED/RUNNING是执行中；WAITING_CLARIFICATION/REQUIREMENTS/DESIGN/DELIVERY是人工等待；智能推荐可自动处理可支持的后续等待点。READY是当次工具验证与交付决定完成；SOURCE_READY是旧原生导出语义；REJECTED不继续；BLOCKED是明确能力冲突；PAUSED_LIMIT保留用户指定预算；FAILED是实际执行错误。

旧日志中的最后答案会在数据库messages保存。升级后不要新建同名项目再重打全部需求。确认备份、迁移、去掉旧限额，重试原UUID后可以继续。将来大幅修改图结构时不保证所有历史checkpoint任意跨版本恢复；升级前备份，保留旧环境完成已运行任务。

每个运行的前后端/数据库选择是冻结选项，防止拿新设置误解释旧产物；修改.env的模型用于后续尚未完成阶段，已落盘的结果和实际模型回执不被重写。API限额不是供应商余额控制，要自己管理供应商预算。

## 15. 本地数据、目录和备份

```text
.data/
  workbench.db / checkpoints.db    控制数据与工作流断点，职责不同
  access-token                    平台本机令牌，不是模型Key
  sources/ knowledge/             解压后的固定模板与可重建索引
  runs/<UUID>/                    规格、产品、生成/测试/交付证据
  native-services/<UUID>/          原生任务自己的服务配置与密码，勿共享
  native/                         可选显式原生运行配置
templates/vendor/                 clone自带的固定源码ZIP与许可证
```

停止平台和Worker后备份完整.data，不只复制正在写入的SQLite主文件而漏掉WAL。PostgreSQL备份还需其数据库备份工具。新交付包的`.deployment`或`.data`保存它自己生成的服务密码，不能加入Git或再分发。

平台可使用PostgreSQL：`uv sync --locked --all-extras`后设置DATABASE_URL。CHECKPOINT_URL可分离图断点库。新空库有迁移和真实CI验证；旧SQLite历史数据并不会因改URL自动搬过去，需要另行数据迁移与恢复验证，不能承诺零操作切库。

## 16. 原生源码、独立SQL与部署边界

这部分详见下一章的逐条命令。核心区别：平台运行用专用开发库生成模块；**最终产品无需复用这个开发库**。它携带独立启动器和原生初始化/业务DDL/菜单SQL，可在另一专用空库真正启动。用户数据、开发测试账号数据不会从开发库导出到菜单脚本。

`portable.py`先保存原生菜单快照，生成后只导出新增/变化菜单，使用SQL标识符和值转义，不拼模型原始SQL。`deployment/manifest.json`绑定规格和SQL哈希；原生SQL种子来自锁定的源码。数据库注释标记claimed/ready与此产品身份，拒绝非空的无关库，重复启动不会覆盖用户名密码。

只有原生全链成功、独立新库启动检查也成功，托管结果才为runtime_verified。单元测试模拟边界只检查契约，不当作真实全栈证据。完整原生矩阵必须跑真实语言工具、数据库、后端、前端和浏览器。

## 17. 正式Actions与手册一致性

正式PR不能只包含“运行过的候选截图”。Actions对提交的源码运行：Linux/Windows回归、PG平台与产品测试、默认产品独立安装、真实工作台和资讯页面浏览器、原生两套生成与独立交付新库启动。CI无需真实模型Key，夹具是显式的；验证你的供应商只能用本机.env。

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest -m "not postgres" -q
uv run python -m scripts.build_handbook --check
```

源码或正文有改动时：

```powershell
uv run python -m scripts.build_handbook
```

生成器把docs正文与当前真实文件完整组合成两个相同手册路径。每个源码块带SHA；test_handbook验证逐块一致性与空目录还原后再次生成相同手册。二进制vendorZIP在Git中单独保存，附录用manifest和许可证描述，不把二进制伪装成代码块。

手工学习创建顺序可照第7—13章；全部源码齐全后再执行全量测试。复现安装始终 `--locked`；依赖更新需提交真实新锁并重跑，不由AI随意修改锁内容。

## 18. 故障定位与通关清单

| 问题 | 正确处理 |
|---|---|
| ModuleNotFoundError | 回到含pyproject的根目录，uv sync --locked；使用包路径workbench，不混用旧from main |
| 超轮数/调用上限 | 检查.env是否仍写旧正数；默认0；改好重启并retry同一UUID |
| 智能推荐仍BLOCKED | 阅读真实unsupported/范围冲突；不为通过而删需求或修改权限 |
| 平台401 / 模型401 / 产品401 | 分别检查rnd token / API_KEY / 产品登录token，不混用 |
| 搜索筛选结果不对 | 核对Plan searchable/filterable/date_range、真实API与前端请求；先清除旧条件，检查日期格式 |
| 原生数据库非空 | 保留现场，不取消保护或自动DROP；使用新的明确授权空库 |
| 前端构建或类型失败 | 保留真实日志，不删页面、不跳过类型；按固定上游兼容适配核对 |
| 独立包只有后台通过 | --check必须前端启动后才成功，不能减少验收项掩盖错误 |
| 浏览器工作台显示KeyError | 现在错误含源码位置；日期/枚举图表有回归测试，检查你是否使用同提交完整源码 |
| 手册不一致 | 修改正文源或代码后重新build_handbook，不手工只改生成文档或关闭测试 |

通关顺序：配置单模型 → 可选阶段覆盖验证 → 选择组合后新建 → 人工13+轮不丢数据 → 任意关卡智能推荐后无后续提问 → 用户资讯案例完整字段与搜索筛选 → 独立产品启动 → 原生环境及独立新库交付 → Windows/Linux/PG/浏览器CI → 整本手册一致。实际结果必须有对应提交的报告，不凭README一句“已通过”。

### 官方资料

uv项目与Actions：https://docs.astral.sh/uv/guides/projects/ 、https://docs.astral.sh/uv/guides/integration/github/
Python3.14 sqlite3事务：https://docs.python.org/3.14/library/sqlite3.html
SQLAlchemy SQLite：https://docs.sqlalchemy.org/en/20/dialects/sqlite.html
Alembic候选迁移：https://alembic.sqlalchemy.org/en/latest/autogenerate.html
LangGraph中断恢复：https://docs.langchain.com/oss/python/langgraph/interrupts
Pydantic Settings：https://docs.pydantic.dev/latest/concepts/pydantic_settings/
FastapiAdmin：https://github.com/fastapiadmin/FastapiAdmin
芋道：https://gitee.com/yudaocode/yudao-cloud-mini 、https://gitee.com/yudaocode/yudao-ui-admin-vben
这些文档解释工具行为；本项目可复现版本以同一提交的uv.lock、vendor manifest、代码及测试为准。
