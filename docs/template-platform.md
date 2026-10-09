# 从零实现可批量定制的模板研发平台

本指南的目标是：**使用 LangChain 产生可校验的需求与设计，使用 LangGraph 管理执行与恢复，从稳定的前后端模板生成不同业务，并用独立测试证明交付可以运行。** 新业务优先增加需求、声明式设计和验收数据；只有模板能力确实不足时才增加受控代码扩展。

## 1. 先认清三个不同的对象

| 对象 | 解决什么问题 | 对应位置 |
|---|---|---|
| 技术模板 | 选后端、前端、数据库、已有能力与代码规范 | `workbench/template_adapters.py`、`templates/standards/` |
| 业务需求 | 定义这个项目的角色、数据、操作、流程与验收 | `examples/acceptance/*/requirement.md` |
| 一次运行 | 保存本次输入、批准版本、步骤、模型调用、产物与验证结果 | `Store`、`Runtime`、LangGraph checkpoint |

阅读书架与采购协作可以使用同一技术模板。给书架复制一份专用生成器，再给采购复制另一份，会让平台很快膨胀。这里的公共执行路径是相同的；业务差异放入 `Requirement`、`Plan`、`BusinessSpec` 和场景验收中。

批量指一次提交多个独立项目，随后由现有持久 Worker 依次处理。每个项目有自己的运行 ID、原始需求、模型预算、审批和交付文件。当前没有分布式并行调度；不要把一次提交十个任务解释成十个任务同时执行。

## 2. 从空目录学习的顺序

完整可还原教材入口是 [learning-docs/README.md](../learning-docs/README.md)。保留整个 `learning-docs` 目录，即可按其中的 `rebuild.py` 从空目录还原自有源码。第三方模板仍按固定版本和许可证取回，依赖与浏览器需要安装。

建议按下表实现最小主线，再展开原生栈和可选工具。右侧是本轮新增能力对应的代码入口，配合教材中连续、带文件路径的源码页阅读。

| 顺序 | 要实现的能力 | 本轮重点入口 | 完成标准 |
|---|---|---|---|
| 1 | 类型与模板选择 | `domain.RunInput/BatchInput`、`catalog.Selection` | 空需求、错误模板组合和超过十项的批次被拒绝 |
| 2 | 数据持久化 | `Store.request/create_run/create_batch` | 重复请求不重复建项目，事务失败整批回滚 |
| 3 | 模型调用 | `ModelGateway`、`model_protocol.structured_model` | LangChain 输出经过 Pydantic 校验，失败可诊断，没有假响应回退 |
| 4 | 模板能力与编码约束 | `TemplateAdapter`、`template_standards.py` | 目录、模型上下文与产物采用同一规范及哈希 |
| 5 | 产品生成与验证 | `generator.py`、`verification.py` | 从声明生成认证、数据、API、界面，并执行独立校验 |
| 6 | 执行与恢复 | `Workflow.compile`、`Runtime.tick` | 图状态按 run ID 持久化，审批绑定当前 gate，失败保留原运行 |
| 7 | 操作台 | `api.py`、`ui/src/state.ts`、Vue 组件 | 用户能提交批次、看到每项真实状态、处理等待与失败、下载交付 |
| 8 | 跨场景验收 | `scripts/ci_template_projects.py` 与案例目录 | 三个真实模型项目全部完成独立验收 |

实现需求到设计的流程时，先用 `analysis_source_conflicts` 检查明确约束的来源一致性，用 `business_analysis_conflicts` 检查已识别业务事实的表达与范围；发现问题即回到 `clarification`，保留原始输入和 requirement ledger，并沿用原有分析修复预算。分析通过后，设计阶段再检查 `Plan` 是否覆盖已批准需求。旧批准事实继续由同一套基于用户明确修改来源的授权机制保护，不能借修复自动删除已批准事实或改动已确认的数据范围。

不要在数据库事务中调用模型或等待构建。事务只负责建立项目、保存需求并入队；耗时任务由 Worker 完成。这样 API 可以及时返回，页面关闭后队列仍然存在。

## 3. 跑起平台

想先体验再学习，可以获取本仓库，在根目录执行：

```bash
uv python install 3.14
uv sync --locked
uv run rnd init
uv run rnd start
```

另开终端执行 `uv run rnd token`，在 `http://127.0.0.1:8000/` 输入本机访问令牌。模型设置只需 BaseURL、模型名和 API Key；也可写入本机 `.env` 的 `BASE_URL`、`MODE`、`API_KEY`。产品数据库、平台数据库和模型凭据分别配置。

`simple-admin` 的完整交付需要真实 Chromium。安装 Node 22 后，在仓库根目录执行以下 Linux/macOS shell 命令，并从同一个终端启动平台：

```bash
npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
export PLAYWRIGHT_BROWSERS_PATH=0
node .native/browser/node_modules/playwright/cli.js install chromium
export PRODUCT_VERIFY_PLAYWRIGHT="$PWD/.native/browser/node_modules/playwright"
uv run rnd start
```

Linux 系统缺少 Chromium 动态库时，按 Playwright 的安装输出准备系统依赖。Windows 的完整浏览器准备步骤见分阶段教材第 06 站。

远端模型默认必须 HTTPS。如果操作者明确使用自己信任的 HTTP 网关，可在启动进程前设置 `ALLOW_INSECURE_MODEL_HTTP=true`。HTTP 会明文传输凭据，应优先使用 HTTPS。这个选项只来自进程配置，不能通过模型输出或网页配置请求开启；改变模型地址时仍必须配置对应地址的独立 Key，重定向也不会自动跟随。

## 4. 一次提交多个项目

页面的批量创建区允许填写 1–10 个项目，每项有标题与原始需求，并复用所选技术栈。选“人工确认”时，每个项目分别等待需求、设计和交付确认；选“智能推荐”时，表示委托补齐细节和后续可委托关卡。必须明确审阅的扩展范围仍会停下来，任何模式都不能跳过独立验收。

API 与页面使用同一个入口。把批次保存为本机 `batch.json`：

```json
{
  "items": [
    {
      "title": "个人阅读书架",
      "requirement": "为登录用户管理各自的读书记录，支持书名搜索、分类筛选和阅读状态。",
      "template": "python-basic",
      "selection": {
        "template": "python-basic",
        "backend": "fastapi",
        "frontend": "simple-admin",
        "database": "sqlite"
      },
      "intelligent": false,
      "allow_custom_extensions": false
    },
    {
      "title": "库存采购协作",
      "requirement": "内部管理供应商、物料和采购单，采购员创建采购单，经理审批，仓库确认收货。",
      "template": "python-basic",
      "intelligent": false
    }
  ]
}
```

然后调用：

```bash
curl -X POST http://127.0.0.1:8000/batches \
  -H "Authorization: Bearer $RND_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: reading-and-purchasing-001" \
  --data-binary @batch.json
```

`RND_TOKEN` 是你在当前终端设置的本机平台访问令牌。响应结构为 `{"items":[{"project_id":"…","title":"…","run_id":"…","status":"QUEUED"}]}`。使用 `/runs/{run_id}` 查看状态；`/runs/{run_id}/events` 和流式接口展示进度，`/runs/{run_id}/report` 提供实际报告。

网络断开且不确定是否成功时，用**同一个幂等键和相同正文**重试。修改需求后应使用新键。单项不合法时整个批次返回 422；同键不同正文返回 409；未配置可用模型时返回 503。所有数据入口都需要认证。

上面两段短需求用于说明 API，不代表完整验收需求。正式验收使用 `examples/acceptance/` 中的完整需求，明确角色、字段和行为，避免把模型猜测误当用户要求。

## 5. 编码规范怎样真正生效

规范由公共规则和所选模板的专用规则合成：

- `templates/standards/common.md`：需求保真、复用已有能力、权限与事务、依赖管理、测试和交付要求。
- `python-basic.md`：FastAPI、SQLAlchemy、迁移、同源请求和 `simple-admin`／`api-only` 边界。
- `fastapiadmin.md`：上游 FastapiAdmin 认证、ORM、Vue 与 Element Plus 组件及扩展位置。
- `yudao-vben.md`：Java 分层、芋道模块实际目录、Vben 页面和原生 Ant Design Vue 组件。

`/catalog` 返回所选规范的内容、来源路径与 SHA-256；页面可以展开阅读。需求、设计和编码上下文使用同一规范。生成产物根目录包含 `AGENTS.md`、`VIBECODING.md`、`template-standard.json`，后续使用支持项目指令文件的 AI 工具时也能找到约束。

规范说明行为意图；执行边界继续由类型校验、允许编辑的路径、原生框架检查及独立测试落实。模型读过规范不等于遵守了规范，写出 README 也不等于项目已经可运行。

添加新模板时，先登记适配器、规范、真实页面/模块路径和验收入口，再添加模板测试。普通业务变化只增加需求与案例；确需新能力时应实现一个可复用的能力类别，并补上正向、越权、边界和失败测试。

## 6. 三个真实模型项目的验收

| 规模 | 场景 | 复杂度 | 核心验证 |
|---|---|---|---|
| 小 | 个人阅读书架 `reading-shelf` | 1 实体、个人数据空间 | 字段约束、搜索/筛选、两用户隔离、浏览器 CRUD |
| 中 | 库存采购协作 `stock-purchasing` | 3 实体、3 业务角色、采购流程 | 关联、角色权限、审批与收货、非法状态转换 |
| 大 | 设施维护运营 `facilities-ops` | 6 实体、4 业务角色、4 流程 | 跨实体关系、分派、处理历史、受限供料确认、提醒、指标和完整浏览器证据 |

三个案例固定使用 `python-basic` / `simple-admin` / SQLite，验证同一技术模板对不同业务场景的复用。这里的“大”指当前模板所支持的业务复杂度，相对前两个案例递增；该套件不代表原生多技术栈覆盖，也不代表高并发、大数据量、多租户 SaaS、线上运维或生产压测验收。

每案的 `requirement.md` 是模型可见的原始需求，`contract.json` 是独立测试的义务与数据，不能当作规划失败时的答案。三案通过 `Store.create_batch` 一次入队，再经普通 LangChain／LangGraph 路径生成。每案最多 12 次模型请求，总上限 36 次；模型格式修复也计入预算。

验收至少包括：模型契约与需求匹配、正常生成与独立验证、真实产品浏览器检查、最终交付包哈希、解压到新目录和新库启动、独立场景行为验证、重启后数据持久化。三个案例全部通过才允许汇总为成功。缺少案例、浏览器失败、模型调用失败或预算用尽都会留下失败结果，不把固定 Plan 或历史截图当作本次实测。

流程验收依据已批准的状态图，从初始状态寻找可达路径。互斥分支通过 API 创建独立测试记录，分别触发声明的状态转换及其通知；每条声明通知都必须有真实事件与正确收件人的验证证据，原有权限和状态转换规则继续约束每个测试动作。

失败回执会把字段差异定位到具体属性，例如 `books.started_on.filterable`，并给出受控的期望值和实际值；可能包含任意文本的值只保留长度、数量或摘要，不导出完整 Plan 或原始文本。每个模型任务的 JSON 格式校验仍最多尝试两次（首次请求与一次重试）。如果响应仅在一个符合 schema 的完整 JSON 对象后多出闭合括号，该对象只作为未批准的候选，供下一次模型调用参考；原响应仍记为失败，必须由模型重新返回一个完整且通过校验的响应，才能继续正常验收。格式修复不会默认通过，也不授权删除或改写已确认需求。

在 GitHub 的 `rnd` Environment 中配置：

| 类型 | 名称 | 用途 |
|---|---|---|
| Secret | `API_KEY` | 推理服务凭据，仅注入真实模型执行步骤 |
| Variable | `BASE_URL` | 兼容 Chat Completions 的 API 根地址 |
| Variable | `MODE` | 该服务实际提供的模型 ID |

运行工作流 **Three-project live acceptance**：对同仓库 PR 明确添加 `run-live-acceptance` 标签，或在工作流已进入默认分支后使用手动运行。普通 PR 同步不自动重复付费验收；变更代码后需要再次明确触发，并核对报告中的被测提交。工作流遵循 `rnd` 已有环境审核与分支规则，不自动批准环境部署。

旧的 `real-model.yml` 和 `ci_real_model.py` 保留历史专用供应商/客服验收约束，新通用三项目验收使用上述工作流。不要把旧流程的固定地址与模型门禁改掉后继续沿用旧证据。

## 7. 怎样检查自己的实现

先运行与本轮改动直接相关的验证：

```bash
uv run pytest -q tests/test_batches.py tests/test_model_http_opt_in.py tests/test_model_settings.py
npm ci --prefix ui --no-audit --no-fund
npm test --prefix ui
npm run build --prefix ui
uv run ruff check .
uv run ruff format --check .
```

完整回归、原生工具链和重建后的全套验收仍按教材第 14 站执行。修改代码、模板规范或 UI 后要重新生成教材，保证从零还原得到的是同一版本：

```bash
uv run python -m scripts.build_handbook
uv run python -m scripts.build_learning_docs
uv run python -m scripts.build_handbook --check
uv run python -m scripts.build_learning_docs --check
```

开发检查与真实模型验收分别记录。通过类型检查不能代替浏览器结果；某个模板通过也不能替其他模板背书。

## 8. 界面设计参考

本轮交互借鉴以下官方文档中的具体做法，再结合本平台现有能力取舍：

- [v0 Templates](https://v0.app/docs/templates)：在选择模板时说明用途、配置与固定版本，附可复用的项目说明。
- [Replit Task board](https://docs.replit.com/features/agent/task-board)：集中查看草稿、排队、执行与待审阅任务。
- [Dify Run History](https://docs.dify.ai/en/cloud/use-dify/debug/history-and-logs)：将最终结果、执行详情与节点追踪分层展示。
- [LangSmith Studio](https://docs.langchain.com/langsmith/use-studio)：结构化输入、真实流式事件与按需展开运行信息。

界面采用表单、项目队列和运行详情，优先让用户理解当前状态、下一步动作和验收证据。状态来自后端事件；没有实际能力的操作不会用可点击按钮假装可用。
