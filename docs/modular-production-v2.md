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
- `mini_swe_output_mode`: 默认 `json_object`。仅本场景可显式选择 `json_schema` 做原生 strict 兼容性试跑；该选项不扩展场景、权限或预算，也不改变普通模型设置。
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

### 经用户明确批准的浏览器 scope 扩展

首次 mini-SWE 运行 `38114248980` 已通过严格无认证 TLS 探测，但在模型调用前被浏览器策略的 workflow 名称门禁拒绝。用户随后明确批准仅该手动场景的 scope 扩展：准确仓库、`real-model.yml` 文件与名称、`mini-swe-sla` Job/场景、首次 `workflow_dispatch`，以及相同的完整 `REVIEWED_SHA`、`GITHUB_SHA`、`GITHUB_WORKFLOW_SHA`。workflow 引用还必须匹配当前分支；不把新名称直接加入旧三个 scope 的白名单。审计条件见 `tools/browser/review-only-v2/README.md`。

策略字节/SHA、Docker/内核/镜像来源检查、非 root、无网络、只读根目录、权限及资源限制均不变。新 scope 配置与离线回归不是实时隔离证明，下一次须在精确修复 head 重新通过全部隔离正反例，才能执行真实模块。

另一个独立的三 SQLite 运行 `38114286680` 在 `c5bb8de` 已完成3/3场景、7次真实模型请求（需求分析/规划），不证明 mini-SWE 执行器；无需为本 scope 修复重跑。两个手动 workflow 使用不同 concurrency group，且均不取消运行中的任务；本修复不修改事件或 concurrency。

### 模型调用前失败的安全诊断

`f0447dfce11388f6f434c273d7615b417b199622` 的手动运行 `38115731003` 通过严格 TLS、限定浏览器 scope 和真实隔离正反例后，在模块执行步骤退出1。回执 `11693670965` 的模型调用预留、HTTP尝试与响应均为0；在线步骤日志只有退出码，无法确定具体异常。不能将此结果归因为模型失败，也不能宣称 mini-SWE 已通过。

失败摘要现在额外保存固定白名单异常类型、固定受信代码阶段及该代码帧的行号；容器检查拒绝沿用现有严格过滤的类别/布尔/数字事实。未知异常名称和仓库外帧被抑制，不保存原始异常、堆栈文本、局部变量、SDK响应、提示词或凭据。离线回归使用真实锁定 Worker、正式场景上下文和模型网关，替换隔离环境及HTTP transport，已确认可到达首次调用预留和模拟 transport；这不是在线沙箱或真实模型成功证据。

此变更仅补齐故障可观测性，尚未确认或修复上述运行的根因。沙箱控制用户、权限、CA、预算和准入策略均未更改；不自动 dispatch 或重跑已通过的三 SQLite 场景。

后续诊断运行 `38117555376`（`d3bf4c9`，artifact `11694582817`）明确在容器检查处被 `sandbox_network` 拒绝：`network_mode=bridge`、`network_count=1`、`runner_bridge_attached=true`，模型调用预留/HTTP尝试/响应仍全部为0。原因是编码器使用 `rnd-agent-` 名称，而已批准 Runner 的网络与资源限制仅在 `rnd-source-` 分支启用；独立验证器已经使用该严格前缀。编码器现使用 `rnd-source-agent-`（原生选择使用既有 `rnd-source-native-` 前缀），使创建配置进入原严格分支，不删除或放宽检查。

原 Runner patch、单一准确 bridge 检查、`network_block_all=true`、私有沙箱、资源限制、控制用户、产品执行守卫及全部隔离正反例均保持不变。既有控制通道只传输批准业务文件，编码阶段不执行产品代码；后续产品执行仍必须经独立验证器与出口阻断守卫，不将控制 bridge 解释为任意网络授权。离线测试先复现原拒绝，再验证正确配置可通过真实检查器；旧前缀、额外网络、缺失配额和出口标志失效仍在上传前失败并删除沙箱。上述为模拟 Docker/SDK 事实上的离线配置证据，实际隔离及模型终态必须由新 SHA 的 Actions 再验证；本线程未 dispatch。

`81c0638` 的运行 `38119017832` 已越过该网络准入并发生3次模型调用预留、HTTP尝试和响应；artifact `11695510530` 随后在候选应用的完整唯一文件集合守卫失败。这不证明双模块或ZIP验收通过。现存回执没有返回路径的结构计数，不能断言具体为遗漏、重复或越界，也不能从3次请求推断已完成哪个模块。适配器离线测试确认文件列表不会被删减或去重，缺失的批准文件不会自动补齐。

此前网关仅校验通用AgentTurn，当前任务集合错误直到候选应用才被发现，错过了既有有界结构化修复流程。响应合同现在绑定当前批准任务：每次edit包含全部批准路径（含未改动文件），每个恰好一次，且不允许大小写重复或额外路径；同一约束在候选应用处继续独立检查。使用网关原有最多两次尝试和原预算，不增加调用、步骤或费用额度。模型指令明确完整文件与当前前像要求；不会以自动补文件掩盖未完成任务，语义完成仍由独立验收决定。失败摘要仅新增批准/返回/缺失/未批准/大小写重复数量，不含路径、源码或模型解释。离线mock transport验证错误集合可以在第二次完整响应后通过，连续错误严格在两次内失败。

同head的Windows截图负例失败（Python运行 `38118890653`，job `114409440268`）是诊断计数4与实际截图请求3不一致：计数递增在共享截止时间检查之前，临界时刻会记录未发送的请求。计数现移到受截止时间保护的CDP发送操作内。可控时钟测试先复现旧代码未发送却计1次，再确认修复为0；已发送但失败仍计1次。漂移/字体/像素断言、总截止时间、不输出不稳定成功截图等要求不变。当前本地缺少Chromium，官方安装端点返回403 Domain forbidden，未绕过；真实像素负例仍须由CI验证。

`d9703ef` 的Python运行 `38122424435` Windows shard1随后暴露了新fixture问题：`write_text("\n")`在Windows创建CRLF基线，而测试动作明确返回LF，两者不是同一未改动内容。候选写入器本来就按动作原文写入；测试现用显式字节构造LF、CRLF及混合换行，在Linux/Windows运行同样的逐字节断言，不忽略或归一化换行。同时，新增真实锁定Worker/mock gateway及真实检查器/mock SDK回归确认生产模型上下文和沙箱初始文件的`read_text()`也会归一化CRLF。仅这两处改用UTF-8字节解码；原样回传的上下文、沙箱文件和候选保持原字节。只改变换行的陈旧前像仍被哈希守卫拒绝，允许路径、预算及隔离不变。

同head手动运行 `38122528136` 于08:07:49 UTC执行步骤退出1。父线程随后通过正式文件下载读取artifact `11696606589`，ZIP SHA256为 `57993571bc1867d29ad18d2a7794aa6e8b168171349e54860981e3fc2f38ad75`。本次模型调用预留/HTTP尝试/响应均为2，失败为`DaytonaError / coding_sandbox / d9703ef第40行`，不是81c0638的候选文件集合错误。该行调用`download_file(path, timeout=...)`；锁定SDK0.190.0的重载标注支持关键字，但实际实现仅接受位置参数。离线真实SDK复现其在下载HTTP前将TypeError包装为DaytonaError，确认调用签名缺陷。

本次最小修复仅把超时改为`download_file(path, timeout)`位置参数，不改SDK版本、端点、批准路径、原超时、100000字节限制或UTF-8要求，不增加请求/重试。保持空文件及CRLF字节支持；实际SDK+mock HTTP回归覆盖空文件、恰好100000字节、超限、非法UTF-8、截断multipart及401/403/404/500失败，并检查响应关闭和原读写超时传递。此修复与独立的Windows换行修复均仅有离线证据，完整双模块/ZIP实时验收仍待新SHA结果。

### 浏览器内存失败的只读观测（尚非修复证明）

453c24a的PostgreSQL隔离运行38126100189在浏览器资源证明处失败，尚未进入PG产品验收。正式artifact11697318126（ZIP SHA256 `f07e5a8d369ee2bd7be0bbf9ebb58ebfa48799f91c6dbe5cf85d0e5f60f46b2e`）记录退出码及docker start返回码137，OOMKilled=false、Running=false、Status=exited，既非超时也非检查失败。进程终止不证明该容器内存上限导致OOM；该失败保留，不能归因于模型或仅凭137通过。

本地诊断补丁新增可选`memory_observation`，只绑定已检查的完整容器ID与本次随机名称。仅尝试`/sys/fs/cgroup/system.slice/docker-<ID>.scope`和`/sys/fs/cgroup/docker/<ID>`两个准确路径，禁止符号链接，检测组身份变化；不扫描进程、不读取其他组或父组信息、不调用sudo或新增权限。只保留有界`memory.max/current/peak`及`memory.events.local`计数，最多30秒/300次只读轮询。Docker事件仅查询同一ID、同一时间区间的oom/kill/die，2秒超时、有限行数，仅输出事件类型和时间，不读取日志、标签、环境或原始错误。

原Node压力循环、768MiB内存/同额MemorySwap/CPU/PID限制、30秒启动超时及`OOMKilled is True and Running is False`判据保持不变。诊断收尾发生在原状态采样和判定之后，不用等待事件来改变原采样结果；诊断构造/读取/权限/收尾失败均不替代原结果。`oom_kill`增量不是通过条件。新辅助代码纳入源码身份摘要，策略JSON和scope不变。

如果原检查没有确认容器停止（包括超时、仍运行或检查失败），先停止只读采样，不等待线程、不额外读计数器或查询Docker事件，避免诊断延迟原有清理。只有已确认停止的容器才进行最多0.5秒收尾等待和2秒事件查询。Docker历史事件缓存有限，查询为空不证明没有OOM或kill；这些观测仅辅助定位，不能替代原有受信资源证明。

启动前或退出后的cgroup可能不存在，缺失样本明确为null，不假设初始计数为零。`pre_post_delta`只有真实前后样本都可用且身份一致时才存在；首末可见样本的`observed_delta`单独记录，不能冒充完整压力区间。该补丁仅准备后续有目标的诊断，不能追补已删除容器的事实，也不宣称解决了此次资源证明失败。


### 登录夹具清理生命周期（本地准备）

453c24a的Windows Python运行38126100115/job114430670410由父线程提供的证据显示：generic-fastapi/missing-main原负例断言完成后，browser.close超过夹具独立3秒限制；2193通过、1失败、69跳过。此处并非导航业务断言或先前换行/截图计数回归。子线程重新读取正式日志及mini-SWE运行38126262748的artifact11697773853均返回ConnectError，后者调用次数及根因仍未知。

本地夹具改为显式context，释放挂起图片后先停止HTTP服务并关闭其连接，再依次关闭context/browser；所有关闭共享启动后29秒的截止点，Python原30秒总上限及业务1800毫秒断言保持不变。清理拒绝或超时不吞掉：保留Node事件循环直至Python按原总上限回收该夹具进程树，防止Node提前退出后无法再确认后代归属。Windows taskkill非零退出也必须报错。现有POSIX身份/启动tick检查及Windows精确PID /T /F范围保持不变，不使用全局进程名终止。

离线Node回归覆盖超过旧3秒但仍在总预算内的完成、context/browser/server拒绝、挂起以及父进程实际回收；真实Chromium与Windows结果仍待后续CI，不将夹具修复或本地测试描述为实时产品验收通过。本轮不推送、不重跑工作流。

### 453c24a 模型失败的诊断缺口

父线程随后通过官方读取恢复mini-SWE运行38126262748/artifact11697773853：passed=false，ModelFailure/model_gateway/trusted_source_line312，model_call_reservations=3、model_http_attempts=3、model_http_responses=2，严格TLS检查通过。精确453c24a源码位置为`workbench/infrastructure/llm/gateway.py:312`；`workbench/llm.py`只是兼容导入。该行是两次尝试耗尽的共用出口，结构化输出失败、可重试HTTP状态或一般传输错误均可到达，不能仅凭少一个响应计数判断限流、超时或其他具体原因。此处不沿用旧运行的DaytonaError。

网关原本会在临时数据库记录每次model_failure，但该场景清理后未向summary保留这些记录。本地补丁在既有finally中导出最多32项`model_failure_receipts`，只含白名单code、1/2次尝试序号，transport_error另含基于有界异常类型链的固定transport_kind。HTTP代码限100–599；未知分类为other，非法序号为null；不导出endpoint、模型名、请求ID、时间、headers、prompt、校验字段路径/值、异常或响应正文。读取诊断失败记null，不替换原验收结果。只增加诊断，不改变两次尝试、退避、TLS、超时、预算或严格输出契约。

真实网关/mock HTTP回归覆盖第一次无效JSON后第二次读取超时、远端协议错误、429或再次无效JSON；两次调用数保持不变。真实锁定Worker离线路径覆盖诊断读取成功和失败；白名单污染、上限及异常链环路有回归。既有453 artifact没有新增分类，补丁不能追补已删除临时数据库中的证据，当前具体根因仍未知；继续仅本地准备，不推送或盲目重跑。

### 719bca1 主回执字段回归（本地修复，待真实复测）

719bca1手动mini-SWE运行38129824945在模型前的ci_capability_security被require_browser_acceptance第302行拒绝；普通SQLite隔离38129655377同处失败。静态精确源码及离线串联复现确认：b932694新增观测时无条件向主回执写入memory_observation，但消费者要求原8个顶层字段精确匹配，即使所有真实检查通过也会拒绝。此前仅测生成器结果而未把其输出交给真实消费者，遗漏了兼容性回归；不能把这次模型前失败归因于模型、OOM或未经证明的时效问题。

本地修复保持消费者原封不动，把可选memory_observation移至独立reports/capability-browser-memory-diagnostic.json，主成功回执恢复原8字段。诊断写入失败不覆盖原验收结果；诊断文件不是准入证据。既有artifact上传步骤仅补此文件，mini-SWE步骤另补原主回执，以便下次模型前失败也可取得证据；不改事件、scope、SHA绑定、时效、超时、调用预算或工作流安全配置。

新增真实main生成器→原require_browser_acceptance串联回归，仅替代Docker/浏览器及主机运行事实，源码与镜像源码摘要仍由真实函数计算；不是实际容器证明。修复前3个成功观测分支均复现第302行拒绝；修复后正例通过，未知顶层字段（包括重新塞入memory_observation）、旧源码/运行身份、不完整检查、mocked及非布尔passed仍拒绝；OOM未证明、仍运行、启动超时等原负例仍拒绝。可选观测不可用、收尾失败、落盘失败、诊断文件修改或缺失均不改变主回执判断。相关离线221项通过；本轮只本地准备，不推送、不触发模型或三SQLite运行，等待719其余CI全部终态。

### dba4ffc 独立验证子进程与节点诊断（本地准备）

手动mini-SWE运行38132855481/artifact11700585899由父线程正式读取：模型预留/HTTP尝试/响应均2，model_failure_receipts为空，失败阶段independent_verification、原异常类型other、精确capability_sandbox.py第388行。官方job114450597615日志只能取得执行步骤退出1；节点回执未在artifact中，临时目录已删除。该行是子进程非零退出的统一PrerequisiteError，不能据此判断具体业务断言失败；普通CheckFailure本来会由子进程捕获并写失败回执。两次模型调用不代表模块或完整交付通过。

源码核查另确认可复现的环境传递缺陷：父控制器已按reviewed策略通过浏览器准入，独立子进程的clean_env却丢弃策略选择及Actions scope字段，再校验同一回执时选择docker-default，造成身份/检查集合不一致。实际Python子进程+原浏览器消费者离线回归先复现非零退出，再验证最小修复：仅给可信验证子进程传递经原selected_policy验证的固定策略与scope字段，子进程继续运行原校验。未修改通用clean_env、策略JSON、scope规则、回执字段/时效、模型预算或独立oracle；key、GitHub token、代理与任意环境不传入子进程。错job/scenario/attempt/repository/workflow引用及SHA仍拒绝。该缺陷必须修复，但旧artifact不足以证明它是本次唯一失败原因。

新增可选节点诊断独立文件，记录固定异常类别、受信源码阶段和行号；捕获普通验收失败及main/准入/清理的未捕获异常，不读取或公开子进程stdout中的原始堆栈。父控制器在临时目录删除前向summary保留最多3个verification_receipts（两个节点及aggregate），只含scope、回执存在、布尔状态、固定cleanup标签、异常分类、受信行号及检查数量。文件读取限1MB；未知、损坏、超限与过期诊断被抑制；不复制候选源码、字段路径/值、构建输出、SDK文本、提示词、URL、环境或headers。原验收回执schema不变，诊断失败不能替代原失败或产生成功。诊断模块加入现有验证器源码摘要。

实际子进程失败→父进程原异常→临时目录删除→最终summary落盘已有串联回归；同时覆盖捕获的隔离拒绝、污染/超限/失效诊断、读写失败及原scope正反例。相关离线241项通过，3项主机Landlock检查因本环境内核条件跳过，不计真实容器证明。

普通Python38132702803的Windows shard0/job114450143346为另一个失败：官方日志定位business-browser.cjs第14行，管理员分配后切换service-a登录，workspace在原15秒内未显示；2207通过、1失败、71跳过。页面显示工作区前等待schema和业务面板请求；日志没有这些请求状态，无法区分请求错误、同步或真实权限回归。本轮不修改UI/RBAC/超时，不以推测修复。PostgreSQL38132702844的资源证明失败仍保留：其pre_start、post_start_return、pre_post_delta均null，零增量仅是三次observed_delta，最后采样峰值不是完整退出期证据；终止来源未知，不扩大诊断或调整压力。

本轮仅本地准备；等待dba4ffc剩余矩阵终态再推，不取消、不额外dispatch或重跑三SQLite，复杂场景未启用。

### efc8e2a 离线启动夹具的 AST 作用域修复（本地）

efc8e2a的普通SQLite38136635699和PG38136635758在离线launcher/receipt测试阶段失败，尚未到本轮资源或产品验收，不能沿用旧PG OOM结论。生产_verify在外层try之前已初始化diagnostic_error；test_capability_startup_paths.py却只抽取start及其后片段和外层finally，漏掉该初始化，32个参数场景在合成作用域中触发NameError。此前较小测试集合遗漏了这一AST消费者。

本次仅修复测试：从同一个真实_verify AST中抽取外层初始化语句并在合成try前执行，不硬写测试默认值，也不移动或绕过生产初始化。原32个后端/前端、初次启动/重启、不同退出状态场景保留异常传播路径，并新增32个使用原生产except处理器的场景；全部保留启动目标绑定、两个客户端关闭、沙箱删除、失败状态及脱敏断言，新路径另检查实际异常对象进入诊断。已审同源AST消费者：startup_session只提取会话构建语句，capability_obligations只提取重启段；只有startup_paths复制外层finally。生产实现、安全scope、工作流及资源门禁均未改。

按两个workflow的完整离线命令解析实际文件集合：SQLite为53文件，PG为55文件且包含前者；使用PG完整集合覆盖两套，始终保留RND_REQUIRE_NODE_TESTS=1、RND_REQUIRE_LANDLOCK=1、RND_REQUIRE_SECCOMP_BPF=1。修复前37失败/2469通过/13跳过，其中32个NameError、5个Landlock强制检查返回78；修复后5失败/2533通过/13跳过，仅剩相同5个主机内核条件失败。三个AST消费者专项200项通过。13个跳过涉及缺少原生Node/Vite工具树与测试数据库；本地Python3.14.7、Node24.19.0，不冒充Actions的Node22和内核环境，也不关闭强制标志伪造全绿。

本轮仅本地准备，未推送、取消或重跑真实模型；等待当前efc8e2a全部运行终态。已有模型、Windows业务登录与环境资源证明的未知原因保持原边界，复杂场景未启用。

### efc8e2a 已到启动健康门禁，补保留既有安全启动事实（本地）

父线程从官方artifact11701442745恢复本次真实mini-SWE证据：模型预留/HTTP尝试/响应为4/4/3，model_failure_receipts含invalid_json attempt1及transport_error/read_timeout attempt1；最终由product_ledger第55行拒绝晋升。节点为CheckFailure/verifier_controller/精确capability_sandbox.py第789行，backend_health_observed=false、checks_count=0、obligation_checks_count=0、restarted=false、passed=false、cleanup=deleted。这次独立验证已运行，不能把最终失败仅归为网关，也不能把4次调用或3次响应算作业务验收通过。

第789行是原启动deadline内未观察到健康2xx。到达此处前已取得启动命令ID与私有预览令牌，但这些不证明应用进程持续存活。候选源码已通过inspect_stack对全部Python文件的AST语法检查；离线用语法正确但引用不存在模块的样例确认该门禁不等价于导入或健康成功，并保留真正语法错误的拒绝。受保护启动命令为start.py --no-install --host 0.0.0.0 --port <批准端口>，当前无固定入口/端口错误的可证修复。实际候选、完整节点回执与启动输出未上传，临时目录已删除，无法复原该次具体导入/初始化/进程或预览问题。

验证器原本已在健康失败时采集有限startup_diagnostic，但上一版summary过滤遗漏了该段。本地仅补过滤已有数据：HTTP状态100–599、固定HTTP错误标签、受控命令退出码0–255/状态、启动上报和输出可读布尔值、固定启动阶段/异常类别提示、受限输出提示及backend/frontend目标类别。候选输出产生的提示仅是线索，不能作为验收或内核证明。继续丢弃原始输出、模块/符号文本、URL、headers、源码与凭据；不增加SDK查询、日志读取、宿主权限或scope，也不改启动命令、deadline、health条件或独立oracle。

55项针对性回归通过，覆盖缺模块、名称错误、HTTP404与连接失败的既有分类器→节点过滤，以及临时目录删除后summary仍保留固定事实且不泄露污染内容。再次执行两个工作流完整55文件覆盖集合，三项强制标志保持1：2539通过、5失败、13跳过；5失败仍是本地Landlock检查返回78，未关闭门禁或宣称全绿。6a4f53a AST夹具修复保留；本轮仅本地准备，等待最后矩阵终态后再推送，不盲重跑真实模型或三SQLite。

### 85ce81c 导入期权限线索与受信模板数据目录修复（仅本地）

父线程从真实运行38140738102的官方artifact11702909015读取：模型预留/HTTP尝试/响应均2，model_failure_receipts为空；后端启动命令退出1，HTTP502，application_startup_reported=false，startup_phase_hint=import，PermissionError及permission-denied提示，tmpfs_noexec=true。节点零健康检查、未重启，账本拒绝晋升且cleanup=deleted。提示不能证明具体模块或路径，也不能证明noexec是原因；旧候选已删除，不能还原它的实际报错路径。

受信模板存在独立可复现的路径矛盾：该SLA计划批准data/application.db，冻结源码只把data父目录交给应用UID20000写入；schema.py导入时即使有PRODUCT_DATABASE_URL，仍无条件创建默认.data。消费者start.py原来只对齐两个数据库URL，没有设置PRODUCT_DATA_DIR。新增回归使用控制器生成的同一acceptance_design模板，在非root POSIX用户、只读源码目录和独立0700数据目录中实际导入schema：原环境因创建.data而PermissionError；把PRODUCT_DATA_DIR绑定到规范数据库父目录后导入成功，.data和__pycache__均未创建，源码根目录写入仍被拒绝。仅执行受信模板，不在宿主执行模型候选。

最小修复限于消费者启动器：解析并规范化原SQLite文件后，同时设置PRODUCT_DATA_DIR为其父目录，覆盖不相干的环境目录。保留已有外部数据库路径兼容性，隔离运行仍由原数据库环境和文件系统规则约束。未改目录权限、UID、noexec、只读依赖树、pycache策略、scope、预算、超时或验收规则。实际隔离器已设置PYTHONDONTWRITEBYTECODE=1并使用只读锁定解释器；本次复现使用仓库锁定依赖的本地解释器和-B，不能冒充远端UID20000、挂载或Landlock运行证明。新增3例修复前全部失败，修复后消费者55项通过；真实旧候选是否触发同一缺陷仍未证明。

完整执行两个workflow的55文件覆盖集合，RND_REQUIRE_NODE_TESTS、RND_REQUIRE_LANDLOCK、RND_REQUIRE_SECCOMP_BPF始终为1：2542通过、5失败、13跳过；失败仍仅是本机Landlock返回78的既有五项，跳过仍涉及原生工具树/Vite和测试数据库。Ruff及生成文档一致性检查通过。本轮只本地提交，未推送、取消、dispatch或重跑三SQLite；等待85ce81c其余CI全部终态后再由父线程决定后续，真实模型验收仍未通过。

### 89f88e7 本轮网关失败与固定解析阶段诊断（仅本地）

父线程监控实际读取真实mini-SWE运行38145005717/artifact11705256919：configuration_valid=true，phase=execution，passed=false，real_model_acceptance=false；模型预留/HTTP尝试/响应2/2/1，第一次transport_error/read_timeout，第二次invalid_json，最终ModelFailure/model_gateway/原第318行。该行是两次尝试耗尽的公共出口。完整允许字段没有HTTP状态、finish_reason、具体JSON错误或verification_receipts；本轮未到独立验证，不能归因于旧PermissionError，也不证明DATA_DIR修复已通过。此处由父线程实际读取内容；本地独立核验官方artifact元数据及准确SHA，下载正文被代理403阻止，未绕过。

离线实际网关分别模拟第一次读取超时、第二次信封JSON损坏或合法信封内正文JSON损坏，两种情况产生完全相同的原2/2/1计数与失败标签；合法正文对照成功，明确finish_reason=length按原规则记truncated。现有回执不足以定位服务端延迟、网络、信封或正文问题，没有可证实的生产判定缺陷，不增加超时/重试、不放宽JSON，也不猜测模型根因。

经限定授权，仅增加可观测性：AuditedTransport记住本次既有HTTP状态；网关给invalid_json失败附加response_facts，以同一审计异常身份及JSON解码/防护异常类型识别envelope_decode（包含SSE帧），以已取得的正文识别content_decode，其他情况unknown。finish_reason只保留审计器完成原检查后已有的stop/unknown，不把未确认的原始结束字符串当作事实。HTTP状态仅允许100–599整数且拒绝bool；临时数据库记录和summary导出共用固定字段白名单，再次过滤未知枚举和多余字段。旧记录没有该字段就不补写，不从旧invalid_json反推阶段；其他失败代码与流式UI错误事件不变。不记录正文、路径、源码、模块名、headers、URL、提示词或凭据。

普通/SSE两条真实网关集成路径覆盖超时后信封失败、正文失败、合法响应、明确截断，保留2预留/2HTTP尝试/1响应、原请求与JSON模式及原接受/拒绝结果；污染/缺失/非法状态/旧记录回归确认安全导出。补充实际观察器ValueError负例，确认非解析本地异常不会被误标为信封或正文解码；原错误代码及两次尝试保持不变。网关、流式、反馈及真实验收脚本相关463项通过。改动不改变模型请求、预算、超时、权限、scope、严格校验、清理或晋升门禁；仅本地准备，等待89f88e7剩余普通CI终态后再决定发布，不推送、不取消、不dispatch或重跑三SQLite。

最终代码再次执行两个workflow的完整55文件集合，三项RND_REQUIRE_NODE_TESTS/LANDLOCK/SECCOMP_BPF保持1：2542通过、5失败、13跳过；五项仍为本地Landlock返回78，跳过仍为原生工具树/Vite与测试数据库。没有关闭强制标志，本地Python3.14.7/Node24.19.0不冒充Actions环境。Ruff、diff及完整手册/771份教材一致性检查通过。此提交仅使未来安全回执能定位解析层级，不修复或追补本轮模型失败，不代表DATA_DIR已通过真实验证。

### ce175a5 模型前API构建停滞与限定脚本观测（本地方案）

第15轮38148774162/job114497616525在API镜像构建2400秒超时，模型步骤未执行，没有新JSON分型。官方日志显示yarn install --immutable解析及下载完成，3594包/1.53GiB的Fetch耗时22.202秒，Link开始于步骤23.57秒；77.15秒出现并行安装脚本列表，最后80.38秒仅见cpu-features的node-gyp请求返回HTTP200，不能证明响应体下载完成或它是唯一阻塞者。API命令第105秒起日志恒为53599字节，直到2400秒；至少2295秒无新增输出。上一轮38145005717/job114486410100的API约196秒完成，整批镜像约532秒。两个提交的构建脚本及工作流没有变化，但固定上游Dockerfile仍引用node:24-slim和未指定版本的Corepack，现有日志不证明所有外部输入完全相同。没有实施依赖、缓存、超时或安装脚本的猜测性修复。

本地最小诊断方案利用[Yarn官方wrapScriptExecution钩子](https://yarnpkg.com/api/yarnpkg-core/interface/hooks#wrapScriptExecution)，通过[Yarn4.13配置支持的YARN_PLUGINS入口](https://raw.githubusercontent.com/yarnpkg/berry/@yarnpkg/cli/4.13.0/packages/yarnpkg-core/sources/Configuration.ts)只在API的两个原有immutable安装命令中加载受信观察器。先核对完整上游Dockerfile blob，再复制唯一观察器文件；其SHA256写入生成recipe，纳入现有recipe摘要，原镜像ID与源码/补丁锁定检查不变。不编辑package.json、yarn.lock或.yarnrc.yml，不关闭脚本，不重定向或压制其原输出。

观察器只记录固定安装脚本名、公开依赖白名单名（其他为other）、有限数字版本、定位符摘要、随机会话标识、开始/返回/抛出和有界退出码。执行器只调用一次，原返回值及异常原样传播。每30秒输出最多32个尚未返回脚本及其耗时，状态仅为awaiting_script_exit，不宣称已识别网络、锁或内核等待。最多跟踪256次调用，超限明确标记；定时器unref不延长工具生命周期，日志写入失败不改变脚本结果。会话分开记录，避免嵌套Yarn或重复配置初始化混淆。没有宿主进程枚举、PID、环境、完整命令行、路径、脚本正文或子进程输出采集。

[Yarn4.13源码](https://raw.githubusercontent.com/yarnpkg/berry/@yarnpkg/cli/4.13.0/packages/yarnpkg-core/sources/scriptUtils.ts)明确区分executePackageScript和executePackageShellcode：此官方钩子只覆盖命名manifest脚本，不覆盖隐式shell构建。回执固定coverage=manifest_scripts_only，不能将零活动脚本解释成所有构建完成；不猴子补丁Yarn内部执行器来伪造完整覆盖。Corepack通过当前构建容器内既有corepack --version读取，2秒/SIGKILL/1KiB输出上限，失败unknown；YarnVersion来自正在执行的Yarn，Node版本来自同一进程。所有诊断开销仍位于原2400秒命令预算内。

宿主只过滤既有run_command的有界首尾日志：从本次BuildKit实际FROM记录提取builder/daytona的node:24-slim摘要，不用后来解析标签来冒充当时身份；日志缺失就不填。版本、阶段、状态和数值再次过滤，最多4会话/64事件，标记日志摘录及会话/脚本截断。成功和ToolFailure都会保存独立api-build-observation.json；写入失败不替代构建结果，失败后仍拒绝image inspect/晋升。该诊断不是镜像准入证据，原始日志行为不变。原mini-SWE artifact仅增加这个精确JSON文件；[upload-artifact对隐藏路径的规则](https://github.com/actions/upload-artifact#uploading-hidden-files)要求include-hidden-files，因此只对原步骤的五个精确安全JSON路径开启，回归拒绝目录或通配符扩张，不上传.data目录或原始构建日志。

离线使用真实Yarn4.13.0及禁止网络的合成项目验证成功/退出7两条路径，观察器前后接受结果一致且三份输入文件逐字节不变；另用31秒合成脚本验证真实30秒等待快照及正常结束。Node钩子回归覆盖挂起、原异常对象、原返回码、日志写失败、只执行一次、不读额外脚本/环境信息和非安装脚本不拦截；解析器覆盖污染、非法数值、会话隔离和缺失输出，构建回归保留2400秒、原ToolFailure对象和失败禁止镜像检查。实际包/构建仍未复现，不据此宣称停滞已修复。仅本地准备，是否发布及下一次有界构建由父线程审阅后协调；未推送、取消、dispatch或重跑三案。

验证结果：相关原有及新增离线测试116项通过，精确artifact路径补充回归另1项通过（合计117）；其中真实Yarn4.13.0三项均实际执行，未按缺工具跳过。完整55文件工作流集合保留RND_REQUIRE_NODE_TESTS/LANDLOCK/SECCOMP_BPF=1：2542通过、5个既有本地Landlock返回78失败、13个工具树/Vite或数据库条件跳过。没有进行Docker/API昂贵复现，也没有真实模型调用；本地主机与真实Actions环境边界保留。Node语法、Ruff、diff及两套生成文档一致性检查通过。

### e2c9dda PG内存端点读数缺失的生命周期核查（仅本地）

父线程监控实际读取PG运行38154312061/artifact11708021591：memory_exhaustion，exit137、Running=false、Status=exited、OOMKilled=false、timeout=false；3次采样memory.max=805306368，最后peak=805306368，observed_delta.max=1，oom/oom_kill/oom_group_kill均0，仅Docker die；pre_start、post_start_return、pre_post_delta仍null。可确认采样时触及内存上限，不能证明整个终止区间的OOM原因或认定严格门禁误报。并行真实mini-SWE38154524202仍在镜像构建，不能混用其结论。

调用顺序已从源码核对：docker create及原检查→observe_memory.start中的一次前置采样→启动100ms轮询线程→docker start -a→原终止状态inspect及OOMKilled/Running判定→observe_memory.finish中停止/最多0.5秒join采样线程→再读一次cgroup→原docker rm清理。post_start_return这个历史字段并非紧贴start返回读取，而是在终止inspect之后。Docker create只准备未启动容器（[官方说明](https://docs.docker.com/reference/cli/docker/container/create/)）；无活进程的cgroup可被移除（[内核说明](https://docs.kernel.org/admin-guide/cgroup-v2.html#processes)），容器记录仍可inspect不代表组目录仍在。这个生命周期模型解释了端点采样窗口为何可能落在组尚未出现/已经消失的区间，而不是断言本次未保存的errno必然为ENOENT。

发现的确定诊断缺陷是原读取器把目录缺失、计数文件缺失、权限拒绝、非法内容/路径及布局歧义全合并为None。最小修复只对同一次既有读取分类：group_absent/counter_missing/permission_denied/invalid_counter_or_path/ambiguous_layout等固定枚举；保留原read_cgroup接口及全部路径、O_NOFOLLOW、数字/字节上限、设备/inode身份和布局规则。sidecar新增pre_start_status、post_start_return_status及post_start_return_stage，准确标记after_termination_inspect；未确认停止则not_sampled，仍不额外读取、join或查询Docker。不输出异常文本、errno上下文、原始路径、环境或其他组内容。

四种离线组目录生命周期组合证明：前置目录不存在及退出时目录被移除可同时造成两端null，而first/last仍保留触限样本及max增量；任一端缺失时pre_post_delta继续null。不是把first_observed重命名为基线，不预设零计数，也不把observed_delta提升为全区间证明。权限/缺文件/坏计数/歧义另有负例，原异常对象和严格失败保持不变。没有修改压力程序、768MiB上限、30秒超时、100ms/300次采样、终止inspect顺序、OOMKilled必须为true且Running为false的条件，未扫描进程或父cgroup、未持有或创建额外组、未冻结进程或增加权限。

本轮改动是缺失原因与阶段的准确标注，不能保证取得完整生命周期端点；要保证启动前压力基线及退出前最终计数，需要另外设计可审核的生命周期同步协议，当前没有实施这种压力时序变化。不能据此宣称PG隔离证明已通过或本轮终止原因已确定。执行环境断开通知后，已在原/workspace工作区实际验证读写与Python执行成功；未切换环境绕过权限。仅本地准备，等待父线程安排，未推送、取消或重跑。

验证：相关生命周期、OOM诊断、原主回执生产者→原消费者及策略回归189项通过；完整55文件集合保留三项强制标志，2542通过、5个既有本地Landlock返回78失败、13个工具树/Vite或测试数据库条件跳过。Ruff、diff及完整手册/774份教材一致性检查通过。没有取得新的真实cgroup/OOM证据，不冒充真实内核隔离验证。

### e2c9dda 模型正文JSON失败的安全诊断投影（仅本地）

父线程实际核验真实运行38154524202/artifact11708343281：2次预留、2次HTTP尝试、1次响应；第一次invalid_json，response_facts为http_status=200、finish_reason=stop、phase=content_decode，第二次transport_error/read_timeout，最终ModelFailure且passed=false，没有双模块ZIP。可定位正文解析阶段，不能猜测正文、认定声明的长度截断或宣称已有根因修复。

只读核查确认：请求使用官方LangChain with_structured_output(method="json_mode")；提示含同一schema及完整对象、禁止围栏/说明/重复字段约束，mini-SWE另明确全部批准文件恰好一次。正文提取保留finish_reason、空白、拒绝及工具调用检查，本地仍执行严格JSON、schema及任务绑定校验。JSON mode不证明私有兼容端点支持服务端json_schema；任务绑定Python校验器也不会完整体现为JSON Schema。本轮未切换协议或探测端点，没有削弱接受条件或修补未知JSON。

已有json_diagnostics保存固定类别、JSONDecodeError行列/偏移及字符/字节数，但验收摘要未导出。最小变更仅为invalid_json新增json_facts投影：只接受恰好一项字典诊断和现有固定JSON类别，排除结构化解析器分歧类别；position仅line/column/offset，lengths仅characters/bytes。所有数字必须type(value) is int，拒绝布尔、字符串、浮点及容器；行列范围1至2000001（包含输入末尾位置），偏移和长度0至2000000，依据原有正文上限。非法字段丢弃，非法类别/诊断结构不产生json_facts；未保存详情的旧回执保持原状。message、path、正文、片段、未知键均不导出，已有32条回执上限不变。empty_content加入固定代码白名单，不再退化为other，不据此推断本次为空白正文。

回归覆盖真实JSON解析诊断到摘要的语法、额外内容、多余括号、重复键、非有限数字路径，范围边界/巨整数/布尔等污染负例及其他失败代码不附带JSON诊断。原普通HTTP/SSE两次尝试集成断言扩展为精确新字段，保留请求不变、JSON mode、调用数和严格失败/成功判定。此次只有诊断投影；请求、schema、批准文件集合、重试次数、时间及费用预算没有变化。本地PG生命周期诊断一并保留，未推送或发起新实测。

验证：相关JSON诊断、HTTP/SSE、预算保护、PG内存诊断及原主回执回归361项通过；完整55文件工作流集合保留RND_REQUIRE_NODE_TESTS/LANDLOCK/SECCOMP_BPF=1，2542通过、5个既有本地Landlock返回78失败、13个工具树/Vite或数据库条件跳过。Ruff、diff及两套生成文档一致性检查通过。普通矩阵38154312075尚未终态时不报告发布封定SHA，不自行推送或派发。

### mini-SWE submit检查点与同会话有界修复（仅本地）

e45f普通CI最终10/10成功。父线程核验第17轮真实38159272888/artifact11710751147：3次预留/3次HTTP尝试/2次响应，仅一次read_timeout；最终节点健康验收失败，backend exit3、lifespan提示、HTTP502、未报告启动完成、exception_hint=other、output_hints为空，checks=0、restart=false、cleanup=deleted，无双模块ZIP。该轮没有JSON失败证据，不沿用旧JSON或PermissionError归因。候选按既定清理删除，不能恢复或猜测源码。消费者合同要求应用初始化新库，基线lifespan查询users；这是明确合同提示的依据，不是本轮遗漏初始化的根因证明。

确认并修复的功能缺口：手动SLA流程此前在run_agent结束后才独立验收，失败直接由ledger拒绝；worker编辑只收到pending，submit立即退出，失败不返回agent。现保留原edit/submit schema，将submit作为平台检查点：对平台当前候选调用原独立隔离验证器，业务失败返回submitted=false，平台把有限verification_feedback加入下一次模型请求；worker消息历史不能覆盖请求、反馈或权限。成功才结束worker，但agent-result仍implementation_verified=false；原节点独立验证/ledger晋升，以及ZIP新目录冷启、重启、HTTP/浏览器/物理数据库oracle均保留，内部通过不能替代最终验收。

只允许受信任验证器明确标记的application_startup或business_assertion反馈。启动分类仅接受实际exit1或exit3、import/lifespan阶段、未报告完成且没有权限/资源/依赖等基础设施提示；HTTP断言仅在有界传输完成后由专用BusinessCheckFailure标记，浏览器仅assertion阶段可标记。传输、隔离、环境、检查超时、清理或预算错误直接停止。反馈仅含固定类别、批准场景ID、候选摘要及重新过滤的既有安全启动字段；不发送原始异常、输出、路径或指令，不授予shell、文件、依赖或验收器权限。

检查使用一次性nonce、完整任务摘要、源码摘要、计划摘要和node范围绑定；清理必须deleted，实际容器与执行隔离守卫仍执行。内部成功还必须通过原require_evidence全部条件。worker动作必须与平台刚返回的模型动作完全一致；每次编辑前像以当前候选为准，重复提交未改变的失败候选被拒绝。提交后的沙箱快照须与已检查的完整候选对应，不能替换或串模块。最终返回的edits仍相对原始已验证前驱生成。原预算日志已存在时拒绝重建会话，生产dispatcher最终节点/汇总否决也不能通过外层修复路由重新分配mini-SWE预算。

步骤/请求/token/费用上限未增加：每模块最多8步、2M token、180秒，全局32次模型HTTP请求；一次模型轮次仍预留两次网关尝试。真实40000字符上下文的保守token预留可能早于8步耗尽，这是原有更严格边界。模型、内部检查及清理共享同一模块时间窗，不重新设定deadline。预留15秒用于worker和文件沙箱收尾，检查子进程在自己的剩余窗内再保留10秒清理；专用验证进程用SIGUSR1 watchdog中断工作，独立于锁定SDK占用的SIGALRM；BaseException逃出普通异常处理，父进程仍按原截止时间强制停止验证进程。原finally负责清理，删除后必须查询得到SDK类型化404才可确认不存在。截止或删除未确认不返回可修复反馈。文件SDK超时按剩余时间向下取整数，保留0.190下载方法的整数位置参数重载。文件沙箱清理由独立子进程执行，父进程用原模块deadline限制运行并独占终态回执。若既有SDK操作超时越界，仍进行一次截止为当前时刻加1秒的紧急删除尝试，到点杀止子进程；启动、调度及回收并非硬实时，不能宣称完整清理往返最多1秒。该路径保留unconfirmed，超出180秒的结果一律拒绝，不能取得额外工作/修复机会。agent-result仅在文件沙箱清理完成且总耗时未超限后写入，记录检查次数、已检查源码摘要及总耗时。

明确边界：内部检查复用完整节点验证，会消耗真实隔离准备、健康及业务检查时间。本轮没有派发或进行新的真实计时，不能承诺180秒必有第二次修复机会，也没有证据据此申请更大预算；时间不足时保留失败。专用截止路径要求支持POSIX SIGUSR1且运行于专用进程主线程的控制端，缺失时失败，不静默使用不受限替代。用户第二次环境断开通知后已在原workspace实际验证读写和Python执行恢复，未换环境绕过限制。

离线证据：新增真实锁定Python3.12 worker闭环用例覆盖失败→安全反馈→同候选修复→内部通过、持续失败耗尽、重复提交、快照漂移、越界/前像冲突、陈旧/串模块回执、伪造通过及反馈污染；同时覆盖检查/清理耗时计入模块期限、真实计时器中断、原验证器超时处理与删除失败、SDK整数重载及最终ledger/dispatcher否决。新用例加入已有Ubuntu production-v2普通CI，不新增workflow或手动dispatch。相关回归893项通过，包括原真实Worker/API/ZIP/重启的人工夹具；这不是新真实模型验收或真实隔离证明。

最终完整55文件工作流集合保留RND_REQUIRE_NODE_TESTS/LANDLOCK/SECCOMP_BPF=1：2542通过、5个既有本地Landlock返回78失败、13个工具树/Vite或数据库条件跳过；未降低强制条件。最后清理计时路径及相关启动回归175项通过，并再次完成893项相关集合。Ruff、diff、完整手册及775份教材一致性检查通过。本轮不推送、不派发真实测试；待父线程评审后决定发布。


### 截止与清理封版审查修正（仍仅本地）

本地ef016503的独立审查发现两项阻塞：Daytona0.190的真实with_timeout在主线程使用SIGALRM并会清掉外部setitimer，因此旧软截止不能保证清理余量；另一个分类条件会把无基础设施提示的137/143退出当成application_startup。两项均须修正后再交父线程封版审查，ef016503本身不能发布。真实SDK非主线程timeout=1包裹time.sleep(1.25)的无网络回归还证明它不能及时打断C阻塞，故取消“SDK参数1秒就是完整清理硬上限”的表述。

新版用独立SIGUSR1与父进程原deadline形成两层截止；回归同时复现旧SIGALRM清零，并在真实SDK正常返回和阻塞调用中检验新截止及finally清理。137/143、非1/3退出和资源/外部终止提示均停止，不作为可修复业务失败；不能据137直接断言OOM。检查子进程被杀、非零返回或晚到时，父进程冻结passed=false/cleanup=unconfirmed并清除repairable_failure，不能残留晚到成功回执。

文件清理子进程只能按平台创建时的随机名称及已知ID取回原沙箱，两者不符时拒绝删除；创建结果未知时只尝试该随机名称且终态仍unconfirmed。父进程只接受当前task/plan/source/nonce的及时确认，不接受其他候选或晚到回执。source是将要上传的候选摘要，在写入前绑定，部分上传失败时不宣称观察到完整远端源码。删除API返回不足以确认完成，必须在截止前查询得到类型化DaytonaNotFoundError；仍存在、网络错误或截止均不得标deleted。SDK子进程不能写父进程的journal，因此晚到返回不能升级失败状态。

agent-cleanup.json及最多8个内部检查回执在现有summary中保留固定字段、任务/计划/候选/nonce与平台随机名称；临时源码删除前重新验证绑定。无效、缺失、污染或读失败清理均明确标unconfirmed，诊断不得掩盖原错误。不导出SDK对象、ID、原始异常/正文/路径、密钥或额外artifact。真实锁定SDK与独立子进程的离线边界回归不是实际Daytona删除或新真实模型成功证据。预算、原独立验收、隔离/权限及只读依赖政策未放宽；没有推送或派发。

修正后的最终本地证据：相关12文件947项通过；完整55文件工作流集合仍保留三项强制环境标记，2542通过、5个既有本地Landlock返回78失败、13个既有条件跳过。为适配真实删除确认，旧的离线SDK夹具增加类型化404返回，未放宽生产判断；相关203项夹具回归通过。Ruff全仓检查及格式检查、diff和完整手册/777份教材一致性检查通过。锁定SDK回归覆盖清理期间原硬截止，另以真实子进程验证提前写入passed=true的检查结果会在超时后被父进程冻结为失败。两项审查阻塞的本地修复已完成，仍须父线程封版审查；未进行新的真实模型、Daytona删除、推送或dispatch。


### 独立累计审查后的编码生命周期监督（仅本地，待复审）

独立审查代理针对e45f0fd..0cdcafde累计实现另发现两项阻塞，0cdcafde未发布：编码控制面refresh_data没有SDK timeout，旧路径可在17秒截止后仍阻塞且未进入清理；preview代理502/503/504被通用HTTP状态断言标为BusinessCheckFailure。独立Event阻塞与MockTransport复现已先证明这两条失败路径，不能把此前作者自检称为独立审查通过。

生产coding_environment现为父进程监督的文件RPC会话，create、refresh、容器准入、初始上传、后续写入和快照均在独立SDK进程内执行。父进程在创建前固定随机沙箱名及任务/计划/候选/nonce回执，读取子进程创建事件后才绑定ID；到原模块deadline减15秒即停止SDK进程，剩余原窗口只用于原沙箱删除确认。watchdog独立于模型/检查等待，控制器空闲时也执行停止与清理。正常结束同样先回收SDK进程，让操作系统释放其连接，再由原监督删除路径确认typed404；不存在父线程直接阻塞SDK refresh的生产路径。创建回执丢失、迟到或名字/ID绑定不明均不能升级为已删；原模块deadline来自run_agent入口，不因初始化另起窗口。

RPC仅支持批准业务文件的write/snapshot，不增加命令、文件权限、模型请求、步骤或时间预算；新进程只接收必要Daytona配置，模型密钥不传入。工作进程不能写父清理journal，晚到创建/响应在closing之后拒绝。结束阶段可以在截止后等待已被kill子进程的有界回收，不提供额外SDK工作或候选接受窗口；操作系统调度和文件系统并非硬实时。_local_environment仅为受监督工作进程内部实现及离线准入夹具使用，既有生产入口不再直接执行它。

无来源确认的502/503/504现在一律为普通CheckFailure，甚至不能因场景预期相同状态而静默接受；因此不会被标记business_assertion或反馈给模型修复。其他业务断言仍须有界传输完成及原隔离、任务/计划/源码/nonce和清理条件，最终独立oracle不变。

新增回归用真实子进程、Event阻塞及真实SDK refresh/生成API/响应解析的无网络路径，覆盖create、refresh、write、snapshot、控制器空闲和正常结束；初始25秒窗口包含进程加载，10秒工作截止后进入原15秒清理保留（较短离线窗口在并行文档生成负载下会先耗于导入，测试明确留出加载余量，生产上限不变），未扩180秒上限。未知create保留unconfirmed，已知ID精确传入清理，部分写入仍绑定预期候选。清理自身的真实SDK阻塞/硬kill及晚到状态沿用既有回归；不使用mock成功代替实际清理证明。MockTransport确认三个网关状态均不可业务修复。修复完成后交同一独立审查者复核新SHA累计diff，仍无推送、真实外部服务或dispatch。

本次本地验证：相关12文件956项通过，最终进程组终止/网关状态边界9项通过；SDK监督进程在回收leader前终止整个自有进程组，离线子进程用例确认阻塞检查后代不继续运行。严格55文件集合2542通过、5个既有本地Landlock返回78失败、13个既有条件跳过；未降低强制标记。全仓Ruff及格式、diff、完整手册与779份教材一致性检查通过。上述为作者实现验证，独立复审结论另行交父线程，不提前宣称通过。

### 第18轮的准入传播及Windows回收修复（本地验证，未重新派发）

父线程实际读取94f21e1的真实运行38167848595/artifact11713775823：模型预留/HTTP尝试/响应均为0、checkpoint为空，agent_controller报UnsupportedScope，sla-api文件沙箱清理为unconfirmed/deletion_unconfirmed。本轮没有进入模型闭环，也没有沙箱已删除证明。正式job114554037314的always Compose down步骤成功，19:42:30—19:42:42 UTC日志明确记录10个Compose容器及2个网络Removed；该命令不删除持久卷。这只能证明此次本地测试部署停止，不能替代具体agent沙箱的typed404确认或把既有unconfirmed回执升级为deleted。

代码检查及真实file_session入口离线回归确认：94f21e1新SDK子进程使用clean_env()，漏传了已验证的浏览器策略Actions scope。现仅复用verifier_policy_environment()返回的既有字段；它在创建子进程前再次验证，子进程准入仍调用原策略选择器和浏览器回执检查。没有修改策略白名单、首次dispatch、三个SHA相等、job/scenario或权限限制；API_KEY、GITHUB_TOKEN和代理环境不随该scope转发。正例真实运行Session→file_session.main→_local_environment→浏览器准入，受控客户端哨兵在准入后终止；负例删除策略或修改SHA、job、scenario、策略摘要时停在准入之前。这是scope传播证明，不是容器隔离或模型验收。旧真实子进程没有阶段诊断，故不能声称已证明上述遗漏是第18轮唯一失败原因。

新增诊断只投影固定阶段和异常类型，不导出SDK消息、路径、密钥或原始HTTP正文。父进程保留create_unconfirmed、module_deadline等原有清理原因，另记file SDK失败阶段和cleanup子进程失败类型；诊断不能升级清理状态。真实锁定SDK的离线HTTP运输替身验证DELETE后的200→404最终一致性、一直200、403、500和迟到404：只有截止前类型化404可确认删除。readonly_dependency_admission夹具补齐相同get→DaytonaNotFoundError接口，原deleted断言及unknown/delete-failed负例保留。

普通Python CI运行38167704467的Windows shard3真实报告refresh生命周期28.008秒，违反原14秒断言。原因是仅kill根进程后，检查后代仍持有stdout，读线程和管道close不能及时返回。Windows现在在发送工作前把SDK子进程加入自有Job Object，使用KILL_ON_JOB_CLOSE及TerminateJobObject回收该进程树；创建、配置或归属失败时不发送工作并失败关闭。不使用全局进程名扫描或提权。读线程join和管道close各有独立0.2秒回收界限。原25秒测试窗口、14秒断言、180秒生产deadline及15秒清理预留均不变。Job Object API合约与管道阻塞测试可在本机执行；新增原生Windows后代终止证明在Linux明确跳过，真实Windows是否修复仍须后续普通CI验证，不能提前宣称通过。

Windows接口依据Microsoft官方文档：[TerminateJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject)、[AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject)及[JOBOBJECT_EXTENDED_LIMIT_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)。本轮保持原模型预算、隔离策略、独立最终oracle及失败关闭标准；旧CI结束前不推送、不取消、不重跑。

独立审查e384194另复现一项P2：reader或pipe本地回收失败时，已回收SDK进程且仍有14.8秒清理预算，却跳过已知沙箱删除。该版本未推送。修复把本地回收和远端删除错误分开处理，先尝试Windows Job关闭，再无论本地回收结果如何都按原deadline调用owned cleanup；保留首次错误，最终仍拒绝候选及保持unconfirmed。两个故障注入回归要求原沙箱ID及原deadline恰好传入一次删除，即使删除替身写入成功回执，本地回收失败也不能因此晋升为正常成功。此项修复须再交同一独立审查者确认，不把作者测试等同独立复审。

### 第19轮进展、Windows夹具定位与安全计时（本地，未新增外部运行）

父线程及监控正式读取9c0e223真实运行38172191014/artifact11714534217：模型预留/HTTP尝试/响应4/4/2，两个失败回执均read_timeout，最终ModelFailure/model_gateway:349。sla-api有一次绑定有效的checkpoint，backend_health=true、checks_count=1、passed=true、cleanup=deleted；节点验证同样通过1项检查。sla-dashboard没有checkpoint，两个agent文件沙箱均deleted/confirmed_absent。完整双模块ZIP仍未通过，也没有失败→反馈→修复闭环已经发生的证据。browser_count=0、obligation_checks=0、restarted=false不能误写为浏览器或重启验收通过。

实际job日志只给出完整执行阶段20:47:50.3739319—20:51:25.4595140 UTC，约215.086秒，包含两模块、节点验证及清理，不能作为dashboard单请求耗时。旧summary没有elapsed/duration/deadline字段。当前live网关明确非流式，SDK max_retries=0，平台每轮最多两次尝试及首次失败后0.2秒等待；实际llm_timeout=min(60,(原模块remaining−15−1)/2)。两次尝试共享本轮选定timeout，原180秒模块及15秒清理保留不变。4次尝试仅2个response对象，不证明服务商内部故障。固定基础输入离线测量为task约407/428字符、schema1068、baseline1497、app.py8483字符；真实API修改后的候选已清理，这不是实际dashboard请求长度。现无证据断定原预算物理不足，也不据此删需求或盲目增加超时。

新增诊断只记录数值和固定task枚举：每轮起始模块/工作剩余时间、实际选定timeout、结束剩余与超窗秒数、payload字符数、HTTP计数前后及轮次耗时；每次HTTP记录序号、完整请求body字节数、传输实际read timeout、收到response headers耗时、传输完成/失败耗时和已读取响应字节数。headers未收到保留null。HTTP耗时止于body迭代完成/失败或关闭，不冒充模型服务内部生成时间；完整模型轮次另行计时。最多8轮/模块、32个HTTP计时记录，非法/超范围数字转null，额外字段丢弃；不保存模型文本、请求内容、凭据或headers。诊断不能授权候选、延长截止或增加重试，仍为非流式。直接改streaming可能改变read timeout的间隔语义，不能把它当作无条件修复或隐式扩窗；后续只根据实际计时再提出最小方案。

Windows普通CI38172056666的checkpoint失败已由正式JUnit11714728237确认：communicate在约0.47665秒截止后，stop_process内wait(timeout=15)再超时，总测试15.613秒。源码发现测试夹具替换了共享subprocess.Popen，所有命令都被改成sleep30的验证器，包括生产stop_process调用的taskkill。因此本次只让夹具拦截准确verifier启动命令，其他命令原样透传，并验证Windows确实调用taskkill；不修改生产15秒回收等待、不降低冻结早到成功回执的要求。

另一Windows idle的正式JUnit11715057043经SHA256核对一致，测试耗时12.638秒，只有原第1122行unconfirmed!=deleted断言，没有底层错误或安全locals；不能借上述taskkill夹具缺陷解释。独立诊断用真实watchdog/finish时序及子进程，证明reader、pipe、Job terminate或Job close不同错误都能满足已有“<14秒、已知ID、删除替身调用一次、进程已回收”断言而最终unconfirmed；Linux原idle测试10.33秒通过。当前没有该Windows实例的首次父回收错误，故不猜0.2秒过紧，也不声称idle根因已修。父回执现附固定supervision_failure_phase/kind，保留首次错误及journal读取/绑定异常阶段；测试失败消息只显示这些固定诊断字段和原因，便于后续Windows证据归因。原14秒断言、0.2秒回收界限、typed404标准、Linux终止行为及unconfirmed拒绝均不变。

### 默认关闭的原生 strict 兼容性试跑

`mini_swe_output_mode=json_schema` 使用锁定的 LangChain/OpenAI SDK 序列化 `ApprovedAgentTurn`，仅允许现有 `sla-api` / `sla-dashboard` 非流式调用。版本与本地审核组合不同则以 `native_sdk_unsupported` 停止；不绕过锁文件、不更换端点、不切换工具调用或 JSON mode。此改动仅有本地 HTTP mock 回归证据，尚未证明真实端点支持 strict。

SDK/范围预检在读取缓存之前执行，旧缓存不能绕过版本不匹配；实际 wire Schema 和审核 SDK 版本也纳入缓存身份。native 与 JSON mode 缓存分开。预检失败不预留或发送模型调用，回执 `attempt:null`。

发送前核对实际 HTTP 的精确目标、模型、response_format/schema/strict、非流式、无工具及 8192 输出上限；完整请求体（含新增 Schema）必须落在原 `4 × MAX_CONTEXT_CHARS` 的输入预留内。返回内容先经过拒绝、完成状态、大小及严格 JSON 检查，再按实际发送的 wire Schema 校验，之后仍执行原 Pydantic 业务约束、批准文件完整清单、preimage、checkpoint 和最终独立验收。SDK 将可空字段变为必填：`submit` 必须带 `edits:null`，新文件必须带 `before_sha256:null`，不能靠客户端默认值补齐。

出站不匹配以 `native_request_mismatch` 在网络前停止；HTTP 400/422 以 `native_format_rejected` 在首个响应后停止，安全回执仅保留数字 HTTP 状态；违反 wire Schema 以 `native_schema_violation` 在首个响应后停止。不得删去服务端不支持的约束或自动重试兼容性格式。HTTP 500/超时及本地业务纠错仍受原每轮最多两次约束；没有第三次回退。每模块 8 步、200 万 token、180 秒、总计 32 次调用及原费用边界全部不变。

受控试跑须另行明确授权，绑定已审查完整 SHA、现有 `rnd` 配置、同 Job 隔离前置证明及原预算。回执分别保留 `native_strict_requested`、`native_request_verified`、`native_local_conformant`，并始终将 `native_provider_enforcement` 标为 `unknown`。HTTP 200 且本地合规只能证明该请求被接受且该响应通过本地校验，不能区分服务端执行 strict 与静默忽略后偶然输出合规 JSON；也不能代替业务验收通过。

### 第21轮之后的传输阶段诊断

父线程提供的第21轮记录显示：API两次HTTP200且本地native Schema合规；dashboard两次60秒read_timeout，均未收到headers/body。本轮120.5592秒后仍有54.3405秒模块预算，overrun为0，不能归因为180秒模块耗尽。API/dashboard使用相同wire Schema和调用策略；实际初始payload相差1379字符、完整请求体相差1486字节，现有证据不能据此解释延迟，也不能证明服务商内部故障或strict执行。

新增可选http_trace仅记录connect、TLS、发送headers、发送body、等待response headers五个固定阶段的started/complete/failed相对秒数、最多64个事件计数及固定失败阶段。最多32次HTTP记录；投影拒绝非有限、负数、布尔及越界值，不记录trace info、headers、地址、异常或正文。保留并透传原trace hook及其异常，成功或失败都恢复原extensions，响应body仍惰性读取。无事件意味着诊断不可用，不能把缺少connect事件单独当作连接复用证明。

离线验证保留锁定SDK、真实HTTPTransport、连接池与HTTP/1.1解析，只替换网络backend并禁止外部网络。覆盖连接、TLS、上传、等待headers失败，严格Schema拒绝及原两次尝试上限；等待headers超时后，真实连接池关闭失败连接，下一次使用新连接。独立审查补测三种原hook状态与各失败阶段，确认恢复、正文不变和连接关闭。此证据不能追溯确定第21轮实际失败阶段。

下一轮沿用已授权mini-swe-sla/json_schema、精确审查SHA和原rnd/TLS/nocharge/隔离前置证明，收集固定阶段回执。所有步骤、调用、token、时间及文件/oracle边界不变；无格式回退或新增重试。read timeout是单次网络操作的等待界限，不是整个响应的绝对墙钟截止；现有SSE循环尚未证明端到端硬截止，因此本次不切流式。API局部通过仍不能代替双模块候选及最终独立验收。
