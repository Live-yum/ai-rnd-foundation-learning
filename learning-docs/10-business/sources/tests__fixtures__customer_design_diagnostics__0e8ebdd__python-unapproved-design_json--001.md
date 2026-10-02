# tests/fixtures/customer_design_diagnostics/0e8ebdd/python-unapproved-design.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/0e8ebdd/python-unapproved-design.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L1599。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`49293`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/0e8ebdd/python-unapproved-design.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a492b0e6e379b6062698bfde77b05a52ba81aab7e7b47d2a84e15e5173fd7ab6"} -->
````json
// tests/fixtures/customer_design_diagnostics/0e8ebdd/python-unapproved-design.json
{
  "format": "customer-design-diagnostic-v1",
  "approval_status": "unapproved",
  "execution_authorized": false,
  "purpose": "offline_contract_validation_only",
  "template": "python-basic",
  "requirement": {
    "summary": "基于用户明确的客服演示契约，建设内部客户服务管理平台：业务范围 shared，三个封闭实体 customers、requests、tasks，三种角色 manager/service/employee。客户档案支持创建、修改、查询、归档、审计与关键词搜索、类别精确筛选；服务请求与协作任务支持分配、处理备注、命名状态流转（start: new→active；resolve: active→resolved 并自动写 resolved_at）、归档、处理历史与不可修改审计；站内提醒持久化覆盖分配、备注、状态变化、解决与逾期；统计包含请求总数、已解决数、平均解决时长、客户分类分布与每日趋势，并按角色数据范围计算。所有权限、关系、流程、提醒与指标以可执行 business 合同声明，custom_rules 留空。",
    "users": [
      "管理人员（manager）：管理客户档案与归档，创建并分配服务请求与协作任务，执行状态转换，查看处理历史、审计与全部统计。",
      "服务人员（service）：仅处理分配给自己的请求与任务（scope=assigned），可查询、修改、添加处理备注、执行状态转换、查看处理历史与审计，并查看本人可见行范围的统计。",
      "普通员工（employee）：提交并查询自己创建的请求（scope=own），接收请求解决等站内提醒；不能分配负责人、不能改变状态、不能读取团队统计。"
    ],
    "data_scope": "shared",
    "features": [
      "客户档案管理：创建、修改、查询、归档客户基础信息并记录不可修改的审计历史。",
      "客户检索：支持按名称、组织、联系方式进行关键词搜索，并按类别（企业/个人/合作伙伴）精确筛选。",
      "客户历史服务记录：客户详情可查看关联的历史服务请求，且遵守被关联记录的权限，不泄露其他员工记录。",
      "服务请求管理：创建服务请求、分配负责人、添加处理记录、修改处理状态、查看处理过程、查询历史请求与归档。",
      "任务协作：管理人员创建并分配协作任务，任务关联所属服务请求，同样支持备注、状态转换、归档与审计。",
      "命名状态流转：请求与任务初始状态 new，start（new→active）、resolve（active→resolved 并自动写入 resolved_at）仅 manager/service 可执行，状态与负责人受动作保护，普通表单不能绕过。",
      "处理历史与审计：三个业务资源均产生不可修改的审计历史，状态变化与处理过程可追溯。",
      "站内提醒：持久化提醒覆盖负责人分配、处理备注、状态变化、解决与逾期；请求解决后提交者可在自己的通知收件箱查看。",
      "角色与行级权限：manager 拥有全部记录的全部动作；service 仅作用于分配给自己的请求/任务；employee 仅作用于自己创建的请求。",
      "数据统计：请求总数、已解决数（request_state=resolved）、创建至 resolved_at 的平均解决时长、客户按类别分组分布、请求按 created_at 的每日趋势，均按当前角色的数据范围计算，不使用预设数字或前端假图。",
      "关联查询：客户详情查看历史请求、请求详情查看关联协作任务，均遵守被关联记录的权限。",
      "多模板界面：分别保留 Python 轻量管理页、FastapiAdmin Vue/Element Plus、Yudao Vben5 Ant Design 风格；api-only 无界面。"
    ],
    "acceptance": [
      "管理人员可创建、修改、查询、归档客户并查看客户审计记录；服务人员与普通员工只能查询客户，不能创建、修改或归档。",
      "客户列表支持按 name、organization、contact 关键词搜索，并支持按 category 精确筛选企业/个人/合作伙伴。",
      "服务请求可创建并分配 assignee_id；请求状态只能通过命名转换变更：start 由 new→active，resolve 由 active→resolved 并自动写入 resolved_at，普通表单无法直接修改状态或负责人。",
      "协作任务可由管理人员创建并分配，任务关联 request_id，并具备与请求一致的 start/resolve 命名转换、备注、归档与审计。",
      "服务人员仅能查询、修改、备注、转换、查看处理历史与审计分配给自己（scope=assigned）的请求与任务，不能看到他人记录。",
      "普通员工只能创建并查询自己创建的请求（scope=own），不能分配负责人、不能执行状态转换、不能读取团队统计。",
      "站内提醒持久化并覆盖分配、处理备注、状态变化（start/resolve）、解决与逾期；解决请求后提交者能在自己的通知收件箱看到提醒，消息按来源事件与接收者去重且已读状态仅本人可见。",
      "统计包含 requests 总数、按 request_state=resolved 筛选的已解决数、由 created_at 至 resolved_at 计算的平均解决时长（秒）、customers 按 category 的分组计数、requests 按 created_at 的每日趋势；服务人员指标只统计本人可见行。",
      "客户详情能查看关联的历史服务请求，请求详情能查看关联协作任务，且关联查询遵守被关联记录的权限，不泄露其他员工的记录。",
      "三个业务资源均产生不可修改的审计历史，处理备注与状态流转可追溯。",
      "系统自动提供 id/created_at/updated_at/created_by/archived_at，实体字段严格等于封闭清单，不出现 published_on 或其他案例字段。",
      "完整业务流程在真正独立的交付数据库、锁定依赖、浏览器与重启测试中验证通过，不以独立 CRUD 或新闻案例成功代替本案例验收。"
    ],
    "questions": [],
    "assumptions": [],
    "unsupported": [],
    "limitations": [
      "站内提醒仅使用应用内持久化消息，不接入邮件、短信或真实客户联系方式。",
      "模板本身不支持网页爬取、外部支付与公开匿名站点，本次也未要求这些能力。",
      "不添加外部服务、支付、邮件短信、爬虫或自定义任意代码，business 合同可执行的固定事务之外不做扩展网络副作用，custom_rules 留空。",
      "验收只创建合成账号与客户数据，不使用真实客户信息。",
      "api-only 前端不提供界面，不参与界面风格验收，也不冒充界面实现。"
    ],
    "recommendations": [
      "所有文本字段 min_length=0，必填与否由 required 决定，不额外设置字符下限。",
      "datetime 字段（resolved_at、due_at）仅存储时间戳，searchable=false、filterable=false、date_range=false；逻辑外键字段同样不添加搜索或日期范围。",
      "请求与任务状态存储值保持 new/active/resolved，通过 choice_labels 显示为 待处理/处理中/已解决；命名动作保留机器名 start、resolve，界面标签为“开始处理”“标记解决”。",
      "关联字段在界面显示当前角色可读的客户名称、请求标题或负责人用户名，不直接暴露 UUID 或整数 ID。",
      "统计指标与角色标签使用中文 label；平均时长单位为秒，每日趋势按 UTC 天分桶。",
      "统计直接引用系统提供的 created_at，不新增统计专用字段或日期字段。"
    ],
    "facts": {
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
            "recipient": "creator",
            "transition": "start",
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
            "filters": []
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
            "label": "请求每日趋势",
            "entity": "requests",
            "kind": "time_count",
            "time_field": "created_at",
            "bucket": "day",
            "timezone": "UTC"
          }
        ]
      },
      "ui": {
        "entity_labels": {
          "customers": "客户",
          "requests": "服务请求",
          "tasks": "协作任务"
        },
        "field_labels": {
          "customers.name": "客户名称",
          "customers.organization": "所属组织",
          "customers.contact": "联系方式",
          "customers.category": "客户类别",
          "requests.title": "请求标题",
          "requests.detail": "问题详情",
          "requests.customer_id": "所属客户",
          "requests.assignee_id": "负责人",
          "requests.request_state": "处理状态",
          "requests.priority": "优先级",
          "requests.resolved_at": "解决时间",
          "requests.due_at": "截止时间",
          "tasks.title": "任务标题",
          "tasks.detail": "任务详情",
          "tasks.request_id": "关联请求",
          "tasks.assignee_id": "负责人",
          "tasks.task_state": "任务状态",
          "tasks.resolved_at": "解决时间",
          "tasks.due_at": "截止时间"
        },
        "choice_labels": {
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
        "frontends": [
          "python 轻量管理页",
          "FastapiAdmin Vue/Element Plus",
          "Yudao Vben5 Ant Design"
        ],
        "api_only_has_ui": false
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
        "filterable": null,
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
        "filterable": null,
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
        "filterable": null,
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
        "filterable": null,
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
            "label": "客户类别",
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
            "label": "问题详情",
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
            "filterable": true,
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
            "filterable": true,
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
      "管理人员可创建、修改、查询、归档客户并查看客户审计记录；服务人员与普通员工只能查询客户，不能创建、修改或归档。",
      "客户列表支持按 name、organization、contact 关键词搜索，并支持按 category 精确筛选企业/个人/合作伙伴。",
      "服务请求可创建并分配 assignee_id；请求状态只能通过命名转换变更：start 由 new→active，resolve 由 active→resolved 并自动写入 resolved_at，普通表单无法直接修改状态或负责人。",
      "协作任务可由管理人员创建并分配，任务关联 request_id，并具备与请求一致的 start/resolve 命名转换、备注、归档与审计。",
      "服务人员仅能查询、修改、备注、转换、查看处理历史与审计分配给自己（scope=assigned）的请求与任务，不能看到他人记录。",
      "普通员工只能创建并查询自己创建的请求（scope=own），不能分配负责人、不能执行状态转换、不能读取团队统计。",
      "站内提醒持久化并覆盖分配、处理备注、状态变化（start/resolve）、解决与逾期；解决请求后提交者能在自己的通知收件箱看到提醒，消息按来源事件与接收者去重且已读状态仅本人可见。",
      "统计包含 requests 总数、按 request_state=resolved 筛选的已解决数、由 created_at 至 resolved_at 计算的平均解决时长（秒）、customers 按 category 的分组计数、requests 按 created_at 的每日趋势；服务人员指标只统计本人可见行。",
      "客户详情能查看关联的历史服务请求，请求详情能查看关联协作任务，且关联查询遵守被关联记录的权限，不泄露其他员工的记录。",
      "三个业务资源均产生不可修改的审计历史，处理备注与状态流转可追溯。",
      "系统自动提供 id/created_at/updated_at/created_by/archived_at，实体字段严格等于封闭清单，不出现 published_on 或其他案例字段。",
      "完整业务流程在真正独立的交付数据库、锁定依赖、浏览器与重启测试中验证通过，不以独立 CRUD 或新闻案例成功代替本案例验收。",
      "系统自动提供 id/created_at/updated_at/created_by/archived_at 等系统托管字段，实体字段严格等于封闭清单，不包含任何其他案例的字段（含发布类日期字段等）。"
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
          "recipient": "creator",
          "transition": "start",
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
          "filters": [
            {
              "field": "request_state",
              "op": "eq",
              "value": "resolved"
            },
            {
              "field": "resolved_at",
              "op": "ne",
              "value": null
            }
          ],
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
          "filters": [
            {
              "field": "category",
              "op": "in",
              "value": [
                "企业",
                "个人",
                "合作伙伴"
              ]
            }
          ],
          "unit": "seconds",
          "bucket": "day",
          "timezone": "UTC"
        },
        {
          "name": "request_daily_trend",
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
        },
        {
          "name": "task_total",
          "label": "协作任务总数",
          "entity": "tasks",
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
          "name": "task_resolved",
          "label": "已解决任务数",
          "entity": "tasks",
          "kind": "count",
          "group_by": null,
          "start_field": null,
          "end_field": null,
          "time_field": null,
          "filters": [
            {
              "field": "task_state",
              "op": "eq",
              "value": "resolved"
            }
          ],
          "unit": "seconds",
          "bucket": "day",
          "timezone": "UTC"
        },
        {
          "name": "task_avg_resolution",
          "label": "任务平均解决时长",
          "entity": "tasks",
          "kind": "average_duration",
          "group_by": null,
          "start_field": "created_at",
          "end_field": "resolved_at",
          "time_field": null,
          "filters": [
            {
              "field": "task_state",
              "op": "eq",
              "value": "resolved"
            },
            {
              "field": "resolved_at",
              "op": "ne",
              "value": null
            }
          ],
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
