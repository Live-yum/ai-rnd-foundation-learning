# 自定义源码执行：有证据的启用门

规划和生成候选不意味着已经通过运行验收。缺少隔离环境时，保留原需求、所选技术栈、
候选源码和任务进度，只暂停执行，不把功能删除或改成另一套模板。

## 控制端配置

`CAPABILITY_EXECUTION_ENABLED` 默认 false。显式启用仍不能绕过安全验收。
`CAPABILITY_PROFILE_DIRECTORY` 默认是项目的 `.data/daytona-capability`；它是控制端
安装配置，不能从模型 Plan 取得，不能指向某个生成运行的目录。

先按已有本机 Daytona 文档构建独立 capability profile。运行
`uv run python -m scripts.ci_capability_security`，只有真实独立服务、正向产品、
安全反例和清理全部成功，才会写出该安装专用的 `capability-security-acceptance.json`。
回执精确绑定当前验证器/守卫/探针源码、Runner、快照 ID 和镜像摘要。
旧文件、模拟通过、普通固定应用回执、镜像或代码漂移均不能启用。
发生失败时先失效旧回执；修复后重新验收。不会自动修改宿主防火墙、sysctl 或 Docker 策略。

执行资格按栈单独签发：python-basic/SQLite 与 FastapiAdmin/PostgreSQL 有不同快照、
资源预算和回执。原生 profile 先通过 `scripts.daytona_native_capability_profile prepare`
和 `register` 构建/登记精确离线依赖，再运行 `scripts.ci_native_capability_security`。
Yudao 的候选保留原生栈，等待对应 profile；不能借用 SQLite 成功回执。
代码里有入口、单元测试通过都不等于获得执行资格。真实 CI 尚未通过时仍然默认关闭。
这里没有声称已经完成全部竞赛业务或真实模型代码生成验收。

### 固定上游的摘要引用修复

Daytona v0.190.0 的固定源码 `01c502bb1f1ff8f2885d0cd490e043736083dca8`
存在一处 API 引用重组错误：SDK 的 `imageName` 和 API 快照记录保留
`registry:6000/repository@sha256:…`，但 SnapshotManager 调用的
`DockerImage.getFullName()` 把摘要前的 `@` 重组成 `:`，使 Runner 的
`INSPECT_SNAPSHOT_IN_REGISTRY` 收到非法 `repository:sha256:…`。
上游位置是 [docker-image.util.ts](https://github.com/daytonaio/daytona/blob/01c502bb1f1ff8f2885d0cd490e043736083dca8/apps/api/src/common/utils/docker-image.util.ts)。

`scripts.daytona_build` 只在干净导出的 API 构建上下文应用
`tools/daytona/api-digest-reference.patch`：SHA-256 摘要使用 `@`，普通标签仍使用
`:`。先核对固定版本、源码 Git blob `b0b03b28ce08b2865db9d2dc291c1745cb6492cf`
和完整补丁字节，任何漂移直接停止；不修改上游工作树、SDK 参数、Runner 或网络设置。
API 镜像标签及 `images.lock.json` 的 `source_patch` 记录补丁与修改后文件的 SHA-256，
实际镜像 ID 继续固定在 Compose 中。本机 Compose 启动与 capability 基础配置准入前，
共享检查器要求锁内含完整、精确的当前补丁来源，并按不可变 API 镜像 ID 检查实际 ID
和版本、源码、补丁标签；旧锁、缺字段、篡改值或标签漂移均拒绝。需要按原安装流程
重新构建 API，不能靠重新登记同一个已失败快照假装完成恢复。
该来源检查也适用于 Compose 诊断和关闭子命令；本补丁不会自动迁移或关闭旧安装。
应在升级前完成原有清理，验收使用新的空目录。

`tests/test_daytona_api_digest.py` 直接执行固定上游 TypeScript 文件，覆盖摘要往返、
带端口仓库、多层命名空间、普通标签、无标签和原有非法摘要拒绝行为；原生登记测试
经真实固定 SDK 的 HTTP JSON 序列化检查 `imageName` 字节。注册仍只接受原先绑定的
不可变摘要、镜像 ID、依赖清单、active 状态和精确资源预算，不提供可变标签回退。
这些回归不等于真实注册或运行时隔离通过；仍须完整 profile CI 的实际证据。

## 每个候选都重新验证

普通固定应用 CI 保留原来的容器重启测试。`rnd-source-*` 专用候选容器由固定 Runner
补丁提供 1 GiB `/tmp` tmpfs 和 PID 上限；控制端读取真实容器 CPU、内存、swap、PID、
tmpfs、非特权、seccomp、只读挂载、私有及禁网状态。应用身份运行的独立探针再次核对
实际 cgroup v2 与 tmpfs 容量，而不是相信模型写出的数字。

候选使用独立 UID 20000、清空附加组和 capabilities、no_new_privs、分离终端和标准流。
Landlock ABI 6+ 把写入限定到 tmpfs 内的产品、HOME、临时和缓存目录；源码不能写控制
回执、守卫、系统解释器或私有数据库目录，不能通过继承 FD、符号链接或 `/proc` 绕过。
依赖从已登记的只读镜像读取，临时区域只保存运行数据和必要缓存。缺失内核能力直接失败，不回退到宿主执行。

候选还通过系统 libseccomp 2.x（最低 2.5）的独立进程过滤器：只允许 Unix/TCP stream
socket，禁止其他网络域、DGRAM/RAW/SEQPACKET（含类型标志组合）、非 Unix socketpair
及 io_uring 旁路。当前 SQLite profile 禁止所有 connect，既不允许外网，也不允许
同端口的其他地址；允许接收控制端对产品的入站请求。原生 PostgreSQL profile 只准连接约定的本机后端、PG 和 Redis 端口；每次执行另外
创建短期、只读、无宿主端口的同桥测试对端，确认可信控制端可连接而应用连接被拒绝，
覆盖同端口的 IPv4 和 IPv4-mapped IPv6 地址。允许 TCP 端口本身不算地址隔离证据。
库、CPU 架构或 ABI 不匹配也会失败。

子进程另有限制：CPU 300 秒、单文件/日志 32 MiB、128 个进程、256 个文件描述符、
禁用 core dump；整体验收仍受原总时限约束。达到限制属于失败，不放宽限制补成功。

## 只读依赖与完整源码绑定

专用容器的 `/tmp` 保留 `noexec`。Python 原生扩展及前端工具预装在镜像的
`/opt/rnd/runtime`，不能在临时目录安装或复制可执行依赖来绕过该保护。原始
`pyproject.toml`、`uv.lock`、`package.json` 与前端锁文件保持精确摘要绑定；不删除锁内
依赖，也不把镜像预装记录成运行时离线安装成功。

确需编译的固定第三方依赖在无凭据、非 root、禁网的独立构建阶段处理，输入与产物
均校验摘要。运行前后核对完整文件、目录、权限及链接图，绑定实际镜像 ID、依赖清单
和本次源码清单。额外模块、描述符漂移、硬链接、越界或被替换的符号链接都必须失败。
候选自身的构建脚本不能成为具有特权的镜像构建输入。

镜像安装使用 `uv pip sync` 的位置参数传入带哈希的锁定requirements文件；`-r` 只用于
相应的 `pip install` 命令。两个profile在长镜像构建前先执行真实uv解析和离线轮包
dry-run回归，确保basic、native与harness路径均匹配实际CLI，而非仅检查命令字符串。

产物收集直接读取已绑定的只读 `python-build` 解释器身份，不再让 `uv python find`
隐式初始化root缓存。Python、uv、Node、系统包、Rust、C编译器和pnpm的版本探针统一
使用非root受限环境、全新临时cwd/HOME、离线配置及60秒预算；Python显式使用`-B`，
避免`-I`忽略环境变量后产生字节码写入。不会放宽根缓存或工具目录权限。禁配置只作用于
身份探针，原始构建/安装的锁文件、default-groups与extras选择语义保持不变。

SQLite 数据库只允许独立非源码子目录中的 `.db`、`.sqlite` 或 `.sqlite3` 文件，不能
把 Python 模块、原生库或源码目录声明为可写数据库。应用重启前后仍验证完整源码与
依赖绑定。前端只开放必要构建输出与缓存，不开放整个依赖目录写权限。

这些实现与负例测试不代表真实容器已经验收通过。只有同一准确提交的独立 profile
流程完成健康检查、功能、安全反例、重启、资源边界和清理，才可签发执行资格。

## 重启和证明的准确含义

tmpfs 随容器停止清空。因此候选 profile 记录的是 `restart_kind=application_process`：
可信控制端只终止本沙箱专用 UID 的进程，确认旧应用端口关闭，重验安全边界后再启动；
检查数据仍可从实际数据库读取。这不证明容器、宿主或断电后的持久化，后者须由独立
交付恢复测试证明。不会把旧进程仍在服务解释为重启成功。

安全验收使用明确固定的正向小应用和可信攻击探针，不使用付费模型，不能证明 AI
实现了全部业务。真正的业务完成仍需当前候选的独立功能、权限、浏览器、数据和恢复
证据。候选自写的 JSON、报告或模型审阅意见不能覆盖任何失败检查。

## 验证与来源

- `tests/test_capability_execution_gate.py` 包含 admission/资源负例及真实子进程
  libseccomp、Landlock 检查。缺内核能力在一般开发机明确 skip；独立 profile CI 设置
  `RND_REQUIRE_LANDLOCK=1` 后必须真实通过，不允许用 skip 代替。
- `.github/workflows/capability-profile.yml` 的真实 Docker/Daytona/HTTP/浏览器流程才是
  完整安全验收入口。单元模拟不签发 live 回执。
- [固定 Daytona Runner 源码](https://github.com/daytonaio/daytona/blob/01c502bb1f1ff8f2885d0cd490e043736083dca8/apps/runner/pkg/docker/container_configs.go)
  与仓库中的精确补丁一同按原始 Git blob 校验，保留上游许可和完整构建来源。
- [libseccomp 规则 API](https://man7.org/linux/man-pages/man3/seccomp_rule_add.3.html)、
  [初始化/加载说明](https://man7.org/linux/man-pages/man3/seccomp_init.3.html) 和
  [固定 ABI 头文件](https://github.com/seccomp/libseccomp/blob/v2.5.5/include/seccomp.h.in)
  是过滤器接线依据；这里使用操作系统库，未另造云端执行服务。

## 原生环境与独立业务验收

原生快照运行真正的 FastapiAdmin `app:create_app --factory`、Vue 构建/类型检查、
独立 PG17 和 Redis。候选容器预算为 CPU2、内存6GiB、PID384、4GiB tmpfs。
数据库管理员只通过私有 peer socket 处理固定目录/集群身份和临时库生命周期；候选表的
数据读取使用独立实际认证的只读 `rnd_verify`，不是在管理员会话中 SET ROLE。验证凭据
只留在控制端私有文件中，应用不能取得；同时限制查询时间、输出、RLS和索引计划路径。
应用角色不能管理角色、其他数据库、
服务器文件或外部程序。Redis 是本沙箱专用实例/DB0；应用不能管理 ACL、配置、复制、
清空全库或切换数据库，不声称适用于已有混合业务的 Redis 实例。

浏览器也执行候选 JavaScript，因此自定义源码不能走宿主浏览器。它使用单独的无网络、
只读根、CPU/内存/PID/tmpfs 有界容器，通过有界标准流 relay 访问唯一私有预览。
应用回执绑定精确浏览器镜像；同一 CI job 必须通过真实出口、只读、PID耗尽、OOM、
正向交互和清理证明。默认 Docker seccomp 下 Chromium 沙箱若无法启动，阻止执行；
不会使用 `--no-sandbox` 或修改宿主安全设置。准备的上游 seccomp 参考文件未启用。

`.github/workflows/native-capability-profile.yml` 还运行明确人工编写的竞赛业务样例，
独立 oracle 检查队伍容量竞争、邀请码过期/撤销/重试、盲审字段、越权拒绝与 PG 实体行。
它只证明这个有界样例，不能当成真实模型编写源码，也不能把剩余加权评分、随机分配、
跨校报名、文件存储、邮件短信和导出等自动标为已完成。

新库重放只重建本次沙箱的临时 `rnd_product`：先确认应用 UID 没有存活线程，核对
控制端保存的沙箱 ID、PG 集群标识、数据目录和原 OID；重建后确认同集群的新 OID、
空业务表，再重放请求。没有使用用户数据库或候选指定的连接配置。

### CI 的已验证纯源码交接

原生工具链的构建目录会保留 `.venv` 和 `node_modules`，不能直接作为候选输入。
CI 使用 `ci_native_tools --capability-source .native/capability-source`：现有独立交付
ZIP 完成完整源码清单往返校验后、其解压副本启动或安装依赖前，捕获另一个全新的纯源码
副本。原构建目录保持原样；这不是对收到的候选目录静默过滤依赖。

交接检查逐项核对真实文件集合与 SHA-256，拒绝链接、硬链接、非普通文件、额外目录、
依赖目录及路径冲突；复制使用 no-follow 文件描述符和排他创建。回执绑定捕获时的 ZIP
摘要、完整清单、全部十一个描述符及其用途与 CI head/run/attempt，只有整套原生工具链验收成功后
才发布成功状态。缺少平台所需的安全文件接口时直接拒绝，不退回跟随链接的复制。

固定 FastapiAdmin 原产品还包含移动端和文档源码，不能为了凑齐旧的六项假设删除它们。
描述符按精确路径分为 runtime 四项（backend 与 frontend/web）、portable_launcher 两项
（deployment）和 auxiliary_source 五项（frontend/app、其 mp-html 子模块及 frontend/docs）。
完整十一项的哈希和角色都被绑定；任何多项、缺项、替换、角色变化或内容漂移都拒绝。

七项非运行描述符只以有界规范 base64 作为构建输入数据，核验字节、原始与规范化哈希后
移除传输内容，仅将哈希和角色纳入不可变镜像清单及回执。它们不增加安装根、依赖包或
运行入口；安装仍限于原有 backend、frontend/web 与独立可信 harness。全部移动端和
文档源码保持原样，候选运行时仍逐项核对十一项描述符，不接受任意辅助 manifest。

镜像准备、原生认证和竞赛样例统一读取这份已绑定的干净来源。竞赛仅添加明确人工编写的
模块文件，再验证完整增量清单与回执摘要；不使用宽泛 ignore 模式丢弃合法示例配置。
候选自带虚拟环境或依赖目录的拒绝规则不变。交接回执只证明 CI 源码来源一致，不能替代
真实容器、数据库、浏览器、重启或清理验收。

## Bounded native preparation diagnostics

Native preparation and registration may emit separate failure-only JSON receipts
through the explicit `--diagnostics` option. The workflow archives these receipts
alongside the existing profile evidence. They contain finite stage, error and
reviewed Dockerfile RUN identifiers, bounded return codes and booleans only. Build
output scanning is limited to 64 KiB and each receipt to 4 KiB; raw logs, exception
messages, commands, dependency names, paths, URLs and environment values are never
copied into these new receipts. Unknown or changed recipe commands remain unknown.

The diagnostic writer creates files exclusively and preserves a more precise
worker receipt. Failure to save a diagnostic never converts the original failure
into success. No build timeout, dependency lock, network isolation, non-root build
condition or readiness check is relaxed. Diagnostic receipts are not readiness or
acceptance evidence, and later native runtime stages remain untested when preparation
fails.

## Durable extension workflow and coverage levels

The selected template is still generated by its deterministic native adapter.
LangGraph persists an extension design gate, bounded source edits, isolated node
verification, aggregate verification, bounded integration repair, clean-room ZIP
verification and delivery approval. Each candidate is addressed by the approved
design, current source manifest, round and repair attempt. Baselines are versioned
by design digest. Retrying missing isolation prerequisites resumes the saved
candidate rather than paying to regenerate it. Permission-changing designs remain
manual gates even when automatic mode is enabled.

The controller stores original messages before extension planning and retains exact
source units. Source references in a model plan are a traceability map, not proof.
The design gate shows a controller-owned policy alongside the executable contract;
source editing cannot alter either. Generic contracts must have linked successful
business writes/reads, concrete non-envelope values, denied permission operations,
invalid/conflicting business input and successful same-resource/value reads after
restart. These structural checks reject health-only acceptance but cannot establish
all meanings of arbitrary natural language. Generic delivery therefore reports
`coverage_level=reviewed-executable-contract`, `full_request_complete=null` and the
original source units plus approved acceptance digest. The UI explicitly explains
that boundary instead of claiming complete semantic coverage.

The known competition request has an additional controller registry. Matching
canonicalizes formatting without changing retained source bytes; distinctive
contest/invitation/blind-review concepts cannot silently downgrade to generic
acceptance. Ambiguous scope requires independent policy review. For the registered
FastapiAdmin/PostgreSQL scope, aggregate verification invokes the authored
`contest-business-v2` oracle outside candidate code. Its exact witnesses cover
invitation codes, atomic capacity, blind identity, access denial, physical rows,
restart persistence and fresh-database replay. Every original source remains an
open full-source obligation, including the 35-unit original request. A successful
bounded slice never completes cross-school registration, weighted scoring,
reviewer allocation, teacher approval, exports, real email/SMS or cloud storage.
Those unresolved obligations block delivery, not just add a warning.

Reports `extension-scope.json`, `extension-acceptance.json` and
`extension-coverage.json` make that distinction inspectable. They live in the
controller run directory, outside candidate writes. Original-request retention,
formatting-resistant registry routing, meaningless-positive/negative rejection,
permission/version/idempotency behavior, retry preservation and UI coverage wording
are regression-tested with authored fixtures. These tests are not paid-model or
live Docker evidence. The live native profile CI still must verify the exact source
pins; candidate execution remains disabled by default until valid certification.
