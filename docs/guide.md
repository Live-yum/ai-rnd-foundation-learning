# 从零实现 AI 研发平台：逐步实操手册

**统一主线：内部客户服务管理系统，从需求、合同、代码到三个模板的独立产品与验收。**

**Python 3.14 · uv · FastAPI · SQLite/可选PostgreSQL · LangGraph · 可选多模型 · 智能推荐 · 自带原生模板**

这是一份完整的实现与操作手册：前半部分按学习顺序说明创建什么、连接到哪里、如何运行与测试；后半部分直接包含同一提交中的全部文本源码、配置、数据库迁移、前端、测试和依赖锁。全文描述一个一致的最终系统，不需要任何较早版本、骨架项目或差异补丁。

本手册只有一个正式文件：`从零实现AI研发平台_逐步实操手册_完整版.md`。你可以只拿到这一份文档，从空文件夹逐个创建本项目的全部源文件。语言解释器、Python包和第三方开源框架属于明确安装的依赖，不要求预先拥有本项目仓库。

**阅读顺序**：先完成第2章的工具准备，按照第6—13章和“逐文件实现讲解”创建文件；每写完一组，紧接着做“动手写与跑”的对应完整小实验，再回到第3—5章体验平台。完整源码区的每个标题就是要创建的文件路径，代码块不省略实现。希望先体验的读者可以在已经取得的演示源码目录直接执行第3—5章，但这不是手写学习的前置条件。

**运行边界**：仅需求理解、规划、规则编码和语义审阅的大模型接口允许使用外部推理服务。索引、检索、向量模型、MCP、Aider、数据库、Daytona控制面及执行器全部在本机。下载依赖、浏览器或固定第三方源码属于安装阶段，不把业务任务交给云端工具执行。

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

上表说明不带`Plan.business`的基础CRUD路径。带业务合同的共享产品另按“从实体CRUD写到有权限、有流程的业务产品”章节处理关联、角色行权限、状态、提醒和统计；仍必须逐关验证，不把普通CRUD的报告借给业务合同使用。

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

Linux/WSL的Ubuntu终端先安装本机Git、curl和uv，不运行PowerShell安装器：

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
git --version
uv --version
```

VS Code从官方安装页按你的系统安装。Windows安装Git时保留命令行PATH选项，安装编辑器后重新打开终端；先看到git和uv版本号，再创建下面的目录。Windows需要原生Java/Vue或Daytona时，在管理员PowerShell执行`wsl --install -d Ubuntu`，按提示重新启动并设置Ubuntu本机用户名；随后所有Linux命令在Ubuntu中执行。默认Python/SQLite演示不需要WSL。

### 2.2 创建一个真正的空文件夹

Windows打开PowerShell；先在文件资源管理器中打开“查看 → 显示 → 文件扩展名”，避免把`app.py`保存为`app.py.txt`。选择你有写权限的位置，例如：

```powershell
New-Item -ItemType Directory -Path "$HOME\rnd-learning"
Set-Location "$HOME\rnd-learning"
uv python install 3.14
code .
```

Linux/WSL使用：

```bash
mkdir -p ~/rnd-learning
cd ~/rnd-learning
uv python install 3.14
code .
```

这时目录中不需要任何代码，也不用运行`git clone`或下载本项目骨架。VS Code是编辑器，PowerShell/Bash是执行命令的终端，Python是执行`.py`文件的解释器，uv负责创建`.venv`并安装精确依赖；它们不是同一个东西。

在VS Code左侧按“新建文件”，输入完整相对路径。斜线前是文件夹，例如`workbench/settings.py`表示在workbench文件夹创建settings.py。复制完整源码区同名文件的整个代码块，不复制外层反引号、行号或标题。保存时选择UTF-8。`#`是Python注释；英文标点和缩进必须保留。

先写第6章列出的项目配置文件，之后才能执行`uv sync --locked`。不要先执行后面的API或模型命令，因为相关模块还没有写出来。

### 2.3 第三方源码不是隐含的骨架

本平台的Python/Java原生框架是第三方依赖。书中给出了`scripts/vendor_templates.py`的全部代码及三个固定源码提交。手写完成这个脚本和模板清单以后执行：

```powershell
uv run python -m scripts.vendor_templates --fetch
```

脚本只从登记的三个公开上游拉取指定SHA，验证许可证，排除Git历史、依赖缓存、密钥、数据库和字体二进制，重建`templates/vendor/*.zip`。它不下载本项目的Python实现，不要求复制已有仓库中的任何骨架文件。先写代码再执行脚本，下载的第三方框架与语言包一样是显式依赖。

最终演示仓库已带这三个普通Git ZIP；直接使用演示仓库的人不需要重复下载。无论采取哪种路径，`rnd init`都校验模板清单并在本机解压到`.data/sources`，不会覆盖`.env`或清空数据库。

安装依赖、模型权重、浏览器、Maven/pnpm包及Daytona镜像需要网络。准备完成以后索引和工具执行不调用云端服务；这不等于无需安装任何软件的完全离线发行版。

### 2.4 在生成带界面的产品前安装浏览器验收工具

`simple-admin`产品需要Node22与本机Playwright1.56.1/Chromium。请先完成本书“从空目录到可信交付”站点4中的Windows或Linux安装与环境变量设置，再在同一终端启动平台。缺少这些工具会阻止交付，不会将浏览器验收记为跳过。api-only没有页面，才允许浏览器项标记不适用。

## 3. 配置模型：单模型先跑通，多模型按需启用

先在项目根目录创建配置文件，已有`.env`则保留，不覆盖里面的密钥。PowerShell：

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Linux/WSL Bash：

```bash
[ -e .env ] || cp .env.example .env
```

再用编辑器打开根目录`.env`，只把下面三个占位内容改为你自己服务商的值。不要把密钥写到Python源码、命令历史、Git提交或教材截图里：

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

第一次使用同一个标准客服案例。先在本书完整源码区创建`examples/requirements/customer-service.md`、`customer-service-decisions.md`和`customer-service-contract.md`（后两份在同一目录），按顺序把三份完整文本一起填入页面。原始需求保留原文，默认决策补充站内提醒、角色范围和统计口径，命名约定明确黑盒验收字段；不把固定Plan当模型答案。下面只是核对摘要，不能用摘要删去原文条目：

> 建设公司内部客户服务管理平台：维护客户档案和历史服务记录；创建服务请求、分配负责人、按批准流程改变状态并追加处理记录；支持协作任务、站内提醒和不可修改的操作审计；提供服务数量、创建到解决的时长、客户分组和每日趋势统计。管理员、客服、普通员工按角色及负责/创建范围访问数据。沿用所选框架的原生认证、ORM、事务与UI组件，并交付可在新目录和新数据库独立启动的产品。

先选择本次要运行的模板组合，再输入需求。基础入口为`python-basic / simple-admin / sqlite`；两个原生入口分别为`fastapiadmin / fastapiadmin-vue / postgresql`及`yudao-vben / vben-antd / postgresql`。原生环境需要先完成第19章准备。设计必须形成完整`Plan.business`，保留客户→请求→任务的关联、三角色行权限、指派、状态、记录、提醒和四类统计，不能退化成三个互不相关的CRUD页面。

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

启动器安装该产品的锁定依赖、应用Alembic迁移、启动产品。`simple-admin`前端在 `http://127.0.0.1:8001/`；api-only只提供接口及 `/docs`。客服产品必须先初始化业务管理员：在产品目录另开终端，执行以下命令，并按隐藏密码提示输入两次（不要把密码写进命令或配置）：

```powershell
uv run python manage.py bootstrap-admin --username manager
```

此入口只允许一次成功的初始化，失败不会覆盖原账号。用该账号登录后再创建客服、员工或给已有账号分配产品角色。普通注册只得到合同中的employee角色，不能靠抢先注册成为管理员。产品角色/行权限来自`Plan.business`，不会把所有员工的数据一律开放。完成后退出并重启，记录与账号数据库仍保留。

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

这是本书的主学习路径。沿用第2章创建的空文件夹，不再创建第二套项目，也不执行会生成隐含骨架的初始化命令：

```powershell
# 在已经创建的空文件夹打开终端，确认位置
Get-Location
uv python install 3.14
```

在VS Code中先创建 `.python-version`、`pyproject.toml`、`uv.lock`、`.gitignore`、`.gitattributes`、`.env.example`、`README.md`、`workbench/__init__.py`、`workbench/local_only.py`，逐字使用附录里的相应文件。确保 `.py` 不是 `.py.txt`，编码UTF-8。把本书给出的pyproject和uv.lock完整保存，再运行 `uv sync --locked`。

文件路径有斜线意味着先创建目录，例如 `workbench/settings.py`。每个模块创建后可 `uv run python -m py_compile workbench/settings.py`；它只是语法检查。等其依赖组齐全再执行对应测试，不提前import尚未创建的API模块。

二进制模板ZIP不需要手工输入或从本项目复制。第2.3节的脚本会从固定第三方源码生成它们。你手写的平台实现全部在本书中，包括脚本本身、模板的自有适配代码、前端、测试、配置和锁文件。“逐文件实现讲解”还给出完整的创建组、输入输出、调用关系与验证方式。

## 7. 第一组：配置、输入契约和数据库

创建 `workbench/local_only.py`、`workbench/settings.py`、`business_contracts.py`、`business_capabilities.py`、`catalog.py`、`domain.py`、`errors.py`、`store.py`、`alembic.ini` 和 `migrations/`中的完整文件。local_only定义仅本机工具策略并关闭遥测；settings依赖Pydantic Settings和local_only，domain和catalog不依赖HTTP；store读取配置并提供短事务，禁止反向import api。

| 文件 | 负责什么 |
|---|---|
| settings.py | 固定数据目录、默认/阶段模型、安全继承、预算；工作目录变化不能移动数据库 |
| business_contracts.py / business_capabilities.py | 先写有限业务合同及能力登记，供domain与catalog读取；不依赖后续API或Worker |
| catalog.py | 真实后端/前端/数据库组合和支持能力；模型无法通过输出一个supported=true创造功能 |
| domain.py | 输入、结构化需求、计划、规则补丁、智能委托和模型审阅格式；拒绝未知字段 |
| errors.py | 可恢复预算暂停等错误类型，与不可恢复失败区分 |
| store.py | 项目、运行、消息、审批、job、阶段回执、幂等键、委托状态、事件及模型调用记录 |
| migrations | 冻结数据库演进；现有用户不删除库也能升级 |

SQLite开启foreign_keys、WAL、busy_timeout；Python3.14显式事务设置。事务中只做数据库工作，不把LLM调用、Git或前端构建包进数据库事务。Engine长期复用、Session每次独立。时间使用明确带UTC偏移的字符串，避免读回无时区对象。

在空数据库按已有的完整迁移文件创建全部控制表：

```powershell
uv run alembic upgrade head
uv run alembic current
uv run alembic check
```

首次使用本书完整给出的revision，不需要自己猜测0001。以后主动改变模型时才用 `revision --autogenerate -m "具体变更"`，人工阅读增加/删除项再upgrade。自动生成是候选，不自动理解数据重命名与搬迁。测试里可对临时库create_all，生产和真实学习数据用迁移。

创建 tests/conftest.py、test_contracts.py、test_store.py，运行：

```powershell
uv run pytest tests/test_contracts.py tests/test_store.py -q
```

通关：提交/回滚、真实外键、幂等、时间/路径、迁移顺序、输入不伪造身份都通过。`test_learning_order.py`还验证这一数据库学习阶段不依赖未来的API或Agent模块。

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

在workbench目录创建filesystem.py、vendor.py、tools.py、symbols.py、knowledge.py、retrieval.py、context_mcp.py、toolchain.py、rules.py、coding.py、aider_tool.py、local_only.py、daytona_worker.py和sandbox.py，全部内容见源码附录。第20章逐项说明解析、检索、Continue、Aider和Daytona的安装、接线与测试。

filesystem负责原子写、路径边界、普通文件与ZIP大小、符号链接/路径遍历/重复文件检查及哈希。API不能接收任意shell命令或任意主机路径。tools的命令来自可信代码参数数组，shell=False；环境只透传必需路径和显式配置，排除平台模型密钥；超时停止进程组并保留有界首尾日志。

vendor读取manifest，核对ZIP整体SHA和解压后的文件指纹与LICENSE。重复init复用有效缓存，篡改立即拒绝。三份模板由固定源码生成后保存在本机，源码未变化就复用已解析条目。knowledge记录文件SHA、符号起止行与增量状态；Python使用标准库AST，Java/TypeScript/JavaScript以及Vue内嵌script通过symbols中的Tree-sitter解析。Java类、方法、字段、注解和继承，TS声明，以及Vue组件标签与真实源码行号进入符号索引；这不是完整的跨模块类型推导或调用图，编译和类型检查仍然必需。retrieval提供SQLite FTS5与可选本机向量检索，context_mcp向Continue开放只读查询，toolchain把同一上下文接入规划。输出目录必须位于被索引源码之外。

```powershell
uv run rnd index workbench .data/platform-knowledge
```

第二次应显示reused增长。读取任务上下文前再核对指纹，过期或超预算时明确失败；不把.env、数据库、依赖缓存或全仓库默认发给模型。

rules只解释白名单AST，不能import/exec模型文件。coding只修改custom_rules.py，携带当前原文件SHA；日期/枚举/搜索本来由模板支持，不能每个项目都交给编码Agent重写。类型不合或前像不匹配拒绝；不允许改认证、数据库迁移和可信测试来蒙混。

```powershell
uv run pytest tests/test_safety.py tests/test_vendor.py tests/test_tools_cli.py -q
```

设计图由规格生成。date/enum必须正确出现在ER图，所选PG产品不能画成SQLite。图旁标记设计来源，不冒充生产反射；客服规格还必须在图和结构中保留客户、请求、任务的引用及业务合同，不用独立的三个表冒充关联。

## 11. 第五组：默认生成产品的完整后端与轻量前端

按附录创建 `templates/product/` 全部源码及锁文件、`templates/frontends/simple-admin/` HTML/CSS/JS，再创建generator.py。

schema读取冻结规格建立ORM结构，app提供登录、用户隔离、CRUD、搜索和筛选，manage/start负责迁移和运行。search/filter的字段来自已批准Plan白名单，不拼接任意用户SQL列名，所有值通过SQLAlchemy参数绑定。date用真实日历校验，YYYY-MM-DD只是格式不是闰日正确性的替代；enum验证固定选项，optional空值有明确含义。

schema-spec和SQL DDL由同一元数据生成，SQLite和PostgreSQL分别输出。分类和日期作为原生类型支持，长度限制在API和HTML表单双层体现。输入 `0` 或 `false` 不能因truthy判断变成空值。

simple-admin不是框架原生UI的假替身，它是明确可选的轻量前端。用户可选择api-only不用它。页面通过真正fetch操作产品API，有登录、列表、新增/编辑、删除、搜索、分类/日期筛选和分页。采用textContent避免把需求文字当HTML执行。清除筛选必须恢复所有控件，并丢弃旧请求的晚到响应；浏览器回归会连续切换关键词、分类、单日和区间。

```powershell
uv run pytest tests/test_business_contracts.py tests/test_business_python.py tests/test_guided_selection.py -q
```

这组测试验证用户日志里的具体案例，不以一个最简单的hello接口替代复杂字段和过滤要求。

## 12. 第六组：独立验证、修复、模型审阅与打包

创建verification.py并阅读templates/product/verify.py、workbench/postgres_lab.py。产品以独立进程真实启动，不从Agent的“我测过了”获取结论。测试账号、登录、越权、字段、CRUD、搜索筛选、进程重启全部通过才继续。

平台默认给产品创建自己的uv环境；集成测试可显式用已有依赖减少下载，但另有ci_clean_install真实安装验证。PG产品验证用独立数据库，不能替换成SQLite后仍声称PG已测。

测试失败归类：业务规则问题最多两轮修复，再失败停止；环境安装/密码/服务问题不交给模型乱改业务。审阅模型只看到需求、规格与已有测试证据；额外缺口报告不能伪造执行日志或覆盖failed结果。

打包前冻结文件SHA，打包后在全新目录验证ZIP清单、安装/迁移/启动/再测，最后等待人工交付或已授权的智能推荐决定。默认产品下载不需要平台继续在线。产物包含源码及SQL，不包含测试用户或真实数据文件。

```powershell
uv run python -m scripts.ci_clean_install
```

这条集成命令不消费模型Key，但真的新建产品环境和干净解压环境。测试夹具的事实必须在报告中明确区分。

## 13. 第七组：LangGraph、Worker和HTTP

创建flow.py、runtime.py、api.py、cli.py、workbench/web/所有页面文件。前面的已测试函数由图连接，不在一个庞大节点里混合调用模型、等待用户和扣费写库。

实际流程节点：analyse → requirements gate → source_context（索引、检索与Repo Map）→ plan → design gate → generate → code（需要时）→ verify；可修复失败经repair回到code，再次verify；验证通过后进入sandbox（已显式启用时执行本机自托管Daytona，否则记录未启用）→ model_review（可选）→ package（含独立解压复验）→ delivery gate。source_context不调用聊天模型，也不默认计算向量；code按CODING_ENGINE使用受限表达式引擎或真实Aider；sandbox失败不能跳到交付。状态主要保存runID、版本、结构化规格、有界上下文与回执，不保存ZIP字节或整个仓库。

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

浏览器集成需预先安装独立Playwright1.56.1/Chromium；普通使用产品页面不需要本机安装Playwright。ci_guided_browser保留基础交互的历史回归，不作为当前客服标准例的完整证据。客服验收走业务章节的三个模板检查、真实三角色页面与独立部署；输入和响应夹具应明确标记，不能mock页面请求或借用旧案例的报告。

## 14. 运行状态、预算与恢复

QUEUED/RUNNING是执行中；WAITING_CLARIFICATION/REQUIREMENTS/DESIGN/DELIVERY是人工等待；智能推荐可自动处理可支持的后续等待点。READY是当次工具验证与交付决定完成；SOURCE_READY是旧原生导出语义；REJECTED不继续；BLOCKED是明确能力冲突；PAUSED_LIMIT保留用户指定预算；FAILED是实际执行错误。

每一条回答都保存在messages表。关闭浏览器不会丢失运行；用同一UUID重新进入即可读取当前等待点。达到显式预算后可调整预算并重启，再重试原UUID；不是再建同名项目、重复输入需求或删除数据库。流程断点、原始消息和工具回执共同解释“已经做到了哪一步”。

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
templates/vendor/                 固定第三方源码ZIP与许可证
```

停止平台和Worker后备份完整.data，不只复制正在写入的SQLite主文件而漏掉WAL。PostgreSQL备份还需其数据库备份工具。新交付包的`.deployment`或`.data`保存它自己生成的服务密码，不能加入Git或再分发。

平台可使用PostgreSQL：`uv sync --locked --all-extras`后设置DATABASE_URL。CHECKPOINT_URL可分离图断点库。新空库有迁移和真实CI验证；SQLite数据并不会因改URL自动搬过去，需要另行数据迁移与恢复验证，不能承诺零操作切库。

## 16. 原生源码、独立SQL与部署边界

这部分详见下一章的逐条命令。核心区别：平台运行用专用开发库生成模块；**最终产品无需复用这个开发库**。它携带独立启动器和原生初始化/业务DDL/菜单SQL，可在另一专用空库真正启动。用户数据、开发测试账号数据不会从开发库导出到菜单脚本。

`portable.py`先保存原生菜单快照，生成后只导出新增/变化菜单，使用SQL标识符和值转义，不拼模型原始SQL。`deployment/manifest.json`绑定规格和SQL哈希；原生SQL种子来自锁定的源码。数据库注释标记claimed/ready与此产品身份，拒绝非空的无关库，重复启动不会覆盖用户名密码。

只有原生全链成功、独立新库启动检查也成功，托管结果才为runtime_verified。单元测试模拟边界只检查契约，不当作真实全栈证据。完整原生矩阵必须跑真实语言工具、数据库、后端、前端和浏览器。

## 17. 正式Actions与手册一致性

正式PR不能只包含“运行过的候选截图”。Actions对提交的源码运行：Linux/Windows回归、PG平台与产品测试、默认产品独立安装、真实工作台/产品页面浏览器及客服三角色业务浏览器、原生两套生成与独立交付新库启动。常规回归不注入真实模型Key，夹具是显式的；真实DeepSeek客服验收另走经过授权的本机配置或rnd环境手动任务，并记录同一提交身份。

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

生成器把全部正文、逐文件讲解与真实源码完整组合成唯一正式手册。每个源码块带SHA；test_handbook验证逐块一致性与空目录还原后再次生成相同手册。客服章节在建档、权限、分配、历史、提醒和统计处配有真实浏览器截图；图注注明模板、来源提交及证据范围。PNG原始字节通过可折叠Base64资源块随书保存，独立还原程序严格解码并逐张核对SHA，正文仍使用`docs/images/`相对路径，不塞入data URI。二进制vendorZIP在Git中单独保存，书中包含重建这些ZIP的完整脚本、manifest与许可证，不把二进制伪装成可手写源码，也不要求已有ZIP作为学习前提。

手工学习创建顺序可照第7—13章；全部源码齐全后再执行全量测试。复现安装始终 `--locked`；依赖更新需提交真实新锁并重跑，不由AI随意修改锁内容。

## 18. 故障定位与通关清单

| 问题 | 正确处理 |
|---|---|
| ModuleNotFoundError | 回到含pyproject的根目录，uv sync --locked；使用包路径workbench，不要写不存在的from main |
| 超轮数/调用上限 | 检查.env是否设置了正数；默认0；改好重启并retry同一UUID |
| 智能推荐仍BLOCKED | 阅读真实unsupported/范围冲突；不为通过而删需求或修改权限 |
| 平台401 / 模型401 / 产品401 | 分别检查rnd token / API_KEY / 产品登录token，不混用 |
| 搜索筛选结果不对 | 核对Plan searchable/filterable/date_range、真实API与前端请求；先清除旧条件，检查日期格式 |
| 原生数据库非空 | 保留现场，不取消保护或自动DROP；使用新的明确授权空库 |
| 前端构建或类型失败 | 保留真实日志，不删页面、不跳过类型；按固定上游兼容适配核对 |
| 独立包只有后台通过 | --check必须前端启动后才成功，不能减少验收项掩盖错误 |
| 浏览器工作台显示KeyError | 错误包含源码位置；日期/枚举图表有回归测试，检查你是否使用同提交完整源码 |
| 手册不一致 | 修改正文源或代码后重新build_handbook，不手工只改生成文档或关闭测试 |

通关顺序：配置单模型 → 可选阶段覆盖验证 → 选择组合后新建 → 人工13+轮不丢数据 → 任意关卡智能推荐后无后续提问 → 客服三资源关联、角色、指派、流程、记录、提醒与统计 → 独立产品启动 → 原生环境及独立新库交付 → Windows/Linux/PG/浏览器CI → 整本手册一致。实际结果必须有对应提交的报告，不凭README一句“已通过”。

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

## 已有生成目录和数据库的保护

基础模板只在不存在的新目标目录中首次生成。已有目录只有在原 `generation.json` 的设计指纹、前端/数据库选择及文件清单有效且匹配时才可原样复用，交付前仍须单独验证源码。回执缺失、损坏或设计/选择不匹配时会停止，并保留全部原字节，包括 `.data/product.db`、`.env` 和你自行添加的源码；不会删除整个产品目录来“恢复成功”。先备份并核对原运行的真实回执和批准设计，不要手写一个成功回执或删除数据库绕过检查。新设计应在新的空目录/新运行中生成；若要把现有业务数据迁移到新结构，需要单独制定、备份并批准迁移方案。生成中断且没有有效回执时也保留现场，不承诺自动重建或自动迁移数据。
