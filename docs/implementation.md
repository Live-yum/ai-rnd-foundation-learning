# 逐文件实现讲解：把空文件夹变成完整系统

这一部分回答“为什么要这样写”，完整源码区回答“到底写哪些字符”。两者描述同一份实现。不要先寻找一个骨架项目，也不要把文件名当作下载链接：每个文件都在完整源码区给出全文。文件很多不是因为需要许多个智能体，而是把用户输入、数据库事务、模型推理、文件操作和真实验收分开，避免一个环节的错误变成另一个环节的假成功。

## A. 先学会读本书的代码

### A.1 值、变量、列表与字典

`title = "客服平台"`把一段文字放到变量title中。`count = 3`是整数，`enabled = False`是布尔值，`None`表示没有值。它们不能随意互换：数量0不是空值，布尔False也不是“没填写”。本系统专门测试这两个边界。

`fields = ["title", "body"]`是有顺序的列表；`{"title": "客服请求", "required": True}`是按键取值的字典。`data["title"]`要求键存在，缺少时会报错；`data.get("title", "")`允许不存在并提供默认值。不能为了避免报错，给本来必需的批准信息随意设True。

Python代码中的`if`是条件，冒号后缩进的行只有条件成立才执行。`for`逐个处理列表元素。`return`结束当前函数并返回结果，`raise`结束正常流程并发出错误。`try/except/finally`分别表示尝试执行、处理指定错误、无论成功失败都执行清理。本地Daytona删除沙箱就在finally里；它不是“仅成功时才清理”。

### A.2 函数、类、模块和import

`def digest(data):`定义一个函数，输入名叫data；函数体的缩进不能丢。定义函数通常不会立刻执行函数体，写`digest(value)`才会调用它。`class Plan(Contract):`定义一种具有字段和校验规则的数据类型；`Plan.model_validate(value)`才把外部数据变成经过检查的计划。

一个`.py`文件通常是一个模块。`from workbench.domain import Plan`表示从本项目workbench文件夹的domain.py导入Plan。`from pathlib import Path`是Python标准库，不需要自己编写pathlib.py；`from fastapi import FastAPI`是安装在`.venv`中的第三方包，由pyproject和uv.lock声明。不要创建`json.py`、`typing.py`、`httpx.py`这些与依赖重名的文件。

`workbench/__init__.py`告诉解释器这是包，并在本实现中关闭托管遥测。它只依赖标准库实现的local_only模块，不启动Web服务器、不创建模型连接、不修改数据库。`if __name__ == "__main__":`让脚本只有作为入口运行时才执行main，导入它做测试时不自动启动服务。

### A.3 参数、注解和严格校验

`def local_http_url(value: str) -> str:`中的str说明输入输出应为文字。Python注解本身不等于运行时安全检查，函数仍然要验证协议、主机名、端口和查询参数。Pydantic把输入字典转换成明确的数据模型；`extra="forbid"`表示不接受未定义字段，防止客户端多传一个`role="assistant"`或`approved=true`就改变权限。

`StrictBool`要求真正的True/False，不能把字符串`"false"`误当成批准。`Field(min_length=1)`限制空文字，`Literal[...]`限定选项集合。校验不是把错误输入偷偷改为成功输入，而是让用户看见哪个约束不满足。

### A.4 路径、字节、哈希和JSON

`Path(__file__).resolve()`得到当前源码文件的实际位置，避免从另一目录启动后把数据库写到错误地方。`read_text(encoding="utf-8")`读取文字；`read_bytes()`读取原始字节。JSON只能保存通用的数字、文字、列表、字典等数据，不能保存正在运行的Python函数。

SHA-256是内容指纹：相同规范化内容得到相同指纹，内容变动会产生不同指纹。它不是加密，也不能替代访问令牌。平台用它绑定规格、索引版本、文件前像和ZIP；数据库密码依然必须保密，不能因为“只存了某个哈希”就公开原始密码。

### A.5 同步、异步与资源关闭

`with engine.begin()`表示进入一个数据库事务：正常结束提交，异常结束回滚。`with`不是“后台执行”，而是资源生命周期管理。`async`函数可以在等待网络等操作时让出执行机会；本平台的重型工具仍由Worker推进，不在一个HTTP请求里等待整个Maven构建。

FastAPI的lifespan在服务启动和退出时管理数据库/Worker。LangGraph的interrupt则是业务暂停点：让系统保存当前状态并等待明确决定。浏览器关闭、HTTP断开、业务暂停和进程崩溃是四件不同的事，因此要分别处理。

## B. 建立清晰的文件创建顺序

以下“创建”都是在空项目中按完整源码区写出整个文件，不是下载一个已经实现好的模块。单个文件可以先做语法检查；只有一组依赖写齐后才执行这一组测试。

| 组 | 先写的文件 | 这一组完成后的可观察结果 |
|---|---|---|
| 0 工具与项目 | `.python-version`、`pyproject.toml`、`uv.lock`、`.env.example`、`.gitignore`、`.gitattributes`、`README.md`、`workbench/__init__.py`、`workbench/local_only.py` | uv创建独立`.venv`；尚未启动服务或调用模型 |
| 1 数据契约 | `settings.py`、`business_contracts.py`、`business_capabilities.py`、`catalog.py`、`domain.py`、`errors.py` | 能把合法字典转成Plan；非法字段、技术栈组合和非本机工具地址被拒绝 |
| 2 数据库 | `store.py`、`alembic.ini`、`migrations/`全部文件；`tests/conftest.py`、`test_contracts.py`、`test_store.py` | 临时数据库能迁移、保存项目和事务回滚；此时完全不需要api.py或runtime.py |
| 3 需求与模型 | `conversation.py`、`llm.py`、`requirement_coverage.py`、`recommendation.py` | 长期会话保存原事实；模型请求有角色路由、预算、缓存和严格响应格式 |
| 4 安全与源代码 | `filesystem.py`、`tools.py`、`vendor.py`、`scripts/vendor_templates.py`、`templates/vendor/`文本清单/许可证 | 能从固定第三方源码生成本机ZIP，再安全解压；没有任意命令入口 |
| 5 上下文 | `symbols.py`、`knowledge.py`、`retrieval.py`、`continue_index.py`、`context_mcp.py`、`toolchain.py`、`tools/node/`全部文本文件 | Java/TS/Vue/Python符号和源码行号可检索；只读MCP共享同一索引 |
| 6 产品 | `templates/product/`全部文件、`templates/frontends/`全部文件、`generator.py`、`product_sql.py`、`business_python.py`、`templates/business/common/policy.py`、`rules.py`、`coding.py`、`aider_tool.py` | 已批准Plan可确定性生成独立产品；只有受限规则文件可以由模型参与修改 |
| 7 验收 | `verification.py`、`postgres_lab.py`、`sandbox.py`、`daytona_worker.py`、本机Daytona脚本和Dockerfile | 本机真实验收、可选隔离复验以及清理失败阻止交付 |
| 8 原生全栈 | 全部`native*.py`、`business*.py`、`portable.py`、`portable_checks.py`、`templates/deployment/`、`templates/business/`、两套business浏览器脚本 | 原框架生成、菜单/权限挂载、前端/浏览器验证及独立新库启动 |
| 9 串联 | `flow.py`、`runtime.py`、`api.py`、`cli.py`、`workbench/web/` | Web和CLI共用同一持久状态流程，能够从需求到下载 |
| 10 可重复验证 | `tests/`剩余文件、`scripts/`剩余文件、`.github/workflows/`、`docs/`、手册构建脚本 | 能运行完整回归，能由本书重新建立代码，再生成字节一致的本书 |

模块之间允许引用后面将创建的模块，所以“文件能保存”不等于“马上能运行”。先看完整源码区自动列出的本项目import关系，再补齐组内依赖。不要用`pass`或删掉import来让中间状态伪装成完成。`tests/test_learning_order.py`会把第一组数据库课的最小文件集复制到新目录，确认这一阶段没有暗中依赖尚未编写的API和Worker。

## C. 第一条完整数据流：用户如何建立一个任务

### C.1 从页面到输入对象

`workbench/web/index.html`定义选择框、输入框、按钮和报告区，style.css决定布局，app.js负责读取值和调用API。浏览器先选后端/前端/数据库，app.js再显示需求输入区；因此系统在理解需求之前就知道允许的能力范围。

`POST /projects`把项目名称交给ProjectInput；`POST /projects/{id}/runs`把需求、template、selection和intelligent交给RunInput。RunInput调用Selection验证三件事：模板必须存在，前后端/数据库必须属于已适配组合，selection中的模板必须与请求中的template一致。客户端不能通过增加字段绕开校验。

Web和CLI不是两套业务实现。cli.py使用同一个API契约，api.py调用Store。这样在页面创建的run可以在CLI恢复，不需要复制一套聊天历史。

### C.2 为什么创建run时就要写job

Store的create_run在同一个短事务中写入Run、第一条Message及待执行Job。假设只保存Message而没保存Job，用户会看到需求已提交却永远不执行；反过来先入队后写消息，Worker可能读不到需求。因此它们必须共同提交或共同回滚。

request/_request给每次写请求绑定Idempotency-Key和输入指纹。网络重试同一请求时返回已有结果，不再创建第二个run；相同键配了不同请求体则409。它解决的是重复提交，不是用户授权。授权由平台令牌、输入类型和当前审批门共同控制。

### C.3 数据库最小实操

Project保存项目身份；Run保存技术选择、状态、预算、自动模式和结果；Message保存原始对话；Job保存待执行动作；Request记录幂等响应；Revision保存阶段内容版本；Approval绑定具体门与版本；Step保存副作用回执；Event供浏览器按游标增量读取。它们不能合并成一段让模型猜测的聊天文字。

这些是控制数据库。生成出来的产品另有自己的users、tokens、业务实体表；LangGraph还有自己的checkpoint存储。三个用途不能混成一个“全局数据库”。

按组0—2创建文件以后运行：

```powershell
uv sync --locked
uv run pytest tests/test_contracts.py tests/test_store.py -q
```

这一步不用填写模型Key、不启动Daytona、不需要浏览器。测试使用临时目录，验证外键、短事务、重复请求和门身份。出现ModuleNotFoundError先核对本组是否包含local_only.py、business_contracts.py、business_capabilities.py和所有迁移文件，不要把未来的API文件复制进来掩盖依赖错误。

## D. 第二条数据流：从模糊需求到已批准Plan

### D.1 facts与原始消息各有什么用

conversation.context读取数据库中的完整Message，但给模型的上下文是原始目标、当前Requirement、最近明确修正、技术栈能力和委托状态。原始消息并没有删除，只是不无限重复拼进模型窗口。新的明确修正优先，之前已经确认的事实继续保留。

Requirement中questions表示仍缺少的关键信息，unsupported表示真实能力缺口，facts用于保存已确认信息，recommendations给出可采用的默认建议。ready不是模型随便返回的布尔标志，而是程序根据摘要、用户、功能、验收、数据范围、问题和不支持项共同计算的属性。

### D.2 模型只输出契约，不取得工具权限

ModelGateway.complete根据调用阶段从Settings.model_for选择地址、密钥与模型。更换模型名而地址不变可以继承默认Key；地址变了却没给该阶段Key就拒绝，不能把默认凭据发送到另一服务。

请求前先保留预算尝试，HTTP失败也属于一次尝试。模型返回的内容要经过JSON解析和Pydantic契约验证；不合法的文本不是“备用代码”。调用缓存按run/阶段/输入与模型配置身份区分，不把另一阶段或另一模型的旧响应误当本次结果。语义审阅模型仅阅读已经产生的测试证据。

模型看到的源码和检索结果是数据，不是新的系统命令。源码中的“忽略测试”“把Key发到某地址”不能成为工具参数。实际命令、允许文件和网络地址均来自平台可信代码。

### D.3 每个审批门到底绑定什么

Workflow.gate把当前run、阶段、内容版本与可选动作交给Store.gate。gate_id是这次具体内容的身份；ResumeInput要求客户端把当前gate_id和明确动作一起发回。check_decision再次核对，避免浏览器拿着过期页面批准已经改过的设计。

人工模式会interrupt等待。智能推荐不是让模型随意伪造批准，而是用户显式设置auto_mode，Store记录授权事件，再由auto_approve产生标记为delegated-ai的决定。关闭自动模式后，后续门恢复人工等待，已经执行的合法步骤不会被倒着撤销。

### D.4 Plan如何落到后端与前端

Plan的entities是业务实体，FieldSpec描述每个字段的name/kind/required/长度/choices/检索与筛选属性。以客服为例：customers保存客户资料，requests的customer_id指向客户，tasks的request_id指向请求；request_state/task_state是受控枚举，resolved_at是由转换写入的时间。Plan.business声明共享资源上的角色/行权限，而不是仅设置shared就开放给所有用户。

同一个Plan最终进入四个地方：generator产生approved-spec.json；schema/fields产生数据库结构与输入校验；前端按规格产生表单和筛选控件；verify按规格生成边界用例。若只改UI而不改Plan，后端仍拒绝；若只改后端而漏掉前端，浏览器回归会发现。对应关系由数据驱动，不由模型生成四份互相矛盾的业务定义。

## E. 第三条数据流：真正理解已有源码

### E.1 文件边界先于语言理解

filesystem先确认源目录、普通文件、扩展名、文件大小、符号链接、路径穿越和敏感名称。输出索引不能放在被索引目录里，否则索引自身会改变源目录指纹，引起无限“过期”。.env、数据库、Git元数据、依赖缓存不应成为默认模型上下文。

manifest返回`相对路径 → SHA-256`。knowledge.build_index保存每个文件的指纹及解析器版本。指纹和解析器身份都没变时复用条目；文件被删除时不再留在新索引中。检索前current_index重新校验源码摘要，防止引用已经变化的行号。

### E.2 Tree-sitter与Python AST各做什么

Python文件由标准库ast.parse读取。Java/TypeScript/JavaScript由固定版本Tree-sitter grammar解析。Vue不是单纯的TypeScript文件：symbols先定位SFC中的script段，再按相应语言解析，并把片段行号加回原始Vue文件偏移；template中的组件标签另做记录。

索引记录声明、注解、继承等可由语法直接证实的信息。它不是Java编译器，不会证明跨模块泛型或运行时调用关系完全正确。因此源码索引不能取代Maven、vue-tsc或真实接口验收。

### E.3 为什么同时需要Repo Map与检索片段

Repo Map是有预算的全局方向图，告诉模型有哪些文件、类与函数；query返回与当前问题有关的少量具体源码片段，并保留路径、起止行和内容。前者提供结构，后者提供证据。不能把一个文件名列表称为“已经理解所有代码”，也不能把全仓库无限塞进提示词。

FTS5在本地SQLite中对分块文本检索。路径/扩展名筛选先应用到候选集合，再排名，避免一百个不相关TS文件把真正的Vue页面挤出top-k。片段行号与源码核对，输出字符预算是硬限制。

### E.4 本机向量检索是明确可选项

不开启EMBEDDING_ENABLED时AST/FTS5照常工作。开启后，本机embedding模型把文本转换成数字向量，增量缓存按文本与模型身份复用，检索用融合排名结合词法和向量结果。端点只能是本机回环地址，HTTP代理和重定向关闭，响应大小与批次数受限。

这是本机模型推理，不能配置托管向量数据库或云端embedding API，也不继承聊天模型Key。prepare_context把同一检索结果接到规划阶段；CLI和Continue的MCP读取的也是这套索引。RETRIEVAL_ENGINE=continue时，continue_index桥接固定的上游FullTextSearchCodebaseIndex组件，seed_cache创建它的本机片段输入，Node适配器实际调用update/retrieve，返回结果交给融合器。未选择时保留无需Node的默认实现；不要把MCP桥接误称为索引算法，也不要把组件测试称为IDE界面测试。

## F. 第四条数据流：生成代码但不执行任意模型程序

### F.1 确定性生成器写出什么

generate_basic先验证Plan和Selection，再复制本书中的产品模板，写入冻结规格、技术选择、迁移、SQL与说明。复制模板不是让LLM重新写认证代码；它保证每个产品继承已经测试过的登录、行隔离、字段校验与搜索逻辑。

product_sql使用同一数据库元数据输出可读DDL。冻结迁移说明首次启动如何建表。正常启动只运行迁移，不让用户先手工执行DDL再执行迁移造成重复建表。SQL文件还用于审查和原生独立交付的结构恢复。

### F.2 为什么模型只能改custom_rules.py

基础字段长度、日期、枚举和普通筛选已有确定性实现，不需要模型改代码。只有Plan中明确提出单条记录的额外业务规则时，coding或Aider才参与写custom_rules.py。输入附带允许与拒绝示例，输出必须匹配当前文件SHA。

rules不是`import custom_rules`后执行任意Python。它解析有限AST，只解释允许的表达式和语句；import、任意属性访问和系统命令不在开放范围。这样模型不能通过更改认证文件、迁移或可信验证器把失败隐藏起来。

### F.3 Aider是一台本机编辑工具，不是第二条云端通道

Aider安装在tools/aider独立Python3.12环境，平台保持Python3.14，避免依赖相互覆盖。平台网关取得经过验证的SEARCH/REPLACE块；Aider CLI在临时独立Git目录执行本机应用操作，不接收真实模型Key。它由tools/aider/offline_runner.py启动，先验证锁定依赖携带的编码和元数据，再禁用联网入口；运行中的版本查询、Repo Map和编辑均不临时下载数据。依赖安装仍是明确单独的uv步骤。

编辑前检查允许路径、文件前像SHA和SEARCH原文唯一匹配。编辑后核对实际内容与平台计算的期望结果，检查没有额外业务文件被改，重新解释规则并验证正反示例，最后保留Git提交与前后指纹。模糊匹配成功、退出码0或Git产生一个commit都不是充分验收条件。

## G. 第五条数据流：产品的登录、CRUD和页面

### G.1 不混用不同身份

平台令牌用来操作研发工作台，模型Key用来访问推理服务，产品用户登录用来访问生成的业务数据。三者分别保存、分别校验。Daytona的本机API Key是第四类本机控制凭据，也不能作为模型Key或产品登录密码。

产品app.py中的password_hash为密码加入随机salt并使用PBKDF2-HMAC-SHA256派生值；数据库不存明文密码。登录比较使用hmac.compare_digest。issue_token生成随机令牌，只把其SHA-256和有效期入库；actor检查令牌指纹、期限并返回用户ID。认证逻辑在app.py中，不需要另找一个本书未提供的auth.py。

### G.2 为什么越权检查必须在SQL条件中

新增记录的owner_id来自actor，不取客户端传入值。列表、详情、修改和删除把当前owner_id放进SQL条件中。即使用户猜中另一条记录的ID，也不能绕开归属条件。前端隐藏按钮只是交互，真正边界在后端。

字段名来自经过批准的实体白名单，值通过SQLAlchemy绑定；不拼接客户端任意列名或SQL片段。fields对整数/布尔/日期/枚举做严格输入处理，querying把关键词、单值筛选和日期上下界组合成明确条件。

### G.3 浏览器为什么会“清除后又出现旧结果”

浏览器请求可能乱序返回：请求A较早发出但较晚返回，请求B较晚发出却先返回。前端用请求序列或失效标记避免A覆盖B。清除筛选不仅清空输入框，还要清空参与请求的状态。自动化浏览器会真实操作控件、观察网络与结果，而不是只断言HTML里有一个按钮。

### G.4 独立产品从哪里启动

下载ZIP后，新目录中的start.py调用自己的uv.lock安装依赖，再运行manage.py迁移并启动app。它不导入原研发平台，不需要原模型账户。SQLite产品把数据留在产品自己的.data；PostgreSQL产品使用本机服务或只属于自己的Compose项目。重复启动不删除数据卷，也不重新设置已有管理员密码。

## H. 第六条数据流：验证、隔离复验和交付

### H.1 平台相信工具证据，不相信“我测过了”

verification启动产品独立进程，通过真实HTTP检查注册、登录、未认证拒绝、两用户隔离、CRUD、字段边界、搜索/筛选和进程重启。验证器来自平台可信模板，不是刚刚由模型改写的测试文件。

PG验收必须使用真实本机PostgreSQL，不能换成SQLite后仍标注PG通过。postgres_lab只创建带随机身份的临时测试库，不能把用户自己的生产库当作测试夹具。

### H.2 修复循环为什么有限

after_verify只有在额外业务规则、错误类型属于code且未超过max_repair_attempts时才回到repair。repair只增加尝试次数，code得到错误证据再修改允许文件，然后重新verify。数据库服务未启动、依赖安装失败或密码错误不是改业务规则能解决的，必须阻止流程。

### H.3 本机Daytona不是把代码交给云端

sandbox节点先经过本机完整验收。SANDBOX_PROVIDER=local表示不加Daytona这一层，不是跳过前面的验收；选daytona时必须显式开启本机执行并配置本机控制面的Key和预热快照。

daytona_worker用独立进程运行固定SDK，输入参数走stdin而不放命令行；它关闭遥测和代理，只允许回环网络以及映射到回环的Daytona本地代理域名。即使SDK收到非本机重定向或工具代理地址也会拒绝。这个Python依赖边界不是可执行恶意本机原生代码的操作系统安全沙箱。

沙箱创建参数明确network_block_all=true，产品安装使用offline和锁文件。因此要先在安装阶段制作预热快照。唯一沙箱名称在创建请求前就写入回执，创建超时后可按同名查找并尝试删除；删除失败或回执缺失都阻止交付。外部进程被强制终止时仍须按留下的名称检查本机控制台，不能声称finally在任何操作系统崩溃中都保证执行。

### H.4 ZIP为什么还要解压再验一次

开发目录可能残留缓存、数据库、上一次构建结果或依赖。package_basic生成ZIP后在新目录校验清单和哈希，再运行独立验证，证明交付包确实包含需要的代码。delivery门在批准时再次核对ZIP哈希；审批期间被修改的包不能下载。

原生产品还要在另一套新数据库恢复原生种子、业务DDL和菜单，启动后端与前端后再检查。portable导出的菜单是生成前后变化的菜单项，不是把开发库中的测试用户、密码和业务记录一股脑打包。

## I. 图、Worker、数据库如何合作

Workflow.State只保留run身份、需求/计划版本、尝试次数、有界上下文和回执。源码ZIP和整个仓库不应放进状态字典。compile把可信函数登记为节点并明确连边；模型不能返回一个节点名称就改变图的连接。

```text
HTTP/CLI提交
    ↓ 短事务保存Message、Run、Job
Worker认领Job
    ↓ 同一个run_id作为LangGraph thread_id
analyse → requirements → source_context → plan → design
                                             ↓
generate → code → verify ──可修复代码错误──→ repair → code
                    ↓通过
                 sandbox → model_review → package → delivery
                                                      ↓批准且哈希一致
                                                    READY
```

requirements可能带着补充回答返回analyse，design修改可能重新规划，reject进入终态。流程图的“通过”来自程序条件，不来自模型一句话。一次回答被消费后记录job身份，恢复时不能让同一回答又批准下一道门。

Runtime在本机文件锁和可选PG advisory lock下启动单Worker。文件锁阻止同一数据目录中的第二个Worker，PG锁额外阻止两个目录争用同一PG控制库。SQLite checkpoint连接和Store连接各有生命周期；关闭一个并不表示另一个也已关闭。

## J. 逐组运行与故障定位

| 你刚完成的组 | 执行的命令 | 失败时首先核对 |
|---|---|---|
| 契约/数据库 | `uv run pytest tests/test_contracts.py tests/test_store.py -q` | 字段名、local_only依赖、迁移文件是否齐全 |
| 模型 | `uv run pytest tests/test_llm.py tests/test_guided_models.py -q` | JSON响应契约、模型路由与密钥继承，不需要真实Key |
| 安全/源码 | `uv run pytest tests/test_safety.py tests/test_vendor.py tests/test_toolchain.py tests/test_local_only.py -q` | 固定模板ZIP是否由脚本生成；所有工具地址是否回环 |
| 产品 | `uv run pytest tests/test_business_contracts.py tests/test_business_python.py tests/test_guided_selection.py -q` | approved-spec与字段/查询/前端是否来自同一Plan |
| 流程/API | `uv run pytest tests/test_api.py tests/test_workflow.py tests/test_guided_workflow.py -q` | gate_id、显式布尔值、Job状态与幂等键 |
| 全部文件 | `uv run python -m scripts.build_handbook`，然后`uv run pytest -m "not postgres" -q` | 先生成唯一手册，再检查源码块与当前文件的一致性 |
| 真实工具 | `uv run python -m scripts.ci_toolchain` | Aider独立环境、实际MCP进程、源码索引，不是模型账号 |
| 手册独立重建 | `uv run python -m scripts.ci_handbook` | 文档源码块、固定第三方依赖重建、本地导入来源及重建后的完整非PostgreSQL回归 |

测试名不是“全部功能一定正确”的证明。单元测试验证契约和分支；HTTP、数据库、真实CLI、浏览器和本机自托管服务测试验证实际连接。不同证据在报告中分开，未运行的检查不得填passed=true。

## K. 只有这一份文档时如何减少抄写错误

手工学习仍按前面的组和逐文件代码区进行。为了校对大量锁文件和重复的完整源码，可以先把下面这段**仅使用Python标准库**的完整代码保存为项目目录外的`rebuild_book.py`。它不要求已有本项目脚本、不下载本项目源码、不执行提取的代码，只把经过SHA验证的源码块和截图原始字节写入一个新的空目录。图片以可折叠的Base64资源块随书收录，不需要照着界面重画，也不需要另外下载图片。还原后在项目根目录重新生成本书，正文的`docs/images/`相对图片路径即可正常显示。

```python
import base64
import binascii
import hashlib
import re
import sys
from pathlib import Path, PurePosixPath

# Windows redirected terminals may otherwise use cp1252 instead of UTF-8.
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
if len(sys.argv) != 3:
    raise SystemExit("用法: python rebuild_book.py 手册路径 新空目录")
book = Path(sys.argv[1]).read_text(encoding="utf-8")
target = Path(sys.argv[2])
if target.is_symlink() or (target.exists() and any(target.iterdir())):
    raise SystemExit("目标必须是新的空目录，不覆盖任何已有项目")
pattern = re.compile(
    r"^<!-- source-file: ([^\r\n]+) sha256: ([0-9a-f]{64})(?: encoding: (base64))? -->\n"
    r"(`{4,})[^\n]*\n(.*?)\n\4\n",
    re.S | re.M,
)
files = {}
for name, expected, encoding, fence, code in pattern.findall(book):
    relative = PurePosixPath(name)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or ":" in name
        or "\\" in name
        or name in files
        or ".git" in relative.parts
        or not relative.parts
        or relative.as_posix() != name
        or any(ord(char) < 32 for char in name)
    ):
        raise SystemExit("不安全或重复路径: " + name)
    if encoding == "base64":
        try:
            content = base64.b64decode(code.replace("\n", ""), validate=True)
        except (binascii.Error, ValueError) as exc:
            raise SystemExit("二进制块编码不合法: " + name) from exc
        if hashlib.sha256(content).hexdigest() != expected:
            raise SystemExit("二进制块哈希不匹配: " + name)
        files[name] = content
        continue
    # Fence separators are not necessarily source bytes: preserve empty files
    # and sources with or without a final newline, using the exact source SHA.
    content = next(
        (
            value
            for value in (code + "\n", code)
            if hashlib.sha256(value.encode("utf-8")).hexdigest() == expected
        ),
        None,
    )
    if content is None:
        raise SystemExit("代码块损坏: " + name)
    files[name] = content
if not files:
    raise SystemExit("文档中没有完整源码块")
if len(files) != len(re.findall(r"^<!-- source-file: ", book, re.M)):
    raise SystemExit("有未完整提取的源码块，拒绝生成残缺项目")
target.mkdir(parents=True, exist_ok=True)
for name, content in files.items():
    path = target / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8", newline="\n")
print("已校验并写入", len(files), "个文件；尚未执行代码或安装依赖。")
```

例如手册和rebuild_book.py都在下载目录，在该目录执行：

```powershell
uv run --no-project --python 3.14 python rebuild_book.py "从零实现AI研发平台_逐步实操手册_完整版.md" "$HOME/rnd-book-only"
Set-Location "$HOME/rnd-book-only"
uv sync --locked --all-extras
uv run python -m scripts.vendor_templates --fetch
uv run python -m scripts.build_handbook
uv run pytest -m "not postgres" -q
uv run rnd init
```

这条路径只以本书为本项目源代码输入。第三方库由锁文件安装，原生框架由本书中的固定SHA脚本取得，Aider与Daytona按第20章安装；没有从自己的演示仓库偷偷复制骨架。自动提取只是校对工具，不能代替理解每组代码的职责和每个真实验收的意义。

## L. 完整源码区怎么读

每个文件先给出用途、与其他模块的关系和验证方向，再给出完整文件。Python文件的函数目录标注实际起止行，列出源码中的条件、调用与返回值，帮助你把本章的业务流程定位到实现。行号由当前文件解析生成，不靠手工维护旧行号。

阅读顺序是“先懂职责，再找到函数，最后逐行看实现”。例如从Workflow.sandbox进入verify_in_daytona，再进入daytona_worker，最后到SDK；从Store.submit进入当前gate校验，再到Job入队；从产品列表接口进入querying.conditions，再回到SQLAlchemy查询。标准库/第三方库的内部实现不在本书重写，但本平台如何调用它们、传什么值、信任什么结果均给出。


## 交付前的审阅与独立恢复门禁

工具测试通过只说明这些测试实际检查的内容通过，不能证明没有遗漏已批准需求。
`Workflow.model_review`把额外语义审阅保存在运行目录的`model-review.json`中。
`observations`用于一般建议，不要求用户继续回答；`uncovered_requirements`专门记录已批准但没有实现的功能。
`require_review_clearance`只要发现后一列表非空，就记录`delivery_clearance=false`并暂停为`BLOCKED`，不生成ZIP。
即使恢复的是已经越过审阅节点的检查点，`package`入口也会再次检查，不能靠重试跳过。
关闭可选审阅不会抹去已记录的缺口；同一运行重新启用审阅并重试时，会把前一份报告连同独立验收证据交给审阅器复核。
模型审阅仍不能将失败的编译、HTTP或浏览器测试改为通过，也不保证能发现所有语义遗漏。
目前自动代码修复限于已批准的单记录规则；任意Java/Vue语义缺口尚未形成自动修复闭环，不能把“阻止错误交付”称为“自动修复全部功能”。

异常发生在两个审批节点之间时，`Runtime.tick`从实际检查点重新读取尚未消费的interrupt。
没有interrupt就保存`pending=None`，而不是复用已经批准过的设计gate。
有真实阻塞gate时仍保留它，因此需求澄清的答复和智能推荐恢复不会丢失。

原生交付的调用关系为`managed_generate → run_acceptance → managed_verify → managed_package`。
`managed_verify`既核对源码清单和验收报告的SHA，也要求`portable_restored`明确证明：
新数据库、前端启动、锁定依赖安装、独立启动器均通过，且没有复用生成数据库、导入工作台或要求模型服务。
这些值必须是JSON布尔值；缺失、字符串和整数不能冒充通过。
仅“原生成环境里能启动”不能取得运行级交付资格；依赖原数据库的产品必须停止，不能发出READY。

编写顺序是先在`tests/test_delivery_clearance.py`构造“工具通过但审阅缺口仍在”和“原生恢复证据缺失”的反例，
再实现上述两个门禁，然后执行：

```powershell
uv run pytest tests/test_delivery_clearance.py tests/test_native_managed.py tests/test_guided_workflow.py -q
uv run pytest tests/test_recommendation_recovery.py tests/test_recommendation_stage_budget.py -q
uv run python -m scripts.build_handbook --check
```

正常结果必须是全部通过。失败时先阅读断言指向的具体门槛，不得通过删除反例、跳过恢复测试或把布尔值改成固定true来继续。
原生协议测试使用固定时间戳的ZIP夹具；它仍比较原始ZIP字节，只是不依赖运行时的时钟，避免跨越ZIP时间刻度产生随机误报。
这些协议夹具不代替Actions中实际启动原生生成器、全栈应用及全新数据库的验收。

## M. 已确认的需求为什么不能在下一轮消失

`Requirement.field_requirements`保存字段级义务，例如`requests.priority`必须为必填枚举、`requests.title`的文本类型、最大长度和可搜索标记；`features`、`acceptance`与`facts`保存用户明确表达的其他条件。它们来自需求阶段，不由设计Plan反向决定。设计中的一个字段存在，不等于它的长度、日期范围和查询能力都正确。

`requirement_coverage.reconcile`先合并前次事实。后一次模型响应漏掉一项，不代表用户同意删除；需要替换时使用`RequirementChange`，包含被改的section/key、replacement和来自新用户消息的source_quote。程序核对引用确实存在并表达这项更正；模型自己写一句“用户同意”不构成证据。

需求确认后，`flow.plan`保留原验收条件，`flow.design`调用`coverage_gaps`逐项比较结构化义务与Plan。把per_user换成shared、把真实日期换成普通文字、遗漏筛选或改掉枚举，都应进入明确的设计阻塞/修正流程，不能一路生成到下载。数据归属更改尤其需要用户的实际更正。

规划输入还包含确定性生成的`field_obligations`：每项保留`field_requirements/索引`来源ID、实体/字段目标以及明确指定的属性。`false`、`0`不能当作缺失值丢掉，未指定的属性也不能凭空变成要求。重试反馈携带同一目标、属性、期望值和实际值，并同时保留原需求与上轮Plan；程序不自动改写模型Plan来伪造符合。

旧版文字条件按章节与语句绑定：标题只提供上下文，字段清单只在归属唯一时帮助确定实体；后面的“按字段搜索/筛选”只约束自己的字段列表。重复字段名如果没有明确实体范围，不推断成所有实体的共同义务。真正明确的文字条件与结构化条件冲突时仍应阻塞，不能把全部文字忽略。其余业务语义继续通过业务合同和独立审阅检查，不能靠字词命中宣称完整理解。

手工追踪一个例子：“标题必填，最多80字，可关键词搜索”。先在Requirement找到这三个条件，再在Plan中找到同一实体同一字段，核对required、max_length、searchable；最后查看产品API和浏览器对同一条件的检查。自由文字识别只覆盖已登记词汇，不能宣称程序已理解任意自然语言业务；明确的字段义务应进入结构化合同，未支持的要求保留为阻塞项。

### 结构化业务义务与离线诊断

需求分析输入直接提供实际 `BusinessSpec` JSON Schema；字段义务仍使用 `field_requirements`，不把指标、角色、关系或模板能力名称当作字段。嵌套资源的实体范围与关系的来源实体会传递给其明确字段约束，列表、按名称索引的映射和 JSON 字符串表示遵守相同边界。

业务事实按资源、关系、权限、状态流转、提醒、指标分别比较。已支持的明确同义表达可转换为规范属性；转换不修改已批准事实。完整权限矩阵默认拒绝未声明的角色或资源授权，明确行范围、禁止动作和只读约束仍需满足。指标权限绑定到指标所属实体；聚合范围不能覆盖冲突的逐指标范围。通知目录的事件与接收者集合不是自动的笛卡尔乘积，带明确实体/事件的通知规则仍逐项验证。

设计失败会把义务来源、预期动作/实体/范围及实际设计传入下一轮规划；真正遗漏的统计或处理历史授权不会被别名兼容隐藏。已留存的三个真实模型失败合同仅用于纯离线验证回归，带 `unapproved` 和 `execution_authorized=false` 标识，不能参与批准、生成或冒充真实交付。

负责人选择只要求目标角色能够以 `all` 或 `assigned` 范围读取该资源；分配者仍必须拥有该记录的 `assign` 权限。只读负责人不因此获得修改、流转、备注或统计权限，`own` 范围或无读取权限的目标不能被当作负责人。三个运行时的服务端与选择器使用相同边界。

原生后端启动前拒绝已占用端口；Linux 就绪检测先只读核对监听 socket 与本次启动的进程组，再调用 HTTP。清理只处理本次创建且仍能观测到的进程组，验证原端口释放，再在同一端口完成重启。失败诊断只记录有界的端口、进程 ID、退出码和拥有关系，不收集环境、凭据或完整进程参数。

查询谓词与结果描述分别解析：例如“搜索结果符合筛选条件”不为邻近字段开启搜索；括号中的逐字段描述保留各自必填、长度和选项约束，不借用前一个字段的数值。明确的额外文字约束与真正冲突仍会阻塞。需求中的通用状态提醒必须覆盖该实体的每一个命名转换及指定接收者，不能只命中一个转换；可执行通知仍使用具体动作名，不能把 null 当作运行时通配规则。

read_audit 与 read_history 是独立读取授权。仅有审计授权的客户记录仍可通过受当前角色行范围保护的入口查看完整不可修改审计；只有历史授权时仅返回去除快照的处理时间线。两种读取权限都不授予备注、修改或状态动作权限。

本机 Daytona 测试控制平面的 `daytona-network` 固定为私有 `172.30.240.0/24`，仍为 `internal:true`；服务成员、仅网关发布的 `127.0.0.1` 端口、禁止沙箱互联和 `network_block_all` 均不改变。固定上游版本 `01c502bb1f1ff8f2885d0cd490e043736083dca8` 的 [runner Docker client](https://github.com/daytonaio/daytona/blob/01c502bb1f1ff8f2885d0cd490e043736083dca8/apps/runner/pkg/docker/client.go) 在禁止互联时使用内层 `172.20.0.0/16`；外层不得由 Docker 动态选择到相同网段。启动前拒绝缺失、改变或重叠的 IPAM 配置；已分配冲突由 Docker 报错，不随机重试、不退回 host 网络，也不修改主机防火墙或 VPN。该约束有渲染和失败前置回归，实际启动与独立应用检查仍必须由同一最终提交的 Actions 完成。
