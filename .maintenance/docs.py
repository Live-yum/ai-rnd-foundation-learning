"""One-time materialization, verified against exact reviewed source; removed before delivery."""
import hashlib
from pathlib import Path

CHANGES = [('README.md',
  '2cf45dd2a56b572c10feead14bdbefa26313798baf643cb7c367bea1d89bfc65',
  [(4, 5, '平台使用 Python、uv、FastAPI、SQLite 和 LangGraph。**仅聊天大模型允许使用外部推理服务；其余工具均为本机运行。** 基础代码、迁移、索引、测试与打包由工具执行。测试失败不能由模型“宣布通过”。\n'),
   (6, 7, '## 1. 初始化完整演示源码\n'),
   (8, 9, '从当前所查看源码分支的Code菜单取得完整源码并解压，进入含pyproject.toml的根目录执行：\n'),
   (11, 14, ''),
   (18, 18, '\n**从零学习不需要先取得这些源码。** 唯一教材`从零实现AI研发平台_逐步实操手册_完整版.md`从空文件夹讲解每个自有文件、调用关系和逻辑，包含所有文本源码及锁文件；书中给出的脚本可从固定第三方提交生成原生模板ZIP。没有本项目骨架也能照书实现。\n'),
   (153, 166, ''),
   (177, 178, '详细从零实现手册：**`从零实现AI研发平台_逐步实操手册_完整版.md`**。从空目录创建文件、数据流讲解、完整代码、数据库迁移、前端、测试、CI与锁文件均包含在同一份教材。第三方模板不是自行编写的代码：教材提供固定提交和打包脚本，读者可以从公开上游重建三个归档，不需要先取得本仓库骨架。演示仓库附带这些归档以便直接体验；源码附录逐文件讲解职责与对应关系。\n'),
   (181, 182, '## 10. 本机工具链与唯一完整教材\n'),
   (183, 184, '默认使用本机Tree-sitter/Python AST、FTS5和符号Repo Map。Aider使用独立Python3.12环境：\n'),
   (185, 186, '```powershell\nuv sync --locked --project tools/aider --python 3.12\nuv run rnd index workbench .data/platform-index\nuv run rnd tools search workbench .data/platform-index "model_for"\nuv run rnd tools continue-config . workbench .data/platform-index\n```\n\n设置`CODING_ENGINE=aider`和`REPO_MAP_PROVIDER=aider`可启用实际本机编辑/Repo Map。真实模型Key只交给平台网关，Aider不取得它。Continue仅通过本机stdio MCP访问只读search_code/repository_map；上游已停止积极维护，本平台不依赖其云服务。\n\n向量服务仅接受回环地址，使用本机模型并显式`EMBEDDING_ENABLED=true`。工具端点拒绝云端/局域网、代理与重定向，数据库和Docker执行也限定本机；继承的LangSmith/OTEL遥测关闭。公开依赖下载不等于云端执行工具。\n\nDaytona固定为**v0.190.0自托管开发部署**，没有云端模式。Linux/WSL准备Docker后：\n'),
   (188, 191, 'uv sync --locked --all-extras\nuv run python -m scripts.daytona_local prepare\nuv run python -m scripts.daytona_local images\nuv run python -m scripts.daytona_local up\nuv run python -m scripts.daytona_bootstrap auth\nuv run python -m scripts.daytona_local snapshot-image\nuv run python -m scripts.daytona_bootstrap snapshot\nuv run python -m scripts.ci_daytona_local\n'),
   (193, 194, '本机随机凭据及平台配置保存在`.data/daytona-local`，不得提交Git。完整教材第20章解释Dex、API、Runner、镜像摘要、离线快照、每一步预期结果和清理。默认Python/SQLite快照不冒充Java/Vue通用镜像；原生完整验收仍在本机进行。Daytona上游Compose仅供开发，privileged Runner不是生产强隔离保证。\n'),
   (195, 196, '仓库只保留`从零实现AI研发平台_逐步实操手册_完整版.md`这一份完整教材，不提供版本差异补丁式教程。源码块带SHA，逐文件讲解与源码同步，标准库重建脚本可只从文档建立全部自有文件：\n'),
   (197, 199, '```powershell\nuv run python -m scripts.build_handbook\nuv run python -m scripts.build_handbook --check\nuv run python -m scripts.ci_handbook\n'),
   (201, 208, '真实模型联调需要你自己的大模型配置。CI使用显式模型协议夹具；真实CLI、数据库、浏览器、本机服务测试的证据分别保存，不把SDK模拟响应当成本机完整部署成功。\n')]),
 ('docs/guide.md',
  '584c016903081eb11cee1736f74b7f5e83679e151e2ecfe738abb6d0b4cbcf9d',
  [(4, 5, '这是一份完整的实现与操作手册：前半部分按学习顺序说明创建什么、连接到哪里、如何运行与测试；后半部分直接包含同一提交中的全部文本源码、配置、数据库迁移、前端、测试和依赖锁。全文描述一个一致的最终系统，不需要任何较早版本、骨架项目或差异补丁。\n'),
   (6, 7, '本手册只有一个正式文件：`从零实现AI研发平台_逐步实操手册_完整版.md`。你可以只拿到这一份文档，从空文件夹逐个创建本项目的全部源文件。语言解释器、Python包和第三方开源框架属于明确安装的依赖，不要求预先拥有本项目仓库。\n\n**阅读顺序**：先完成第2章的工具准备，按照第6—13章和“逐文件实现讲解”创建文件，再回到第3—5章体验平台。完整源码区的每个标题就是要创建的文件路径，代码块不省略实现。希望先体验的读者可以在已经取得的演示源码目录直接执行第3—5章，但这不是手写学习的前置条件。\n\n**运行边界**：仅需求理解、规划、规则编码和语义审阅的大模型接口允许使用外部推理服务。索引、检索、向量模型、MCP、Aider、数据库、Daytona控制面及执行器全部在本机。下载依赖、浏览器或固定第三方源码属于安装阶段，不把业务任务交给云端工具执行。\n'),
   (43, 44, '### 2.2 创建一个真正的空文件夹\n\nWindows打开PowerShell；先在文件资源管理器中打开“查看 → 显示 → 文件扩展名”，避免把`app.py`保存为`app.py.txt`。选择你有写权限的位置，例如：\n'),
   (46, 49, 'New-Item -ItemType Directory -Path "$HOME\\rnd-learning"\nSet-Location "$HOME\\rnd-learning"\n'),
   (50, 52, 'code .\n'),
   (54, 55, 'Linux/WSL使用：\n'),
   (56, 57, '```bash\nmkdir -p ~/rnd-learning\ncd ~/rnd-learning\nuv python install 3.14\ncode .\n```\n'),
   (58, 59, '这时目录中不需要任何代码，也不用运行`git clone`或下载本项目骨架。VS Code是编辑器，PowerShell/Bash是执行命令的终端，Python是执行`.py`文件的解释器，uv负责创建`.venv`并安装精确依赖；它们不是同一个东西。\n'),
   (60, 61, '在VS Code左侧按“新建文件”，输入完整相对路径。斜线前是文件夹，例如`workbench/settings.py`表示在workbench文件夹创建settings.py。复制完整源码区同名文件的整个代码块，不复制外层反引号、行号或标题。保存时选择UTF-8。`#`是Python注释；英文标点和缩进必须保留。\n\n先写第6章列出的项目配置文件，之后才能执行`uv sync --locked`。不要先执行后面的API或模型命令，因为相关模块还没有写出来。\n\n### 2.3 第三方源码不是隐含的骨架\n\n本平台的Python/Java原生框架是第三方依赖。书中给出了`scripts/vendor_templates.py`的全部代码及三个固定源码提交。手写完成这个脚本和模板清单以后执行：\n'),
   (63, 64, 'uv run python -m scripts.vendor_templates --fetch\n'),
   (66, 67, '脚本只从登记的三个公开上游拉取指定SHA，验证许可证，排除Git历史、依赖缓存、密钥、数据库和字体二进制，重建`templates/vendor/*.zip`。它不下载本项目的Python实现，不要求复制已有仓库中的任何骨架文件。先写代码再执行脚本，下载的第三方框架与语言包一样是显式依赖。\n'),
   (68, 69, '最终演示仓库已带这三个普通Git ZIP；直接使用演示仓库的人不需要重复下载。无论采取哪种路径，`rnd init`都校验模板清单并在本机解压到`.data/sources`，不会覆盖`.env`或清空数据库。\n'),
   (70, 82, '安装依赖、模型权重、浏览器、Maven/pnpm包及Daytona镜像需要网络。准备完成以后索引和工具执行不调用云端服务；这不等于无需安装任何软件的完全离线发行版。\n'),
   (235, 236, '这是本书的主学习路径。沿用第2章创建的空文件夹，不再创建第二套项目，也不执行会生成隐含骨架的初始化命令：\n'),
   (238, 240, '# 在已经创建的空文件夹打开终端，确认位置\nGet-Location\n'),
   (241, 243, ''),
   (245, 246, '在VS Code中先创建 `.python-version`、`pyproject.toml`、`uv.lock`、`.gitignore`、`.gitattributes`、`.env.example`、`README.md`、`workbench/__init__.py`、`workbench/local_only.py`，逐字使用附录里的相应文件。确保 `.py` 不是 `.py.txt`，编码UTF-8。把本书给出的pyproject和uv.lock完整保存，再运行 `uv sync --locked`。\n'),
   (249, 250, '二进制模板ZIP不需要手工输入或从本项目复制。第2.3节的脚本会从固定第三方源码生成它们。你手写的平台实现全部在本书中，包括脚本本身、模板的自有适配代码、前端、测试、配置和锁文件。“逐文件实现讲解”还给出完整的创建组、输入输出、调用关系与验证方式。\n'),
   (253, 254, '创建 `workbench/local_only.py`、`workbench/settings.py`、`catalog.py`、`domain.py`、`errors.py`、`store.py`、`alembic.ini` 和 `migrations/`中的完整文件。local_only定义仅本机工具策略并关闭遥测；settings依赖Pydantic Settings和local_only，domain和catalog不依赖HTTP；store读取配置并提供短事务，禁止反向import api。\n'),
   (266, 267, '在空数据库按已有的完整迁移文件创建全部控制表：\n'),
   (274, 275, '首次使用本书完整给出的revision，不需要自己猜测0001。以后主动改变模型时才用 `revision --autogenerate -m "具体变更"`，人工阅读增加/删除项再upgrade。自动生成是候选，不自动理解数据重命名与搬迁。测试里可对临时库create_all，生产和真实学习数据用迁移。\n'),
   (282, 283, '通关：提交/回滚、真实外键、幂等、时间/路径、迁移顺序、输入不伪造身份都通过。`test_learning_order.py`还验证这一数据库学习阶段不依赖未来的API或Agent模块。\n'),
   (316, 317, '在workbench目录创建filesystem.py、vendor.py、tools.py、symbols.py、knowledge.py、retrieval.py、context_mcp.py、toolchain.py、rules.py、coding.py、aider_tool.py、local_only.py、daytona_worker.py和sandbox.py，全部内容见源码附录。第20章逐项说明解析、检索、Continue、Aider和Daytona的安装、接线与测试。\n'),
   (320, 321, 'vendor读取manifest，核对ZIP整体SHA和解压后的文件指纹与LICENSE。重复init复用有效缓存，篡改立即拒绝。三份模板由固定源码生成后保存在本机，源码未变化就复用已解析条目。knowledge记录文件SHA、符号起止行与增量状态；Python使用标准库AST，Java/TypeScript/JavaScript以及Vue内嵌script通过symbols中的Tree-sitter解析。Java类、方法、字段、注解和继承，TS声明，以及Vue组件标签与真实源码行号进入符号索引；这不是完整的跨模块类型推导或调用图，编译和类型检查仍然必需。retrieval提供SQLite FTS5与可选本机向量检索，context_mcp向Continue开放只读查询，toolchain把同一上下文接入规划。输出目录必须位于被索引源码之外。\n'),
   (354, 355, '创建verification.py并阅读templates/product/verify.py、workbench/postgres_lab.py。产品以独立进程真实启动，不从Agent的“我测过了”获取结论。测试账号、登录、越权、字段、CRUD、搜索筛选、进程重启全部通过才继续。\n'),
   (372, 373, '实际流程节点：analyse → requirements gate → source_context（索引、检索与Repo Map）→ plan → design gate → generate → code（需要时）→ verify；可修复失败经repair回到code，再次verify；验证通过后进入sandbox（已显式启用时执行本机自托管Daytona，否则记录未启用）→ model_review（可选）→ package（含独立解压复验）→ delivery gate。source_context不调用聊天模型，也不默认计算向量；code按CODING_ENGINE使用原有受限引擎或真实Aider；sandbox失败不能跳到交付。状态主要保存runID、版本、结构化规格、有界上下文与回执，不保存ZIP字节或整个仓库。\n'),
   (395, 396, '## 14. 运行状态、预算与恢复\n'),
   (399, 400, '每一条回答都保存在messages表。关闭浏览器不会丢失运行；用同一UUID重新进入即可读取当前等待点。达到显式预算后可调整预算并重启，再重试原UUID；不是再建同名项目、重复输入需求或删除数据库。流程断点、原始消息和工具回执共同解释“已经做到了哪一步”。\n'),
   (413, 414, 'templates/vendor/                 固定第三方源码ZIP与许可证\n'),
   (418, 419, '平台可使用PostgreSQL：`uv sync --locked --all-extras`后设置DATABASE_URL。CHECKPOINT_URL可分离图断点库。新空库有迁移和真实CI验证；SQLite数据并不会因改URL自动搬过去，需要另行数据迁移与恢复验证，不能承诺零操作切库。\n'),
   (445, 446, '生成器把全部正文、逐文件讲解与真实源码完整组合成唯一正式手册。每个源码块带SHA；test_handbook验证逐块一致性与空目录还原后再次生成相同手册。二进制vendorZIP在Git中单独保存，书中包含重建这些ZIP的完整脚本、manifest与许可证，不把二进制伪装成代码块，也不要求已有ZIP作为学习前提。\n'),
   (453, 455, '| ModuleNotFoundError | 回到含pyproject的根目录，uv sync --locked；使用包路径workbench，不要写不存在的from main |\n| 超轮数/调用上限 | 检查.env是否设置了正数；默认0；改好重启并retry同一UUID |\n'),
   (461, 462, '| 浏览器工作台显示KeyError | 错误包含源码位置；日期/枚举图表有回归测试，检查你是否使用同提交完整源码 |\n')]),
 ('docs/native-baseline.md',
  '44d71c956ed590d5e0509f9c0f233434c1c637343d1f2145dab4925f91f9f0c1',
  [(4, 5, '固定模板源码由书中的vendor脚本取得，演示仓库也已自带；原生产品的交付包含新数据库初始化、业务DDL和菜单SQL，不要求依附当初生成它的平台数据库。原生语言运行时仍必须存在，不可能通过三个模型参数替代Java、Node、PostgreSQL和Redis。\n'),
   (11, 12, '| 原生接口导出 | 为已部署生成器提供专用配置/令牌 | 只导出源码时仍是SOURCE_READY，不能冒充全栈已测 |\n'),
   (27, 28, '| `native_lab.py`、`scripts/ci_native_bundled.py` | 平台和CI共用执行链；从随库模板开始，不依赖本项目骨架 |\n'),
   (47, 48, '原生全栈在Linux验收。Windows使用WSL2 Ubuntu，在Linux目录按本书创建文件并建立Linux `.venv`，不要复用Windows虚拟环境。默认Python产品仍在Windows/Linux分别测试。完整Vben较大，建议至少16GB主机内存和足够磁盘；平台错开Java和Vite构建，必要时明确配置交换空间，不删除业务页面来减负。\n'),
   (81, 82, '回到按照本书创建的项目根目录（例如`~/rnd-learning`）：\n'),
   (84, 88, 'cd ~/rnd-learning\n'),
   (90, 90, '# 从空目录手写时执行；已有合法vendor ZIP的演示仓库可直接init\nuv run python -m scripts.vendor_templates --fetch\n'),
   (93, 94, '全部平台源码来自本书完整代码区；vendor脚本只取得固定第三方依赖，不下载本项目的现成骨架。不要复用Windows虚拟环境，也不要用清空数据库解决安装问题。\n'),
   (259, 260, '本手册第二部分使用的所有实现代码都在后面的整份源码附录；源码改变后用同一build_handbook命令重新生成，不把“待实现”函数藏在附录里。独立交付首次环境仍需互联网安装依赖，但不再需要重新拉取模板或原始开发数据。测试结果以所用提交对应的Actions及portable-start报告为准。\n')])]

for name, expected, edits in CHANGES:
    path = Path(name)
    old = path.read_text(encoding="utf-8")
    if hashlib.sha256(old.encode()).hexdigest() != expected:
        raise ValueError("Reviewed preimage mismatch: " + name)
    lines = old.splitlines(keepends=True)
    for start, end, replacement in reversed(edits):
        lines[start:end] = [replacement]
    path.write_text("".join(lines), encoding="utf-8", newline="\n")
Path(__file__).unlink()
