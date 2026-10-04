# docs/native-baseline.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本教材正文的源文件。** 上文正文就是这些源文件拼接后的内容。它们也收录在附录中，使从教材还原出的项目能再次生成逐字一致的完整教材，而不是只有一次性的代码快照。

**对应关系：** scripts/build_handbook.py的GUIDES → 正文 → 完整源码附录。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `docs/native-baseline.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L288。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`22733`。本段原文以LF换行结束。

<!-- learning-source: {"path": "docs/native-baseline.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fd86229cac7577c22ac05079d19f7ae104ffb25647e7909eff7b4d420468b6ee"} -->
````markdown
<!-- docs/native-baseline.md -->
## 19. 原生全栈：自带源码、自动生成与独立新数据库交付

本章使用真实 FastapiAdmin / 芋道 Cloud Mini / Vben 固定源码，不另写一个简化后端冒充原框架。基础CRUD由原生生成器产生，平台负责受校验的表元数据、挂载、菜单、兼容修正、权限/浏览器验证以及独立部署包。

固定模板源码由书中的vendor脚本取得，演示仓库也已自带；原生产品的交付包含新数据库初始化、业务DDL和菜单SQL，不要求依附当初生成它的平台数据库。原生语言运行时仍必须存在，不可能通过三个模型参数替代Java、Node、PostgreSQL和Redis。

### 19.1 本章的真实范围

| 通道 | 创建方式 | 成功标准 |
|---|---|---|
| 原生托管生成 | 页面/CLI先选择原生前后端、PostgreSQL | 当次原生生成、挂载、角色、CRUD、重启、前端构建/类型/浏览器以及独立新库启动通过，交付获授权后READY |
| 原生接口导出 | 为已部署生成器提供专用配置/令牌 | 只导出源码时仍是SOURCE_READY，不能冒充全栈已测 |
| 独立交付启动 | 解压原生产品，在产品目录运行start.py | 自己的依赖锁、SQL、服务和数据库，无需原平台或模型Key |

不带business合同的原生基础路径处理shared数据、原生角色权限及text/integer/boolean单表CRUD；不能暗改默认产品的per_user数据归属。声明Plan.business时，另由业务适配器处理明确关系、角色行范围、命名状态操作及相应统计，详见业务产品章节。两条路径分别验证，不能互相借用成功报告。任意脚本、合同外关系/副作用、支付和生产安全部署不在自动适配范围；business合同与自由额外custom_rules不混用。

### 19.2 文件、职责与完整代码位置

附录逐个包含所有文件最终代码。按表顺序阅读和创建，不补占位函数、不把不同模板的代码文件混起来。

| 文件组 | 职责 |
|---|---|
| `vendor.py`、`templates/vendor/manifest.json` | 读取仓库内固定ZIP，核对SHA/许可证/安全解压，提供源码知识包 |
| `native_environment.py`、`native_resources.py` | 创建本次运行自己的服务或接受已授权的空开发库；原生安装、初始化、进程启停和真实登录 |
| `native_modules.py`、`native_compatibility.py`、`native_vben.py` | 原生生成器调用、审计字段元数据、Java/Vue插件挂载、菜单与兼容变更回执 |
| `native_checks.py`、`native_acceptance.py` | 普通角色授权/撤销、生成实体CRUD、必填验证与重启持久化 |
| `native_frontend.py`、`scripts/native_browser.cjs` | 完整应用构建/类型检查，真实Chromium登录、菜单及两个生成页面 |
| `native_lab.py`、`scripts/ci_native_bundled.py` | 平台和CI共用执行链；从随库模板开始，不依赖本项目骨架 |
| `portable.py`、`portable_checks.py` | 导出新库所需SQL及菜单，把独立启动器放进产品，再用另一新数据库实测 |
| `templates/deployment/entry.py/run.py/services.yaml/uv.lock` | 最终用户拿到的独立启动与数据库生命周期，不依赖原平台安装 |
| `native_delivery.py` | 绑定源码和验收证据，只有完整通过才发布，兼容重新打开原开发副本 |

### 19.3 固定源码与环境

| 组件 | 固定输入 |
|---|---|
| 平台、FastapiAdmin后端 | Python3.14，各用自己的uv.lock |
| FastapiAdmin源码 | `1cd12c726ad9032c17ef85ce805ce991be60fbdf` |
| 芋道Java源码 | `47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be`，JDK17/Maven |
| Vben源码 | `1b14e889f529e245fd620daa720dcea6de0cc5e7` |
| Node | 22系列，满足Vben的至少22.18要求 |
| pnpm | FastapiAdmin9.15.3；Vben11.16.0 |
| 原生服务 | PostgreSQL17、Redis7.4 |
| 平台浏览器验收 | Playwright1.56.1对应Chromium |

源码在 `templates/vendor/fastapiadmin.zip`、`yudao-backend.zip`、`yudao-frontend.zip`。运行 `uv run rnd init` 后本地解压；再执行 `uv run rnd native prepare 模板名`也只是验证/准备这些已包含的固定快照。安装依赖仍用网络，不等于离线构建。

原生全栈在Linux验收。Windows使用WSL2 Ubuntu，在Linux目录按本书创建文件并建立Linux `.venv`，不要复用Windows虚拟环境。默认Python产品仍在Windows/Linux分别测试。完整Vben较大，建议至少16GB主机内存和足够磁盘；平台错开Java和Vite构建，必要时明确配置交换空间，不删除业务页面来减负。

### 19.4 在Linux/WSL准备工具

Windows先启用WSL2及Docker Desktop的WSL Integration，进入Ubuntu终端。以下是Ubuntu x86-64命令，不是PowerShell：

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates xz-utils openjdk-17-jdk maven
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
java -version
mvn -version
docker version
```

FastapiAdmin不要求JDK/Maven。芋道的Maven实际使用Java必须为17。docker version必须显示Server，不只是安装了Client。原生运行只绑定回环，不应在公网暴露开发管理员或数据库。

#### 19.4.1 Docker还没有安装时怎么办

Windows读者先从[Docker Desktop官方Windows安装页](https://docs.docker.com/desktop/setup/install/windows-install/)按安装向导选择WSL2后端，安装后从开始菜单启动Desktop并自行阅读/决定接受其许可条款；商业组织须核对适用订阅。在Settings的Resources → WSL Integration启用本次Ubuntu。不要同时在同一个WSL发行版里另外安装第二个Docker Engine。回到Ubuntu运行`docker version`与`docker compose version`，两条都成功才继续。

以下只适用于没有既有Docker/容器运行环境的受支持Ubuntu主机。若已有容器、镜像或冲突软件包，先按[官方Ubuntu安装说明](https://docs.docker.com/engine/install/ubuntu/)核对；不要为了跟教程自动卸载已有服务。新主机可按顺序配置官方软件源并安装：

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl --fail --silent --show-error --location https://download.docker.com/linux/ubuntu/gpg --output /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
printf 'Types: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: %s\nComponents: stable\nArchitectures: %s\nSigned-By: /etc/apt/keyrings/docker.asc\n' "${UBUNTU_CODENAME:-$VERSION_CODENAME}" "$(dpkg --print-architecture)" | sudo tee /etc/apt/sources.list.d/docker.sources
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl start docker
sudo docker version
sudo docker compose version
```

先验证sudo下能连接服务，再决定让运行平台的本机账号使用Docker。Docker组拥有相当于root的主机权限；只在自己控制的开发机、理解这一后果后，依照[官方用户组说明](https://docs.docker.com/engine/install/linux-postinstall/)执行`sudo usermod -aG docker "$USER"`，退出系统会话后重新登录。最后不用sudo运行`docker version`，确认Client/Server都可见。不要用`chmod 666 /var/run/docker.sock`给所有账号开放权限，也不要开启公网TCP Docker管理端口。

这一步修改的是主机软件与权限，不是项目Python环境。平台脚本不会替你提升权限；仍报Permission denied时停下来核对账号/服务，不把整个研发平台用sudo启动。记录`docker version`与`docker compose version`的实际版本，作为后续本机Daytona证据的环境信息。

#### 19.4.2 Node与平台依赖

已有Node22.18+直接使用；没有时可安装官方用户目录二进制并核对哈希：

```bash
mkdir -p "$HOME/.local/share/rnd-tools"
cd "$HOME/.local/share/rnd-tools"
curl -fLO https://nodejs.org/dist/v22.18.0/node-v22.18.0-linux-x64.tar.xz
curl -fsS https://nodejs.org/dist/v22.18.0/SHASUMS256.txt | grep ' node-v22.18.0-linux-x64.tar.xz$' > node.sha256
sha256sum -c node.sha256
tar -xJf node-v22.18.0-linux-x64.tar.xz
export PATH="$HOME/.local/share/rnd-tools/node-v22.18.0-linux-x64/bin:$PATH"
node --version
npm --version
```

其他CPU架构使用匹配官方二进制。新终端要保留这个PATH或写入自己的shell配置。系统旧Node版本不能用来装Vben11系pnpm。

回到按照本书创建的项目根目录（例如`~/rnd-learning`）：

```bash
cd ~/rnd-learning
uv python install 3.14
uv sync --locked --all-extras
# 从空目录手写时执行；已有合法vendor ZIP的演示仓库可直接init
uv run python -m scripts.vendor_templates --fetch
uv run rnd init
```

全部平台源码来自本书完整代码区；vendor脚本只取得固定第三方依赖，不下载本项目的现成骨架。不要复用Windows虚拟环境，也不要用清空数据库解决安装问题。

安装平台的独立浏览器验证工具：

```bash
npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
export PLAYWRIGHT_BROWSERS_PATH=0
.native/browser/node_modules/.bin/playwright install --with-deps chromium
```

仅平台做真实浏览器验收需要该目录；拿到最终产品的普通用户启动时不需要平台本身，也不需要导入CI模型夹具。

### 19.5 先选原生前后端/数据库，再描述需求

FastapiAdmin先选择对应pnpm：

```bash
npm install --global pnpm@9.15.3
uv run rnd start
```

另一个同目录终端设置同一Node PATH，运行：

```bash
uv run rnd chat --template fastapiadmin --frontend fastapiadmin-vue --database postgresql
```

芋道改用pnpm11.16.0及 `--template yudao-vben --frontend vben-antd --database postgresql`。浏览器首页同样先选择这三个组合，再写需求；不再默认锁死python-basic后不断要求删需求。

示例原生需求：“设备和分类两个台账，数据按原生角色共享。设备包含必填名称、数量、启用状态；分类包含必填名称和排序。两个模块支持增删改查、必填校验、只读角色和写入角色。不需要逐用户隔离、关系或外部接口。”

手工确认或智能推荐均可。没有专门的runtime配置时，平台在设计获授权后为该run创建独立Docker Compose服务，随机密码、回环空闲端口、独立持久卷，防止共用已有生产数据库。服务凭据保存在 `.data/native-services/<run-id>/`，不进入Git或交付包。

### 19.6 可选：显式授权自己准备的开发服务

不使用自动Docker时，你可以在本机创建自己拥有的专用空PostgreSQL库和Redis。数据库名称必须以 `_codegen` 结尾，只允许回环地址；非空库会被拒绝，不取消检查。

例如创建独立实验容器：

```bash
export NATIVE_PG_PASSWORD="$(uv run python -c 'import secrets; print(secrets.token_urlsafe(24))')"
docker run -d --name rnd-native-pg \
  -e POSTGRES_USER=native -e POSTGRES_PASSWORD="$NATIVE_PG_PASSWORD" \
  -e POSTGRES_DB=fastapi_codegen -v rnd-native-pg-data:/var/lib/postgresql/data \
  -p 127.0.0.1:5432:5432 postgres:17
docker run -d --name rnd-native-redis -p 127.0.0.1:6379:6379 redis:7.4-alpine
docker exec rnd-native-pg pg_isready -U native -d fastapi_codegen
docker exec rnd-native-redis redis-cli ping
```

预期接受连接和PONG。同名容器或端口已占用时先检查，不强制删除。密码只保存在你自己的安全位置/.env，不贴日志。Redis无密码仅用于这里的本机开发服务，不是生产模板。

在.env设置 `NATIVE_FASTAPIADMIN_DATABASE_URL=postgresql+psycopg://native:自己的密码@127.0.0.1:5432/fastapi_codegen`，执行 `uv run rnd native runtime-config fastapiadmin`，编辑打印的runtime.json，将initialize_empty_database改为JSON布尔true。芋道使用另一个新空库、NATIVE_YUDAO_DATABASE_URL和对应runtime-config命令。配置文件存在不代表已完成验证，每次仍按安全条件检查。

独立交付验收会创建另一个临时数据库，不复用生成源库，所以用于平台原生验收的本机账户需要CREATEDB权限。所有操作限定你授权的开发环境，不提供生产数据库自动维护。生成中途失败保留现场，修正后新建运行/空库，不DROP旧业务数据掩盖错误。

### 19.7 原生生成怎样连接到真实框架

FastapiAdmin使用原生导入、元数据更新、批量ZIP、本地输出接口。每个实体独立module_name，避免两个实体覆盖同一个模块。代码和菜单由原生生成器输出，平台重启后由原来的插件发现机制加载。原生API、角色和生成业务控制器的数据库依赖使用有记录的函数级提交修正：先提交成功，后返回响应，防止导入/授权成功响应早于数据可见。不会关闭原生权限或盲目sleep重试。

芋道以原生master数据源、Vben5 AntDesign类型40生成。平台元数据包含真实审计列、tenant_id、PostgreSQL序列和注释；逻辑删除字段按原始PG种子使用整数，与普通业务布尔字段区分。Controller/Service/DO/Mapper/VO挂载到infra模块，Vben导出挂到apps/web-antd。错误码常量只在明确原生模板格式下确定性补齐；菜单通过原生API创建，不执行模型自拟SQL。

保留完整原生应用。固定Vben原始源码的兼容修正记录修改前后SHA，不删除旧页面或路由；生成表单的modal泛型、数值控件和布尔选项适配有单独测试。工作副本建立空的本地Git扫描边界，不复制上游历史/凭据，避免Tailwind扫描父目录；该.git不会进入交付。

构建和完整应用vue-tsc检查都必须通过。构建在类型检查之前，因为Vite插件先生成自动导入声明。skipLibCheck仅针对第三方声明，不排除业务源码或新生成模块。Java两阶段构建保证模块为普通依赖JAR，聚合入口包含PG驱动；编译命令使用-DskipTests，不能因此声称上游所有Java单测通过。

### 19.8 模块与菜单权限的实际验收

每个生成实体必须经过：未登录/伪造token拒绝、创建、读取比较所有字段、修改后读取、分页包含记录、缺失必填被客户端错误拒绝、删除后消失、写入持久化样例、后端进程重启后仍能读取。

普通原生角色测试：无权限拒绝、只读授权可读取共享记录且显示菜单、无写权限新增拒绝、写授权后新增成功、撤销后再次拒绝并移除菜单。芋道原版有一分钟权限缓存，测试等待有界收敛并记录，不清空缓存、不升级管理员去“通过”。需要即时撤权的生产需求另做实现。

Chromium实际填写用户名密码、执行原生认证、读取真正菜单，打开设备与分类两个生成页面，等待真实列表请求并比较持久化样例。Vben额外真正提交新增表单并检查整数0和布尔false的请求/返回类型。不是只访问首页200，也不注入用户token或mock页面请求。

### 19.9 最终产品为什么能在新数据库独立启动

平台先保存生成前菜单快照，生成后仅导出新增/变化菜单；不会把开发用户、密码或业务记录当成菜单SQL打包。SQL标识符和值由psycopg安全转义，不是大模型自由输出的字符串。

产品根目录包含：

```text
start.py
START_HERE.md
backend/                         真实原生后端
frontend/web/ 或 frontend-product/  真实原生前端
deployment/
  pyproject.toml、uv.lock、.python-version
  run.py、services.yaml
  manifest.json
  database/002-business.sql
  database/003-menus.sql
  workbench/                     独立启动所需的有限可信工具，不是原平台安装引用
```

原生初始化种子在已包含的后端源码中。启动顺序由run.py实现：校验SQL哈希 → 空库或本产品归属 → 原生种子 → 业务表/序列 → 菜单 → 原生依赖与后端 → 新库菜单/CRUD检查 → 停止后端构建完整前端 → 再启动后端和前端。

交付之前，CI会将只有可分发文件的副本复制到一个新目录，在**另一个新的数据库**执行这个包自己的start.py --check；检查passed、frontend_started、菜单恢复、类型及CRUD，才记录独立交付成功。即使原开发副本已经通过浏览器，也不能跳过这次新库启动。

### 19.10 拿到ZIP后的唯一入口

在Linux/WSL安装本模板需要的语言工具和Docker Compose，解压ZIP，进入包含start.py的根目录：

```bash
uv run --no-project --python 3.14 python start.py
```

无需原平台、原开发库或模型API_KEY。首次自动创建本产品的服务，随机数据库密码，配置在`.deployment/services.json`，数据库卷持久化。控制台打印后端和前端地址，浏览器打开前端（默认5173）。后端自动选择本机 TCP 动态客户端端口范围之外的空闲非特权端口，避免 Java 连接 PostgreSQL/Redis 时先占用 48080 再导致 HTTP 监听失败。选择记录在该副本的 `.deployment/backend-port.json`；产品锁和端口锁跨构建、两次启动和清理持续持有，重启复用相同端口，独立副本重新分配。前端构建和验收使用同一实际后端地址。不会修改主机网络设置或结束占用端口的其他进程，已记录端口发生冲突就明确失败。

`NATIVE_DELIVERY_PORT` 仍表示用户明确指定的精确端口，不会在冲突时换端口；若自行指定动态范围内端口，调用方承担出站源端口碰撞风险。未知操作系统或无法读取动态范围时，自动选择明确失败，可按该主机网络配置显式指定端口。平台 CI 和托管原生验收使用相同分配器；已有外部原生服务配置及上游生产默认端口不变。

只有自己已经准备好新的专用空数据库与Redis时，才显式设置：

```bash
export NATIVE_DELIVERY_DATABASE_URL='postgresql+psycopg://自己的账号:自己的密码@127.0.0.1:5432/new_product_codegen'
export NATIVE_DELIVERY_REDIS_PORT=6379
uv run --no-project --python 3.14 python start.py
```

这样的环境不需要自动Docker服务。库名以_codegen结尾，必须空或由同一产品认领；不能指向生产库。启动器的SQL清单和数据库注释防止误重复初始化另一产品。运行默认种子账号只供本机开发，首次成功后修改密码；普通重启不重置密码也不要求旧默认密码。

首次安装完成后可 `start.py --skip-build` 复用该副本的构建输出；不要在全新目录跳过构建。该模式检查副本端口回执及前端构建地址，改变端口或复制目录后应先不带 `--skip-build` 重建；Java 启动读取当前 native 配置，包含监听端口及 OpenFeign 自调用地址。`start.py --check` 完成后端和前端都启动并验证后退出，适合干净交付验收而非普通长时间使用。Ctrl+C停止应用但不删除数据库卷。

源代码和初始化SQL不等于用户数据备份。产品使用后，迁往另一主机还要备份真实PG数据及必要配置；不要将`.deployment`密钥或数据库导出提交Git/源码ZIP。首启失败若数据库标为claimed，保留现场按日志修正后在同一产品恢复；未知/部分不一致业务表不自动覆盖。

### 19.11 不调用真实模型的本地原生验收

平台源代码和浏览器工具就绪后，为测试创建一个新的专用空数据库；不要用已经生成完产品的库。测试数据库管理账户可创建/删除仅此测试的临时新库。

```bash
export NATIVE_TEST_DATABASE_URL='postgresql+psycopg://native:自己的实验密码@127.0.0.1:5432/native_codegen'
npm install --global pnpm@9.15.3
uv run python -m scripts.ci_native_bundled fastapiadmin
```

芋道另用新的空库与对应pnpm：

```bash
export NATIVE_TEST_DATABASE_URL='postgresql+psycopg://native:自己的实验密码@127.0.0.1:5432/yudao_codegen'
npm install --global pnpm@11.16.0
uv run python -m scripts.ci_native_bundled yudao-vben
```

两套验收默认使用 `.native/product` 输出路径。同一checkout顺序跑时，第一套完成后将其整个工作产物目录**移动保留到别处**，确认没有占用进程，再跑另一套；也可使用两个干净平台checkout。脚本不无条件覆盖已有产品。每条命令的输入是显式的测试规格，不是你的真实模型回答。真实模型体验使用前述rnd chat。

### 19.12 读取报告与故障定位

平台run证据在 `.data/runs/<UUID>/native-evidence/`；独立脚本证据在 `reports/native/`。

| 证据 | 含义 |
|---|---|
| bundled-sources.json、vendor manifest | 使用的随库源码、固定commit和整体哈希 |
| approved-spec.json、business-schema.sql | 实际输入与原生业务DDL |
| generation.json、原生ZIP | 原生生成器实际输出、挂载路径和修改回执 |
| generated/crud.json、permissions.json | 真正生成模块及角色权限结果 |
| restart/persistence.json | 后端进程重启后的记录比较 |
| frontend-*日志 | 锁定安装、完整构建、业务源码类型检查 |
| browser.json、PNG截图 | 实际登录、菜单、两个生成页及Vben表单 |
| portable-start.log/json | 另一空库和独立交付启动器的结果，frontend_started不可缺失 |
| acceptance.json、manifest | 全部阶段成功标识，与当前代码/规格/SQL哈希绑定 |

只看到部分成功文件不代表最终通过。失败时acceptance保持未完成，failure.log保留阶段和位置。工具超时保留有界首尾日志；账号密码不进入公共报告。

遇到HTTP500不是权限拒绝；授权错误看真实角色和缓存，不关闭鉴权。前端缺类型先核对原生lock与固定兼容适配，不删路由/降低检查。独立启动只有后台成功时继续检查前端，不提前返回--check。数据库非空时不取消保护、不自动DROP，不通过“再跑一次删库”掩盖错误。

### 19.13 原生验收的边界

正式Actions原生矩阵使用真实PG/Redis/Java/Python/Node/Chromium；平台模型CI使用夹具，不能说已验证用户供应商账户。原生类型检查与HTTP验收不代表所有上游历史测试通过。普通共享CRUD权限不代表任意行级隔离或多租户生产安全。

本手册第二部分使用的所有实现代码都在后面的整份源码附录；源码改变后用同一build_handbook命令重新生成，不把“待实现”函数藏在附录里。独立交付首次环境仍需互联网安装依赖，但不再需要重新拉取模板或原始开发数据。测试结果以所用提交对应的Actions及portable-start报告为准。
````
