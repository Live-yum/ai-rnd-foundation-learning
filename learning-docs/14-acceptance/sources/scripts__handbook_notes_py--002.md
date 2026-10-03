# scripts/handbook_notes.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](scripts__handbook_notes_py--001.md)

**作用：把源码变成逐文件教学提示。** 先按具体文件职责解释输入、调用方和结果，再解析Python AST列出类/函数、行号、参数、关键分支和返回。它不执行被讲解的业务代码；手写教学章节补充业务意图与练习。

**对应关系：** build_handbook → purpose/notes → 每个源码块前的对应关系。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `purpose`（L734–L946）：接收`name`。 控制顺序：L736按`name.startswith("ui/")`分支；L765按`name == "workbench/__init__.py"`分支；L771按`name.startswith("workbench/") and path.stem in MODULES`分支；L773按`name.startswith("templates/business/")`分支；L774按`role := BUSINESS_FILES.get(name.removeprefix("templates/business/"))`分支；L781按`name == "examples/requirements/customer-service.md"`分支；L787按`name == "examples/requirements/customer-service-decisions.md"`分支；L793按`name == "examples/requirements/customer-service-contract.md"`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`name.startswith`、`roles.get`、`BUSINESS_FILES.get`、`name.removeprefix`、`PRODUCT.get`、`name[:-3].replace`、`name.endswith`。 返回路径：L757的`( "Vue 3 / Ant Design本机操作台源码", roles.get( name, "这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触…`；L766的`( "包入口", "导入workbench时只关闭继承的托管遥测，不立即启动HTTP服务、创建数据库或调用模型。", "所有workbench子模块首先经过此入口；数据库初学步骤因…`；L772的`MODULES[path.stem]`。
- `notes`（L949–L1059）：接收`name`、`content`。 控制顺序：L953按`not name.endswith(".py")`分支；L960遍历`tree.body`；L961按`isinstance(node, ast.ImportFrom) and node.module`分支；L963按`isinstance(node, ast.Import)`分支；L966按`own`分支；L973按`not rows`分支；L976遍历`rows`；L978按`isinstance(node, ast.ClassDef)`分支。后续分支沿下方源码相同行号继续阅读。 调用`purpose`、`name.endswith`、`parse`、`isinstance`、`imports.append`、`imports.extend`、`sorted`、`set`、`i.startswith`等。 返回路径：L954的`out`；L958的`out + "此文件包含运行时专用语法；依照正文使用Python3.14，完整实现见下方源码。\n\n"`；L974的`out + "**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。\n\n"`。

</details>

**创建路径：** `scripts/handbook_notes.py`；**本文件共有 2 段**。本段覆盖源文件 L734–L1059。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`23129`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/handbook_notes.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "697bd8cfff82da3f0f096363ca9cd6ad1024f3236c8757e627b632d35dbc8ada"} -->
````python
# scripts/handbook_notes.py
def purpose(name):
    path = Path(name)
    if name.startswith("ui/"):
        roles = {
            "ui/src/main.ts": "创建Vue应用并挂载顶层组件，统一导入界面样式。",
            "ui/src/App.vue": "组合本机连接、项目导航与页面路由；锁定时清空内存令牌与当前任务状态。",
            "ui/src/api.ts": "同源fetch携带内存Bearer令牌；写操作传幂等键。流读取用TextDecoder和SSEParser保留跨网络块的未完成帧，不能把每个TCP块当作一个JSON对象。",
            "ui/src/state.ts": "集中管理任务快照、事件游标、当前订阅与错误。切换运行先abort旧订阅并增加代次，迟到请求不得覆盖新任务；重连用游标去重，不重新发起模型生成。",
            "ui/src/presentation.ts": "把已验证的运行阶段、消息事件与关卡身份投影为显示状态，失败草稿和完成结果采用不同呈现。页面文案不能替代后台状态判断。",
            "ui/src/types.ts": "定义浏览器持有的项目、运行、消息与事件形状；TypeScript约束本地使用，不能替代服务端输入验证。",
            "ui/src/style.css": "定义操作台的布局、间距、响应式断点和状态样式；真实组件仍负责交互与无障碍语义。",
            "ui/src/components/RunView.vue": "显示对话、流式草稿、审批内容、阶段进度与证据；根据当前运行状态开放实际可用的回答、批准、重试和下载操作。",
            "ui/src/components/Questionnaire.vue": "按后端当前问题渲染单选、多选或文字回答，提交问题ID和选项ID；必填和自定义约束在浏览器提示后仍由后端复验。",
            "ui/src/components/SettingsView.vue": "编辑默认与分阶段模型配置；已保存密钥不回填，保存使用版本号防止覆盖另一窗口的修改。保存成功不表示连通性测试或付费模型调用通过。",
            "ui/src/components/ProjectsView.vue": "读取、筛选和打开已有项目，将导航交给上层；不在项目列表中另造创建运行的业务逻辑。",
            "ui/src/components/HomeView.vue": "接收用户需求，在提交前打开技术组合与标题确认，再调用创建项目（需要时）和创建运行接口；兼容项以服务器目录为准，重试复用幂等请求身份。",
            "ui/src/components/DataDocument.vue": "把结构化需求、计划或报告变成可阅读字段；输出作为文本显示，不执行模型提供的HTML。",
            "ui/vite.config.ts": "配置Vue编译和开发期API代理，生产资源写到workbench/web供本机FastAPI与wheel使用；开发代理不是生产部署。",
            "ui/package.json": "声明固定Vue/AntDesign及编译测试工具版本，提供dev/check/test/build命令；npm ci以相邻lock锁定完整依赖树。",
            "ui/package-lock.json": "npm依赖树的完整锁定回执；不手写各传递依赖，原样恢复后用npm ci安装。",
            "ui/tsconfig.json": "让Vue与TypeScript检查脚本、组件和测试的类型，不把类型检查通过当作浏览器交互通过。",
            "ui/index.html": "Vite开发与构建的HTML入口；源入口由编译器替换为生产静态资源引用。",
        }
        return (
            "Vue 3 / Ant Design本机操作台源码",
            roles.get(
                name,
                "这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。",
            ),
            "ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。",
        )
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
            "Vue操作台的精确构建资产",
            "由ui源码、锁文件与Vite配置生成，不手写或修改压缩代码。教材按资产字节保存；独立构建后还必须逐文件比较，不能用已有bundle掩盖源代码不可构建。",
            "ui源码 → npm run build --prefix ui → 本目录 → FastAPI静态路由及Python wheel；ci_guided_browser验证真实页面。",
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
