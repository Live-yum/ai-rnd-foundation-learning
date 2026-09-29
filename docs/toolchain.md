## 20. 结构化代码工具：从文件索引接到真实研发流程

本章在第0—19章已经能启动、生成、验收和独立交付的基础上增加工具，不把原流程改造成自由执行shell的Agent。第一次从空目录学习时，先按附录创建本章所列文件，再回第10章执行索引测试；第13章组装流程时使用附录中的新版flow.py。不要混搭上一版本的锁文件、配置或手册。

### 20.1 先弄清每个工具的职责和边界

Tree-sitter是读取代码结构的解析器，不是编译器。Java类、方法、继承签名、注解、TS函数/变量/接口和Vue组件/脚本行号写入index.json；Python继续使用标准库AST。Vue先用HTML语法解析外壳，再按script的lang选择TS/JS语法，保留原文件行号。这个索引不是跨语言类型系统、完整调用图或vue-tsc的替代品，语法错误和不支持的script语言会被记录，而不是假称成功。

Aider有两个可选接入点：真实RepoMap算法生成紧凑骨架；真实离线`--apply`应用SEARCH/REPLACE。平台仍由现有ModelGateway调用你配置的CODING模型，因此模型预算、重试、密钥隔离和回执没有绕开。Aider子进程不接收模型API_KEY、不进行第二次推理，也不生成CRUD。它的工作副本不是任意代码执行沙箱；平台只接受已经通过Rules解析器的受限验证函数。

Continue使用当前支持的MCP扩展机制连接平台的只读索引。这里没有把Continue已弃用的`@Codebase`内部代码伪装成稳定的独立Python索引引擎。检索器是本仓库实现的AST/关键词/TF-IDF稀疏向量混合排序；TF-IDF是词法向量，不是神经语义embedding。默认不会下载嵌入模型或上传源码到另一家embedding供应商。需要神经语义检索或直接内嵌Continue内部索引时，必须另外确定模型、版本、服务地址、授权及维护边界。

Daytona通过可选的真实Python SDK接入，默认关闭。当前登记的远程验收配置是FastAPI Basic + SQLite的离线依赖安装、真实HTTP和进程重启持久化测试。FastapiAdmin及Yudao/Vben仍保留原来的本机/Docker完整原生生成、构建、浏览器与新数据库验收，不会偷偷降级为远程只跑一个echo。尚未提供云端/自建地址、快照和授权时，不能声称Daytona真机验收通过。

### 20.2 在空目录中创建哪些文件，为什么创建

所有下表文件的**完整内容**都在本手册后面的同名源码块中，包括新的依赖锁、脚本、测试和Actions。创建文件时先按路径创建父文件夹，再完整复制对应块，不复制表格说明当作代码。

| 文件 | 为什么需要、连接到哪里 |
|---|---|
| `workbench/code_index.py` | Tree-sitter语法加载、Java/TS/JS/Vue提取；knowledge调用它，不发模型请求 |
| `workbench/knowledge.py` | 索引schema升级到2；文件SHA与解析器版本联合控制缓存，vendor/init继续调用同一个入口 |
| `workbench/retrieval.py` | 按当前源码哈希检索；plan节点把有文件名/行号/哈希的上下文真正交给规划模型 |
| `tools/aider/pyproject.toml`、`tools/aider/uv.lock`、`tools/aider/worker.py` | 独立Python3.12的固定Aider环境和离线工作进程，不污染平台Python3.14 |
| `workbench/aider_tools.py`、`workbench/coding.py` | 当前文件SHA→精确唯一匹配→受限AST→Aider独立副本→结果对比→Git回滚包→原子落盘 |
| `workbench/continue_mcp.py` | stdio MCP服务；只有search_code/read_source，无shell、写文件或数据库工具 |
| `workbench/daytona_tools.py` | 授权、独立凭据、私有沙箱、禁止出网、固定验收命令、报告大小限制、等待删除确认 |
| `workbench/toolchain_cli.py`、`workbench/cli.py` | 为初学者提供tools status/install-aider/search/repo-map/continue-config入口 |
| `workbench/settings.py`、`.env.example` | 可选工具开关；缺省仍只需要原来的BASE_URL/API_KEY/MODE |
| `workbench/flow.py` | plan读取模板索引，code选择受限编辑器，verify在原验收通过后追加已授权Daytona检查 |
| `tests/test_toolchain_*.py` | 结构、行号、过期、越界、事务、回滚、授权、清理及流程接线的回归测试 |
| `scripts/ci_toolchain.py` | 安装并执行真实Aider/Tree-sitter/MCP，故意制造一次业务错误再真实修复并独立解压验收 |
| `scripts/ci_daytona_live.py` | 仅供明确人工授权的真实Daytona联调；只生成合成测试数据，不使用生产数据 |
| `.github/workflows/toolchain.yml` | Linux/Windows真实工具测试；单独的人工授权Daytona任务，不把它的未执行算成通过 |
| `scripts/build_handbook.py` | 将本章及以上全部源码/工具锁/正式workflow加入完整手册并校验 |

不用修改控制库表结构，因此本章没有空迁移文件。已有数据库先备份、按第14章升级；已有索引的schema或解析器版本不同会重建，不能靠删除业务数据库解决索引问题。

### 20.3 先通过默认多语言索引关卡

在含pyproject.toml的仓库根目录执行：

```powershell
uv sync --locked
uv run rnd tools status
uv run rnd index templates/product .data/example-index
uv run rnd tools search templates/product .data/example-index validate
uv run rnd tools repo-map templates/product .data/example-index
uv run pytest tests/test_toolchain_index.py tests/test_toolchain_flow.py -q
```

正常结果：status列出固定Tree-sitter语法版本，aider_installed可能为false；不影响默认使用。index返回source_digest、parsed_python、parsed_tree_sitter、parse_errors及reused。上面示例是Python模板，因此parsed_tree_sitter为0正常，不是Java能力验证；单元测试会真正解析Java、TS及Vue样例。再次index应复用未变化文件。search结果带path、line、end_line、sha256和content；修改源码后直接search应报过期，需要重建，不能继续拿旧片段编辑。

运行`uv run rnd init`时，三份固定原生源码从仓库ZIP展开并自动解析。下面是本提交固定Vben Ant Design工作区的完整路径示例，不需要额外git clone上游：

```powershell
uv run rnd index .data/bundled/yudao-frontend/1b14e889f529e245fd620daa720dcea6de0cc5e7 .data/vben-index
uv run rnd tools search .data/bundled/yudao-frontend/1b14e889f529e245fd620daa720dcea6de0cc5e7 .data/vben-index useVbenForm
```

设置过DATA_DIR时，把示例的.data换成你设置的位置。旧索引版本、被修改的模板、符号链接、超限查询都明确失败。语法错误文件保留诊断，但不作为可信符号结果送给模型。不要因为一个未支持语法文件有诊断，就删掉用户需求或者取消后续编译测试。

规划开始时会写入`.data/runs/运行ID/design/template-context.json`。它记录实际模板来源摘要、检索片段和地图。源码和注释标为不可信参考数据，不能把其中的文字当系统指令，更不能据此扩大已选模板的功能范围。

### 20.4 再安装Aider，平台不能降级Python

固定的aider-chat 0.86.2要求Python小于3.13，因此本仓库使用独立的3.12工具环境。平台、控制库、API、LangGraph和默认交付产品仍是3.14。不要把aider-chat直接加入平台主dependencies或强行忽略Requires-Python。

```powershell
uv run rnd tools install-aider
uv run rnd tools status
uv run rnd tools repo-map templates/product .data/example-index --engine aider
```

安装会下载Python3.12及`tools/aider/uv.lock`锁定的依赖；这是明确执行安装命令后的软件包下载，不是上传项目给模型。成功后aider_installed为true。地图engine应为`aider-0.86.2-repomap`，而不是用本地符号拼接器冒名。预算使用保守UTF-8字节计数，不假装精确等于某个供应商的token数；超预算裁剪有truncated标识。

需要在后续真实流程中启用时，在自己的.env中设置：

```dotenv
CODING_ENGINE=aider
REPO_MAP_ENGINE=aider
```

重新启动平台后创建带有受支持逐记录业务规则的任务，例如“priority不能为负”。CRUD仍走确定性生成器；只有额外规则会调用编码模型。模型返回的Edits必须携带当前SHA，SEARCH必须精确唯一匹配完整行，不能夹带新的控制块。任何规则AST错误、工具失败、额外文件、模糊匹配结果或过期SHA都不能修改原项目。

每次成功编辑在运行目录写`aider-0.json`和`aider-0.bundle`，修复轮次依次递增。JSON有前后SHA、真实Git提交、diff、bundle哈希和Aider模型调用数0。Git仓库是工具的独立事务仓库，不会提交或覆盖你的主仓库。要检查或取回旧规则，在**新的空目录**克隆该bundle，然后用回执的before_commit查看旧文件；不要对主仓库执行reset --hard。

```powershell
git clone .data/runs/运行ID/aider-0.bundle .data/inspect-aider-edit
cd .data/inspect-aider-edit
git log --oneline
git show 回执中的before_commit:custom_rules.py
```

“运行ID”和“回执中的before_commit”来自那次运行的真实JSON，不能照抄成一个假ID。回滚前保留现有产物和回执；改回文件后必须重新索引、重新验证和重新打包，旧READY证据不会自动适用于新文件。

### 20.5 Continue连接的是只读工具，不是秘密配置复制器

```powershell
uv sync --locked --extra continue
uv run rnd tools continue-config templates/product .data/example-index
```

命令只打印一个包含mcpServers的配置片段，不覆盖你的Continue配置，不复制BASE_URL/API_KEY，不替你选择Continue的模型。将打印的name、command、args、cwd条目加入你自己Continue配置的mcpServers列表，保留原有模型条目。JSON对象也是合法YAML结构，合并时不要创建两个重复的mcpServers键。`command`是当前平台虚拟环境的解释器绝对路径；移动项目后重新生成配置。

Continue连接成功后可调用search_code找例子，再带搜索结果的sha256调用read_source。读取最多80行/20000字符；不能读取.env、工具私密目录、索引外路径或过期版本。这里的测试验证真实MCP客户端/服务端握手和工具调用；它不是已安装Continue桌面插件的UI自动化测试，也不是“已验证全部Continue内部索引功能”。

### 20.6 Daytona先授权，再创建任何远程资源

默认配置是：

```dotenv
SANDBOX_BACKEND=local
DAYTONA_UPLOAD_AUTHORIZED=false
```

这表示继续原来的本机验收。本机受限子进程不是安全沙箱，不能拿来执行任意不可信仓库。Daytona云端可能计费，也可以由你选择自己管理的服务；本仓库不预设一家云端地址、不读取其他工具的Key、不默认授权上传，也不操作生产数据库。

管理员选定服务、取得独立Key，并准备一个无秘密、无生产数据的私有快照后，先安装可选SDK：

```powershell
uv sync --locked --extra daytona
```

快照必须包含Python3.14、uv，以及与`templates/product/uv.lock`一致的离线依赖缓存；运行用户应具有自己的/tmp和uv缓存写权限。在你准备快照的临时环境中，复制本仓库的`templates/product/pyproject.toml`及`templates/product/uv.lock`到一个空文件夹并运行下面命令预热，完成后保留uv缓存，不往镜像加入.env或API_KEY：

```sh
uv sync --locked --no-dev --python 3.14 --project /opt/rnd-product-dependencies
uv sync --locked --offline --no-dev --python 3.14 --project /opt/rnd-product-dependencies
```

`/opt/rnd-product-dependencies`是放置上述两个文件的快照内目录。快照如何创建/上传取决于你实际选择的云端或自建Daytona部署，先按该部署的管理方式完成并记录快照名；平台不会擅自替你开通账号、选择地域或购买容量。快照中的运行用户、缓存位置必须一致，否则复制一份别人的.venv并不能使离线安装成功。应使用没有启动钩子、没有外部账号凭据的干净快照；外层资源隔离由你授权的Daytona部署提供。

随后才在自己的.env填写：

```dotenv
SANDBOX_BACKEND=daytona
DAYTONA_API_URL=你明确选择的HTTPS服务API根地址
DAYTONA_API_KEY=该服务独立Key
DAYTONA_SNAPSHOT=你已预热的快照名
DAYTONA_UPLOAD_AUTHORIZED=true
```

这些中文提示必须替换成自己的实际值，DAYTONA_API_KEY不能用默认模型Key充数。DAYTONA_TARGET可按所选服务另外配置。任一条件未满足，设计/验收应停下并说明原因；智能推荐也不能替你授权或绕过生产数据库保护。

验收流程是：原有本机测试通过→检查明确授权和受支持模板→创建私有、禁止出网的临时沙箱→仅上传非敏感产品源码→从平台单独上传可信HTTP验证器→固定离线安装命令→真正启动产品、访问API、重启检查数据→流式读取不超过64KB的报告→等待沙箱删除确认。正常、命令失败和异常路径都尝试清理。未确认删除时禁止READY；创建超时拿不到ID时按回执rnd-operation标签检查可能的资源，15分钟TTL只是兜底，不能代替删除证据。

远程回执在`daytona-轮次.json`，不含Key。重新打包依然保留原来的干净解压复测；开启Daytona不是减少本机或原生验收项的开关。

### 20.7 按测试关卡进入下一步

先验证源码契约，再安装真实可选工具并执行集成：

```powershell
uv sync --locked --all-extras
uv run pytest tests/test_toolchain_index.py tests/test_toolchain_edit.py tests/test_toolchain_daytona.py tests/test_toolchain_flow.py -q
uv run rnd tools install-aider
uv run python -m scripts.ci_toolchain
uv run ruff check .
uv run ruff format --check .
uv run python -m scripts.build_handbook --check
uv run pytest -m "not postgres" -q
```

ci_toolchain故意让明确的模型协议夹具第一次返回语义错误的规则。真实Aider完成第一次编辑，真正的规则验收失败，LangGraph进入repair，真实Aider修复，再执行HTTP、数据库、重启、ZIP解压独立验收。不能把“工具函数被mock调用了”作为这一关通过证据。Linux还对仓库自带三套源码实际建索引，并对整个芋道后端运行真实Aider地图、查询Vben Hook；Windows运行同一实际Aider流程和MCP握手，额外的大型原生地图只在Linux执行。

报告保存在reports/toolchain：aider-workflow、aider-yudao-map、bundled-ast、vben-retrieval、continue-mcp及daytona-coverage。最后一个必须明确cloud_executed=false，因为自动PR没有获得你的远程资源授权；真实SDK类型检查和模拟的失败清理测试不等于云端真机验证。

需要云端真机联调时，由仓库管理员在GitHub创建受保护的`daytona-sandbox`环境，设置环境变量DAYTONA_API_URL、DAYTONA_SNAPSHOT、可选DAYTONA_TARGET和环境秘密DAYTONA_API_KEY。只有你手动运行Structured code toolchain acceptance并勾选明确上传授权时，authorized-daytona任务才运行；自动PR不能触发这个任务。它只使用新生成的合成数据，通过后还要检查报告的executed、passed及cleanup_confirmed。没有运行记录就不能把这一项写成“已通过”。

### 20.8 同步整本手册、升级和排错

从附录还原全部文件后，安装同提交锁定依赖再运行：

```powershell
uv run python -m scripts.build_handbook
uv run python -m scripts.build_handbook --check
uv run pytest tests/test_handbook.py tests/test_handbook_order.py -q
```

build_handbook同时更新完整版及旧v3文件名，追加所有新模块、测试、脚本、Aider工作进程与工具专用锁文件，不省略代码。它不会把tools/aider/.venv、缓存或用户密钥写进手册。测试从空目录还原源码并再次生成相同手册；vendor的二进制归档仍由第0—19章说明的固定清单重建，不把压缩包误当作文本源码。

| 故障 | 处理与禁止事项 |
|---|---|
| Aider要求Python<3.13 | 使用install-aider建立独立3.12环境，不降级主平台、不改锁文件伪造兼容 |
| 某语法解析失败 | 查看index条目的parse_error和原文件，保留后续编译/类型检查，不删除用户需求 |
| 文件已变化/哈希过期 | 保留现场后重建索引、重读当前原文；不要把expected_sha256改成任意值硬通过 |
| SEARCH不唯一或Aider结果不同 | 缩小为唯一完整行块，重新走编码/验证；不启用模糊匹配和自由shell |
| Aider工具未装 | 先运行显式安装命令；不自动联网安装、不偷偷改回另一个引擎 |
| Continue找不到MCP | 用安装了continue extra的环境重新打印配置，检查绝对路径与cwd，不复制Key到工具参数 |
| Daytona依赖离线安装失败 | 修复你授权快照的Python/uv缓存；不自动放开出网、不把主机.venv与凭据上传 |
| Daytona清理未确认 | 根据回执ID/操作标签在所选部署确认和清理；不能删回执或改passed绕过 |
| 手册不一致 | 改正文源或源码后重新生成两个完整手册，不跳过Actions一致性检查 |

### 本章的官方接口依据

Tree-sitter Python API：https://tree-sitter.github.io/py-tree-sitter/
Aider RepoMap：https://aider.chat/docs/repomap.html
Aider固定包及Python约束：https://pypi.org/project/aider-chat/0.86.2/
Aider离线apply CLI：https://aider.chat/docs/config/options.html
Continue MCP配置与弃用项：https://docs.continue.dev/reference
MCP Python SDK：https://github.com/modelcontextprotocol/python-sdk
Daytona配置/创建/删除：https://www.daytona.io/docs/en/python-sdk/sync/daytona/
Daytona固定命令与文件API：https://www.daytona.io/docs/en/python-sdk/sync/process/ 、https://www.daytona.io/docs/en/python-sdk/sync/file-system/
这些链接帮助理解接口；真正可复现的组合以本提交两个uv.lock、worker适配代码和Actions结果为准。
