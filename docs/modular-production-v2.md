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
