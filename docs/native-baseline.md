## 19. 验证原生框架：启动、登录、角色权限与前端

这一章验证固定上游版本自身的运行基线，不改变默认 Python 产品流程，也不把 `SOURCE_READY` 改为 `READY`。**原生生成文件自动挂载、生成模块菜单与权限集成、生成业务完整运行验收仍未完成。** 原框架自己的用户管理页面通过测试，不能代替生成业务验收。

### 19.1 本章创建的文件及连接顺序

本章所有文件的完整内容在下方源码附录；按下面顺序创建，不要根据名称自行补实现。

| 文件 | 工作 | 连接到哪里 |
|---|---|---|
| `workbench/native_environment.py` | 检查专用数据库、复制原生源码、安装依赖、启动和停止后端、真实登录 | 复用 `filesystem` 和 `tools`，不读取模型密钥 |
| `workbench/native_checks.py` | 调用原生用户、角色和菜单接口测试授权与撤销 | 使用真实后端 HTTP，不修改鉴权实现 |
| `workbench/native_frontend.py` | 冻结安装前端依赖、类型检查、构建、启动预览 | 使用上游原生目录和脚本 |
| `scripts/native_browser.cjs` | Chromium 浏览器真实登录并打开原生用户管理页面 | 不注入 token、不伪造 HTTP 响应 |
| `scripts/ci_native_runtime.py` | 串联整次原生基线验收，保存每一步证据 | 调用上面四个文件 |
| `tests/test_native_baseline.py` | 单元测试路径、环境隔离、响应码与菜单树算法 | 不代替真实服务测试 |
| `.github/workflows/native-runtime.yml` | 两套原生框架分别在 PostgreSQL、Redis 环境运行 | 独立于默认 Python 产品验收 |

运行链：复制固定源码 → 检查空专用库 → 初始化原生数据库 → 安装/编译 → 启动原生后端 → 登录 → 最小权限测试 → 前端安装/类型检查/构建 → Chromium 登录与原生页面验证 → 保存报告。

### 19.2 版本与环境

| 部分 | 固定输入 |
|---|---|
| 平台及 FastapiAdmin 后端 | Python 3.14；平台依赖使用仓库 `uv.lock` |
| FastapiAdmin 源码 | `1cd12c726ad9032c17ef85ce805ce991be60fbdf` |
| 芋道后端源码 | `47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be`，JDK 17 |
| Vben 源码 | `1b14e889f529e245fd620daa720dcea6de0cc5e7` |
| Node | 22 系列，至少满足 Vben 的 22.18 要求 |
| FastapiAdmin 的 pnpm | 9.15.3 |
| Vben 的 pnpm | 11.16.0 |
| 浏览器测试工具 | Playwright 1.56.1，Chromium |
| 数据库与缓存 | 本机 PostgreSQL 17、Redis 7.4 |

平台自身仍可用 SQLite。PostgreSQL 和 Redis 是本章原生框架运行的依赖，不是平台初次体验的前置条件。

原生运行脚本当前在 Linux CI 验证。Windows 用户可以在 WSL 2 的 Linux 目录执行本章命令；不要把 Windows 的 `.venv` 复制到 WSL。默认 Python 产品的 Windows 验收和原生框架 Linux 验收是不同范围。

### 19.3 先验证平台代码

以下命令在仓库根目录执行：

```bash
uv python install 3.14
uv sync --locked --all-extras
uv run python --version
uv run pytest tests/test_native_baseline.py -q
```

`--all-extras` 在这里安装 PostgreSQL 驱动，不会自动启动数据库。

### 19.4 建立隔离的开发数据库

只对你自己创建的空开发库执行。不要填写生产连接字符串，也不要为了通过测试删除现有数据库。

下面示例需要已安装并启动 Docker。第一次执行：

```bash
export NATIVE_PG_PASSWORD="$(uv run python -c 'import secrets; print(secrets.token_urlsafe(24))')"
docker run -d --name rnd-native-pg \
  -e POSTGRES_USER=native \
  -e POSTGRES_PASSWORD="$NATIVE_PG_PASSWORD" \
  -e POSTGRES_DB=fastapi_codegen \
  -p 127.0.0.1:5432:5432 postgres:17
docker run -d --name rnd-native-redis \
  -p 127.0.0.1:6379:6379 redis:7.4-alpine
```

检查服务：

```bash
docker exec rnd-native-pg pg_isready -U native -d fastapi_codegen
docker exec rnd-native-redis redis-cli ping
```

数据库应显示 accepting connections；Redis 应返回 PONG。端口被占用时先处理冲突，不要连接另一个未知服务。

为第二套模板建立另一个空库：

```bash
docker exec rnd-native-pg psql -U native -d postgres -v ON_ERROR_STOP=1 \
  -c 'CREATE DATABASE yudao_codegen'
```

本章使用无密码 Redis，仅限上述绑定回环地址的临时开发环境。不是公网部署配置。数据库名称必须匹配小写标识并以 `_codegen` 结尾；脚本检测到已有表会拒绝初始化，不会替你删库重建。芋道上游种子 SQL 含删除语句，因此空库检查是强制门禁。

### 19.5 取得固定原生源码

下面命令只运行一次。目录已存在时先确认版本，不要覆盖旧工作副本。

```bash
mkdir -p .native
git clone https://github.com/fastapiadmin/FastapiAdmin.git .native/fa-source
git -C .native/fa-source checkout --detach 1cd12c726ad9032c17ef85ce805ce991be60fbdf
git clone https://github.com/yudaocode/yudao-cloud-mini.git .native/yudao-source
git -C .native/yudao-source checkout --detach 47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be
git clone https://github.com/yudaocode/yudao-ui-admin-vben.git .native/vben-source
git -C .native/vben-source checkout --detach 1b14e889f529e245fd620daa720dcea6de0cc5e7
```

原生验证使用这三个已固定并实际下载的 GitHub 提交。使用 Gitee 时必须另外核对对应 SHA，不能假定镜像同步。

### 19.6 安装浏览器测试工具

先确认 `node --version` 满足前述要求，再执行：

```bash
npm install --prefix .native/browser --no-audit --no-fund --package-lock=false playwright@1.56.1
export PLAYWRIGHT_BROWSERS_PATH=0
.native/browser/node_modules/.bin/playwright install --with-deps chromium
```

这只给验证脚本安装浏览器工具，没有将 Playwright 添加到平台运行依赖。Linux 浏览器系统库安装可能需要 sudo 权限。

### 19.7 执行 FastapiAdmin 基线

```bash
npm install --global pnpm@9.15.3
export NATIVE_TEST_DATABASE_URL="postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/fastapi_codegen"
uv run python -m scripts.ci_native_runtime fastapiadmin \
  --source .native/fa-source --output .native/fa-product --frontend
```

脚本复制原生源码到新工作目录，不修改原始 `.native/fa-source`。后端监听 8001，前端预览监听 5173。`ENVIRONMENT=dev` 用于回环 HTTP 测试，`DEBUG=False`；原生生产模式的 HTTPS 跳转不适用于这个直接 HTTP 的实验。不要把测试环境参数复制到生产部署。当前 FastapiAdmin 开发启动可能生成自身迁移，测试仅在空专用库执行；平台自己的 Alembic 不代管上游数据库。

浏览器使用上游初始化的本地示例用户，执行页面上的真实登录与本地拖动校验。报告不保存访问令牌。后端不是 mock，API 返回的角色和菜单也不是前端伪造数据。

### 19.8 执行芋道 + Vben 基线

先确认 `java -version`、`mvn -version` 中是 JDK 17。第二套模板运行前先保存上一套报告，避免相同默认报告目录覆盖结果。

```bash
cp -r reports/native reports/native-fastapiadmin
npm install --global pnpm@11.16.0
export NATIVE_TEST_DATABASE_URL="postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/yudao_codegen"
uv run python -m scripts.ci_native_runtime yudao-vben \
  --source .native/yudao-source --output .native/yudao-product \
  --frontend-source .native/vben-source --frontend
```

脚本先用原生 PostgreSQL 种子初始化空库，给复制后的 `yudao-server` 创建 `application-native.properties`。凭据由进程环境变量提供，不写进该文件。JDBC 检查语句是 PostgreSQL 的 `SELECT 1`，而不是 MySQL 示例的 `SELECT 1 FROM DUAL`。

`yudao.security.mock-enable=false` 保持真实鉴权。验证码在临时实验环境显式关闭，浏览器仍必须用真实用户名密码获得原生 token。服务端监听 48080，Vben 使用原生 `/admin-api` 代理。Java 构建和启动显式设置 `LANG=C.UTF-8`、`LC_ALL=C.UTF-8`，防止清理子进程环境后中文文件名无法解析。

当前 Maven 命令先用 `-DskipTests` 构建，这是**编译步骤**，不能被写成 Java 单元测试全部通过；紧接着执行的 HTTP 权限和浏览器检查才是本章运行验收。

### 19.9 如何读取证据

报告目录 `reports/native/`：

| 文件 | 表示什么 |
|---|---|
| `backend-build.log` | 实际依赖安装或 Maven 编译日志 |
| `backend-runtime.log` | 原生后端启动及请求日志 |
| `openapi.json` | 本次真实运行服务导出的接口 |
| `baseline.json` | 原生启动与登录已达到的结果 |
| `permissions.json` | 无权限、授权、撤销等实际检查结果 |
| `frontend-install.log` / `frontend-typecheck.log` / `frontend-build.log` | 各阶段真实工具输出 |
| `frontend-build.json` | 构建命令、锁文件哈希和范围 |
| `browser.json`、`native-user-page.png` | Chromium 实际登录及原生用户页面证据 |
| `failure.log`、`browser-failure.png` | 失败位置；存在这些文件时先看失败原因 |
| `acceptance.json` | 整次命令完成后的范围和结果 |

命令退出码非零就是失败。只存在部分 JSON 不代表后续通过。每份最终报告都保留 `generated_runtime_verified=false`；原框架测试完成也不会把生成业务改成已验证。

### 19.10 权限验收到底测试什么

脚本通过真实管理员 API 创建专用测试用户和普通角色，只在临时数据库留下测试记录。按顺序确认：未登录拒绝；伪造示例 token 拒绝；空角色拒绝读取；管理员赋予用户管理读权限后可以读取；菜单出现在原生登录信息里；没有写权限时创建角色被拒绝；撤销读权限后重新登录仍被拒绝。

菜单页和查询按钮可能使用同一权限标识。脚本收集所有匹配项及其父目录，而不是错误地假定一个权限只能对应一个菜单。授权的是原生用户管理页面，**不是新生成业务页面**。

### 19.11 常见失败与停止条件

后端就绪请求出现 HTTPS 跳转：检查 FastapiAdmin 是否仍被设为 prod；不要关闭正式生产安全配置来迎合测试。

Java 报中文路径 `InvalidPathException`：检查子进程 UTF-8 locale。不要删除上游中文文件来掩盖环境错误。

前端 `--frozen-lockfile` 失败：记录真实锁文件与包管理器版本；不要静默改成无锁安装并继续宣称可复现。

原生权限接口报 403：检查本章新建普通角色与管理员角色是否混用；不要把普通用户改成超级管理员来让断言通过。

前端 API 404：检查 `/api/v1` 与 `/admin-api` 前缀、Vite 代理、实际端口；只看到首页 HTML 200 不等于前后端已联通。

再次运行提示输出目录存在或数据库非空：这是数据保护。建立新的工作目录和新的空专用库；不删除其他项目的数据。

**本章通关：** 原生启动、真实登录、角色读写边界、权限撤销、前端类型检查、构建、浏览器原生页面全部有通过证据。此后才具备继续排查生成业务集成的可靠基线；原生代码生成结果的挂载、菜单注册、生成 API/页面、两用户数据隔离和干净交付仍是独立且未完成的关卡。

### 19.12 GitHub Actions 与手册同步

`Native baseline acceptance` 在 Linux runner 上分别运行两套固定原生框架。PostgreSQL、Redis 是任务创建的临时服务，端口只绑定回环地址。工作流权限为 `contents: read`，不携带模型密钥。

测试结果查看该工作流对应提交的 Jobs 和 `native-runtime-fastapiadmin`、`native-runtime-yudao-vben` artifacts；不要用另一个提交或只有 `native-sources` 的绿色结果代替这次运行。

修改任一本章代码或说明后执行：

```bash
uv run ruff check --fix workbench scripts tests
uv run ruff format workbench scripts tests
uv run python -m scripts.build_handbook
uv run python -m scripts.build_handbook --check
uv run pytest -m 'not postgres' -q
```

根目录整份 Markdown 自动包含本章正文、相关源码和 CI 配置，不需要读者自己拼接多个补丁文件。
