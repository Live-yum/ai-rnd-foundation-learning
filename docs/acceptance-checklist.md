# 功能与验收对照清单

本清单说明每项要求落在哪段实现、应由什么证据验收；它不是预先签字的“全部通过”报告。实际结论必须核对同一提交的测试输出和Actions。`passed`、`failed`、`pending`、`skipped`与“未运行”分别记录；失败或未运行不能写成通过。

| 要求 | 主要实现 | 应核对的测试或真实证据 |
|---|---|---|
| Python3.14、uv精确安装；Windows/Linux可运行基础平台 | `pyproject.toml`、`uv.lock`、`.python-version` | `test.yml`的双系统tests与clean-install；记录实际解释器版本 |
| 从空目录完成全功能，不要求本项目骨架 | 唯一完整手册、`build_handbook.py`、`rebuild_from_handbook.py` | `test_handbook*`、`test_learning_order`；handbook-only从书还原、重建第三方归档、重建Continue并跑回归 |
| 只保留一份完整教材，源码与讲解同步 | `docs/`正文、`handbook_notes.py`、固定输出文件名 | `build_handbook --check`；源码块SHA、全文件比对与重建相等；无_v3正式副本 |
| 单模型只填三项，需求/规划/编码/审阅可分别选模型 | `settings.py`、`llm.py`、`.env.example` | `test_guided_models`、`test_llm`；换服务不继承错误密钥；真实供应商配置另验 |
| 人工多轮澄清，不用固定少量问答截断 | `conversation.py`、`flow.py`、`store.py` | `test_guided_workflow`、`test_guided_completion`；轮数/预算/已确认事实保留 |
| 一次智能推荐继续后续关卡，不能降低原需求 | `recommendation.py`、`flow.py`、`runtime.py` | `test_recommendation_recovery`、`test_recommendation_stage_budget`；澄清与设计分别有界修正，保留实际阻塞 |
| 已确认字段、长度、必填、枚举、搜索筛选与数据归属不丢失 | `domain.FieldRequirement`、`RequirementChange`、`requirement_coverage.py` | `test_requirement_coverage`；引用当前用户更正才能覆盖事实；计划漏项不能进入生成 |
| 先选后端/前端/数据库再输入需求 | `catalog.py`、API与网页选择器 | `test_guided_selection`、`ci_guided_browser`；拒绝未适配组合 |
| 基础产品真实CRUD、认证、逐用户隔离、字段/日期/枚举校验、搜索组合筛选 | `templates/product/`、`templates/frontends/`、`generator.py` | `test_news_delivery`、`test_guided_postgres`；产品HTTP与真实逐规格浏览器报告 |
| 每个带界面产品必须真实浏览器验收，不以示例截图替代 | `verify.py`、`verify-browser.cjs`、`verification.require_browser_evidence` | `test_product_browser_gate`；当前实体/字段完整checks、零页面错误，缺Node/Chromium失败；api-only才不适用 |
| 独立ZIP可从新目录、新依赖环境和新库启动 | `verification.package_basic`、`portable.py`、`templates/deployment/` | clean-install、native-runtime及handbook-only；独立解压复验不能导入平台业务目录 |
| FastapiAdmin原生模块/菜单/角色/前端，保留框架而非另造假页面 | `native_modules.py`、`native_environment.py`、`native_lab.py` | `ci_native_bundled fastapiadmin`；实际生成器、PG/Redis、Vue编译/类型/CRUD/RBAC/浏览器/新库启动 |
| 芋道Java后端+Vben原生前端及完整独立交付 | `native_vben.py`、原生模块与portable启动器 | `ci_native_bundled yudao-vben`；真实JDK/Maven/pnpm、后端、类型/构建、菜单权限和浏览器 |
| Tree-sitter本机语法解析及真实行号 | `symbols.py`、`knowledge.py` | `test_toolchain`与`ci_toolchain`；固定Java/TS/JS grammar、Vue script偏移、缓存/过期拒绝 |
| 本机源码检索与Repo Map | `retrieval.py`、`toolchain.py`、可选Aider Repo Map | `ci_toolchain`；来源指纹、片段行号、范围与预算；不把文件名当语法解析 |
| 实际Continue全文组件+本机MCP接入 | `continue_index.py`、固定上游TS、Node host/runner、`context_mcp.py` | `test_continue_index`、`ci_toolchain`；实际update/retrieve、FTS库、只读MCP；不声称完整复制IDE生命周期 |
| 本机真实向量权重和混合检索 | `tools/embeddings/`、`ci_local_embeddings.py`、`retrieval.py` | local-embeddings工作流；固定ONNX/Tokenizer、CPU推理、三份真实Vben源码、Continue+AST+FTS+vector RRF、缓存/过期/范围测试 |
| 实际Plop创建受信任业务文件并接入原生表单 | `scaffolding.py`、`tools/node/plop-runner.mjs`与模板 | `test_native_tools`、`ci_native_tools`；实际node-plop版本/动作及生成文件指纹 |
| 实际Aider本机应用补丁与失败修复 | `aider_tool.py`、`native_coding.py`、独立Python3.12环境 | `ci_toolchain`、`ci_native_tools`；错误规则被真实反例拒绝、回滚、随后修复；不改鉴权/依赖锁/测试 |
| 原生失败可在安全阶段恢复，不损坏已有生成现场 | `native_recovery.py`、`native_lab.py`、`owned_lifecycle.py` | `test_native_recovery`、`ci_native_tools`两次真实中断；同Plan/源码/数据库身份、权限重试自有随机账号、检查点不匹配失败 |
| Daytona0.190.0控制面与执行器全部本机 | `daytona_local.py`、`daytona_build.py`、bootstrap及Dockerfile | daytona-local；固定源码/Runner身份、本机Dex/Registry/MinIO、API与Runner真实启动；不是仅SDK安装 |
| Daytona覆盖SQLite及全部已登记PostgreSQL模板组合 | `daytona_profiles.py`、matrix镜像/探针、`sandbox.py` | daytona-local + native-toolchain-daytona三行矩阵；禁外网、新库、完整运行/浏览器/重启及删除回执 |
| 只有大模型推理允许外部服务，其余工具本机执行 | `local_only.py`、受控工具入口、只读MCP、禁网适配器 | `test_local_only`、`test_aider_offline`、真实沙箱与embedding报告；依赖准备下载与业务运行分开 |
| 失败、缺失证据、不支持需求不能交付 | `flow.py`、`verification.py`、`native_delivery.py`、严格报告合同 | `test_delivery_clearance`、browser gate、Daytona matrix合同；智能模式也不能绕过 |

## 明确的能力范围

- 原生框架自动编码针对已批准的单记录布尔业务规则；路径、类、导入、权限、数据库配置、依赖与测试不交给模型任意改写。它不是任意跨模块业务的开放式Java/Vue开发器
- 支付、外部采集、跨实体事务及未登记的模板/数据库组合，必须明确报告未支持。智能推荐可补齐普通细节，不能抹掉用户已经明确要求的功能
- 原生恢复针对完整、身份一致且程序明确标记可恢复的检查点。不可重放生成中途硬终止、现场被改或检查点缺失时保留现场等待检查，不宣称任意崩溃都能自动恢复
- 向量证据是三份固定Vben源码的真实权重融合验证，不是全模板语义召回率或中文准确率认证；更多源码范围需要显式预算与进一步评估
- 上游Daytona开发Runner使用privileged DinD，只用于拥有权限的本机开发环境，不作为恶意代码生产级强隔离承诺

## 怎样区分夹具和真实执行

正式CI中的聊天模型通常是明确的固定响应夹具，它验证流程如何处理计划、失败反馈与修复。Aider、Plop、Tree-sitter、Continue、数据库、编译器、浏览器、Daytona和本机向量权重是否真实执行，要看各自脚本及报告，不能由“模型是夹具”推断所有工具都是模拟，也不能反过来声称真实服务商已经验收。

提交验收结论时记录完整commit SHA、工作流/作业链接和对应报告；未结束的矩阵保留pending，失败写出失败层及日志。只有对应要求的真实检查在该提交通过，才把该项标为通过。本文不提前写入最终CI状态，避免后续源码改变后留下过期的“全绿”承诺。

## 所选模板的页面风格

原生模板的页面必须由对应原生生成器生成并挂载到原管理端。FastapiAdmin保留原生Vue布局、Fa组件和Element Plus；芋道保留Vben5 web-antd布局、Ant Design Vue和VXE。不得替换成Python Basic通用页面。

`workbench/native_style.py`逐文件比对原模板布局、主题、核心设计源码的SHA，并用Tree-sitter核对每个生成页面的原生组件及导入。`scripts/native_browser.cjs`在实际生成路由检查侧栏、顶栏、原生表格/按钮/表单和主题变量，并保存表格与编辑对话框截图；修改布局主题或用通用页面替代会阻止交付。`tests/test_native_style.py`包含缺组件、改主题、替换布局的失败反例。截图和浏览器证据必须来自当前提交的Native/Daytona工作流，不沿用旧截图冒充新提交验收。
