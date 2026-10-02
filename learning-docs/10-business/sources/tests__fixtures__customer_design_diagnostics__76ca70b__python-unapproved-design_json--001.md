# tests/fixtures/customer_design_diagnostics/76ca70b/python-unapproved-design.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/76ca70b/python-unapproved-design.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L1457。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`45095`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/76ca70b/python-unapproved-design.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "293da0b8cde09658f618ac76328eb1393b1d3eb79193456a419170adae1b4ecc"} -->
````json
// tests/fixtures/customer_design_diagnostics/76ca70b/python-unapproved-design.json
{
  "format": "customer-design-diagnostic-v1",
  "approval_status": "unapproved",
  "execution_authorized": false,
  "purpose": "offline_contract_validation_only",
  "template": "python-basic",
  "requirement": {
    "summary": "内部客户服务管理平台，业务范围 shared，固定三个实体 customers、requests、tasks 与三个角色 manager（管理人员）、service（服务人员）、employee（普通员工）。以声明式 business 契约实现关联外键、行级权限、负责人分配、命名状态流转（start/resolve，resolve 自动写 resolved_at）、追加只读审计、处理备注、归档、站内提醒与统计指标；字段清单穷尽封闭，不引入 published_on 等案例外字段。",
    "users": [
      "管理人员（manager）：团队业务管理、分配与统计，可操作全部记录",
      "服务人员（service）：只处理分配给自己的请求/任务（scope=assigned）",
      "普通员工（employee）：提交并查看自己创建的请求（scope=own），无分配、状态转换与统计权限"
    ],
    "data_scope": "shared",
    "features": [
      "客户档案管理：创建、修改、查询、归档客户，字段限于 name、organization、contact、category",
      "客户搜索：对 name、organization、contact 做关键词搜索，对 category 做精确筛选",
      "客户历史服务记录：客户详情查看关联历史服务请求，遵守被关联记录的行权限",
      "服务请求管理：创建、修改、分配负责人、状态转换、处理备注、归档、查看处理过程",
      "服务请求搜索：对 title、detail 做关键词搜索，对 priority 做精确筛选",
      "协作任务管理：任务创建、分配负责人、状态转换、处理备注、归档",
      "关联关系：requests.customer_id→customers，requests.assignee_id→$users，tasks.request_id→requests，tasks.assignee_id→$users，均为受校验外键",
      "命名状态流转：requests.request_state 与 tasks.task_state 初始 new，start/new→active，resolve/active→resolved 并自动写 resolved_at，仅 manager/service 可执行",
      "角色与行权限：manager scope=all；service scope=assigned 处理被分配的请求/任务；employee scope=own 创建并查询自己提交的请求",
      "不可修改的追加只读审计历史覆盖三个业务资源",
      "持久化站内提醒：负责人分配、处理备注、状态变化、解决、逾期；解决请求后提交者可在通知收件箱看到",
      "服务端计算统计：requests 总数、已解决数、创建至 resolved_at 平均解决时长、customers 按 category 分组计数、requests 按 created_at 每日趋势",
      "中文界面标签：字段 label、状态 choice_labels、角色 label、动作 label 与统计 label 均为中文，关联字段显示可读名称"
    ],
    "acceptance": [
      "以 manager 引导首个账号；新注册账号角色默认为 employee，注册后不能自行提升权限。",
      "customers 仅包含 name、organization、contact、category 四个业务字段；requests 仅包含 title、detail、customer_id、assignee_id、request_state、resolved_at、due_at、priority；tasks 仅包含 title、detail、request_id、assignee_id、task_state、resolved_at、due_at；不存在 published_on 或任何额外业务字段，也无遗漏。",
      "manager 可创建、修改、查询、归档客户并查看客户审计；service 与 employee 只能查询客户档案。",
      "requests 与 tasks 初始 request_state/task_state=new；仅 manager 与 service 可执行 start（new→active）与 resolve（active→resolved）；resolve 自动写入 resolved_at；通过普通表单直接改状态或改负责人被拒绝。",
      "manager 可对全部记录执行创建、查询、修改、分配、状态转换、添加备注、归档、查看处理历史与查看审计。",
      "service 只能查询并处理 assignee_id 为自己的 requests/tasks，越权读取或修改返回拒绝，且服务人员统计只覆盖其本人可见行。",
      "employee 可创建并查询 created_by 为自己的 requests，不能分配、不能改变状态、不能读取任何统计指标。",
      "客户详情列出其关联的历史服务请求，请求详情列出其关联协作任务；不可见记录不泄露。",
      "分配、备注、状态变化、解决、逾期均产生持久化站内提醒；请求被 resolve 后提交者能在自己的通知收件箱看到该提醒。",
      "统计为服务端真实计算结果：requests 计数、request_state=resolved 计数、created_at→resolved_at 平均时长（秒，缺端点样本排除，零样本返回 null）、customers 按 category 分组计数、requests 按 created_at 的 UTC 每日计数；非预置数字或前端假图。",
      "审计历史不可修改，归档不删除历史记录与关联关系；无效的 customer_id、request_id、assignee_id 被外键校验拒绝，而非当作自由备注文本接受。"
    ],
    "questions": [],
    "assumptions": [
      "注册开放且默认角色为 employee；bootstrap_role=manager 用于引导首个管理账号，角色管理权归 manager。",
      "customers 不启用处理备注（仅请求与任务启用备注、分配、状态转换与归档），三个资源均启用审计与归档。",
      "请求与任务的 due_at 为可选时间戳，逾期提醒以该字段为触发依据，接收者为当前负责人。"
    ],
    "unsupported": [],
    "limitations": [
      "提醒仅限持久化站内消息，不连接邮件、短信或真实客户联系方式。",
      "不提供外部服务调用、支付、爬虫、公共匿名站点或自定义任意代码；custom_rules 留空，业务合同与自定义规则不混用。",
      "验收仅创建合成账号与客户数据，不使用真实客户数据。",
      "本案例仅含 customers、requests、tasks 三个实体，且各实体字段清单封闭，不接受扩展字段或新增实体。"
    ],
    "recommendations": [
      "所有文本字段 min_length=0，必填性由 required 表达，不额外添加字符下限。",
      "resolved_at、due_at 采用 datetime，只存时间戳，不参与关键词搜索与筛选，不设日期范围条件（template date_range 仅对 date 字段生效）。",
      "customer_id、assignee_id、request_id 等逻辑外键不添加搜索、筛选或日期范围条件，由原生生成器转换为真实外键。",
      "created_at、updated_at、id、created_by、archived_at 由运行时提供，不在实体字段清单中重复声明；统计直接引用系统 created_at。",
      "状态枚举与动作在存储和校验中使用机器值 new/active/resolved 及动作名 start/resolve，界面通过 choice_labels（待处理/处理中/已解决）与动作 label（开始处理/标记解决）展示中文。",
      "列表页默认按系统 created_at 倒序分页展示当前角色可见行，关联字段渲染为可读名称（客户名称、请求标题、负责人用户名）。"
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
            "name": "requests_avg_resolution",
            "label": "平均解决时长",
            "entity": "requests",
            "kind": "average_duration",
            "start_field": "created_at",
            "end_field": "resolved_at"
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
            "time_field": "created_at"
          }
        ]
      },
      "ui": {
        "frontend": "simple-admin",
        "language": "zh-CN",
        "state_labels": {
          "new": "待处理",
          "active": "处理中",
          "resolved": "已解决"
        },
        "action_labels": {
          "start": "开始处理",
          "resolve": "标记解决"
        },
        "role_labels": {
          "manager": "管理人员",
          "service": "服务人员",
          "employee": "普通员工"
        },
        "collection_labels": {
          "customers": "客户",
          "requests": "服务请求",
          "tasks": "协作任务"
        },
        "related_display": "关联字段渲染当前角色可读的客户名称、请求标题或负责人用户名，不直接展示 UUID 或整数 ID"
      },
      "relation_contract": "关系键在声明合同中用 text，由原生生成器转换为受校验的真实外键，不得实现为不校验的备注文本。",
      "state_protection": "request_state、task_state 与 assignee_id 受命名动作保护，普通表单不能绕过状态转换或分配直接写入。",
      "audit": "三个业务资源记录不可修改的追加只读审计历史；归档保留历史与关联引用。",
      "dashboard": {
        "computed_server_side": true,
        "no_placeholder_numbers": true,
        "metrics_roles": [
          "manager",
          "service"
        ],
        "service_scope": "本人可见行"
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
        "description": "客户档案管理",
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
        "description": "服务请求管理",
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
        "description": "协作任务管理",
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
      "以 manager 引导首个账号；新注册账号角色默认为 employee，注册后不能自行提升权限。",
      "customers 仅包含 name、organization、contact、category 四个业务字段；requests 仅包含 title、detail、customer_id、assignee_id、request_state、resolved_at、due_at、priority；tasks 仅包含 title、detail、request_id、assignee_id、task_state、resolved_at、due_at；不存在 published_on 或任何额外业务字段，也无遗漏。",
      "manager 可创建、修改、查询、归档客户并查看客户审计；service 与 employee 只能查询客户档案。",
      "requests 与 tasks 初始 request_state/task_state=new；仅 manager 与 service 可执行 start（new→active）与 resolve（active→resolved）；resolve 自动写入 resolved_at；通过普通表单直接改状态或改负责人被拒绝。",
      "manager 可对全部记录执行创建、查询、修改、分配、状态转换、添加备注、归档、查看处理历史与查看审计。",
      "service 只能查询并处理 assignee_id 为自己的 requests/tasks，越权读取或修改返回拒绝，且服务人员统计只覆盖其本人可见行。",
      "employee 可创建并查询 created_by 为自己的 requests，不能分配、不能改变状态、不能读取任何统计指标。",
      "客户详情列出其关联的历史服务请求，请求详情列出其关联协作任务；不可见记录不泄露。",
      "分配、备注、状态变化、解决、逾期均产生持久化站内提醒；请求被 resolve 后提交者能在自己的通知收件箱看到该提醒。",
      "统计为服务端真实计算结果：requests 计数、request_state=resolved 计数、created_at→resolved_at 平均时长（秒，缺端点样本排除，零样本返回 null）、customers 按 category 分组计数、requests 按 created_at 的 UTC 每日计数；非预置数字或前端假图。",
      "审计历史不可修改，归档不删除历史记录与关联关系；无效的 customer_id、request_id、assignee_id 被外键校验拒绝，而非当作自由备注文本接受。",
      "customers 仅包含 name、organization、contact、category 四个业务字段；requests 仅包含 title、detail、customer_id、assignee_id、request_state、resolved_at、due_at、priority；tasks 仅包含 title、detail、request_id、assignee_id、task_state、resolved_at、due_at；不存在任何额外业务字段，也无遗漏。",
      "customers、requests、tasks 的字段清单穷尽封闭，不存在任何额外业务字段，也无遗漏。"
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
