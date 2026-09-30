## 20. 本机工具链：解析、检索、编辑、MCP与自托管Daytona

所有操作从你按本书写出的项目根目录执行。除了四类聊天大模型推理端点，其他工具没有云端运行模式：工具URL只接受127.0.0.1、localhost或::1，localhost会规范化为数值回环；不接受公网、局域网、代理转发或驱动查询参数覆盖。数据库、本地容器、源码、索引、沙箱与回执均保留在本机。

安装软件仍要下载公开包、源码、镜像和模型权重。这与把用户源码上传到托管工具执行是两件事。本章不要求Daytona云账号、云端向量库、Auth0租户、托管MCP或在线代码编辑服务。

### 20.1 先确认基础工具

```powershell
uv sync --locked --all-extras
uv run rnd doctor
uv run rnd models
uv run rnd init
```

没有自己的真实模型配置时doctor可以指出缺项，但索引和工具契约测试不需要模型Key。`--all-extras`安装本机PostgreSQL驱动和固定Daytona SDK，不创建任何服务。真正创建本机Daytona资源还需要后面的显式准备与启用。

### 20.2 Tree-sitter与本地代码检索

```powershell
uv run rnd index workbench .data/platform-index
uv run rnd tools search workbench .data/platform-index "model_for"
uv run rnd tools repo-map workbench .data/platform-index
```

首次建立索引；第二次复用指纹未变的解析条目；源文件修改后要重建索引，否则检索拒绝过期行号。索引目录必须位于源目录之外。默认Repo Map来源是本机符号索引，不调用大模型。

Java类、方法、注解和继承通过Java grammar解析；TypeScript/JavaScript声明通过相应grammar；Vue脚本的行号会转换回原始SFC行号，并记录template中的组件标签。每个检索结果包含真实路径、起止行和片段。它不提供编译器级完整类型证明，因此最终仍要编译与运行。

原生源码在`rnd init`后由模板准备函数返回实际路径。运行详情的context-receipt.json记录slot和来源；使用回执中的目录建立自己的索引，不猜测另一个框架目录。CLI支持`--file-suffix .vue --path-prefix apps/web-antd/`，先限制候选再排名。

### 20.3 可选本机向量模型

不需要向量时保持`EMBEDDING_ENABLED=false`即可，FTS5与符号图已经可用。需要语义检索时，先安装并启动本机兼容`POST /v1/embeddings`的模型服务，例如本机Ollama，再下载它支持的embedding模型。模型权重下载属于准备阶段，推理不能转发到云端。

Windows先从官方`https://ollama.com/download/windows`安装Ollama，退出任务栏中的Ollama，再在PowerShell设置仅本机运行：

```powershell
[Environment]::SetEnvironmentVariable('OLLAMA_NO_CLOUD', '1', 'User')
[Environment]::SetEnvironmentVariable('OLLAMA_HOST', '127.0.0.1:11434', 'User')
```

从开始菜单重新打开Ollama并重新开终端。Linux/WSL的Ubuntu执行以下安装与配置命令：

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl edit ollama.service
```

编辑器中在有效配置区写入下面完整的覆盖配置；已有覆盖项则合并，不能删掉其他用途的配置。使用nano时按Ctrl+O、回车保存，再按Ctrl+X退出：

```ini
[Service]
Environment="OLLAMA_NO_CLOUD=1"
Environment="OLLAMA_HOST=127.0.0.1:11434"
```

然后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
sudo systemctl status ollama --no-pager
```

没有systemd的手动开发环境，先停止占用11434端口的另一个Ollama，再在单独终端执行`OLLAMA_NO_CLOUD=1 OLLAMA_HOST=127.0.0.1:11434 ollama serve`。本机服务日志应显示`Ollama cloud disabled: true`；不登录云账号、不启用cloud模型或网络搜索。这些设置是Ollama进程自己的环境，不是只填在平台.env里就会生效。

服务启动后，Windows/Linux都在另一终端下载本机nomic-embed-text模型并记录版本：

```text
ollama --version
ollama pull nomic-embed-text
ollama list
```

先用不涉及私有源码的输入检查本机端点。在已经安装平台依赖的项目目录执行：

```powershell
uv run python -c "import httpx; r=httpx.post('http://127.0.0.1:11434/v1/embeddings',json={'model':'nomic-embed-text','input':['local indexing']},timeout=120,trust_env=False); r.raise_for_status(); print('vector dimensions:',len(r.json()['data'][0]['embedding']))"
```

成功会显示一个正整数维度；连接失败先检查服务，模型不存在则检查ollama list，不能把URL改成云端来绕过。记录ollama list显示的模型ID并保持同一权重；服务软件与模型是独立依赖，不在平台uv.lock中。下面的检索协议测试不冒充你的机器已加载了这个真实模型。

项目`.env`使用：

```dotenv
EMBEDDING_BASE_URL=http://127.0.0.1:11434/v1
EMBEDDING_API_KEY=local-no-auth
EMBEDDING_MODE=nomic-embed-text
EMBEDDING_ENABLED=true
EMBEDDING_MAX_CHUNKS=500
```

local-no-auth只是无鉴权本机服务的非秘密占位值，不是云账号密钥。受本机鉴权保护的服务填其专用Key；绝不继承聊天Key。设置完成后：

```powershell
uv run rnd index workbench .data/platform-index
uv run rnd tools embed workbench .data/platform-index
uv run rnd tools search workbench .data/platform-index "如何选择每个阶段的模型"
```

建立向量时对文本、模型身份和源码指纹做增量缓存；重新运行不会无条件重算所有未变片段。启用后规划上下文和MCP也使用这一套本机融合检索。向量数量超过显式预算会停止并要求你调整范围或预算，不静默漏掉代码。HTTP客户端关闭环境代理与重定向，远端地址即使带HTTPS也被拒绝。

### 20.4 Aider：独立Python环境中的真实本机工具

```powershell
uv sync --locked --project tools/aider --python 3.12
uv run --locked --project tools/aider --python 3.12 aider --version
```

预期Aider版本为0.86.2。平台依然用Python3.14；不要把Aider的依赖装进平台环境。工具路径可以由程序发现，或在AIDER_EXECUTABLE中明确指定本机安装位置。

```dotenv
REPO_MAP_PROVIDER=aider
CODING_ENGINE=aider
```

修改配置后重启平台。REPO_MAP_PROVIDER改变结构图的产生方式；CODING_ENGINE只影响Plan里确实存在额外单记录规则时的编辑步骤。普通CRUD不会为了展示工具而重复调用编码模型。

Aider在隔离HOME、有效空YAML配置、独立空env文件及临时Git副本中运行，关闭遥测、版本检查、自动lint/test和模型自动提交。真实模型请求只有平台ModelGateway执行，Aider不取得真实API Key。它使用CLI应用经过平台验证的SEARCH/REPLACE块；编辑后仍由平台检查唯一原文、允许文件、期望内容、规则示例与Git差异。

```powershell
uv run python -m scripts.ci_toolchain
```

这个脚本真实调用Aider，真实启动MCP并索引固定Java/Vue源码；模型响应是显式本机测试夹具，不消耗付费模型。报告中的SDK契约测试和本机Daytona服务测试分开标记，不能把前者冒充后者。

### 20.5 Continue通过本机stdio连接

先在本机安装VS Code，并在项目根目录终端安装固定Continue扩展：

```powershell
code --install-extension Continue.continue@2.0.0
code --list-extensions --show-versions
code .
```

第二条命令的输出应包含`continue.continue@2.0.0`。若系统找不到code，关闭并重新打开终端，或者在VS Code扩展面板搜索发布者Continue的Continue扩展，选择“安装另一个版本”中的2.0.0。不要在远程Codespaces、远程SSH或云端开发环境打开本课程目录。本节使用固定本机版本，不要求登录Continue账号或使用Hub配置。

在VS Code命令面板打开“Preferences: Open User Settings (JSON)”，在现有对象内设置`"telemetry.telemetryLevel": "off"`；不要覆盖其他个人设置。安装时访问公开软件仓库不等于把项目交给远程工具执行。Continue自己的工具策略是独立的：本平台只提供下文两个只读MCP工具，不授权IDE任意修改平台文件。

打开Continue侧边栏的配置入口，使用本机`config.yaml`。Windows路径为`%USERPROFILE%\.continue\config.yaml`，Linux/WSL为`~/.continue/config.yaml`。首次使用可以写入以下完整最小配置；已有配置先复制备份再人工合并，不能把已有模型密钥与另一供应商地址混用：

```yaml
name: RND local context
version: 1.0.0
schema: v1
models:
  - name: My selected chat model
    provider: openai
    model: "填写你选择的模型ID"
    apiBase: "https://填写该模型服务地址/v1"
    apiKey: "填写该服务专用密钥"
    roles:
      - chat
    capabilities:
      - tool_use
context: []
data: []
```

这里的model、apiBase、apiKey分别对应平台的MODE、BASE_URL、API_KEY，但本机IDE不会自动读取平台.env。apiBase与apiKey必须成对属于同一供应商。此文件只留在个人目录，不加入仓库或分享截图。只有聊天模型推理可用外部服务；不要添加云端embed/rerank模型、远程MCP地址、`uses`远程配置或data上传目标。`tool_use`只是声明模型支持工具调用，不会让不支持的模型凭空获得能力；模型服务必须实际支持。检索本身不需要这个模型或密钥。

先建立索引，然后导出配置：

```powershell
uv run rnd index workbench .data/platform-index
uv run rnd tools continue-config . workbench .data/platform-index
```

这会创建`.continue/mcpServers/rnd.json`，已有文件会拒绝覆盖。配置中是本机uv命令、项目目录和源/索引路径，没有Key。Continue通过stdio启动`rnd tools context-server`；stdout只传MCP协议，诊断去stderr。两个只读工具是search_code和repository_map，没有任意文件写入、任意shell或上传工具。

保存配置并重新载入Continue，在工具列表中确认出现`search_code`和`repository_map`。先在只读的Plan模式提出：“调用repository_map，再用search_code查找model_for，回答中给出文件和行号。”允许这两个本机MCP调用，不授权无关终端或写文件工具。应该看到源码路径、行号及内容，而不是要求注册远程索引账号。若MCP未连接，检查VS Code终端能否运行`uv --version`、导出配置的绝对目录是否存在；索引过期时先重新执行rnd index。命令行`uv run rnd tools search workbench .data/platform-index model_for`可独立验证检索，不用付费模型。

本平台仅使用Continue的公开MCP接口，不依赖托管Continue服务、不复制其私有索引实现，也不把协议测试称为IDE界面测试。IDE本身的聊天模型配置可按你的大模型服务填写；不要启用额外的云端检索或遥测扩展。

### 20.6 Daytona v0.190.0：必须部署完整本机服务

固定版本为v0.190.0，源码SHA为`01c502bb1f1ff8f2885d0cd490e043736083dca8`。下载一个CLI或安装Python SDK并不等于已经运行Daytona；完整本地系统还有API、Runner、Proxy、PostgreSQL、Redis、Dex、本地镜像Registry和MinIO。

上游的Docker Compose明确用于开发，不是生产安全部署。Runner使用privileged Docker-in-Docker；请只在你拥有的Linux/WSL开发环境使用，不暴露公网，不把它描述成抵御恶意内核攻击的强隔离。平台仍只执行登记的验证命令。

准备Linux x86_64/WSL2的Docker Engine或Docker Desktop集成，确认本机`/var/run/docker.sock`可用。`docker version`必须同时显示Client和Server。Windows平台本身可以直接运行，但本章的自托管服务路径以Linux/WSL为准；不要把Windows与WSL的虚拟环境混用。

在已经按本书创建的项目目录执行：

```bash
uv sync --locked --all-extras
uv run python -m scripts.daytona_local prepare
uv run python -m scripts.daytona_local images
uv run python -m scripts.daytona_local snapshot-image
uv run python -m scripts.daytona_local up
uv run python -m scripts.daytona_local status
```

prepare从固定SHA取得上游安装资源，生成本机配置和随机密码；目录非空时拒绝覆盖。它不是克隆本项目骨架。配置保存在`.data/daytona-local`，不得提交Git或共享。上游源码与许可证保存在upstream子目录，便于审查。

images不是去猜测可用的在线Daytona镜像标签。`scripts/daytona_build.py`先从固定Git提交导出干净的构建输入：不带`.git`、未提交修改或本机`.env`。API与Proxy的上游Dockerfile还要逐字节验证Git对象哈希；只在已匹配的构建环境中显式关闭Nx云构建/远程缓存和遥测，实际编译在本机Docker中进行。Runner的本机运行镜像使用兼容glibc的Debian环境，并从固定Docker版本复制Docker静态工具与DinD初始化脚本；Docker只监听容器内Unix socket，不开放TCP管理端口。构建时故意传入无效API_PORT，必须看到Runner自身的配置校验错误与退出码2，才能证明不是“文件存在但系统不能执行”。真正启动时先检查本机Docker daemon就绪，再启动Runner。Runner使用同一v0.190.0发布的`runner-amd64`，安装脚本把固定大小156006775字节和SHA256 `4265d2bb58ad6375b3c4c526ffa2bc2e1d197d94b92b431e532bf827c8f4dfa9`同时作为硬性条件，然后按完整给出的`tools/daytona/runner.Dockerfile`封装成自己的本机镜像。这不是下载其他版本替代，也不是使用在线Runner。该固定发布的Runner安装路径支持Linux x86_64，其他架构会明确停止；Windows请使用x86_64 WSL2 Docker。

基础依赖先逐项拉取并检查可用性，再执行较重的本机源码构建；MinIO使用独立固定源码`9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a`（`RELEASE.2025-10-15T17-29-55Z`），由`tools/daytona/minio.Dockerfile`在本机编译；没有第三方重打包镜像、商业账户或latest回退。这个对象存储版本与Daytona版本是两个独立依赖，Daytona仍严格固定v0.190.0。Go编译器版本固定1.24.8，编译时使用已提交的go.mod/go.sum校验依赖并关闭Go遥测；镜像包含原始LICENSE、依赖清单及对应源码source.tar，下载的原始仓库也保留在upstream-minio目录。MinIO是AGPLv3软件，本机演示与任何再分发都应保留其许可、署名和对应源码；不要把第三方源码标成本项目原创。API不授予privileged权限，只有运行Docker-in-Docker的Runner需要它。

构建镜像标签带版本与源码SHA，images.lock.json记录本机Image ID、构建文件SHA及Runner发布文件SHA；PostgreSQL等基础依赖拉取明确版本后记录实际Registry摘要。compose.lock.yaml只引用这些内容地址。重新启动前逐项对照两份锁，配置不一致就停止；没有任何latest或云端回退。构建失败看终端尾部和本机构建日志，不跳过images进入下一步。

snapshot-image先只启动本机Registry与固定TCP入口，再构建并推送预热快照。之后up才启动完整控制面，默认快照也指向本机Registry，不在业务验证时临时从Docker Hub拉取。up使用`--pull never`和已锁定摘要。所有发布端口绑定127.0.0.1；API、Runner、数据库、存储等后端仅连接internal网络，阻止外部出口；Docker命令显式指向本机daemon，不跟随保存的远程Docker context。

`scripts/daytona_gateway.py`是一个只转发字节的本机入口：Docker的internal网络不负责宿主机端口映射，所以不能把“容器Up”当成127.0.0.1可达。入口容器同时连接普通入口网络与内部网络，宿主机发布地址全部为127.0.0.1；其余服务没有第二网络、没有直接发布端口。入口只接受源码中固定的七个端口/服务对应，不读用户提供的URL或环境代理，不提供任意目标转发。它以UID65534、只读文件系统、删除全部Linux capabilities和no-new-privileges运行，只挂载这一份标准库脚本，不挂载.env、Docker socket或产品源码。它保留TCP字节和半关闭行为，因此HTTP、WebSocket与Registry传输都不需要改写请求或泄露令牌。

普通入口网络自身不是无出口网络；安全边界是入口代码只建立固定内部连接，而处理任务的API/Runner/存储仍只有internal网络。不要自行给这些后端添加普通网络来绕开连接错误。安装脚本先从127.0.0.1:6000取得真实Registry响应再推送快照；失败检查gateway与registry日志。这个拓扑也避免依赖Docker虚拟机内部IP，适用于本机Linux与WSL2的Docker。

up命令既检查全部容器状态，也检查API/Runner/Dex/Registry的真实回环HTTP响应；任一服务退出立即停止，不进入认证。区域名固定为local-computer，不能填入含空格的显示名称；上游会拒绝这种名称。私有管理Key与其他本机凭据一起随机生成并按0600保存，日志归档必须脱敏。

Dex在非privileged容器内用UID0读取只读挂载的0600配置，避免依赖开发电脑恰好使用UID1001；仅挂载自己的配置和身份数据库卷，并设置no-new-privileges。不能通过把密码文件改成公开可读来排错。

服务之间使用本机Docker网络名称通信。身份认证由本机Dex完成，文件存储为本机MinIO，镜像在本机Registry。外部PostHog/OTEL配置被移除或关闭；没有Auth0或云端控制面。Daytona自己的开发数据库与平台控制数据库、产品业务数据库各自独立。

### 20.7 创建本机身份并登记预热快照

```bash
uv run python -m scripts.daytona_bootstrap auth
uv run python -m scripts.daytona_bootstrap snapshot
```

auth使用本机Dex的独立bootstrap客户端及随机本机密码取得经过真实签名验证的身份，再为个人组织创建只含所需资源权限的API Key。它不伪造JWT、不登录云账号。这个密码授权流程只为回环绑定的开发环境提供确定性初始化，不建议照搬到公开OAuth产品。

上一节的snapshot-image只向docker build传入Dockerfile、产品pyproject.toml和uv.lock三个公开输入，不传平台源码目录、.env或用户数据。构建阶段下载Python3.14.7、uv和产品锁定依赖，把缓存预热到镜像；之后推送到本机127.0.0.1:6000 Registry。snapshot把该本机镜像登记为本机Daytona快照。注册操作在最长720秒的独立本机子进程中完成，超时终止而不是无限等待；失败不能写成已就绪。检查本机API/Runner日志和快照状态后再运行snapshot，不删除数据库或更换云端服务。

生成的`.data/daytona-local/workbench.env`包含可直接填入项目`.env`的六个Daytona字段及工具超时。打开文件在本机复制这些配置，不把Key贴到Issue、聊天或报告里。不要覆盖已有的BASE_URL/API_KEY/MODE；它们属于聊天大模型。

```dotenv
SANDBOX_PROVIDER=daytona
DAYTONA_ALLOW_LOCAL_EXECUTION=true
DAYTONA_API_URL=http://127.0.0.1:3000/api
DAYTONA_API_KEY=本机生成的值
DAYTONA_TARGET=local
DAYTONA_SNAPSHOT=本机脚本登记的快照名
```

重启平台后，只有本机验收通过才会进入Daytona附加关卡。默认Python/SQLite预热镜像支持迁移、HTTP、CRUD与重启复验的检查命令。沙箱参数禁止外网，安装命令明确offline，因此缺失依赖不会偷偷联网补齐。

原生Java/Vue的附加关卡需要准备包含Maven/pnpm离线缓存的本机快照；本书的默认Python预热镜像不冒充Java/Vue通用构建镜像。未准备原生快照时保持SANDBOX_PROVIDER=local即可完成原生完整本机验收。原生Daytona关卡只是额外构建/类型证据，不能替代原本的角色、数据库和浏览器验证。Python/PostgreSQL通道不会把本机数据库凭据复制到沙箱，选择这一组合并启用Daytona会明确阻止。

### 20.8 实际测试、报告和清理

```bash
uv run python -m scripts.ci_daytona_local
uv run python -m scripts.daytona_local status
```

ci_daytona_local生成一个独立SQLite产品，在本机Daytona中创建沙箱、传入可信源码/验证器、离线安装、执行HTTP/CRUD/重启检查并删除沙箱。最终读取reports/daytona-local.json。成功必须同时包含passed=true与cleanup=deleted；SDK响应模拟测试不产生这一实际服务证据。

运行自己的项目后，页面“报告”或`GET /runs/{id}/report`显示context、编辑与Daytona回执。沙箱的唯一名称在创建前已落盘，失败时按该名称在本机控制台核查。创建超时、执行失败、报告缺失和删除失败都会阻止交付，不改用一个伪造passed的本机结果。

本机服务停止：

```bash
uv run python -m scripts.daytona_local down
```

down不带-v，不删除持久卷、用户、Key或快照。已有安装用up继续，不再次prepare覆盖。确实要销毁实验环境时先确认没有需要保留的数据，再由你在Docker中明确处理该项目的卷；平台不自动删除未知资源。

### 20.9 接线和验收对应关系

| 能力 | 本机实现入口 | 对应证据 |
|---|---|---|
| 结构解析 | symbols.parse_file、knowledge.build_index | 固定Java/TS/Vue源码符号与行号；重复索引复用 |
| 混合检索 | retrieval.query、add_embeddings | FTS5、可选本机向量、预算、过滤、过期拒绝 |
| 精确编辑 | aider_tool.apply_blocks、code_rules_with_aider | CLI实际执行、唯一前像、文件范围、SHA、规则正反例、Git提交 |
| IDE桥接 | context_mcp.make_server、export_continue | 真实stdio MCP初始化、工具列表和查询，不是云端服务 |
| 本机沙箱 | sandbox、daytona_worker、daytona_local、daytona_bootstrap | URL/网络拒绝测试；另加本机完整服务生命周期报告 |
| 唯一手册 | build_handbook、rebuild_from_handbook、ci_handbook | 全部文本源码哈希、空目录重建、第三方依赖重建与本地导入来源 |

### 固定实现的官方来源

Daytona发布：https://github.com/daytonaio/daytona/releases/tag/v0.190.0
本地部署说明：https://github.com/daytonaio/daytona/blob/v0.190.0/docker/README.md
上游Compose：https://github.com/daytonaio/daytona/blob/v0.190.0/docker/docker-compose.yaml
镜像版本构建规则：https://github.com/daytonaio/daytona/blob/v0.190.0/nx.json
API构建文件：https://github.com/daytonaio/daytona/blob/01c502bb1f1ff8f2885d0cd490e043736083dca8/apps/api/Dockerfile
Runner发布文件：https://github.com/daytonaio/daytona/releases/download/v0.190.0/runner-amd64
固定Python SDK：https://github.com/daytonaio/daytona/tree/v0.190.0/libs/sdk-python
Dex本机密码连接示例：https://github.com/dexidp/dex/blob/v2.42.0/examples/config-dev.yaml
Continue固定接口与代码：https://github.com/continuedev/continue
Aider本机CLI选项：https://aider.chat/docs/config/options.html

这些链接用于查看第三方依据；完成本项目代码不要求读者从外部链接补齐本书遗漏的自有模块。

MinIO固定源码与构建说明：https://github.com/minio/minio/tree/9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a

Continue固定扩展与配置依据：https://github.com/continuedev/continue/blob/v2.0.0-vscode/README.md
Continue YAML字段：https://docs.continue.dev/reference
VS Code固定扩展安装：https://code.visualstudio.com/docs/configure/command-line

GitHub Actions按要求在测试Runner内部运行同样的本机服务，不调用Daytona托管API。用户启动产品和平台不依赖Actions；CI使用的临时身份与数据不代表用户的实际账户。

Ollama本机安装：https://docs.ollama.com/linux
Ollama关闭云功能与回环绑定：https://docs.ollama.com/faq
Ollama embedding兼容端点：https://docs.ollama.com/api/openai-compatibility

Docker内部网络与端口依据：https://docs.docker.com/reference/cli/docker/network/create/
Docker端口发布：https://docs.docker.com/engine/network/port-publishing/

Runner程序入口与配置校验：https://github.com/daytonaio/daytona/blob/01c502bb1f1ff8f2885d0cd490e043736083dca8/apps/runner/cmd/runner/main.go
区域名称约束：https://github.com/daytonaio/daytona/blob/01c502bb1f1ff8f2885d0cd490e043736083dca8/apps/api/src/region/services/region.service.ts


### 禁用可选 SSH 服务与 API 鉴权配置不是同一件事

固定版本 v0.190.0 的 `apps/api/src/auth/api-key.strategy.ts` 在校验任意 API Key 前，先通过 `getOrThrow('sshGateway.apiKey')` 读取配置。删除可选 SSH 容器仍需给 API 提供该必需值，否则本机登录能够成功，但使用生成的 API Key 注册快照时会报临时鉴权服务错误。

本机配置将 `SSH_GATEWAY_API_KEY` 从本次安装随机生成的管理密钥通过带用途标识的 HMAC-SHA256 派生为独立哨兵值。它不是固定公开密码，也不复用代理或健康检查密钥；没有 SSH 容器、地址或对外 SSH 端口，Runner 的 `SSH_GATEWAY_ENABLE` 仍为 `false`。密钥仅位于受限的本机配置，验收报告不包含环境配置和凭据文件。
