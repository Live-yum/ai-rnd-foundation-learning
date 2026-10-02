# README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L259。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18553`。本段原文以LF换行结束。

<!-- learning-source: {"path": "README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cb6b5a9b33b800125e032675e9186eaa69ece97dbdb2351472625112d7453b95"} -->
````markdown
<!-- README.md -->
# AI 研发工作台 · Python 3.14

**标准主线：从空目录实现并生成完整的内部客户服务管理系统。**

从需求到可启动产品的本地工作台：**先选择后端、前端与数据库 → 描述需求 → 人工确认或一键智能推荐 → 原生/确定性生成 → 独立测试 → 可选模型审阅 → 打包下载**。

平台使用 Python、uv、FastAPI、SQLite 和 LangGraph。**仅聊天大模型允许使用外部推理服务；其余工具均为本机运行。** 基础代码、迁移、索引、测试与打包由工具执行。测试失败不能由模型“宣布通过”。

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

普通细节给推荐默认值；每轮最多要求模型提出两个阻塞问题，已经明确的事实随结构化需求保存。客服的站内提醒、角色范围、统计口径及字段命名以三份需求文本为准；字段、枚举与日期范围经过合同校验，用户明确指定优先。

`批准`、`“批准”` 等控制指令不会被当作需求文本再次发送给模型。不满足批准条件时保持原等待点，提示回答或智能推荐，不消耗一轮。

## 6. “智能推荐”是持续委托，不是再问一次

页面任意非终态均可点击 **智能推荐**，或在新建时选择智能推荐；CLI 可输入 `智能推荐`，或者：

```powershell
uv run rnd recommend 运行UUID
uv run rnd chat --smart
```

这是你授权：**从现在起，剩余不明确细节按 AI 推荐补齐；后续需求/设计/交付不再逐项询问。** 它保留你已明确的要求，记录推荐与 `delegated-ai` 决定。可以随时点“恢复人工确认”或执行 `uv run rnd manual UUID`，在后续关卡恢复人工模式。

智能推荐不允许跳过独立测试、覆盖生产库、伪造成功或删掉你明确要求的功能。确实超出模板能力时明确 `BLOCKED`，不会再次陷入无限提问，也不会偷偷生成缩水产品。

本仓库的标准端到端示例是**内部客户服务管理系统**，从空目录教材、需求、计划、生成、测试到独立部署都围绕同一案例：

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
uv run ruff check .
uv run ruff format --check .
uv run pytest -m "not postgres" -q
uv run python -m scripts.build_handbook --check
uv run python -m scripts.build_learning_docs --check
```

Actions 覆盖Windows/Linux、真实PostgreSQL、独立产品安装、原生新数据库交付、真实Chromium智能推荐与产品页面回归，并由客服矩阵验证三角色、关系、流程、提醒和统计。CI模型采用显式协议夹具，不消耗真实Key，也不声称已验证你的供应商账号。

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

仓库只保留`从零实现AI研发平台_逐步实操手册_完整版.md`这一份完整教材，不提供版本差异补丁式教程。源码块带SHA，逐文件讲解与源码同步，标准库重建脚本可只从文档建立全部自有文件：

```powershell
uv run python -m scripts.build_handbook
uv run python -m scripts.build_handbook --check
uv run python -m scripts.ci_handbook
```

真实模型联调需要你自己的大模型配置。CI使用显式模型协议夹具；真实CLI、数据库、浏览器、本机服务测试的证据分别保存，不把SDK模拟响应当成本机完整部署成功。

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

真实模型的手动入口和证据解释见`docs/real-model-acceptance.md`。当前客服分支运行`.github/workflows/native-probe.yml`时选择`feat/customer-service-acceptance`，明确设置`real_model=true`，`expected_sha`填写已审查的完整40位提交SHA。`rnd`环境的`APK_KEY`仅在模型调用步骤映射成`API_KEY`，不打印或复制到源码；三个模板分别执行smoke与完整客服交付，任何一行未完成都仍是未验证。
````
