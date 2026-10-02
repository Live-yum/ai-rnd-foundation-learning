# tests/fixtures/customer_design_diagnostics/2a4106f/python-basic.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/2a4106f/python-basic.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L1413。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`47098`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/2a4106f/python-basic.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0ad2c86625dd7454bab688edf402c59b4a3d28ba3e4f5eb07f8c3b9747dfd8a5"} -->
````json
// tests/fixtures/customer_design_diagnostics/2a4106f/python-basic.json
{
  "format": "customer-design-diagnostic-v1",
  "approval_status": "unapproved",
  "execution_authorized": false,
  "purpose": "offline_contract_validation_only",
  "template": "python-basic",
  "requirement": {
    "summary": "基于 FastAPI + 轻量管理页面（simple-admin / SQLite）交付内部客户服务管理平台，采用 shared 业务范围与可执行 business 合同：三个固定实体 customers、requests、tasks，三角色 manager/service/employee（管理人员/服务人员/普通员工），bootstrap_role=manager、注册默认 employee。客户档案维护与搜索、服务请求全生命周期跟踪（分配、备注、命名状态流转、归档、审计）、协作任务、持久化站内提醒（分配/备注/状态变化/解决/逾期）、按角色数据范围计算的统计指标，全部通过声明式外键关系、行权限、命名转换、提醒与指标契约实现；不引入外部采集、支付、邮件短信或任意脚本。",
    "users": [
      "管理人员（manager）：管理客户、请求、任务的全部记录，负责分配、状态流转、归档、审计与团队统计（scope=all）",
      "服务人员（service）：只处理分配给自己的请求与任务，可查询、修改、添加备注、转换状态、查看处理历史与审计，并按本人可见行查看指标（scope=assigned）",
      "普通员工（employee）：提交并查看自己创建的客户服务请求（scope=own），可查询客户资料，不能分配、改变状态或读取团队统计"
    ],
    "data_scope": "shared",
    "features": [
      "客户档案管理：管理人员创建、修改、查询、归档客户，维护 name、organization、contact、category",
      "客户搜索：对 name、organization、contact 进行关键词搜索，对 category（企业/个人/合作伙伴）进行精确筛选",
      "客户资料查询：服务人员与普通员工可查询客户基础资料",
      "客户历史服务记录：客户详情展示该客户关联的历史服务请求，且只展示当前角色有权读取的记录",
      "服务请求管理：创建、修改、查询历史请求，维护 title、detail、customer_id、priority、request_state、assignee_id、due_at",
      "请求负责人分配：通过分配动作设置 assignee_id（关联 $users），普通表单不能绕过",
      "命名状态流转：请求初始 new，start 为 new→active，resolve 为 active→resolved 并自动写入 resolved_at，仅 manager/service 可执行",
      "请求处理备注：追加式处理记录，可查看完整处理过程（read_history）",
      "请求归档与不可修改审计历史（append-only audit）",
      "协作任务管理：管理人员创建 tasks 并分配，任务同样支持备注、命名状态流转、归档与审计",
      "请求详情展示关联协作任务，关联查询遵守任务行权限，不泄露其他员工记录",
      "站内提醒：负责人分配、处理备注、状态变化、解决与逾期均产生持久化站内通知，接收者在自己收件箱查看，已读状态私有",
      "数据统计：requests 总数、已解决数（request_state=resolved）、创建至 resolved_at 的平均解决时长（秒）、customers 按 category 分组数、requests 按 created_at 的每日趋势（UTC）",
      "统计按当前角色可读范围在服务端计算，服务人员只统计本人可见行，不用预设数字或前端假图",
      "角色与行权限：manager=all、service=assigned、employee=own，注册默认 employee 不能自行提升权限",
      "基于既有项目技术体系交付 FastAPI 后端与 simple-admin 轻量管理页面，使用共享交付数据库、锁定依赖，并提供部署运行方式与必要测试"
    ],
    "acceptance": [
      "业务范围为 shared：三个角色在同一工作区内协作，行可见范围严格由权限矩阵控制（manager=all、service=assigned、employee=own），shared 不代表任何人可读取全部数据。",
      "客户可创建、修改、查询、归档；name 必填且最长 120，organization 最长 160，contact 最长 200，category 必填且取值为企业/个人/合作伙伴之一。",
      "客户列表支持对 name、organization、contact 的关键词搜索，并支持按 category 精确筛选。",
      "客户详情可查看该客户关联的历史服务请求，且只返回当前角色有权读取的请求，不泄露其他员工的记录。",
      "服务请求可创建并跟踪：title 必填最长 200，detail 必填最长 3000，customer_id 必须指向存在的客户记录，priority 必填且取值为普通/紧急，可按 priority 精确筛选。",
      "新建请求初始 request_state=new；start 动作使 new→active；resolve 动作使 active→resolved 并自动写入 resolved_at；只有 manager/service 能执行这两个转换。",
      "负责人通过分配动作设置 assignee_id（关联 $users）；直接修改 request_state 或 assignee_id 的普通表单请求被拒绝或被动作流程接管。",
      "请求支持追加处理备注、查看处理过程与归档；每次变更在同一事务内产生服务端编写、不可修改的审计记录。",
      "服务人员只能查询和处理分配给自己的请求与任务（scope=assigned），包括备注、状态转换、处理历史与审计。",
      "普通员工可创建请求并只查询自己创建的请求（scope=own），不能分配负责人、改变状态或读取团队统计。",
      "任务 tasks 由管理人员创建并分配：title 必填最长 200，detail 必填最长 3000，request_id 必须指向存在的请求，task_state 初始 new，start/resolve 转换与 resolved_at 自动写入规则与请求一致。",
      "请求详情可查看关联协作任务，且只展示当前角色有权读取的任务，不泄露他人记录。",
      "站内提醒持久化：负责人分配（接收者=负责人）、处理备注（接收者=负责人，请求同时通知创建者）、状态变化（接收者=创建者）、逾期（按 due_at，接收者=负责人）分别产生 in_app 通知；已读状态仅接收者本人可见。",
      "解决请求后，创建者（提交者）能在自己的通知收件箱看到提醒。",
      "提醒渠道固定为 in_app，不发送邮件、短信，不联系真实客户联系方式。",
      "统计指标可用且为服务端按当前权限范围计算：requests 总数（count）、已解决数（request_state=resolved 的 count）、创建至 resolved_at 的平均解决时长（average_duration，start_field=created_at，单位秒）、customers 按 category 的 group_count、requests 按 created_at 的每日 time_count。",
      "只有 manager 与 service 可读取指标；服务人员的指标只统计其可见行（assigned），不返回团队全量数据。",
      "指标结果来自真实数据与角色范围计算，不是预设数字或前端静态图。",
      "customers、requests、tasks 均启用归档历史与不可修改审计；归档保留既有关系与历史记录，外键删除采用 restrict。",
      "注册默认角色为 employee，用户不能自行提升权限；bootstrap 角色为 manager，管理人员负责角色与团队业务管理。",
      "交付为 FastAPI + simple-admin 轻量管理页面，使用共享交付数据库与锁定依赖；重启后数据、权限与完整流程仍可验证，并提供部署运行方式与必要测试。",
      "系统自动提供 id、created_at、updated_at、created_by、archived_at，不在用户字段中重复声明；统计直接引用系统 created_at。"
    ],
    "questions": [],
    "assumptions": [
      "已授权的 autonomous 模式下，用户未进一步指定的界面与交互细节由本需求按模板可执行能力决定，不再回问用户。",
      "提醒中的逾期事件依据请求/任务的 due_at 与当前时间比较产生，不引入后台定时外呼。",
      "三个实体共享同一工作区数据，行可见性完全由 role/entity/actions/scope 权限矩阵决定。"
    ],
    "unsupported": [],
    "limitations": [
      "不包含外部网页采集、外部支付与公众匿名站点（本次未要求，模板亦不支持）。",
      "站内提醒仅 in_app，不集成邮件、短信或真实客户联系方式推送。",
      "不支持任意自定义脚本、外部消息投递或网络副作用；业务规则只在声明式 business 合同内表达，custom_rules 留空。",
      "界面仅提供 Python 轻量管理页面（simple-admin），不提供其他前端框架风格或独立 api-only 交付形态。"
    ],
    "recommendations": [
      "列表默认按 created_at 倒序、每页 20 条；关键词搜索采用不区分大小写的包含匹配，仅覆盖已声明的可搜索字段。",
      "未声明可筛选的字段（request_state、task_state、resolved_at、due_at、关系键）不提供界面筛选条件，避免与已确认的搜索/筛选范围冲突。",
      "归档记录默认从常规列表隐藏，管理页面提供切换查看归档；归档不删除关联与历史。",
      "处理备注为追加式、不可编辑或删除；审计记录同事务写入、不可修改。",
      "所有 datetime 以 UTC 存储（仅作为时间戳，不参与搜索或筛选），界面按本地时区以 YYYY-MM-DD HH:mm 展示。",
      "文本字段 min_length=0，必填性完全由 required 决定；统计报表由服务端计算并返回结构化数据，前端只负责渲染表格与趋势图。"
    ],
    "facts": {
      "backend": "fastapi",
      "frontend": "simple-admin（Python 轻量管理页面）",
      "database": "sqlite",
      "custom_rules": "留空，所有业务规则通过 business 可执行合同声明",
      "reminders": "仅持久化站内 in_app 提醒，不连接邮件、短信或真实客户联系方式",
      "acceptance_data": "只创建合成账号与客户数据",
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
            "archive": true,
            "audit": true,
            "notes": false
          },
          {
            "entity": "requests",
            "assignee_field": "assignee_id",
            "archive": true,
            "audit": true,
            "notes": true
          },
          {
            "entity": "tasks",
            "assignee_field": "assignee_id",
            "archive": true,
            "audit": true,
            "notes": true
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
            "entity": "customers",
            "actions": [
              "read",
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
            "role": "employee",
            "entity": "requests",
            "actions": [
              "create",
              "read"
            ],
            "scope": "own"
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
            "recipient": "creator",
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
            "recipient": "creator",
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
            "name": "requests_total",
            "label": "服务请求总数",
            "entity": "requests",
            "kind": "count"
          },
          {
            "name": "requests_resolved",
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
            "name": "requests_avg_resolution_seconds",
            "label": "平均解决时长（秒）",
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
            "label": "请求每日趋势",
            "entity": "requests",
            "kind": "time_count",
            "time_field": "created_at",
            "bucket": "day",
            "timezone": "UTC"
          }
        ]
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
        "date_range": null,
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
        "date_range": null,
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
        "date_range": null,
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
        "date_range": null,
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
            "label": "组织单位",
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
              "new": "新建",
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
              "new": "新建",
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
      "业务范围为 shared：三个角色在同一工作区内协作，行可见范围严格由权限矩阵控制（manager=all、service=assigned、employee=own），shared 不代表任何人可读取全部数据。",
      "客户可创建、修改、查询、归档；name 必填且最长 120，organization 最长 160，contact 最长 200，category 必填且取值为企业/个人/合作伙伴之一。",
      "客户列表支持对 name、organization、contact 的关键词搜索，并支持按 category 精确筛选。",
      "客户详情可查看该客户关联的历史服务请求，且只返回当前角色有权读取的请求，不泄露其他员工的记录。",
      "服务请求可创建并跟踪：title 必填最长 200，detail 必填最长 3000，customer_id 必须指向存在的客户记录，priority 必填且取值为普通/紧急，可按 priority 精确筛选。",
      "新建请求初始 request_state=new；start 动作使 new→active；resolve 动作使 active→resolved 并自动写入 resolved_at；只有 manager/service 能执行这两个转换。",
      "负责人通过分配动作设置 assignee_id（关联 $users）；直接修改 request_state 或 assignee_id 的普通表单请求被拒绝或被动作流程接管。",
      "请求支持追加处理备注、查看处理过程与归档；每次变更在同一事务内产生服务端编写、不可修改的审计记录。",
      "服务人员只能查询和处理分配给自己的请求与任务（scope=assigned），包括备注、状态转换、处理历史与审计。",
      "普通员工可创建请求并只查询自己创建的请求（scope=own），不能分配负责人、改变状态或读取团队统计。",
      "任务 tasks 由管理人员创建并分配：title 必填最长 200，detail 必填最长 3000，request_id 必须指向存在的请求，task_state 初始 new，start/resolve 转换与 resolved_at 自动写入规则与请求一致。",
      "请求详情可查看关联协作任务，且只展示当前角色有权读取的任务，不泄露他人记录。",
      "站内提醒持久化：负责人分配（接收者=负责人）、处理备注（接收者=负责人，请求同时通知创建者）、状态变化（接收者=创建者）、逾期（按 due_at，接收者=负责人）分别产生 in_app 通知；已读状态仅接收者本人可见。",
      "解决请求后，创建者（提交者）能在自己的通知收件箱看到提醒。",
      "提醒渠道固定为 in_app，不发送邮件、短信，不联系真实客户联系方式。",
      "统计指标可用且为服务端按当前权限范围计算：requests 总数（count）、已解决数（request_state=resolved 的 count）、创建至 resolved_at 的平均解决时长（average_duration，start_field=created_at，单位秒）、customers 按 category 的 group_count、requests 按 created_at 的每日 time_count。",
      "只有 manager 与 service 可读取指标；服务人员的指标只统计其可见行（assigned），不返回团队全量数据。",
      "指标结果来自真实数据与角色范围计算，不是预设数字或前端静态图。",
      "customers、requests、tasks 均启用归档历史与不可修改审计；归档保留既有关系与历史记录，外键删除采用 restrict。",
      "注册默认角色为 employee，用户不能自行提升权限；bootstrap 角色为 manager，管理人员负责角色与团队业务管理。",
      "交付为 FastAPI + simple-admin 轻量管理页面，使用共享交付数据库与锁定依赖；重启后数据、权限与完整流程仍可验证，并提供部署运行方式与必要测试。",
      "系统自动提供 id、created_at、updated_at、created_by、archived_at，不在用户字段中重复声明；统计直接引用系统 created_at。"
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
          "entity": "customers",
          "actions": [
            "read",
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
          "role": "employee",
          "entity": "requests",
          "actions": [
            "create",
            "read"
          ],
          "scope": "own"
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
          "recipient": "creator",
          "transition": "start",
          "due_field": null,
          "channel": "in_app"
        },
        {
          "entity": "tasks",
          "event": "transitioned",
          "recipient": "creator",
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
          "name": "requests_avg_resolution_seconds",
          "label": "平均解决时长（秒）",
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
          "label": "请求每日趋势",
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
