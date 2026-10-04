# 09 · 原生快照与框架接入

[总目录](../README.md) · [上一阶段](../08-control-plane/README.md) · [下一阶段](../10-business/README.md)

## 原生不是给通用CRUD换一个名字

`vendor.py` 根据manifest核对三个源码归档：FastapiAdmin、芋道后端、Vben前端。它们保留固定提交和许可证，解压复用也要重新核对源码身份。普通克隆已经带归档；从只有教材的空目录恢复时，要使用书中的完整重建路径，从指定公开提交重建归档，不能拿主分支最新ZIP代替。上游源码不是你自行实现的文件，教材应当清楚区分“重建上游快照”与“手写自有适配器”。

`native.py` 知道各模板的固定来源与生成接口；`native_modules.py` 把已批准实体转成适合框架的数据库表和真实代码生成请求，再将导出文件装进原框架。FastapiAdmin继续使用自己的认证、模块、Vue管理端；芋道继续使用Java后端、菜单权限和Vben界面。字段和表名还要适配框架保留列、序列与逻辑删除约定，不能把Python Basic文件复制过去宣称原生。

`native_environment.py` 准备本次后端与本机数据库连接，`native_frontend.py` 负责真实依赖、类型检查、构建与预览，`owned_lifecycle.py` 追踪本次启动的进程与端口。`native_style.py` 同时检查原生布局/主题指纹和生成页面组件。`native_lab.py` 组合这些真实操作，`native_recovery.py` 只在源码、Plan、数据库身份一致且明确可恢复的阶段继续；任意硬杀后的未知状态并不自动安全。

## 固定源码去哪里取得，怎样处理

本教材使用下列准确来源，提交号同时保存在 `scripts/vendor_templates.py` 和 `templates/vendor/manifest.json`，不是让读者任选最新版本：

- [FastapiAdmin固定源码](https://github.com/fastapiadmin/FastapiAdmin/tree/1cd12c726ad9032c17ef85ce805ce991be60fbdf)：`1cd12c726ad9032c17ef85ce805ce991be60fbdf`
- [芋道Cloud Mini固定后端](https://github.com/yudaocode/yudao-cloud-mini/tree/47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be)：`47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be`
- [芋道Vben固定前端](https://github.com/yudaocode/yudao-ui-admin-vben/tree/1b14e889f529e245fd620daa720dcea6de0cc5e7)：`1b14e889f529e245fd620daa720dcea6de0cc5e7`

推荐使用下一节的 `vendor_templates --fetch`：脚本为每份上游建立临时Git目录，只fetch指定SHA、detached checkout，再核对 `rev-parse HEAD` 完全相同。若你自己取得了上述固定版本的源文件，把三个根目录分别命名为 `fastapiadmin`、`yudao-backend`、`yudao-frontend` 放在同一个 `upstream-sources` 目录中，先核对来源和LICENSE，然后可用 `uv run python -m scripts.vendor_templates --source-root upstream-sources`。这个离线目录入口只打包你提供的文件，不能替你证明它们来自哪个提交；你必须保留获取记录并比对教材的固定来源摘要。

打包不是压缩整台开发机。脚本排除 `.git`、`.venv`、node_modules、缓存、target、dist、logs、实际 `.env`、数据库、私钥和字体二进制；保留源码、迁移、依赖锁和LICENSE。遇到符号链接、异常大文件或许可证不符就停止。输出三个普通ZIP、三份LICENSE及manifest，其中有文件数、排除清单、归档SHA与按文件hash汇总的source_digest。

`vendor.unpack_source` 先验归档SHA，再限制解压路径、重复条目、链接、敏感文件与大小，最后重新计算解压后source_digest。只有全部成立才发布本机源码目录。这个双层检查把“传输压缩包有没有变”和“真正源码有没有变”分开；下方pytest正是在验证这些事实。

## 先过快照和环境边界

原生层与独立交付帮助模块有顶层 `psycopg` 导入，开始这一层前安装额外依赖：

```bash
# .learning/commands/09-native-install.sh
uv sync --locked --extra postgres
uv run python -m scripts.vendor_templates --fetch
uv run pytest tests/test_vendor.py tests/test_native_archive_limits.py tests/test_native_delivery_boundaries.py -q
uv run rnd init
```

从空目录还原时没有预带第三方ZIP，上面的 `vendor_templates --fetch` 会用Git获取固定公开提交并重建三个归档；普通克隆且归档已核验存在时可略过这一重建步骤。该命令不是获取最新主分支，不跳过来源和解压后源码摘要校验。压缩库版本可能使ZIP压缩字节不同，因此重建后以脚本生成的新归档hash配合固定commit/解压源码摘要记录，不混用旧压缩hash。测试应无failed/error；`rnd init` 应创建本机状态、令牌并从已具备的归档解压模板，不覆盖已有 `.env`。这个命令完成不代表PostgreSQL、Redis、Java或Vue已经运行。

### 重打包后，分阶段还原为什么可能暂停

固定提交和解压后的源码摘要相同，也不保证不同zlib版本产出的ZIP压缩字节完全相同。此时变化的是 `templates/vendor/manifest.json` 中的 `archive_sha256`，脚本必须把它更新为你本机真实归档的摘要；固定commit、source_digest和文件数仍应与教材一致。若这些来源字段也不同，应先停止调查，不能把它解释成压缩差异。

可选的 `--advance` 对已经还原的文件逐字节检查，因此这个正常的重打包变化也会触发保护，拒绝推进。这不代表模板源码丢失，也不是让你改掉校验。不要删除 `.learning-progress.json`、伪造其中的哈希，或把旧manifest强行盖回去：旧归档哈希可能与本机新ZIP不符。

推荐改用“完整空目录还原后继续学习”路线。保留原 `student-project` 及其中的源码修改、状态、数据库和报告；不删除、不覆盖、不把它当作新项目的代码来源。在同时放着教材和原项目的父目录运行下列命令；新名字 `student-project-complete` 必须尚不存在或为空。若你原项目叫别的名字，先在终端确认当前位置再操作。

```bash
# .learning/commands/09-repack-continue.sh
uv run --no-project --python 3.14 python learning-docs/rebuild.py student-project-complete
cd student-project-complete
uv sync --locked --all-extras
uv run python -m scripts.vendor_templates --fetch
```

Windows PowerShell也可执行以上四行。这里一次性取得完整自有代码，之后不再对这个新目录使用 `--advance`；仍按第10站以后的教学顺序阅读、练习和验收。按第06站在新目录安装浏览器并重新设置其绝对模块路径，按第11站安装/构建Node工具，再运行需要它们的检查。原生实验继续遵守专用空数据库要求，不能为了复用已初始化的旧库而删除数据。最后按第14站从本机实际模板清单重新生成两套教材并检查一致性。

手写路线本来就不需要进度账本；也可以保留当前目录、按后续完整源码页手写新文件。无论选哪条路，哈希保护都保持严格，不把“还原完成”当作依赖和服务已经准备完成。

FastapiAdmin使用pnpm9.15.3，芋道Vben使用pnpm11.16.0；不要在同一全局安装中含糊地说“有pnpm即可”。两者需要Node22和本机PG/Redis，芋道还需要JDK17与Maven。按下一节的完整本机步骤准备专用 `*_codegen` 数据库。拒绝非空库时先检查归属，不能用DROP整库来让下一条命令变绿。

## 从Ubuntu/WSL准备原生运行环境

以下命令是Ubuntu x86_64的Bash，不是PowerShell。Windows先按 [Docker Desktop官方Windows安装说明](https://docs.docker.com/desktop/setup/install/windows-install/) 安装、启动Docker Desktop，自行阅读并决定接受许可条款，在Resources → WSL Integration启用你使用的Ubuntu；不要在同一个发行版里同时另装一套冲突Engine。工作目录放在WSL的Linux文件系统，重新安装Linux `.venv`，不能复用Windows的虚拟环境。

已有Docker的读者先运行 `docker version`、`docker compose version`，前者必须同时显示Client和Server。尚未安装Docker的干净Ubuntu主机，可按 [Docker官方Ubuntu安装文档](https://docs.docker.com/engine/install/ubuntu/) 配置来源。下面仅适用于没有既有容器环境的受支持Ubuntu；有冲突包、现存服务或组织限制时先处理兼容性，不自动卸载别人的软件：

```bash
# .learning/commands/09-docker-ubuntu.sh
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

后续平台由普通用户运行。如果只有sudo能访问Docker，先阅读 [Docker安装后权限说明](https://docs.docker.com/engine/install/linux-postinstall/) 并决定是否赋予本机开发账户Docker组权限；该组近似root权限，不是一个无风险修复。不要把socket chmod成666，也不要开启公网Docker TCP端口。平台不代替你更改权限；正常用户 `docker version` 成功后才继续。

芋道需要JDK17/Maven，FastapiAdmin可不安装这两项。Ubuntu准备命令如下，`mvn -version` 中显示的Java也必须为17；机器有多个JDK时先正确选择JAVA_HOME，不能只看另一个终端的 `java -version`：

```bash
# .learning/commands/09-native-language-tools.sh
sudo apt-get update
sudo apt-get install -y git curl ca-certificates xz-utils openjdk-17-jdk maven
java -version
mvn -version
```

原生Vben要求Node22.18或更新的22.x，比第11站Continue的最低22.13更严格。第06站若装了更早22.x，现在升级到满足原生要求的22.x。Ubuntu x86_64可安装固定官方用户目录二进制；下面不修改系统Node，不把哈希检查删掉：

```bash
# .learning/commands/09-node-linux.sh
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

预期SHA检查为OK、Node为v22.18.0。ARM机器不能执行这个x64命令，应从官方页面取匹配架构；Daytona本教程明确只验Linux x86_64/WSL2 x86_64。重新打开终端后重设PATH，回到你的 `student-project` 根目录；不要在 `~/.local/share/rnd-tools` 安装平台依赖。Vben完整构建较重，预留足够磁盘与内存；失败时保留构建日志，不删除原生业务页面来缩减构建。

## 建立只属于实验的PostgreSQL与Redis

真实平台也能为获准运行自动创建独立Compose服务。为了理解原生CI脚本，下面显式创建实验服务。先确认 `rnd-learning-pg`、`rnd-learning-redis` 名称和本机5432/6379端口未被别的服务占用；有冲突先调查，不能强制删除。密码用随机值留在当前终端，不贴聊天或提交Git。

```bash
# .learning/commands/09-owned-services.sh
export NATIVE_PG_PASSWORD="$(uv run python -c 'import secrets; print(secrets.token_urlsafe(24))')"
docker run -d --name rnd-learning-pg \
  -e POSTGRES_USER=native -e POSTGRES_PASSWORD="$NATIVE_PG_PASSWORD" \
  -e POSTGRES_DB=fastapi_codegen -v rnd-learning-pg-data:/var/lib/postgresql/data \
  -p 127.0.0.1:5432:5432 postgres:17
docker run -d --name rnd-learning-redis -p 127.0.0.1:6379:6379 redis:7.4-alpine
docker exec rnd-learning-pg pg_isready -U native -d fastapi_codegen
docker exec rnd-learning-redis redis-cli ping
```

PG初始化可能需要几秒，尚未接受连接就稍后重跑 `pg_isready`，不要重发 `docker run`。成功分别看到accepting connections和PONG。容器内的实验native账户有创建独立验收新库所需权限；只用于这次回环开发服务。用你自己的现有PG账号时，需要先由拥有者明确提供专用空库和必要CREATEDB权限，不能自行扩大生产账号权限。

为两个框架选择各自pnpm版本；下面将npm全局工具放在自己用户目录，避免sudo安装。首先跑FastapiAdmin：

```bash
# .learning/commands/09-fastapi-native-runtime.sh
export PATH="$HOME/.local/share/rnd-tools/npm-global/bin:$PATH"
npm install --global --prefix "$HOME/.local/share/rnd-tools/npm-global" pnpm@9.15.3
pnpm --version
export NATIVE_TEST_DATABASE_URL="postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/fastapi_codegen"
uv run python -m scripts.ci_native_bundled fastapiadmin
```

本条是标准原生CRUD与独立新库验收，使用公开确定性规格，不调用真实模型。浏览器环境变量仍要延续第06站。成功后在 `reports/native` 阅读完整报告，而不是只看到生成ZIP。默认产物位于 `.native/product`。在全部测试进程退出后，将本次产物和报告移动保留，再准备另一个空库；不要让第二个模板覆盖第一个的证据：

```bash
# .learning/commands/09-preserve-first-native-run.sh
mkdir -p .native/completed/fastapiadmin
mv .native/product .native/completed/fastapiadmin/product
mv reports/native .native/completed/fastapiadmin/reports
docker exec rnd-learning-pg createdb -U native yudao_codegen
npm install --global --prefix "$HOME/.local/share/rnd-tools/npm-global" pnpm@11.16.0
pnpm --version
export NATIVE_TEST_DATABASE_URL="postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/yudao_codegen"
uv run python -m scripts.ci_native_bundled yudao-vben
```

若目标保留目录或yudao_codegen已存在，停下来核对前一次实验，不靠覆盖/清库继续。两次pnpm版本输出应分别为9.15.3、11.16.0；第二条运行还要求Java17/Maven已经通过版本检查。这里先验原生基本能力；第10站客服测试要另建自己的空库和无冲突输出，不能在已经初始化过的库上重跑生成器。完成学习后可由你明确停止自己创建的两个容器，保留持久卷和报告；不要执行删除全部Docker资源的清理命令。

## 分开记录源码导出与运行通过

`SOURCE_READY` 只表示源码导出，不表示编译、权限、浏览器或独立新库部署通过。全运行前再次核对实际环境；下一站完成客服适配后，可分别执行下列标准客服矩阵命令：

```bash
# .learning/commands/09-native-customer-runtime.sh
uv run python -m scripts.ci_native_bundled fastapiadmin --spec examples/plans/customer-service.json
uv run python -m scripts.ci_native_bundled yudao-vben --spec examples/plans/customer-service.json
```

这里明确是“第10站业务文件齐全后回到这里执行”；执行前在本节实验PG中另建新的专用空_codegen库，并像上面一样以当前终端随机密码设置 `NATIVE_TEST_DATABASE_URL`，保留前次 `.native/product` 和报告；不要直接在书中写真实密码。每次只认本模板本次报告，先保存或分目录留存再跑另一模板，避免覆盖证据。合同测试只证明适配器拒绝/接受给定输入，真实原生通过要看编译、类型检查、HTTP、浏览器和独立新库部署。

## 先检查可选依赖，后产生原生副作用

基础Windows环境可以选择原生模板、读取能力和到达设计关卡，即使没有psycopg；这不表示Windows已支持原生执行。真正运行在WSL2/Linux进行，并在其项目目录安装：

```bash
# .learning/commands/09-postgres-extra.sh
uv sync --locked --extra postgres
uv run python -c "import psycopg; print('PostgreSQL driver import PASS')"
```

`native_delivery.prerequisites` 在加载实际 `native_lab` 执行入口前检查系统、驱动和必需命令。缺少驱动给出上面的安装命令和“重试同一运行”提示；必须在创建目标目录、Compose服务、复制代码和连接数据库之前停止。不要把try/except包住真实数据库失败后继续生成，也不要移除平台检查来让Windows误入Linux工具链。

旧的 `FAILED` 运行补齐条件后从同一UUID恢复，继续使用历史需求、审批和检查点。若原目标曾被错误改成管理员代录，先完成第07/08站的能力范围澄清，再执行原生生成；依赖修好不等于旧设计已经获得新的有效批准。

## 本阶段源码和后续依赖

本阶段首次创建 66 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
