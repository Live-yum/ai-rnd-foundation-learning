# scripts/learning_docs_content.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.learning_docs_content.j；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/learning_docs_content.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L585。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`135523`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/learning_docs_content.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7e9a3508caf5175d7876a40945d2ede1b5e0ddbaa000949c248b38fd86716bcf"} -->
````json
// scripts/learning_docs_content.json
[
  {
    "id": "00-environment",
    "title": "项目与安装边界",
    "goal": "从真正的空目录建立可以安装的 Python 包，先验证解释器和锁文件，再接触平台入口。",
    "prerequisites": [
      "能打开终端与保存UTF-8文本；无需预装Python",
      "持有完整learning-docs目录；安装期可访问Git和uv官方来源"
    ],
    "concepts": [
      "Python解释器、虚拟环境与包不是同一事物",
      "声明依赖与锁定依赖",
      "平台目录、运行数据目录、交付目录的不同寿命"
    ],
    "steps": [
      "先写本阶段配置、锁文件和 workbench/__init__.py",
      "在该根目录安装 Python3.14 和锁定主环境",
      "核对运行解释器与基础库；不要调用尚不存在的 rnd 命令"
    ],
    "checks": [
      "Python版本必须3.14.x",
      "import fastapi、pydantic、sqlalchemy 成功",
      "没有 .env 密钥也是此站正常状态",
      "未安装postgres extra时，基础平台不应被可选原生依赖拖垮；原生执行前另行预检"
    ],
    "troubleshooting": [
      "SyntaxError先核对解释器，而非改写源码以迁就3.12",
      "锁文件不匹配先找漏抄文件，不随手 uv lock 升级",
      "网络下载失败属于安装阻塞，未获得测试结果"
    ],
    "boundaries": [
      "此站只建立开发环境，不证明应用可启动",
      "不需要模型账号、Docker、PostgreSQL、Node或Daytona服务"
    ],
    "body": "## 真正从没有工具的电脑开始\n\n本教程不要求克隆本项目源码。你需要的是这份完整 `learning-docs` 教材目录、一处准备写代码的空目录，以及终端和纯文本编辑器。编辑器任选你熟悉的工具，能创建目录、显示文件扩展名并按UTF-8保存即可；别把Word文档改名成 `.py`。基础平台可在Windows/Linux学习；原生框架和Daytona章节请使用其明确支持的Linux/WSL环境。\n\n先从 [Git官方安装入口](https://git-scm.com/install/) 选择操作系统并按官方步骤安装。Git在后面的固定上游源码获取和Aider隔离副本中需要；不必先用它克隆本项目。安装后重新打开终端，运行 `git --version` 应显示版本。若提示命令不存在，先检查安装器提示与PATH，不盲目重装Python。\n\nuv有不依赖预装Python的独立安装器。下面是 [uv官方安装文档](https://docs.astral.sh/uv/getting-started/installation/) 提供的两种入口，按自己的系统只选一条；它会下载并执行官方安装脚本，你也可以先从官方文档检查脚本内容。\n\n```bash\n# .learning/commands/00-install-uv-linux.sh\ncurl -LsSf https://astral.sh/uv/install.sh | sh\n```\n\n```powershell\n# .learning/commands/00-install-uv-windows.ps1\npowershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\"\n```\n\n安装后关闭并重新打开终端，运行 `uv --version` 应显示版本。PowerShell的这条命令为本次官方安装脚本使用相应执行策略，不需要为了教程永久关闭系统安全设置。若组织策略不允许安装，请使用组织批准的官方安装方式，不绕过限制。\n\n## 先取得解释器，再选择手写或逐站还原\n\n你还没有 `pyproject.toml` 时，也可以让uv安装Python3.14；这解决“教材还原器本身需要Python”的前置问题。在教材目录的上一级执行：\n\n```bash\n# .learning/commands/00-bootstrap-python.sh\nuv python install 3.14\nuv run --no-project --python 3.14 python -c \"import sys; assert sys.version_info[:2] == (3, 14); print(sys.version.split()[0])\"\n```\n\n应打印3.14.x。`--no-project` 表示这一条命令不寻找尚未创建的项目配置。接下来有两条都真实可行的学习路径：手写时新建 `student-project`，按本阶段源码索引创建每个文件；辅助还原时先不要创建目标目录，由教材自己的标准库脚本只还原第00站。两种方式都逐站读解释与运行检查，不需要先得到完整平台骨架。\n\n```bash\n# .learning/commands/00-restore-first-stage.sh\nuv run --no-project --python 3.14 python learning-docs/rebuild.py student-project --through 00\ncd student-project\n```\n\n此时应只有第00站登记的源文件与学习进度记录，没有API、CLI和Worker。下一站可以手写补齐，也可以从 `student-project` 目录运行下面的增量命令；它在已恢复源码匹配时新增到指定阶段，不覆盖你改过的代码：\n\n```bash\n# .learning/commands/00-next-stage-example.sh\nuv run --no-project --python 3.14 python ../learning-docs/rebuild.py . --through 01 --advance\n```\n\n这条是“开始第01站时再执行”的示例。若你有意修改了旧源码，先理解并保存自己的变更；还原器拒绝覆盖是保护，不应通过删除检查绕开。正式安装项目依赖要在第00站文件已写齐后执行下节命令。\n\n## 先认清你正在搭建什么\n\n最终平台有两种程序。第一种是研发工作台，负责保存需求、审批、调用模型和运行工具；第二种是它生成的业务产品，具有自己的依赖、用户和数据库。现在只搭建第一种程序的安装外壳。`pyproject.toml` 声明 Python 范围、依赖和 `rnd` 入口，`uv.lock` 固定实际解析结果，`.python-version` 帮终端选择解释器，`workbench/__init__.py` 让工作台成为可安装包。入口声明可以先存在，入口指向的 `cli.py` 要等后面实现；安装成功不会替你补出 CLI。\n\n按本阶段源码索引逐文件写入，不要先复制整个最终仓库。根目录是含 `pyproject.toml` 的目录；教材目录和将来的产品解压目录都不是它。保存文件使用 UTF-8，不要让编辑器暗中加 `.txt`。锁文件较长是因为依赖身份必须完整记录，它是数据，不需要当作算法逐行背诵。不要删去看起来不重要的 hash，也不要把自己重新生成的锁冒充书中同一组依赖。\n\n下面所有 `.learning/commands/...` 标记表示终端命令示例的归属，不要求保存成脚本；后面明确写“保存为”的练习才要创建文件。\n\n```bash\n# .learning/commands/00-install.sh\nuv python install 3.14\nuv sync --locked\nuv run python -c \"import sys; assert sys.version_info[:2] == (3, 14); import fastapi, pydantic, sqlalchemy; print('00 PASS: Python 3.14 and base dependencies')\"\n```\n\n最后一条应打印 `00 PASS: Python 3.14 and base dependencies`。Python3.12/3.13不是可互换环境：最终代码包含 Python3.14 的语法与运行接口，靠“我电脑有 Python”不足以判断可用。Aider 后面独立使用3.12，那是工具隔离要求，不是把平台降级到3.12。\n\n## 学会区分安装与运行\n\n`uv sync --locked` 会下载并安装可信来源的依赖；这不是把生成业务交给远程工具执行。平台设计要求业务工具在本机，允许聊天模型访问你明确配置的 HTTPS 推理服务。第三方源码快照、Python锁文件和Node锁文件解决的是不同层的复现问题，不能只保存其中一个。\n\n本阶段还没有 Store、API、CLI、模型网关。不要运行 `rnd init`、`rnd doctor` 或 `rnd start` 来检验半成品；这些命令导入后续模块，`init` 还会准备原生模板；模型未配置时可在第08站启动设置页，但此时模块尚未齐全。此时运行它们报缺模块是顺序错误，不是让你提前粘贴全部源码的理由。\n\n完成后能说清三句话：平台源码可版本管理；`.data` 是后续本机状态且不能作为源码分享；最终ZIP要去新目录和新数据库验收。此站不要放真实模型密钥，也不要建立实际业务数据。\n\n## 后面还会建立一套平台自己的Vue操作台\n\n第08站的 `ui/` 是平台控制面的Vue 3 / Ant Design源码，和第05站写入生成产品的 `templates/frontends/` 不是同一套界面。它使用Node 22与相邻 `package-lock.json`，不要在Python环境或 `tools/node` 目录里安装这套前端。初学到本阶段不必先构建所有界面；到第08站按顺序执行 `npm ci --prefix ui`、测试和构建。教材同时保留可重建源码与精确静态资产快照，快照不是需要手写的压缩代码。\n\n## Windows基础安装与原生执行依赖是两条边界\n\n`uv sync --locked` 安装基础平台；没有安装可选 `postgres` extra、因而不能 `import psycopg`，不应让Windows上的原生模板选择、能力说明或设计检查崩溃。原生设计模块必须能在基础环境导入，真正的数据库运行模块等到需要执行时再加载。不要为修复设计页的导入错误而要求每位Windows读者安装全部原生工具。\n\n实际原生全栈运行仍只在WSL2/Linux执行。到第09站进入WSL2/Linux项目目录后，安装 `uv sync --locked --extra postgres`，再检查本机工具与专用数据库；Windows和Linux不能共用同一个 `.venv`。平台先检查操作系统、PostgreSQL驱动和必需命令，再创建输出目录、容器或数据库连接。预检通过只说明依赖就绪，不能替代真正的编译、HTTP和浏览器验收。\n"
  },
  {
    "id": "01-contracts",
    "title": "配置与数据合同",
    "goal": "把自由输入限制成可核查的模板组合、需求、设计与审批数据。",
    "prerequisites": [
      "00环境安装成功",
      "完整写入local_only、settings、template_adapters、catalog、business_contracts、domain、errors"
    ],
    "concepts": [
      "Pydantic模型与确定性校验",
      "用户输入、能力目录和批准记录各有职责",
      "配置继承不能导致跨服务泄露密钥"
    ],
    "steps": [
      "从local_only的回环地址校验读到Settings.model_for",
      "写Selection与字段、需求、Plan等合同",
      "先认识BusinessSpec结构，业务运行将在10阶段展开",
      "用直接练习代替pytest，避免conftest提前导入Store"
    ],
    "checks": [
      "默认python-basic选simple-admin/SQLite",
      "yudao-vben/SQLite被ValidationError拒绝",
      "显式错误长度被拒绝",
      "更改阶段服务地址但无独立密钥时被拒绝"
    ],
    "troubleshooting": [
      "不要把ValidationError吞成正常结果",
      "MODE是模型名，不是开发模式",
      "SecretStr防止常见展示泄密，不是允许打印原值"
    ],
    "boundaries": [
      "这时只校验结构，不启动网络、数据库或模型",
      "Selection.capabilities需要03的business_capabilities，01不要调用它"
    ],
    "body": "## 先写边界，再写功能\n\n从 `local_only.py` 开始：`local_http_url` 接受回环服务，拒绝公网、局域网、URL凭据和查询参数；模型地址由 `ModelProfile.validate_endpoint` 单独校验，允许远程 HTTPS。两类地址规则分开，才能做到“模型可以外部推理，其余工具本地运行”，而不是一刀切地禁网或放网。\n\n`Settings` 把环境配置变成类型化对象。四个模型阶段依次是 requirements、planning、coding、review。`model_for` 决定哪些值可以继承，`public` 决定哪些值可以显示。尤其要读“地址改变但阶段密钥为空”分支：拒绝复用默认密钥，是在请求发出前阻止跨服务泄露。`_env_file=None` 只是不读个人 `.env`；进程环境变量仍然有效，遇到意外配置时检查当前终端，不要打印密钥排错。\n\n`template_adapters.py` 提供模板合同，`catalog.py` 的选择校验直接导入它；两者必须在本阶段一同写入，再运行合同练习。它们固定后端、前端、数据库的合法组合，基础选择校验不启动后续原生服务。`domain.py` 不把字典原样转交后续工具，而是校验项目名、字段类型、保留名称、枚举、示例与批准动作。`BusinessSpec` 提前落盘，是因为 `Plan` 在导入时直接引用它；提前实现合同不代表现在就已经拥有角色和流程运行时。此时只理解“业务行为要能声明与验证”，第10阶段再把这些声明变成数据库事务。\n\n## 保存并运行第一个合同练习\n\n保存为 `.learning/checks/01_contracts.py`。这不是产品代码，而是你对刚写模块提出的可重复问题。\n\n```python\n# .learning/checks/01_contracts.py\nfrom pydantic import ValidationError\nfrom workbench.catalog import Selection\nfrom workbench.domain import FieldSpec, digest\nfrom workbench.settings import Settings\n\nchosen = Selection(template=\"python-basic\")\nassert (chosen.frontend, chosen.database) == (\"simple-admin\", \"sqlite\")\nfor create in (\n    lambda: Selection(template=\"yudao-vben\", database=\"sqlite\"),\n    lambda: FieldSpec(name=\"title\", kind=\"text\", min_length=81, max_length=80),\n):\n    try:\n        create()\n    except ValidationError:\n        pass\n    else:\n        raise AssertionError(\"invalid contract was accepted\")\nassert digest({\"a\": 1, \"b\": 2}) == digest({\"b\": 2, \"a\": 1})\nsettings = Settings(\n    base_url=\"https://one.example/v1\",\n    api_key=\"exercise-only\",\n    model=\"demo\",\n    planning_base_url=\"https://two.example/v1\",\n    planning_api_key=\"\",\n    _env_file=None,\n)\ntry:\n    settings.model_for(\"planning\")\nexcept ValueError:\n    print(\"01 PASS: valid selection; invalid contracts and cross-provider key reuse rejected\")\nelse:\n    raise AssertionError(\"a different provider requires its own key\")\n```\n\n```bash\n# .learning/commands/01-check.sh\nuv run python .learning/checks/01_contracts.py\n```\n\n应出现一行以 `01 PASS` 开头的文字；示例地址没有被请求，字符串 `exercise-only` 只是本地假值。把一个断言临时反过来应得到 `AssertionError`，改回后再继续。不要删断言来获得绿色结果。\n\n现在不要运行 `pytest tests/test_contracts.py`：pytest 会先加载全局 `tests/conftest.py`，它顶层导入 Store，而 Store 是下一站。这种隐藏依赖比“测试文件名叫合同测试”更能决定何时可执行。也不要调用 `Selection.capabilities()`，其业务能力展开在下一批模块完成后才可用。\n\n## 用同一契约描述技术模板\n\n`TemplateAdapter` 集中声明兼容选型、原生前端页面组件、扩展目录和验收入口；新增业务不再复制这些按技术栈分支的判断。`template_standards.coding_standard` 合并 `templates/standards/common.md` 与当前模板规范，生成稳定的内容哈希。规范属于本阶段必须还原的输入，目录与模型上下文都会读取它。写入产品的函数留到生成阶段执行。\n\n远端模型仍默认要求 HTTPS。明确使用可信 HTTP 网关时，由操作者在进程设置 `ALLOW_INSECURE_MODEL_HTTP=true`；配置请求与模型输出都不能自行开启该选项。HTTP 凭据没有传输加密，应优先使用 HTTPS。模型调用仍固定到配置快照中的地址，不跟随重定向，更换地址也不继承旧 Key。\n"
  },
  {
    "id": "02-storage",
    "title": "持久化与迁移",
    "goal": "在没有网页和模型的情况下，证明任务状态可持久化、事务可回滚、重试可幂等。",
    "prerequisites": [
      "01合同通过",
      "Store、Alembic配置与两份迁移齐全",
      "tests/conftest与本阶段测试齐全"
    ],
    "concepts": [
      "控制数据库与产品数据库不同",
      "事务覆盖业务变化与请求回执",
      "幂等键绑定请求内容",
      "审批版本绑定数据摘要"
    ],
    "steps": [
      "按表之间外键理解Project/Run/Message/Job/Revision/Approval/Step/Event",
      "先跑迁移，再直接调用Store",
      "验证相同键重放与不同内容冲突",
      "观察故意失败的事务不会留下半条项目"
    ],
    "checks": [
      "Alembic版本为0002",
      "相同请求只创建一个项目",
      "同键不同内容抛Conflict",
      "失败事务无残留"
    ],
    "troubleshooting": [
      "SQLite锁冲突先查是否复用实际.data而非临时目录",
      "Windows删除临时库前先dispose连接池",
      "迁移env.py不得导入API或Runtime"
    ],
    "boundaries": [
      "没有后台工作线程与图检查点",
      "不会创建正式用户产品数据库"
    ],
    "body": "## 从内存对象跨进数据库\n\n合同只能保证“这一份输入长得正确”，不能保证进程重启后记得它。`Store` 使用 SQLAlchemy，保存项目、运行、消息、排队任务、请求回执、审批修订和步骤证据。先画出 Project → Run → Message/Job 的归属，再看 Revision 与 Approval 为什么共用 gate_id：一次批准对应某个确定版本的内容，不能漂移到后来改过的设计。\n\n`Store.tx` 是短事务边界；`request → _request` 把请求指纹和响应与实际变化一起提交。第一次创建成功后，网络重试带同一个幂等键应得到原响应；同键换了内容则冲突。幂等不是“忽略所有重复动作”，更不是允许把一个人的批准挪到下一道关卡。`step` 记录已完成步骤的回执，用于避免安全可重放步骤无意义地重做；后续仍要核对输入身份和源码指纹。\n\n平台使用 Alembic 升级控制库，而不是每次启动调用删除重建。`migrations/env.py` 接收已有连接时复用它，否则自行建立 Store；它只能依赖本阶段基础层，不应导入还没实现的 API 和 Runtime。初始迁移建立控制表，第二份迁移加入运行选择与持续委托数据。数据库的版本号应是 `0002`，不会因为你少抄一份迁移而自动补齐。\n\n## 用临时目录验证四件事\n\n保存为 `.learning/checks/02_storage.py`：\n\n```python\n# .learning/checks/02_storage.py\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\nfrom sqlalchemy import text\nfrom workbench.settings import Settings\nfrom workbench.store import Conflict, Project, Store\n\nwith TemporaryDirectory(prefix=\"rnd-learning-store-\") as directory:\n    store = Store(\n        Settings(data_dir=Path(directory), database_url=\"\", install_products=False, _env_file=None)\n    )\n    try:\n        store.migrate()\n        with store.engine.connect() as connection:\n            assert connection.scalar(text(\"SELECT version_num FROM alembic_version\")) == \"0002\"\n        first = store.create_project(\"客服学习\", \"same-request\")\n        assert store.create_project(\"客服学习\", \"same-request\") == first\n        try:\n            store.create_project(\"另一个项目\", \"same-request\")\n        except Conflict:\n            pass\n        else:\n            raise AssertionError(\"idempotency conflict was ignored\")\n        try:\n            with store.tx() as session:\n                session.add(Project(title=\"must roll back\"))\n                raise RuntimeError(\"exercise rollback\")\n        except RuntimeError:\n            pass\n        assert len(store.list_projects()) == 1\n    finally:\n        store.engine.dispose()\nprint(\"02 PASS: migration, idempotency, conflict and rollback\")\n```\n\n```bash\n# .learning/commands/02-check.sh\nuv run python .learning/checks/02_storage.py\nuv run pytest tests/test_contracts.py tests/test_store.py -q\n```\n\n第一条应打印 `02 PASS`，第二条应正常退出且没有 failed/error。测试会用临时库；确认没有把 `DATABASE_URL` 环境变量指向你已有的真实数据库。`finally` 在清理临时目录前关闭连接池，特别避免 Windows 文件句柄未释放。\n\n这一站的成功意味着控制面的持久化规则成立。它还不意味着 LangGraph 的暂停点被保存，也不意味着 Worker 已启动。稍后 `checkpoints.db` 管“图停在哪”，`workbench.db` 管“用户看见什么任务和批准”；产品库则管客户、请求和任务，三者不能混用。\n\n## 将单次运行推广成批量提交\n\n`BatchInput` 是 1–10 个带标题的普通 `RunInput`。`Store.create_batch` 先校验整批，再通过同一个 `request` 事务创建 Project、Run、原始 Message 和 Job；单项与批量共享 `_enqueue_run`。任何一次写入失败都整批回滚，使用相同幂等键与正文重试只返回原来的结果。每项保留自己的手动或智能委托策略，批量没有额外的审批捷径。\n\n验证入口是 `tests/test_batches.py`：检查整批回滚、重试、不重复入队、模板兼容和认证。当前 Worker 仍串行消费队列；高吞吐并行调度需要另一套明确的资源与数据库隔离设计，本阶段不声称已实现。\n"
  },
  {
    "id": "03-requirements",
    "title": "需求保真与模型协议",
    "goal": "让模型提出结构化候选，再由确定性规则保留既有事实、拒绝漏项与冲突。",
    "prerequisites": [
      "02临时库与基础测试通过",
      "requirement_coverage、requirement_sources、entity_requirements、business_capabilities完整",
      "llm与model_protocol及其依赖齐全"
    ],
    "concepts": [
      "结构正确不等于需求正确",
      "省略不代表删除",
      "更正必须引用当前用户来源",
      "模型协议失败与实现失败分层",
      "报名主体、账号注册与公众入口必须分别表达"
    ],
    "steps": [
      "先写覆盖检查与保留合并，再写来源冲突",
      "把SDK输出接入同一Pydantic合同",
      "运行无网络模型协议测试",
      "故意删搜索能力验证缺口仍存在"
    ],
    "checks": [
      "正确计划无缺口，删除searchable产生缺口",
      "模型省略的facts仍被保留",
      "协议测试无真实供应商请求"
    ],
    "troubleshooting": [
      "JSON可解析但字段错误仍应失败",
      "冲突需求需澄清，不能硬改Plan去满足互斥条件",
      "不要把生产无密钥改成固定模型答案"
    ],
    "boundaries": [
      "不承诺任意自然语言都可自动穷尽理解",
      "test_requirement_coverage/source_conflicts完整回归到14运行，03用可执行纯函数与协议测试"
    ],
    "body": "## 两道不同的门：响应合同与需求覆盖\n\n`model_protocol.py` 接管服务商结构化输出的协议边界：选择正式 LangChain 集成、检查HTTP状态和响应大小、解析JSON、执行本地严格验证。`llm.ModelGateway` 再负责阶段模型选择、调用预算、缓存/回执与安全诊断。返回合法JSON只是第一道门；例如用户要求标题可搜索，而候选计划把 `searchable` 设为 false，所有JSON字段都合法，业务仍然错误。\n\n因此 `requirement_coverage.py` 不依赖模型自己宣布“全部覆盖”。它读取已保存的 Requirement，包括类型化字段约束、实体清单、既有 facts 及受约束的旧文本表达，再与 Plan 比较。`entity_requirements.py` 负责实体字段清单；开放清单要求“至少有这些”，封闭清单还要求“不能多出别的”。`business_capabilities.py` 专门处理角色动作、范围、关联、提醒、统计等业务义务，不能把这些义务错当作普通字段。\n\n多轮澄清最大的陷阱是遗漏。`reconcile` 保留上一轮已确认的事实，不因下一轮模型没再写一遍就删除。真正的修改要有 `RequirementChange`，其 `source_quote` 必须能对应本轮新收到的用户更正。`requirement_sources.py` 进一步检测不同来源中的互斥约束；诊断指出冲突双方，不能自己决定哪方胜出。智能推荐是补齐普通未知项的委托，不是修改明确要求的授权。\n\n## 一个无需真实模型的反例实验\n\n保存为 `.learning/checks/03_requirements.py`：\n\n```python\n# .learning/checks/03_requirements.py\nfrom workbench.domain import Plan, Requirement\nfrom workbench.requirement_coverage import coverage_gaps, reconcile\n\nrequirement = Requirement(\n    summary=\"请求标题\",\n    users=[\"员工\"],\n    data_scope=\"per_user\",\n    features=[\"管理请求\"],\n    acceptance=[\"标题可搜索\"],\n    facts={\"original\": \"保留原始标题\"},\n    field_requirements=[\n        {\n            \"entity\": \"request\",\n            \"field\": \"title\",\n            \"kind\": \"text\",\n            \"required\": True,\n            \"max_length\": 80,\n            \"searchable\": True,\n        }\n    ],\n)\nplan = Plan(\n    title=\"请求\",\n    data_scope=\"per_user\",\n    acceptance=[\"标题可搜索\"],\n    entities=[\n        {\n            \"name\": \"request\",\n            \"description\": \"请求\",\n            \"fields\": [\n                {\n                    \"name\": \"title\",\n                    \"kind\": \"text\",\n                    \"required\": True,\n                    \"max_length\": 80,\n                    \"searchable\": True,\n                }\n            ],\n        }\n    ],\n)\nassert coverage_gaps(requirement, plan) == []\nwrong = plan.model_copy(deep=True)\nwrong.entities[0].fields[0].searchable = False\nassert coverage_gaps(requirement, wrong)\nomitted = requirement.model_copy(update={\"facts\": {}, \"field_requirements\": []})\nmerged = reconcile(requirement.model_dump(), omitted, corrections=[])\nassert merged.facts == requirement.facts\nassert merged.field_requirements == requirement.field_requirements\nprint(\"03 PASS: coverage detects loss; omission preserves intent\")\n```\n\n```bash\n# .learning/commands/03-check.sh\nuv run python .learning/checks/03_requirements.py\nuv run pytest tests/test_llm.py tests/test_provider_structured_outputs.py tests/test_field_predicate_semantics.py -q\n```\n\n练习应打印 `03 PASS`，测试应无 failed/error。协议测试通过显式 MockTransport 检查请求响应合同，不会验证你自己的供应商账号。`deep=True` 很重要：否则错误样本可能共享嵌套对象，误把正确计划也改坏。把练习里的“正确计划”“缺搜索计划”“省略事实的下一轮”对应回三个独立变量，就能看清各函数的职责。\n\n不要在这一站直接跑 `tests/test_requirement_coverage.py` 或 `tests/test_requirement_source_conflicts.py` 的整文件。它们混合纯函数、工作流和原生适配/诊断数据用例，既有后续Runtime导入，也读取后续fixtures。第14阶段完整源码就位后再跑它们；这并不是少测，而是把集成测试放到真实依赖成立之后。\n\n## 从真实模型增量到可见草稿，仍不能绕过最终合同\n\n`Runtime` 创建生产 `ModelGateway(..., streaming=True)`。网关仍通过官方LangChain结构化链解析结果；`model_protocol.AuditedTransport` 在SDK规范化之前审计真实HTTP响应。服务端返回 `text/event-stream` 时，`AuditedEventStream` 逐帧消费内容、完成原因和usage，并检查大小上限、结束标记与本地严格schema。网络块不是一个JSON对象，也不保证一个中文字已经完整，协议层因此需要增量解码和帧边界处理。\n\n`streaming.AssistantStream` 并不把服务商原始JSON全部发到网页。只有本项目指定schema的公开根字符串可以显示：需求的 `summary`、计划的 `title`、补丁的 `explanation`、复核的 `summary`。嵌套对象、补丁源码和隐藏推理字段不在投影范围。`root_string_prefix` 只返回当前已经完整解码的字符串前缀；碰到半个JSON转义或UTF-16代理对时等待后续数据，不猜一个字符。若目标字段前还有尚未完成的对象，暂时没有公开文字也是正常情况。\n\n可以跟踪一个具体反例：服务商先返回summary前半句，页面已显示草稿，后半段却让Requirement缺了必填字段。增量不能使这次调用提前成功，完整对象仍须校验；失败事件把草稿清空并保留失败状态，重新纠错是另一次有身份的尝试。只有最终通过校验的对象才进入需求/计划与后续业务判断。\n\n另一个难点是密钥跨块泄露。若已知Key的前半段恰好出现在当前公开字符串末尾，`AssistantStream.content` 会暂留这个可能的前缀，直到能判定或统一脱敏后才追加可见文本。修改过的本机模型配置中的旧Key也保留在脱敏集合，不能只保护当前环境变量。测试用的都是明确假Key，不需要把自己的Key写进测试证明保护有效。\n\n并非每个兼容服务都支持流。若服务忽略 `stream=true` 而一次返回JSON，回执明确 `non_streaming`，界面一次显示真实完整结果，不在浏览器伪造逐字动画。只有协议中明确的“不支持stream”错误才允许一次非流回退；认证错误、普通超时和任意400不能被当作能力回退。增量显示、传输成功、schema通过和业务通过是四件不同的事。\n\n## “报名网站”不能被模型悄悄改成后台代录\n\n报名产品的核心是参赛者能否自行提交。单独出现“报名网站”并不明确等于匿名访问；先把尚未说明的入口保留为待澄清，而不是宣称所有报名都不支持。现有能力支持参赛者注册并登录后，在已生成的业务界面提交报名；设计须保留非管理员参与者角色、默认业务角色，以及create/read等本人记录权限。账号注册和业务报名是两件事，不能因为框架能注册账号就宣称独立公众报名门户已经存在。\n\n明确要求匿名提交或独立自定义公众门户时，当前实现暂停并说明需要扩展、验证对应能力，不能换个模板名称假装已经支持。“仅管理员录入”是产品范围变更，只有用户明确取消参赛者自行报名并选择管理员代录时才成立。智能推荐、模型给出的推荐值、旧设计中的管理员角色都不能代替这个更正。\n\n跟踪原始用户消息和本轮逐字更正的来源，再看需求账本中的before、after及变更记录。历史模型分析如果已把队长改成联系人，原始自行报名目标仍应恢复到当前摘要和范围提示；旧分析保留供审计，不能删掉历史后宣称从未出错。重复角色或等价CRUD表述可做保守规范化，但权限、否定、主体、约束和不确定改写仍须保留，不能用模糊相似度去重删除义务。\n\n`requirement_intent.analysis_intent_conflicts` 还检查候选需求是否仍有真实参与者角色和正向自行提交行为，不能只在摘要保留“报名”两个字。`registration_plan_gaps` 再检查可执行设计：明确的报名实体、默认参与者角色、需要账号注册时启用registration，以及对应create/read的own权限。`python-basic` 的per_user、无business合同路径已有内置owner_id隔离；该窄路径无需凭空添加团队业务合同。角色、需求与Plan三层都要通过，单独选择一个范围选项不是执行证据。\n"
  },
  {
    "id": "04-local-foundation",
    "title": "文件安全与源码检索",
    "goal": "建立可定位行号、可验证新鲜度的本机源码上下文，限制文件访问与工具执行。",
    "prerequisites": [
      "03合同与需求模块齐全",
      "filesystem、tools、symbols、knowledge、retrieval、rules齐全；coding/toolchain在07落盘"
    ],
    "concepts": [
      "路径归属与secret排除",
      "源码SHA与索引身份",
      "AST/Tree-sitter与FTS分工",
      "受限规则解释不等于exec"
    ],
    "steps": [
      "先实现文件访问和受控进程",
      "写本机符号索引与检索",
      "观察二次索引复用与源码变化后拒绝旧索引",
      "用一正一反一非法输入验证Rules"
    ],
    "checks": [
      "demo.py能按model_for命中",
      "未变化第二次索引reused=1",
      "源码变化后查询拒绝旧索引",
      "import os规则被拒绝"
    ],
    "troubleshooting": [
      "索引目录必须位于源码目录外",
      "先检查真实起止行，不把命中文件名当语法解析",
      "子进程失败先看退出码与限量日志"
    ],
    "boundaries": [
      "此站默认不启用Continue、向量或Aider",
      "test_toolchain整文件有未来依赖，完整工具回归放12之后"
    ],
    "body": "## 检索要能回答“证据在哪一行”\n\n`filesystem.py` 是其他工具的共同入口：解析目标必须留在授权根目录内，遍历时排除敏感配置、运行数据和日志，写入使用原子替换，解压检查危险路径。它看起来比模型调用普通，却决定后面索引和交付包会不会把 `.env`、数据库或运行日志当源码带走。先跟踪 `inside → files → manifest`，再看生成器、上下文和打包器怎样共同使用这些函数。\n\n`symbols.py` 负责多语言语法；Python使用AST，Java/TypeScript/JavaScript/HTML使用固定Tree-sitter语法。`knowledge.build_index` 保存文件SHA、符号及起止行，第二次只重用指纹未变的文件。`retrieval.py` 再生成FTS索引、检索片段和紧凑仓库地图。它们不是同一个黑箱：解析告诉你“这个定义在哪”，全文检索告诉你“哪些位置含相关词”，新鲜度检查告诉你“现在还能不能信这个索引”。\n\n`tools.py` 只接收明确的字符串参数数组，清理子进程环境、设置期限并清理本次进程组。它是可信固定工具的执行器，不是可接收任意模型 shell 的安全沙箱。`rules.py` 允许有限AST节点，按自己的解释器计算单记录规则；第07站实现的 `coding.py` 会进一步把改动锁定到 `custom_rules.py` 和正确前像SHA。规则通过也只证明那段受限业务表达式有效，不能由此授权改鉴权、测试或启动器。\n\n## 观察真实索引的生命周期\n\n保存为 `.learning/checks/04_index.py`：\n\n```python\n# .learning/checks/04_index.py\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\nfrom workbench.knowledge import build_index\nfrom workbench.retrieval import query\nfrom workbench.rules import Rules, UnsafeRule\n\nwith TemporaryDirectory(prefix=\"rnd-learning-index-\") as temporary:\n    root = Path(temporary)\n    source, index = root / \"source\", root / \"index\"\n    source.mkdir()\n    file = source / \"demo.py\"\n    file.write_text(\"def model_for(stage):\\n    return stage\\n\", encoding=\"utf-8\")\n    assert build_index(source, index)[\"files\"] == 1\n    assert build_index(source, index)[\"reused\"] == 1\n    assert any(hit[\"path\"] == \"demo.py\" for hit in query(source, index, \"model_for\")[\"matches\"])\n    file.write_text(\"def model_for(stage):\\n    return 'changed'\\n\", encoding=\"utf-8\")\n    try:\n        query(source, index, \"model_for\")\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(\"stale index was accepted\")\nrule = Rules(\n    \"def validate(entity, data):\\n    if data['quantity'] < 0:\\n        raise ValueError('nonnegative')\\n    return None\\n\"\n)\nrule.validate(\"request\", {\"quantity\": 0})\ntry:\n    rule.validate(\"request\", {\"quantity\": -1})\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError(\"negative example was accepted\")\ntry:\n    Rules(\"import os\\n\")\nexcept UnsafeRule:\n    pass\nelse:\n    raise AssertionError(\"arbitrary code was accepted\")\nprint(\"04 PASS: source-backed retrieval, stale rejection and bounded rules\")\n```\n\n```bash\n# .learning/commands/04-check.sh\nuv run python .learning/checks/04_index.py\n```\n\n应打印 `04 PASS`。其中 `demo.py` 只被当源码解析，没有执行它。索引和源码是并列目录，因为把输出放进被扫描的目录会产生自我索引。现在的检索不需要Node和向量服务，切换更多引擎要等第11站。\n\n学习时随手打开命中的文件，看行号对应的真实函数；然后把 `query` 的字符预算调得过小，观察明确拒绝，而不是让上下文静默截断。上下文预算与来源指纹共同保护规划：模型收到的是可追溯的源码证据，源码注释也仍然是不可信数据，不能覆盖用户批准。\n"
  },
  {
    "id": "05-product",
    "title": "产品模板与认证",
    "goal": "先把将被复制的完整业务应用写齐，理解产品自己的认证、模型、迁移与界面。",
    "prerequisites": [
      "04安全文件与规则解释器通过",
      "templates/product全部文件、templates/frontends/simple-admin全部文件",
      "business/common/policy与business_python按依赖先实现"
    ],
    "concepts": [
      "模板文件还不是生成后的项目",
      "平台令牌、模型Key、产品用户Token互不通用",
      "字段合同贯穿API校验、SQL与表单",
      "权限依赖服务端而不是按钮隐藏"
    ],
    "steps": [
      "按schema→fields/querying→app→manage/start顺序阅读",
      "再写simple-admin浏览器交互与验证脚本",
      "把业务分支完整落盘，第10站深学",
      "只做源码语法检查，生成后才能运行"
    ],
    "checks": [
      "所有模板Python文件可由3.14解析",
      "Node就绪时三个核心CJS/JS脚本语法检查通过",
      "模板根目录不被当成产品直接启动"
    ],
    "troubleshooting": [
      "缺approved-spec.json或selection.json是尚未生成，不手工复制平台配置蒙混",
      "ModuleNotFoundError rule_engine说明误在模板目录直接运行",
      "认证失败先辨别使用了哪一种令牌"
    ],
    "boundaries": [
      "语法通过不代表HTTP或浏览器运行通过",
      "不提供默认真实管理员密码、不在文档放真实凭据"
    ],
    "body": "## 为什么先写模板，再写生成器\n\n生成器的主要工作不是让模型写一整套CRUD，而是把已审阅的应用模板和批准的结构组合起来。因此这一站先完成“将被复制的产品”，下一站才写复制和冻结设计的过程。`templates/product` 整个目录都需要落盘，包括业务扩展和验证脚本，因为生成器按完整目录复制；不能把尚未讲解的业务文件先省略，否则最终包不再是同一实现。\n\n从 `schema.py` 阅读数据流：它读取生成后的 `approved-spec.json`，根据字段声明建SQLAlchemy表，决定使用独立 SQLite 文件还是本机 PostgreSQL。`fields.py` 为请求建立严格输入模型，`querying.py` 把关键词、枚举筛选和含边界的日期查询变成参数化条件。`app.py` 提供注册、登录与CRUD，每条数据通过服务端当前用户约束所属范围，不能信任客户端提交的 owner_id。\n\n密码使用带盐哈希；产品发出的访问Token在数据库中保存其哈希与有效期。平台访问令牌保护“谁能操作研发平台”，产品Token保护“谁能访问最终客户记录”，模型API_KEY则只用于推理供应商，三者不能互换。普通注册和管理员初始化也是两回事：业务产品的初始化管理员由 `manage.py bootstrap-admin` 单独建立，密码通过终端隐藏输入，不能凭借普通注册获得管理角色。\n\n## 页面只是完整链路的一环\n\n`templates/frontends/simple-admin/app.js` 根据 `/schema` 呈现已批准实体和字段，把日期、枚举、搜索/筛选条件映射到HTTP请求。选择关系、提交表单、显示错误和重新加载需要保持一致；不能只看首屏渲染就认为认证和业务完成。业务模式安装时，`business_runtime.py` 替换相关CRUD与schema路由，继续使用同一个认证入口，并在每次请求从服务端重新加载角色。\n\n`verify.py` 是可信验收入口。普通实体走 `verify-browser.cjs`；客服业务由 `verify_business.py` 与 `verify-business-browser.cjs` 检查。这些测试脚本也会进入交付包，让新目录复验不必借平台源码。它们不受编码模型控制，不能在规则失败时改测试以求通过。\n\n## 本站检查：模板齐全，但暂时不启动\n\n```bash\n# .learning/commands/05-syntax.sh\nuv run python -m compileall -q templates/product templates/business/common\n```\n\n命令应退出码为0；成功可能没有输出。它只编译语法，不导入模板应用，也不创建产品数据库。此刻不要在 `templates/product` 中执行 `uv run python app.py`：它尚没有生成的 `approved-spec.json`、`selection.json`、迁移文件和从规则解释器复制出的 `rule_engine.py`。缺这些文件是阶段边界，不是应当手工做一套重复配置。\n\nNode22准备好后，可增加下面的纯语法检查；没有Node时将本项记录为“待第06阶段浏览器准备”，不能伪装通过。\n\n```bash\n# .learning/commands/05-node-syntax.sh\nnode --check templates/frontends/simple-admin/app.js\nnode --check templates/product/verify-browser.cjs\nnode --check templates/product/verify-business-browser.cjs\n```\n\n本阶段完成后，你应该能沿着“批准字段 → schema → API输入校验 → SQL写入 → 前端表单”口述完整路径，并指出服务端何处阻止跨用户访问。第10站会把角色、关联、工作流、提醒和统计展开；这里先保证完整产品文件集合就位，不把未来功能留成 `pass`。\n"
  },
  {
    "id": "06-generation",
    "title": "确定性生成与独立验证",
    "goal": "把批准的Plan变成真实文件，验证本次文件对应本次设计，并首次运行真实产品。",
    "prerequisites": [
      "05产品模板完整",
      "generator、product_sql、verification、postgres_lab及其依赖齐全",
      "带simple-admin验收前准备Node22/Playwright1.56.1/Chromium"
    ],
    "concepts": [
      "生成回执与源码manifest",
      "已有目录保护",
      "环境故障不同于代码故障",
      "浏览器证据绑定实体与字段"
    ],
    "steps": [
      "跟踪generate_basic冻结spec/selection/迁移",
      "先跑生成保护测试",
      "显式安装浏览器工具后运行生成验收练习",
      "保留生成回执与verification.json阅读"
    ],
    "checks": [
      "generation.json包含spec_digest、selection、files",
      "已有不匹配目录被保留而不是覆盖",
      "真实产品报告http/restart/passed均true",
      "simple-admin具有逐实体真实browser证据"
    ],
    "troubleshooting": [
      "缺Playwright模块检查绝对路径与当前终端环境",
      "缺Chromium回到显式安装阶段，不在运行时隐式联网",
      "重新生成失败不要删除用户.data"
    ],
    "boundaries": [
      "模型尚未参与此处Plan输入",
      "install_products=False只适合开发测试，不能声称独立依赖验收"
    ],
    "body": "## 一份批准设计怎样变成可运行项目\n\n`generator.generate_basic` 首先校验模板选择与数据范围，再检查目标目录是否为危险链接或已经存在。新目录中复制产品模板、规则解释器和所选前端，冻结 `approved-spec.json` 与 `selection.json`，生成固定迁移并导出参考DDL。最后把设计摘要、选择和完整文件指纹写入目录外的 `generation.json`。参考SQL用于阅读和核对；正常启动由版本化迁移执行，不要再手工把参考SQL执行第二遍。\n\n已存在的产品不是可随时删掉的临时产物。只有相符生成回执时才允许安全重用；缺回执、计划改变、选择改变或目录身份异常都应保留现场并拒绝。这个分支保护产品数据库、用户笔记和人工维护的文件。幂等的含义是“重做同一请求不损坏结果”，不是“每次清空再生成看起来一样”。\n\n`verification.verify_basic` 先将当前manifest与生成回执对比。可信模板、验证器和启动器不能被编码器改动；只允许规则文件走指定路径。然后解析源码、运行正反规则样例、安装产品自己的锁定依赖，调用 `run_probe → verify.py` 进行迁移、真实HTTP、重启和浏览器检查。最后把源码摘要绑定到报告，防止测试过后换一份文件仍拿旧报告交付。\n\n## 先检验保护，再准备浏览器\n\n```bash\n# .learning/commands/06-generator-contracts.sh\nuv run pytest tests/test_generation_preservation.py -q\n```\n\n应无 failed/error。该组测试故意破坏回执并放入用户文件哨兵，验证失败后每个字节仍在；它并不证明产品已经启动。\n\n完整 simple-admin 产品需要真实浏览器。先打开 [Node.js官方下载页](https://nodejs.org/en/download)，在版本选择中明确选22.x（至少22.13），再选你的系统与架构，使用官方安装器/预编译包；不要直接采用页面默认的另一个主版本。也可在 [官方版本归档](https://nodejs.org/en/download/archive) 查找22.x。安装后重开终端，运行 `node --version` 和 `npm --version`；前者应是v22.x且不低于22.13。安装到其他终端的Node不一定进入当前PATH。\n\nLinux/WSL在项目根目录执行：\n\n```bash\n# .learning/commands/06-browser-linux.sh\nnpm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1\nexport PLAYWRIGHT_BROWSERS_PATH=0\nnode .native/browser/node_modules/playwright/cli.js install --with-deps chromium\nexport PRODUCT_VERIFY_PLAYWRIGHT=\"$PWD/.native/browser/node_modules/playwright\"\n```\n\nWindows PowerShell执行对应版本：\n\n```powershell\n# .learning/commands/06-browser-windows.ps1\nnpm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1\n$env:PLAYWRIGHT_BROWSERS_PATH = '0'\nnode .native/browser/node_modules/playwright/cli.js install chromium\n$env:PRODUCT_VERIFY_PLAYWRIGHT = (Resolve-Path '.native/browser/node_modules/playwright').Path\n```\n\nLinux `--with-deps` 可能需要本机管理员安装系统库，按系统提示由你处理。环境变量仅对当前终端及子进程有效，后续平台和测试从同一终端启动。模块路径不是浏览器URL，也不是Chromium可执行文件。安装失败要先修复环境，不通过改成 api-only 来规避本来选择的页面验收。\n\n## 保存一个真正运行的生成练习\n\n保存为 `.learning/checks/06_generate.py`：\n\n```python\n# .learning/checks/06_generate.py\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\nfrom workbench.domain import Plan\nfrom workbench.generator import generate_basic\nfrom workbench.settings import Settings\nfrom workbench.verification import verify_basic\n\nplan = Plan(\n    title=\"请求标题练习\",\n    data_scope=\"per_user\",\n    acceptance=[\"CRUD与两用户隔离\"],\n    entities=[\n        {\n            \"name\": \"request\",\n            \"description\": \"请求\",\n            \"fields\": [{\"name\": \"title\", \"kind\": \"text\", \"max_length\": 80, \"searchable\": True}],\n        }\n    ],\n)\nwith TemporaryDirectory(prefix=\"rnd-learning-generation-\") as temporary:\n    root = Path(temporary)\n    product = root / \"run/product\"\n    settings = Settings(\n        data_dir=root / \"state\",\n        database_url=\"\",\n        install_products=True,\n        tool_timeout=600,\n        _env_file=None,\n    )\n    generation = generate_basic(\n        plan,\n        product,\n        {\"template\": \"python-basic\", \"frontend\": \"simple-admin\", \"database\": \"sqlite\"},\n    )\n    assert \"approved-spec.json\" in generation[\"files\"]\n    report = verify_basic(plan, product, settings)\n    assert report[\"passed\"] is True and report[\"http\"] and report[\"restart\"]\n    assert report[\"browser\"][\"real_browser\"] is True\n    assert report[\"isolated_dependencies\"] is True\nprint(\"06 PASS: generated files, isolated dependencies, real HTTP/browser and restart\")\n```\n\n```bash\n# .learning/commands/06-runtime.sh\nuv run python .learning/checks/06_generate.py\nuv run pytest tests/test_product_browser_gate.py -q\n```\n\n只有实际执行并出现 `06 PASS` 才能记“产品运行通过”。这个Plan是公开写在练习里的确定性输入，不是假装来自模型。还没有测试后续流程图；下一站才让需求、审批和这些工具衔接起来。\n"
  },
  {
    "id": "07-orchestration",
    "title": "审批状态机与恢复",
    "goal": "用持久状态机串联需求、设计、生成、验证与交付，并证明中断不吞批准。",
    "prerequisites": [
      "06真实产品运行通过且浏览器仍可用",
      "flow、runtime、conversation、recommendation齐全",
      "toolchain、sandbox、daytona_profiles必须在运行时导入链内提前就位"
    ],
    "concepts": [
      "控制库与图检查点协同",
      "interrupt与gate_id",
      "一步回执和任务认领",
      "持续委托不跳过验证",
      "预算暂停可恢复"
    ],
    "steps": [
      "按compile图边逐节点阅读",
      "先用FixtureGateway运行人工三关卡",
      "测试旧gate拒绝与重启恢复",
      "再测试智能推荐各阶段独立修复预算"
    ],
    "checks": [
      "人工路径经历WAITING_REQUIREMENTS/DESIGN/DELIVERY",
      "CRUD不调用coding模型",
      "旧gate不能消费新批准",
      "最终READY带cleanroom通过",
      "旧FAILED检查点保留同run身份、历史审批与审计，已知范围选择不重复调用模型"
    ],
    "troubleshooting": [
      "单Worker锁错误先检查第二个进程",
      "PAUSED_LIMIT调整配置后重试原运行",
      "BLOCKED读具体诊断，不新建任务抹除证据"
    ],
    "boundaries": [
      "本阶段模型使用显式测试夹具",
      "Daytona源码前置仅满足import，不表示已安装或运行服务"
    ],
    "body": "## 图负责顺序，工具负责真相\n\n`flow.Workflow` 把前面写好的函数串成节点：分析需求、澄清/确认、形成设计、设计校验、生成、受限编码、独立验证、可选本机沙箱、可选模型审阅、交付批准和打包。按 `compile` 中的节点与条件边阅读，不要把某个节点函数存在误认为它一定会执行。例如纯CRUD不需要编码模型；只有已批准的额外单记录规则进入编码与有界修复。\n\n`gate` 先由 Store 固化这一版审批内容，再调用 LangGraph 的 `interrupt`。用户回答带 gate_id，恢复时再次核对当前版本与已存批准；模型不能通过在JSON里写 `approved=true` 自己跨过关卡。`conversation.py` 将“批准”“智能推荐”等控制词与普通需求内容区分，避免把批准口令当新需求再次发给模型。\n\n`Runtime` 负责取队列任务、载入检查点、进入图、完成任务和归类错误。SQLite使用独立 `checkpoints.db`；PostgreSQL使用对应checkpoint后端。文件锁和数据库锁限制一个Worker。`last_job_id` 与当前中断共同防止“图已推进，但任务完成记录还没写入”这种崩溃窗口重复消耗下一次回答。\n\n## 依赖闭包为什么比章节标题更重要\n\n此站第一次跑整条本地流程。`flow.plan` 会导入 `toolchain.prepare_context`，`flow.design` 即使是local配置也会导入 `sandbox.validate_configuration`，后者又需要 `daytona_profiles.py`。这些文件必须先完整写入；Daytona SDK和服务仍是第12站才安装启用的可选运行能力。不要为了看起来顺序漂亮把源码换成假stub，也不要因为文件提前存在就声称沙箱已经验收。\n\n模型使用 `tests/conftest.py` 的 `FixtureGateway`，这是明确的测试替身，只为让同样输入可重现。生产 `rnd start` 不会在缺Key时偷偷选择它。夹具控制模型响应，但生成、迁移、HTTP、浏览器和干净解压仍由真实本机工具决定结果。\n\n```bash\n# .learning/commands/07-state-machine.sh\nuv run pytest tests/test_workflow.py tests/test_guided_workflow.py tests/test_recommendation_stage_budget.py -q\n```\n\n前提是相关测试文件已按本阶段索引写齐。需求覆盖完整历史回归含原生适配用例，来源冲突回归还读取诊断fixtures，recommendation_recovery会导入CLI，guided_completion会读取独立部署模板，因此这些整文件统一放第14站全套运行；此处只运行当前闭包完整的三个文件。预期所有用例正常退出，没有failed/error。`test_complete_default_flow` 会实际依次检查 `WAITING_REQUIREMENTS`、`WAITING_DESIGN`、`WAITING_DELIVERY`，再看到 `READY` 和cleanroom报告；其模型调用只有 requirement 与 plan，恰好证明CRUD不靠模型自由编码。\n\n## 主动制造一次“不能继续”\n\n读测试里的旧gate、第二Worker和模型预算反例，先说出你预期的错误，再运行对应测试。`MAX_ROUNDS=0` 和 `MAX_MODEL_CALLS=0` 表示不设累计上限，不意味着HTTP重试或自动修复无限。智能推荐对每个阻塞阶段有独立修复预算，修复失败进入 `BLOCKED` 并保存诊断；不能把需求澄清消耗的修复次数错误借到设计阶段，也不能删掉验收条件来解除阻塞。\n\n本阶段结束时应能跟踪同一run_id从排队到等待、从批准到恢复。真正的恢复是继续已有身份与证据，而非重新新建一个项目看起来成功。下一站只是在这条已测链路外加API、CLI和操作台，不把业务逻辑搬进网页按钮。\n\n## 对话事件与工作流状态分别持久化\n\n流式页面需要展示“正在收到什么”，而编排需要决定“下一步可以执行什么”。两者共用run_id，但不能混为一张已批准需求表。`Store.assistant_event` 追加 `assistant_start/status/delta/completed/failed` 事件；用户回答继续写入Message。助手草稿不会被当作下一轮用户需求，完成事件也不会自动消费审批关卡。\n\n一次逻辑模型响应由response_id联系起来，每次真实尝试还有单独message_id。工作进程重启后，新尝试开始时旧的未完成草稿会被标为 `worker_interrupted`；终态事件重复到达不能追加第二个完成结果。这样既能说明发生过重试，又不让旧消息永远显示“生成中”。\n\n刷新页面时，`Store.transcript` 在同一个读取快照中返回对话与cursor；后续SSE只从cursor之后继续。PostgreSQL显式使用可重复读，避免“消息包含了某个增量，cursor却没包含它”造成重复。`event_stream` 从已经提交的事件回放再跟随新事件，检查到任务不再QUEUED/RUNNING时补查一次尾部事件，再发送idle结束。浏览器关闭或切换任务只关闭这条订阅，已持久化Worker任务仍可继续；重新订阅不会再次调用模型。\n\n需求澄清现在还可包含有ID的结构化问题与选项。先看 `domain.ClarificationQuestion` 的single/multiple/text约束，再看 `clarification.render_answer`：它在 `Store.submit` 已锁定、核对当前gate_id的事务里，从服务器当前选项恢复标签、拼接用户补充文字。旧关卡、伪造选项或漏答必填必须整体拒绝，不能先入队再提示错误。合法回答进入下一轮分析，批准需求/计划仍是另一次明确操作。\n\n## 已失败的旧运行要恢复原目标和原身份\n\n一个旧运行可能已保存Requirement、批准和设计检查点，随后因可选psycopg未安装变为 `FAILED`。修好安装边界后，必须用同一run_id恢复，不能要求重建项目来绕过旧状态。`Workflow.capability_recovery` 在继续旧流程之前重新核对原始用户消息与当前能力：需要入口选择时创建新的需求关卡、清除当前待执行的旧Plan引用，保留历史需求账本和审批记录；旧批准不能自动授权已更正的需求。\n\n恢复时还要尊重LangGraph的旧interrupt身份。已在关卡等待的运行先消费原来gate的合法回答，再回到澄清；已批准但尚未执行的设计则在产生原生副作用前重查范围。新的gate_id、原run_id、messages、ledger和旧Approval应一起核对。重启Runtime或刷新页面都不能丢掉这个决策点。\n\n已知报名入口需要用户选择时，反复点“智能推荐”不应再消费分析模型预算，也不能把模糊入口自动选成匿名或管理员。当前界面保留明确能力提示和可执行选项；用户选择“登录后自行提交”才沿已有业务UI路径继续，明确匿名/自定义门户则继续暂停，明确取消自行报名并管理员代录才接受范围更正。这与普通缺信息的有界自动补全不同。\n\n完整回归 `tests/test_legacy_signup_recovery.py`、`tests/test_capability_recovery_controls.py` 放在第14站运行，因为它们要用到后续API、原生设计与历史状态依赖。失败恢复是状态机合同测试；它本身不证明真实原生数据库或全栈运行已通过。\n\n图状态的 `requirement_intent_version` 标识已应用的新入口约束。旧的登录后自行报名运行即使不再缺范围选择，也必须迁移历史“仅联系人/管理员代录”假设、重新校验参与者与Plan；没有标识的旧批准不能绕过升级检查。迁移追加scope_changes和来源，保留其他字段义务及旧审计。\n\n范围问题使用中性提问“参与者将通过哪种入口报名？”，而不是把尚未明确的入口称为能力冲突。零模型调用保证针对已知范围决策；历史运行若已明确选择可支持入口、但旧分析丢失参与者或提交行为，仍可进入有界的分析修正，不能笼统承诺每个旧运行恢复都不调用模型。旧gate的digest必须按旧内容重放，版本标记不能被用来重写已等待关卡的身份。\n"
  },
  {
    "id": "08-control-plane",
    "title": "API、CLI与Vue流式操作台",
    "goal": "以真实API连接Vue操作台、CLI、可重放的流式对话和本机模型设置，区分页面状态与后台执行状态。",
    "prerequisites": [
      "07状态机测试通过",
      "api、cli、ui完整源码与锁、web构建快照齐全",
      "完整原生vendor尚未准备时不能运行rnd init"
    ],
    "concepts": [
      "展示层调用Store/Runtime而非复制逻辑",
      "健康与就绪不同",
      "平台本机令牌与Host限制",
      "HTTP幂等键"
    ],
    "steps": [
      "先TestClient验证无Worker API",
      "按lock安装、测试与构建Vue",
      "核对CLI帮助和本机地址，启动设置页",
      "输入需求并在提交运行前确认技术组合，观察流式草稿与真实关卡"
    ],
    "checks": [
      "health=ok，ready=200",
      "错误Bearer=401，非本机Host=400",
      "同键重复创建返回同项目",
      "创建运行前确认实际模板组合，需求草稿不提前调用模型",
      "Vue类型/单元测试与生产构建成功，生成资产可由源码重建",
      "增量草稿、验证完成、失败及非流结果准确区分",
      "刷新/重连去重、切换运行无串线、旧关卡与配置冲突被拒绝",
      "能力范围提示来自当前gate，不能把登录后自行报名自动降级成管理员代录"
    ],
    "troubleshooting": [
      "无模型配置可启动设置页；创建运行仍明确拒绝，不以夹具兜底",
      "init缺vendor归档应等09而非联网猜模板",
      "readiness失败分清数据库和Worker"
    ],
    "boundaries": [
      "仅本机单操作人，不是公网生产多租户身份体系",
      "真实供应商调用会产生费用，纯API测试不会",
      "订阅断开不等于停止Worker任务",
      "设置保存只做格式和安全校验，不表示实际供应商连接已通过"
    ],
    "body": "## 一套内核，三个入口\n\n`api.create_app` 把Store和Runtime接到FastAPI生命周期，启动时迁移控制数据库并取得本机访问令牌，可选启动内置Worker；关闭时通知Worker停止、等待线程退出并释放数据库。`/health` 说明进程能回答，`/ready` 进一步检查数据库与要求中的Worker，它们不能互相替代。\n\nCLI和Vue操作台都是HTTP客户端，不各自复制一套编排。全部数据接口、模型设置、SSE和下载都要求本机Bearer令牌；TrustedHost限制可信主机名，页面还设置同源脚本/连接等CSP边界。创建项目、运行、回答关卡等状态变更继续使用幂等键，审批继续绑定当前gate_id。漂亮的按钮不能让一个过期批准重新有效。\n\n## 先按依赖顺序写界面，再构建\n\n`ui/` 是平台本身的控制面，`templates/frontends/` 是以后生成给业务产品的页面，两者不能互换。先读 `ui/src/types.ts` 与 `api.ts` 的数据和传输约定，再写 `presentation.ts`、`state.ts` 的状态变化，最后组装App和components。每一层都有独立责任：api只处理认证请求和流帧；state管理当前任务、游标和订阅寿命；展示函数把事件映射为消息；组件渲染表单、进度与操作。\n\n在学生项目根目录执行以下命令，不进入tools/node，也不在learning-docs目录安装依赖：\n\n```bash\n# .learning/commands/08-build-vue.sh\nnpm ci --prefix ui --no-audit --no-fund\nnpm test --prefix ui\nnpm run build --prefix ui\n```\n\n`npm ci` 根据lock安装，`npm test` 执行实际Vitest测试，build先做vue-tsc类型检查再由Vite输出 `workbench/web`。构建失败就停在这里，不使用工作区里原有app.js假装新源码已经成功。`npm run dev --prefix ui` 只适合开发热更新，代理目标见vite配置；正式 `rnd start` 使用本机后端提供的构建资源，不要求另开Vite服务器。\n\n生成的app.js、style.css和index.html在源码附页中按Base64资产快照折叠保存。它们无需手写；可读实现位于ui/src。这样只带教材既能逐字节还原已有运行资产，也能用完整源与锁重新构建。最后一站的独立验收会比较重新构建后的全部资产路径和字节，不允许漏文件或用旧bundle掩盖源码缺失。\n\n## 无账号的检查先走通\n\n```bash\n# .learning/commands/08-api.sh\nuv run pytest tests/test_api.py tests/test_guided_selection.py tests/test_cli_connection.py tests/test_streaming_backend.py tests/test_model_settings.py tests/test_clarification_choices.py -q\nuv run rnd --help\nuv run rnd doctor\n```\n\nAPI测试使用临时Store和明确测试网关，协议测试使用受控的增量HTTP传输；它们不接触自己的供应商账号。检查包括错误令牌401、恶意Host400、过期配置409、错误关卡冲突、幂等重复请求、真实协议增量先于最终结果、失败草稿清除和跨分块密钥脱敏。这是本机协议与交互逻辑的证据，不是已向真实付费模型成功请求的证据。未配置模型时doctor明确显示缺失，不能把它叫模型通过。\n\n## 第一次启动，先打开设置壳\n\n本阶段可以在没有供应商Key时启动操作台，页面会引导配置；创建运行及需要模型的后续操作仍拒绝无效配置，不会偷偷换成测试答案。`rnd init` 还会解压原生模板归档，分阶段读到这里先不运行它；归档要在第09站按固定上游来源准备。基础页面和模型设置不等于原生环境已经就绪。\n\n终端A在项目根目录保持服务运行：\n\n```bash\n# .learning/commands/08-live-start.sh\nuv run rnd start\n```\n\n终端B在同一项目目录取得本机令牌，输入终端A打印的页面地址：\n\n```bash\n# .learning/commands/08-local-token.sh\nuv run rnd token\n```\n\n令牌只输入自己的本机页面，不分享、不写入截图或教程。页面把它保存在当前内存，刷新后需要重新连接；它不是模型API Key。默认地址为 `http://127.0.0.1:8000/`，设置PORT后用实际打印地址。端口冲突先检查启动日志，不能看到旧页面就判断新服务已启动。平台仍只监听本机，没有公网多用户身份体系。\n\n## 一个需求怎样逐段出现\n\n连接后可先在首页或项目内写下需求，提交前再确认真实目录中的模板、前端、数据库和标题。HomeView负责创建项目（需要时）与运行，ProjectsView只负责已有项目列表和导航。页面创建运行只是提交受认证的HTTP请求，模型由Worker执行。`Runtime → ModelGateway → AuditedEventStream → AssistantStream → Store事件` 是文字产生链；`/runs/{id}/stream → ui/src/api.ts → state.ts → RunView` 是显示链。\n\n这里用带Authorization的fetch读取SSE，而不是把令牌放URL。TextDecoder保留不完整UTF-8字符，SSEParser等到空行才结束一帧；一帧可能跨多个网络块，也可能含多行data，注释心跳不应变成聊天消息。公开增量显示为待验证草稿，完成事件用严格校验后的完整公开内容收口，失败则清除草稿并显示安全错误。模型的隐藏推理、原始提示和补丁源码不会因此成为聊天内容。\n\n刷新不是“重新问一次模型”。页面先获取同一个快照的transcript与cursor，再订阅cursor之后的事件。断线按有界退避重连，每个事件id只应用一次。快速从运行A切到B时，`runGeneration` 和AbortController让A迟到的响应失效，不会把A的字填进B。关闭页面或断开订阅不等于取消后台任务，本版本不能把它说明为已经停止模型；真正运行状态始终以后台为准。\n\n服务商没有提供增量时，页面明确显示非流式结果，不以逐字动画伪装。任务阶段进度来自run状态、pending和事件；“等待确认”“预算暂停”“生成失败”“可交付”各有不同的后台含义。阅读进度抽屉时，应能在事件或报告中找到对应事实，而不是只看到一个装饰百分比。\n\n## 澄清选项与审批不是一回事\n\n单选、多选和文字问题来自当前Requirement.question_items。Questionnaire提交question_id、option_ids及用户补充，后端从当前pending取选项标签。比如“谁用第一版”已经从旧问题Q变为Q2，旧页即使仍能点击也不能排队；要刷新当前关卡、重新确认。必答项没完成，页面应解释缺项，服务器仍要再校验。\n\n补充回答只让需求继续分析。看到需求或计划卡片后再执行批准/拒绝；gate_id保护内容版本。智能推荐修改的是持续委托状态，不是一次普通提示，恢复人工确认影响后续关口。连续点击同一操作或网络重试必须保留相同幂等请求身份；旧版本冲突不能靠自动重发批准消除。\n\n## 模型设置：保存成功不等于连接测试成功\n\n设置页区分默认连接、需求、计划、代码和可选复核覆盖。GET `/settings/models` 只返回安全摘要与revision，不回填已保存密钥。保存使用PATCH/PUT及expected_revision，另一窗口已经写入时返回409；用户应读取最新版本重新核对，而不是让页面暗中覆盖。输入仍未保存时离开有提示，放弃修改也清除尚未保存的Key。\n\nKey操作明确区分保留、更换和清除；更换BaseURL必须为新服务输入独立Key，不能把旧服务Key自动带到新地址。同源认证、请求大小限制、文件锁与原子替换共同保护写入。本机配置文件包含秘密，POSIX要求600权限，路径不能是符号链接；不要将它加入Git或当成学习示例。正在执行的一次模型调用和它的重试使用固定配置快照，下一次调用才看到新配置。\n\n当前保存接口只做格式、继承、安全约束与持久化校验，不发起模型请求；界面的连接测试尚未开放，不能显示“保存即连接成功”。需要真实调用时由操作者明确配置自己的供应商并发起需求，费用与外部服务证据单独记录。\n\n## CLI连接语义保留\n\n`rnd chat` 不是独立服务启动器。终端A保持 `uv run rnd start`，终端B才运行chat、show、retry、recommend、manual或download。`client()` 用contextmanager管理HTTP连接，按同一份Settings.port构造地址，在初次交互之前先请求 `/health`。\n\n初次或后续 `httpx.ConnectError` 都转换为“无法连接本机平台”和另终端启动、检查PORT/日志的中文提示，退出码为1并关闭客户端。初次健康检查失败不会先询问项目；后续断连可能发生在交互开始后。服务端业务错误、模型配置缺失或审批拒绝，不属于这条连接错误。`tests/test_cli_connection.py` 的7类离线命令与2种成功/后续断连实例继续保护用户修复。\n\n## 本阶段练习与排错\n\n用受控测试先验证：两个增量在最终响应前可见；失败不留下已批准结果；刷新无重复文本；切到另一运行无串线；过期问题/配置保存被拒绝。真实页面测试见第14站的浏览器验收，它会实际启动服务并操作组件，不能用截一张静态原型图代替。\n\n白屏先看构建是否完成以及index引用的 `/ui/` 资产是否可达；401先重新输入本机令牌；模型配置503去设置页核对有效字段；SSE无文字先区分“没有公开字段增量”“兼容服务非流式”和“网络断开”。不要用允许跨源、移除认证或伪造完成事件来解决页面问题。下载仍要检查实际交付状态、批准与包哈希：READY表示运行验收后的交付；SOURCE_READY只允许拿到来源已核对的源码包，不等于原生平台已经编译、启动或浏览器验收。不能仅凭下载按钮说明项目已完成。\n\n## 看得见的能力范围，才能作出有效选择\n\n当前关卡存在报名入口冲突时，Vue操作台显示单独的能力范围提示，保留原始目标、当前模板边界及可选路径。尚未明确入口时说明需要选择，不先假定匿名；明确匿名或独立公众门户时说明暂不支持。选择已支持的登录后自行提交，要保留参赛者业务角色与本人记录权限；选择仅管理员录入则应是用户清楚作出的范围更正。\n\n这个提示来自服务器当前gate中的 `capability_conflicts`，不是前端扫描聊天关键词自行决定。刷新、重连、智能推荐切换和FAILED恢复后都必须仍对应当前关卡；提交仍带当前gate_id与选项ID。选项文字不等于批准设计，已知范围决策不会靠重复模型调用“投票”解决。第14站用真实浏览器检查新运行、旧运行恢复与选择后的状态。\n\n同一能力澄清在人工模式可保持 `WAITING_CLARIFICATION`，并显示can_approve=false；自动模式则由Runtime置为 `BLOCKED`，停止自动补全。入口未说明时 `unsupported=[]`，仅 `capability_conflicts` 要求选择；明确匿名/独立公众门户才属于已知不支持能力。不要只根据状态名推断所有报名目标都不可实现。\n\n## 把创建、队列和运行证据连成完整交互\n\n新增 `POST /batches` 复用普通运行契约，返回每项 project_id、run_id 与 QUEUED 状态。页面提交时保留幂等键；失败后保留草稿，改正文后才建立新的提交身份。项目列表分别呈现排队、处理中、待确认、失败和交付，并能打开各自运行。模板详情从同一目录读取 coding_standard，显示规范内容与版本。\n\n阶段与验收页签展示后端真实事件和已有报告。切换页面只影响订阅，不取消后台工作。窄屏也应能查看执行阶段，状态筛选必须覆盖 FAILED 与 PAUSED_LIMIT。恢复依旧调用当前 run 的真实重试或审批接口；不创建只有视觉效果的进度和操作。设计与批量API使用示例见 `docs/template-platform.md`。\n"
  },
  {
    "id": "09-native",
    "title": "原生快照与框架接入",
    "goal": "接入固定上游源码与真正的原生生成器，保持框架认证、菜单、ORM和前端风格。",
    "prerequisites": [
      "08控制入口齐全",
      "vendor清单、许可证、归档与脚本可复现",
      "Linux/WSL、PG/Redis、Node22、对应pnpm；芋道另需JDK17/Maven",
      "uv postgres额外依赖安装"
    ],
    "concepts": [
      "自有适配代码与第三方源码分开",
      "原生生成ZIP不等于运行验收",
      "专用空_codegen库",
      "原生风格与菜单鉴权属于验收"
    ],
    "steps": [
      "验证manifest与归档身份，再解压",
      "先学习native/native_modules与框架导出挂载",
      "学习environment/frontend/owned_lifecycle管理真实进程",
      "最后用独立原生CI脚本执行一个模板再另一个"
    ],
    "checks": [
      "三个归档SHA匹配且许可证齐全",
      "SOURCE_READY不能冒充READY",
      "真实编译/类型检查/浏览器各有报告",
      "恢复身份不匹配拒绝而不清库",
      "WSL2/Linux与postgres extra在输出目录、容器、数据库副作用前检查"
    ],
    "troubleshooting": [
      "psycopg缺失先安装postgres extra",
      "不得用已有业务库代替专用空库",
      "原生页面风格不符排查适配器，不能换通用页面"
    ],
    "boundaries": [
      "本节受固定上游版本和已适配组合约束",
      "原生运行很重，未运行矩阵必须明确未验证"
    ],
    "body": "## 原生不是给通用CRUD换一个名字\n\n`vendor.py` 根据manifest核对三个源码归档：FastapiAdmin、芋道后端、Vben前端。它们保留固定提交和许可证，解压复用也要重新核对源码身份。普通克隆已经带归档；从只有教材的空目录恢复时，要使用书中的完整重建路径，从指定公开提交重建归档，不能拿主分支最新ZIP代替。上游源码不是你自行实现的文件，教材应当清楚区分“重建上游快照”与“手写自有适配器”。\n\n`native.py` 知道各模板的固定来源与生成接口；`native_modules.py` 把已批准实体转成适合框架的数据库表和真实代码生成请求，再将导出文件装进原框架。FastapiAdmin继续使用自己的认证、模块、Vue管理端；芋道继续使用Java后端、菜单权限和Vben界面。字段和表名还要适配框架保留列、序列与逻辑删除约定，不能把Python Basic文件复制过去宣称原生。\n\n`native_environment.py` 准备本次后端与本机数据库连接，`native_frontend.py` 负责真实依赖、类型检查、构建与预览，`owned_lifecycle.py` 追踪本次启动的进程与端口。`native_style.py` 同时检查原生布局/主题指纹和生成页面组件。`native_lab.py` 组合这些真实操作，`native_recovery.py` 只在源码、Plan、数据库身份一致且明确可恢复的阶段继续；任意硬杀后的未知状态并不自动安全。\n\n## 固定源码去哪里取得，怎样处理\n\n本教材使用下列准确来源，提交号同时保存在 `scripts/vendor_templates.py` 和 `templates/vendor/manifest.json`，不是让读者任选最新版本：\n\n- [FastapiAdmin固定源码](https://github.com/fastapiadmin/FastapiAdmin/tree/1cd12c726ad9032c17ef85ce805ce991be60fbdf)：`1cd12c726ad9032c17ef85ce805ce991be60fbdf`\n- [芋道Cloud Mini固定后端](https://github.com/yudaocode/yudao-cloud-mini/tree/47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be)：`47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be`\n- [芋道Vben固定前端](https://github.com/yudaocode/yudao-ui-admin-vben/tree/1b14e889f529e245fd620daa720dcea6de0cc5e7)：`1b14e889f529e245fd620daa720dcea6de0cc5e7`\n\n推荐使用下一节的 `vendor_templates --fetch`：脚本为每份上游建立临时Git目录，只fetch指定SHA、detached checkout，再核对 `rev-parse HEAD` 完全相同。若你自己取得了上述固定版本的源文件，把三个根目录分别命名为 `fastapiadmin`、`yudao-backend`、`yudao-frontend` 放在同一个 `upstream-sources` 目录中，先核对来源和LICENSE，然后可用 `uv run python -m scripts.vendor_templates --source-root upstream-sources`。这个离线目录入口只打包你提供的文件，不能替你证明它们来自哪个提交；你必须保留获取记录并比对教材的固定来源摘要。\n\n打包不是压缩整台开发机。脚本排除 `.git`、`.venv`、node_modules、缓存、target、dist、logs、实际 `.env`、数据库、私钥和字体二进制；保留源码、迁移、依赖锁和LICENSE。遇到符号链接、异常大文件或许可证不符就停止。输出三个普通ZIP、三份LICENSE及manifest，其中有文件数、排除清单、归档SHA与按文件hash汇总的source_digest。\n\n`vendor.unpack_source` 先验归档SHA，再限制解压路径、重复条目、链接、敏感文件与大小，最后重新计算解压后source_digest。只有全部成立才发布本机源码目录。这个双层检查把“传输压缩包有没有变”和“真正源码有没有变”分开；下方pytest正是在验证这些事实。\n\n## 先过快照和环境边界\n\n原生层与独立交付帮助模块有顶层 `psycopg` 导入，开始这一层前安装额外依赖：\n\n```bash\n# .learning/commands/09-native-install.sh\nuv sync --locked --extra postgres\nuv run python -m scripts.vendor_templates --fetch\nuv run pytest tests/test_vendor.py tests/test_native_archive_limits.py tests/test_native_delivery_boundaries.py -q\nuv run rnd init\n```\n\n从空目录还原时没有预带第三方ZIP，上面的 `vendor_templates --fetch` 会用Git获取固定公开提交并重建三个归档；普通克隆且归档已核验存在时可略过这一重建步骤。该命令不是获取最新主分支，不跳过来源和解压后源码摘要校验。压缩库版本可能使ZIP压缩字节不同，因此重建后以脚本生成的新归档hash配合固定commit/解压源码摘要记录，不混用旧压缩hash。测试应无failed/error；`rnd init` 应创建本机状态、令牌并从已具备的归档解压模板，不覆盖已有 `.env`。这个命令完成不代表PostgreSQL、Redis、Java或Vue已经运行。\n\n### 重打包后，分阶段还原为什么可能暂停\n\n固定提交和解压后的源码摘要相同，也不保证不同zlib版本产出的ZIP压缩字节完全相同。此时变化的是 `templates/vendor/manifest.json` 中的 `archive_sha256`，脚本必须把它更新为你本机真实归档的摘要；固定commit、source_digest和文件数仍应与教材一致。若这些来源字段也不同，应先停止调查，不能把它解释成压缩差异。\n\n可选的 `--advance` 对已经还原的文件逐字节检查，因此这个正常的重打包变化也会触发保护，拒绝推进。这不代表模板源码丢失，也不是让你改掉校验。不要删除 `.learning-progress.json`、伪造其中的哈希，或把旧manifest强行盖回去：旧归档哈希可能与本机新ZIP不符。\n\n推荐改用“完整空目录还原后继续学习”路线。保留原 `student-project` 及其中的源码修改、状态、数据库和报告；不删除、不覆盖、不把它当作新项目的代码来源。在同时放着教材和原项目的父目录运行下列命令；新名字 `student-project-complete` 必须尚不存在或为空。若你原项目叫别的名字，先在终端确认当前位置再操作。\n\n```bash\n# .learning/commands/09-repack-continue.sh\nuv run --no-project --python 3.14 python learning-docs/rebuild.py student-project-complete\ncd student-project-complete\nuv sync --locked --all-extras\nuv run python -m scripts.vendor_templates --fetch\n```\n\nWindows PowerShell也可执行以上四行。这里一次性取得完整自有代码，之后不再对这个新目录使用 `--advance`；仍按第10站以后的教学顺序阅读、练习和验收。按第06站在新目录安装浏览器并重新设置其绝对模块路径，按第11站安装/构建Node工具，再运行需要它们的检查。原生实验继续遵守专用空数据库要求，不能为了复用已初始化的旧库而删除数据。最后按第14站从本机实际模板清单重新生成两套教材并检查一致性。\n\n手写路线本来就不需要进度账本；也可以保留当前目录、按后续完整源码页手写新文件。无论选哪条路，哈希保护都保持严格，不把“还原完成”当作依赖和服务已经准备完成。\n\nFastapiAdmin使用pnpm9.15.3，芋道Vben使用pnpm11.16.0；不要在同一全局安装中含糊地说“有pnpm即可”。两者需要Node22和本机PG/Redis，芋道还需要JDK17与Maven。按下一节的完整本机步骤准备专用 `*_codegen` 数据库。拒绝非空库时先检查归属，不能用DROP整库来让下一条命令变绿。\n\n## 从Ubuntu/WSL准备原生运行环境\n\n以下命令是Ubuntu x86_64的Bash，不是PowerShell。Windows先按 [Docker Desktop官方Windows安装说明](https://docs.docker.com/desktop/setup/install/windows-install/) 安装、启动Docker Desktop，自行阅读并决定接受许可条款，在Resources → WSL Integration启用你使用的Ubuntu；不要在同一个发行版里同时另装一套冲突Engine。工作目录放在WSL的Linux文件系统，重新安装Linux `.venv`，不能复用Windows的虚拟环境。\n\n已有Docker的读者先运行 `docker version`、`docker compose version`，前者必须同时显示Client和Server。尚未安装Docker的干净Ubuntu主机，可按 [Docker官方Ubuntu安装文档](https://docs.docker.com/engine/install/ubuntu/) 配置来源。下面仅适用于没有既有容器环境的受支持Ubuntu；有冲突包、现存服务或组织限制时先处理兼容性，不自动卸载别人的软件：\n\n```bash\n# .learning/commands/09-docker-ubuntu.sh\nsudo apt-get update\nsudo apt-get install -y ca-certificates curl\nsudo install -d -m 0755 /etc/apt/keyrings\nsudo curl --fail --silent --show-error --location https://download.docker.com/linux/ubuntu/gpg --output /etc/apt/keyrings/docker.asc\nsudo chmod a+r /etc/apt/keyrings/docker.asc\n. /etc/os-release\nprintf 'Types: deb\\nURIs: https://download.docker.com/linux/ubuntu\\nSuites: %s\\nComponents: stable\\nArchitectures: %s\\nSigned-By: /etc/apt/keyrings/docker.asc\\n' \"${UBUNTU_CODENAME:-$VERSION_CODENAME}\" \"$(dpkg --print-architecture)\" | sudo tee /etc/apt/sources.list.d/docker.sources\nsudo apt-get update\nsudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin\nsudo systemctl start docker\nsudo docker version\nsudo docker compose version\n```\n\n后续平台由普通用户运行。如果只有sudo能访问Docker，先阅读 [Docker安装后权限说明](https://docs.docker.com/engine/install/linux-postinstall/) 并决定是否赋予本机开发账户Docker组权限；该组近似root权限，不是一个无风险修复。不要把socket chmod成666，也不要开启公网Docker TCP端口。平台不代替你更改权限；正常用户 `docker version` 成功后才继续。\n\n芋道需要JDK17/Maven，FastapiAdmin可不安装这两项。Ubuntu准备命令如下，`mvn -version` 中显示的Java也必须为17；机器有多个JDK时先正确选择JAVA_HOME，不能只看另一个终端的 `java -version`：\n\n```bash\n# .learning/commands/09-native-language-tools.sh\nsudo apt-get update\nsudo apt-get install -y git curl ca-certificates xz-utils openjdk-17-jdk maven\njava -version\nmvn -version\n```\n\n原生Vben要求Node22.18或更新的22.x，比第11站Continue的最低22.13更严格。第06站若装了更早22.x，现在升级到满足原生要求的22.x。Ubuntu x86_64可安装固定官方用户目录二进制；下面不修改系统Node，不把哈希检查删掉：\n\n```bash\n# .learning/commands/09-node-linux.sh\nmkdir -p \"$HOME/.local/share/rnd-tools\"\ncd \"$HOME/.local/share/rnd-tools\"\ncurl -fLO https://nodejs.org/dist/v22.18.0/node-v22.18.0-linux-x64.tar.xz\ncurl -fsS https://nodejs.org/dist/v22.18.0/SHASUMS256.txt | grep ' node-v22.18.0-linux-x64.tar.xz$' > node.sha256\nsha256sum -c node.sha256\ntar -xJf node-v22.18.0-linux-x64.tar.xz\nexport PATH=\"$HOME/.local/share/rnd-tools/node-v22.18.0-linux-x64/bin:$PATH\"\nnode --version\nnpm --version\n```\n\n预期SHA检查为OK、Node为v22.18.0。ARM机器不能执行这个x64命令，应从官方页面取匹配架构；Daytona本教程明确只验Linux x86_64/WSL2 x86_64。重新打开终端后重设PATH，回到你的 `student-project` 根目录；不要在 `~/.local/share/rnd-tools` 安装平台依赖。Vben完整构建较重，预留足够磁盘与内存；失败时保留构建日志，不删除原生业务页面来缩减构建。\n\n## 建立只属于实验的PostgreSQL与Redis\n\n真实平台也能为获准运行自动创建独立Compose服务。为了理解原生CI脚本，下面显式创建实验服务。先确认 `rnd-learning-pg`、`rnd-learning-redis` 名称和本机5432/6379端口未被别的服务占用；有冲突先调查，不能强制删除。密码用随机值留在当前终端，不贴聊天或提交Git。\n\n```bash\n# .learning/commands/09-owned-services.sh\nexport NATIVE_PG_PASSWORD=\"$(uv run python -c 'import secrets; print(secrets.token_urlsafe(24))')\"\ndocker run -d --name rnd-learning-pg \\\n  -e POSTGRES_USER=native -e POSTGRES_PASSWORD=\"$NATIVE_PG_PASSWORD\" \\\n  -e POSTGRES_DB=fastapi_codegen -v rnd-learning-pg-data:/var/lib/postgresql/data \\\n  -p 127.0.0.1:5432:5432 postgres:17\ndocker run -d --name rnd-learning-redis -p 127.0.0.1:6379:6379 redis:7.4-alpine\ndocker exec rnd-learning-pg pg_isready -U native -d fastapi_codegen\ndocker exec rnd-learning-redis redis-cli ping\n```\n\nPG初始化可能需要几秒，尚未接受连接就稍后重跑 `pg_isready`，不要重发 `docker run`。成功分别看到accepting connections和PONG。容器内的实验native账户有创建独立验收新库所需权限；只用于这次回环开发服务。用你自己的现有PG账号时，需要先由拥有者明确提供专用空库和必要CREATEDB权限，不能自行扩大生产账号权限。\n\n为两个框架选择各自pnpm版本；下面将npm全局工具放在自己用户目录，避免sudo安装。首先跑FastapiAdmin：\n\n```bash\n# .learning/commands/09-fastapi-native-runtime.sh\nexport PATH=\"$HOME/.local/share/rnd-tools/npm-global/bin:$PATH\"\nnpm install --global --prefix \"$HOME/.local/share/rnd-tools/npm-global\" pnpm@9.15.3\npnpm --version\nexport NATIVE_TEST_DATABASE_URL=\"postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/fastapi_codegen\"\nuv run python -m scripts.ci_native_bundled fastapiadmin\n```\n\n本条是标准原生CRUD与独立新库验收，使用公开确定性规格，不调用真实模型。浏览器环境变量仍要延续第06站。成功后在 `reports/native` 阅读完整报告，而不是只看到生成ZIP。默认产物位于 `.native/product`。在全部测试进程退出后，将本次产物和报告移动保留，再准备另一个空库；不要让第二个模板覆盖第一个的证据：\n\n```bash\n# .learning/commands/09-preserve-first-native-run.sh\nmkdir -p .native/completed/fastapiadmin\nmv .native/product .native/completed/fastapiadmin/product\nmv reports/native .native/completed/fastapiadmin/reports\ndocker exec rnd-learning-pg createdb -U native yudao_codegen\nnpm install --global --prefix \"$HOME/.local/share/rnd-tools/npm-global\" pnpm@11.16.0\npnpm --version\nexport NATIVE_TEST_DATABASE_URL=\"postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/yudao_codegen\"\nuv run python -m scripts.ci_native_bundled yudao-vben\n```\n\n若目标保留目录或yudao_codegen已存在，停下来核对前一次实验，不靠覆盖/清库继续。两次pnpm版本输出应分别为9.15.3、11.16.0；第二条运行还要求Java17/Maven已经通过版本检查。这里先验原生基本能力；第10站客服测试要另建自己的空库和无冲突输出，不能在已经初始化过的库上重跑生成器。完成学习后可由你明确停止自己创建的两个容器，保留持久卷和报告；不要执行删除全部Docker资源的清理命令。\n\n## 分开记录源码导出与运行通过\n\n`SOURCE_READY` 只表示源码导出，不表示编译、权限、浏览器或独立新库部署通过。全运行前再次核对实际环境；下一站完成客服适配后，可分别执行下列标准客服矩阵命令：\n\n```bash\n# .learning/commands/09-native-customer-runtime.sh\nuv run python -m scripts.ci_native_bundled fastapiadmin --spec examples/plans/customer-service.json\nuv run python -m scripts.ci_native_bundled yudao-vben --spec examples/plans/customer-service.json\n```\n\n这里明确是“第10站业务文件齐全后回到这里执行”；执行前在本节实验PG中另建新的专用空_codegen库，并像上面一样以当前终端随机密码设置 `NATIVE_TEST_DATABASE_URL`，保留前次 `.native/product` 和报告；不要直接在书中写真实密码。每次只认本模板本次报告，先保存或分目录留存再跑另一模板，避免覆盖证据。合同测试只证明适配器拒绝/接受给定输入，真实原生通过要看编译、类型检查、HTTP、浏览器和独立新库部署。\n\n## 先检查可选依赖，后产生原生副作用\n\n基础Windows环境可以选择原生模板、读取能力和到达设计关卡，即使没有psycopg；这不表示Windows已支持原生执行。真正运行在WSL2/Linux进行，并在其项目目录安装：\n\n```bash\n# .learning/commands/09-postgres-extra.sh\nuv sync --locked --extra postgres\nuv run python -c \"import psycopg; print('PostgreSQL driver import PASS')\"\n```\n\n`native_delivery.prerequisites` 在加载实际 `native_lab` 执行入口前检查系统、驱动和必需命令。缺少驱动给出上面的安装命令和“重试同一运行”提示；必须在创建目标目录、Compose服务、复制代码和连接数据库之前停止。不要把try/except包住真实数据库失败后继续生成，也不要移除平台检查来让Windows误入Linux工具链。\n\n旧的 `FAILED` 运行补齐条件后从同一UUID恢复，继续使用历史需求、审批和检查点。若原目标曾被错误改成管理员代录，先完成第07/08站的能力范围澄清，再执行原生生成；依赖修好不等于旧设计已经获得新的有效批准。\n"
  },
  {
    "id": "10-business",
    "title": "角色权限与客服业务",
    "goal": "把标准客户服务合同实现成可审计的数据库事务和三角色界面流程。",
    "prerequisites": [
      "09原生适配完整",
      "三份客户需求与确定性Plan输入齐全",
      "business_*适配、policy、各框架业务模板与浏览器探针齐全"
    ],
    "concepts": [
      "默认拒绝动作授权",
      "own/assigned/all行范围",
      "命名转换与保护字段",
      "审计历史与提醒同事务",
      "统计必须尊重角色与行范围"
    ],
    "steps": [
      "先按三份需求梳理客户/请求/任务与角色",
      "从BusinessSpec回看policy的授权",
      "分别跟进Python/FastapiAdmin/Yudao事务适配",
      "跑正向业务与越权反例再真实浏览器"
    ],
    "checks": [
      "普通员工不能通过通用update改负责人或状态",
      "请求解决通知提交者",
      "read_history和read_audit各自授权",
      "统计不同过滤/分组有不同值",
      "重启后数据和提醒读状态保留"
    ],
    "troubleshooting": [
      "403/404先按批准动作与范围定位，不扩大角色权限",
      "空平均时长应为null而非伪造0",
      "处理记录字段不能替代真实不可改审计"
    ],
    "boundaries": [
      "仅站内提醒，不含外部邮件/短信",
      "业务合同不能与自由custom_rules混用",
      "fixtures中的未批准诊断不能作为生成计划"
    ],
    "body": "## 从个人CRUD走向团队业务\n\n现在回到标准案例：维护客户、创建服务请求、分配负责人、按批准动作推进状态、追加处理记录、协作任务、站内提醒和统计。三份输入有不同职责：原始需求保存业务目标，默认决策明确可执行选择，字段合同固定名称、枚举和类型。必须一起保留，不能把原需求改写成更小的任务后说完成。`examples/plans/customer-service.json` 是确定性验收输入，不是模型失败时的隐藏答案。\n\n`BusinessSpec` 把行为限制成可验证的结构。资源声明负责人字段、归档与历史；关系声明引用目标及restrict删除语义；permissions逐角色逐实体声明完整动作和范围；workflows给出命名转换、合法起始状态和时间戳写入；notifications明确事件与接收者；metrics明确计数、平均时长、分组和每日趋势。shared表示团队业务模型，不表示所有员工都能读全部记录。\n\n`templates/business/common/policy.py` 负责共同语义。默认没有动作就拒绝；own依据不可改的created_by，assigned依据批准的负责人字段，all才是全部可见范围。`read_history`、`read_audit`、`read_metrics` 是独立动作，不能由“能读记录”推导出“能读审计与统计”。角色从服务端实时读取；前端隐藏按钮只是辅助体验，HTTP直接请求仍必须被服务端拒绝。\n\n## 沿一笔“解决请求”追踪事务\n\n从页面点击命名动作resolve开始，先识别当前用户，再核对该角色对requests的transition权限和当前行范围；读取并锁定记录，检查原状态是否属于允许来源，然后修改状态并填写批准的完成时间。同一个事务还要追加服务端作者的审计/历史、生成要求的站内提醒。失败要整体回滚，不能出现“状态已解决却没有审计”，也不能允许普通update绕过命名转换。\n\nPython产品的 `business_schema.py`、`business_runtime.py` 生成表并实现事务；FastapiAdmin适配器与模板延续其原生控制器/ORM/事务；Yudao适配器生成Java服务、Mapper、控制器和原生表单面板。共同合同不意味着强行共用同一套前端或伪造框架事务。`business_schema_receipt.py` 与业务探针把实际SQL结构及行为证据绑定到设计。\n\n提醒要按源事件和接收者去重，读收件箱不能再产生一批提醒；标记已读只影响当前接收者。统计同样先授权再选行：总数与已解决数不能混用，创建到解决平均时长排除缺失端点的记录，零样本返回null，UTC日桶必须一致。增加未解决对照请求和第二类客户，是为了让错误的全量计数、分组或时长计算暴露出来。\n\n## 按层验收，不只看一个总passed\n\n```bash\n# .learning/commands/10-business-contracts.sh\nuv run pytest tests/test_business_contracts.py tests/test_business_capabilities.py tests/test_business_python.py tests/test_business_fastapi.py tests/test_business_yudao.py -q\nuv run pytest tests/test_business_audit_permissions.py tests/test_business_note_notifications.py tests/test_customer_employee_task_scopes.py tests/test_business_query_api.py -q\n```\n\n这些文件中一部分是真实生成产品HTTP/SQL，另一部分是适配器与证据合同；阅读文件说明，不能把全部统称原生运行。相关测试辅助文件和fixtures必须按源码索引齐全。浏览器工具准备好后：\n\n```bash\n# .learning/commands/10-business-browser.sh\nuv run pytest tests/test_business_python_browser.py -q\n```\n\n再回到第09节执行两种原生客服命令，分别保留真实报告。预期包括三角色授权正反例、客户关联选择、分配、start/resolve、备注、归档、提醒和统计，不只是“页面有几张卡片”。原生浏览器必须从登录与菜单进入实际业务路由，不能注入Token或截一张静态首页替代流程。\n\n如果一个计划缺动作或范围，先回需求与设计层判定批准内容；不要临时给员工管理员角色以让测试通过。失败的诊断候选Plan只是分析材料，只有确实已批准且通过合同检查的Plan才能进入生成。\n"
  },
  {
    "id": "11-local-tools",
    "title": "Continue、Plop与Aider",
    "goal": "在保留默认本机能力的基础上接入真实可选工具，并验证它们实际执行且边界未扩大。",
    "prerequisites": [
      "10业务完整",
      "Node22.13+与tools/node全部锁定文件",
      "Aider独立Python3.12项目完整",
      "原生规则实验需09原生运行环境"
    ],
    "concepts": [
      "索引引擎不等于完整IDE",
      "只读MCP",
      "Plop脚手架与Aider精确补丁分工",
      "模型网关与禁网编辑进程隔离"
    ],
    "steps": [
      "先npm ci/build准备Continue与Plop",
      "独立uv安装Aider并执行本机依赖自检",
      "按需切换RETRIEVAL_ENGINE/CODING_ENGINE",
      "用真实工具脚本读回执与Git前后提交"
    ],
    "checks": [
      "Continue回执指出固定上游组件实际update/retrieve",
      "Aider禁网自检通过",
      "Plop生成受信文件并挂载入口",
      "错误规则回滚后有限修复通过"
    ],
    "troubleshooting": [
      "Aider依赖冲突不要合并平台3.14环境",
      "SEARCH匹配多处或SHA过期应拒绝",
      "可选Node测试skip不等于已验证"
    ],
    "boundaries": [
      "真实模型Key只给网关，不进入编辑子进程",
      "不允许模型改鉴权、依赖锁、可信测试或任意命令"
    ],
    "body": "## 给每个工具一件可以检查的事\n\n第04站的AST/FTS已经能工作。现在接入可选增强工具：Continue使用仓库内固定提交的 `FullTextSearchCodebaseIndex.ts`，Node桥接负责本机SQLite宿主和update/retrieve调用；`continue_index.py` 核对桥接身份并执行它。这里不是安装整个IDE生命周期，也不读取IDE私有缓存。`context_mcp.py` 把同一检索与仓库地图作为只读stdio工具提供给支持MCP的客户端，不新增任意文件修改权限。\n\nPlop与Aider不负责同一层。`scaffolding.py` 根据批准规则注册允许文件和区域，由真实node-plop从受信模板放入框架规则与表单入口。`aider_tool.py`、`native_coding.py` 再把模型网关给出的精确SEARCH/REPLACE或受限表达式交给实际Aider，在隔离Git副本里应用。命中不唯一、前像SHA过期、未知路径、越界区域、非法表达式都拒绝。Aider退出码0只说明它完成编辑，不代表业务规则通过。\n\n原生规则需继续编译、类型检查、API正反例和真实浏览器；失败回滚候选文件，保留诊断，在有限次数内修复。客服声明式business路径无需自由编码，且不能与standalone custom_rules混用。把所有需求都推给编码模型，会破坏前面建立的确定性边界。\n\n## 安装边界必须显式\n\n```bash\n# .learning/commands/11-tool-install.sh\nnode --version\nnpm ci --prefix tools/node --no-audit --no-fund\nnpm run build --prefix tools/node\nuv sync --locked --project tools/aider --python 3.12\nuv run --locked --project tools/aider --python 3.12 python tools/aider/offline_runner.py --check-local-deps\n```\n\nNode应为22.13或更新的22.x；Aider自检应报告锁定依赖和禁网状态。此处Python3.12环境位于tools/aider，平台仍为3.14。不要为解决一个工具的版本冲突改写平台锁文件。依赖与浏览器安装属于准备期，实际编辑/检索不应临时下载模型元数据或编码资源。\n\n配置 `.env` 的 `RETRIEVAL_ENGINE=continue` 后重启平台，才会使用该引擎；`CODING_ENGINE=aider` 与 `REPO_MAP_PROVIDER=aider` 分别选择编辑与仓库地图。不是安装成功就已启用，也不是写了配置就已证明真实执行。\n\n```bash\n# .learning/commands/11-tool-check.sh\nuv run pytest tests/test_continue_index.py tests/test_aider_offline.py tests/test_native_tools.py -q\nuv run python -m scripts.ci_toolchain\n```\n\n可选Node测试可能在未准备工具时skip，必须查看摘要而不是只读退出码。`ci_toolchain` 会实际运行Aider、Continue、MCP和源码检索，并把证据写入 `reports/toolchain.json`；报告明确不声称Daytona服务已通过。此脚本包含已有产品工作流，故仍需浏览器工具。\n\n## 向量是独立选择\n\n`EMBEDDING_ENABLED` 默认为false。需要向量时按 `tools/embeddings` 的锁定项目和 `scripts/ci_local_embeddings.py` 准备本机权重与回环端点，然后检查真实CPU推理及融合证据。不能在本机服务连接失败时偷偷改成云地址。三份固定Vben源码的命中测试也不代表所有模板、所有中文问题都达到某个召回率；扩大范围要扩大数据和验收，而不是扩大口头承诺。\n\n\n### 亲手验证可选本机向量\n\n向量工具与Aider一样使用自己的Python3.12环境，不能安装进平台3.14里混用。准备期下载固定权重，验证期在回环HTTP服务中做真实ONNX CPU推理。下面Linux/WSL命令按顺序执行；Windows的最后一条 `--python` 改为 `tools/embeddings/.venv/Scripts/python.exe`。\n\n```bash\n# .learning/commands/11-local-embeddings.sh\nuv sync --locked --project tools/embeddings --python 3.12\nuv run --locked --project tools/embeddings --python 3.12 python scripts/ci_local_embeddings.py prepare\nuv run python -m scripts.ci_local_embeddings verify --python tools/embeddings/.venv/bin/python\n```\n\nprepare会检查固定模型文件身份，verify自行启动并关闭本次回环服务，结合真实Continue/AST/FTS检索，报告在 `reports/local-embeddings.json`。没有成功报告不算本机向量通过。这个验收服务的随机端口只属于本次测试；要长期启用平台向量，另按同一脚本的serve接口或你自己的已准备回环服务提供稳定端点，再将实际URL和模型名写入 `.env`，不要把一次测试端口当长期服务。\n\n\n若想直接用本脚本提供平台向量端点，在平台根目录的终端A运行下面命令；它持续运行，Ctrl+C只停止本次服务，不删除权重：\n\n```bash\n# .learning/commands/11-embedding-serve.sh\nuv run --locked --project tools/embeddings --python 3.12 python scripts/ci_local_embeddings.py serve --ready .data/embedding-ready.json\n```\n\n终端B读取本次实际回环地址：\n\n```bash\n# .learning/commands/11-embedding-address.sh\nuv run python -c \"import json; from pathlib import Path; print(json.loads(Path('.data/embedding-ready.json').read_text())['url'])\"\n```\n\n把打印的完整URL填入 `.env` 的 `EMBEDDING_BASE_URL`，设置 `EMBEDDING_MODE=sentence-transformers/all-MiniLM-L6-v2`、`EMBEDDING_API_KEY=local-no-auth`、`EMBEDDING_ENABLED=true`，然后重启平台。服务每次重开可能换端口，因此重启向量服务后重新读本次ready文件并核对；旧ready文件存在不证明进程还活着。这个服务只监听回环，外部请求不在本教程能力内。\n"
  },
  {
    "id": "12-daytona",
    "title": "本机沙箱与镜像",
    "goal": "准备固定版本自托管Daytona，验证离线快照内运行与本次沙箱清理，而不是只安装SDK。",
    "prerequisites": [
      "11本机直接工具与产品已验证",
      "Linux x86_64或Windows x86_64 WSL2，Docker可用",
      "daytona相关脚本、Dockerfile、会话/诊断/快照模块齐全",
      "明确同意本机资源创建与所需下载"
    ],
    "concepts": [
      "控制面、Runner、快照、业务验收是独立层",
      "准备期下载与运行期禁网",
      "模板数据库profile绑定镜像身份",
      "异步提交不自动重发",
      "清理属于交付条件"
    ],
    "steps": [
      "安装额外依赖后严格按prepare到snapshot执行",
      "基础SQLite快照先验收",
      "为PG/FastapiAdmin/Yudao分别预热matrix镜像",
      "检查报告绑定源码、运行、重启和删除"
    ],
    "checks": [
      "API健康且快照active",
      "对应组合在禁外网沙箱内完成真实验收",
      "report身份匹配当前源代码与profile",
      "删除本次sandbox成功"
    ],
    "troubleshooting": [
      "创建超时先读有限启动诊断，不能遍历别人的容器",
      "缺依赖返回镜像准备期，不运行时开放网络",
      "提交响应丢失不重发POST"
    ],
    "boundaries": [
      "Daytona0.190.0开发部署，不是托管云模式",
      "privileged Runner不是生产强隔离保证",
      "默认Python/SQLite镜像不能冒充Java/Vue环境"
    ],
    "body": "## 先让本机产品跑通，再隔离它\n\n沙箱不是修补不可运行项目的魔法。平台先做本机可信验证，Daytona再增加一层本机自托管执行证据。`sandbox.py` 校验配置和profile，打包受控源码与验收harness，创建本次命名的沙箱，传入不含主机模型Key和主机数据库密码的必要材料，再读回有大小与身份限制的报告。`daytona_worker.py` 在专门子进程内施加回环工具约束，不能把它描述为抵抗任意恶意代码的操作系统隔离。\n\n`daytona_profiles.py` 按模板/数据库决定快照与必须的检查项目：Python/SQLite、Python/PostgreSQL、FastapiAdmin/PostgreSQL、Yudao/PostgreSQL各有真实依赖。数据库和Redis在适用沙箱内初始化，不把主机的正式库连接串复制进去。源码hash、锁文件身份与镜像回执串起来，才能知道这份环境究竟验了哪个产品。\n\n`daytona_sessions.py` 对长运行使用一个异步命令提交，后续短GET轮询，最后读日志。请求超时不证明服务器没执行，因此不能重发一个可能已成功的POST来“再试一次”。输出目录保护和总预算同样保留；状态pending时不允许写passed。\n\n## 严格按顺序准备固定版本\n\n这是较重的可选能力，只在你确实准备好Linux/WSL、Docker及本机资源后执行。若尚未安装浏览器、Node工具、Aider和基础产品依赖，先回前面章节。\n\n```bash\n# .learning/commands/12-daytona-prepare.sh\nuv sync --locked --all-extras\nuv run python -m scripts.daytona_local prepare\nuv run python -m scripts.daytona_local images\nuv run python -m scripts.daytona_local snapshot-image\nuv run python -m scripts.daytona_local up\nuv run python -m scripts.daytona_bootstrap auth\nuv run python -m scripts.daytona_bootstrap snapshot\nuv run python -m scripts.ci_daytona_local\nmkdir -p reports/daytona-python-sqlite\ncp .data/daytona-local/snapshot-image.json reports/daytona-python-sqlite/snapshot-image.json\ncp reports/daytona-local.json reports/daytona-python-sqlite/daytona-local.json\n```\n\n每一步退出码为0并得到对应回执后才执行下一步。prepare固定上游并写本机配置；images构建固定控制面与Runner；snapshot-image预热基础离线执行环境；up启动本机服务；auth建立本机认证；snapshot登记可运行快照。最后验收才说明业务和工具实际执行。CLI存在、API健康、快照active、产品通过和沙箱删除是五个不同事实。\n\n`.data/daytona-local` 含本机随机凭据和状态，不进入Git或交付ZIP。服务端口只绑定回环，内部服务网络和Runner网络按脚本分开；不要为了排错把它暴露到公网。安装阶段下载公共依赖与运行阶段外联业务工具是不同事件。\n\n## 三个PostgreSQL profile逐个做，不猜参数\n\n下列命令来自实际 `ci_daytona_matrix`、`daytona_matrix_image`、`ci_native_tools` 的参数定义。先完成本节基础Daytona服务，且第09站PG/Redis、第11站Aider/Node/浏览器仍可用。每次只做一个profile，并在切换前保留报告；`.data/daytona-local/snapshot-image.json` 会被最新镜像覆盖，不能最后才回头猜前面快照名。\n\n### A. Python/PostgreSQL\n\n它使用明确的确定性新闻CRUD规格检查数据库型别，不冒充客服业务矩阵或真实模型。\n\n```bash\n# .learning/commands/12-python-postgres-matrix.sh\nuv run python -m scripts.ci_daytona_matrix prepare-basic python-basic --product .native/daytona-python-pg\nuv run python -m scripts.daytona_matrix_image python-basic --database postgresql --product .native/daytona-python-pg\nuv run python -m scripts.daytona_bootstrap snapshot\nuv run python -m scripts.ci_daytona_matrix verify python-basic --product .native/daytona-python-pg\nmkdir -p reports/daytona-python-pg\ncp .data/daytona-local/snapshot-image.json reports/daytona-python-pg/snapshot-image.json\ncp reports/daytona-matrix.json reports/daytona-python-pg/daytona-matrix.json\n```\n\n首次prepare要求目标尚不存在；反复执行时遇到保护要核对原生成回执，不能删数据库来“刷新”。build步骤过滤产品文件、预热锁定依赖，推送本机registry并写不可变image_id；snapshot确认已登记的同名快照来源一致且active后，更新本机 `workbench.env`。verify从该配置读取准确快照名，要求passed、cleanup=deleted、host_credentials_used=false、host_database_used=false。\n\n### B. FastapiAdmin/PostgreSQL\n\n先在第09站实验PG创建一个新的专用空库，不能用已经完成客服或原生生成的库。这里沿用当前终端的 `NATIVE_PG_PASSWORD`；若你换了终端，先从自己的安全保存处恢复它，不把密码打印进日志。\n\n```bash\n# .learning/commands/12-fastapiadmin-matrix.sh\ndocker exec rnd-learning-pg createdb -U native fastapi_tools_codegen\nexport NATIVE_TEST_DATABASE_URL=\"postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/fastapi_tools_codegen\"\nexport PATH=\"$HOME/.local/share/rnd-tools/npm-global/bin:$PATH\"\nnpm install --global --prefix \"$HOME/.local/share/rnd-tools/npm-global\" pnpm@9.15.3\nuv run python -m scripts.ci_native_tools fastapiadmin --output .native/daytona-fastapiadmin\nuv run python -m scripts.daytona_matrix_image fastapiadmin --database postgresql --product .native/daytona-fastapiadmin\nuv run python -m scripts.daytona_bootstrap snapshot\nuv run python -m scripts.ci_daytona_matrix verify fastapiadmin --product .native/daytona-fastapiadmin\nmkdir -p reports/daytona-fastapiadmin\ncp .data/daytona-local/snapshot-image.json reports/daytona-fastapiadmin/snapshot-image.json\ncp reports/daytona-matrix.json reports/daytona-fastapiadmin/daytona-matrix.json\nmv reports/native-tools reports/daytona-fastapiadmin/native-tools\n```\n\n`ci_native_tools` 先用真实原生生成器产出模块，故意中断后恢复，再用显式测试模型给出错误规则、验证真实反例失败与回滚、下一轮修复，再做后端、前端、浏览器和独立新库验收。它成功后才能拿输出目录制作快照。只运行daytona_matrix_image不包含这部分原生编辑链证明。\n\n### C. Yudao/PostgreSQL\n\n保留上一profile报告后，再准备Java17/Maven、pnpm11.16.0与另一个新空库；不得把FastapiAdmin产品目录当作Vben源：\n\n```bash\n# .learning/commands/12-yudao-matrix.sh\ndocker exec rnd-learning-pg createdb -U native yudao_tools_codegen\nexport NATIVE_TEST_DATABASE_URL=\"postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/yudao_tools_codegen\"\nnpm install --global --prefix \"$HOME/.local/share/rnd-tools/npm-global\" pnpm@11.16.0\njava -version\nmvn -version\nuv run python -m scripts.ci_native_tools yudao-vben --output .native/daytona-yudao\nuv run python -m scripts.daytona_matrix_image yudao-vben --database postgresql --product .native/daytona-yudao\nuv run python -m scripts.daytona_bootstrap snapshot\nuv run python -m scripts.ci_daytona_matrix verify yudao-vben --product .native/daytona-yudao\nmkdir -p reports/daytona-yudao\ncp .data/daytona-local/snapshot-image.json reports/daytona-yudao/snapshot-image.json\ncp reports/daytona-matrix.json reports/daytona-yudao/daytona-matrix.json\nmv reports/native-tools reports/daytona-yudao/native-tools\n```\n\n每条命令成功后再向下执行，不能把失败命令与后续命令一起粘贴后只看最后的cp。脚本给Yudao快照登记10GiB内存、30GiB磁盘，基础/FA的PG profile使用4GiB内存、30GiB磁盘；主机还要承担控制面和构建，因此实际主机需要更多可用资源。内存不足先增加你明确控制的本机资源或调整实验安排，不省略类型检查、权限测试和浏览器。\n\n### 把多个已通过快照接回日常平台\n\n上面的单profile验收会由bootstrap自动把当前准确快照写到 `.data/daytona-local/workbench.env`。日常平台的 `.env` 与这份工具配置不是同一文件；不要直接覆盖 `.env` 而丢掉模型配置。将本机Daytona连接配置私下合并到现有 `.env`，其中Key只留本机；多profile名称分别读取已保留的snapshot-image.json的snapshot字段。下面是需要编辑的字段说明，不是可原样执行的虚假名称：\n\n```dotenv\n# .env\nSANDBOX_PROVIDER=daytona\nDAYTONA_ALLOW_LOCAL_EXECUTION=true\nDAYTONA_API_URL=http://127.0.0.1:3000/api\nDAYTONA_TARGET=local\nDAYTONA_RUNTIME_TIMEOUT=3600\nDAYTONA_SNAPSHOTS={\"python-basic/postgresql\":\"替换为Python-PG回执snapshot\",\"fastapiadmin/postgresql\":\"替换为FastapiAdmin回执snapshot\",\"yudao-vben/postgresql\":\"替换为Yudao回执snapshot\"}\n```\n\nSQLite基础profile继续使用前面基础回执的 `DAYTONA_SNAPSHOT`；也需保留其准确名字。确认没有占位词后重启平台。镜像source_hash受锁文件和Docker构建输入约束；源码变化不一定改变依赖快照身份，但每次上传与运行仍需绑定新源码hash。缺依赖时显式重建对应镜像，不运行时放开外网。\n\n## 复杂模板单独预热，失败后保留证据\n\n基础镜像并不包含Java/Vue完整原生环境。先根据本次实际生成目录，通过 `daytona_matrix_image.py` 等本阶段完整脚本预热各profile，将快照回执中的准确名称填入 `DAYTONA_SNAPSHOTS`。不要自行猜快照名，不把Python镜像改名当作Yudao镜像，也不在缺依赖时开放运行期网络。\n\n需要诊断时显式开启 `DAYTONA_CAPTURE_STARTUP_DIAGNOSTICS`。诊断仅限本次已确认身份的沙箱、限定日志尾部与时间预算、先脱敏，再继续原清理路径。即使日志采集成功，创建超时或业务失败也仍然失败。最后确认应用端口关闭、重启检查成立、沙箱删除成功；清理失败是交付阻塞，不是可忽略的收尾。\n\n```bash\n# .learning/commands/12-daytona-contracts.sh\nuv run pytest tests/test_daytona_snapshot.py tests/test_daytona_sessions.py tests/test_daytona_startup_diagnostics.py tests/test_daytona_matrix.py -q\n```\n\n这些合同与反例测试可以在没有完整服务时解释边界，不能代替上面的真实自托管运行，更不能代替三行原生/PG矩阵。最终报告按每种profile逐项写passed、failed或未运行。\n"
  },
  {
    "id": "13-delivery",
    "title": "独立交付与重启",
    "goal": "把已验证源代码打包，在干净目录、独立依赖和新数据库重复验证，并保留重启数据。",
    "prerequisites": [
      "所选模板相关运行与浏览器证据通过",
      "portable、portable_checks、native_delivery与deployment模板完整",
      "交付ZIP来自当前源码摘要而非历史输出"
    ],
    "concepts": [
      "构建目录成功不等于交付包独立成功",
      "包内只含源码和初始化语句",
      "不可恢复删除不是排错手段",
      "测试后源码变化使旧报告失效"
    ],
    "steps": [
      "跟踪package_basic的临时ZIP→安全解压→再安装→再验证",
      "学习portable导出固定helpers与原生种子",
      "独立目录启动并验证重复启动保留数据",
      "核对delivery.json与archive SHA"
    ],
    "checks": [
      "cleanroom.passed=true且源码manifest一致",
      "独立依赖标志为true",
      "产品无需平台PYTHONPATH或模型Key",
      "重启后业务数据/密码不重置"
    ],
    "troubleshooting": [
      "缺包内模块应修正导出清单，不从平台借文件",
      "新库保护报错先检查真实空库",
      "--skip-build仅在同产品先前构建成功后使用"
    ],
    "boundaries": [
      "源码包不是实际业务数据备份",
      "production_ready仍为false",
      "独立启动不等于生产安全认证"
    ],
    "body": "## 最后一次验证要离开原工作台\n\n`verification.package_basic` 并不在得到一个passed后马上返回下载链接。它先重算文件manifest，确认报告绑定当前源码，再写临时ZIP；随后在新临时目录安全解压，检查包中文件是否与通过验证的文件一致，安装独立产品环境，再跑真实迁移、HTTP、重启和浏览器。全部成立后才原子替换成正式 `delivery.zip` 并保存 `delivery.json`。\n\n这条链解决一个常见错觉：原生成目录能运行，可能因为借用了平台venv、环境变量或未打包文件。干净解压要清楚证明产品自身代码与锁文件足够。`install_products=False` 的开发测试能验证很多行为，但其回执会明确说明没有隔离安装；不能把它当成完整独立交付证据。\n\n原生交付由 `portable.py` 冻结必需帮助模块、原生源码、SQL和菜单种子，`templates/deployment` 提供独立启动器。`portable_checks.py` 检查恢复后的数据与行为，`native_delivery.py` 对原生运行、业务、页面风格、来源身份和报告作交付门禁。它们可能因09层的导入闭包而提前写入，但只有这一站完整讨论“去掉原平台后还剩什么”。\n\n## 先跑真实独立环境验收\n\n```bash\n# .learning/commands/13-clean-install.sh\nuv run python -m scripts.ci_clean_install\nuv run pytest tests/test_delivery_clearance.py tests/test_native_delivery_boundaries.py tests/test_native_delivery_diagnostics.py -q\n```\n\n第一条需要第06站浏览器准备和正常依赖下载环境，成功应输出 `PASS: genuine product venv + separate clean-room venv; HTTP CRUD/isolation/restart; fixture model only`，并产生 `reports/clean-install.json`。报告中的模型是明确夹具，但两个独立venv、HTTP/浏览器和重启是真执行。第二条检查拒绝边界与诊断，不代替两种原生真实新库运行。\n\n真实任务达到READY后，用 `rnd show` 检查报告再下载。下列 `运行UUID` 要替换为你的实际任务标识：\n\n```bash\n# .learning/commands/13-download.sh\nuv run rnd show 运行UUID\nuv run rnd download 运行UUID\n```\n\n把得到的ZIP解压到一个全新目录，进入含 `start.py` 的产品根目录；下面的命令不在平台根目录执行：\n\n```bash\n# .learning/commands/13-product-start.sh\nuv run --no-project --python 3.14 python start.py\n```\n\n基础SQLite产品会安装自己的锁定依赖并迁移启动。基础PostgreSQL产品使用自己的Docker Compose随机凭据与持久卷，或明确的本机 `PRODUCT_DATABASE_URL`。原生产品按自身启动器建立新的独立数据库与服务，并打印实际前端地址；需要专用空库时按启动器契约配置 `NATIVE_DELIVERY_DATABASE_URL`，绝不能用生成器开发库冒充新库验收。\n\n## 数据必须能留住，也必须不被带走\n\n客服产品先在产品目录执行 `uv run python manage.py bootstrap-admin --username manager`，在隐藏终端输入中设置管理员密码。重复执行不能覆盖原管理员，重复启动不能重置业务记录和密码。手工创建一条请求、停止后重新启动，再确认仍可登录且记录存在；内置验收也要记录重启结果。\n\n源码ZIP包含初始化/迁移语句，不包含实际用户数据库、`.env`、模型密钥或运行日志。它不是业务备份。不要用“删除数据库后成功启动”替代恢复性验证；原生 `--skip-build` 只适合同一个产品此前确已构建成功的情况，也不是第一次交付省略构建的快捷方式。即使所有开发验收通过，回执仍明确 `production_ready=false`，不把本机开发产品当作公网生产部署认证。\n\n## 平台自己的wheel也必须带上操作台\n\n上面的业务交付ZIP和这里的平台Python wheel是两种产物。平台的可编辑前端源在 `ui/`，生产静态资产在 `workbench/web/`；`rnd start` 从包内提供它们，而不是去找你的Vite开发服务器。因此先按第08站用lock构建，再做打包和干净安装验证；只有原仓目录能打开页面不能证明wheel完整。\n\n静态资产作为教材的精确快照只是为了独立恢复。最终目录验收会从还原的ui源重新执行npm ci、单元测试、类型检查与生产构建，然后核对整个workbench/web文件集合和逐字节内容。多一个旧chunk、漏一个CSS、或bundle与源不一致都应失败；不能选择忽略压缩文件差异来获得通过。发生差异先核对实际Node版本、锁文件和构建配置，并保留原报告，不能把源代码缺项误报成“平台环境已验证”。\n"
  },
  {
    "id": "14-acceptance",
    "title": "全平台验收与证据阅读",
    "goal": "按同一源码身份汇总所有能力层，明确通过、失败、跳过和未运行，完成真正可复现的平台。",
    "prerequisites": [
      "00—13全部实现页与测试支持文件齐全",
      "完整依赖与可选服务按所选矩阵准备",
      "本次源码版本、日志、报告可追溯"
    ],
    "concepts": [
      "全量源码重建与功能执行是独立证据",
      "单元/集成/浏览器/真实供应商分层",
      "同一提交同一模板同一数据库组合",
      "没有报告就没有通过结论"
    ],
    "steps": [
      "运行格式与全套非PG回归",
      "独立跑PG与原生/客服/工具/Daytona矩阵",
      "检查教材还原与源码一致性",
      "汇总最终证据并标明未运行项"
    ],
    "checks": [
      "lint/format/pytest都明确成功",
      "完整重建文件与源码一致",
      "每项对应真实报告与同一提交",
      "失败诊断和未批准候选不混入交付",
      "目录独立还原后，报名范围真实浏览器检查另存唯一证据且失败关闭"
    ],
    "troubleshooting": [
      "skip先读原因不能算通过",
      "超时清理后保留失败状态与已产生JUnit",
      "真实模型脚本带授权部署限制，不伪造环境绕过"
    ],
    "boundaries": [
      "不预填全绿，不用别的提交或模板证据替代",
      "真实DeepSeek脚本不是通用本地任意模型测试入口",
      "教材源码一致性不等于运行矩阵通过"
    ],
    "body": "## 现在才到“整个项目”\n\n前面的每站都有一个小而真实的完成条件：合同能拒绝错误、事务能回滚、索引能拒绝过期、产品能运行、状态机能恢复、业务能拒绝越权、交付能在新目录重启。最后的全平台验收不是把这些文字勾选一遍，而是在最终文件集合上重跑对应检查，并核对报告属于同一个源码版本。任何后续改动都可能使旧报告失效。\n\n## 先生成教材，再检查；先准备工具，再跑全套\n\n如果你是从空目录手抄或还原出来的学生项目，根目录的生成版完整手册和新的 `learning-docs` 可能尚不存在。所有第14站源码和正文源文件都齐全后，先按第08站从ui源码构建静态资产，再生成它们，最后用 `--check` 检查；检查命令只核对现有输出，不替你创建缺失输出。\n\n```bash\n# .learning/commands/14-build-books.sh\nnpm ci --prefix ui --no-audit --no-fund\nnpm test --prefix ui\nnpm run build --prefix ui\nuv run python -m scripts.build_handbook\nuv run python -m scripts.build_learning_docs\nuv run python -m scripts.build_handbook --check\nuv run python -m scripts.build_learning_docs --check\n```\n\n完整非PostgreSQL回归也需要第06站的Playwright/Chromium和当前终端的 `PRODUCT_VERIFY_PLAYWRIGHT`、`PLAYWRIGHT_BROWSERS_PATH=0`，以及第11站真实Node组件。先运行 `npm ci --prefix tools/node --no-audit --no-fund` 和 `npm run build --prefix tools/node`。测试必须强制实际Node组件存在，Linux/WSL在同一终端设置：\n\n```bash\n# .learning/commands/14-node-required-linux.sh\nexport RND_REQUIRE_NODE_TESTS=1\n```\n\nWindows PowerShell设置：\n\n```powershell\n# .learning/commands/14-node-required-windows.ps1\n$env:RND_REQUIRE_NODE_TESTS = '1'\n```\n\n没有这些前提时先标记阻塞，不把可选工具skip当作全平台通过。然后执行最广的静态与基础回归：\n\n```bash\n# .learning/commands/14-base-regression.sh\nuv sync --locked --all-extras\nuv run ruff check .\nuv run ruff format --check .\nuv run pytest -m \"not postgres\" -q\nuv run python -m scripts.build_handbook --check\nuv run python -m scripts.build_learning_docs --check\n```\n\n`ruff` 要真实通过，不能因返回非零就自动改成忽略规则。非PostgreSQL套件包含需要浏览器和若干可选工具的测试，先查看test markers与skip原因；“not postgres”不代表“只需Python且所有工具都模拟”。原有完整手册一致性检查应输出 `Single handbook source consistency PASS`；新分阶段教材的检查命令同样必须退出码为0，二者各自证明对应文档与源码一致，不能互相替代。\n\n最后验证“只带教材目录”的完整重建，而不是从原仓库偷借依赖或ZIP：\n\n```bash\n# .learning/commands/14-textbook-clean-room.sh\nuv run python -m scripts.ci_learning_docs\n```\n\n该脚本复制教材到临时目录，用标准库还原全部自有文件；先按 `PLAYWRIGHT_BROWSERS_PATH=0` 真正启动并关闭Chromium，核对第06站要求的本地浏览器安装位置，再安装学生项目独立venv；用还原出的ui/package-lock.json执行npm ci、Vitest、类型检查和生产构建，并将所有新资产与教材快照逐字节比较；然后从固定上游提交重建三个模板归档，构建真实Node组件，执行还原平台的真实Vue浏览器验收，再执行真实完整非PostgreSQL回归。它还核对手册和分阶段教材能再生成一致；不是只检查文件数就打印PASS。需要公开依赖下载、Node和已安装浏览器，成功与否查看 `reports/learning-docs-clean-room.json` 和对应测试结果。超时、依赖失败、测试失败都保留原失败阶段，不能手工把报告中的passed改成true。原生服务、PostgreSQL和Daytona完整矩阵仍需各自环境与证据，这个脚本不声称验证了那些未启动服务。\n\n## 单独执行Vue真实页面验收\n\n在第06站安装的Playwright 1.56.1/Chromium可用、当前终端已设置PRODUCT_VERIFY_PLAYWRIGHT及PLAYWRIGHT_BROWSERS_PATH=0、tools/node已安装构建、ui已按第08站构建后，于项目根目录执行：\n\n```bash\n# .learning/commands/14-vue-browser.sh\nuv run python -m scripts.ci_guided_browser\n```\n\n这条命令启动真实本机FastAPI和Chromium，用明确的本机HTTP模型夹具控制增量及结束时机，操作Vue页面、人工/委托关卡、刷新、过期冲突、设置和下载，还保留生成产品页面回归。它不使用真实供应商账号。阅读 `reports/guided-browser/summary.json`、`workbench.json`、各步骤log与 `screenshot-manifest.json`，同时检查实际桌面/窄屏截图；启动或任何断言失败都不得叫通过。单独的pytest夹具保护测试不等于执行了这条浏览器命令。\n\n`ci_learning_docs` 也会在只从教材还原的新项目中调用同一driver，每次独立证据复制到 `reports/learning-docs-guided-browser/本次唯一编号`，当前目录记在learning-docs-clean-room.json的frontend.browser.evidence_directory中，失败重跑不混入上次成功summary或截图，再进入完整非PostgreSQL套件。源工作区浏览器成功和教材还原后浏览器成功分别记录，不能互借结果。失败时保留已经产生的日志或截图，不改场景、移除认证或写入假summary来通过。\n\n## 建立一份不冒进的验收记录\n\n每一层写清输入身份、命令、环境前提、实际结果、报告位置和未覆盖范围。建议按下面顺序读证据：\n\n1. 安装与还原：Python3.14、锁文件、完整自有源码、固定第三方归档与许可证；若从教材还原，逐文件hash相等\n2. 内核与操作台：合同、数据库、需求覆盖、来源冲突、真实增量协议、本机设置、幂等与审批恢复；Vue类型/组件测试和真实浏览器另有结果\n3. 基础产品：生成回执、独立依赖、HTTP、真实浏览器、两用户隔离与重启\n4. 客服业务：三角色动作/行范围、关联、分配、命名状态、历史、审计、提醒、指标与查询\n5. 原生模板：分别记录FastapiAdmin和Yudao的生成、SQL、编译、类型检查、原生页面与独立新库启动\n6. 工具链：实际Continue、Plop、Aider、MCP及可选本机向量；不能只记录安装版本\n7. Daytona：对应profile的真实离线执行、重启、端口与沙箱清理；基本镜像不代表全部矩阵\n8. 真实模型：服务商实际响应与完整需求流程；不能拿协议夹具或确定性Plan重放来代替\n\n每项只能写passed、failed、pending、skipped或未运行的真实状态。一个总passed不能抵消缺少必须的逐实体/逐字段浏览器checks；一张旧截图不能证明当前提交；某个模板成功不代表另一个模板成功。源码包中的业务数据为空是正确交付边界，不能因此声称真实业务备份恢复已被验证。\n\n## 真实模型与CI有自己的权限边界\n\n`scripts/ci_real_model.py` 是仓库专门的受限真实供应商验收，代码检查固定仓库、允许ref、手动dispatch、地址与模型，不是给任意本地模型的通用命令。不要在本机伪造GITHUB_ACTIONS等变量绕过门禁，也不要改服务商或预算后继续沿用原来的验收名称。普通本机体验使用已完成的 `rnd start/chat` 和你自己的配置；正式真实供应商证明按该工作流的实际授权与证据要求执行。\n\n批准的合成Plan可做确定性重放；失败时保存的Requirement/Plan诊断明确未批准，不能被当作备用生成答案。模型语义审阅同样只提供有依据的额外意见，不能把HTTP或浏览器失败改成成功。\n\n## 完成后能够独立解释的十个问题\n\n不要背文件名，试着从输入走到结果：为什么改模型地址必须换Key？为什么下一轮遗漏不删除事实？为什么批准绑定gate_id？为什么生成器保留旧目录？为什么搜索索引要核对SHA？为什么隐藏按钮不等于权限？为什么状态、审计和提醒同事务？为什么模型不能改测试？为什么新目录要再装依赖？为什么沙箱删除也会阻止交付？\n\n能用本项目的真实函数、调用方和失败测试回答这些问题，才说明你掌握了平台的构造，而不只是拥有一份源码。所有缺失服务与未运行矩阵继续明确列出；完整实现、可运行基础链路、全面环境验收是三个相关但不同的结论。\n\n## 怎样证明流式页面，而不是证明打字动画\n\n后端协议测试要让受控HTTP响应先发两个有间隔的增量、最后才结束，并断言结束前已有公开delta；Vue解析器单元测试检查半帧、中文分块，状态单元测试检查认证、幂等键与锁定后的迟到请求。openRun订阅、真实刷新/重连去重、切换任务和草稿到完成的联动由浏览器验收另行操作，不能把纯函数测试当作整条页面链已通过。三层各证明一段链，不相互冒充。\n\n失败流必须清掉未验证草稿，非流服务必须标记non_streaming，断开订阅不能额外调用模型或停止持久Worker。设置页要实际操作保留/更换/清除Key与409版本冲突，不能把“表单保存”记为“供应商连接测试”。所有测试输入用合成Key和受控协议；如未运行真实付费供应商，报告明确写未运行。\n\n`reports/learning-docs-clean-room.json` 的frontend字段记录目录还原后的独立npm测试、类型/构建、资产字节比较，以及还原平台的真实HTTP/Chromium流式页面结果。只运行manifest校验或格式检查不能替它填写passed。UI改动后必须在最终组合源码上重生两套教材并运行受影响验证，之前文档版本或原型截图不能当新界面的验收结果。\n\n## 报名入口与历史FAILED恢复的独立浏览器证据\n\n在上面的真实浏览器前提全部成立后，另跑报名范围专用driver：\n\n```bash\n# .learning/commands/14-signup-scope-browser.sh\nuv run python -m scripts.ci_signup_scope_browser\n```\n\n`scripts/signup_scope_browser.cjs` 操作真实Vue页面与本机API，模型使用显式进程内需求网关夹具。它先恢复一个真实旧FAILED设计检查点，核对同run身份、原始报名目标和既有delegated-ai审批，再检查桌面/窄屏能力提示、旧进度不误显示完成、范围没有默认选项、重复智能推荐不消耗模型调用，以及先选管理员后改选登录后自行提交时只发送最终选择。成功停在WAITING_REQUIREMENTS，不启动原生生成，也不宣称新建任务、显式匿名分支或全部原生全栈的浏览器验收已经完成；这些范围分支另由后端回归保护。\n\n`ci_learning_docs` 在教材独立还原后也执行该driver，并把本次证据单独复制到 `reports/learning-docs-signup-scope-browser/本次唯一编号`。它必须先检查 `browser.json` 的真实浏览器、范围及恢复断言和进程内夹具模式，并核对ui_bundle_sha256与还原后的资产、screenshot_sha256与保留的PNG字节一致，才可进入最终全套通过；任何缺字段、假布尔值、失败或遗留summary都不能冒充成功。流式页面证据和报名范围证据分别保存，各自的失败日志/截图仍应保留。\n\n## 用三种业务验收批量模板平台\n\n新的通用入口是 `scripts/ci_template_projects.py`，配合 `examples/acceptance` 中个人阅读书架、库存采购协作与设施维护运营三套需求。它们用同一 python-basic/simple-admin/SQLite 模板，分别覆盖 1、3、6 个实体以及递增的权限和流程复杂度。三条真实需求通过 create_batch 一次入队，由正常 LangChain 与 LangGraph 路径处理；任何一个失败都不能汇总为成功。\n\n每案 requirement.md 提供给模型；contract.json 是独立验收义务与合成测试数据，不是失败时的固定 Plan 回退。预算最多12次模型请求/案、总计36次；格式修复计入预算。普通独立验证之后还要检查最终ZIP、新目录新数据库、场景API与浏览器、重启持久化。这里的规模是模板内业务复杂度，不等于吞吐和线上生产验收。\n\n工作流使用 rnd 环境的 secrets.API_KEY、vars.BASE_URL 和 vars.MODE，在同仓库PR显式添加 run-live-acceptance 标签时执行，或进入默认分支后手动运行。它按被审阅的当前head校验身份，并遵循已有环境保护；普通代码同步不自动消耗模型预算。旧 real-model 工作流保留历史固定供应商约束。详见 `docs/template-platform.md`；看本次报告中的提交与每案状态，不把本地单元测试记成真实模型通过。\n"
  }
]
````
