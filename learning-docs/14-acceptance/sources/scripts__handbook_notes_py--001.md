# scripts/handbook_notes.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：把源码变成逐文件教学提示。** 先按具体文件职责解释输入、调用方和结果，再解析Python AST列出类/函数、行号、参数、关键分支和返回。它不执行被讲解的业务代码；手写教学章节补充业务意图与练习。

**对应关系：** build_handbook → purpose/notes → 每个源码块前的对应关系。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `parse`（L661–L667）：接收`content`。 调用`re.sub`、`ast.parse`。 返回路径：L667的`ast.parse(normalized)`。
- `segment`（L670–L673）：接收`content`、`node`、`limit`。 调用`ast.get_source_segment`、`type`、`" ".join(value.split()).replace`、`" ".join`、`value.split`、`len`。 返回路径：L673的`value if len(value) <= limit else value[:limit] + "…"`。
- `definitions`（L676–L683）：接收`node`、`prefix`。 控制顺序：L677遍历`ast.iter_child_nodes(node)`；L678按`isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))`分支。 调用`ast.iter_child_nodes`、`isinstance`、`definitions`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `body_nodes`（L686–L691）：接收`node`。 控制顺序：L687遍历`ast.iter_child_nodes(node)`；L688按`isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))`分支。 调用`ast.iter_child_nodes`、`isinstance`、`body_nodes`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `purpose`（L694–L877）：接收`name`。 控制顺序：L696按`name == "workbench/__init__.py"`分支；L702按`name.startswith("workbench/") and path.stem in MODULES`分支；L704按`name.startswith("templates/business/")`分支；L705按`role := BUSINESS_FILES.get(name.removeprefix("templates/business/"))`分支；L712按`name == "examples/requirements/customer-service.md"`分支；L718按`name == "examples/requirements/customer-service-decisions.md"`分支；L724按`name == "examples/requirements/customer-service-contract.md"`分支；L730按`name.startswith("examples/")`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`name.startswith`、`BUSINESS_FILES.get`、`name.removeprefix`、`PRODUCT.get`、`name[:-3].replace`、`name.endswith`。 返回路径：L697的`( "包入口", "导入workbench时只关闭继承的托管遥测，不立即启动HTTP服务、创建数据库或调用模型。", "所有workbench子模块首先经过此入口；数据库初学步骤因…`；L703的`MODULES[path.stem]`；L706的`role`。
- `notes`（L880–L990）：接收`name`、`content`。 控制顺序：L884按`not name.endswith(".py")`分支；L891遍历`tree.body`；L892按`isinstance(node, ast.ImportFrom) and node.module`分支；L894按`isinstance(node, ast.Import)`分支；L897按`own`分支；L904按`not rows`分支；L907遍历`rows`；L909按`isinstance(node, ast.ClassDef)`分支。后续分支沿下方源码相同行号继续阅读。 调用`purpose`、`name.endswith`、`parse`、`isinstance`、`imports.append`、`imports.extend`、`sorted`、`set`、`i.startswith`等。 返回路径：L885的`out`；L889的`out + "此文件包含运行时专用语法；依照正文使用Python3.14，完整实现见下方源码。\n\n"`；L905的`out + "**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。\n\n"`。

</details>

**创建路径：** `scripts/handbook_notes.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L990。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`79763`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/handbook_notes.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e8a454df9246461fe2b58589ac432791696ef107e0284cd1344e0a2338a3242c"} -->
````python
# scripts/handbook_notes.py
"""Teaching notes tied to real source lines; no remote model or generated pseudo-code."""

import ast
import re
from pathlib import Path

# Each module has a distinct architectural job. These explanations accompany,
# rather than replace, the complete and SHA-checked source below them.
MODULES = {
    "requirement_sources": (
        "在规划前拒绝明确来源互相冲突的分析候选",
        "对能可靠定位的同一原子义务比较明确值，保留用户原文、已确认契约和模型候选来源；矛盾走已有有界分析纠错，不替用户选值或批准，未知旧文本仍保守校验。",
        "Workflow.analyse → 来源冲突诊断与需求账本 → 原有clarification关口；有效分析才进入设计。",
    ),
    "business_contracts": (
        "业务合同的类型和交叉校验",
        "将角色、资源、关联、状态、提醒与指标作为有限声明；检查实体/字段/角色引用、不可改系统字段和互相矛盾的权限，拒绝任意SQL或执行脚本。",
        "Plan.business → validate_plan → 各模板适配器与独立验收。",
    ),
    "business_capabilities": (
        "业务合同的可执行能力边界",
        "按实际模板及已实现适配判断合同是否能执行，不根据模型声称动态开启能力；未登记功能保留阻塞。",
        "选择器/规划门 → 合同检查 → 对应业务运行时。",
    ),
    "business_yudao": (
        "在真实Yudao生成物上挂载业务策略",
        "核对当前表名、权限、路由及生成文件身份，保留DO/Mapper/Service与原生Vben结构，将控制器全部交给统一事务策略；输出明确扩展DDL和可核查源清单，不执行用户SQL或重置数据。",
        "native_lab → install_native_business → install_yudao_business → Spring/MyBatis/Vben产物 → 显式SQL安装。",
    ),
    "business_fastapi": (
        "在真实FastapiAdmin产物上挂载业务策略",
        "保留框架认证与生成模型、补齐关系，保护原CRUD入口并挂载带行权限的业务接口和原生组件页面；注册仍走原生校验，之后事务性附加默认业务角色。",
        "native_lab → extend_business → module_business插件、Fa页面和扩展DDL。",
    ),
    "business_native": (
        "事务安装明确的原生业务扩展",
        "根据模板选适配器，再向已验证的专用本机库按顺序执行受信任扩展SQL；同一事务失败全部回滚，证据记录实际SQL哈希而非直接宣告运行成功。",
        "生成器及菜单完成 → 本文件 → 后端重新构建/启动 → HTTP与浏览器验收。",
    ),
    "business_schema_receipt": (
        "独立交付的真实数据库结构签名",
        "从当前数据库读取列、外键与关键约束，形成可比较结构；恢复不能仅以表存在代替结构一致，也不能删除不匹配的数据。",
        "portable创建清单 → 独立启动器校验新库/已有同产品库 → 结构一致性证据。",
    ),
    "business_probe": (
        "三角色实际原生HTTP验收",
        "使用明确合成账号和业务记录，通过原生登录取得身份，检查关联、分配、转换、历史、审计、提醒和统计，另以无权用户验证后端拒绝；不把隐藏按钮当权限证明。",
        "native_lab/独立恢复 → customer_service_acceptance → business.json及临时浏览器场景。",
    ),
    "native_business_probe": (
        "原生接口的逐字段检索、关联权限与审计不变性验证",
        "用合成对照记录和五个真实身份计算预期可见集合，实际请求搜索、精确筛选、日期区间及组合条件；尝试无权关系写入和审计修改删除，比较拒绝前后的记录与哈希。只有断言完成才写入观察结果，不根据合同本身填入成功标记。",
        "business_probe → NativeOracle及真实HTTP探针 → execution_evidence；portable将同一探针带入新数据库再次执行。",
    ),
    "native_evidence": (
        "绑定实际原生执行证据并交给独立模型审阅",
        "严格校验逐项观察的类型、角色、字段、预期与实际计数及集合哈希，确认覆盖当前批准合同，再绑定源码及报告哈希。传给模型的内容只含受限的测试结果与复现文件摘要，不发送账号、原始记录或工具日志；旧的汇总布尔值不能替代详细证据。",
        "native_delivery.managed_verify → native_review_evidence → flow.model_review；审阅仍可因真实缺口阻塞交付。",
    ),
    "business_browser": (
        "用临时场景连接真实原生浏览器验收",
        "只把本次合成账号交给临时场景文件，启动对应浏览器脚本并要求passed及零错误；临时凭据不进入上传报告。",
        "native_lab/portable → 模板专用CJS脚本 → business-browser.json与截图。",
    ),
    "business_python": (
        "基础Python产品的业务合同挂载",
        "把共享的有限业务策略与产品自身Schema/认证连接，生成独立运行所需配置及文件；不依赖开发工作台进程或真实模型服务。",
        "generate_basic → 完整业务合同 → 产品自身运行时和独立验收。",
    ),
    "daytona_sessions": (
        "长时间沙箱检查的单次异步提交",
        "建立独立会话并仅提交一次异步命令，按总期限用有界GET轮询，终止后读一次日志。传输层关闭透明重试，单请求最多30秒；提交响应丢失立即失败，不能用同步exec重放。",
        "sandbox非SQLite矩阵命令 → run_session_command → mode/session/command回执 → 可信运行报告与自有沙箱清理。",
    ),
    "daytona_diagnostics": (
        "本次自有沙箱的有界启动诊断",
        "创建失败后仅按确切随机名称和UUID读取固定本机Runner内的状态及日志尾部；限制单项与总时间、过滤秘密后限长保存。不枚举其他容器、不改配置，诊断失败不阻止原清理，成功不替代验收。",
        "sandbox失败创建路径的显式可选开关 → capture_startup → startup_diagnostics回执 → 原沙箱删除路径。",
    ),
    "native_style": (
        "原生UI壳、主题和组件族的身份检查",
        "先比较固定上游与生成目录中受保护布局/主题文件的内容清单，再解析生成Vue页应使用的真实框架组件；输出绑定模板、来源和Plan的回执。静态身份检查之后仍须真实浏览器检查，不能用一张通用页面替代原生风格。",
        "native_lab → verify_native_style → native_style.json → 原生浏览器与managed_verify。",
    ),
    "recommendation": (
        "解释智能推荐为何暂停",
        "把当前gate中的明确阻塞、未回答问题和能力说明分开，记录阶段、尝试次数及门身份；不会把所有暂停一律解释成模板不支持，也不会自行宣布已完成。",
        "runtime自动修正达到有界次数 → blocked_report → recommendation-blocked.json → 页面/CLI诊断。",
    ),
    "local_only": (
        "工具的本机运行边界",
        "地址先校验再创建客户端；localhost规范成回环IP，数据库URL拒绝能覆盖主机的查询参数。Docker命令显式指定本机套接字，Daytona子进程同时限制DNS和连接目标。此处不限制用户明确配置的大模型服务。",
        "settings → tools/retrieval/daytona_worker；test_local_only验证拒绝路径。",
    ),
    "settings": (
        "把配置转换为带类型、可校验的运行参数",
        "BaseSettings从.env/环境变量读字符串，再交给字段类型及验证器转换。ModelProfile负责模型端点，Settings负责目录、预算、工具和数据库；model_for按阶段选模型，更换服务商不能沿用默认密钥。redact统一清理报告中的凭据。",
        "CLI/API建立Settings → Store/Runtime/ModelGateway/本机工具；test_guided_models及test_local_only。",
    ),
    "catalog": (
        "技术栈组合目录",
        "Selection把前端、后端、数据库当作一个整体校验，而不是三个互不相关的文本。网页和CLI从同一目录取得可选项，生成器也读取同一个已验证选择，避免页面允许选但后端不能生成。",
        "api/cli → Selection → Run.options → generator/native_delivery；test_guided_selection。",
    ),
    "domain": (
        "模型、网页、数据库之间的数据合同",
        "Pydantic模型定义哪些字段可以进入系统；校验在业务处理前发生。FieldSpec约束字段类型，Entity组合字段，Plan组合实体与规则；digest把规范化JSON变成稳定指纹，审批只对该指纹有效。",
        "api/llm解析 → Requirement/Plan → knowledge/generator/verification；test_contracts。",
    ),
    "store": (
        "持久化项目、会话、任务、版本、审批和证据",
        "SQLAlchemy类说明表的列，Store的方法说明事务操作。create_run建立运行和首条消息；任务认领与完成有状态约束，修订和审批保留指纹。页面状态与Worker进度不能只保存在内存变量里。",
        "api写入Store → Runtime认领Job → Workflow记录Revision/Approval/Step/Event；test_store。",
    ),
    "errors": (
        "区分暂停预算和超出能力",
        "这两个异常不是随意的报错字符串：调用方根据异常类型，把运行置为可恢复暂停或明确阻塞，而不是继续生成一个不满足要求的产品。",
        "llm/flow抛出 → runtime捕获；test_workflow及test_guided_workflow。",
    ),
    "conversation": (
        "从持久化记录组织对话上下文",
        "context读取已经保存的消息和能力说明。command_word规范化简短控制指令；concise_requirements保留已确认事实。这里不直接调用模型，避免每个界面各自重新解释用户已经回答的内容。",
        "Store消息 → conversation → flow需求节点 → ModelGateway。",
    ),
    "llm": (
        "唯一的对话模型调用网关",
        "网关集中选择阶段模型、计算调用预算、发送HTTP请求和校验结构化结果。重试有上限；没有真实配置时应报错，而不是暗中返回演示答案。测试由调用者显式注入协议夹具。",
        "Workflow/coding/aider_tool → ModelGateway → 大模型；test_llm、test_guided_models。",
    ),
    "flow": (
        "需求到交付的LangGraph状态机",
        "State是节点共享的数据合同，Workflow注册节点和转移。需求确认后才能整理源码上下文并规划；批准方案后才能生成和验收；通过真实检查后才进入交付确认。interrupt把人工关口持久化，自动模式只委托选择，不绕过验收。",
        "Runtime驱动 → 需求/上下文/规划/生成/验证/本机沙箱/审阅/打包 → Store保存证据；test_workflow。",
    ),
    "runtime": (
        "持久化Worker和断点恢复",
        "Runtime把数据库任务和LangGraph检查点连接起来。它按run_id恢复同一流程，认领任务后执行，遇到中断等待回答；异常转成明确状态并保留报告。数据库与checkpoint连接均须在退出时关闭。",
        "api/cli启动Worker → Runtime → Workflow → Store；test_postgres及test_guided_workflow。",
    ),
    "api": (
        "网页及CLI调用的HTTP接口",
        "create_app是应用工厂，先准备依赖和生命周期，再定义路由。路由校验本机访问令牌和请求合同，调用Store/Runtime；下载与报告只允许受控目录内的文件。内层函数就是具体HTTP处理器，不是另一个服务。",
        "web/app.js或cli → FastAPI路由 → Store/Runtime；test_api。",
    ),
    "cli": (
        "终端入口和运维命令",
        "Typer把Python函数映射为rnd子命令。init建立本机数据和索引，start启动网页，chat/recommend调用与网页相同的API；index/tools等工具命令是独立的本机诊断入口。token只供本机使用，不应贴进公开日志。",
        "pyproject的project.scripts → cli.app → api/runtime/toolchain；test_tools_cli。",
    ),
    "filesystem": (
        "限定文件路径、归档成员和写入范围",
        "inside在读取或写入前确认路径属于工作目录；files过滤凭据和运行目录；manifest逐文件算SHA，防止源码改了却使用旧索引；unpack拒绝越界和特殊文件；atomic_text用临时文件完成替换。",
        "knowledge/retrieval/aider_tool/sandbox/打包共用；test_safety、test_toolchain。",
    ),
    "symbols": (
        "从真实语法树提取代码符号",
        "Python使用标准库AST；Java、TS、JS使用固定grammar的Tree-sitter。Vue先定位SFC中的script与模板标签，再给script节点补上原文件行偏移。提取的是声明、继承和注解等结构，不把文件名当作函数解析结果。",
        "knowledge.build_index → parse_file → declarations；test_toolchain及ci_toolchain。",
    ),
    "knowledge": (
        "建立可追溯的源码索引和设计包",
        "build_index对比文件SHA，只重新解析变化的文件，并处理已删除文件；索引与FTS检索库对应同一源码摘要。context_for按路径和字符预算读取源码。design_pack把经批准的Plan转成供人审阅的规格、测试要求与SQL设计。",
        "toolchain → knowledge → symbols/retrieval；flow → design_pack。",
    ),
    "continue_index": (
        "固定Continue全文索引组件的本机适配器",
        "bridge_identity校验源码与已编译工具；seed_cache把Tree-sitter分块转换为上游组件需要的表列。rank按索引身份原子重建并运行实际update/retrieve，再把结果限制在平台已验证的分块范围。缺少工具时报出安装命令，绝不连接云端替代。",
        "retrieval.query → continue_index → 固定Continue组件 → 独立本机SQLite缓存；test_continue_index。",
    ),
    "retrieval": (
        "本机代码检索及可选本机向量融合",
        "chunks给片段附上文件和行号，FTS5负责关键词排序。query先核对源码摘要，防止返回过期行号，再应用路径/扩展名与预算限制；启用本机embedding时以独立配置生成和复用向量，采用倒数排名融合而非直接相加不同尺度的分数。",
        "toolchain/context_mcp → query → 本机SQLite；add_embeddings → 本机模型服务；test_toolchain。",
    ),
    "toolchain": (
        "把源码上下文接到实际主流程",
        "prepare_context不是只为展示准备的CLI：它为选定模板建立索引，按需调用本机embedding，然后检索并生成有预算的Repo Map。其他Typer函数提供同一能力的人工诊断入口。",
        "flow上下文节点 → prepare_context → knowledge/retrieval/aider_tool；context_server → MCP。",
    ),
    "context_mcp": (
        "只读本机MCP适配器",
        "make_server将search_code和repository_map包装成MCP工具，结果仍来自本平台索引。export_continue只写明确的stdio启动配置，已有配置拒绝覆盖；服务不开放HTTP云入口；启用Continue引擎时，查询会交给固定上游全文组件及本机适配器，而非IDE全局缓存。",
        "Continue本机Agent → stdio → context_mcp → retrieval。",
    ),
    "generator": (
        "确定性生成基础FastAPI产品",
        "generate_basic复制本项目编写的模板，再把Plan写入产品规格、路由信息和迁移文件。相同Plan使用同一套生成规则；模型不负责重写登录、数据库与整套骨架。代码字符串中的upgrade/downgrade是写入成品迁移的内容。",
        "flow生成节点 → generator → templates/product + product_sql → verification。",
    ),
    "coding": (
        "不依赖Aider的受限规则编辑",
        "apply_patch只接收允许文件的替换内容，校验旧内容和新规则。code_rules向网关请求结构化补丁并保存每轮证据。它不执行任意shell，也不能越权修改认证、路由和依赖锁。",
        "flow → coding → ModelGateway + Rules → verification；test_safety。",
    ),
    "aider_tool": (
        "隔离的Aider命令行适配",
        "Repo Map与SEARCH/REPLACE调用真实Aider CLI，但CLI不持有大模型Key。先用原文唯一匹配算出期望结果，再在临时Git工作区应用，检查实际结果和变更文件集合；只把批准的规则文件放回产品。",
        "coding_engine=aider → code_rules_with_aider → gateway/preview_blocks/apply_blocks；ci_aider_workflow。",
    ),
    "rules": (
        "解释受限的业务表达式",
        "Rules先解析表达式AST，只接纳允许节点、操作符和变量，再解释它，而非调用Python eval执行模型产生的任意代码。输入、输出与示例均受Plan约束，拒绝导入、反射和文件系统操作。",
        "coding/aider_tool校验 + 成品对应规则解释器；test_safety及业务例子复验。",
    ),
    "tools": (
        "有界子进程、清洁环境与失败证据",
        "run_command只执行参数数组而非拼接shell，限定目录和时间；超时停止进程树。输出落入临时文件防止内存无限增长，读取尾部形成ToolFailure证据。clean_env过滤凭据并强制禁用遥测，Docker显式走本机。",
        "生成/构建/测试适配器 → tools → 本机进程；runtime保存tool-failure报告。",
    ),
    "verification": (
        "基础产品的真实验收和干净解压复验",
        "先用产品自己的锁安装独立环境，再运行产品HTTP和逐规格真实Chromium验收。require_browser_evidence核对当前实体、字段与检查名称，不接纳缺项报告；package_basic解压到新目录再次完整验证，避免仅在工作目录偶然可运行。",
        "flow → verify_basic/package_basic → templates/product/verify.py/verify_business.py；test_customer_workflow与test_business_python。",
    ),
    "sandbox": (
        "本机Daytona附加验收与生命周期",
        "先检查本地执行授权和本机配置。source_archive过滤敏感文件并限制大小；checks_for只返回固定检查命令。创建前持久化随机名称，创建后立即保存ID，无论验证成败都尝试删除自己的沙箱；清理失败不能交付。",
        "flow沙箱节点 → daytona_worker → _verify_in_daytona → 本机Daytona；test_local_only及ci_daytona_local。",
    ),
    "daytona_worker": (
        "SDK专用的本机网络子进程",
        "父进程通过stdin传递最少配置，不把Key放进命令行；子进程先安装回环网络钩子再导入SDK。SDK默认云地址、重定向和代理不能绕过连接检查。父进程只接受passed=true且cleanup=deleted的回执。",
        "sandbox.verify_in_daytona → 子进程main → sandbox.client_for/_verify_in_daytona；test_local_only。",
    ),
    "vendor": (
        "核验并展开固定第三方模板",
        "inventory读取随教材给出的来源清单；unpack_source核验归档和源码摘要后才展开。prepare为特定模板选对后端/前端归档。模板是第三方依赖，不要求初学者重新手写其数千文件。",
        "rnd init/native_prepare → vendor → 本机templates/vendor；test_vendor。",
    ),
    "native": (
        "原生代码生成接口的公共适配",
        "NativeConfig描述可调用的代码生成服务，NativeClient进行认证请求，native_export把Plan映射为原生生成器元数据并取回真实导出。只导出源码的结果为SOURCE_READY，不能冒充托管运行验收READY。",
        "flow/native_delivery → NativeClient → 本机FastapiAdmin或Yudao生成器；test_native。",
    ),
    "native_environment": (
        "本机原生后端环境和进程",
        "先确认专用本机数据库，再复制固定源码、初始化种子并生成环境；install_backend准备依赖与构建，running_backend管理进程存活和退出，记录启动轮次、阶段、已拥有进程与目标端口状态。启动失败后清理也失败时保留原始异常并附加清理事实，不杀死占用端口的其他进程，也不把超时改成成功。兼容改动检查原文并记录。",
        "native_lab/native_delivery/portable → backend环境 → 本机PG/Redis/Java或Python。",
    ),
    "yudao_navigation": (
        "让原生菜单只呈现实际安装的能力",
        "固定mini后端只安装system/infra，完整上游种子仍含其他模块；生成覆盖层将已有菜单与实际注册的Spring处理器、已安装Maven模块及随包Vben组件求交集。管理员也不能看到未安装模块；不删除菜单数据、不增加角色授权，重建和ZIP恢复重新计算能力。",
        "install_backend → 原生MenuService只读覆盖层 → auth/menu/role-menu接口与Vben侧栏。",
    ),
    "yudao_navigation_checks": (
        "独立检查实际菜单与角色授权的交集",
        "通过真实原生接口和浏览器，比较安装的基础能力、批准方案业务菜单及各角色原有授权；同时保留应出现和应拒绝的具体观察值。源实例、新数据库恢复与重启重复检查，不能用覆盖层自报清单或单个passed标记替代执行证据。",
        "原生HTTP/浏览器与独立恢复 → 菜单能力观察 → 源码和原始报告哈希绑定的独立审阅。",
    ),
    "native_delivery": (
        "原生生成、完整验收和打包的流程接口",
        "managed_generate协调本机源码、专用数据库和生成器；managed_verify核对数据库身份及完整回执，managed_package只有在验收成功时打包。serve_managed用于本机查看生成结果，不是公网部署。",
        "flow → managed_generate/verify/package → native_lab/portable；test_native_managed。",
    ),
    "native_modules": (
        "把Plan的实体挂载成原生业务模块",
        "validate_plan先拒绝尚未适配的业务类型；元数据生成与业务建表使用同一Plan。generate_modules实际调用原生生成器，解包并挂载后端、前端、菜单和权限，记录映射，不能以几个示例文件冒充整套原生工程。",
        "native_lab → create_native_tables/generate_modules → NativeClient/native_vben；test_native_modules。",
    ),
    "native_lab": (
        "两套原生全链路验收的总协调",
        "run_acceptance依次准备本机数据库、启动后端、生成挂载模块、检查CRUD/RBAC、重启验证持久化、构建前端和打开真实浏览器。任何一步失败都保留报告并退出，不能仅看后端健康接口。",
        "ci_native_generated/native_delivery → native_lab → native_environment/modules/acceptance/frontend。",
    ),
    "native_acceptance": (
        "实际调用生成后的业务接口",
        "sample_record为不同字段构造有效记录；generated_crud检查创建、读取、修改、删除和无效载荷，persistence检查重启后记录仍在，permissions实际授权及撤权，不只读取权限配置。",
        "native_lab → 后端HTTP/PG；test_native_baseline和native CI。",
    ),
    "native_checks": (
        "统一原生响应、菜单和权限断言",
        "两套原生系统响应结构不同，payload/record_id等辅助函数统一读取方式。await_permission有明确超时，不用无限重试把失败伪装成通过；拒绝未认证和伪造令牌仍是必须验证的路径。",
        "native_acceptance/native_lab → native_checks → 原生HTTP。",
    ),
    "native_compatibility": (
        "原生事务提交时机的精确适配",
        "commit_before_response只在固定控制器满足预期代码形态时改变依赖生命周期，让成功响应之前提交事务。prepare_fastapi_transactions逐文件检查并记录哈希，不以sleep掩盖事务竞态。",
        "native_environment → FastapiAdmin控制器；test_native_transaction。",
    ),
    "native_vben": (
        "Vben兼容适配与生成表单类型保持",
        "checked_replacement要求精确匹配数量，防止套用到未知源码。原有视图保留；生成表单处理DTO泛型、未使用导入、整数控件及布尔选项，使0和false不变成字符串或空值。",
        "native_environment/native_modules → Vben完整源码；test_native_vben及真实Chromium。",
    ),
    "native_frontend": (
        "完整原生前端构建和浏览器入口",
        "按模板选择真实前端根目录和环境，固定包管理器与锁文件安装，执行完整构建/类型检查。preview管理服务端口和生命周期，browser_check启动实际浏览器检查页面，而不是只检查HTML文件存在。",
        "native_lab/portable → pnpm/Vite/vue-tsc → scripts/native_browser.cjs。",
    ),
    "native_resources": (
        "为一次运行分配隔离资源",
        "free_port从本机取得可用端口，for_run按run_id产生独立的数据库/Redis等资源配置和回执。资源名和范围不能从任意用户文本拼接，避免碰到既有业务数据。",
        "native_delivery → 每次运行隔离资源；test_native_managed。",
    ),
    "postgres_lab": (
        "基础产品真实PostgreSQL验收环境",
        "checked_admin_url拒绝远程或能覆盖主机的参数。database在显式本机管理连接或本机Docker中创建独立测试数据库，并在上下文退出时清理本次资源；不连接云数据库。",
        "verification → 本机PG验收；test_guided_postgres。",
    ),
    "product_sql": (
        "从同一Plan生成可读SQL交付资料",
        "render使用字段合同生成业务DDL和菜单等资料，标识符不是任意模型文本。SQL资料与真正的迁移/原生生成器用途不同，文档说明哪个脚本负责实际初始化，防止重复执行。",
        "knowledge/generator → product_sql → 设计包与产品。",
    ),
    "portable": (
        "让原生产品脱离工作台独立启动",
        "导出原生种子、增量业务表和菜单SQL，复制启动器所需全部HELPERS，包括本机策略模块。verify_native_delivery在另一个新的本机数据库恢复并启动前后端，确认没有导入原工作台或复用原生成数据库；失败时在删除临时副本前保留白名单日志尾和进程阶段，限制读取与输出大小并遮蔽凭据，不复制环境、服务密码文件或任意运行目录。诊断回执不能授予验收成功。",
        "managed_package → portable → templates/deployment；test_native_delivery_boundaries。",
    ),
    "requirement_coverage": (
        "保留用户事实并检查可执行需求覆盖",
        "模型格式与类型先由官方LangChain结构化输出和Pydantic负责。reconcile保留已确认事实，替换要有当前真实用户更正原文；coverage_gaps逐项比较结构化字段、数据归属与可识别业务约束，指标与列表查询分区。仅提到英文别名不会建立新字段义务；真实正向声明、明确禁止字段及旧文本兼容检查仍保留，不把部分typed清单当成语义完整证明。来源冲突与设计漏项仍阻塞，不让规划模型自行宣布已覆盖。",
        "flow.analyse保留事实 → Requirement.field_requirements → flow.design → coverage_gaps；test_requirement_coverage。",
    ),
    "entity_requirements": (
        "用户明确封闭的实体与字段清单",
        "普通项目默认允许扩展；只有明确封闭的批准清单才禁止额外实体或字段。逐实体比较计划并报告缺失、额外字段与来源编号，不直接修改模型计划。模型遗漏清单不构成撤销批准，修正需可追溯的用户原文。",
        "Requirement.entity_requirements/additional_entities → coverage_gaps → 设计门与下一轮精准修复反馈。",
    ),
    "native_recovery": (
        "身份绑定的原生中断检查点",
        "identity绑定模板、批准Plan、数据库身份和前后端来源；save记录实际文件清单与可恢复阶段；load只接受同一身份、完整且未篡改的可恢复现场。不可重放阶段中断不能自动重置数据库。",
        "native_lab保存/恢复 → 同一生成目录及本机数据库 → native_coding继续验证；test_native_recovery。",
    ),
    "scaffolding": (
        "用真实Plop接入受限业务规则",
        "从批准Plan和已生成原生模块计算白名单路径、精确锚点及模板参数；先在临时目录调用node-plop，再核对实际新增和修改文件，最后写回。失败恢复已有文件，模型不能提供自己的生成脚本。",
        "native_coding → scaffolding → tools/node/plop-runner.mjs → 真实原生Python/Java/Vue规则入口；test_native_tools。",
    ),
    "native_coding": (
        "原生业务规则的有界编辑与修复",
        "平台网关提出SEARCH/REPLACE，Aider在独立Git副本实际应用；允许变更仅限已登记的规则表达式。真实后端、前端与浏览器拒绝错误候选，回滚后再把脱敏失败反馈交给下一轮，达到预算就停止。",
        "native_lab的规则回调 → Plop → ModelGateway → Aider → native_business_checks/native_frontend；ci_native_tools。",
    ),
    "native_business_checks": (
        "用批准的正反例验证原生业务约束",
        "实际发送新增和修改请求，区分业务拒绝、鉴权失败和服务错误；拒绝新增不能留下记录，拒绝修改不能改变旧值，合法操作仍须成功。不能仅断言HTTP不等于200。",
        "native_coding候选验证/原生整体验收 → 真实后端接口 → 保留业务证据。",
    ),
    "daytona_profiles": (
        "按技术栈登记离线快照和验收合同",
        "模板与数据库组成profile，依赖锁的内容摘要绑定预热镜像；报告必须属于当前源码及选择，并使用严格布尔值证明对应关卡和清理，不能复用主机数据库。",
        "daytona_matrix_image准备 → snapshot_for选择 → sandbox运行 → require_runtime_report核验；test_daytona_matrix。",
    ),
    "owned_lifecycle": (
        "只控制本次启动的服务并核实退出",
        "启动器、进程与端口属于一次明确生命周期；结束时先等待和检查，再验证端口关闭。重启必须是新进程，不能让残留服务冒充成功，也不能为释放端口终止别人的应用。",
        "Daytona矩阵和独立原生启动器复验 → 所拥有的进程 → services_stopped证据；test_owned_lifecycle。",
    ),
    "portable_checks": (
        "独立原生产品的业务复验",
        "check_restored_product对新数据库启动后的产品执行实际认证和CRUD断言，输入来自产品随包规格。它不能依赖工作台的运行对象，否则在用户独立解压后就失效。",
        "templates/deployment/start.py复制的helper → 产品后端HTTP。",
    ),
}

BUSINESS_FILES = {
    "yudao/RndBusinessQuery.java": (
        "芋道业务列表的声明式查询谓词",
        "将配置允许的查询编译为纯Java谓词：关键词只搜索已声明字段，精确过滤按类型比较，日期上下界包含边界，多个条件取交集。无权行先由服务层排除；未知或未开放条件返回输入错误。真实Java断言和错误实现变异检查验证这些规则。",
        "RndBusinessService.page先检查角色/行权限 → 本文件匹配 → 原生Vxe列表；business-form.ts只显示批准的查询控件。",
    ),
    "common/policy.py": (
        "三个模板共享的有限业务策略解释器",
        "Policy按批准合同查角色、资源、权限与状态转换，校验受控字段并计算登记指标；只处理数据和规则，不持有数据库连接或外部网络权限。",
        "Plan.business → business_python/fastapiadmin复制策略 → 各自事务运行时；Yudao以审查过的Java实现相同合同。",
    ),
    "fastapiadmin/controller.py": (
        "FastapiAdmin原生认证下的业务HTTP入口",
        "路由接收严格动作载荷，使用框架当前用户和数据库依赖调用运行时；业务权限不能由浏览器传入角色或负责人来决定。",
        "原生路由注册 → controller → runtime → SQLAlchemy模型与policy。",
    ),
    "fastapiadmin/guard.py": (
        "原生成CRUD入口的绕过防护",
        "业务合同挂载后，原CRUD路径不能成为跳过行范围、受控字段与事件的备用写入口；这里检查当前模块身份并拒绝不允许的调用。",
        "business_fastapi改造生成控制器 → guard → 合同业务接口。",
    ),
    "fastapiadmin/index.vue": (
        "Fa与Element Plus业务页面",
        "沿用原生布局和组件，按合同渲染列表、表单、关系选项、指派、状态、历史、提醒与统计；页面只提示权限，服务器仍实施权限。",
        "原生菜单/路由 → 本Vue页 → 同框架业务API；business_fastapi_browser.cjs实际操作。",
    ),
    "fastapiadmin/model.py": (
        "FastapiAdmin业务事件与通知模型",
        "用原生ORM事件表承载操作、处理记录和收件人通知，字段来自受审查适配器；与生成实体使用同一专用数据库，不建立旁路内存数据库。",
        "扩展DDL → 原生模型发现 → runtime事务读写。",
    ),
    "fastapiadmin/registration.py": (
        "原生注册与默认业务角色的事务连接",
        "在已有账号校验和密码哈希之后添加合同默认非管理员角色；初始化权限和普通注册分离，不允许用户选择管理员角色。",
        "原生注册接口 → 同事务注册钩子 → 产品专属角色。",
    ),
    "fastapiadmin/runtime.py": (
        "FastapiAdmin合同事务运行时",
        "读取真实原生身份，实施角色/行范围、关联锁、命名动作、事件与通知；指标使用当前可见范围，关键写入共同提交或回滚。",
        "controller → policy/生成模型/扩展模型 → PostgreSQL → 原生响应。",
    ),
    "fastapiadmin/__init__.py": (
        "FastapiAdmin业务插件包入口",
        "使生成后的module_business目录成为可导入模块；具体路由、事务和策略分别由同目录文件实现。",
        "business_fastapi写入 → 原生模块发现 → controller/model。",
    ),
    "yudao/EntityController.java": (
        "Yudao生成实体的受保护控制器",
        "保留原生路由、VO与认证接线，将实体读写转交合同服务，避免旧生成CRUD旁路跳过角色、关系和事件规则。",
        "Vben生成API → 此Controller → RndBusinessService → 原生Mapper。",
    ),
    "yudao/RndBusinessController.java": (
        "Yudao业务动作与管理路由",
        "公开角色、关系、分配、命名转换、历史、通知和统计入口；身份来自原生登录，接口参数不能伪造操作者。",
        "Vben业务面板 → Controller → RndBusinessService事务。",
    ),
    "yudao/RndBusinessMapper.java": (
        "Yudao扩展事件与业务查询Mapper",
        "以明确登记表与参数绑定读写扩展数据；实体DO/Mapper仍来自真实生成器，不能用用户输入替换SQL表名。",
        "RndBusinessService → MyBatis Mapper → 本产品业务及事件表。",
    ),
    "yudao/RndBusinessRegistration.java": (
        "Yudao原生注册后的业务角色连接",
        "沿用框架注册、校验与密码处理，事务性分配合同默认非管理员角色，不签发假令牌或存储明文密码。",
        "原生账号注册 → 本产品角色钩子 → 初始化与权限验证。",
    ),
    "yudao/RndBusinessService.java": (
        "Yudao业务合同的Java事务实现",
        "校验真实身份与精确资源映射，锁定记录后执行关系、分配和状态动作，追加事件/通知；角色管理保护最后管理员，统计应用可见行范围。",
        "业务/实体Controller → Spring事务 → 原生DO/Mapper及扩展Mapper → PostgreSQL。",
    ),
    "yudao/business-form.ts": (
        "Vben合同表单与关联选项",
        "在原生Form Schema中移出状态/负责人等受控字段，把关系键接为服务器限定的可识别选择项；关系选择器按可读标签搜索并保留虚拟滚动，选项多时也能找到新记录，不扩大后端权限范围。保留字段校验和类型。",
        "生成Vben表单 → 本辅助函数 → 合同关系API与原生表单组件。",
    ),
    "yudao/metric-chart.vue": (
        "Vben真实指标的图表组件",
        "将服务器已按角色范围计算的指标转换为Echarts展示；空样本、数量、时长和日期轴有不同含义，不在前端编造统计数字。",
        "业务metrics响应 → panel.vue → 本图表 → 原生主题。",
    ),
    "yudao/panel.vue": (
        "Vben业务处理与协作面板",
        "使用原生Ant/Vben组件展示指派、状态、备注、历史、提醒和统计，调用合同专用API；权限变化后仍以后端结果为准。",
        "生成Page/Grid/TableAction入口 → 本面板/Form/Modal → 业务Controller。",
    ),
}

PRODUCT = {
    "business_schema.py": "纯元数据构造器：按批准合同创建实体真实外键、角色、初始化标记、不可改审计、处理记录与收件人通知表；不在导入时连接数据库，可供生成器编译审查SQL。",
    "business_runtime.py": "独立客服产品事务执行器：每请求读真实角色，把all/own/assigned放进查询；保护创建人/负责人/状态/时间，锁定记录执行动作，追加事件与提醒，并按范围计算四类指标。",
    "verify_business.py": "独立客服HTTP/浏览器验收器：新建自有数据库和三角色合成账号，验证关系、指派、流程、记录、提醒、统计、拒绝路径及重启；截图仅限有界命名PNG，不导出密码或运行数据库。",
    "verify-business-browser.cjs": "Python轻量原生UI的三角色真实Chromium场景：通过登录、列表、关联表单、详情动作、提醒及统计控件完成客服流程，记录检查项和合成数据截图；不注入token或mock接口。",
    "fields.py": "按批准字段规则验证新增/修改载荷：必填、整数与布尔、文本长度、日期和枚举各自处理；可选空值不等于整数0或布尔False。业务规则在结构校验之后执行。",
    "querying.py": "把搜索词、精确筛选、日期上下界转成受字段白名单约束的SQLAlchemy条件；类型和范围先验证，再通过参数绑定查询，不拼接用户SQL。",
    "manage.py": "产品自己的迁移/启动及一次性bootstrap-admin入口：管理员密码在隐藏终端交互输入，初始化与事件同事务完成；普通注册不能抢占管理员，也不修改平台控制数据库。",
    "compose.yaml": "独立产品的本机PostgreSQL服务声明：服务、回环端口与持久卷属于该产品；启动器生成本机随机凭据并保留已有配置，应用退出不删除数据卷。",
    "pyproject.toml": "独立产品的Python依赖清单，与平台环境分开；先由uv按对应uv.lock安装，再启动产品，不能依赖开发平台碰巧装过的库。",
    "uv.lock": "该独立产品的精确Python依赖及分发哈希；与产品pyproject配套保存，由启动器--locked安装，不使用平台或Aider锁代替。",
    "README.md": "交付包内的独立启动和使用说明模板；生成器还会写入规格、选择和SQL，使用户离开研发平台后仍知道运行哪个入口。",
    "app.py": "FastAPI产品认证与路由入口：无business时保留per_user实体接口；有business时安装business_runtime事务接口与角色范围。网页不能直接访问数据库或伪造操作者，角色从服务器读取。",
    "schema.py": "产品数据库及字段合同：按spec.json创建运行表模型与校验规则；独立产品也拒绝远程数据库。字段类型同时决定请求校验、SQL列类型、序列化和查询筛选行为。",
    "auth.py": "产品自己的账号密码与会话：加盐口令派生、会话令牌摘要、过期和身份读取；这里的产品登录不是工作台访问令牌，更不是大模型API Key。",
    "rules.py": "交付给用户的受限规则解释器：与生成时采用相同的允许表达式和输入输出合同，不使用eval或任意Python执行。",
    "verify.py": "真实产品验收程序：创建测试账号调用HTTP接口，再根据simple-admin选择启动同目录verify-browser.cjs；缺浏览器或逐规格检查缺项都失败，api-only明确记为不适用。与app.py分离，不能因应用自称成功就通过。",
    "verify-browser.cjs": "逐规格真实Chromium验收：页面注册登录、遍历全部实体和字段，检查CRUD、长度拒绝、搜索/组合筛选/含边界日期、用户隔离和退出重新登录；刷新另核对同源路由、真实认证schema/list响应与已保存记录DOM，不以整页load或HTTP200独自代替业务就绪。不注入登录Token或mock接口，输出明确checks与页面错误。",
    "start.py": "成品自包含入口：在产品目录安装自己的锁定依赖，准备本机SQLite或专用PostgreSQL，执行迁移后启动HTTP服务；不调用模型，不要求原工作台目录。",
    "custom_rules.py": "唯一允许自动定制的业务规则文件；生成前后的约束、例子与SHA由平台检查。其他身份、存储和启动代码不开放给模型任意编辑。",
    "spec.json": "该文件是模板示例规格，运行时由已批准Plan生成具体成品规格；不要把示例实体名称硬编码到平台通用生成流程。",
}

SCRIPT_ROLES = {
    "business_fastapi_browser.cjs": (
        "FastapiAdmin三角色真实客服页面验收",
        "使用临时合成账号通过原生登录、菜单与Fa/Element Plus组件，操作客户/请求/任务、关系、分配、流程、历史、提醒和统计；查询按钮等定位以锁定的真实组件为准，同时核对请求参数、响应记录和页面记录，不能用夹具自造的按钮名代替。检查原生主题及页面错误，保存命名截图。",
        "business_browser → 本脚本 → business-browser.json与当前生成产品的PNG。",
    ),
    "business_yudao_browser.cjs": (
        "Yudao/Vben三角色真实客服页面验收",
        "通过原生登录和租户选择进入Vben/Ant/VXE组件，执行同一客服合同；关联控件搜索本轮记录并选择准确ID。角色菜单截图进入真实授权列表，一次只读采样按CSS字体合并全部可见Unicode码点检查，不跨帧缓存字体状态；再捕获未改动像素并复查。已适配viewport的页面不启用会临时缩到1×1的越界捕获，长页仍保留完整像素。布局变化在同一45秒期限内重新稳定，等宽更新仍检查新字形。不改DOM或禁用字体校验；阶段/采样耗时不含业务文字。HTTP拒绝和UI共同组成证据，不以静态图替代。",
        "business_browser → 本脚本 → business-browser.json与当前生成产品的PNG。",
    ),
    "ci_real_model.py": (
        "显式授权的真实模型完整验收",
        "可信客服分支的手动任务在rnd中将APK_KEY映射为API_KEY，三个模板各自先Hello再校验同提交同attempt回执。完整需求由原文、默认决策和命名约定构成；真实网页只一次初始智能推荐，随后必须READY、实际下载、新库HTTP/浏览器/重启；公开白名单状态及经过校验的合成页面截图，不输出密钥或模型原文。",
        "native-probe手动real_model=true+expected_sha，或real-model手动矩阵 → rnd job → ModelGateway真实请求 → 当前模板独立产品 → summary.json与合成PNG；工具矩阵和BLOCKED恢复另验。",
    ),
    "build_handbook.py": (
        "生成唯一完整教材",
        "按GUIDES顺序拼正文并调整图片相对路径，再按GROUPS枚举自有源码与真实截图，排除依赖/运行目录；附录写源码指纹、完整代码及可折叠Base64二进制块。--check比较全部文本与唯一输出，不改源码。",
        "正文及真实源文件 → render → 单一Markdown；test_handbook验证独立重建。",
    ),
    "handbook_notes.py": (
        "把源码变成逐文件教学提示",
        "先按具体文件职责解释输入、调用方和结果，再解析Python AST列出类/函数、行号、参数、关键分支和返回。它不执行被讲解的业务代码；手写教学章节补充业务意图与练习。",
        "build_handbook → purpose/notes → 每个源码块前的对应关系。",
    ),
    "rebuild_from_handbook.py": (
        "从一本书还原安全的新项目",
        "extract先验证全部标记、路径和SHA；截图严格解码Base64后验证原始字节，再由restore写入新的空目录。任一源码或资源块残缺就不动目标；不运行提取出的程序或下载依赖。",
        "书中独立bootstrap或本脚本 → 完整自有源码和真实截图 → ci_handbook。",
    ),
    "vendor_templates.py": (
        "重建固定的第三方源码归档",
        "按登记远端与提交取得公开依赖，保留许可证，排除密钥/缓存/数据库等不应打包内容，记录归档SHA与逐文件内容摘要。它不取得本平台骨架代码。",
        "教材还原后--fetch → templates/vendor → workbench.vendor校验并解压。",
    ),
    "ci_handbook.py": (
        "证明一本书足够重建平台",
        "把教材单独复制进临时目录，恢复所有文本与二进制截图，确认导入来源，验证再次生成相同教材；再重建三个上游归档和Continue。完整非PG套件有明确1800秒预算，外层仍40分钟；超时中断自有测试进程、保留阶段与已有JUnit且仍失败，不增加单项等待。",
        "handbook-only工作流 → 本脚本 → handbook-test-status.json/JUnit；完整通过才产生handbook-clean-room.json。",
    ),
    "ci_clean_install.py": (
        "独立依赖环境与成品干净解压验收",
        "显式需求/计划夹具只代替模型响应，Runtime与产品进程实际运行。批准三个关卡后必须READY，且isolated_dependencies、cleanroom真实通过；临时目录退出时清理。",
        "双系统clean-install工作流 → Runtime → 生成/验证/解压 → clean-install.json。",
    ),
    "ci_aider_workflow.py": (
        "基础产品实际Aider编排验收",
        "固定响应提出批准业务规则，真实LangGraph调用真实Aider，然后运行独立产品验收。记录工具调用和结果，不能把夹具响应当作付费模型质量证据。",
        "toolchain验收 → Runtime/ModelGateway替身 → 本机Aider → 基础产品验证。",
    ),
    "ci_toolchain.py": (
        "实际解析、Continue、MCP和Aider串联验收",
        "准备固定真实源码，建立符号/全文索引、启动只读MCP并执行真实Aider入口；每类工具的输出单独验证，再运行受控业务规则流程。",
        "toolchain工作流 → 本脚本 → 本机工具报告；模型输出为明确夹具。",
    ),
    "ci_local_embeddings.py": (
        "固定真实权重的本机推理验收和服务",
        "prepare显式下载校验后的公开模型；serve在回环HTTP上用CPU推理且拒绝出站套接字；verify启动自有服务、取固定Vben样本、查缓存及真实融合检索，最后关闭服务。",
        "独立tools/embeddings解释器 + 平台retrieval → local-embeddings.json。",
    ),
    "ci_guided_browser.py": (
        "工作台到资讯产品的浏览器验收协调",
        "启动实际工作台与浏览器，显式模型夹具提供资讯需求，检查智能推荐和产物；随后访问真正生成的产品，不将静态HTML当成功。",
        "browser工作流 → guided_browser.cjs → 实际API/页面/独立交付。",
    ),
    "guided_browser.cjs": (
        "在真实浏览器操作研发工作台",
        "通过DOM选择技术栈、提交需求与控制智能推荐，等待真实状态/网络结果；操作生成资讯页面的登录、CRUD和查询，保存截图与错误。",
        "ci_guided_browser启动服务 → 本文件驱动Chromium → 可复查界面证据。",
    ),
    "ci_native_sources.py": (
        "固定原生模板源码完整性检查",
        "核对所有已登记归档、许可证、固定提交及关键原生生成器文件，确认仓库真带框架源码。只检查来源的通过不代表服务器或浏览器通过。",
        "native-sources/verify-bundles → vendor清单与归档 → 来源报告。",
    ),
    "ci_native_generated.py": (
        "定义并运行原生模块集成样例",
        "acceptance_spec给出多实体、文本/整数/布尔的确定性Plan；入口把模板、数据库和源码参数交给同一个native_lab，避免CI另写一套伪生成器。",
        "原生CI入口 → acceptance_spec → native_lab.run_acceptance。",
    ),
    "ci_native_bundled.py": (
        "从随附原生源码生成并独立新库恢复",
        "从vendor清单取得固定源码，把真实Plan交给native_lab，启用完整原生运行和portable新库复验。没有前端或独立恢复证据不能通过。",
        "native-runtime工作流 → 本脚本 → reports/native中的运行与恢复证据。",
    ),
    "ci_native_runtime.py": (
        "原框架本身的运行基线验收",
        "复制固定原生源码、初始化专用空库，安装并启动后端/前端，执行原框架登录和权限检查。它测原生基线，不代替新增业务模块和独立交付。",
        "本机显式原生基线命令 → native_environment/native_frontend → 基线报告。",
    ),
    "ci_native_tools.py": (
        "原生Plop/Aider修复与可恢复中断验收",
        "真实生成后故意中断再恢复，权限验证后再中断再恢复；规则夹具先给错误候选，真实正反例拒绝并回滚，随后修复，最终完成浏览器/独立新库验收。",
        "native-toolchain-daytona矩阵 → 原生工具验收 → 已验证产品供快照准备。",
    ),
    "native_browser.cjs": (
        "真实原生登录、菜单、表单与规则浏览器检查",
        "按FastapiAdmin或Vben的真实DOM操作，登录提交必须核对实际认证/权限HTTP、同源非登录路由和原生shell，不等待概览页无关资源的整页load；再验证生成菜单的实际列表API/DOM、原生组件及表单正反例。失败截图/网络错误用于诊断，不能注入令牌越过登录，45秒等待上限不变。",
        "native_frontend.browser_check → 本文件 → browser.json与截图。",
    ),
    "native_coding_fixture.py": (
        "故意先出错的原生编码测试模型",
        "对已登记规则区域返回可审查SEARCH/REPLACE；首轮总为true，后轮是数量非负表达式。它不直接写代码，实际应用与失败回滚仍由Plop/Aider及平台执行。",
        "ci_native_tools注入 → native_coding调用 → 真实工具和反例检查。",
    ),
    "news_fixture.py": (
        "资讯需求与智能推荐的显式测试响应",
        "保存固定资讯规格及能力说明，故意让首轮把无关限制误当阻塞，检查后续是否根据真实反馈修正并保留字段。它只被测试导入，不是生产未配模型时的默认响应。",
        "ci_guided_browser/Daytona资讯验收 → 显式夹具 → 正常工作流。",
    ),
    "daytona_local.py": (
        "安装和管理本机Daytona开发服务",
        "prepare取得固定资源与随机本机配置，images构建并锁定镜像，up验证锁后启动，status读取状态；snapshot-image预热产品依赖。每一步分开执行，失败不跳下一步。",
        "终端明确命令 → 本机Docker/Compose → .data/daytona-local配置与锁。",
    ),
    "daytona_build.py": (
        "从固定来源构建并锁定本机镜像",
        "验证源码Git对象、Runner发布字节与许可证，在干净构建上下文编译控制面和存储，记录不可变镜像身份；不猜测latest标签或切换云端服务。",
        "daytona_local images → Docker本机构建 → images.lock/compose.lock。",
    ),
    "daytona_bootstrap.py": (
        "真实本机身份认证与快照注册",
        "auth通过本机Dex与API获取本机密钥；snapshot核对预热镜像/资源并限时等待active。准确名称和身份匹配后才写workbench.env，失败不写假就绪。",
        "up健康后 → auth → snapshot → 平台本机Daytona配置。",
    ),
    "daytona_gateway.py": (
        "固定端口的本机网络入口",
        "TARGETS静态列出容器服务，异步转发只连接这些固定目标；不读取用户URL、代理主机或模型密钥，不把它当任意TCP代理。",
        "本机Compose回环发布端口 → 只读网关容器 → 内部服务。",
    ),
    "daytona_diagnostics.py": (
        "保留有界且脱敏的失败诊断",
        "仅读取本次本机安装的状态和尾部日志，先收集本机秘密用于替换，再写报告；不打包credentials或env。诊断脚本不宣告业务通过。",
        "工作流always失败/成功收尾 → reports/daytona诊断 → 人工定位。",
    ),
    "daytona_matrix_image.py": (
        "为每个技术栈制作离线依赖快照",
        "从已生成项目提取受限公开构建输入和依赖锁，排除运行数据与秘密，按profile预热工具后推到本机registry，记录来源/资源/锁身份。",
        "真实原生产品 → matrix.Dockerfile/warm.py → snapshot-image.json。",
    ),
    "daytona_matrix_probe.py": (
        "沙箱内独立数据库和产品验收",
        "在沙箱内创建自有PG/Redis，离线安装/构建并通过独立启动器运行产品，执行HTTP、权限、浏览器及重启；检查服务退出后生成严格报告。",
        "sandbox固定命令 → 本脚本 → 当前profile的运行证据；不复用主机库。",
    ),
    "ci_daytona_local.py": (
        "真实本机Daytona中的资讯端到端验收",
        "先用明确模型夹具完成智能资讯工作流，再创建实际本机沙箱并执行离线产品检查，确认删除和独立ZIP复验；SDK模拟测试不是这份报告。",
        "daytona-local工作流 → Runtime/本机工具/Daytona → daytona-local.json。",
    ),
    "ci_daytona_matrix.py": (
        "数据库与模板矩阵的沙箱验收入口",
        "prepare-basic创建用于矩阵的基础PG产品；verify读取已登记同profile快照并运行真实沙箱，核对运行和清理证据。它不能用一种镜像冒充所有技术栈。",
        "native-toolchain-daytona三行矩阵 → profile快照 → daytona-matrix.json。",
    ),
}

FUNCTIONS = {
    "prepare_context": "先确定模板源码位置与摘要，再生成检索上下文；返回的内容在规划节点使用，不是只写报告后丢弃。",
    "local_http_url": "这是纯校验函数：输入字符串，输出规范化本机URL；不满足合同直接抛异常，不发起网络请求。",
    "local_database_url": "在数据库引擎建立前完成校验，避免驱动查询参数把看似本机的URL转到别处。",
    "apply_blocks": "保护对象是原产品目录：先在隔离副本验证全部变更，只把批准且校验通过的结果复制回去。",
    "preview_blocks": "每段SEARCH必须与原文唯一匹配；预先算出的完整新文本是检查Aider实际执行结果的依据。",
    "_verify_in_daytona": "成功不止看命令退出码，还要求本次沙箱成功删除；异常路径同样写回执并尝试清理。",
    "install_loopback_guard": "先保存原DNS函数再包装它，并安装连接审计；只应在专用SDK进程执行，不能封住平台合法的大模型请求。",
    "create_app": "定义并返回FastAPI应用对象；内层带路由装饰器的函数在对应HTTP请求到达时调用，而不是定义时立即执行。",
    "render": "生成物完全由正文源文件和实际源码计算；检查模式比较整份结果，不允许手动修改生成手册来掩盖源码不同步。",
    "restore": "先验证所有源码块与目标路径，再向空目录写入；这一步本身不执行任何写出的项目代码。",
    "auth": "用本机Dex真实签发的JWT访问本机API创建密钥，不伪造token，也不向云身份服务注册账号。",
    "images": "先在本机从固定源码或校验后的同版本发布文件构建Daytona，再锁定Image ID；其他基础依赖记录Registry摘要。启动对照两份锁且禁止自动拉取替代版本。",
    "build_images": "确认Docker是本机Linux x86_64后，从固定Git对象导出临时上下文；构建在本机进行，返回可审计的镜像ID与来源哈希。",
    "recipe": "先验证上游Dockerfile完整前像的Git对象哈希，再加入禁用云构建、远程缓存和遥测的环境变量；不匹配即停止。",
    "download_runner": "发布文件大小与SHA256固定写在源码中，下载时逐块累计、校验通过才原子落盘；已有损坏文件不能执行。",
    "relay": "本机入口只按固定端口选择内部服务，逐字节转发并保留半关闭语义；不解析用户传入URL、目标地址或模型密钥，超时与退出时关闭两侧连接。",
    "wait_for_registry": "检测宿主机127.0.0.1上的真实Registry响应，而不是只检查容器存在；限时重试失败即停止，不上传到云端仓库。",
    "build_storage": "从MinIO独立的固定提交导出干净源码，在本机编译对象存储，镜像附上对应源码与许可证；返回来源指纹而不是信任可变的在线镜像标签。",
    "snapshot_image": "构建上下文只有Dockerfile与产品依赖文件，不含模型Key、平台源码或用户数据库。镜像进入本机Registry供本机Runner读取。",
}


FUNCTION_OVERRIDES = {
    (
        "workbench/api.py",
        "auth",
    ): "核对当前工作台HTTP请求的本机访问令牌；它不是产品用户登录，也不联系Dex或大模型供应商。",
    (
        "workbench/product_sql.py",
        "render",
    ): "根据同一Plan建立SQLAlchemy元数据，再分别编译SQLite/PostgreSQL的可读DDL；写出SQL用于审查，不在此函数中连接或修改数据库。",
}


def parse(content):
    # PEP 758 syntax is valid on Python 3.14. Normalize only this ANALYSIS copy
    # so the standard-library book builder is deterministic on older interpreters.
    normalized = re.sub(
        r"(?m)^(\s*except )([A-Za-z_][\w.]*(?:,\s*[A-Za-z_][\w.]*)+)(:)", r"\1(\2)\3", content
    )
    return ast.parse(normalized)


def segment(content, node, limit=110):
    value = ast.get_source_segment(content, node) or type(node).__name__
    value = " ".join(value.split()).replace("|", "\\|")
    return value if len(value) <= limit else value[:limit] + "…"


def definitions(node, prefix=""):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = prefix + child.name
            yield name, child
            yield from definitions(child, name + ".")
        else:
            yield from definitions(child, prefix)


def body_nodes(node):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        yield child
        yield from body_nodes(child)


def purpose(name):
    path = Path(name)
    if name == "workbench/__init__.py":
        return (
            "包入口",
            "导入workbench时只关闭继承的托管遥测，不立即启动HTTP服务、创建数据库或调用模型。",
            "所有workbench子模块首先经过此入口；数据库初学步骤因此不依赖未来API骨架。",
        )
    if name.startswith("workbench/") and path.stem in MODULES:
        return MODULES[path.stem]
    if name.startswith("templates/business/"):
        if role := BUSINESS_FILES.get(name.removeprefix("templates/business/")):
            return role
        return (
            "合同驱动的业务运行与原生界面模板",
            "此文件被对应适配器写入实际生成产品。通用策略解释有限合同，框架适配保留其认证/ORM/事务/组件；服务器控制状态与负责人，事件追加，提醒与统计按权限读取。模板占位符仅由受信任生成器填充，不由用户输入执行任意代码。",
            "business_fastapi/business_yudao/business_python → 本文件 → 当前产品；完整链路由business_probe和真实浏览器验证。",
        )
    if name == "examples/requirements/customer-service.md":
        return (
            "用户原始客服需求",
            "原文保留客户管理、请求处理、协作、统计、权限和现有技术体系要求；默认决策与命名约定放在相邻补充文件，不用补充文件改写或删去原文。",
            "原文 + decisions + contract → 用户输入/真实模型 → Requirement → Plan.business；不作为预置JSON模型响应。",
        )
    if name == "examples/requirements/customer-service-decisions.md":
        return (
            "客服演示的明确默认决策",
            "将站内提醒、合成验收数据、角色范围、统计口径和三套原生风格明确写入需求；它是可见输入，不是失败后暗中降低要求的补丁。",
            "customer-service.md之后输入 → 需求事实与设计 → 三模板独立验收。",
        )
    if name == "examples/requirements/customer-service-contract.md":
        return (
            "客服黑盒验收的字段与命名约定",
            "明确实体、角色、字段、关系、状态、提醒和指标的实施决策；保留自然语言约束，由真实模型构造并校验Plan，禁止拿固定样例替代模型。",
            "原始需求/默认决策后追加 → ModelGateway → require_customer_spec → 三模板黑盒用例。",
        )
    if name.startswith("examples/"):
        return (
            "可审查的需求与完整合同验收样例",
            "自然语言说明目标，JSON计划逐项登记实体、字段、关系、角色、转换和指标。它用于确定性验收，不是生产模型失败后的隐藏答案；改需求需修改并重新批准相应合同。",
            "按正文验证Plan → ci_native_bundled --spec → 真实原生工具验收；该文件随教材一并还原。",
        )
    if name.startswith("templates/product/"):
        return (
            "独立基础产品的组成文件",
            PRODUCT.get(
                path.name,
                "这是成品自有的配置、迁移或页面；生成器把它复制到交付目录，由产品启动器和应用读取，不通过工作台动态加载。",
            ),
            "generator复制 → 产品start.py/app.py；verification在独立环境复验。",
        )
    if name.startswith("workbench/web/"):
        return (
            "工作台浏览器界面",
            "HTML提供控件与容器，CSS控制布局，JavaScript绑定事件并调用/api接口。界面先保存技术栈选择，再创建运行、读取状态、回答关卡或委托智能推荐；认证令牌只发给同一本机工作台。",
            "网页事件 → api路由 → Store/Runtime → 状态JSON → 页面重新渲染；ci_guided_browser。",
        )
    if name.startswith("templates/frontends/"):
        return (
            "交付给产品的前端选项",
            "轻量页面围绕产品规格显示字段和查询条件；注册登录后才请求业务API。清除筛选必须同时重置控件和查询状态，不能只隐藏标签；API-only模板则不需要管理页面。",
            "Selection → generator选取前端 → 产品HTTP/业务路由；verify-business-browser和test_business_python_browser。",
        )
    if name.startswith("templates/deployment/"):
        return (
            "原生独立交付启动器",
            "该文件随成品复制，负责本机数据库初始化、业务/菜单SQL恢复和前后端启动。helper文件来自portable.HELPERS的明确清单，不允许从原开发目录隐式导入。",
            "portable.build_native_delivery → 新目录运行start.py → 新数据库复验。",
        )
    if name.startswith("migrations/"):
        return (
            "工作台数据库迁移",
            "Alembic按revision/down_revision的依赖顺序执行；upgrade创建当前结构，downgrade描述逆操作。迁移表达结构，不是删除用户数据的排错手段；数据库模型、迁移和Store查询应保持一致。",
            "alembic.ini → migrations/env.py → versions → Store使用这些表。",
        )
    if name.startswith("tests/"):
        return (
            "可重复的验收用例",
            "pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。",
            "阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。",
        )
    if name.startswith("scripts/") and path.name in SCRIPT_ROLES:
        return SCRIPT_ROLES[path.name]
    if name.startswith("scripts/"):
        return (
            "本机维护、构建或集成验收入口",
            "main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。",
            "终端python -m " + name[:-3].replace("/", ".") + "；完整命令及成功条件见正文对应章节。",
        )
    if name.startswith(".github/workflows/"):
        return (
            "可复现的自动化验收配置",
            "on决定何时触发，jobs定义隔离机器，steps按顺序安装锁定依赖并运行上文相同脚本。矩阵是不同操作系统/模板的重复验证，不能重复计算为新增独立用例；上传的报告不应含凭据。",
            "与本机同一脚本；GitHub Actions仅作为开发验收服务，不是产品运行依赖。",
        )
    if name.endswith("uv.lock"):
        return (
            "精确依赖锁",
            "pyproject声明允许的依赖，uv.lock记录本次可复现安装的具体版本、平台条件及下载哈希。先抄写对应pyproject再完整保存此文件，使用uv sync --locked；不要为了跳过报错随意删锁。",
            "平台、Aider和产品各有独立环境与锁，不能混用Python3.12和3.14依赖。",
        )
    if name == "tools/daytona/runner-entry.sh":
        return (
            "本机Runner启动顺序与退出清理",
            "在DinD完成命名空间准备后，仅启动Unix socket上的本机Docker；限时检测daemon就绪再启动Runner，TERM/INT或Runner退出时清理子进程。没有远程Docker或云端回退。",
            "runner.Dockerfile → dind → runner-entry.sh → dockerd就绪 → 固定版本Runner。",
        )
    if name == "tools/daytona/runner.Dockerfile":
        return (
            "本机Runner服务镜像",
            "以固定Docker-in-Docker运行环境装入已经验证大小和SHA256的v0.190.0 Runner发布文件；入口同时启动本机Docker daemon与Runner。私有registry登记为本机不安全HTTP仓库，不指向公网。它不是产品快照。",
            "daytona_build.download_runner → build_exported → daytona_local.images/up → Runner管理本机沙箱。",
        )
    if name == "tools/daytona/minio.Dockerfile":
        return (
            "本机对象存储服务镜像",
            "第一阶段在固定Go编译器中校验并编译固定MinIO源码；第二阶段只复制运行二进制、对应源码、许可证和依赖清单。数据写入独立持久卷；更新检查关闭，端点仅供本机开发网络使用。",
            "daytona_build.build_storage → images.lock → daytona_local.up → API/Runner使用本机S3存储。",
        )
    if name.startswith("tools/daytona/"):
        return (
            "本机Daytona的预热镜像",
            "Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。",
            "scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。",
        )
    if name == "tools/aider/offline_runner.py":
        return (
            "Aider本机禁网入口",
            "校验独立Python版本、Aider版本、依赖中Token数据与模型元数据，再安装审计钩子并调用真实CLI；--check-local-deps只做离线自检。",
            "aider_tool.command → 本文件 → Aider Repo Map/apply；tests/test_aider_offline和ci_toolchain分别验证拒绝路径与实际工具。",
        )
    if name == "tools/node/plop-runner.mjs" or name.startswith("tools/node/templates/"):
        return (
            "原生业务规则的真实Plop生成入口与模板",
            "固定node-plop执行受信任的add/modify动作，模板定义Python、Java、Vue之间一致的规则入口。请求只提供受校验数据；已有文件、锚点数量和生成集合都要匹配，不能执行用户脚本。",
            "workbench.scaffolding → no-network → plop-runner → 实际规则文件/表单挂载；native_coding接着验证候选。",
        )
    if name.startswith("tools/node/upstream/"):
        return (
            "固定的Continue开源全文索引组件及许可证",
            "TypeScript源码原样保留，manifest记录上游提交、Git对象哈希与SHA256，构建前逐个验证。这里只嵌入全文索引组件，不加载Continue的IDE、账户或托管服务；LICENSE必须随源码保留。",
            "npm run build --prefix tools/node → esbuild绑定本机host → continue_index调用；独立SQLite缓存。",
        )
    if name.startswith("tools/node/"):
        return (
            "本机Node索引运行边界",
            "package-lock固定安装依赖；build校验上游源码并编译工具，host用Node内置SQLite提供数据库接口，runner只接受有界JSON文件协议，no-network在进程启动时拒绝网络接口。源码片段只写入检索库，不被执行。",
            "先npm ci再npm run build；Python continue_index校验构建回执并调用runner；test_continue_index与ci_toolchain。",
        )
    if name.startswith("tools/embeddings/"):
        return (
            "真实本机向量模型的独立验证环境",
            "单独锁定向量模型运行依赖，避免大体积机器学习依赖混入平台与Aider环境。安装和公开模型权重下载是准备阶段，向量推理必须留在本机；不能用协议模拟响应冒充模型实际运行。",
            "对应本机向量验收脚本 → 独立依赖环境与本地权重 → retrieval向量检索证据。",
        )
    if name.startswith("tools/aider/"):
        return (
            "Aider独立运行环境",
            "固定Python3.12和Aider版本，避免它的依赖影响Python3.14平台；平台通过子进程运行这个环境的CLI，不把它导入平台解释器。",
            "uv sync --locked --project tools/aider --python 3.12 → workbench.aider_tool。",
        )
    if name.startswith("templates/vendor/"):
        return (
            "第三方源码来源与许可证",
            "模板属于第三方依赖。manifest记录固定提交、归档哈希、逐文件内容摘要及排除项；LICENSE原样保留。只从教材也可以用vendor_templates --fetch重建源码归档，不需要复制本仓库已有ZIP。",
            "scripts/vendor_templates.py → manifest/ZIP → workbench/vendor.py → 原生生成器。",
        )
    if name.startswith("docs/images/"):
        return (
            "真实浏览器截图的来源与验收边界",
            "provenance记录模板、Actions运行、平台与上游源码提交以及各PNG的原始SHA；summary保留该历史运行的真实模型与完整工作流结果。它们不是当前提交或其他模板的通过证据。",
            "成功运行的原图与回执 → 客服正文图注 → 附录逐字节还原与哈希测试。",
        )
    if name.startswith("docs/"):
        return (
            "本教材正文的源文件",
            "上文正文就是这些源文件拼接后的内容。它们也收录在附录中，使从教材还原出的项目能再次生成逐字一致的完整教材，而不是只有一次性的代码快照。",
            "scripts/build_handbook.py的GUIDES → 正文 → 完整源码附录。",
        )
    return (
        "项目根配置或说明",
        "按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。",
        "先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。",
    )


def notes(name, content):
    title, logic, relation = purpose(name)
    out = f"**作用：{title}。** {logic}\n\n**对应关系：** {relation}\n\n"
    out += "**如何编写：** 新建与标题完全相同的相对路径，完整保存下面代码块；不要复制围栏标记。以下行号从代码块第一行起计，行号不属于文件内容。\n\n"
    if not name.endswith(".py"):
        return out
    try:
        tree = parse(content)
    except SyntaxError:
        return out + "此文件包含运行时专用语法；依照正文使用Python3.14，完整实现见下方源码。\n\n"
    imports = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    own = sorted(set(i for i in imports if i.startswith(("workbench", "scripts", "."))))
    if own:
        out += (
            "**先有这些模块：** "
            + "、".join(f"`{v}`" for v in own)
            + "。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。\n\n"
        )
    rows = sorted(definitions(tree), key=lambda pair: pair[1].lineno)
    if not rows:
        return out + "**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。\n\n"
    out += "**逐个入口与控制逻辑：**\n\n"
    for qualified, node in rows:
        line = f"L{node.lineno}–L{node.end_lineno}"
        if isinstance(node, ast.ClassDef):
            fields = [
                n.target.id
                for n in node.body
                if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
            ]
            bases = ", ".join(segment(content, n, 80) for n in node.bases) or "object"
            out += f"- `{qualified}`（{line}）：继承`{bases}`。"
            if fields:
                out += (
                    "声明的数据项为"
                    + "、".join(f"`{x}`" for x in fields)
                    + "；类型约束/数据库列参数以完整定义为准。"
                )
            else:
                out += (
                    "把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。"
                )
            out += "\n"
            continue
        params = [
            a.arg
            for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            if a.arg not in ("self", "cls")
        ]
        if node.args.vararg:
            params.append("*" + node.args.vararg.arg)
        if node.args.kwarg:
            params.append("**" + node.args.kwarg.arg)
        out += f"- `{qualified}`（{line}）：" + (
            "接收" + "、".join(f"`{p}`" for p in params) + "。"
            if params
            else "不接收显式业务参数，从已配置对象/模块读取依赖。"
        )
        out += FUNCTION_OVERRIDES.get((name, node.name), FUNCTIONS.get(node.name, ""))
        doc = ast.get_docstring(node)
        if doc:
            out += " 源码说明：" + " ".join(doc.split())[:200] + "。"
        body = list(body_nodes(node))
        calls = list(
            dict.fromkeys(segment(content, n.func, 65) for n in body if isinstance(n, ast.Call))
        )
        controls = [
            n for n in body if isinstance(n, (ast.If, ast.For, ast.While, ast.Raise, ast.Assert))
        ]
        if controls:
            descriptions = []
            for part in controls[:8]:
                if isinstance(part, ast.If):
                    value = f"L{part.lineno}按`{segment(content, part.test, 85)}`分支"
                elif isinstance(part, ast.For):
                    value = f"L{part.lineno}遍历`{segment(content, part.iter, 65)}`"
                elif isinstance(part, ast.While):
                    value = f"L{part.lineno}在`{segment(content, part.test, 65)}`成立时循环"
                elif isinstance(part, ast.Assert):
                    value = f"L{part.lineno}断言`{segment(content, part.test, 85)}`"
                else:
                    value = f"L{part.lineno}抛异常，停止当前正常路径"
                descriptions.append(value)
            out += " 控制顺序：" + "；".join(descriptions) + "。"
            if len(controls) > 8:
                out += "后续分支沿下方源码相同行号继续阅读。"
        if calls:
            out += (
                " 调用"
                + "、".join(f"`{v}`" for v in calls[:9])
                + ("等" if len(calls) > 9 else "")
                + "。"
            )
        returns = [n for n in body if isinstance(n, ast.Return) and n.value]
        if returns:
            out += (
                " 返回路径："
                + "；".join(f"L{n.lineno}的`{segment(content, n.value, 90)}`" for n in returns[:3])
                + "。"
            )
        elif any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in body):
            out += "使用yield把资源/结果交给调用方，继续执行后续清理语句。"
        else:
            out += "没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。"
        out += "\n"
    return out + "\n"
````
