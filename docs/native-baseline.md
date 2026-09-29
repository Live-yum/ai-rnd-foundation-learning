## 19. 原生生成产品：自动挂载、菜单权限和完整前后端验收

本章使用真实 FastapiAdmin、芋道 Cloud Mini 和 Vben 固定源码。基础代码来自它们自己的生成器；平台只做规格转换、模块挂载、必要的有记录兼容修正、独立验证和交付。

两种模式必须分清：第12章的外部服务模式只导出源码，结果是 `SOURCE_READY`；本章的托管原生模式会启动原生后端、调用生成器、挂载模块和菜单、验证角色权限、构建完整前端并运行真实浏览器。只有本次运行全部验收成功且你批准交付后才是 `READY`。配置文件存在不代表已经验收。

支持范围是本机单操作人、Linux/WSL 2、共享业务数据加原生角色权限、简单文本/整数/布尔字段 CRUD。每个实体至少一个必填文本字段。不要把逐用户隔离需求改成共享数据；关联表、支付、跨表事务和任意业务编码仍不支持。本章不是公网多租户生产部署指南。

### 19.1 按什么顺序创建文件

先完成第18章的平台文件。在同一仓库根目录按下表创建文件，内容完整复制自本手册下方同名源码块。不要另猜 API 地址或补空函数。

| 顺序 | 文件 | 工作及连接关系 |
|---|---|---|
| 1 | `workbench/native_environment.py` | 空库保护、源码副本、后端依赖构建、进程生命周期和真实登录；调用 filesystem/tools |
| 2 | `workbench/native_compatibility.py` | 只在副本中修正事务依赖作用域，记录修改前后哈希 |
| 3 | `workbench/native_modules.py` | Plan 转原生数据表；调用 NativeClient；生成、挂载代码和菜单 |
| 4 | `workbench/native_checks.py`、`workbench/native_acceptance.py` | 独立 HTTP 检查真实生成实体、角色授权撤销和重启持久化 |
| 5 | `workbench/native_vben.py`、`workbench/native_frontend.py`、`scripts/native_browser.cjs` | 冻结安装、完整应用构建与类型检查、Chromium 真实登录和生成页面 |
| 6 | `workbench/native_lab.py`、`scripts/ci_native_generated.py` | 串联各阶段；平台、CLI、CI 使用同一份实现 |
| 7 | `workbench/native_delivery.py` | 显式授权配置、交付等级、证据绑定、重新打开产品 |
| 8 | `tests/test_native_*.py` | 路径、配置、元数据、挂载、权限、事务和交付证据回归 |
| 9 | `.github/workflows/native-runtime.yml` | 在隔离 PostgreSQL/Redis 下真实运行两套原生产品和浏览器 |

连接顺序：`rnd chat → API → Job/Worker → LangGraph → managed_generate → run_acceptance → 原生 codegen → CRUD/RBAC → 停止后端 → Vite/vue-tsc → 重启与持久化 → Chromium → managed_verify/package → 人工交付确认`。

单文件创建后先运行 `uv run python -m py_compile 文件路径`。这只证明语法。相关依赖组齐全后，再运行：

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest tests/test_native_baseline.py tests/test_native_modules.py tests/test_native_managed.py tests/test_native_transaction.py tests/test_native_frontend_lifecycle.py tests/test_native_vben.py -q
```

这些本地测试不能代替真实原生全栈验收。后面的命令实际启动数据库、原生服务和浏览器。

### 19.2 固定版本与运行条件

| 部分 | 版本或固定提交 |
|---|---|
| 平台、FastapiAdmin 后端 | Python 3.14；分别使用自身 uv.lock |
| FastapiAdmin | `1cd12c726ad9032c17ef85ce805ce991be60fbdf` |
| 芋道后端 | `47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be`，JDK 17 |
| Vben 前端 | `1b14e889f529e245fd620daa720dcea6de0cc5e7` |
| Node | 22 系列且至少22.18 |
| FastapiAdmin / Vben 的 pnpm | 分别9.15.3 / 11.16.0 |
| 浏览器 | Playwright 1.56.1 对应的 Chromium |
| 原生数据库 / 缓存 | PostgreSQL 17 / Redis 7.4 |

平台本身仍默认 SQLite，三个模型参数足以体验默认 Python 通道；Java、Vue、PostgreSQL、Redis 不会因此消失。原生运行需要这些额外环境。Windows 请用 WSL 2 Ubuntu，在 Linux 用户目录创建新的克隆和 Linux `.venv`，不能复用 Windows `.venv`。

完整 Vben 前端较大，建议按16GB内存及约20GB可用磁盘规划，并预留交换空间。CI 为临时 runner 添加8GB交换文件；Node 堆上限8GB，Rust构建并行度2；构建前停止Java以降低峰值内存。没有删减页面或关闭类型检查。默认Python通道不要求这些资源。

### 19.3 在 Ubuntu / WSL 2 安装工具

Windows 用户先启动 Docker Desktop，在 Settings → Resources → WSL Integration 启用所用 Ubuntu。进入 Ubuntu 终端执行。以下不是 PowerShell 命令。

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates xz-utils openjdk-17-jdk maven
java -version
mvn -version
docker version
```

Maven显示的Java应是17。`docker version` 必须有 Server 部分。没有Docker的Linux主机也可以自行安装同版本数据库/Redis，但仍必须是回环地址与专用空库。

安装uv并克隆当前PR分支：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
mkdir -p "$HOME/Code"
cd "$HOME/Code"
git clone --branch feat/python314-workbench https://github.com/Live-yum/ai-rnd-foundation-learning.git
cd ai-rnd-foundation-learning
uv python install 3.14
uv sync --locked --all-extras
uv run rnd init
```

已有目录不要重复覆盖，先 `git status` 检查自己的改动。`--all-extras` 安装 PostgreSQL 驱动但不启动数据库。编辑这个Linux项目自己的 `.env`，保留 `BASE_URL`、`API_KEY`、`MODE`。

已有满足条件的 Node 22 时执行 `node --version` 和 `npm --version` 检查。没有时，可在用户目录安装官方22.18.0二进制并检查下载哈希：

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
cd "$HOME/Code/ai-rnd-foundation-learning"
```

新终端也要设置该PATH。上述二进制针对Linux x86-64；ARM设备需相应架构，不属于本章CI验证的体系。

### 19.4 创建专用空开发库

下面命令首次创建新容器。已有同名容器或端口占用时先检查，不要删掉不认识的数据。

```bash
export NATIVE_PG_PASSWORD="$(uv run python -c 'import secrets; print(secrets.token_urlsafe(24))')"
docker run -d --name rnd-native-pg \
  -e POSTGRES_USER=native \
  -e POSTGRES_PASSWORD="$NATIVE_PG_PASSWORD" \
  -e POSTGRES_DB=fastapi_codegen \
  -v rnd-native-pg-data:/var/lib/postgresql/data \
  -p 127.0.0.1:5432:5432 postgres:17
docker run -d --name rnd-native-redis \
  -p 127.0.0.1:6379:6379 redis:7.4-alpine
```

检查并等待健康，然后创建第二个库：

```bash
docker exec rnd-native-pg pg_isready -U native -d fastapi_codegen
docker exec rnd-native-redis redis-cli ping
docker exec rnd-native-pg psql -U native -d postgres -v ON_ERROR_STOP=1 -c 'CREATE DATABASE yudao_codegen'
```

预期依次为 accepting connections、PONG、CREATE DATABASE。Redis无密码仅用于上述回环开发环境。将随机密码保存在自己的密码管理器，并写入本机 `.env` 的数据库URL，不要发到聊天、日志或Git。

库名必须以 `_codegen` 结尾，主机限定127.0.0.1/localhost。初始化会检查所有非系统schema，发现已有表、视图、序列就停止。上游种子含DROP语句，不能取消空库保护。每个新原生生成运行需要新空库；失败也不会替你删除旧数据。

正常停止服务用 `docker stop rnd-native-pg rnd-native-redis`；恢复用 `docker start rnd-native-pg rnd-native-redis`。不要把删除数据卷当排错办法。已有数据卷重启时不要重新生成并覆盖原密码。

### 19.5 安装浏览器并固定源码

始终在平台仓库根目录执行：

```bash
npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
export PLAYWRIGHT_BROWSERS_PATH=0
.native/browser/node_modules/.bin/playwright install --with-deps chromium
```

浏览器系统库安装可能需要sudo。这些工具不加入平台Python依赖。

独立验收使用三个只读来源目录，后续一律复制到新的工作副本：

```bash
mkdir -p .native
git clone https://github.com/fastapiadmin/FastapiAdmin.git .native/fa-source
git -C .native/fa-source checkout --detach 1cd12c726ad9032c17ef85ce805ce991be60fbdf
git clone https://github.com/yudaocode/yudao-cloud-mini.git .native/yudao-source
git -C .native/yudao-source checkout --detach 47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be
git clone https://github.com/yudaocode/yudao-ui-admin-vben.git .native/vben-source
git -C .native/vben-source checkout --detach 1b14e889f529e245fd620daa720dcea6de0cc5e7
```

这里使用实际核验的GitHub固定提交。Gitee可以作为下载入口，但必须核对同一SHA确实存在，不能用镜像最新分支代替固定版本。平台 `rnd native prepare` 会从白名单克隆固定源码并建立知识包。

### 19.6 实际验收 FastapiAdmin 的两个生成模块

先不调用模型。此命令使用明确测试规格：设备与分类两个新实体，包含文本、整数、布尔字段；不是只打开原有用户管理页。

```bash
npm install --global pnpm@9.15.3
export NATIVE_TEST_DATABASE_URL="postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/fastapi_codegen"
uv run python -m scripts.ci_native_generated fastapiadmin \
  --source .native/fa-source --output .native/fa-product \
  --reports reports/native-fastapiadmin
```

程序执行：复制 → 初始化空库 → 原生后端真实登录 → 建业务表 → 原生导入/配置/ZIP导出/本地写入 → 发现插件路由 → CRUD → 原生角色与菜单授权撤销 → 停止后端 → 冻结安装前端、完整Vite构建和类型检查 → 后端重启与持久化 → Chromium真实登录、打开两个生成页面。

成功要求退出码0且 `reports/native-fastapiadmin/acceptance.json` 全部门槛为true。只有ZIP或部分日志不算通过。后端8001，前端预览5173；结束后停止所创建进程，数据库数据保留。

### 19.7 实际验收芋道 + Vben 的两个生成模块

使用另一个空库，切换对应pnpm：

```bash
npm install --global pnpm@11.16.0
export NATIVE_TEST_DATABASE_URL="postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/yudao_codegen"
uv run python -m scripts.ci_native_generated yudao-vben \
  --source .native/yudao-source --output .native/yudao-product \
  --frontend-source .native/vben-source \
  --reports reports/native-yudao
```

后端使用 `yudao-server` 聚合应用，无需整个Nacos集群。保留原生Spring Security、密码登录、角色和租户处理，`mock-enable=false`。开发验收关闭滑动验证码，但不跳过账号认证。后端48080，前端预览5173，不要与另一套同时占用端口。

原生生成器前端类型为40：Vben5 Ant Design Schema，不是Vben2或Element Plus。Controller/Service/DO/Mapper/VO由原生工具生成并挂入infra模块，前端挂入 `apps/web-antd`。调用原生菜单API建立目录、页面、按钮权限；对生成器要求手动加入的ErrorCode常量做确定性冲突检查与挂载。原生SQL导出仅保存，不盲目执行未知SQL。

Java先安装普通模块JAR，再单独打包聚合启动JAR，检查依赖JAR结构与PostgreSQL驱动。构建命令包含 `-DskipTests`，所以不能称上游Java单测全过。真正的本章证明来自随后执行的生成业务HTTP、角色权限、完整前端构建/typecheck和Chromium验收。

### 19.8 从平台需求进入原生全流程

独立验收用过的库已经非空。为新的平台运行另建库：

```bash
docker exec rnd-native-pg psql -U native -d postgres -v ON_ERROR_STOP=1 -c 'CREATE DATABASE my_fastapi_codegen'
```

在项目 `.env` 保留模型三项，并新增数据库URL：

```dotenv
NATIVE_FASTAPIADMIN_DATABASE_URL=postgresql+psycopg://native:填写自己的数据库密码@127.0.0.1:5432/my_fastapi_codegen
```

创建托管配置：

```bash
uv run rnd native runtime-config fastapiadmin
```

打开生成的 `.data/native/fastapiadmin.runtime.json`，只有确认是自己创建的空库后，才把初始化授权改成true：

```json
{
  "database_url_env": "NATIVE_FASTAPIADMIN_DATABASE_URL",
  "initialize_empty_database": true
}
```

JSON不保存密码。新文件默认false，避免误初始化。再运行：

```bash
npm install --global pnpm@9.15.3
uv run rnd native prepare fastapiadmin
uv run rnd start
```

另开同目录Linux终端，设置同一Node PATH后：

```bash
uv run rnd chat --template fastapiadmin
```

示例需求：共享设备台账，采用FastapiAdmin原生角色权限。设备包含必填name、quantity、active；分类包含必填name、position。两个模块支持增删改查，只读角色不可创建，写角色可创建，撤权后应拒绝访问。不要逐用户隔离、附件和关联表。

分别批准需求、设计与交付。模型只提出结构化规格，不重新手写重复CRUD。

芋道流程相同：另建 `my_yudao_codegen`，`.env` 增加 `NATIVE_YUDAO_DATABASE_URL`，运行 `uv run rnd native runtime-config yudao-vben` 并显式授权，切换pnpm11.16.0，然后 `uv run rnd native prepare yudao-vben`、`uv run rnd chat --template yudao-vben`。

托管模式自动通过原生种子管理员正常登录，不要求手动复制管理员token。第12章外部服务令牌JSON是另一种模式，不要混写。

### 19.9 重新打开已验证产品

保存运行UUID。在平台目录执行：

```bash
uv run rnd show 运行UUID
uv run rnd download 运行UUID
uv run rnd native serve 运行UUID
```

`serve`校验源码与验收哈希以及数据库身份后，启动后端和前端预览，不初始化、不删除数据。数据库身份绑定主机、端口、库名，允许密码轮换；切换新运行的数据库配置后，打开旧产品前要恢复它原来的库。

浏览器打开 `http://127.0.0.1:5173`。开发种子账号：FastapiAdmin `super`/`123456`；芋道 `admin`/`admin123`。生成过程还会建立权限测试角色和普通用户。这些都不能直接用于公网，部署前应修改密码并清理测试身份。

**原生ZIP是已验证源码，不是数据库备份。** 它依赖保留的专用PG开发库，其中有原生种子、菜单、角色和业务表；还需要Redis和原生依赖。不能承诺解压到任意空库即可恢复数据。迁移机器时另行安全备份和迁移数据库，不能把真实数据库转储或密钥混入代码包。默认Python产品的干净空库ZIP验证是另一个通道。

### 19.10 查看实际证据

独立测试使用传入的 `--reports` 目录；平台执行在 `.data/runs/运行UUID/native-evidence/`。

| 路径 | 作用 |
|---|---|
| `approved-spec.json`、`business-schema.sql` | 本次规格与业务DDL |
| `baseline/backend-build.log`、`baseline/backend-runtime.log` | 原生依赖、编译和启动 |
| `baseline/openapi.json` | 实际服务导出的接口契约 |
| `device-native.zip`、`category-native.zip`、`generation.json` | 原生生成器输出及挂载回执 |
| `native-compatibility.json`、`vben-compatibility.json` | 原生工作副本兼容修正的前后哈希与 Vben 独立扫描边界 |
| `generated/crud.json` | 两个生成实体CRUD、必填校验、非法认证检查 |
| `generated/permissions.json` | 普通角色授权、撤权及菜单检查 |
| `restart/persistence.json` | 重启后实际业务数据存在 |
| `frontend-install.log`、`frontend-build.log`、`frontend-typecheck.log` | 安装、生产构建、完整应用类型检查 |
| `browser.json`、`device.png`、`category.png`、Vben 的 `device-created.png` / `category-created.png` | 真实登录、列表渲染、生成表单提交与截图 |
| `generated-manifest.json` | 被验证源码哈希 |
| `acceptance.json` | 全部门槛；失败时保留false |
| `progress.json`、`failure.log`、`browser-failure.png` | 当前阶段与失败现场 |

检查报告：

```bash
uv run python -c "import json; d=json.load(open('reports/native-fastapiadmin/acceptance.json',encoding='utf-8')); print(d); assert d['generated_runtime_verified'] is True"
```

最终还必须有 `native_codegen`、`automatic_mount`、`menu_and_permissions`、`real_crud`、`restart_persistence`、`frontend_build`、`frontend_typecheck`、`real_browser`、`source_unmodified`，全部为true。只看一个HTTP200或服务首页不够。

### 19.11 兼容规则与排错

FastapiAdmin 的工作副本在启动前，对原生角色控制器与代码生成控制器的 `db_getter` 依赖设置 `scope="function"`，保留原有认证、权限、CRUD 和事务实现。这样导入表结构、更新生成配置、挂载菜单及授予角色权限都会先提交事务再返回成功，避免下一次列表/导出/登录请求早于提交产生偶发缺失。生成业务控制器沿用同样的提交边界，修改记录写入 `native-compatibility.json` 和生成回执；不是靠固定等待或盲目重试掩盖失败。

Vben 固定版本 `1b14e889f529e245fd620daa720dcea6de0cc5e7` 的兼容入口为 `workbench/native_vben.py`，在业务模块挂载完成后、前端冻结安装之前自动执行，不需要读者手工拼补丁。它核对全部预期源码片段后，修复已存在组件的失效引用、表单上下文、弹窗载荷和可选值、集合/排序声明、IP 校验 API，以及部门 ID 的类型收窄。任何输入片段不匹配都会报错，不盲目替换新版本源码。生成器导出的新增表单也做精确兼容：将旧式 `modalApi.getData<DTO>()` 的泛型迁到 `useVbenModal<Partial<DTO>>`，保留新增时的空载荷和编辑时的 ID 检查。原始生成 ZIP 不改写，`generation.json` 同时记录原始文件与实际挂载文件的哈希。未使用的 `Dayjs`、`getDictOptions` 导入仅在确认没有引用时删除，不关闭编译器的未使用检查。整数编辑/查询控件使用 `InputNumber` 并限定零位小数；布尔编辑/查询控件使用有真实 `true/false` 选项的 `RadioGroup`，不提交字符串代替布尔值。Chromium 还会从两个生成页面实际新增记录，检查整数 `0`、布尔 `false` 的请求值和数据库返回值，并保存新增后的页面截图。

工作副本不会复制上游 `.git`、令牌或环境文件。Vben 副本单独执行 `git init --quiet --template=` 建立本地扫描边界，没有上游 remote、提交历史或 hooks；此边界也不进入源码 ZIP。缺少边界时，构建扫描可能跨入平台和兄弟工作目录，导致日志停滞与内存异常增长。不要用扩大内存、删除业务路由或禁用类型检查代替修复。保留原始仓库不变，并保存 `vben-compatibility.json` 中逐文件的 before/after SHA-256。

前端使用原始 `apps/web-antd` 入口和完整应用配置。顺序为 `pnpm install --frozen-lockfile`、`vite build --mode production`、`vue-tsc --noEmit --skipLibCheck`；最后一项检查全部应用源码和生成模块，`skipLibCheck` 仅沿用第三方声明检查边界，不排除业务目录，不加入 `@ts-ignore`、`@ts-nocheck` 或宽泛 `any` 来掩盖错误。构建、类型检查、重启持久化和真实浏览器均成功才写入最终成功回执。

FastapiAdmin生成服务使用flush，事务由yield依赖完成。在生成控制器和副本内的角色控制器中，将数据库依赖设为function scope，使提交在成功响应发送前完成。这样创建后立即查询和授权后立即登录不会看到未提交状态。保存前后哈希，不改鉴权逻辑、不放宽断言。官方说明：<https://fastapi.tiangolo.com/advanced/advanced-dependencies/>。

芋道PG种子的逻辑删除字段是整数；不能与业务布尔字段混用。业务字段保留注释以供原生生成器识别。权限检查使用真实原生API，不直接插入管理员身份。验证无登录/伪造token/空角色拒绝、只读可查不可写、写授权可创建、撤权再拒绝。原生权限缓存存在传播时间，检查有明确等待上限，不以清缓存或改权限实现绕过。

数据库非空：停止，保留数据，为新运行另建空库。原生生成中断后的部分数据库和文件不自动销毁。不要重复覆盖已经批准的工作目录。

后端失败：先看对应构建日志尾部，再看运行日志。Maven环境问题不能交给编码模型乱改业务代码。每条后端构建命令360秒上限，前端900秒；超时停止进程组并保留有界首尾日志。进度每15秒输出耗时、日志字节量和可用内存，不输出密钥或进程环境。

前端缺少ref/computed等自动声明：先让原生Vite插件生成声明，再运行完整应用vue-tsc，不能删除检查。Vben原生配置插件从dotenv文件读取，因此工作副本生成 `.env.production` 和可交付 `.env.production.example`；只包含公开VITE变量，不复制模型或数据库密码。

浏览器失败：读 `browser.json` 的响应、状态和page_errors，再看截图。Ant Design 单选按钮内部 input 是隐藏的，真实自动操作点击对应可见 label，再验证 isChecked 和请求中的布尔值，不强制点击隐藏元素。FastapiAdmin采用真实鼠标滑块操作；先等布局稳定，再在轨道内拖至末端，移出轨道会触发原生重置。不能注入token、mock接口或删掉生成页面检查。Playwright定位器说明：<https://playwright.dev/docs/best-practices>。

### 19.12 GitHub Actions 与完整手册同步

`Native generated full-stack acceptance` 用两个Linux矩阵job分别创建临时PG17和Redis7.4，克隆固定源码、安装Chromium，并执行同一个 `ci_native_generated`。两个job各自成功才算两套原生生成模块验收通过。源码下载job、本地单测、另一提交的绿色结果不能代替它。

`Python 3.14 acceptance`另外运行Windows/Linux平台回归、实际PG checkpoint、默认Python产品独立安装与干净解压。两套工作流范围不同。

修改源码和本章正文后，在仓库根运行：

```bash
uv run ruff check .
uv run ruff format --check .
uv run python -m scripts.build_handbook
uv run python -m scripts.build_handbook --check
uv run pytest -m 'not postgres' -q
```

所有实现文件、迁移、依赖锁、测试、CI与说明会同步进入根目录完整Markdown。测试检查逐文件哈希、在空目录还原代码和重新生成手册，不需要读者拼接多份补丁。
