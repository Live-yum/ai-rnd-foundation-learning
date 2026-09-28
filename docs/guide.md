# 从零实现 AI 研发平台：逐步实操手册

这份手册对应本仓库 Python 3.14 源码。本文的完整文件内容由源码生成；测试会重新核对每一个文件，避免出现“文字让你调用一个并不存在的函数”。正文末尾包含所有代码、测试、配置、迁移和实际依赖锁。

## 1. 先启动体验，再按章节理解

### 1.1 安装工具

Windows 安装 Git 和 uv 后，重新打开 PowerShell。安装 uv 使用其官方安装器：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
git --version
uv --version
```

平台初始不要求 Docker、PostgreSQL、Redis、Java、Node。原生 FastapiAdmin / 芋道模板有独立的运行前提，见第 12 章；不要把平台 SQLite 与模板数据库混在一起。

### 1.2 取得本次实现

PR 尚未合并时：

```powershell
cd D:\Code
git clone --branch feat/python314-workbench https://github.com/Live-yum/ai-rnd-foundation-learning.git
cd ai-rnd-foundation-learning
uv python install 3.14
uv sync --locked
uv run rnd init
```

如果已经克隆，在现有仓库执行 `git status` 确认没有尚未保存的修改，再切换这个分支。不要删除你的数据、覆盖其他学习目录或使用 `git reset --hard` 排错。PR 合并后可以使用 main。

`uv sync --locked` 创建本项目 `.venv`，使用已经提交的真实锁文件，不会临时选择其他版本。统一执行 `uv run ...`，不需要手动激活 Conda 或 venv。确认解释器：

```powershell
uv run python -c "import sys; print(sys.executable); print(sys.version)"
```

必须是 Python **3.14.x**。本项目不需要降级到 3.12。

### 1.3 填写模型配置

`rnd init` 只在缺少文件时复制 `.env.example`，自动升级本地数据库并生成访问令牌，不覆盖已有配置。

用 VS Code 打开根目录的 `.env`，填写：

```dotenv
BASE_URL=https://你的供应商兼容接口地址/v1
API_KEY=你的真实密钥
MODE=供应商提供的模型名称
```

`MODE` 是**模型名称**，不是 dev / prod，也不是“推理模式”；兼容别名 `MODEL`。`BASE_URL` 是 API 根地址，程序在后面拼接 `/chat/completions`，不要再次填入这个后缀。只支持返回 Chat Completions `choices[0].message.content` 格式的接口；不是网页聊天地址，也不自动适配仅提供其他协议的供应商。本地模型可以使用 loopback HTTP；远端必须 HTTPS。本地服务要求非空 API_KEY，可填写其规定的占位值。

不要把 `.env`、`.data/access-token`、数据库或者模型请求内容发到公开 PR。`.gitignore` 默认排除它们。

### 1.4 启动与交互

终端 A：

```powershell
uv run rnd doctor
uv run rnd start
```

终端 B，**也在仓库根目录**：

```powershell
uv run rnd chat
```

输入项目名称和需求，例如：

> 做一个个人任务管理后端，每个注册用户只看自己的任务。任务有必填标题、整数优先级、是否完成，支持增删改查。不需要共享、审批、附件和外部集成。

程序通过真实模型澄清需求。看完每一道关卡展示的内容后，输入 `批准`、`拒绝` 或具体修改意见。必须分别批准**需求、设计、交付**，不会替你默认批准。标准 CRUD 的生成、测试、索引、打包不调用模型。

服务运行时，浏览器可打开 `http://127.0.0.1:8000/docs`。执行 `uv run rnd token`，把令牌填入 Swagger 的 Authorize；这是平台本机操作令牌，不是 API_KEY。HTTP 修改接口还需要独立的 `Idempotency-Key`，一次业务提交使用一个 UUID，网络重试用原值，不同请求不能共用同一个键。CLI 会处理常规请求键。

流程结束显示运行 ID。下载：

```powershell
uv run rnd download 这里替换为运行ID
```

输出 `deliveries/<运行ID>.zip`。保留原 ID 可查询：

```powershell
uv run rnd show 这里替换为运行ID
uv run rnd chat --run 这里替换为运行ID
```

停止聊天终端不会抹掉运行。停止服务用 Ctrl+C，再次 `rnd start` 后恢复。当前是本机单操作人版本，不是可公开部署的多租户平台。

### 1.5 运行交付产品

把 ZIP 解压到一个**新目录**。进入含 `manage.py`、`pyproject.toml` 的目录：

```powershell
uv sync --locked
uv run python manage.py init
uv run python verify.py
uv run python manage.py serve --port 8001
```

产品不再需要平台源码、模型 Key 或平台访问令牌。产品 Swagger 位于 `http://127.0.0.1:8001/docs`。先 `/auth/register` 注册账号，再 `/auth/login`，将返回的 `access_token` 填入产品 Authorize。产品每个用户只能操作自己的记录。示例登录账号由你自行创建，不内置生产管理员密码。

平台和产品是两套独立数据库/令牌；不要把平台的 access-token 当产品用户令牌。

**本章通关：** 实际模型能够澄清 → 三次人工决定 → 状态 READY → 下载 → 在新目录启动产品。模型质量和外网依赖下载仍取决于你的供应商和网络；HTTP 401/429/超时不会自动切换成假模型。

## 2. 能力范围与流程图

默认 `python-basic` 完整闭环：注册/登录，逐用户数据隔离，text/integer/boolean 类型 CRUD，独立进程 HTTP 验收，进程重启数据保持，ZIP 干净解压再验收。可选字段验证由受限规则编码器实现，最多两轮修复。**不支持**关系表、共享业务数据、企业角色权限、付款、跨表事务、文件上传和任意 Python 包安装。

FastapiAdmin、Yudao+Vben 通道使用锁定的真实上游源码与其 HTTP 原生生成器。当前输出为 **SOURCE_READY**：原生生成文件与上游源码一起交付，但不自动挂载所有路由、菜单、迁移，也没有通过完整原生应用运行验收。因此不能叫它们“完整产品 READY”。选择原生模板会在设计和交付时标注等级，不能静默退回基础模板。

```text
创建项目/运行 → 真实需求澄清 → 等待需求批准
    → 结构化设计与任务/图表 → 等待设计批准
    → 确定性生成 → 必要时编写受限规则 → 独立验证
       → 失败且可修复：最多两轮 → 再验证
    → ZIP + 独立目录复验 → 等待交付批准 → READY
原生模板：原生生成器导出 → 源码验证 → 交付批准 → SOURCE_READY
拒绝 → REJECTED；真实错误/超限/条件未满足 → FAILED
```

这是有限任务的软件工厂，不是能自行实现任意软件的无限自主 Agent。模型不拥有宿主机 shell，生成的规则不通过 Python `exec` 或 import 执行。

## 3. 从空目录逐个创建，而不是覆盖已有项目

第 1 章是体验路径；以下是学习路径。另建空目录，不在同一目录再次 `uv init`：

```powershell
mkdir D:\Code\rnd-rebuild
cd D:\Code\rnd-rebuild
uv python install 3.14
uv init --bare --no-package --no-workspace --python 3.14
uv python pin 3.14
```

在 VS Code 选择“打开文件夹”。按本章后面的源码清单，逐个右键“新建文件”，复制该文件的**完整代码块**。路径如 `workbench/settings.py` 表示先创建 `workbench` 文件夹，再创建 `settings.py`。保存为 UTF-8；确认不是 `settings.py.txt`。

先创建配置组：`.python-version`、`pyproject.toml`、`uv.lock`、`README.md`、`.gitignore`、`.gitattributes`、`.env.example`、`workbench/__init__.py`。README.md 是 pyproject 声明的构建输入，不能漏建。覆盖 `uv init` 的最小 pyproject 为本手册对应版本，再执行 `uv sync --locked`。`uv.lock` 是实际解析结果，不手工删依赖或凭空编版本。完整锁较长，在源码附录单独列出。

本仓库采用安装式包 `workbench`，入口为 `rnd = workbench.cli:app`。不再有 `from main import app`、`from settings import ...` 这种扁平导入。每个 import 与实际包路径一致，不需要手工编辑 sys.path。

各章按职责解释代码，实际创建与运行测试的先后顺序以第18章为准。每组测试必须在该组及其前置组的文件齐全后运行；不要提前复制尚未实现模块的测试。源码附录按职责列出最终一致版本；单个文件创建后先执行语法检查，相关依赖组齐全再运行该组测试：

```powershell
uv run python -m compileall -q workbench
```

手册末尾可选重建工具能把附录还原到新的空目录，只还原文件，不执行源码，也不替你确认需求。学习时仍推荐逐组阅读。

## 4. 配置与数据库

创建 `workbench/settings.py`、`workbench/domain.py`、`workbench/store.py`、`alembic.ini`、迁移目录内的三个文件。

| 文件 | 用途与连接 |
|---|---|
| settings.py | 以自身位置定位仓库根和 `.data`；读取 `.env`；不根据终端工作目录猜数据库位置 |
| domain.py | Pydantic 输入/模型输出契约；拒绝未知字段、越界名称、字符串伪装的批准值 |
| store.py | SQLAlchemy 模型、事务与数据访问；建立连接工厂；每次短事务独立 Session |
| migrations/env.py | Alembic 接入 Base.metadata；接收 Store 提供的连接 |
| 0001_initial_control_plane_schema.py | 冻结的初始迁移；不依赖未来会变化的模型定义来修改旧版本 |

SQLite 位于 `.data/workbench.db`。数据库记录 projects、runs、messages、jobs、requests、revisions、approvals、steps、events。LangGraph 断点保存在另一份 `.data/checkpoints.db`。源码/ZIP/日志是文件，数据库保存归属、状态和回执。

SQLite 开启外键、busy timeout 和 WAL，Python 3.14 显式使用非 legacy 的事务设置。WAL 仍只有一个写者，不支持无上限并发。数据库放本地磁盘，不放网盘同步目录。测试使用 tmp_path，不污染你的真实数据库。

时间字段保存明确带 UTC 偏移的 ISO 字符串，避免 SQLite ORM datetime 读回后丢时区。消息 role 只由平台设置，HTTP 请求没有 role 参数。

添加 `tests/conftest.py`、`tests/test_contracts.py`、`tests/test_store.py` 后：

```powershell
uv run pytest tests/test_contracts.py tests/test_store.py -q
```

测试覆盖输入、持久化、真实外键、事务回滚、并发重复请求、模型预算。不要为了通过测试而改成 SQLite 内存假替身。

首次安装使用已提交的冻结迁移，不再次生成 0001：

```powershell
uv run alembic upgrade head
uv run alembic current
uv run alembic check
```

以后修改模型才执行 `uv run alembic revision --autogenerate -m "具体变更"`，打开新文件审查，再 upgrade。重命名字段、数据搬迁不能盲信自动生成。**任何阶段都不要求删除现有数据库才能继续。**

## 5. 幂等、审批与短事务

Store.create_run 在同一事务保存运行、首条用户消息、待执行 job；不会“需求保存成功，但任务完全没入队”。Request 表记录请求指纹与响应：重复相同请求返回原结果；同一个键对应不同内容返回409。

Revision 的 gate_id 由 run、阶段、轮次、内容摘要生成。审批必须绑定当前 gate_id，而且 approved 必须是真布尔值。通过 API 写入 Approval 后，LangGraph 恢复仍会再次检查这条记录。模型文本“我批准了”无效。

SQLite API 修改由文件锁串行化，PostgreSQL 同时使用事务 advisory lock。外部模型/工具调用不放在数据库事务中。对已完成的工具操作保存 Step 回执，恢复时可复用。**这不是跨数据库/网络的“恰好一次”承诺**：进程在模型返回而回执尚未写入时退出，重试仍可能再次调用模型；调用预算预先记账，限制损失。

通关：重复创建只出现一个项目；旧 gate409；无 Approval 记录无法从图层绕过；字符串 `"true"` 被422拒绝。

## 6. 文件安全与真实代码生成

创建 `workbench/filesystem.py`、`workbench/tools.py`、`workbench/generator.py`，以及 `templates/product/` 全部文件。

filesystem 统一执行相对路径、链接、ZIP 限制、密钥排除、原子写入和 SHA-256。不能从 API 接收任意系统路径。tools 只运行平台固定参数数组，shell=False；复制子进程环境时排除 API_KEY、BASE_URL、MODE 和原生服务令牌，超时终止进程组。

模板包含真实 FastAPI CRUD、SQLAlchemy schema、独立迁移启动器、注册登录和验收脚本。generator 只把已批准的 Plan 转成冻结迁移和元数据，并复制经审查的模板；不向 LLM 请求“写一套 CRUD”。生成环境仍是独立项目：自己的 pyproject、uv.lock、SQLite、README。

平台环境与生成产品环境分离，因此附录同时给出 `uv.lock` 与 `templates/product/uv.lock`。不要把平台数据库、模型 Key 或完整工作环境复制进产品。

## 7. 受限规则编码，不开放任意宿主代码执行

创建 `workbench/rules.py` 和 `workbench/coding.py`。

当设计存在 custom_rules 时，模型只能返回一个 SHA 前置条件补丁：`custom_rules.py`。内容只能是 `validate(entity, data)` 中的条件判断、布尔比较、data.get、len、raise ValueError、return None。所有规则先解析 AST；不允许 import、赋值、循环、任意属性/调用、文件/网络操作。执行由平台自己的小解释器完成，**不会 eval/exec 模型代码**。

这适合“优先级不得小于0”“满足某个条件时字段必填”等逐记录校验。复杂事务、调用第三方服务、任意 Python Agent Server 不属于当前默认能力，遇到这类需求必须阻塞并重新确认范围。

补丁的 before_sha256 不匹配就拒绝；已经应用的相同补丁可安全重放。AI 不能修改原生运行器、验证脚本、鉴权或依赖锁。设计中的正反例经过类型和字段校验，并在规则解释器及真实 HTTP 两层执行。

```powershell
uv run pytest tests/test_safety.py tests/test_tools_cli.py -q
```

通关：路径越界、ZIP重复路径、私钥、危险 AST、过期补丁均被拒绝；允许的业务校验真实生效。

## 8. 模型网关

创建 `workbench/llm.py`，然后 `tests/test_llm.py`。

ModelGateway 把 Pydantic JSON Schema 与明确任务一起送到兼容接口，完整校验响应。请求与响应有限长；401/403、404、429和超时有明确错误；结构错误最多重试一次；每次运行有 MAX_MODEL_CALLS 上限。失败不静默缩小需求或退回演示结果。

单元测试注入 httpx.MockTransport，明确不消耗用户模型费用。`rnd start` 没有测试模型模式，只使用 `.env` 的真实接口。CI 全绿证明程序与协议处理经过测试，不能证明任意供应商模型的回答质量。

```powershell
uv run pytest tests/test_llm.py -q
```

通关：合法响应通过、错误 JSON 停止、鉴权错误不泄漏 Key、相同模型步骤已保存回执可复用。

## 9. 知识包和图表

创建 `workbench/knowledge.py`。

`build_index` 扫描源码、计算文件 SHA，使用 Python AST 收集类、函数、位置和 imports。未变文件复用已有索引；变化或删除后重建对应条目。知识包输出必须在源码目录外，以免把自己越索引越大。

```powershell
uv run rnd index workbench .data/platform-knowledge
```

输出 index.json、AGENTS.md、build-stats.json。第二次运行应能看到 reused 增加。`context_for` 在每次读取前对比当前源码摘要，旧索引失效时直接拒绝。只将目标文件与 approved-spec 送入编码步骤，不每次把全仓库送入模型。

设计阶段自动生成 tasks.json、approved-spec.json、design-er.mmd、architecture.mmd、diagram-source.json。Mermaid 是可版本控制的图源。ER/拓扑是设计图，注明来源规格摘要，不冒充线上数据库反射。

Repomix 和 Serena 可作为后续更复杂仓库的补充工具，并非当前运行的必要依赖；本实现不会假称已连接它们的远程 Agent。当前 Python 索引是真实可用的本地 AST 索引，Java/TS 提供文件地图，不冒充精确调用图。

## 10. LangGraph 与恢复

创建 `workbench/flow.py`、`workbench/runtime.py`。

Flow 中节点都是明确的普通函数：analyse、requirements、plan、design、generate、code、verify、repair、package、delivery。LLM 只参与需求、设计和必要的定制规则。State 只保存结构化状态、ID、摘要，不存 ZIP 和整仓库二进制。

interrupt 会在恢复时重入当前节点，因此 gate 写入必须幂等。审批在 Store 保存，图层再次验证。Runtime 使用 run UUID 作为 thread_id，恢复使用 Command(resume=...)，不接受用户任意更改 State。

API 默认内置一个 Worker。SQLite 用 worker.lock 保证单实例；PostgreSQL 加 session advisory lock 防止多主机重复 worker。启动后仅在拥有锁时回收 RUNNING 任务。每次 gate 消费记录 job_id：在“图已前进但 Store.finish 未执行”的崩溃窗口，重新领取相同 job 不会消费下一道审批。

```powershell
uv run pytest tests/test_workflow.py -q
```

包含完整闭环、需求修改、旧 gate、拒绝、checkpoint 重开、崩溃恢复、规则一次失败后修复、交付文件被篡改后的拒绝。

## 11. 独立验证、打包和发布

创建 `workbench/verification.py`。它调用**平台侧经审查的** product/verify.py，而不是相信产品内可以自行修改的测试脚本。

默认验收先 `uv sync --locked` 给产品建立独立 .venv，再启动真实 HTTP 服务：验证账号、登录、错误凭据、类型/必填约束、CRUD、两个用户的越权读改删、进程重启和数据保持。结构化正反例也经 HTTP 运行。

成功后比较所有源码 SHA，拒绝“测试完成之后代码又变了”。ZIP 使用稳定文件顺序与时间戳；在第二个新目录解压、核对清单、再次创建独立 .venv 并完整验收，最后才展示交付审批。审批后下载再验证 ZIP 哈希。

CI 快速测试为节省网络使用已安装的 Python3.14依赖（`install_products=False`，只在测试设置显式注入）；独立依赖验收 job 使用默认 True，分别新建产品环境和干净解压环境。两种证据不会混称。

```powershell
uv run python -m scripts.ci_clean_install
```

这条命令会下载/安装依赖，但不调用付费模型，使用显式的 CI 规格夹具。成功报告在 reports/clean-install.json，模型模式标为fixture。

## 12. 接入你指定的原生开源模板

### 12.1 源码版本与生成器

创建 `workbench/native.py` 和 `tests/test_native.py`。SOURCES 是白名单注册表；每个上游锁定 commit，而不是每次跟随 master：

- FastapiAdmin：`1cd12c726ad9032c17ef85ce805ce991be60fbdf`
- Yudao Cloud Mini master-jdk17：`47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be`
- Yudao Vben：`1b14e889f529e245fd620daa720dcea6de0cc5e7`

```powershell
uv run rnd native prepare fastapiadmin
uv run rnd native prepare yudao-vben
uv run rnd templates
```

Git clone/fetch 由固定命令执行；记录实际URL、SHA、dirty状态和知识包。芋道优先Gitee，失败可用官方GitHub对应仓库，但仍必须匹配同一个锁定SHA。上游源码目录不用于直接开发。

### 12.2 为什么原生模板还需要额外环境

平台 SQLite 不代表 Java/Spring/Redis 等依赖消失。运行原生服务器仍须按固定提交的 README/SKILL、pyproject、pom、package.json、env 示例准备环境。FastapiAdmin后端也使用uv；芋道后端保留Java17与Maven，前端保留其Node/pnpm，uv不管理Java或Node依赖。

生成器需访问与你配置一致的**专用开发数据库**，不能对线上库自动建表。适配器只允许绝对路径的 `*-codegen.db` SQLite 或本机以 `_codegen` 结尾的 PostgreSQL。默认 `allow_create_tables=false`，你明确改为true才创建本次运行前缀的业务表，不覆盖现有不同结构。

### 12.3 配置原生服务器接口

```powershell
uv run rnd native config-example fastapiadmin
```

打开 `.data/native/fastapiadmin.json`。字段说明：base_url 是已运行的本机FastapiAdmin服务；openapi_path 是该服务实际导出的OpenAPI路径；token_env/database_url_env是读取环境变量的名称，不是凭据本身。

在根 `.env` 追加：

```dotenv
NATIVE_FASTAPIADMIN_TOKEN=通过你自己部署的原生服务登录取得的管理员令牌
NATIVE_FASTAPIADMIN_DATABASE_URL=sqlite:///D:/Code/native-dev/fastapi-codegen.db
```

**这个数据库必须与原生生成器读取的数据库相同。** 不能只改平台环境变量、不改原生后端。核对后将原生JSON配置的allow_create_tables改为true。

芋道同理：

```powershell
uv run rnd native config-example yudao-vben
```

`.env` 示例：

```dotenv
NATIVE_YUDAO_TOKEN=你本机芋道管理员登录令牌
NATIVE_YUDAO_DATABASE_URL=postgresql+psycopg://开发账号:开发密码@127.0.0.1:5432/yudao_codegen
```

使用PostgreSQL时先 `uv sync --locked --extra postgres`。原生JSON内data_source_config_id必须对应原生服务中的实际数据源编号；tenant_id与你登录租户一致；front_type只允许40/41，与锁定的Vben5 Ant Design Vue前端匹配，不使用Vben2或ElementPlus的生成代码冒充。

程序从真实OpenAPI定位唯一的生成器操作，再调用导入、字段明细、更新、ZIP下载；未找到、缺权限、跳过部分表、字段不匹配都失败，不伪造输出。

### 12.4 执行原生导出

```powershell
uv run rnd chat --template fastapiadmin
uv run rnd chat --template yudao-vben
```

选择你已经准备好的那套，不要求两套同时运行。最终状态SOURCE_READY明确只代表源代码导出：包里 upstream/ 是锁定源码，generated/ 是原生生成器实际输出。先在新的开发分支检查目录映射、鉴权、菜单、初始化/迁移，再手动合入并执行原框架测试。**当前实现不自动完成这段原生挂载与完整运行认证，无法只凭三个模型参数启动芋道全栈。**

测试分级：test_native.py为HTTP协议mock测试和真实SQLite建表测试；Actions native-sources 为真实仓库克隆/索引验证；两者都不等于原生服务器完整验收。

## 13. API 与命令行入口

创建 `workbench/api.py`、`workbench/cli.py` 和 `tests/test_api.py`。

FastAPI lifespan 建立 Store、迁移、令牌和 Worker，关闭时等待当前任务完成再释放checkpoint连接。HTTPBearer保护所有项目、运行、消息、报告与下载；TrustedHost只允许本机主机名。公网多租户、账号计费和团队权限不是这个本地版本的功能。

| 接口 | 作用 |
|---|---|
| GET /health、/ready | 进程存活；数据库/内置Worker就绪 |
| POST /projects | 创建项目，Idempotency-Key必填 |
| POST /projects/{id}/runs | 保存原始需求并入队 |
| GET /runs/{id} | 状态、pending关卡、结果、错误 |
| POST /runs/{id}/resume | 回答/修改/明确批准或拒绝当前gate |
| POST /runs/{id}/retry | 修复外部条件后重试FAILED任务 |
| GET /runs/{id}/events | 按游标查看执行事件 |
| GET /runs/{id}/report | 查看生成/验证/交付回执 |
| GET /runs/{id}/download | 已批准的READY或SOURCE_READY才可下载 |
| GET /templates | 查询真实能力与准备状态 |

不直接提供接受任意shell、URL、文件路径或Python代码的HTTP接口。测试命令与模型规则都有固定边界。

## 14. GitHub Actions 验收

创建 `.github/workflows/test.yml`。CI没有用户模型Key也能运行，因为明确使用协议夹具；不是“真实账户验收已完成”。

CI任务包括：Linux/Windows Python3.14全套快速测试、PostgreSQL真实数据库与checkpoint恢复、产品独立依赖与干净解压HTTP验收、锁定原生源码克隆/索引、手册一致性和重建检查。日志和JUnit作为Actions artifacts上传。

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest -m "not postgres" -q
uv run python -m scripts.build_handbook --check
```

本地没有PostgreSQL时那组测试不运行；Actions postgres job必须设置TEST_DATABASE_URL并明确执行，不能因为缺配置skip了却声称PostgreSQL通过。TEST_DATABASE_URL只指向一次性测试库。

如果需要更新依赖：`uv lock` → `uv sync --locked` → 全部CI → 提交新的uv.lock；产品依赖变更同样在templates/product内更新并复验。锁文件不由模型编写。

## 15. 数据、备份、升级和恢复

`.data` 内有需求和可能敏感的业务文字，即使不是密钥也不应公开。备份前停止API/Worker，用SQLite backup API或在停止后复制完整数据库；不要只复制活动中的WAL主文件。恢复后保留同一平台版本与checkpoint库，避免业务审批表和图断点不一致。

API独立运行可用 `uv run rnd start --no-worker`，另一终端 `uv run rnd worker`；仍只允许一个worker。默认一条命令已经内置worker，不要重复启动。进程故障后Runtime会回收未完成job；代码版本更改导致图节点结构变化时不能假设旧checkpoint无限兼容，先保留旧环境完成/取消旧运行，备份后升级。

FAILED会明确显示原因。模型配额/地址或原生前置环境修正后 `uv run rnd retry ID`。预算耗尽/不支持需求应重新整理并新建运行，不能无限重试消费费用。不会把故障状态自动改READY。

## 16. PostgreSQL 可选路径

默认路径不需要本章。需要服务器数据库时：

```powershell
uv sync --locked --extra postgres
```

`.env`中配置 `DATABASE_URL=postgresql+psycopg://.../workbench`。平台业务迁移仍由Alembic执行，Runtime自动使用PostgresSaver，可用CHECKPOINT_URL指定另一库（必须配套备份）。只配置新URL不会自动把旧SQLite数据搬过去。

本实现支持**PostgreSQL空库初始化和后端/断点运行**，有Actions真实验证；**不包含已有SQLite业务历史的自动数据搬迁器**。现有数据迁移须停机备份、数据转换、主外键/行数核验、重建对应审批和checkpoint历史并回归，不能说“改一个URL就无损迁移”。当前即使换PG也坚持单Worker，不伪装成分布式队列。

## 17. 常见问题

**ModuleNotFoundError：** 确认在含pyproject.toml的仓库根执行，先`uv sync --locked`，再`uv run python -c "import workbench; print(workbench.__file__)"`。本手册没有根目录main.py，不再用旧的`from main import app`测试。

**实际Python仍是3.12/3.14不一致：** 查看`.python-version`及pyproject.requires-python，执行`uv python install 3.14`、`uv sync --locked`。Conda提示符不代表uv实际解释器，使用sys.executable核实；不要直接删除旧环境和业务数据。

**端口占用：** `.env`增加PORT=8010，两个终端均读取同一.env，重新启动；产品端口另行指定8001/其他空闲端口。

**401：** 平台401需要rnd token；模型401检查API_KEY；产品401需要/auth/login的access_token。这三种令牌不是同一个。

**模型404：** 检查BASE_URL是否已带/v1且未带/chat/completions，MODE是否是供应商认可的模型标识。

**模型反复问问题：** 检查需求是否超出模板支持、数据共享/权限是否未确认。不能为了让界面继续而清空unsupported。确实不需要的功能由你明确删除后重新确认。

**生成器能输出但没有产品：** 原生通道当前是SOURCE_READY，见第12章；不要把导出文件当已挂载的全栈应用。

**SQLite locked/Worker已存在：** 关闭重复运行的rnd start/rnd worker和长事务工具，保留一个。禁止以删除workbench.db解决。

**产品依赖下载失败：** 这是网络/环境故障，不触发AI修改业务代码。确认同一终端中uv可用、索引可达，再retry。整个验证环境不继承模型凭据和任意代理变量。

**修改代码后手册检查失败：** 执行`uv run python -m scripts.build_handbook`并一起提交源码与手册。不要删文档测试或关闭检查。

## 18. 每阶段的停止条件与源码顺序

| 顺序 | 本组新增文件（保留前组） | 本组验证 |
|---|---|---|
| 1 环境 | .python-version、pyproject.toml、uv.lock、README.md、.gitignore、.gitattributes、.env.example、workbench/__init__.py | uv sync --locked；uv run python -c "import workbench" |
| 2 数据与审批 | workbench/settings.py、domain.py、store.py；alembic.ini、migrations 全部文件；tests/conftest.py、test_contracts.py、test_store.py | uv run pytest tests/test_contracts.py tests/test_store.py -q；alembic upgrade head/current/check |
| 3 基础工具与模型协议 | workbench/filesystem.py、tools.py、rules.py、knowledge.py、llm.py；tests/test_llm.py | uv run pytest tests/test_llm.py -q；不调用真实模型 |
| 4 默认产品与受限编码 | templates/product 全部文件（包括其独立 uv.lock）；workbench/generator.py、coding.py、verification.py；tests/test_safety.py | uv run pytest tests/test_safety.py -q |
| 5 状态图 | workbench/native.py、flow.py、runtime.py；tests/test_workflow.py | uv run pytest tests/test_workflow.py -q；实际 SQLite/HTTP 验收，模型用显式夹具 |
| 6 HTTP与交互 | workbench/api.py、cli.py；tests/test_api.py、test_tools_cli.py | uv run pytest tests/test_api.py tests/test_tools_cli.py -q；rnd init；填写三项配置；rnd start 与 rnd chat |
| 7 独立安装与原生源码 | scripts/__init__.py、ci_clean_install.py、ci_native_sources.py；tests/test_native.py | test_native；python -m scripts.ci_clean_install；原生源码下载为可选扩展 |
| 8 发布一致性 | .github/workflows/test.yml；scripts/build_handbook.py、rebuild_from_handbook.py；docs/guide.md；其余全部 tests 文件 | 生成手册；Ruff；pytest -m "not postgres"；手册 --check；GitHub Actions |

表内未写全命令前缀的 Python/pytest/alembic 命令统一加 `uv run`，并始终在含 pyproject.toml 的根目录执行。第2组有独立测试把这些文件复制到新的空目录，并确认没有 API/runtime 文件也能运行该组测试。第4组必须先有第3组的 knowledge/rules；第5组必须先有第4组的 verification；不能按章节编号提前运行依赖尚未建立的测试。

每组代码从下方对应路径的完整代码块复制，文件不存在就逐个创建；不是把所有代码拼进一个 main.py。第8组才复制剩余测试，避免 pytest 在收集阶段导入尚未创建的模块。原生模板导出仍不等于完整原生运行认证，见第12章。

下面按职责给出文件完整内容。不出现“此处自行实现”或省略函数体；能力未实现的部分已在对应章节说明，不会用假success蒙混过关。

## 参考资料

这些链接是核对工具行为的官方来源；实际可复现版本以本仓库uv.lock和SOURCES内commit为准。

- uv项目管理与GitHub Actions： https://docs.astral.sh/uv/guides/projects/ 、 https://docs.astral.sh/uv/guides/integration/github/
- Python3.14 sqlite3事务： https://docs.python.org/3.14/library/sqlite3.html
- SQLAlchemy SQLite事务与外键： https://docs.sqlalchemy.org/en/20/dialects/sqlite.html
- Alembic候选迁移： https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- LangGraph中断与恢复： https://docs.langchain.com/oss/python/langgraph/interrupts
- Pydantic校验： https://docs.pydantic.dev/latest/concepts/models/
- FastapiAdmin： https://github.com/fastapiadmin/FastapiAdmin
- 芋道后端： https://gitee.com/yudaocode/yudao-cloud-mini
- 芋道Vben： https://gitee.com/yudaocode/yudao-ui-admin-vben
