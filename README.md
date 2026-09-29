# AI 研发工作台 · Python 3.14

从需求到可启动产品的本地工作台：**先选择后端、前端与数据库 → 描述需求 → 人工确认或一键智能推荐 → 原生/确定性生成 → 独立测试 → 可选模型审阅 → 打包下载**。

平台使用 Python、uv、FastAPI、SQLite 和 LangGraph。只有真实模型接口会产生模型费用；基础代码、迁移、索引、测试与打包由工具执行。测试失败不能由模型“宣布通过”。

## 1. 克隆并初始化

本功能 PR 合并前使用功能分支；合并后可以使用 main。

```powershell
cd D:\Code
git clone --branch feat/controlled-toolchain-integration https://github.com/Live-yum/ai-rnd-foundation-learning.git
cd ai-rnd-foundation-learning
uv python install 3.14
uv sync --locked
uv run rnd init
```

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

## 8. 从已合并的旧版本升级

先停止旧服务，备份整个 `.data/` 和自己的 `.env`；在已有仓库保存/提交本地代码改动后切换新PR分支并更新依赖：

```powershell
git fetch origin
git switch feat/controlled-toolchain-integration
uv sync --locked
uv run rnd init
```

`init` 不覆盖 `.env`。旧配置显式写了 `MAX_ROUNDS=10` 或 `MAX_MODEL_CALLS=16` 时，请改成0再重启。数据库迁移增加必要字段，不删除原记录。针对“超轮数”运行，修正配置后可 `uv run rnd retry UUID`，随后 `uv run rnd chat --run UUID` 或 `uv run rnd recommend UUID`。已有运行的模板选择被保留；更换技术栈应新建运行，不能覆盖已经生成的数据。

## 9. 测试、证据、手册

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest -m "not postgres" -q
uv run python -m scripts.build_handbook --check
```

Actions 覆盖Windows/Linux、真实PostgreSQL、独立产品安装、原生新数据库交付、真实Chromium智能推荐和资讯页面搜索筛选。CI模型采用显式协议夹具，不消耗真实Key，也不声称已验证你的供应商账号。

详细从零实现手册：**`从零实现AI研发平台_逐步实操手册_完整版.md`**。兼容旧链接的 `_v3.md` 与它逐字一致。正文、完整代码、数据库迁移、前端、测试、CI、锁文件一起生成；修改代码后执行 `uv run python -m scripts.build_handbook`。模板ZIP二进制不嵌入Markdown，但已随普通clone包含，附录给出哈希、来源和许可证。

当前是仅监听本机、单操作人和单Worker的研发工作台。没有公网生产身份体系。请勿公开 `.env`、`.data`、`.deployment` 或访问令牌。更多环境条件、SQL步骤、预算恢复、原生部署与故障定位见完整手册。

## 代码上下文、Aider、Continue 与 Daytona

实际流程新增“需求确认 → 模板源码索引/检索/仓库地图 → 规划”，以及“本机验收 → 可选 Daytona 附加验收 → 原有打包/干净解压复验”。CRUD、迁移和菜单仍优先用现有确定性/原生生成器，不交给 LLM 重写。

默认安装即包含 Java/TS/Vue Tree-sitter 解析与本地 SQLite FTS5 检索，不需要新账户：

```bash
uv run rnd index templates/product .data/examples/product-index
uv run rnd tools search templates/product .data/examples/product-index "validate"
uv run rnd tools continue-config . templates/product .data/examples/product-index
```

最后一条为 Continue 创建 `.continue/mcpServers/rnd.json`，只读查询与仓库地图通过真实 MCP 协议访问同一索引；没有复制或冒充 Continue 的私有索引引擎。Continue 上游已宣布停止主动维护，本平台不依赖其私有索引内部实现；客户端兼容性与维护边界见工具链章节。配置已存在时拒绝覆盖。索引结果含路径、行号和 SHA，源码变化先重建，默认不上传向量。

Aider 是可选独立工具环境，**平台仍是 Python 3.14**：

```bash
uv sync --locked --project tools/aider --python 3.12
```

设置 `.env` 的 `REPO_MAP_PROVIDER=aider` 使用真实 Repo Map；`CODING_ENGINE=aider` 使用真实 SEARCH/REPLACE 应用引擎。模型调用仍走平台安全的多模型配置和预算，Aider 不接收真实 Key。当前自动编辑只开放已批准的 Python 业务规则文件；不声称任意 Java/Vue 业务已经自动适配。前后文件哈希、diff、Git commit 和验证回执均保留。

Daytona 默认 `SANDBOX_PROVIDER=local`（关闭）。启用需 `uv sync --locked --extra daytona`，独立 Daytona Key、已审核快照以及 `DAYTONA_ALLOW_UPLOAD=true`；会上传产品源码并可能产生账户费用。Python/SQLite 远程执行真实运行检查；原生通道是额外构建检查，不能替代现有数据库/浏览器/新库恢复。任何远程检查或清理失败都阻止交付，不偷偷回退到“成功”。云端 smoke 仅在 main 分支显式授权后手动运行，不在普通 PR 中读取云密钥。

工具失败时，网页运行报告可查看 `tool-failure.json`（退出码、超时、有限且脱敏的输出）；上下文回执和 Daytona 回执也可从报告读取。修复工具后重试同一 run，不要删除 `.data` 或重新创建项目。

完整安装、可选向量及独立密钥、Continue Agent 配置、Daytona 快照要求、失败处理和从零实现步骤见 [工具链实操章节](docs/toolchain.md)，也已纳入两份完整手册的正文及完整源码附录。凭据未提供时只可声明 SDK 契约测试，不可声明你的 Daytona 账户已经通过真实云验收。
