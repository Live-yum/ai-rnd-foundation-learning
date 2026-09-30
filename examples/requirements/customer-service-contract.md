# 客服演示的可执行命名合同

这是原始需求的补充实施决策，用于让同一套黑盒用例能够验证三个技术模板；不是模型响应。必须由实际模型生成 Requirement、Plan 和审查意见，禁止把 examples/plans/customer-service.json 当模型输出。

- 业务范围 shared；三个实体名固定 customers、requests、tasks，角色名固定 manager、service、employee，显示名称分别为管理人员、服务人员、普通员工。bootstrap_role=manager；注册默认 employee，不能自行提升权限。
- customers：name（必填文本，最长120，可搜索）、organization（可选文本，最长160，可搜索）、contact（可选文本，最长200，可搜索）、category（必填枚举，企业/个人/合作伙伴，可精确筛选）。管理人员可创建、修改、查询、归档、查看审计；服务人员和普通员工可查询。
- requests：title（必填文本，最长200，可搜索）、detail（必填文本，最长3000，可搜索）、customer_id（必填文本关系键，关联 customers）、assignee_id（可选文本关系键，关联 $users）、request_state（必填枚举 new/active/resolved）、resolved_at（可选 datetime）、due_at（可选 datetime）、priority（必填枚举 普通/紧急，可精确筛选）。
- tasks：title（必填文本，最长200，可搜索）、detail（必填文本，最长3000，可搜索）、request_id（必填文本关系键，关联 requests）、assignee_id（可选文本关系键，关联 $users）、task_state（必填枚举 new/active/resolved）、resolved_at（可选 datetime）、due_at（可选 datetime）。关系键在声明合同中用 text，原生生成器负责转换为真实整数外键；不得把关联实现成不校验的备注文本。
- 请求和任务的初始状态为 new，命名转换 start：new→active，resolve：active→resolved 并自动写 resolved_at。只有 manager/service 可执行转换。状态和负责人受动作保护，禁止普通表单绕过转换或分配。
- 三个业务资源均记录不可修改的审计历史。请求和任务启用处理备注、分配、状态转换与归档。管理人员拥有所有记录的动作权限；服务人员只处理分配给自己的请求/任务（scope=assigned），包括查询、修改、添加备注、转换、查看处理历史和审计；普通员工可创建并查询自己提交的请求（scope=own），协作任务由管理人员创建分配，不能分配、改变状态、读取团队统计。
- 客户详情能查看关联的历史服务请求，请求详情能查看关联协作任务；关联查询遵守被关联记录的权限，不泄露其他员工记录。
- 站内提醒持久化，包含负责人分配、处理备注、状态变化、解决和逾期提醒；解决请求后提交者可以在自己的通知收件箱看到提醒。
- 指标至少包括 requests 总数（count）、已解决数（count，按 request_state=resolved 筛选）、创建至 resolved_at 的平均解决时长（average_duration，start_field=created_at）、customers 按 category 分类（group_count）、requests 按 created_at 的每日趋势（time_count）。角色只允许 manager/service，服务人员指标必须按本人可见行计算；不是预设数字或前端假图。
- 不添加外部服务、支付、邮件短信、爬虫或自定义任意代码。以 business 可执行合同实现，custom_rules 留空。所有业务权限、关系、流程、提醒和指标均须明确声明，不能只写在中文说明中。
