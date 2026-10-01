## 显式授权的真实模型客服端到端验收

常规Actions用明确模型响应夹具验证编排，同时真实运行数据库、浏览器和本机工具。真实服务商测试是有调用成本的另一项验收，不随普通PR自动调用。它必须在可信指定分支、获准的GitHub Environment中运行；测试脚本再次核对仓库、分支、事件与目标，不允许切换服务商或模型来绕过失败。本章说明如何执行及判断结果，不预先声称任何模板已经通过。

### 明确字段清单与设计前校验

本客服基准的三个实体与业务字段清单是明确封闭的，模型必须在真实生成的
`Requirement.entity_requirements` 中逐实体记录 `entity`、`fields` 和
`additional_fields=false`，并设 `additional_entities=false`。这是发送给模型的
公开需求合同，不是把示例 Plan 作为模型输出。一般项目的两种扩展开关默认均为
`true`，仅列举字段不会自动禁止用户项目增加其他受支持的字段。

`coverage_gaps` 在生成之前比较批准清单与模型 Plan，给出来源编号、实体、
缺失字段和额外字段，原样传入下一次设计修复。不会悄悄删除生成字段或打开批准的
封闭清单。模型重述需求时遗漏清单不会删除已有承诺；修改需要有用户本轮原文作为
来源的明确修正。时间戳显示格式、默认格式或否定日期需求，不会凭空要求新增日期字段。

最外层客服断言还保留独立的逐规则错误编号；即使平台已 READY，后续下载、合同或
独立运行失败，也会保留有大小上限且通过密钥扫描的 Requirement/Plan 诊断信封。
信封明确没有执行授权，不能作为 Plan 输入绕过批准或替代真实模型验收。

### 原生产品的逐项证据怎样进入审阅

原生客服验收在生成时和独立新数据库恢复后分别执行同一组 HTTP 与浏览器探针。
五个合成身份覆盖管理人员、两名服务人员和两名员工，实际比较提醒接收者和私有已读
状态、按可见行计算的指标、审计修改删除的拒绝及前后哈希、关联读写权限，以及每个
已声明字段的搜索、精确过滤、日期范围和可组合条件。查询预期集合来自未过滤记录
及批准权限的独立计算；不能用被测试查询自身作为正确答案。

`execution_evidence` 是测试断言完成后写出的有界观察记录。`native_evidence.py`
核对它是否覆盖当前 Plan，再绑定源码和验收文件哈希，将实际计数与结果发送给独立
审阅模型。只有“业务已通过”一个布尔值的旧报告会被拒绝。部署包同时包含对应探针、
锁文件和独立启动说明，可在新数据库重复执行；协议模拟单元测试不代替这些真实运行。
固定五身份的详细探针对应本章客服标准案例，普通非业务原生模板仍走自身原有验收。

投影版本 `2` 将重复的关联写入和关联访问矩阵编码为列名表与等长数据行，完整保留每项
观察值；原始观察 schema 仍为 `1`，且完整执行证据的哈希保持绑定。解码按列名与数据行
一一对应，不能把哈希当成实际证明值。64,000 字节上限不因方案变大而放宽。
FastapiAdmin 的真实登录与菜单外壳单独保存为严格白名单 `login_shells`，不能用来替代
任何实体的原生表单和列表证据；没有实体标识的任意页面不会因此被接受。

芋道列表保留原生控件，并只显示合同声明的查询能力：关键词不区分大小写、枚举等
精确条件不接受子串匹配、日期上下界包含边界、不同条件使用交集。服务器先执行
租户与行权限，再匹配查询；未声明的过滤条件作为输入错误拒绝，而非静默放宽查询。

### 环境变量与锁定服务商

专用验收使用GitHub Environment `rnd`。环境Secret名称是`APK_KEY`，只在模型测试步骤中映射成平台读取的`API_KEY`；两个变量名各有用途，不为拼写一致复制或打印密钥。环境Variables提供`BASE_URL`和`MODE`，当前授权目标分别为`https://api.deepseek.com`和`deepseek-flash`。关键接线如下，表达式由GitHub解释，不能替换为密钥正文提交：

```yaml
environment: rnd
# 仅实际调用模型的步骤声明以下env；安装依赖的步骤不注入密钥
env:
  API_KEY: ${{ secrets.APK_KEY }}
  BASE_URL: ${{ vars.BASE_URL }}
  MODE: ${{ vars.MODE }}
```

`environment`属于job，`env`属于其模型调用step；完整可执行层级见源码附录。环境保护规则若要求批准，由有权限的人批准，不改环境、不绕过审批、不把Secret放进源码。未绑定该Environment的普通测试不能作为已取得凭据的证明。

### 在客服分支手动触发，先核对精确提交

当前客服开发分支为`feat/customer-service-acceptance`。在仓库的Actions中选择`.github/workflows/native-probe.yml`对应的工作流，打开Run workflow：

1. 在分支选择器选`feat/customer-service-acceptance`，不要使用默认分支代码代替待测客服代码。
2. 明确勾选`real_model=true`；默认false不调用付费模型。
3. `expected_sha`填写已审查的完整40位提交SHA。先在该分支用`git rev-parse HEAD`核对，再与GitHub分支头核对；不是短SHA、分支名或过去成功的提交。
4. 确认目标和费用授权后手动运行。job在模型访问之前要求`expected_sha`与这次`GITHUB_SHA`完全一致，不相等立即停止。
5. 分别查看`python-basic`、`fastapiadmin`、`yudao-vben`三行，记录每行的提交、run ID、attempt与终态。某行失败或pending时不宣布整个矩阵通过。

`.github/workflows/real-model.yml`是专用的手动真实模型入口，只声明`workflow_dispatch`，同样使用三模板矩阵和`rnd`环境。工作流是否能在界面列出，取决于GitHub已登记的默认分支入口；客服分支尚未合并时使用上面的`native-probe.yml`入口，不为显示新工作流而合并未验收代码。不要用push触发、提交消息标记或周期任务代替明确授权。

### 每个模板先测协议，再测完整交付

每行在自己的隔离job中依次运行：

```bash
uv run python -m scripts.ci_real_model --phase smoke --template python-basic
uv run python -m scripts.ci_real_model --phase full --template python-basic
```

另两行的`--template`分别为`fastapiadmin`和`yudao-vben`，对应`fastapiadmin-vue/PostgreSQL`与`vben-antd/PostgreSQL`；基础行使用`simple-admin/SQLite`。这些命令由受信任的Actions环境执行，不要在本机伪造`GITHUB_*`来绕过保护。原生行还必须准备各自固定pnpm、PostgreSQL、Redis和浏览器，Yudao另需JDK17/Maven，完整步骤以两份工作流为准。

smoke发送明确Hello请求，保留`thinking.type=enabled`、`reasoning_effort=high`与`stream=false`。HTTP200且有效回复只证明协议请求可用。同一job、同一attempt、同一commit的smoke成功之后，才进入完整阶段；脚本拒绝复用别的运行的smoke回执。

full通过真实工作台网页选择当前行的模板/前端/数据库，按顺序输入以下三个文件的全部文本：

- `examples/requirements/customer-service.md`：用户原始需求，保留原文
- `examples/requirements/customer-service-decisions.md`：明确演示默认决策
- `examples/requirements/customer-service-contract.md`：黑盒验收需要的实体、角色、字段与流程命名约定

三个文件不包含预置模型Plan。真实模型必须自己形成并通过`Requirement`、`Plan.business`与审阅校验；`examples/plans/customer-service.json`仅是确定性工具测试样例，不能读它替代模型输出。网页只勾选一次初始智能推荐，后续不追加批准或重试；要求保留客户/请求/任务、角色行范围、分配/状态、备注/审计、提醒和全部四类统计后到达`READY`。

到达`READY`后仍要实际点击下载ZIP、验证哈希、解压至新目录，并使用该产品自己的依赖和全新数据库执行HTTP、浏览器与重启检查。原生模板必须真实生成和构建自己的框架，不用Python页面冒充。每阶段有调用与时间预算，失败保留失败，不改用夹具、缩减功能或换供应商补成功。

### 只上传允许公开的机器证据与合成页面截图

每行的`reports/real-model/summary.json`保留白名单回执：运行身份、模板、阶段、错误代码、数值HTTP状态、有限token用量、合同有效性和必要字段标记、浏览器/下载/新库/重启结果。失败时还保留具体义务的来源位置、期望/实际属性，以及有限的未支持说明、审阅缺口、运行异常首行和原生阶段。相关文字每段最多600字符、共用6000字符预算；先替换完整已知密钥，并过滤凭据、令牌、认证头和URL用户信息，再截断。该文件位于`real-model-sanitized-${template}-${runid}-${attempt}`产物中。不上传密钥正文、片段或哈希，不上传完整模型响应、推理、原始服务商错误体、原始工具日志、生成源码包或运行数据库。真实密钥不继续传给浏览器、uv或产品子进程。

本公开合成客服案例的运行失败时，还可单独保留`customer-plan-replay-${template}-${sha}`中的`approved-plan-replay.json`。它只能来自已经通过当时设计门的生成产物：Python 的 product/approved-spec.json，或原生模板的 native-evidence/approved-spec.json；不从候选设计修订回退。须重新通过Plan schema校验、客服实体范围检查和凭据扫描，大小不超过128 KiB。含凭据或不符合范围的规范直接拒绝保存，不通过修改规范来冒充原失败输入；文件记录精确哈希，保留7天。这个规范用于复现失败，不代表其满足全部用户义务，更不能作为下一次真实模型的替代输出。

下载该规范并核对回执哈希后，在具备同一锁定依赖、独立空PostgreSQL/Redis和原生构建工具的环境中，可运行：

```bash
uv run python -m scripts.ci_native_bundled yudao-vben --spec /absolute/path/approved-plan-replay.json
```

FastapiAdmin将模板参数换成`fastapiadmin`。该路径直接验证保存的Plan并调用原生生成器，不调用模型；编译器错误与原生浏览器错误应先用它复现，不为补日志重复付费。代码修复后仍须在最终同一提交重新执行完整真实模型三模板矩阵，确定性重放成功不能替代它。

如果失败发生在设计或审阅阶段，本公开合成案例可另存`customer-design-replay-${template}-${sha}`中的`unapproved-design-contract.json`，用于离线检查字段与业务义务。该信封只选择并重新校验规范化的Requirement与候选Plan，标记`approval_status=unapproved`、`execution_authorized=false`，整体不超过128 KiB；凭据、无效schema、越界或过大的内容直接拒绝，保留7天。它不是Plan输入，不能传给生成器，不能当作批准或绕过审阅；不包含完整服务商响应、环境、数据库或原始日志。可从中读取明确的结构化事实值并调用纯合同校验器重现误判，无需为补诊断再调用模型。

真实产品页面使用合成客户和验收账号；经过路径、名称、大小及PNG校验的截图位于`reports/real-model/screenshots/*.png`，单独保存为`customer-ui-${template}-${sha}`产物。它们只用于查看该行实际页面，不公开实际客户数据或临时密码。下载后应真正打开列表、表单、关联、处理、提醒和统计画面，结合业务章节的视觉清单检查；有截图文件不等于已完成视觉审阅。

只有某行`acceptance_scope=full_workflow`、整体`passed=true`且模板/commit/attempt吻合，才能将该行标为真实模型完整流程通过；三个模板各自满足才可称三模板通过。`smoke_only`、固定计划测试、之前其他案例或其他提交的成功都不能替代。原来`BLOCKED`的任务恢复、Aider编辑、Continue原生索引和Daytona是另外的验证范围；当前真实模型路径明确记录这些未覆盖项，不借用旧报告填充它们。

工作流每次完成输出上限为65,536 tokens，保留16次工作流调用和单次响应2,000,000字节的硬边界；独立兼容性smoke报文不添加这个参数。该上限保留完整需求与Plan，避免此前16,000上限把思考和JSON输出截断；`finish_reason=length`仍记为失败而不修剪需求。DeepSeek官方Chat Completions文档（https://api-docs.deepseek.com/api/create-chat-completion/ ，2026-09-30核对）允许最大393,216 tokens，thinking默认64K。

## 原生交付 ZIP 与已批准方案复现

原生独立验收先把可交付源码打包，再安全解压到全新目录，并核对源码清单，随后才在独立数据库启动、做真实浏览器验证和重启检查。它与最终下载使用同一套生产者/消费者规则，不能用原目录可启动代替下载包可用。

通用、Python 和 FastapiAdmin 压缩包最多 10,000 个条目；只有调用者已经选择的 `yudao-vben` 使用 25,000 条目上限。这个差异来自锁定的原始 Vben 单仓前端本身已有 12,112 个源码文件，不能删除原模板代码来迎合较小上限。所有模板最多 200,000,000 解压字节，单文件最多 32,000,000 字节，另有压缩比检查；路径越界、大小写重复路径、符号链接、凭据和数据库文件仍被拒绝。完整预检发生在写入第一个文件之前，错误分别报告条目数和字节数。

诊断需要复现真实模型已经批准的方案时，可运行下面这个有明确来源的回归案例：

```bash
uv run python -m scripts.ci_native_bundled yudao-vben --approved-replay yudao-1d7
uv run python -m scripts.ci_native_bundled fastapiadmin --approved-replay fastapi-0e8
```

第一条命令读取真实运行 `36795375784`、源码 `1d7c70b03e63509830e97af9af398c0bd148902e` 中通过设计及模型复核的合成客服 Plan，并在原生生成前验证固定哈希、大小、方案结构和凭据模式。对应运行当时因下载 ZIP 的条目数上限失败，因此这个输入只用于复现，不代表历史下载已经通过。Actions 的 `approved-1d7` 案例独立生成、解压并启动该产品，不调用模型，也不会覆盖两个标准客服案例的产物。

第二条命令对应运行 `36826237130`、源码 `0e8ebdd0c74a86538b648d55b9fe56dcc71a9de9`
中通过设计门的 FastapiAdmin Plan。当时原生执行报告已接受，但审阅证据投影失败，
尚未进入独立模型复核；完整原始运行报告未保留，所以不能据此断言原始失败的具体条件。
`approved-0e8` 案例重新执行同一批准方案，不改用候选诊断信封。

四个零模型案例都在原生执行、新库恢复与重启后继续调用生产审阅证据投影，复用运行与
部署门槛、原生风格及业务检查，并核对实际验收文件、方案及源码哈希。`acceptance.json`
保留真正执行记录；`review-projection.json` 仅在严格校验通过后产生。
`review-projection-status.json` 只记录阶段、哈希与结果，失败不补写证明值或沿用旧成功文件。

真实模型验收始终重新进行推荐、设计与独立复核，不读取这个回归方案。`customer_design_diagnostics` 中明确标记未批准的候选方案只供校验器诊断，不能进入生成或执行。
