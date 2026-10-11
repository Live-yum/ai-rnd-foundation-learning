# docs/modular-production-v2.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本教材正文的源文件。** 上文正文就是这些源文件拼接后的内容。它们也收录在附录中，使从教材还原出的项目能再次生成逐字一致的完整教材，而不是只有一次性的代码快照。

**对应关系：** scripts/build_handbook.py的GUIDES → 正文 → 完整源码附录。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `docs/modular-production-v2.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L150。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16977`。本段原文以LF换行结束。

<!-- learning-source: {"path": "docs/modular-production-v2.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d64e20d53650e9ef1e9e63c7217b850bb50e2f8a27cd916c5b8097bbc642ba29"} -->
````markdown
<!-- docs/modular-production-v2.md -->
# 模块化单体与 V2 生产路径

## 状态与证据边界

本次基于 main `5c942d38c19b2cc784c2c66fa7c354cd27ae23c4`（PR #13）。
现有失败不能视为本次新增回归：Python acceptance `37961479973` 的 Windows browser-cleanup 超时；Daytona matrix `37961480166` 的 python-basic 失败。基线 artifact `11632412286` 的下载链接在当前执行环境返回 HTTP 403，尚未重检其内部原因。

本地 M0 核心基线：规划、候选守卫、旧 checkpoint 与审批恢复 42 项通过。
离线测试可以证明协议和恢复行为，不能证明真实模型能力、真实 Daytona 隔离或业务全量完成。
真实认证模型调用当前等待 HTTPS；mini-SWE 路径额外要求 HTTPS，不能使用 `ALLOW_INSECURE_MODEL_HTTP` 绕过。

| 里程碑 | 实现 | 验证与剩余工作 |
| --- | --- | --- |
| M0 | 固定 main、保留旧接口和 Gate 摘要 | 核心基线 42 项通过；已有 Actions 失败单独保留 |
| M1 | 实际迁移 core、planning、requirements、coding、production、interfaces、generation、persistence、llm | 旧模块为同一实现对象的兼容导入，非空目录 |
| M2 | 版本化 PlannedModuleV2 / CapabilityTaskV2、配置固定执行器、依赖和别名一致性检查 | 新 Run 固定 production_version=2；旧 Run 缺省 V1，不迁移旧审批 |
| M3 | 每 Run/来源版本隔离工作区、rnd-factory schema、受控 CLI JSON、ModelGateway 文档生成、严格来源映射 | 真实 OpenSpec 1.14.1 CLI 已验证；真实文档模型尚待 HTTPS |
| M4 | Python3.12 mini-SWE 2.4.6 Worker、平台 RPC、Daytona 文件环境、费用/请求/token/时间预算、复用 apply_candidate | 真实 Worker + mock 模型/环境通过；真实 Daytona 必须重新安全验收 |
| M5 | 客户/工单基础产品、两个 SLA 模块、独立 API/ZIP/重启 authored 场景 | authored fixture 与真实模型结果严格分开；浏览器 CDN 在本地返回403，Actions负责实际浏览器检查 |
| M6 | Vue features 域、关键后端分域、源码索引和教材重建 | 分域为渐进迁移；store 的队列/审批事务仍保留在现有 Store，原生 FastapiAdmin/Yudao 适配器尚未进一步分拆 |

## 目录与依赖

- `core/contracts.py`：稳定输入、需求与基线产品合同。
- `projects/models.py`：现有持久化项目、运行、审批、作业和步骤模型；不改变数据库表。
- `requirements/source_ledger.py, coverage.py, clarification.py, intent.py`：原始来源、覆盖与澄清。
- `planning/contracts.py, feature_planner.py, versioning.py, dependency_graph.py`：唯一权威 FeatureDesign、四路由、任务合同与串行 DAG。
- `specifications/service.py, artifact_writer.py, validator.py, openspec/cli.py`：规格文档准备，不执行产品工作流。
- `production/graph.py, state.py, dispatcher.py, worker.py, candidates.py`：LangGraph、恢复、分派与原子晋升。
- `coding/ports.py, bounded.py, candidates.py, diff_guard.py, mini_swe.py, aider.py`：受控代码编辑与外部 Worker。
- `infrastructure/persistence/store.py, llm/gateway.py, sandbox/coding.py`：平台数据、模型调用和经准入的本机 Daytona。
- `interfaces/http.py, cli.py`：FastAPI 和 CLI 入口；`workbench.api`、`workbench.cli` 等旧入口继续有效。
- `generation/python_basic.py`：完整基础模板生成。已有模板选择、原生栈和业务适配能力保留。
- `ui/src/features/{projects,plans,runs,approvals,delivery,settings}`：实际 Vue 功能实现；旧组件导入保留兼容。

生产编排调用领域合同；领域合同不导入 production。为保持现有调用与 monkeypatch 兼容，旧 Python 模块通过 `sys.modules` 指向新实现对象。不能把兼容文件误当成全部实现，安全验收源码清单同时绑定新实现路径。

## 新 Run 的显式选择

标准模式默认不调用 OpenSpec，module 路由使用 `bounded_edit`。`native/declarative/module/blocked` 不变，`mini_swe` 是 module 内部执行器，blocked 不自动转 Agent。

```json
{
  "requirement": "客户与工单管理，另加特殊 SLA 看板",
  "template": "python-basic",
  "allow_custom_extensions": true,
  "specification_mode": "enhanced",
  "module_executor": "mini_swe"
}
```

CLI：`uv run rnd chat --extensions --enhanced-specs --mini-swe`。增强设置只影响新运行；恢复使用 `--run`，不改旧 Gate。默认新增字段不进入旧请求指纹，维持原默认创建请求的幂等兼容。

PlannedModuleV2 与 CapabilityTaskV2 同时含 `version/task_id/executor/depends_on/requirement_ids/allowed_paths/acceptance_ids/max_steps`。兼容字段 `id/requirements/files/scenarios` 必须逐项一致。编译器检查原 V1 模块和任务一致后才产生 V2，绝不从 Markdown 复选框获得权限。模块数、来源、场景、路径、依赖以及整体合同版本全部验证。

## OpenSpec 的固定边界

官方版本与接口来源：<https://github.com/Fission-AI/OpenSpec>，本项目锁定 npm `@fission-ai/openspec@1.14.1`。安装：

```sh
npm ci --prefix tools/openspec --ignore-scripts
```

实际验证的命令：`--version`、`schema validate rnd-factory --json`、`new change product --schema rnd-factory --json`、`instructions proposal|specs|design|tasks --change product --json`、`status --change product --json`。

`rnd-factory` 是平台在独立工作区写入的自定义 schema，不假设上游内置。只产生 proposal/specs/design/tasks 和绑定回执。CLI 不接收任意参数、模型命令或产品目录，不调用 apply/archive。ModelGateway 生成严格 JSON 文档包，Feature Planner 使用同一完整来源独立生成可执行合同。文档摘要与设计摘要绑定，所有产物仍是未批准状态。

## mini-SWE 的执行边界与预算

官方协议来源：<https://github.com/SWE-agent/mini-swe-agent/tree/v2.4.6/src/minisweagent>。平台 Python 3.14 不安装该依赖；Worker 单独安装：

```sh
uv sync --project tools/mini-swe --python 3.12 --locked
```

Worker 通过标准输入输出的有界 JSON-line RPC 请求平台模型与文件编辑。它没有模型/Daytona 凭据，不装载用户全局配置，不使用 LocalEnvironment 或默认 DockerEnvironment。Environment 只允许 `edit` 和 `submit`；没有任意 shell 工具。此版本是受约束的 mini-SWE 编辑循环，不宣称支持其所有终端工具能力。

真实文件通道使用现有 `capability_execution_prerequisites`、本机 Daytona 私有无出口配置、实际容器检查与 profile 绑定。新源码变更使旧安全回执失效；必须重新执行原真实隔离正反例验收，不能拿 mock 替代。

控制端先检查路径、前像 SHA256、文件数量和 UTF-8 内容大小，再写沙箱；收回完整批准路径快照并转为 CapabilityEdits，最后复用 `apply_candidate`。Agent 不能编辑平台、审批、依赖锁、迁移、验收器或启动器。新增依赖/迁移仍阻塞。

显式启用 `MINI_SWE_ENABLED=true`，配置 `MINI_SWE_USD_PER_MILLION_TOKENS` 为运营方确认的保守费用上界；默认0会阻止真实调用。coding模型还必须显式配置 `max_output_tokens`（配置界面，或 `CODING_MAX_OUTPUT_TOKENS` / `MAX_OUTPUT_TOKENS`），未设置则阻止真实调用，不能只预留费用却发送无输出上限的请求。`MINI_SWE_MAX_TOKENS`、`MINI_SWE_MAX_COST_USD`、`MINI_SWE_TIMEOUT` 与批准任务 `max_steps` 共同约束。每次请求预留网关最多两次尝试的 token/费用上界，预留写入任务预算日志后才能调用；实际计费仍以网关回执为准。恢复可能保守重复预留，但不能增加已批准预算。平台原有 Run 级模型次数上限继续生效。

## 版本晋升和恢复

模板完整生成基线 v0。每个模块按依赖顺序创建候选，独立验证精确源码、计划、场景及隔离证据后才原子更新版本指针。版本回执包含来源摘要、代码 manifest、任务ID、前像摘要和完整测试证据。重复晋升只有候选与证明完全一致才幂等；修改已冻结产品会阻塞。

聚合验证要求所有任务完成、浏览器和重启证据完整后才产生 Verified Product。`AgentResult.success` 或 `Submitted` 只表示存在候选，不能成为业务验收通过。文件版本晋升可恢复；不承诺任意 shell 或外部服务副作用的精确恢复。

## 可复现验证

```sh
uv run pytest -q tests/test_production_v2.py tests/test_sla_vertical.py
npm test --prefix ui
npm run build --prefix ui
uv run python -m scripts.build_handbook
uv run python -m scripts.build_learning_docs
uv run python -m scripts.build_handbook --check
uv run python -m scripts.build_learning_docs --check
```

`test_sla_vertical.py` 的代码是审核过的 authored fixture：基础客户工单产品保留，两个模块通过真实 Python3.12 Worker 和 mock 模型/文件环境编辑，解包到新目录启动，独立 API 检查认证、用户隔离、逾期排除和重启持久化。设置 `PRODUCT_VERIFY_PLAYWRIGHT` 时增加实际 Chromium 页面断言。它不产生真实 Daytona 或真实模型证明。

## 手动真实模块验收：第一段交付

现有 [Manual real-model customer acceptance](https://github.com/Live-yum/ai-rnd-foundation-learning/actions/workflows/real-model.yml) 增加 `scenario=mini-swe-sla`。这是一个可执行的、范围固定的真实执行器验收配置，尚未运行真实模型；不是穷尽所有业务或所有执行器组合的验收声明。既有四路由保持不变。

| 模板 / 数据库 | 实现方式与当前入口 | 明确边界 |
| --- | --- | --- |
| python-basic / SQLite | native/declarative 确定性生成；`template-project-acceptance.yml` 三个真实模型规划场景 | 既有入口不覆盖模块执行器；不是三种模板 |
| python-basic / SQLite | module 的 `bounded_edit`，既有受控编辑和独立隔离验收 | 本轮未增加此执行器的付费完整场景 |
| python-basic / SQLite | module 的 `mini_swe`；本轮 `mini-swe-sla` | 两个审核固定的 SLA 模块，真实实现代码必须来自模型，不提供 authored 实现回退 |
| python-basic / PostgreSQL | 既有模板生成及独立运行矩阵 | 当前自定义模块准入只登记 Python/SQLite，不能借此声称 PostgreSQL mini-SWE 已支持 |
| FastapiAdmin / PostgreSQL | native/declarative 及既有原生工具路径；module 执行 profile 已登记 | 尚无本轮 mini-SWE 完整业务场景；模块 ZIP 原子消费者契约仅支持 Python/SQLite |
| Yudao / PostgreSQL | 既有 native/declarative 和原生工具验收 | 当前自定义模块执行准入未登记该 profile，不能自动切为 Python 或放开 Agent |
| 其他组合 / blocked | 继续按既有能力判定拒绝或暂停 | 不把 blocked 自动升级为 module |

新场景复用审核的 SLA **合同**和基础模板生成器，不调用 fixture 的 authored 实现函数。执行顺序是：无密钥 preflight → 同一 Job 的真实浏览器/Daytona 隔离正反例 → 两个真实 mini-SWE 模块（Python3.12 Worker、Daytona 文件通道）→ 每模块独立精确源码验收及晋升 → 重开版本账本、幂等重放晋升且不增加模型调用 → ZIP 解包新目录 → 新的隔离沙箱内使用受信任 `start.py` 冷启动、浏览器/API、数据库保留重启 → 聚合证据及消费者契约检查。新增断言覆盖未认证访问拒绝、其他用户数据隔离、已解决/未来工单排除和基础客户接口保留；生成代码始终不在控制器宿主执行。

恢复证据只覆盖版本账本重新打开和晋升幂等性；**不声称完成 LangGraph/Gate 全流程崩溃恢复**。需求规划、OpenSpec 文档生成及审批在此场景使用审核固定合同，不能视为真实模型规划验收；原生模板 mini-SWE 场景、旧数据库迁移、任意依赖变更及 M6 剩余拆分仍未完成。

### 手动入口和参数

在上述 Actions 页面选择 `feat/modular-production-v2` 分支，输入：

- `scenario`: `mini-swe-sla`（默认仍为 `legacy`，不会意外开启新付费场景）。
- `reviewed_sha`: 本次已审核分支的完整40位 SHA；必须与实际 checkout 完全一致。
- `max_cost_usd`: 本次单次手动运行的授权总上限，`0 < 值 <= 10`；默认 `0` 失败关闭。
- `usd_per_million_tokens`: 运营方核实的输入或输出 token 每百万美元费用的保守最大值，`0 < 值 <= 10000`；默认 `0` 失败关闭，脚本不会猜价格。
- `remaining_budget_cny`: 保留默认 `0`，仅属旧修复场景，不约束本场景。

Job 绑定既有 `rnd` 环境；`vars.BASE_URL` 必须是 HTTPS，`vars.MODE` 必须非空。只有通过 preflight、真实隔离准入后最后一个执行步骤获得 `secrets.API_KEY`。不新增环境、权限或不安全 HTTP 例外。若 Actions 页面仍显示默认分支的旧输入表单，可由操作者使用 `gh workflow run real-model.yml --ref feat/modular-production-v2` 并传入以上 `-f` 参数；先确认准确 SHA 和费用配置。这里不自动 dispatch，不通过加标签触发。

固定限制：两个模块，每模块最多8步；网关含修复尝试总共最多32次模型请求；每次输出上限8192 tokens；每模块预留总 token 上限2,000,000，总计4,000,000；每模块最多180秒；整个 Job 最多90分钟。总美元上限均分为两个不可借用的模块预算；每轮按最多两次网关尝试预留 `2 × (4 × 40000 + 8192)` tokens 及对应费用。配置必须至少容纳每模块 edit+submit 两轮，否则在持有模型密钥前拒绝。实际账单以服务方为准，保守价格必须覆盖所有计费 token 类别；多个新手动 dispatch 不共享累计预算，每次需重新授权。GitHub 的 Re-run（attempt > 1）不会执行此付费 Job。

仅上传 `reports/live-modules/summary.json` 白名单摘要，含精确 head、预算、源码/合同摘要及已检查的验收布尔项；不上传模型输入输出、产品代码、平台数据库或凭据。preflight 成功的报告明确 `passed=false`、`real_model_acceptance=false`，不能误当真实通过。最终必须同时检查 Job 成功及报告的真实验收标志。

离线验证：`uv run pytest -q tests/test_ci_live_modules.py`；正常 Python acceptance 的 production-v2 Job 同时执行这些契约测试。离线单测使用显式 mock 检查拒绝、预算、步骤顺序和晋升条件，绝不代表此新增完整真实路径已经通过。

### 已授权的测试 CA 与零计费模式

2026-10-11，用户明确授权公开 CA 入库并仅用于 `https://170.106.181.109:8317/v1` 的测试客户端，声明该测试服务无费用。证书保存在 `tests/resources/live-service/caddy-root.pem`，指纹及来源见同目录 README。该文件不是私钥，也不安装为系统根。

两条手动入口现均支持 `test_ca=caddy-ip`、`billing_mode=declared_free` 和 `confirm_no_charge=true`：mini-SWE 使用 `real-model.yml` 的 `scenario=mini-swe-sla`；三个 Python/SQLite 业务场景使用 `template-project-acceptance.yml`。两者都填写准确 `reviewed_sha` 并选择本 PR 分支；通过既有 `rnd.BASE_URL`、`rnd.MODE` 和 `rnd.API_KEY` 配置服务，不把密钥作为输入。mini-SWE 的 `max_cost_usd`、`usd_per_million_tokens` 保持真实的 `0`，不伪造正数价格。

`declared_free` 必须明确确认且绑定上述准确端点，回执注明 `user-confirmed-no-charge-2026-10-11` 及“用户声明，不是服务商账单”。平台 mini-SWE 同样要求明确零计费确认、精确端点绑定和费用/价格均为0；恢复不能更换原账本的计费模式。上述正数费用要求继续适用于默认 `metered` 模式，未声明免费时仍失败关闭。两个模块的32次请求、8192输出tokens/次、8步/模块、4,000,000总预留tokens、180秒/模块与90分钟Job上限保持不变。三个业务场景仍为每例12次、合计36次请求，每次最多16384输出tokens，Job最多90分钟。

在模型密钥仅对最后执行步骤可用之前，Actions 先请求不带认证的 `/v1/models`：严格 TLS 成功且服务返回200或401才继续。证书 SHA256 必须匹配固定指纹；SSLContext 保留 `CERT_REQUIRED`、主机/IP SAN、有效期和链验证。专用 transport 只允许准确服务的探测及 Chat Completions 路径，拒绝其他主机、端口、API根和重定向。没有 `verify=False`、HTTP回退、系统根安装或代理配置变更；旧三场景 workflow 的 HTTP 例外已移除。私有根正确不等于服务器叶证书正确；Actions 如仍遇IP SAN、链或访问拒绝，会在使用模型密钥前停止。

上述代码与离线测试不能代表真实调用成功。只有本次精确head的 Actions 终态及对应回执可以证明运行结果；TLS探测、三业务场景、mini-SWE模块路径分别报告，不互相替代。
````
