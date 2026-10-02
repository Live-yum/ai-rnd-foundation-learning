# tests/fixtures/customer_design_diagnostics/1d7c70b/fastapiadmin.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/1d7c70b/fastapiadmin.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L1504。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`51018`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/1d7c70b/fastapiadmin.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d0d30b7d9ccd6a77e2f0e6a599592d9b63637884cec6ec627953e395474d4a72"} -->
````json
// tests/fixtures/customer_design_diagnostics/1d7c70b/fastapiadmin.json
{
  "format": "customer-design-diagnostic-v1",
  "approval_status": "unapproved",
  "execution_authorized": false,
  "purpose": "offline_contract_validation_only",
  "template": "fastapiadmin",
  "requirement": {
    "summary": "内部客户服务管理平台：shared 业务范围，三个业务实体 customers / requests / tasks，三类角色 manager（管理人员）/ service（服务人员）/ employee（普通员工）。管理人员维护客户档案、分配负责人、查看审计与统计；服务人员只处理分配给自己的请求与任务（scope=assigned），可查询、修改、加备注、执行命名状态转换、查看处理历史与审计；普通员工提交并只查看自己创建的请求（scope=own），不能分配、改状态、看团队统计。请求与任务初始状态 new，命名转换 start（new→active）、resolve（active→resolved 并自动写 resolved_at），仅 manager/service 可执行，状态与负责人受动作保护。三个资源均记录不可修改审计；请求/任务启用处理备注、分配、状态转换与归档及持久化站内提醒（分配、备注、状态变化、解决、逾期），请求解决后创建者可在自己的通知收件箱看到提醒。统计包含请求总数、已解决数、created_at→resolved_at 平均解决时长、客户按 category 分组、请求按 created_at 的 UTC 每日趋势，按调用者 read_metrics 行范围计算。技术栈为 FastapiAdmin 原生后端 + Vue 管理端 + PostgreSQL，遵循既有代码规范、组件与前后端架构，附带必要测试与部署运行方式。",
    "users": [
      "管理人员（manager）：管理团队业务、客户档案、分配负责人、查看审计与统计，拥有三个资源全部记录的动作权限",
      "服务人员（service）：只处理分配给自己的请求与任务（scope=assigned），可查询、修改、添加备注、执行状态转换、查看处理历史与审计，统计按本人可见行计算",
      "普通员工（employee）：提交并只查看自己创建的请求（scope=own），不能分配、改变状态、读取团队统计",
      "新注册用户：默认获得 employee 角色，不能自行提升权限",
      "首个引导账号（bootstrap_role=manager）：由系统初始化为管理人员"
    ],
    "data_scope": "shared",
    "features": [
      "客户档案管理：管理人员可创建客户（name 必填、最长120；organization 最长160；contact 最长200；category 必填枚举 企业/个人/合作伙伴），修改、归档客户并查看审计；服务人员与普通员工只能查询客户资料。",
      "客户查询：按 name、organization、contact 关键词搜索，按 category 精确筛选，支持不同条件组合检索。",
      "客户历史服务记录：客户详情展示其关联的服务请求列表，并遵守被关联请求的行权限，不泄露其他员工记录。",
      "服务请求管理：创建请求（title 最长200、detail 最长3000、customer_id 关联客户、priority 必填），分配负责人、添加处理备注、查看处理过程、归档。",
      "请求状态流转：初始 new，命名转换 start（new→active）与 resolve（active→resolved，自动写入 resolved_at），仅 manager/service 可执行；状态与负责人受动作保护，禁止普通表单绕过转换或分配。",
      "请求查询：按 title、detail 关键词搜索，按 priority（普通/紧急）精确筛选，可查询历史请求。",
      "协作任务管理：创建任务（title 最长200、detail 最长3000、request_id 关联请求），分配负责人、添加处理备注、状态流转（start/resolve）、归档、查看处理过程与审计。",
      "任务查询：按 title、detail 关键词搜索历史任务。",
      "关联视图：请求详情展示其关联的协作任务，客户详情展示关联请求；关联字段显示当前角色可读的客户名称、请求标题或负责人用户名，不显示内部 ID。",
      "审计与处理历史：customers、requests、tasks 均记录不可修改的审计历史；处理历史按 read_history、完整审计按 read_audit 分别授权查看。",
      "站内提醒：负责人分配、添加处理备注、状态变化（start/resolve）、解决、逾期（due_at）事件生成持久化站内消息给对应接收者；请求被解决后创建者在自己的通知收件箱看到提醒；已读状态仅对该接收者可见。",
      "数据统计：requests 总数（count）、已解决数（count，request_state=resolved）、创建至 resolved_at 的平均解决时长（average_duration，单位秒，无样本返回空值）、customers 按 category 分组计数、requests 按 created_at 的 UTC 每日趋势；结果来自数据库真实记录，按当前角色数据范围计算，非前端假图。",
      "权限管理：固定三角色 manager/service/employee，显示名称分别为管理人员/服务人员/普通员工；注册默认 employee；仅 manager 可管理角色，用户不能自行提升权限。",
      "中文界面标签：实体、字段、角色、统计均使用可声明中文 label；request_state/task_state 通过 choice_labels 显示 待处理/处理中/已解决（存储与动作仍用 new/active/resolved），转换 start 显示“开始处理”、resolve 显示“标记解决”。",
      "工程交付：基于当前项目技术体系（FastapiAdmin 原生后端 + Vue 管理端 + PostgreSQL）实现，遵循已有代码规范与组件、保持前后端架构一致，添加必要测试并提供部署运行方式。"
    ],
    "acceptance": [
      "以 bootstrap 的 manager 账号登录后可创建客户（name、category 必填，organization、contact 可选，超过 120/160/200 分别报错）；service 与 employee 账号可查询客户但创建、修改、归档被拒绝。",
      "客户列表可按 name/organization/contact 关键词搜索、按 category=企业/个人/合作伙伴 精确筛选，条件组合结果正确。",
      "客户详情展示该客户关联的历史服务请求，且只显示当前角色有权读取的请求。",
      "创建服务请求时 title（≤200）、detail（≤3000）、customer_id、priority 必填，customer_id 必须指向已存在客户，创建后 request_state 初始值为 new。",
      "请求可分配负责人；被分配的服务人员只能看到并处理 scope=assigned 的请求，看不到其他服务人员的请求。",
      "只有 manager/service 可对请求执行 start（new→active）与 resolve（active→resolved）；resolve 自动写入 resolved_at；无权限角色或非法转换（如 new→resolved）被拒绝。",
      "通过普通表单直接改写 request_state 或 assignee_id 被拒绝，必须走命名转换与分配动作。",
      "请求可添加处理备注；无 read_history 权限的角色看不到处理历史，无 read_audit 权限的角色看不到完整审计；两项授权互不隐含。",
      "任务可创建、分配、添加备注、执行 start/resolve、归档；tasks.title/detail 关键词搜索生效；请求详情展示关联协作任务并遵守 tasks 行权限。",
      "customers/requests/tasks 的审计历史不存在修改或删除入口，归档后历史与被引用关系保留。",
      "分配负责人、添加备注、执行 start/resolve、到达 due_at 时，对应接收者收到持久化站内提醒；请求被 resolve 后创建者在自己的通知收件箱看到提醒；提醒已读状态仅对该接收者可见。",
      "统计返回：requests 总数、request_state=resolved 的数量、created_at→resolved_at 的平均解决秒数（零样本返回空值而非 0）、customers 按 category 的分组计数、requests 按 created_at 的 UTC 每日趋势，数值与数据库实际记录一致。",
      "服务人员调用统计时按 scope=assigned 的可见请求行计算；普通员工无 read_metrics 权限，调用统计被拒绝。",
      "新注册用户默认获得 employee 角色，无法自行提升权限；仅 manager 可执行角色管理操作。",
      "界面按中文标签呈现：request_state/task_state 显示 待处理/处理中/已解决，动作显示 开始处理/标记解决，关联字段显示客户名称、请求标题或负责人用户名。"
    ],
    "questions": [],
    "assumptions": [
      "实体名固定为 customers、requests、tasks，角色名固定为 manager、service、employee，状态机器值固定为 new/active/resolved；中文显示名称按命名合同落地。",
      "关系键 customer_id、assignee_id、request_id 在声明合同中为 text 类型，由原生生成器转换为真实整数外键并校验存在性，不实现为不校验的备注文本。",
      "所有文本字段 min_length=0（必填由 required 负责）；datetime 字段仅存储时间戳，不参与搜索、筛选或日期范围。",
      "统计时区固定 UTC、每日分桶，平均解决时长单位固定为秒；已解决数通过 request_state=resolved 过滤。",
      "审计记录不可修改且由服务端在事务内自动写入；归档保留引用与历史。",
      "界面字段与统计中文标签由业务术语落地，可按团队用语调整而不改变字段名与机器值。"
    ],
    "unsupported": [],
    "limitations": [
      "不连接邮件、短信或真实客户联系方式，提醒仅为持久化站内消息。",
      "不包含外部数据采集、公开匿名访问、爬虫或支付等外部副作用；以声明式业务合同实现，custom_rules 留空。",
      "业务权限、关系、流程、提醒与统计仅在声明式业务合同内实现，不支持任意脚本或任意状态机扩展。",
      "本实例交付为 FastapiAdmin 原生后端 + Vue 管理端 + PostgreSQL 单界面风格；api-only 无界面变体与 Yudao/Java 变体不在本次界面验收范围。",
      "验收仅创建合成账号与客户数据，不导入真实客户隐私数据。"
    ],
    "recommendations": [
      "普通文本统一 min_length=0（必填由 required 承担），标题类上限按合同取 120/160/200，正文上限 3000，日期与时间戳展示格式 YYYY-MM-DD（系统 created_at/updated_at 由运行时提供，不在实体字段中重复声明）。",
      "datetime 字段（resolved_at、due_at）仅存储时间戳，不参与搜索、筛选与日期范围；本需求未要求按时间区间筛选，如后续需要可按日期字段单独追加。",
      "关键字搜索分别落在 customers.name/organization/contact、requests.title/detail、tasks.title/detail；分类精确筛选仅落 customers.category 与 requests.priority，状态字段不默认追加筛选条件。",
      "命名合同未要求普通员工读取协作任务，暂不授予 tasks 权限；若希望员工看到分配给自己的任务，可追加 tasks read + add_note、scope=assigned。",
      "服务人员对 customers 为全量查询（customers 无负责人字段），因此客户分类分布指标对服务人员按全部可见客户计算；若需按负责范围隔离客户，需为 customers 增加 assignee 字段并改成 assigned 范围。",
      "普通员工没有 read_metrics，统计入口对其不可见；管理人员统计范围为全部记录，服务人员统计按 scope=assigned 的可见请求行计算。",
      "站内提醒按源事件与接收者去重，已读状态仅对该接收者可见；请求解决的提醒同时发送给负责人与创建者。",
      "界面字段与统计中文标签为按业务术语给出的建议值，可在不改变字段名与机器值的前提下调整。",
      "归档对 requests/tasks 启用并保留审计与引用关系；客户档案归档后其历史请求仍可查询。"
    ],
    "facts": {
      "business": {
        "scope": "shared",
        "roles": [
          {
            "name": "manager",
            "label": "管理人员"
          },
          {
            "name": "service",
            "label": "服务人员"
          },
          {
            "name": "employee",
            "label": "普通员工"
          }
        ],
        "registration": {
          "enabled": true,
          "default_role": "employee"
        },
        "bootstrap_role": "manager",
        "role_admin_roles": [
          "manager"
        ],
        "resources": [
          {
            "entity": "customers",
            "notes": false,
            "archive": true,
            "audit": true
          },
          {
            "entity": "requests",
            "assignee_field": "assignee_id",
            "notes": true,
            "archive": true,
            "audit": true
          },
          {
            "entity": "tasks",
            "assignee_field": "assignee_id",
            "notes": true,
            "archive": true,
            "audit": true
          }
        ],
        "relations": [
          {
            "entity": "requests",
            "field": "customer_id",
            "target_entity": "customers",
            "on_delete": "restrict"
          },
          {
            "entity": "requests",
            "field": "assignee_id",
            "target_entity": "$users",
            "on_delete": "restrict"
          },
          {
            "entity": "tasks",
            "field": "request_id",
            "target_entity": "requests",
            "on_delete": "restrict"
          },
          {
            "entity": "tasks",
            "field": "assignee_id",
            "target_entity": "$users",
            "on_delete": "restrict"
          }
        ],
        "permissions": [
          {
            "role": "manager",
            "entity": "customers",
            "actions": [
              "create",
              "read",
              "update",
              "archive",
              "read_audit",
              "read_metrics"
            ],
            "scope": "all"
          },
          {
            "role": "service",
            "entity": "customers",
            "actions": [
              "read",
              "read_metrics"
            ],
            "scope": "all"
          },
          {
            "role": "employee",
            "entity": "customers",
            "actions": [
              "read"
            ],
            "scope": "all"
          },
          {
            "role": "manager",
            "entity": "requests",
            "actions": [
              "create",
              "read",
              "update",
              "archive",
              "assign",
              "transition",
              "add_note",
              "read_history",
              "read_audit",
              "read_metrics"
            ],
            "scope": "all"
          },
          {
            "role": "service",
            "entity": "requests",
            "actions": [
              "read",
              "update",
              "add_note",
              "transition",
              "read_history",
              "read_audit",
              "read_metrics"
            ],
            "scope": "assigned"
          },
          {
            "role": "employee",
            "entity": "requests",
            "actions": [
              "create",
              "read"
            ],
            "scope": "own"
          },
          {
            "role": "manager",
            "entity": "tasks",
            "actions": [
              "create",
              "read",
              "update",
              "archive",
              "assign",
              "transition",
              "add_note",
              "read_history",
              "read_audit"
            ],
            "scope": "all"
          },
          {
            "role": "service",
            "entity": "tasks",
            "actions": [
              "read",
              "update",
              "add_note",
              "transition",
              "read_history",
              "read_audit"
            ],
            "scope": "assigned"
          }
        ],
        "workflows": [
          {
            "entity": "requests",
            "status_field": "request_state",
            "initial": "new",
            "transitions": [
              {
                "name": "start",
                "label": "开始处理",
                "from_states": [
                  "new"
                ],
                "to_state": "active",
                "roles": [
                  "manager",
                  "service"
                ]
              },
              {
                "name": "resolve",
                "label": "标记解决",
                "from_states": [
                  "active"
                ],
                "to_state": "resolved",
                "roles": [
                  "manager",
                  "service"
                ],
                "set_timestamp": "resolved_at"
              }
            ]
          },
          {
            "entity": "tasks",
            "status_field": "task_state",
            "initial": "new",
            "transitions": [
              {
                "name": "start",
                "label": "开始处理",
                "from_states": [
                  "new"
                ],
                "to_state": "active",
                "roles": [
                  "manager",
                  "service"
                ]
              },
              {
                "name": "resolve",
                "label": "标记解决",
                "from_states": [
                  "active"
                ],
                "to_state": "resolved",
                "roles": [
                  "manager",
                  "service"
                ],
                "set_timestamp": "resolved_at"
              }
            ]
          }
        ],
        "notifications": [
          {
            "entity": "requests",
            "event": "assigned",
            "recipient": "assignee"
          },
          {
            "entity": "requests",
            "event": "note_added",
            "recipient": "assignee"
          },
          {
            "entity": "requests",
            "event": "transitioned",
            "transition": "start",
            "recipient": "assignee"
          },
          {
            "entity": "requests",
            "event": "transitioned",
            "transition": "resolve",
            "recipient": "assignee"
          },
          {
            "entity": "requests",
            "event": "transitioned",
            "transition": "resolve",
            "recipient": "creator"
          },
          {
            "entity": "requests",
            "event": "due",
            "recipient": "assignee",
            "due_field": "due_at"
          },
          {
            "entity": "tasks",
            "event": "assigned",
            "recipient": "assignee"
          },
          {
            "entity": "tasks",
            "event": "note_added",
            "recipient": "assignee"
          },
          {
            "entity": "tasks",
            "event": "transitioned",
            "transition": "start",
            "recipient": "assignee"
          },
          {
            "entity": "tasks",
            "event": "transitioned",
            "transition": "resolve",
            "recipient": "assignee"
          },
          {
            "entity": "tasks",
            "event": "due",
            "recipient": "assignee",
            "due_field": "due_at"
          }
        ],
        "metrics": [
          {
            "name": "requests_total",
            "label": "服务请求总数",
            "entity": "requests",
            "kind": "count"
          },
          {
            "name": "requests_resolved",
            "label": "已解决服务请求数",
            "entity": "requests",
            "kind": "count",
            "filters": [
              {
                "field": "request_state",
                "op": "eq",
                "value": "resolved"
              }
            ]
          },
          {
            "name": "requests_avg_resolution",
            "label": "平均解决时长",
            "entity": "requests",
            "kind": "average_duration",
            "start_field": "created_at",
            "end_field": "resolved_at",
            "unit": "seconds"
          },
          {
            "name": "customers_by_category",
            "label": "客户分类分布",
            "entity": "customers",
            "kind": "group_count",
            "group_by": "category"
          },
          {
            "name": "requests_daily_trend",
            "label": "服务请求每日趋势",
            "entity": "requests",
            "kind": "time_count",
            "time_field": "created_at",
            "bucket": "day",
            "timezone": "UTC"
          }
        ]
      },
      "labels": {
        "entities": {
          "customers": "客户",
          "requests": "服务请求",
          "tasks": "协作任务"
        },
        "fields": {
          "customers": {
            "name": "客户名称",
            "organization": "所属组织",
            "contact": "联系方式",
            "category": "客户分类"
          },
          "requests": {
            "title": "请求标题",
            "detail": "问题描述",
            "customer_id": "所属客户",
            "assignee_id": "负责人",
            "request_state": "处理状态",
            "resolved_at": "解决时间",
            "due_at": "截止时间",
            "priority": "优先级"
          },
          "tasks": {
            "title": "任务标题",
            "detail": "任务说明",
            "request_id": "关联请求",
            "assignee_id": "负责人",
            "task_state": "任务状态",
            "resolved_at": "解决时间",
            "due_at": "截止时间"
          }
        },
        "choices": {
          "request_state": {
            "new": "待处理",
            "active": "处理中",
            "resolved": "已解决"
          },
          "task_state": {
            "new": "待处理",
            "active": "处理中",
            "resolved": "已解决"
          }
        },
        "transitions": {
          "start": "开始处理",
          "resolve": "标记解决"
        },
        "relation_display": "关联字段显示当前角色可读的客户名称、请求标题或负责人用户名，不显示内部 ID"
      },
      "access_rules": {
        "registration_default_role": "employee",
        "self_escalation": "禁止用户自行提升权限",
        "status_protected_by_transitions": true,
        "assignee_protected_by_assign_action": true,
        "history_and_audit_separate": "read_history 与 read_audit 为独立授权"
      },
      "reminders": {
        "channel": "in_app",
        "persisted": true,
        "events": [
          "assigned",
          "note_added",
          "transitioned:start",
          "transitioned:resolve",
          "due"
        ],
        "no_external_channels": [
          "邮件",
          "短信",
          "真实客户联系方式"
        ]
      },
      "tech": {
        "backend": "fastapiadmin",
        "frontend": "fastapiadmin-vue",
        "database": "postgresql",
        "requirements": [
          "遵循已有项目代码规范",
          "使用已有组件和基础设施",
          "保持前后端架构一致",
          "添加必要测试",
          "提供部署运行方式"
        ]
      },
      "verification": {
        "database": "真正独立的交付数据库",
        "dependencies": "锁定依赖",
        "checks": [
          "浏览器端完整流程验证",
          "重启后验证"
        ],
        "fixtures": "仅使用合成账号与客户数据",
        "note": "不把独立 CRUD 或新闻案例成功当作本案例完成"
      }
    },
    "field_requirements": [
      {
        "field": "name",
        "entity": "customers",
        "kind": "text",
        "required": true,
        "min_length": 0,
        "max_length": 120,
        "searchable": true,
        "filterable": null,
        "date_range": null,
        "choices": null
      },
      {
        "field": "organization",
        "entity": "customers",
        "kind": "text",
        "required": false,
        "min_length": 0,
        "max_length": 160,
        "searchable": true,
        "filterable": null,
        "date_range": null,
        "choices": null
      },
      {
        "field": "contact",
        "entity": "customers",
        "kind": "text",
        "required": false,
        "min_length": 0,
        "max_length": 200,
        "searchable": true,
        "filterable": null,
        "date_range": null,
        "choices": null
      },
      {
        "field": "category",
        "entity": "customers",
        "kind": "enum",
        "required": true,
        "min_length": null,
        "max_length": null,
        "searchable": null,
        "filterable": true,
        "date_range": null,
        "choices": [
          "企业",
          "个人",
          "合作伙伴"
        ]
      },
      {
        "field": "title",
        "entity": "requests",
        "kind": "text",
        "required": true,
        "min_length": 0,
        "max_length": 200,
        "searchable": true,
        "filterable": null,
        "date_range": null,
        "choices": null
      },
      {
        "field": "detail",
        "entity": "requests",
        "kind": "text",
        "required": true,
        "min_length": 0,
        "max_length": 3000,
        "searchable": true,
        "filterable": null,
        "date_range": null,
        "choices": null
      },
      {
        "field": "customer_id",
        "entity": "requests",
        "kind": "text",
        "required": true,
        "min_length": null,
        "max_length": null,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "choices": null
      },
      {
        "field": "assignee_id",
        "entity": "requests",
        "kind": "text",
        "required": false,
        "min_length": null,
        "max_length": null,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "choices": null
      },
      {
        "field": "request_state",
        "entity": "requests",
        "kind": "enum",
        "required": true,
        "min_length": null,
        "max_length": null,
        "searchable": null,
        "filterable": null,
        "date_range": null,
        "choices": [
          "new",
          "active",
          "resolved"
        ]
      },
      {
        "field": "resolved_at",
        "entity": "requests",
        "kind": "datetime",
        "required": false,
        "min_length": null,
        "max_length": null,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "choices": null
      },
      {
        "field": "due_at",
        "entity": "requests",
        "kind": "datetime",
        "required": false,
        "min_length": null,
        "max_length": null,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "choices": null
      },
      {
        "field": "priority",
        "entity": "requests",
        "kind": "enum",
        "required": true,
        "min_length": null,
        "max_length": null,
        "searchable": null,
        "filterable": true,
        "date_range": null,
        "choices": [
          "普通",
          "紧急"
        ]
      },
      {
        "field": "title",
        "entity": "tasks",
        "kind": "text",
        "required": true,
        "min_length": 0,
        "max_length": 200,
        "searchable": true,
        "filterable": null,
        "date_range": null,
        "choices": null
      },
      {
        "field": "detail",
        "entity": "tasks",
        "kind": "text",
        "required": true,
        "min_length": 0,
        "max_length": 3000,
        "searchable": true,
        "filterable": null,
        "date_range": null,
        "choices": null
      },
      {
        "field": "request_id",
        "entity": "tasks",
        "kind": "text",
        "required": true,
        "min_length": null,
        "max_length": null,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "choices": null
      },
      {
        "field": "assignee_id",
        "entity": "tasks",
        "kind": "text",
        "required": false,
        "min_length": null,
        "max_length": null,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "choices": null
      },
      {
        "field": "task_state",
        "entity": "tasks",
        "kind": "enum",
        "required": true,
        "min_length": null,
        "max_length": null,
        "searchable": null,
        "filterable": null,
        "date_range": null,
        "choices": [
          "new",
          "active",
          "resolved"
        ]
      },
      {
        "field": "resolved_at",
        "entity": "tasks",
        "kind": "datetime",
        "required": false,
        "min_length": null,
        "max_length": null,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "choices": null
      },
      {
        "field": "due_at",
        "entity": "tasks",
        "kind": "datetime",
        "required": false,
        "min_length": null,
        "max_length": null,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "choices": null
      }
    ],
    "changes": []
  },
  "candidate_plan": {
    "title": "内部客户服务管理平台",
    "data_scope": "shared",
    "entities": [
      {
        "name": "customers",
        "description": "客户",
        "fields": [
          {
            "name": "name",
            "label": "客户名称",
            "choice_labels": {},
            "kind": "text",
            "required": true,
            "max_length": 120,
            "min_length": 0,
            "choices": [],
            "searchable": true,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "organization",
            "label": "所属组织",
            "choice_labels": {},
            "kind": "text",
            "required": false,
            "max_length": 160,
            "min_length": 0,
            "choices": [],
            "searchable": true,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "contact",
            "label": "联系方式",
            "choice_labels": {},
            "kind": "text",
            "required": false,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": true,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "category",
            "label": "客户分类",
            "choice_labels": {
              "企业": "企业",
              "个人": "个人",
              "合作伙伴": "合作伙伴"
            },
            "kind": "enum",
            "required": true,
            "max_length": 200,
            "min_length": 0,
            "choices": [
              "企业",
              "个人",
              "合作伙伴"
            ],
            "searchable": false,
            "filterable": true,
            "date_range": false
          }
        ]
      },
      {
        "name": "requests",
        "description": "服务请求",
        "fields": [
          {
            "name": "title",
            "label": "请求标题",
            "choice_labels": {},
            "kind": "text",
            "required": true,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": true,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "detail",
            "label": "问题描述",
            "choice_labels": {},
            "kind": "text",
            "required": true,
            "max_length": 3000,
            "min_length": 0,
            "choices": [],
            "searchable": true,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "customer_id",
            "label": "所属客户",
            "choice_labels": {},
            "kind": "text",
            "required": true,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": false,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "assignee_id",
            "label": "负责人",
            "choice_labels": {},
            "kind": "text",
            "required": false,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": false,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "request_state",
            "label": "处理状态",
            "choice_labels": {
              "new": "待处理",
              "active": "处理中",
              "resolved": "已解决"
            },
            "kind": "enum",
            "required": true,
            "max_length": 200,
            "min_length": 0,
            "choices": [
              "new",
              "active",
              "resolved"
            ],
            "searchable": false,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "resolved_at",
            "label": "解决时间",
            "choice_labels": {},
            "kind": "datetime",
            "required": false,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": false,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "due_at",
            "label": "截止时间",
            "choice_labels": {},
            "kind": "datetime",
            "required": false,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": false,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "priority",
            "label": "优先级",
            "choice_labels": {
              "普通": "普通",
              "紧急": "紧急"
            },
            "kind": "enum",
            "required": true,
            "max_length": 200,
            "min_length": 0,
            "choices": [
              "普通",
              "紧急"
            ],
            "searchable": false,
            "filterable": true,
            "date_range": false
          }
        ]
      },
      {
        "name": "tasks",
        "description": "协作任务",
        "fields": [
          {
            "name": "title",
            "label": "任务标题",
            "choice_labels": {},
            "kind": "text",
            "required": true,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": true,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "detail",
            "label": "任务说明",
            "choice_labels": {},
            "kind": "text",
            "required": true,
            "max_length": 3000,
            "min_length": 0,
            "choices": [],
            "searchable": true,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "request_id",
            "label": "关联请求",
            "choice_labels": {},
            "kind": "text",
            "required": true,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": false,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "assignee_id",
            "label": "负责人",
            "choice_labels": {},
            "kind": "text",
            "required": false,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": false,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "task_state",
            "label": "任务状态",
            "choice_labels": {
              "new": "待处理",
              "active": "处理中",
              "resolved": "已解决"
            },
            "kind": "enum",
            "required": true,
            "max_length": 200,
            "min_length": 0,
            "choices": [
              "new",
              "active",
              "resolved"
            ],
            "searchable": false,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "resolved_at",
            "label": "解决时间",
            "choice_labels": {},
            "kind": "datetime",
            "required": false,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": false,
            "filterable": false,
            "date_range": false
          },
          {
            "name": "due_at",
            "label": "截止时间",
            "choice_labels": {},
            "kind": "datetime",
            "required": false,
            "max_length": 200,
            "min_length": 0,
            "choices": [],
            "searchable": false,
            "filterable": false,
            "date_range": false
          }
        ]
      }
    ],
    "acceptance": [
      "以 bootstrap 的 manager 账号登录后可创建客户（name、category 必填，organization、contact 可选，超过 120/160/200 分别报错）；service 与 employee 账号可查询客户但创建、修改、归档被拒绝。",
      "客户列表可按 name/organization/contact 关键词搜索、按 category=企业/个人/合作伙伴 精确筛选，条件组合结果正确。",
      "客户详情展示该客户关联的历史服务请求，且只显示当前角色有权读取的请求。",
      "创建服务请求时 title（≤200）、detail（≤3000）、customer_id、priority 必填，customer_id 必须指向已存在客户，创建后 request_state 初始值为 new。",
      "请求可分配负责人；被分配的服务人员只能看到并处理 scope=assigned 的请求，看不到其他服务人员的请求。",
      "只有 manager/service 可对请求执行 start（new→active）与 resolve（active→resolved）；resolve 自动写入 resolved_at；无权限角色或非法转换（如 new→resolved）被拒绝。",
      "通过普通表单直接改写 request_state 或 assignee_id 被拒绝，必须走命名转换与分配动作。",
      "请求可添加处理备注；无 read_history 权限的角色看不到处理历史，无 read_audit 权限的角色看不到完整审计；两项授权互不隐含。",
      "任务可创建、分配、添加备注、执行 start/resolve、归档；tasks.title/detail 关键词搜索生效；请求详情展示关联协作任务并遵守 tasks 行权限。",
      "customers/requests/tasks 的审计历史不存在修改或删除入口，归档后历史与被引用关系保留。",
      "分配负责人、添加备注、执行 start/resolve、到达 due_at 时，对应接收者收到持久化站内提醒；请求被 resolve 后创建者在自己的通知收件箱看到提醒；提醒已读状态仅对该接收者可见。",
      "统计返回：requests 总数、request_state=resolved 的数量、created_at→resolved_at 的平均解决秒数（零样本返回空值而非 0）、customers 按 category 的分组计数、requests 按 created_at 的 UTC 每日趋势，数值与数据库实际记录一致。",
      "服务人员调用统计时按 scope=assigned 的可见请求行计算；普通员工无 read_metrics 权限，调用统计被拒绝。",
      "新注册用户默认获得 employee 角色，无法自行提升权限；仅 manager 可执行角色管理操作。",
      "界面按中文标签呈现：request_state/task_state 显示 待处理/处理中/已解决，动作显示 开始处理/标记解决，关联字段显示客户名称、请求标题或负责人用户名。"
    ],
    "custom_rules": [],
    "business": {
      "roles": [
        {
          "name": "manager",
          "label": "管理人员"
        },
        {
          "name": "service",
          "label": "服务人员"
        },
        {
          "name": "employee",
          "label": "普通员工"
        }
      ],
      "registration": {
        "enabled": true,
        "default_role": "employee"
      },
      "bootstrap_role": "manager",
      "role_admin_roles": [
        "manager"
      ],
      "resources": [
        {
          "entity": "customers",
          "assignee_field": null,
          "archive": true,
          "notes": false,
          "audit": true
        },
        {
          "entity": "requests",
          "assignee_field": "assignee_id",
          "archive": true,
          "notes": true,
          "audit": true
        },
        {
          "entity": "tasks",
          "assignee_field": "assignee_id",
          "archive": true,
          "notes": true,
          "audit": true
        }
      ],
      "relations": [
        {
          "entity": "requests",
          "field": "customer_id",
          "target_entity": "customers",
          "on_delete": "restrict"
        },
        {
          "entity": "requests",
          "field": "assignee_id",
          "target_entity": "$users",
          "on_delete": "restrict"
        },
        {
          "entity": "tasks",
          "field": "request_id",
          "target_entity": "requests",
          "on_delete": "restrict"
        },
        {
          "entity": "tasks",
          "field": "assignee_id",
          "target_entity": "$users",
          "on_delete": "restrict"
        }
      ],
      "permissions": [
        {
          "role": "manager",
          "entity": "customers",
          "actions": [
            "create",
            "read",
            "update",
            "archive",
            "read_audit",
            "read_metrics"
          ],
          "scope": "all"
        },
        {
          "role": "service",
          "entity": "customers",
          "actions": [
            "read",
            "read_metrics"
          ],
          "scope": "all"
        },
        {
          "role": "employee",
          "entity": "customers",
          "actions": [
            "read"
          ],
          "scope": "all"
        },
        {
          "role": "manager",
          "entity": "requests",
          "actions": [
            "create",
            "read",
            "update",
            "archive",
            "assign",
            "transition",
            "add_note",
            "read_history",
            "read_audit",
            "read_metrics"
          ],
          "scope": "all"
        },
        {
          "role": "service",
          "entity": "requests",
          "actions": [
            "read",
            "update",
            "add_note",
            "transition",
            "read_history",
            "read_audit",
            "read_metrics"
          ],
          "scope": "assigned"
        },
        {
          "role": "employee",
          "entity": "requests",
          "actions": [
            "create",
            "read"
          ],
          "scope": "own"
        },
        {
          "role": "manager",
          "entity": "tasks",
          "actions": [
            "create",
            "read",
            "update",
            "archive",
            "assign",
            "transition",
            "add_note",
            "read_history",
            "read_audit"
          ],
          "scope": "all"
        },
        {
          "role": "service",
          "entity": "tasks",
          "actions": [
            "read",
            "update",
            "add_note",
            "transition",
            "read_history",
            "read_audit"
          ],
          "scope": "assigned"
        }
      ],
      "workflows": [
        {
          "entity": "requests",
          "status_field": "request_state",
          "initial": "new",
          "transitions": [
            {
              "name": "start",
              "label": "开始处理",
              "from_states": [
                "new"
              ],
              "to_state": "active",
              "roles": [
                "manager",
                "service"
              ],
              "set_timestamp": null
            },
            {
              "name": "resolve",
              "label": "标记解决",
              "from_states": [
                "active"
              ],
              "to_state": "resolved",
              "roles": [
                "manager",
                "service"
              ],
              "set_timestamp": "resolved_at"
            }
          ]
        },
        {
          "entity": "tasks",
          "status_field": "task_state",
          "initial": "new",
          "transitions": [
            {
              "name": "start",
              "label": "开始处理",
              "from_states": [
                "new"
              ],
              "to_state": "active",
              "roles": [
                "manager",
                "service"
              ],
              "set_timestamp": null
            },
            {
              "name": "resolve",
              "label": "标记解决",
              "from_states": [
                "active"
              ],
              "to_state": "resolved",
              "roles": [
                "manager",
                "service"
              ],
              "set_timestamp": "resolved_at"
            }
          ]
        }
      ],
      "notifications": [
        {
          "entity": "requests",
          "event": "assigned",
          "recipient": "assignee",
          "transition": null,
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "requests",
          "event": "note_added",
          "recipient": "assignee",
          "transition": null,
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "requests",
          "event": "transitioned",
          "recipient": "assignee",
          "transition": "start",
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "requests",
          "event": "transitioned",
          "recipient": "assignee",
          "transition": "resolve",
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "requests",
          "event": "transitioned",
          "recipient": "creator",
          "transition": "resolve",
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "requests",
          "event": "due",
          "recipient": "assignee",
          "transition": null,
          "due_field": "due_at",
          "channel": "in_app"
        },
        {
          "entity": "tasks",
          "event": "assigned",
          "recipient": "assignee",
          "transition": null,
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "tasks",
          "event": "note_added",
          "recipient": "assignee",
          "transition": null,
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "tasks",
          "event": "transitioned",
          "recipient": "assignee",
          "transition": "start",
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "tasks",
          "event": "transitioned",
          "recipient": "assignee",
          "transition": "resolve",
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "tasks",
          "event": "due",
          "recipient": "assignee",
          "transition": null,
          "due_field": "due_at",
          "channel": "in_app"
        }
      ],
      "metrics": [
        {
          "name": "requests_total",
          "label": "服务请求总数",
          "entity": "requests",
          "kind": "count",
          "group_by": null,
          "start_field": null,
          "end_field": null,
          "time_field": null,
          "filters": [],
          "unit": "seconds",
          "bucket": "day",
          "timezone": "UTC"
        },
        {
          "name": "requests_resolved",
          "label": "已解决服务请求数",
          "entity": "requests",
          "kind": "count",
          "group_by": null,
          "start_field": null,
          "end_field": null,
          "time_field": null,
          "filters": [
            {
              "field": "request_state",
              "op": "eq",
              "value": "resolved"
            }
          ],
          "unit": "seconds",
          "bucket": "day",
          "timezone": "UTC"
        },
        {
          "name": "requests_avg_resolution",
          "label": "平均解决时长",
          "entity": "requests",
          "kind": "average_duration",
          "group_by": null,
          "start_field": "created_at",
          "end_field": "resolved_at",
          "time_field": null,
          "filters": [],
          "unit": "seconds",
          "bucket": "day",
          "timezone": "UTC"
        },
        {
          "name": "customers_by_category",
          "label": "客户分类分布",
          "entity": "customers",
          "kind": "group_count",
          "group_by": "category",
          "start_field": null,
          "end_field": null,
          "time_field": null,
          "filters": [],
          "unit": "seconds",
          "bucket": "day",
          "timezone": "UTC"
        },
        {
          "name": "requests_daily_trend",
          "label": "服务请求每日趋势",
          "entity": "requests",
          "kind": "time_count",
          "group_by": null,
          "start_field": null,
          "end_field": null,
          "time_field": "created_at",
          "filters": [],
          "unit": "seconds",
          "bucket": "day",
          "timezone": "UTC"
        }
      ]
    },
    "unsupported": []
  }
}
````
