# docs/workbench-layout.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本教材正文的源文件。** 上文正文就是这些源文件拼接后的内容。它们也收录在附录中，使从教材还原出的项目能再次生成逐字一致的完整教材，而不是只有一次性的代码快照。

**对应关系：** scripts/build_handbook.py的GUIDES → 正文 → 完整源码附录。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `docs/workbench-layout.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L70。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6931`。本段原文以LF换行结束。

<!-- learning-source: {"path": "docs/workbench-layout.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fca1e9889fbf6495cfa3c3f90695f0f3e7f41cb14b46fc93a0f2869a870058ea"} -->
````markdown
<!-- docs/workbench-layout.md -->
# workbench 功能目录与兼容边界

本轮把实现放进按职责划分的 Python 包，保留已有业务、审批、恢复和验收语义。目录迁移不等于扩大产品能力，也不证明真实模型、Daytona 或生产部署已通过。

## 目录职责

以下路径均相对 `workbench/`：

- `core/`：稳定输入、需求及产品合同。
- `projects/`：项目、运行、作业、审批和步骤的持久化模型，不改变表结构。
- `requirements/`：对话、实体需求、来源账本、规范化、覆盖、意图与澄清。
- `models/`：模型设置、连接、发现、协议与诊断；模型调用网关仍在基础设施层。
- `knowledge_services/`：索引、检索、符号、Continue 索引和 MCP 上下文服务。
- `templates/`：模板目录、适配合同、版本化规范、上游资源及脚手架。
- `planning/`：FeatureDesign、能力任务合同、规则、推荐、依赖图与版本合同。
- `specifications/`：规格产物、验证及固定 OpenSpec CLI，不执行产品工作流。
- `coding/`：有界编辑、候选、差异守卫、Aider 和 mini-SWE 执行端口。
- `production/`：工作流图、状态、分派、Worker 与候选版本晋升。
- `business/`：业务合同、能力、Python/FastapiAdmin/Yudao 适配、结构回执与业务探针；`modules/` 保存已批准的确定性业务模块。
- `generation/`：基础 Python、产品 SQL 和 `native/` 原生栈生成，包括 schema、前端、模块、样式、Vben 和导航。
- `acceptance/`：基础/原生/业务/便携产品验证、能力沙箱、数据库实验及独立证据。成功候选不能替代验收。
- `delivery/`：原生交付、便携包及恢复，不新增部署动作。
- `extensions/`：扩展消费者、策略、准入、义务、服务、技术栈与独立 oracle。
- `infrastructure/persistence/`：事务与存储；`llm/`：模型网关；`processes/`：受控进程工具与生命周期；`native/`：本机环境、端口、资源。
- `infrastructure/sandbox/`：执行、隔离、依赖、诊断及启动边界；`browser/`：浏览器策略与隔离；`daytona/`：固定 profile、会话、Worker、验证和诊断。
- `interfaces/`：HTTP、CLI、事件流和工具链入口。
- `_compat/`：精确旧模块名映射与惰性导入注册，不保存第二份业务实现。
- `web/`：已构建的操作台静态资源；前端源码仍在仓库 `ui/`。

编排调用领域合同，领域合同不依赖 production；业务、生成和验收各自保留真实职责，不通过兼容层复制实现。

## 根目录的 8 个 Python 文件

`workbench/` 根只保留 `__init__.py`、`errors.py`、`filesystem.py`、`local_only.py`、`settings.py`、`cli.py`、`capability_sandbox.py`、`daytona_worker.py`。

前五个分别提供包初始化、公共错误、受控文件工具、遥测关闭和稳定配置。`workbench.settings.ROOT` 仍表示同一个仓库或安装资源根；移动实现不能改写 ROOT，也不能把资源定位改为新模块的父目录。

后三个是必须保留物理文件的命令入口：

- `python -m workbench.cli`，以及已有 `rnd = workbench.cli:app`。
- `python -m workbench.capability_sandbox`。
- `python -m workbench.daytona_worker`。

入口转交唯一功能实现；作为普通模块导入时仍保留同对象兼容，不能用只有导入别名而无物理入口的方案破坏 `python -m`。

## 旧接口：同对象、惰性兼容

例如 `workbench.store` 与 `workbench.infrastructure.persistence.store`、`workbench.api` 与 `workbench.interfaces.http` 指向同一个模块对象，旧 monkeypatch 和新路径调用共享状态。`_compat/aliases.py` 维护明确的一对一映射，`_compat/__init__.py` 按需加载目标并注册到 `sys.modules`；不使用通配扫描，也不在导入 workbench 时批量加载实现。

包启动只关闭继承的托管遥测并安装导入兼容器，不创建数据库、启动服务、调用模型或加载未来教材阶段。新增父包的 `__init__.py` 保持轻量。现有 `coding/__init__.py` 公开有界编辑接口，需要第07阶段实现，不能假装是第00阶段空壳。

## 教材与安全源码清单

每个迁移实现继续使用原来的教材阶段。兼容注册及轻量父包在第00阶段可用；第02阶段数据库课只恢复其真实依赖闭包，不能夹带第03阶段业务能力或未来 HTTP/Worker。业务源码收集使用 `workbench/business/**/*.py`，不再依赖已经空掉的根级 `business*.py`。

安全证据必须绑定精确安全源码清单：同时覆盖真正被执行的新实现、兼容入口/注册与相关启动和策略文件。路径移动或实现字节变化会使旧源码摘要失效，必须重新获得对应精确 head 的证据。不能只哈希根目录 shim、漏掉嵌套实现、改成目录名存在检查，或用宽泛 glob/动态导入来弱化受审查的固定清单。离线测试可检查清单完整性和失败关闭，不能替代真实隔离正反例、模型或业务验收。

## 本次本地验收与未覆盖边界

迁移基线为 main `2660e2ab708e4b93f08169938603c94eafd16c77`。目录改动以唯一实现及兼容性为主；额外明确修正是独立原生交付的 helper 闭包，包含新父包、兼容注册器、模板适配器及4份实际读取的规范资源，而不是复制整个平台。

2026-10-15 的本地验证：

- 205项目录/旧新导入身份、两个导入顺序、并发、monkeypatch、命令入口及序列化边界测试通过。
- 125项教材及独立早期课程还原测试通过；两套教材重新生成并通过一致性检查。独立交付在隔离目录中导入全部38个指定helper、拒绝平台专用依赖并运行启动器帮助命令。
- 前端77项测试、格式、类型检查和生产构建通过，提交的静态资源与基线一致。Python Ruff及格式检查通过。
- 广回归首次记录9415通过、31失败、194跳过。冻结文件后重跑31个失败项，8项通过，剩余23个浏览器前提相关失败在未改基线逐项复现。原始失败保留，不将其改写为全套通过；另6个初始SDK测试失败由环境SOCKS代理缺少可选依赖造成，使用同环境已有HTTP代理路由且测试自身禁止网络连接后通过，不改变SDK代码或安全规则。
- sdist和wheel离线构建成功，隔离wheel的核心旧别名、ROOT及静态资源检查通过。API导入在基线和新wheel中均因未打包`templates/standards/common.md`失败；这是既有wheel资源缺口，本次不宣称独立wheel全功能通过。

Linux离线证据不替代Windows、PostgreSQL、真实浏览器、原生服务、真实Daytona隔离或真实模型验收。当前缺失环境和可选工具的跳过仍保留；下一步需在最终提交上运行对应CI。没有通过修改断言、复用旧安全回执或扩大权限来消除阻塞。
````
