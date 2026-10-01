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

字段的补充精确定义：所有文本的 min_length=0（必填由 required 负责，未另加字符下限）；datetime 字段仅存储时间戳，searchable=false、filterable=false、date_range=false。逻辑外键字段同样不添加搜索或日期范围。系统自动提供 id/created_at/updated_at/created_by/archived_at，不能在 entities.fields 重复声明；统计直接引用系统 created_at。

本例只能包含 customers、requests、tasks 三个实体，Requirement.additional_entities=false。三个实体的上述业务字段清单是穷尽且封闭的，不允许增加字段，也不能遗漏字段。需求分析须在 entity_requirements 完整记录如下清单并设 additional_fields=false：customers=[name, organization, contact, category]；requests=[title, detail, customer_id, assignee_id, request_state, resolved_at, due_at, priority]；tasks=[title, detail, request_id, assignee_id, task_state, resolved_at, due_at]。日期格式说明和模板能力不构成额外业务要求；本客服案例没有新闻、发布或客户档案发布日期字段，不得引入 published_on 等其他案例字段。不得用新增字段替代已有的系统 created_at 或业务 datetime 时间戳。

界面字段使用可声明的 label 中文名称；请求/任务状态通过 choice_labels 声明 new=待处理、active=处理中、resolved=已解决，存储与动作仍使用原机器值。角色label分别为管理人员、服务人员、普通员工；所有统计label用中文。关联字段显示当前角色可读的客户名称、请求标题或负责人用户名，不能直接把UUID或整数ID当成人类可读名称。
命名状态动作同时声明中文 label：start 为“开始处理”、resolve 为“标记解决”，动作 name 不变。
