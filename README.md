# AI 研发工作台 · Python 3.14

从需求到可启动产品的本地工作台：**先选择后端、前端与数据库 → 描述需求 → 人工确认或一键智能推荐 → 原生/确定性生成 → 独立测试 → 可选模型审阅 → 打包下载**。

平台使用 Python、uv、FastAPI、SQLite 和 LangGraph。**仅聊天大模型允许使用外部推理服务；其余工具均为本机运行。** 基础代码、迁移、索引、测试与打包由工具执行。测试失败不能由模型“宣布通过”。

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

**从零学习不需要先取得这些源码。** 唯一教材`从零实现AI研发平台_逐步实操手册_完整版.md`从空文件夹讲解每个自有文件、调用关系和逻辑，包含所有文本源码及锁文件；书中给出的脚本可从固定第三方提交生成原生模板ZIP。没有本项目骨架也能照书实现。

需要先安装 Git、uv。Windows 的 uv 官方安装器：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

`rnd init` 创建本地数据库和访问令牌，不覆盖已有 `.env` 或删除数据，并从仓库内的 `templates/vendor/` 解压 FastapiAdmin、芋道后端与 Vben 源码。**普通 git clone 已包含模板代码快照，不用再 clone 上游仓库、初始化 submodule 或下载 LFS 文件。** 源码压缩包、许可证、固定 commit 和 SHA-256 清单一起提交。安装第三方依赖、下载浏览器等仍需网络；包含源码不等于完全离线运行。

## 2. 单模型配置：只填三项

编辑仓库根 `.env`：

```dotenv
BASE_URL=https://你的兼容服务/v1
API_KEY=你的密钥
MODE=你的模型名称
```

`MODE` 是模型 ID，也兼容 `MODEL` 别名；不是运行模式。`BASE_URL` 是 Chat Completions API 根地址，不包含 `/chat/completions` 后缀。只支持兼容该协议的服务。远端必须 HTTPS，本机模型服务可以使用回环 HTTP。不要上传 `.env` 或分享密钥。

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

将本机访问令牌填入页面。它不是模型 API_KEY，也不是生成产品的用户登录令牌。先选模板、兼容前端和数据库，点“确认选择”，之后才显示项目名称与需求表单。

也可以只用 CLI：

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

界面只允许已适配的组合，不任意混接一个框架的前端和另一个框架的鉴权 API。**所选数据库是交付产品的数据库；平台控制库仍可用 SQLite。** 完整原生环境准备见手册第二部分。

## 5. 不再被澄清轮数卡死

默认 `MAX_ROUNDS=0`、`MAX_MODEL_CALLS=0`：没有累计人工会话轮数或模型调用数量上限。HTTP重试与自动代码修复仍有限，避免单次故障无限调用。按需设正整数限制预算，达到后为 `PAUSED_LIMIT`，保留原回答与断点，不要求新建项目。

普通细节给推荐默认值；每轮最多要求模型提出两个阻塞问题，已经明确的事实随结构化需求保存。默认标题250字、正文3000字、日期YYYY-MM-DD、区间含两端、分类可选，用户指定优先。

`批准`、`“批准”` 等控制指令不会被当作需求文本再次发送给模型。不满足批准条件时保持原等待点，提示回答或智能推荐，不消耗一轮。

## 6. “智能推荐”是持续委托，不是再问一次

页面任意非终态均可点击 **智能推荐**，或在新建时选择智能推荐；CLI 可输入 `智能推荐`，或者：

```powershell
uv run rnd recommend 运行UUID
uv run rnd chat --smart
```

这是你授权：**从现在起，剩余不明确细节按 AI 推荐补齐；后续需求/设计/交付不再逐项询问。** 它保留你已明确的要求，记录推荐与 `delegated-ai` 决定。可以随时点“恢复人工确认”或执行 `uv run rnd manual UUID`，在后续关卡恢复人工模式。

智能推荐不允许跳过独立测试、覆盖生产库、伪造成功或删掉你明确要求的功能。确实超出模板能力时明确 `BLOCKED`，不会再次陷入无限提问，也不会偷偷生成缩水产品。

建议首次验证用真实示例：

> 个人泰拉瑞亚资讯助手。手动录入，标题250字、正文3000字、发布日期必填且为YYYY-MM-DD。分类可选，只有资讯/攻略/大神。支持标题和正文搜索、分类和单日筛选、包含起止日的日期区间。数据按用户隔离。

选择 `python-basic + simple-admin + SQLite`。这些能力已实现，不再反复将搜索、筛选或日期说成“不支持”。

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

- 默认产品：自动安装产品自身锁定依赖、执行Alembic迁移、启动；轻量界面在 `http://127.0.0.1:8001/`，API文档在 `/docs`。先注册自己的产品账号。SQLite无需外部服务。
- 默认产品选PostgreSQL：启动器使用该产品独立Docker Compose、随机密码、回环端口和持久卷；或显式提供 `PRODUCT_DATABASE_URL`。
- 原生产品：包含原生源码、独立启动器、原生种子、业务DDL和菜单SQL。在Linux/WSL准备其语言工具和Docker后，同一启动命令自动初始化**新的独立数据库**并启动前后端；无需原研发平台、模型Key或原开发数据库。可用本机专用空库 `NATIVE_DELIVERY_DATABASE_URL` 和Redis替代Docker。浏览器地址由启动器打印。

源码包含初始化/迁移语句，不包含用户实际业务数据。重复启动不重置记录或密码。原生 `--check` 会完整验证数据库、菜单、CRUD和前端启动后退出；`--skip-build` 仅用于之前已成功构建的同一产品。不要删除数据库排错，不把源码包当作用户数据备份。

## 8. 测试、证据、手册

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest -m "not postgres" -q
uv run python -m scripts.build_handbook --check
```

Actions 覆盖Windows/Linux、真实PostgreSQL、独立产品安装、原生新数据库交付、真实Chromium智能推荐和资讯页面搜索筛选。CI模型采用显式协议夹具，不消耗真实Key，也不声称已验证你的供应商账号。

详细从零实现手册：**`从零实现AI研发平台_逐步实操手册_完整版.md`**。从空目录创建文件、数据流讲解、完整代码、数据库迁移、前端、测试、CI与锁文件均包含在同一份教材。第三方模板不是自行编写的代码：教材提供固定提交和打包脚本，读者可以从公开上游重建三个归档，不需要先取得本仓库骨架。演示仓库附带这些归档以便直接体验；源码附录逐文件讲解职责与对应关系。

当前是仅监听本机、单操作人和单Worker的研发工作台。没有公网生产身份体系。请勿公开 `.env`、`.data`、`.deployment` 或访问令牌。更多环境条件、SQL步骤、预算恢复、原生部署与故障定位见完整手册。

## 9. 本机工具链与唯一完整教材

默认使用本机Tree-sitter/Python AST、FTS5和符号Repo Map。Aider使用独立Python3.12环境：

```powershell
uv sync --locked --project tools/aider --python 3.12
uv run rnd index workbench .data/platform-index
uv run rnd tools search workbench .data/platform-index "model_for"
uv run rnd tools continue-config . workbench .data/platform-index
```

设置`CODING_ENGINE=aider`和`REPO_MAP_PROVIDER=aider`可启用实际本机编辑/Repo Map。真实模型Key只交给平台网关，Aider不取得它。Continue仅通过本机stdio MCP访问只读search_code/repository_map，本平台不依赖其云服务。

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

本机随机凭据及平台配置保存在`.data/daytona-local`，不得提交Git。完整教材第20章解释Dex、API、Runner、镜像摘要、离线快照、每一步预期结果和清理。默认Python/SQLite快照不冒充Java/Vue通用镜像；原生完整验收仍在本机进行。Daytona上游Compose仅供开发，privileged Runner不是生产强隔离保证。

仓库只保留`从零实现AI研发平台_逐步实操手册_完整版.md`这一份完整教材，不提供版本差异补丁式教程。源码块带SHA，逐文件讲解与源码同步，标准库重建脚本可只从文档建立全部自有文件：

```powershell
uv run python -m scripts.build_handbook
uv run python -m scripts.build_handbook --check
uv run python -m scripts.ci_handbook
```

真实模型联调需要你自己的大模型配置。CI使用显式模型协议夹具；真实CLI、数据库、浏览器、本机服务测试的证据分别保存，不把SDK模拟响应当成本机完整部署成功。

### 本机Daytona的安装边界

Daytona固定v0.190.0；API/Proxy从固定SHA在本机Docker构建，Runner使用同版本、固定SHA256的发布文件。服务运行在本机internal网络，端口仅绑定回环，SDK也禁止非回环连接；不申请Daytona云账号。完整安装顺序为`prepare → images → snapshot-image → up → auth → snapshot → ci_daytona_local`，每一步的完整代码、用途、预期结果及失败处理见唯一手册第20章。此安装通道使用Linux x86_64或Windows x86_64 WSL2；默认平台与普通本机验收不要求安装Daytona。安装时下载公开依赖，不等于把生成代码交给云端运行。
