# 从实体CRUD写到有权限、有流程的业务产品

本章说明同一份`Plan.business`怎样驱动关联数据、岗位权限、分配与状态操作、处理历史、审计、站内提醒和统计。它不是把“客户服务”写死在模型回复中：实体、字段、角色、关系、转换和统计项均来自经过校验的合同。`examples/requirements/customer-service.md`保留用户原始需求，`customer-service-decisions.md`与`customer-service-contract.md`在同一目录保存默认决策和明确命名约定；三份文本一起作为需求输入。`examples/plans/customer-service.json`保存对应的完整结构化工具验收样例。四份文件均完整收录在附录。

**证据边界**：代码生成、合同测试、真实原生HTTP、完整前端构建/类型检查、三角色浏览器以及独立新库启动是不同关卡。应按当前提交的报告判断结果，不能因为本章描述了代码就把未执行的原生关卡标成通过。固定计划用于确定性工具验收；它不代替模型真实理解该需求的测试，也不是生产模型失败后的默认答案。

## 0. 把原始需求逐项映射到实现

先照原文逐项打勾，不能只看实体数或菜单数：

| 原始要求 | 可执行合同与主要代码 | 最少实际行为 |
|---|---|---|
| 客户建档、修改、查询、条件搜索和历史服务 | customers字段；relations；`querying.py`；各业务运行时的related查询 | 管理员建档，员工按名称/分类搜索，从客户详情打开有权查看的请求 |
| 请求创建、负责人、状态、记录和过程 | requests、`assignee_field`、workflows、notes、audit；`Policy`与事务适配 | 员工提交，管理员指派，客服start/resolve，备注与历史保持完整 |
| 团队任务、处理提醒、操作/状态追踪 | tasks→requests；notifications；追加事件与收件人通知表 | 分派任务；相关角色得到站内提醒；他人不能读或改收件箱 |
| 数量、效率、客户分析和趋势 | count、average_duration、group_count、time_count | 展示数量、解决秒数、客户分类和UTC日趋势；客服只统计本人范围 |
| 管理、服务与普通员工权限 | manager/service/employee；permissions；all/assigned/own | 同一数据由三角色实际读取/修改；无权请求由后端拒绝 |
| 沿用当前体系、组件、测试和部署 | 三个适配器、原生ORM/事务/UI、业务测试及独立启动器 | 每模板分别真实构建、浏览器操作、下载、新库启动和重启 |

`business_contracts.py`负责结构与引用合法性，`business_capabilities.business_gaps`负责对已识别业务义务检查是否缺合同能力，`flow.py`把缺项留在设计修正关口。二者都不是完整自然语言正确性的证明：仍须模型审阅和按原始要求执行真实黑盒验收。`knowledge.design_pack`把角色、关系、流程、通知与指标写入可审查设计，不只输出三张表。

## 1. 先写清楚数据，不要先写三个没有联系的页面

按下面顺序创建附录中的文件。不要提前运行还未写齐的模块：

| 顺序 | 要完整创建的文件 | 输入、职责和输出 |
|---|---|---|
| 1 | `workbench/business_contracts.py`，再把`domain.py`中的可选business字段连接好 | 校验角色、资源、关联、状态、通知和指标；拒绝未知实体、未知角色、矛盾字段与任意脚本 |
| 2 | `examples/requirements/customer-service.md`、同目录decisions/contract补充文本、`examples/plans/customer-service.json` | 把自然语言目标与机器可验收合同并排保存；明白每条要求映射到哪里 |
| 3 | `templates/business/common/policy.py`及`workbench/business_capabilities.py` | 解释已登记动作与行范围；不允许模型自称支持未经适配的能力 |
| 4 | `workbench/business_python.py`、`templates/product/business_schema.py`、`business_runtime.py`、`manage.py`及`templates/frontends/simple-admin/` | 先让Python产品拥有真实外键、角色策略、独立初始化和轻量原生界面 |
| 5 | `workbench/business_fastapi.py`及`templates/business/fastapiadmin/`，`workbench/business_yudao.py`及`templates/business/yudao/` | 在两套真实原生生成结果上挂载同一合同，不另造假原生管理页面 |
| 6 | `workbench/business_native.py`、`business_schema_receipt.py`，及native_lab/portable中的调用 | 在专用库事务中安装明确DDL，记录表结构签名，连接新库恢复验证 |
| 7 | `workbench/business_probe.py`、`business_browser.py`、`templates/product/verify_business.py`、三个模板的business浏览器脚本及测试 | 用实际原生账号、API、页面和数据库验证全部环节；将结果保存为证据 |

客户服务案例有三个资源：customers保存客户资料；requests以customer_id引用客户；tasks以request_id引用请求。`assignee_id`引用本机原生用户，不是自由填写的名字。API上的引用ID使用字符串，原生数据库中仍采用相应数值主键与外键；字符串`"12"`不能被解释成另一个实体的编号，更不能通过字符串拼接进入SQL。

字段`request_state`与`task_state`分别表示两个流程的状态。原生框架自己的`status`是保留字段，不能把同名业务字段塞进去覆盖它。`created_by`、`created_at`、`updated_at`、`archived_at`是服务器拥有的虚拟字段，用户不能通过表单指定创建人或修改审计时间。

先保存完整样例，再在项目根目录只做合同检查：

```powershell
uv run python -c "import json; from pathlib import Path; from workbench.domain import Plan; p=Plan.model_validate(json.loads(Path('examples/plans/customer-service.json').read_text(encoding='utf-8'))); print(p.title); print([r.name for r in p.business.roles]); print([e.name for e in p.entities])"
uv run pytest tests/test_business_contracts.py tests/test_business_capabilities.py tests/test_business_yudao.py -q
```

预期能看到三个实体与manager/service/employee三种业务角色；这两条命令不创建正式业务数据库。失败先修合同，不要为了通过删除权限、外键或业务步骤。

## 2. 角色与行范围是两个问题

一个权限条目同时回答“能做什么”和“对哪些记录能做”。`actions`列出create、read、update、archive、assign、transition、add_note、read_history、read_audit、read_metrics等已登记动作；`scope`取all、own或assigned。业务合同不能与额外`custom_rules`同时使用；命名流程动作不是让模型任意写交易代码。own依据不可改的创建人；assigned依据资源声明的负责人引用字段。某用户能打开菜单，不代表他可以查看所有数据。

案例中，管理员负责整体管理；客服只能处理分配给自己的请求和任务；普通员工只能查看自己提交的请求和相关历史。客户资料的读取范围在合同中单独声明，不能因为请求是自己的就自动得到管理所有客户的权限。统计也应用调用者的read_metrics行范围，不能先统计全库再仅隐藏页面上的表格。

Python产品由独立`manage.py bootstrap-admin`在本机终端交互初始化首位管理员；原生产品沿用框架已有的超级管理员。两者都不能通过普通注册自封管理员。

`bootstrap_role`声明最初业务管理员角色，`role_admin_roles`声明谁能管理业务角色，`registration.default_role`只能是非管理员角色。初始化不是直接把用户编号1写进SQL。部署后，已经通过原生认证的原生超级管理员显式点击业务权限初始化按钮；服务校验其真实身份，在事务与初始化锁下建立本产品专属角色和标记。普通注册不能抢先建立管理员，也不能让后续初始化失效。

业务角色管理只操作本产品声明的角色，不给用户赋予原生全局管理员。角色变更在项目锁下重新检查操作者权限并保护最后一位管理员；不能只靠“禁止自己降级”应付两位管理员同时相互降级。出现多个相互矛盾的本产品角色时应拒绝，而不是挑一个权限最大的角色。

## 3. 把会改变业务含义的字段收回到命名操作

负责人、流程状态与由转换写入的完成时间不能通过普通update偷偷改变。一般编辑只改普通业务字段；分配负责人使用assign，状态变化使用transition，处理备注使用add_note。删除入口按合同执行归档，保留关联和历史，不硬删业务记录。

workflow声明初始状态和转换。一次转换包含名称、允许的旧状态、目标状态、允许角色及可选的服务器时间戳字段。例如start从new进入active，resolve从active进入resolved并记录resolved_at。后端必须锁定当前记录再核对旧状态与权限，因此两个请求不能都以同一旧状态重复执行一次完成操作。

创建/修改关联记录时，要检查目标真实存在、未归档且调用者有权引用。目标记录与归档操作使用一致的事务锁，避免另一请求在检查之后把目标归档。原生物理外键继续保留，不靠前端下拉框替代数据库约束。归档遇到仍有效的引用时遵守明确的限制，不能静默级联删除。

## 4. 三个模板的代码、组件和调用关系

| 模板 | 从平台到产品的调用 | 产品内的执行与页面 |
|---|---|---|
| Python基础 | `generator.generate_basic → business_python.prepare_product` | `business_schema.build_metadata`生成实际外键与事件表；`app.py → business_runtime.install_business`挂载事务接口；`simple-admin/app.js`连接已有列表、表单、详情、提醒与统计容器 |
| FastapiAdmin | `native_modules → business_native → business_fastapi.extend_business` | 保留生成模型与原生认证；`module_business/controller.py → runtime.py → policy.py`；生成页面使用Fa/Element Plus，关系与动作由合同决定 |
| Yudao/Vben | `native_modules → business_native → business_yudao.install_yudao_business` | 保留生成DO/Mapper/VO；Controller调用`RndBusinessService.java`，通过MyBatis与事务完成写入；Vben页面连接`panel.vue`、`business-form.ts`和`metric-chart.vue` |

Python的`business_schema.py`只构造元数据，不连接数据库；`business_python.py`据此写出两种SQL并冻结迁移，独立产品不再导入workbench。`business_runtime.py`每次请求从库中读取角色，将行范围放进查询条件，锁定记录再执行动作，和事件一起提交。共享`policy.py`只解释有限声明，不自己访问网络或执行任意脚本。前端隐藏无权按钮只是体验，后端仍重复校验。

### 4.1 FastapiAdmin的原生挂载

FastapiAdmin先由真实生成器产生模型、控制器和页面。适配器保留原生模型/认证，补齐ORM关系；原生成CRUD入口加保护，业务入口用同一原生数据库会话执行合同。页面继续使用原来的Fa/Element Plus组件、导航和主题。

### 4.2 Yudao/Vben的原生挂载

Yudao先由Infra生成器产生真实Java DO、Mapper、Service、VO与Vben页面。`business_yudao.py`校验这些产物的路径和身份，再把同一路径的CRUD控制器接到事务性业务服务；真实MyBatis Mapper/DO继续负责原表读写，生成的VO校验也保留。额外审计/通知/初始化表通过明确DDL创建。目标表、权限和路由必须符合当前生成结果的精确命名，不能把一个合法SQL标识符替换成system_users之类无关表。

Vben保留原来的Page、Grid、TableAction、Form、Modal及Ant主题。适配器只把合同里的关联字段变成受限下拉框、把受控字段移出普通编辑，再加入业务详情面板、时间线、提醒和Echarts统计。浏览器要真实操作这些组件；相似颜色或一张静态截图不证明保留了原生框架。

原生用户注册仍走框架自己的账号校验、密码哈希与认证流程。业务注册钩子在同一事务中附加明确的默认业务角色；它不自己保存明文密码，不造假登录令牌，也不会向模型暴露本机登录凭据。

## 5. 历史、审计、提醒和统计如何连接

每次业务修改与对应服务器事件在同一事务中提交。事件记录操作者、动作、记录身份、时间和必要的前后状态。处理备注是追加事件；历史页面显示处理过程，审计视图按独立权限读取更多细节。审计不是可以在普通CRUD页面修改或删除的一张业务表；数据库还应拒绝更改已有审计事件。

站内提醒由创建、分配、指定转换或到期条件触发，只写给合同声明的创建人/负责人。相同来源事件和收件人去重。已读状态只属于收件人，不能用另一个人的提醒ID标记或读取他的内容。到期提醒依赖当前本机时间和合同中的日期字段；它不等于邮件、短信或外部推送。

统计类型固定为count、average_duration、group_count、time_count，过滤条件也是结构化字段/操作符，不接收任意SQL。处理时长用created_at到resolved_at的秒数，缺少结束时间的记录不参加平均，零样本返回null而非伪造0。客服标准例按customers.category进行客户分类；其他分组只能使用合同已声明字段；每日趋势使用UTC日桶。日期时间输入带明确时区，原生无时区存储的转换必须与服务器UTC策略一致。

## 6. 在专用空库运行，按证据确认完成

完成原生章节的本机工具准备，使用原生验收章节明确创建的专用空测试库。不要把个人或生产库地址填入NATIVE_TEST_DATABASE_URL。先在已准备浏览器的同一终端验证Python客服产品，再分别运行两个原生完整入口：

```bash
uv run pytest tests/test_business_python.py tests/test_business_python_browser.py tests/test_customer_workflow.py -q
uv run python -m scripts.ci_native_bundled fastapiadmin --spec examples/plans/customer-service.json
uv run python -m scripts.ci_native_bundled yudao-vben --spec examples/plans/customer-service.json
```

两条原生命令分别在对应的干净环境/专用空库运行，不要连续指向同一个已经写入数据的库。脚本先启动真实原生代码生成器，建基础业务表、生成模块/菜单，再事务性安装`business-extension-schema.sql`和可选的`business-role-seed.sql`，随后重新构建并启动后端。DDL来自受审查适配器，不能由模型直接提供。安装失败保留现场并报告，不能删除已有数据库来假装一次新成功。

HTTP验收使用本次创建的合成账号，验证真实注册/登录、角色分配、三个资源、关联、指派、状态转换、历史/审计、提醒、统计及越权拒绝。浏览器验收继续使用真实原生登录和租户选择，不注入token或替换接口响应。临时场景文件中的合成密码不上传到报告；最终证据应保留检查项、截图、错误与当前提交身份。

最后还要把实际生成的产品打包，在另一目录和另一全新数据库重建。独立启动器按顺序应用原生种子、业务表、菜单及扩展表，核对列、外键和关键约束的结构签名，而不只看表名存在。新产品没有预先复制的业务用户或业务记录；管理员首次进入后完成本产品权限初始化。真实新库复验通过，才可声称ZIP能独立运行。

`--check`属于验收，会创建合成账号和测试记录；只对明确的测试部署使用。普通用户启动采用产品README中的常规入口，不把测试检查当日常数据迁移，也不要把测试密码用于实际账户。任何原生编译、SQL、浏览器或恢复关卡未执行/失败，都要保持对应状态，不能仅凭单元测试发布“完整通过”。

## 7. Actions通过后，还要真正打开截图做视觉检查

机器报告先确认实际交互与权限，再检查对应提交的截图。至少逐项打开以下画面，不只看文件名或“保存成功”：

| 画面 | 视觉与内容检查 | 必须结合的行为证据 |
|---|---|---|
| 客户、请求、任务列表 | 原生导航/表格/操作组件保持一致，标题和关键字段齐全，操作不遮挡数据 | 列表确实来自当前原生API，行范围正确 |
| 三类新增/编辑表单 | 原生Form/Modal、标签、必填、枚举、时间控件清楚，弹窗底部按钮可见 | 提交、错误输入及关闭/再开行为真实执行 |
| 客户→请求→任务的关联选择 | 展示可识别的客户/请求标签，而非难以识别的任意数字；选项不被弹窗裁切 | 外键与读取权限仍在服务器执行 |
| 分配与状态处理 | 负责人、可用转换、备注和当前状态表达一致；禁用/无权操作不能误导 | 实际assign/transition请求成功，非法转换被拒绝 |
| 处理历史和审计 | 时间线有操作者、动作、时间和记录，不重叠、不将长内容挤出容器 | 事件不可修改，读历史/读审计权限分别校验 |
| 收件人提醒 | 未读/已读、来源记录和内容清楚；员工看到自己的提醒 | 不同用户不可互读或更改对方已读状态 |
| 统计面板 | 数量、秒数、无样本状态、客户分组与日期轴明确，图表不空白/截断 | 数据按当前角色行范围计算，不能拿装饰图代替真实指标 |

FastapiAdmin应继续体现Fa/Element Plus，Yudao应继续体现Vben/Ant Design/VXE及其原生主题；不能因为两个模板的数据相同，就将页面统一替换成另一套通用UI。检查常用桌面宽度及较窄视口，确认菜单、表单和图表没有横向溢出或被遮挡。若当前自动化只采集了一个视口，就如实记录这个范围，不能宣称所有屏幕都已验证。

最终验收记录应区分：Actions行为结果、实际模型结果、独立部署结果、已打开检查的截图清单，以及发现并修复的视觉问题。任何一项仍缺失就标为未验证；截图不能替代权限/数据库测试，测试通过也不能替代人实际查看图像。

## 8. 从空目录学完后，亲手跑一遍完整客服操作

先按前面的创建顺序写齐附录全部文件、安装锁定依赖、重建固定第三方归档和准备浏览器。第一次选Python/simple-admin/SQLite能少配置外部服务，但不是删除需求；另外两种原生模板必须各自重复完整过程。

1. 用`uv run rnd init`准备控制库，从同一终端`uv run rnd start`。打开工作台，填本机令牌，先确认模板/前端/数据库，再填项目名。
2. 按原文、默认决策、命名合同顺序粘贴三份客服文本，选择一次初始智能推荐。需求与设计页面应保留所有业务义务；不要粘贴固定Plan替模型答题。遇到`BLOCKED`读缺项与真实工具错误，修正受支持原因后继续同一run；不能删权限或提醒来凑成功。
3. 打开设计说明，找到customers→requests→tasks的关系、manager/service/employee、own/assigned范围、new→active→resolved、resolved_at、站内通知和四类指标。再在源码附录定位它们分别由合同、策略、事务和页面哪一部分承担。
4. 等`READY`后真实点击下载，在新目录解压、运行`uv run --no-project --python 3.14 python start.py`。Python产品另开终端执行`uv run python manage.py bootstrap-admin --username manager`，按隐藏提示设置自己的密码。原生产品用启动器提供的原生初始化方式登录，再初始化本产品业务权限。不要使用测试源码中的合成密码作为实际账号密码。
5. 管理员建立客户，创建或授权服务、员工账号。员工登录创建关联请求；管理员指派客服；客服在自己的范围内start、追加备注、resolve。再为请求建立关联任务并重复分配/处理。员工刷新后应看到自己请求的结果及站内提醒。
6. 用第二个员工/客服账号核对看不到不属于其范围的请求、任务、历史和通知。尝试越权API还应被后端拒绝，不能只以按钮消失作为证明。打开客户详情时，相关请求也必须按调用者范围筛选。
7. 打开管理员/客服统计：数量、解决时长、客户分类、日趋势均对应实际数据；未解决记录不计入平均解决时长。检查通知已读，再退出、停止、重启产品，确认业务与历史仍在。备份是另外的数据操作，不能把源码ZIP当数据备份。
8. 保存此模板的当前提交、工具/浏览器/新库/重启结果和实际打开检查的截图。对两个原生模板重复步骤，确认各自的组件与主题，不把一套成功复制给另外两套。最后才汇总三模板结果；真实DeepSeek仍按下一章单独验收。

这一轮能回答“每条原始需求在哪里实现、谁能执行、怎么拒绝越权、怎么证明交付包离开平台仍能启动”。答不出的部分回到对应代码与测试，不追加第二份带版本后缀的教材。
