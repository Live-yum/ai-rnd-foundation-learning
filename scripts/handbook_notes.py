"""Teaching notes tied to real source lines; no remote model or generated pseudo-code."""

import ast
import re
from pathlib import Path

# Each module has a distinct architectural job. These explanations accompany,
# rather than replace, the complete and SHA-checked source below them.
MODULES = {
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
        "flow → verify_basic/package_basic → templates/product/verify.py；test_news_delivery。",
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
        "先确认专用本机数据库，再复制固定源码、初始化种子并生成环境；install_backend准备依赖与构建，running_backend管理进程存活和退出。兼容改动检查原文并记录，不静默忽略失败。",
        "native_lab/native_delivery/portable → backend环境 → 本机PG/Redis/Java或Python。",
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
        "导出原生种子、增量业务表和菜单SQL，复制启动器所需全部HELPERS，包括本机策略模块。verify_native_delivery在另一个新的本机数据库恢复并启动前后端，确认没有导入原工作台或复用原生成数据库。",
        "managed_package → portable → templates/deployment；test_native_delivery_boundaries。",
    ),
    "requirement_coverage": (
        "保留用户事实并检查可执行需求覆盖",
        "reconcile合并已确认事实，后续模型省略不等于用户删除；替换要有当前真实用户更正原文。coverage_gaps把结构化字段义务、数据归属及可识别的明确约束与Plan逐项比较，设计漏项就阻塞，不让规划模型自行宣布已覆盖。",
        "flow.analyse保留事实 → Requirement.field_requirements → flow.design → coverage_gaps；test_requirement_coverage。",
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

PRODUCT = {
    "app.py": "FastAPI产品路由：从spec.json建立实体接口；依赖先验证产品登录，再在每次查询中施加owner_id范围。网页不能直接访问数据库，也不能指定另一个用户作为owner。",
    "schema.py": "产品数据库及字段合同：按spec.json创建运行表模型与校验规则；独立产品也拒绝远程数据库。字段类型同时决定请求校验、SQL列类型、序列化和查询筛选行为。",
    "auth.py": "产品自己的账号密码与会话：加盐口令派生、会话令牌摘要、过期和身份读取；这里的产品登录不是工作台访问令牌，更不是大模型API Key。",
    "rules.py": "交付给用户的受限规则解释器：与生成时采用相同的允许表达式和输入输出合同，不使用eval或任意Python执行。",
    "verify.py": "真实产品验收程序：创建测试账号调用HTTP接口，再根据simple-admin选择启动同目录verify-browser.cjs；缺浏览器或逐规格检查缺项都失败，api-only明确记为不适用。与app.py分离，不能因应用自称成功就通过。",
    "verify-browser.cjs": "逐规格真实Chromium验收：页面注册登录、遍历全部实体和字段，检查CRUD、长度拒绝、搜索/组合筛选/含边界日期、用户隔离和退出重新登录；不注入登录Token或mock接口，输出明确checks与页面错误。",
    "start.py": "成品自包含入口：在产品目录安装自己的锁定依赖，准备本机SQLite或专用PostgreSQL，执行迁移后启动HTTP服务；不调用模型，不要求原工作台目录。",
    "custom_rules.py": "唯一允许自动定制的业务规则文件；生成前后的约束、例子与SHA由平台检查。其他身份、存储和启动代码不开放给模型任意编辑。",
    "spec.json": "该文件是模板示例规格，运行时由已批准Plan生成具体成品规格；不要把示例实体名称硬编码到平台通用生成流程。",
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
            "Selection → generator选取前端 → 产品HTTP路由；资讯浏览器测试。",
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
        if node.name in FUNCTIONS:
            out += FUNCTIONS[node.name]
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
