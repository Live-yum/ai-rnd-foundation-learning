# tests/fixtures/customer_design_diagnostics/dd7e5f2/fastapi-unapproved-design.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/dd7e5f2/fastapi-unapproved-design.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L1556。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`49980`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/dd7e5f2/fastapi-unapproved-design.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9c8cdc4576208ee3f3954d724a7789e2f635e50ae25b66f65d75e34d0e41b5f5"} -->
````json
// tests/fixtures/customer_design_diagnostics/dd7e5f2/fastapi-unapproved-design.json
{
  "format": "customer-design-diagnostic-v1",
  "approval_status": "unapproved",
  "execution_authorized": false,
  "purpose": "offline_contract_validation_only",
  "template": "fastapiadmin",
  "requirement": {
    "summary": "内部客户服务管理平台（FastapiAdmin 原生后端 + Vue 管理端，PostgreSQL，shared 业务范围）。固定三个业务实体 customers、requests、tasks，三个角色 manager（管理人员）、service（服务人员）、employee（普通员工）；bootstrap_role=manager，自助注册默认 employee 且不可自行提权。客户档案维护与多维搜索、服务请求全流程跟踪（创建、分配、命名状态流转、处理备注、处理历史与不可修改审计）、请求关联协作任务、客户历史服务记录与请求协作任务关联查询、持久化站内提醒（分配、备注、状态变化、解决、逾期）、以及按角色行范围计算的统计指标（服务数量、已解决数、平均解决时长、客户分类分布、每日趋势）。所有关联、权限、流程、提醒与指标以可执行 business 合同声明，custom_rules 留空，不引入外部服务、支付、邮件短信、爬虫或任意代码。",
    "users": [
      "管理人员 manager：管理团队业务、客户档案、请求与任务分配、状态流转、审计与全部统计",
      "服务人员 service：只处理分配给自己的请求与任务，可查询、修改、添加备注、状态流转、查看处理历史与审计，并查看本人可见范围内的统计",
      "普通员工 employee：提交并查询自己创建的请求，接收站内提醒；不能分配、不能改变状态、不能读取团队统计"
    ],
    "data_scope": "shared",
    "features": [
      "客户档案管理：创建、修改、查询、归档客户，并由管理人员查看审计历史",
      "客户搜索：按 name、organization、contact 关键词搜索，按 category 精确筛选（企业/个人/合作伙伴）",
      "客户历史服务记录：在客户详情查看关联的 requests，且只显示当前角色有权读取的记录",
      "服务请求管理：创建请求（title、detail、customer_id、priority），分配 assignee_id，添加处理备注，查看处理过程与处理历史",
      "服务请求查询：按 title、detail 关键词搜索，按 priority 精确筛选（普通/紧急），查询历史请求",
      "命名状态流转：请求与任务初始 new；start: new→active（“开始处理”）；resolve: active→resolved（“标记解决”）并自动写入 resolved_at；仅 manager/service 可执行，普通表单不得绕过流转或直接改状态/负责人",
      "协作任务管理：由管理人员创建并分配 tasks（title、detail、request_id、assignee_id），服务人员处理分配给自己的任务",
      "请求详情查看关联协作任务，且关联查询遵守被关联记录的行权限，不泄露他人记录",
      "处理提醒：持久化站内消息，覆盖负责人分配、处理备注、状态变化、解决与逾期；解决请求后提交者在自己的通知收件箱看到提醒",
      "操作记录与状态变化追踪：customers、requests、tasks 均记录不可修改的审计历史",
      "数据统计：requests 总数、已解决数（request_state=resolved）、创建至 resolved_at 的平均解决时长、customers 按 category 分组数量、requests 按 created_at 的每日趋势；均按调用角色可读行范围实时计算，且仅 manager/service 可读取指标",
      "权限管理：manager 拥有全部记录的动作权限；service 仅在 assigned 行范围内操作请求/任务；employee 仅在 own 行范围内创建与查询自己的请求",
      "字段中文 label、角色 label（管理人员/服务人员/普通员工）、状态 choice_labels（new=待处理、active=处理中、resolved=已解决）、动作 label（start=开始处理、resolve=标记解决）与统计 label 均为中文；关联字段展示可读的客户名称/请求标题/负责人用户名而非 ID"
    ],
    "acceptance": [
      "customers、requests、tasks 三个实体存在且字段清单与封闭合同完全一致，无额外业务字段；系统自动提供 id/created_at/updated_at/created_by/archived_at，业务字段中不重复声明",
      "customers.name/organization/contact 支持关键词搜索；category 支持企业/个人/合作伙伴精确筛选；name、category 必填校验生效",
      "requests.title/detail 支持关键词搜索；priority 支持普通/紧急精确筛选；title、detail、customer_id、request_state、priority 必填校验生效",
      "tasks.title/detail 支持关键词搜索；title、detail、request_id、task_state 必填校验生效",
      "创建请求或任务后状态为 new；manager/service 执行 start 后状态变为 active，执行 resolve 后状态变为 resolved 且 resolved_at 被自动写入（非空）",
      "employee 或任何非 manager/service 角色无法执行状态流转，也无法通过普通编辑表单直接修改 request_state/task_state 或 assignee_id，绕过尝试被拒绝",
      "manager 可创建、修改、查询、归档客户并查看客户审计；service 与 employee 只能读取客户，不能修改或归档",
      "manager 可对全部 requests/tasks 执行创建、分配、修改、备注、流转、归档、查看处理历史与审计",
      "service 只能读取与操作 assignee_id 为自己的 requests/tasks：对未分配给自己的记录执行读取或修改被拒绝，且不会出现在列表结果中",
      "employee 可创建请求并只查询到自己创建的请求（scope=own），无法分配、无法改变状态、无法读取团队统计（指标接口拒绝）",
      "客户详情展示该客户关联的 requests；请求详情展示关联 tasks；当被关联记录不在当前角色可见范围时，该关联结果不出现，不泄露其他员工记录",
      "请求或任务被分配、添加处理备注、发生状态变化、被解决时产生持久化站内提醒；解决请求后，请求创建者能在自己的通知收件箱看到对应提醒；提醒为 in_app，不发送邮件或短信",
      "接近或超过 due_at 的请求/任务产生逾期站内提醒",
      "请求与任务的每次修改都写入不可修改的审计历史，状态变化可追踪，普通用户无删除或改写审计记录的能力",
      "指标接口返回真实计算结果：requests 总数为 count；已解决数为 request_state=resolved 的 count；平均解决时长为 created_at→resolved_at 的平均秒数（无样本返回空而非 0 或假图）；customers 按 category 的 group_count；requests 按 created_at 的 UTC 每日 time_count",
      "指标按调用角色行范围计算：service 的 requests 指标只统计分配给自己的记录；employee 调用指标被拒绝",
      "所有业务权限、关系、流程、提醒和指标均由 business 可执行合同声明，custom_rules 为空；无法通过自定义脚本实现任意逻辑",
      "端到端验收使用合成账号与客户数据，在独立交付数据库、锁定依赖、浏览器与重启后重跑完整流程（登录、建客户、建请求、分配、流转、备注、提醒、统计）均通过"
    ],
    "questions": [],
    "assumptions": [
      "共享数据范围 shared 下的行权限由角色 scope 控制：manager=all，service=assigned，employee=own；shared 不代表所有人都能读取全部记录。",
      "站内提醒只使用持久化消息与通知收件箱，不接入邮件、短信或真实客户联系方式。",
      "统计引用系统自动提供的 created_at 作为趋势与平均时长起点，不为统计新增业务字段。",
      "日期格式说明与模板能力元数据不构成新增业务字段或额外筛选条件。"
    ],
    "unsupported": [],
    "limitations": [
      "本模板为 shared 范围，不支持 per-user 完全隔离（per-user-isolation），因此未采用个人私有记录模式。",
      "不支持外部服务调用、支付、邮件/短信、爬虫或任意代码执行；custom_rules 保持为空。",
      "未要求公众匿名访问或对外公开门户，系统仅面向内部团队账号使用。",
      "未要求外部数据采集或客户联系方式同步；客户联系方式仅作为文本字段记录。",
      "本次环境仅提供 FastapiAdmin 原生 Vue 管理端界面，不生成其他前端风格的界面。",
      "datetime 字段（resolved_at、due_at）仅存储时间戳，不提供搜索、筛选或日期范围条件。"
    ],
    "recommendations": [
      "所有文本字段 min_length=0（必填性由 required 承担，不另设字符下限）：customers.name≤120、organization≤160、contact≤200；requests/tasks 的 title≤200、detail≤3000。",
      "逻辑关联字段用 text 声明（requests.customer_id→customers、requests.assignee_id→$users、tasks.request_id→requests、tasks.assignee_id→$users），由原生生成器落地为真实外键并做存在性校验，不实现为无校验备注文本。",
      "关联字段在界面显示可读名称（客户名称、请求标题、负责人用户名），不直接展示 ID。",
      "状态存储值保持 new/active/resolved，界面通过 choice_labels 展示 待处理/处理中/已解决；动作名保持 start/resolve，界面 label 为 开始处理/标记解决。",
      "客户实体不启用处理备注，仅启用审计与归档；请求与任务启用处理备注、分配、状态流转与归档。",
      "逾期提醒以 due_at 为触发字段，按 in_app 渠道去重投递；通知已读状态仅对该接收者可见。"
    ],
    "facts": {
      "scope": "shared",
      "entities_closed": true,
      "system_fields": [
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "archived_at"
      ],
      "entity_fields": {
        "customers": [
          "name",
          "organization",
          "contact",
          "category"
        ],
        "requests": [
          "title",
          "detail",
          "customer_id",
          "assignee_id",
          "request_state",
          "resolved_at",
          "due_at",
          "priority"
        ],
        "tasks": [
          "title",
          "detail",
          "request_id",
          "assignee_id",
          "task_state",
          "resolved_at",
          "due_at"
        ]
      },
      "search_and_filter_targets": {
        "customers": {
          "keyword_search": [
            "name",
            "organization",
            "contact"
          ],
          "exact_filter": [
            "category"
          ]
        },
        "requests": {
          "keyword_search": [
            "title",
            "detail"
          ],
          "exact_filter": [
            "priority"
          ]
        },
        "tasks": {
          "keyword_search": [
            "title",
            "detail"
          ],
          "exact_filter": []
        }
      },
      "ui_labels": {
        "roles": {
          "manager": "管理人员",
          "service": "服务人员",
          "employee": "普通员工"
        },
        "choice_labels": {
          "requests.request_state": {
            "new": "待处理",
            "active": "处理中",
            "resolved": "已解决"
          },
          "tasks.task_state": {
            "new": "待处理",
            "active": "处理中",
            "resolved": "已解决"
          }
        },
        "transition_labels": {
          "start": "开始处理",
          "resolve": "标记解决"
        },
        "relation_display": "关联字段显示当前角色可读的客户名称、请求标题或负责人用户名，不显示 ID/UUID"
      },
      "notifications_scope": "仅持久化站内消息（in_app），无邮件、短信或真实客户联系方式",
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
            "target_entity": "customers"
          },
          {
            "entity": "requests",
            "field": "assignee_id",
            "target_entity": "$users"
          },
          {
            "entity": "tasks",
            "field": "request_id",
            "target_entity": "requests"
          },
          {
            "entity": "tasks",
            "field": "assignee_id",
            "target_entity": "$users"
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
              "read_audit"
            ],
            "scope": "all"
          },
          {
            "role": "service",
            "entity": "customers",
            "actions": [
              "read"
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
              "transition",
              "add_note",
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
              "transition",
              "add_note",
              "read_history",
              "read_audit"
            ],
            "scope": "assigned"
          },
          {
            "role": "service",
            "entity": "customers",
            "actions": [
              "read_metrics"
            ],
            "scope": "all"
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
            "recipient": "assignee",
            "channel": "in_app"
          },
          {
            "entity": "requests",
            "event": "note_added",
            "recipient": "assignee",
            "channel": "in_app"
          },
          {
            "entity": "requests",
            "event": "note_added",
            "recipient": "creator",
            "channel": "in_app"
          },
          {
            "entity": "requests",
            "event": "transitioned",
            "transition": "start",
            "recipient": "creator",
            "channel": "in_app"
          },
          {
            "entity": "requests",
            "event": "transitioned",
            "transition": "resolve",
            "recipient": "creator",
            "channel": "in_app"
          },
          {
            "entity": "requests",
            "event": "transitioned",
            "transition": "resolve",
            "recipient": "assignee",
            "channel": "in_app"
          },
          {
            "entity": "requests",
            "event": "due",
            "recipient": "assignee",
            "due_field": "due_at",
            "channel": "in_app"
          },
          {
            "entity": "tasks",
            "event": "assigned",
            "recipient": "assignee",
            "channel": "in_app"
          },
          {
            "entity": "tasks",
            "event": "note_added",
            "recipient": "assignee",
            "channel": "in_app"
          },
          {
            "entity": "tasks",
            "event": "transitioned",
            "transition": "start",
            "recipient": "assignee",
            "channel": "in_app"
          },
          {
            "entity": "tasks",
            "event": "transitioned",
            "transition": "resolve",
            "recipient": "assignee",
            "channel": "in_app"
          },
          {
            "entity": "tasks",
            "event": "due",
            "recipient": "assignee",
            "due_field": "due_at",
            "channel": "in_app"
          }
        ],
        "metrics": [
          {
            "name": "request_total",
            "label": "服务请求总数",
            "entity": "requests",
            "kind": "count"
          },
          {
            "name": "request_resolved",
            "label": "已解决请求数",
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
            "name": "request_avg_resolution",
            "label": "平均解决时长",
            "entity": "requests",
            "kind": "average_duration",
            "start_field": "created_at",
            "end_field": "resolved_at",
            "unit": "seconds"
          },
          {
            "name": "customer_category",
            "label": "客户分类分布",
            "entity": "customers",
            "kind": "group_count",
            "group_by": "category"
          },
          {
            "name": "request_daily_trend",
            "label": "服务请求每日趋势",
            "entity": "requests",
            "kind": "time_count",
            "time_field": "created_at",
            "bucket": "day",
            "timezone": "UTC"
          }
        ]
      },
      "custom_rules": [],
      "no_external_side_effects": true
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
        "filterable": false,
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
        "filterable": false,
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
        "filterable": false,
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
        "searchable": false,
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
        "filterable": false,
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
        "filterable": false,
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
        "searchable": false,
        "filterable": false,
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
        "searchable": false,
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
        "filterable": false,
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
        "filterable": false,
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
        "searchable": false,
        "filterable": false,
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
    "entity_requirements": [
      {
        "entity": "customers",
        "fields": [
          "name",
          "organization",
          "contact",
          "category"
        ],
        "additional_fields": false
      },
      {
        "entity": "requests",
        "fields": [
          "title",
          "detail",
          "customer_id",
          "assignee_id",
          "request_state",
          "resolved_at",
          "due_at",
          "priority"
        ],
        "additional_fields": false
      },
      {
        "entity": "tasks",
        "fields": [
          "title",
          "detail",
          "request_id",
          "assignee_id",
          "task_state",
          "resolved_at",
          "due_at"
        ],
        "additional_fields": false
      }
    ],
    "additional_entities": false,
    "changes": []
  },
  "candidate_plan": {
    "title": "内部客户服务管理平台",
    "data_scope": "shared",
    "entities": [
      {
        "name": "customers",
        "description": "客户档案",
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
            "choice_labels": {},
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
            "label": "请求详情",
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
            "label": "关联客户",
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
            "label": "请求状态",
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
            "choice_labels": {},
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
            "label": "任务详情",
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
      "customers、requests、tasks 三个实体存在且字段清单与封闭合同完全一致，无额外业务字段；系统自动提供 id/created_at/updated_at/created_by/archived_at，业务字段中不重复声明",
      "customers.name/organization/contact 支持关键词搜索；category 支持企业/个人/合作伙伴精确筛选；name、category 必填校验生效",
      "requests.title/detail 支持关键词搜索；priority 支持普通/紧急精确筛选；title、detail、customer_id、request_state、priority 必填校验生效",
      "tasks.title/detail 支持关键词搜索；title、detail、request_id、task_state 必填校验生效",
      "创建请求或任务后状态为 new；manager/service 执行 start 后状态变为 active，执行 resolve 后状态变为 resolved 且 resolved_at 被自动写入（非空）",
      "employee 或任何非 manager/service 角色无法执行状态流转，也无法通过普通编辑表单直接修改 request_state/task_state 或 assignee_id，绕过尝试被拒绝",
      "manager 可创建、修改、查询、归档客户并查看客户审计；service 与 employee 只能读取客户，不能修改或归档",
      "manager 可对全部 requests/tasks 执行创建、分配、修改、备注、流转、归档、查看处理历史与审计",
      "service 只能读取与操作 assignee_id 为自己的 requests/tasks：对未分配给自己的记录执行读取或修改被拒绝，且不会出现在列表结果中",
      "employee 可创建请求并只查询到自己创建的请求（scope=own），无法分配、无法改变状态、无法读取团队统计（指标接口拒绝）",
      "客户详情展示该客户关联的 requests；请求详情展示关联 tasks；当被关联记录不在当前角色可见范围时，该关联结果不出现，不泄露其他员工记录",
      "请求或任务被分配、添加处理备注、发生状态变化、被解决时产生持久化站内提醒；解决请求后，请求创建者能在自己的通知收件箱看到对应提醒；提醒为 in_app，不发送邮件或短信",
      "接近或超过 due_at 的请求/任务产生逾期站内提醒",
      "请求与任务的每次修改都写入不可修改的审计历史，状态变化可追踪，普通用户无删除或改写审计记录的能力",
      "指标接口返回真实计算结果：requests 总数为 count；已解决数为 request_state=resolved 的 count；平均解决时长为 created_at→resolved_at 的平均秒数（无样本返回空而非 0 或假图）；customers 按 category 的 group_count；requests 按 created_at 的 UTC 每日 time_count",
      "指标按调用角色行范围计算：service 的 requests 指标只统计分配给自己的记录；employee 调用指标被拒绝",
      "所有业务权限、关系、流程、提醒和指标均由 business 可执行合同声明，custom_rules 为空；无法通过自定义脚本实现任意逻辑",
      "端到端验收使用合成账号与客户数据，在独立交付数据库、锁定依赖、浏览器与重启后重跑完整流程（登录、建客户、建请求、分配、流转、备注、提醒、统计）均通过"
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
            "read_audit"
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
            "transition",
            "add_note",
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
            "transition",
            "add_note",
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
          "event": "note_added",
          "recipient": "creator",
          "transition": null,
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "requests",
          "event": "transitioned",
          "recipient": "creator",
          "transition": "start",
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
          "event": "transitioned",
          "recipient": "assignee",
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
          "name": "request_total",
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
          "name": "request_resolved",
          "label": "已解决请求数",
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
          "name": "request_avg_resolution",
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
          "name": "customer_category",
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
          "name": "request_daily_trend",
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
