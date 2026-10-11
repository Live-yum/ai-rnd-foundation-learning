# docs/modular-production-v2.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本教材正文的源文件。** 上文正文就是这些源文件拼接后的内容。它们也收录在附录中，使从教材还原出的项目能再次生成逐字一致的完整教材，而不是只有一次性的代码快照。

**对应关系：** scripts/build_handbook.py的GUIDES → 正文 → 完整源码附录。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `docs/modular-production-v2.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L253。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`39941`。本段原文以LF换行结束。

<!-- learning-source: {"path": "docs/modular-production-v2.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4611ee1875961650c819d268e3b6e1c2a8c87de717c1a7dba631a72a0b366ad4"} -->
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
````
