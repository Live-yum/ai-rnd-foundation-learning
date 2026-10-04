# 12 · 本机沙箱与镜像

[总目录](../README.md) · [上一阶段](../11-local-tools/README.md) · [下一阶段](../13-delivery/README.md)

## 先让本机产品跑通，再隔离它

沙箱不是修补不可运行项目的魔法。平台先做本机可信验证，Daytona再增加一层本机自托管执行证据。`sandbox.py` 校验配置和profile，打包受控源码与验收harness，创建本次命名的沙箱，传入不含主机模型Key和主机数据库密码的必要材料，再读回有大小与身份限制的报告。`daytona_worker.py` 在专门子进程内施加回环工具约束，不能把它描述为抵抗任意恶意代码的操作系统隔离。

`daytona_profiles.py` 按模板/数据库决定快照与必须的检查项目：Python/SQLite、Python/PostgreSQL、FastapiAdmin/PostgreSQL、Yudao/PostgreSQL各有真实依赖。数据库和Redis在适用沙箱内初始化，不把主机的正式库连接串复制进去。源码hash、锁文件身份与镜像回执串起来，才能知道这份环境究竟验了哪个产品。

`daytona_sessions.py` 对长运行使用一个异步命令提交，后续短GET轮询，最后读日志。请求超时不证明服务器没执行，因此不能重发一个可能已成功的POST来“再试一次”。输出目录保护和总预算同样保留；状态pending时不允许写passed。

## 严格按顺序准备固定版本

这是较重的可选能力，只在你确实准备好Linux/WSL、Docker及本机资源后执行。若尚未安装浏览器、Node工具、Aider和基础产品依赖，先回前面章节。

```bash
# .learning/commands/12-daytona-prepare.sh
uv sync --locked --all-extras
uv run python -m scripts.daytona_local prepare
uv run python -m scripts.daytona_local images
uv run python -m scripts.daytona_local snapshot-image
uv run python -m scripts.daytona_local up
uv run python -m scripts.daytona_bootstrap auth
uv run python -m scripts.daytona_bootstrap snapshot
uv run python -m scripts.ci_daytona_local
mkdir -p reports/daytona-python-sqlite
cp .data/daytona-local/snapshot-image.json reports/daytona-python-sqlite/snapshot-image.json
cp reports/daytona-local.json reports/daytona-python-sqlite/daytona-local.json
```

每一步退出码为0并得到对应回执后才执行下一步。prepare固定上游并写本机配置；images构建固定控制面与Runner；snapshot-image预热基础离线执行环境；up启动本机服务；auth建立本机认证；snapshot登记可运行快照。最后验收才说明业务和工具实际执行。CLI存在、API健康、快照active、产品通过和沙箱删除是五个不同事实。

`.data/daytona-local` 含本机随机凭据和状态，不进入Git或交付ZIP。服务端口只绑定回环，内部服务网络和Runner网络按脚本分开；不要为了排错把它暴露到公网。安装阶段下载公共依赖与运行阶段外联业务工具是不同事件。

## 三个PostgreSQL profile逐个做，不猜参数

下列命令来自实际 `ci_daytona_matrix`、`daytona_matrix_image`、`ci_native_tools` 的参数定义。先完成本节基础Daytona服务，且第09站PG/Redis、第11站Aider/Node/浏览器仍可用。每次只做一个profile，并在切换前保留报告；`.data/daytona-local/snapshot-image.json` 会被最新镜像覆盖，不能最后才回头猜前面快照名。

### A. Python/PostgreSQL

它使用明确的确定性新闻CRUD规格检查数据库型别，不冒充客服业务矩阵或真实模型。

```bash
# .learning/commands/12-python-postgres-matrix.sh
uv run python -m scripts.ci_daytona_matrix prepare-basic python-basic --product .native/daytona-python-pg
uv run python -m scripts.daytona_matrix_image python-basic --database postgresql --product .native/daytona-python-pg
uv run python -m scripts.daytona_bootstrap snapshot
uv run python -m scripts.ci_daytona_matrix verify python-basic --product .native/daytona-python-pg
mkdir -p reports/daytona-python-pg
cp .data/daytona-local/snapshot-image.json reports/daytona-python-pg/snapshot-image.json
cp reports/daytona-matrix.json reports/daytona-python-pg/daytona-matrix.json
```

首次prepare要求目标尚不存在；反复执行时遇到保护要核对原生成回执，不能删数据库来“刷新”。build步骤过滤产品文件、预热锁定依赖，推送本机registry并写不可变image_id；snapshot确认已登记的同名快照来源一致且active后，更新本机 `workbench.env`。verify从该配置读取准确快照名，要求passed、cleanup=deleted、host_credentials_used=false、host_database_used=false。

### B. FastapiAdmin/PostgreSQL

先在第09站实验PG创建一个新的专用空库，不能用已经完成客服或原生生成的库。这里沿用当前终端的 `NATIVE_PG_PASSWORD`；若你换了终端，先从自己的安全保存处恢复它，不把密码打印进日志。

```bash
# .learning/commands/12-fastapiadmin-matrix.sh
docker exec rnd-learning-pg createdb -U native fastapi_tools_codegen
export NATIVE_TEST_DATABASE_URL="postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/fastapi_tools_codegen"
export PATH="$HOME/.local/share/rnd-tools/npm-global/bin:$PATH"
npm install --global --prefix "$HOME/.local/share/rnd-tools/npm-global" pnpm@9.15.3
uv run python -m scripts.ci_native_tools fastapiadmin --output .native/daytona-fastapiadmin
uv run python -m scripts.daytona_matrix_image fastapiadmin --database postgresql --product .native/daytona-fastapiadmin
uv run python -m scripts.daytona_bootstrap snapshot
uv run python -m scripts.ci_daytona_matrix verify fastapiadmin --product .native/daytona-fastapiadmin
mkdir -p reports/daytona-fastapiadmin
cp .data/daytona-local/snapshot-image.json reports/daytona-fastapiadmin/snapshot-image.json
cp reports/daytona-matrix.json reports/daytona-fastapiadmin/daytona-matrix.json
mv reports/native-tools reports/daytona-fastapiadmin/native-tools
```

`ci_native_tools` 先用真实原生生成器产出模块，故意中断后恢复，再用显式测试模型给出错误规则、验证真实反例失败与回滚、下一轮修复，再做后端、前端、浏览器和独立新库验收。它成功后才能拿输出目录制作快照。只运行daytona_matrix_image不包含这部分原生编辑链证明。

### C. Yudao/PostgreSQL

保留上一profile报告后，再准备Java17/Maven、pnpm11.16.0与另一个新空库；不得把FastapiAdmin产品目录当作Vben源：

```bash
# .learning/commands/12-yudao-matrix.sh
docker exec rnd-learning-pg createdb -U native yudao_tools_codegen
export NATIVE_TEST_DATABASE_URL="postgresql+psycopg://native:${NATIVE_PG_PASSWORD}@127.0.0.1:5432/yudao_tools_codegen"
npm install --global --prefix "$HOME/.local/share/rnd-tools/npm-global" pnpm@11.16.0
java -version
mvn -version
uv run python -m scripts.ci_native_tools yudao-vben --output .native/daytona-yudao
uv run python -m scripts.daytona_matrix_image yudao-vben --database postgresql --product .native/daytona-yudao
uv run python -m scripts.daytona_bootstrap snapshot
uv run python -m scripts.ci_daytona_matrix verify yudao-vben --product .native/daytona-yudao
mkdir -p reports/daytona-yudao
cp .data/daytona-local/snapshot-image.json reports/daytona-yudao/snapshot-image.json
cp reports/daytona-matrix.json reports/daytona-yudao/daytona-matrix.json
mv reports/native-tools reports/daytona-yudao/native-tools
```

每条命令成功后再向下执行，不能把失败命令与后续命令一起粘贴后只看最后的cp。脚本给Yudao快照登记10GiB内存、30GiB磁盘，基础/FA的PG profile使用4GiB内存、30GiB磁盘；主机还要承担控制面和构建，因此实际主机需要更多可用资源。内存不足先增加你明确控制的本机资源或调整实验安排，不省略类型检查、权限测试和浏览器。

### 把多个已通过快照接回日常平台

上面的单profile验收会由bootstrap自动把当前准确快照写到 `.data/daytona-local/workbench.env`。日常平台的 `.env` 与这份工具配置不是同一文件；不要直接覆盖 `.env` 而丢掉模型配置。将本机Daytona连接配置私下合并到现有 `.env`，其中Key只留本机；多profile名称分别读取已保留的snapshot-image.json的snapshot字段。下面是需要编辑的字段说明，不是可原样执行的虚假名称：

```dotenv
# .env
SANDBOX_PROVIDER=daytona
DAYTONA_ALLOW_LOCAL_EXECUTION=true
DAYTONA_API_URL=http://127.0.0.1:3000/api
DAYTONA_TARGET=local
DAYTONA_RUNTIME_TIMEOUT=3600
DAYTONA_SNAPSHOTS={"python-basic/postgresql":"替换为Python-PG回执snapshot","fastapiadmin/postgresql":"替换为FastapiAdmin回执snapshot","yudao-vben/postgresql":"替换为Yudao回执snapshot"}
```

SQLite基础profile继续使用前面基础回执的 `DAYTONA_SNAPSHOT`；也需保留其准确名字。确认没有占位词后重启平台。镜像source_hash受锁文件和Docker构建输入约束；源码变化不一定改变依赖快照身份，但每次上传与运行仍需绑定新源码hash。缺依赖时显式重建对应镜像，不运行时放开外网。

## 复杂模板单独预热，失败后保留证据

基础镜像并不包含Java/Vue完整原生环境。先根据本次实际生成目录，通过 `daytona_matrix_image.py` 等本阶段完整脚本预热各profile，将快照回执中的准确名称填入 `DAYTONA_SNAPSHOTS`。不要自行猜快照名，不把Python镜像改名当作Yudao镜像，也不在缺依赖时开放运行期网络。

需要诊断时显式开启 `DAYTONA_CAPTURE_STARTUP_DIAGNOSTICS`。诊断仅限本次已确认身份的沙箱、限定日志尾部与时间预算、先脱敏，再继续原清理路径。即使日志采集成功，创建超时或业务失败也仍然失败。最后确认应用端口关闭、重启检查成立、沙箱删除成功；清理失败是交付阻塞，不是可忽略的收尾。

```bash
# .learning/commands/12-daytona-contracts.sh
uv run pytest tests/test_daytona_snapshot.py tests/test_daytona_sessions.py tests/test_daytona_startup_diagnostics.py tests/test_daytona_matrix.py -q
```

这些合同与反例测试可以在没有完整服务时解释边界，不能代替上面的真实自托管运行，更不能代替三行原生/PG矩阵。最终报告按每种profile逐项写passed、failed或未运行。

## 本阶段源码和后续依赖

本阶段首次创建 41 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
