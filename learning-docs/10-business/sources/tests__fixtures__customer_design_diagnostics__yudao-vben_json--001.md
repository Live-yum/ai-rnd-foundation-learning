# tests/fixtures/customer_design_diagnostics/yudao-vben.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/yudao-vben.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L1445。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`47653`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/yudao-vben.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "387597908c075b12193585499482402359ba99afcc8c99cd173e17d93f806afe"} -->
````json
// tests/fixtures/customer_design_diagnostics/yudao-vben.json
{
  "format": "customer-design-diagnostic-v1",
  "approval_status": "unapproved",
  "execution_authorized": false,
  "purpose": "offline_contract_validation_only",
  "template": "yudao-vben",
  "requirement": {
    "summary": "建设一套内部客户服务管理平台，基于芋道 Java 后端 + Vben5 Ant Design 前端 + PostgreSQL，以共享数据范围实现三个业务资源（customers、requests、tasks）的客户档案维护、服务请求跟踪、团队协作任务分配、处理备注、命名状态流转、不可修改审计、持久化站内提醒与角色化运营统计。角色固定为管理人员（manager）、服务人员（service）、普通员工（employee）：管理人员管理全部团队业务、分配与统计；服务人员只处理分配给自己的请求与任务；普通员工提交并查看自己创建的请求，不能分配、改状态或读取团队统计。客户详情可查看关联历史服务请求，请求详情可查看关联协作任务，且关联查询遵守被关联记录的行权限，不泄露他人记录。",
    "users": [
      "管理人员（manager）：管理团队业务、分配负责人、处理全部客户/请求/任务、查看审计与全部统计",
      "服务人员（service）：处理分配给自己的请求与任务，可查询客户、添加处理备注、执行状态流转、查看本人可见范围的统计",
      "普通员工（employee）：创建并查询自己提交的服务请求，查询客户资料，只读分配给自己的协作任务，不能分配、改变状态或读取团队统计"
    ],
    "data_scope": "shared",
    "features": [
      "客户管理：创建客户档案、修改客户信息、查询客户资料、归档客户",
      "客户搜索：按 name、organization、contact 关键词搜索，按 category（企业/个人/合作伙伴）精确筛选",
      "客户历史：在客户详情查看关联的历史服务请求",
      "服务请求管理：创建服务请求、分配负责人、修改处理状态、添加处理记录、查看处理过程、查询历史请求",
      "协作任务管理：创建协作任务、分配负责人、修改处理状态、添加处理记录、查看处理过程",
      "关联关系：requests.customer_id 关联 customers，requests.assignee_id 与 tasks.assignee_id 关联用户，tasks.request_id 关联 requests，并在详情中展示可读名称",
      "命名状态流转：请求与任务初始 new，start：new→active，resolve：active→resolved 并自动写入 resolved_at；仅 manager/service 可执行",
      "团队协作：任务分配、负责人变更、处理备注与状态变化追踪",
      "站内提醒：负责人分配、处理备注、状态变化、解决与逾期提醒持久化到收件箱",
      "审计历史：customers、requests、tasks 记录不可修改的操作历史",
      "运营统计：请求总数、已解决数、创建至解决的平决解决时长、客户按类别分布、请求每日趋势",
      "权限管理：管理人员/服务人员/普通员工按角色与行范围（all/assigned/own）控制操作与数据可见性"
    ],
    "acceptance": [
      "管理人员可创建、修改、查询、归档客户档案，并可查看客户审计历史；服务人员与普通员工只能查询客户资料，不能修改或归档。",
      "按 category 精确筛选客户可得到 企业/个人/合作伙伴 三类结果；按 name、organization、contact 关键词搜索可命中对应字段，且不会错误命中未声明字段。",
      "客户详情页展示该客户关联的历史服务请求，列表遵守当前角色的行权限，不出现其他员工不可见记录。",
      "用户可创建服务请求，title 与 detail 必填，customer_id 必须指向已存在的客户，priority 为 普通/紧急 之一；缺失或非法值被拒绝。",
      "管理人员或服务人员可将服务请求/任务分配给某个用户；普通员工不能执行分配动作，也不能通过普通表单直接修改 assignee_id 或状态。",
      "请求与任务创建后初始状态为 new；执行 start 后变为 active，执行 resolve 后变为 resolved 并自动写入 resolved_at；非法流转（如 new→resolved）被拒绝。",
      "只有 manager 与 service 可执行状态流转；employee 调用流转或分配接口被拒绝。",
      "服务人员只能查询、修改、备注、流转和查看审计分配给自己的请求与任务（scope=assigned），不能读取或修改其他服务人员的记录。",
      "普通员工只能创建和查询自己提交的请求（scope=own）；不能分配、不能改变状态、不能读取团队统计。",
      "服务请求与协作任务支持添加处理备注，备注与操作记录一起进入不可修改的审计历史，任何角色都无法编辑或删除历史审计条目。",
      "请求详情可查看关联的协作任务，任务详情可查看所属请求；关联查询遵守被关联记录的行权限，普通员工看不到不属于自己的关联记录。",
      "分配负责人、添加处理备注、状态变化、请求解决时产生持久化站内提醒；请求被解决后提交者可在自己的通知收件箱看到提醒，重启服务后提醒仍存在。",
      "逾期提醒依据 due_at 与当前时间判定，并在站内收件箱中呈现，不发送邮件或短信。",
      "统计至少包含：requests 总数（count）、request_state=resolved 的已解决数（count）、创建至 resolved_at 的平均解决时长（average_duration，start_field=created_at）、customers 按 category 分组计数（group_count）、requests 按 created_at 的每日趋势（time_count）。",
      "统计接口只允许 manager 与 service 调用；服务人员看到的统计只按本人可见行计算，管理人员看到全部数据，数值来自真实业务数据而非固定值或前端假图。",
      "所有关联字段在界面上显示当前角色可读的客户名称、请求标题或负责人用户名，不直接展示整数 ID 或 UUID。",
      "请求/任务状态在界面显示为 待处理/处理中/已解决，动作显示为 开始处理/标记解决，存储与动作名仍为 new/active/resolved、start/resolve。",
      "结算界面按所选模板保留原生风格：Python 轻量管理页、FastapiAdmin 原生 Vue/Fa/Element Plus 或芋道 Java/Vben5 Ant Design，不混用样式冒充。",
      "项目遵循已有代码规范与既有组件/基础设施，前后端架构一致，包含必要自动化测试，并提供可执行的部署运行方式。",
      "在真正独立的交付数据库上执行完整端到端流程（创建客户→创建请求→分配→添加备注→流转→解决→查看提醒→查看统计），并在浏览器验证与服务重启后确认数据与审计仍然存在。"
    ],
    "questions": [],
    "assumptions": [
      "数据范围为 shared，行权限通过角色作用域 all/assigned/own 表达，不采用物理逐用户隔离。",
      "状态与负责人的修改只能通过声明式动作（分配、start、resolve）完成，普通表单不提供直接改写入口。",
      "审计历史为追加型，任何角色都不能编辑或删除历史条目。",
      "统计引用系统提供的 created_at，不需要额外声明创建时间字段。",
      "普通员工对协作任务仅有分配给自己的只读权限。"
    ],
    "unsupported": [],
    "limitations": [
      "本案例未要求公众匿名访问、对外网站或爬虫采集，系统为内部平台，仅登录用户可访问。",
      "提醒仅使用持久化的站内消息，不连接邮件、短信或真实客户联系方式。",
      "未要求支付、外部服务调用或自定义任意代码执行，业务以声明式合同与 custom_rules 为空的方式实现。",
      "验收仅创建合成账号与合成客户数据，不使用真实客户隐私数据。",
      "模板的 per-user-isolation 不适用于本案例：数据范围为 shared，行权限通过角色的 all/assigned/own 作用域实现，而非物理隔离。",
      "所有实体 id/created_at/updated_at/created_by/archived_at 由运行时提供，不作为业务字段声明；统计直接引用系统 created_at。"
    ],
    "recommendations": [
      "日期与时间展示统一使用 YYYY-MM-DD（含时间时按模板原生格式展示），datetime 字段仅存储时间戳，不参与搜索、筛选或日期区间查询。",
      "文本字段最小长度统一为 0（必填性由 required 承担）：customers.name ≤120、organization ≤160、contact ≤200；requests/tasks 的 title ≤200、detail ≤3000。",
      "逻辑外键 customer_id、assignee_id、request_id 在声明合同中为 text，由原生生成器转换为真实整数外键并做存在性校验，不实现为无校验的备注文本。",
      "任务由管理人员创建并分配；普通员工只读分配给自己的任务，可恢复为仅能查看与自身请求相关的任务，以进一步减少越权读取风险。",
      "逾期提醒判定建议以 due_at 早于当前时间且状态非 resolved 为条件，在同一持久化通知表中生成，避免额外定时基础设施。",
      "服务人员统计建议在查询层自动叠加 assignee_id = 当前用户的过滤条件，确保行范围与列表一致。",
      "分类与状态的界面下拉选项建议直接取用合同声明的 choices 与 choice_labels，避免前后端各自硬编码造成不一致。"
    ],
    "facts": {
      "business": {
        "scope": "shared",
        "bootstrap_role": "manager",
        "registration_default_role": "employee",
        "self_elevation_allowed": false,
        "custom_rules": "",
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
        "resources": [
          {
            "name": "customers",
            "label": "客户",
            "fields": [
              "name",
              "organization",
              "contact",
              "category"
            ],
            "audit_history": "append-only",
            "archive": true,
            "handling_notes": false,
            "assignment": false,
            "state_transitions": []
          },
          {
            "name": "requests",
            "label": "服务请求",
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
            "audit_history": "append-only",
            "archive": true,
            "handling_notes": true,
            "assignment": true,
            "initial_state": "new",
            "state_transitions": [
              "start",
              "resolve"
            ]
          },
          {
            "name": "tasks",
            "label": "协作任务",
            "fields": [
              "title",
              "detail",
              "request_id",
              "assignee_id",
              "task_state",
              "resolved_at",
              "due_at"
            ],
            "audit_history": "append-only",
            "archive": true,
            "handling_notes": true,
            "assignment": true,
            "initial_state": "new",
            "state_transitions": [
              "start",
              "resolve"
            ]
          }
        ],
        "relations": [
          {
            "from": "requests",
            "field": "customer_id",
            "to": "customers",
            "kind": "many-to-one",
            "required": true
          },
          {
            "from": "requests",
            "field": "assignee_id",
            "to": "$users",
            "kind": "many-to-one",
            "required": false
          },
          {
            "from": "tasks",
            "field": "request_id",
            "to": "requests",
            "kind": "many-to-one",
            "required": true
          },
          {
            "from": "tasks",
            "field": "assignee_id",
            "to": "$users",
            "kind": "many-to-one",
            "required": false
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
              "view_audit"
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
              "assign",
              "note",
              "transition",
              "archive",
              "view_audit"
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
              "assign",
              "note",
              "transition",
              "archive",
              "view_audit"
            ],
            "scope": "all"
          },
          {
            "role": "manager",
            "entity": "metrics",
            "actions": [
              "read"
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
            "role": "service",
            "entity": "requests",
            "actions": [
              "read",
              "update",
              "note",
              "transition",
              "view_audit"
            ],
            "scope": "assigned"
          },
          {
            "role": "service",
            "entity": "tasks",
            "actions": [
              "read",
              "update",
              "note",
              "transition",
              "view_audit"
            ],
            "scope": "assigned"
          },
          {
            "role": "service",
            "entity": "metrics",
            "actions": [
              "read"
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
          },
          {
            "role": "employee",
            "entity": "tasks",
            "actions": [
              "read"
            ],
            "scope": "assigned"
          }
        ],
        "workflows": [
          {
            "entity": "requests",
            "field": "request_state",
            "transitions": [
              {
                "name": "start",
                "label": "开始处理",
                "from": "new",
                "to": "active",
                "roles": [
                  "manager",
                  "service"
                ]
              },
              {
                "name": "resolve",
                "label": "标记解决",
                "from": "active",
                "to": "resolved",
                "roles": [
                  "manager",
                  "service"
                ],
                "sets": {
                  "resolved_at": "now"
                }
              }
            ]
          },
          {
            "entity": "tasks",
            "field": "task_state",
            "transitions": [
              {
                "name": "start",
                "label": "开始处理",
                "from": "new",
                "to": "active",
                "roles": [
                  "manager",
                  "service"
                ]
              },
              {
                "name": "resolve",
                "label": "标记解决",
                "from": "active",
                "to": "resolved",
                "roles": [
                  "manager",
                  "service"
                ],
                "sets": {
                  "resolved_at": "now"
                }
              }
            ]
          }
        ],
        "notifications": {
          "channel": "in-app",
          "persistent": true,
          "triggers": [
            "assignment",
            "handling_note",
            "state_change",
            "resolved",
            "overdue"
          ],
          "recipients": [
            "assignee",
            "request_submitter"
          ],
          "overdue_rule": "due_at 早于当前时间且状态非 resolved 时生成逾期提醒"
        },
        "metrics": [
          {
            "name": "requests_total",
            "label": "服务请求总数",
            "type": "count",
            "entity": "requests"
          },
          {
            "name": "requests_resolved",
            "label": "已解决请求数",
            "type": "count",
            "entity": "requests",
            "filter": {
              "request_state": "resolved"
            }
          },
          {
            "name": "avg_resolution_duration",
            "label": "平均解决时长",
            "type": "average_duration",
            "entity": "requests",
            "start_field": "created_at",
            "end_field": "resolved_at"
          },
          {
            "name": "customers_by_category",
            "label": "客户分类分布",
            "type": "group_count",
            "entity": "customers",
            "group_by": "category"
          },
          {
            "name": "requests_daily_trend",
            "label": "请求每日趋势",
            "type": "time_count",
            "entity": "requests",
            "time_field": "created_at",
            "bucket": "day"
          }
        ],
        "metrics_roles": [
          "manager",
          "service"
        ],
        "metrics_scope": "manager=all；service=assigned（只按本人可见行计算）"
      },
      "labels": {
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
        "display_relations": [
          "requests.customer_id 显示当前角色可读的客户 name",
          "requests.assignee_id 显示负责人用户名",
          "tasks.request_id 显示当前角色可读的请求 title",
          "tasks.assignee_id 显示负责人用户名"
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
        "filterable": false,
        "date_range": false,
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
        "date_range": false,
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
        "date_range": false,
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
        "date_range": false,
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
        "date_range": false,
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
        "date_range": false,
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
        "date_range": false,
        "choices": [
          "new",
          "active",
          "resolved"
        ]
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
        "date_range": false,
        "choices": [
          "普通",
          "紧急"
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
        "field": "title",
        "entity": "tasks",
        "kind": "text",
        "required": true,
        "min_length": 0,
        "max_length": 200,
        "searchable": true,
        "filterable": false,
        "date_range": false,
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
        "date_range": false,
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
        "date_range": false,
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
            "label": "单位名称",
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
            "label": "联系人",
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
            "label": "请求负责人",
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
            "label": "任务负责人",
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
      "管理人员可创建、修改、查询、归档客户档案，并可查看客户审计历史；服务人员与普通员工只能查询客户资料，不能修改或归档。",
      "按 category 精确筛选客户可得到 企业/个人/合作伙伴 三类结果；按 name、organization、contact 关键词搜索可命中对应字段，且不会错误命中未声明字段。",
      "客户详情页展示该客户关联的历史服务请求，列表遵守当前角色的行权限，不出现其他员工不可见记录。",
      "用户可创建服务请求，title 与 detail 必填，customer_id 必须指向已存在的客户，priority 为 普通/紧急 之一；缺失或非法值被拒绝。",
      "管理人员或服务人员可将服务请求/任务分配给某个用户；普通员工不能执行分配动作，也不能通过普通表单直接修改 assignee_id 或状态。",
      "请求与任务创建后初始状态为 new；执行 start 后变为 active，执行 resolve 后变为 resolved 并自动写入 resolved_at；非法流转（如 new→resolved）被拒绝。",
      "只有 manager 与 service 可执行状态流转；employee 调用流转或分配接口被拒绝。",
      "服务人员只能查询、修改、备注、流转和查看审计分配给自己的请求与任务（scope=assigned），不能读取或修改其他服务人员的记录。",
      "普通员工只能创建和查询自己提交的请求（scope=own）；不能分配、不能改变状态、不能读取团队统计。",
      "服务请求与协作任务支持添加处理备注，备注与操作记录一起进入不可修改的审计历史，任何角色都无法编辑或删除历史审计条目。",
      "请求详情可查看关联的协作任务，任务详情可查看所属请求；关联查询遵守被关联记录的行权限，普通员工看不到不属于自己的关联记录。",
      "分配负责人、添加处理备注、状态变化、请求解决时产生持久化站内提醒；请求被解决后提交者可在自己的通知收件箱看到提醒，重启服务后提醒仍存在。",
      "逾期提醒依据 due_at 与当前时间判定，并在站内收件箱中呈现，不发送邮件或短信。",
      "统计至少包含：requests 总数（count）、request_state=resolved 的已解决数（count）、创建至 resolved_at 的平均解决时长（average_duration，start_field=created_at）、customers 按 category 分组计数（group_count）、requests 按 created_at 的每日趋势（time_count）。",
      "统计接口只允许 manager 与 service 调用；服务人员看到的统计只按本人可见行计算，管理人员看到全部数据，数值来自真实业务数据而非固定值或前端假图。",
      "所有关联字段在界面上显示当前角色可读的客户名称、请求标题或负责人用户名，不直接展示整数 ID 或 UUID。",
      "请求/任务状态在界面显示为 待处理/处理中/已解决，动作显示为 开始处理/标记解决，存储与动作名仍为 new/active/resolved、start/resolve。",
      "结算界面按所选模板保留原生风格：Python 轻量管理页、FastapiAdmin 原生 Vue/Fa/Element Plus 或芋道 Java/Vben5 Ant Design，不混用样式冒充。",
      "项目遵循已有代码规范与既有组件/基础设施，前后端架构一致，包含必要自动化测试，并提供可执行的部署运行方式。",
      "在真正独立的交付数据库上执行完整端到端流程（创建客户→创建请求→分配→添加备注→流转→解决→查看提醒→查看统计），并在浏览器验证与服务重启后确认数据与审计仍然存在。"
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
            "assign",
            "add_note",
            "transition",
            "archive",
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
            "assign",
            "add_note",
            "transition",
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
            "read"
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
            "read_audit",
            "read_metrics"
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
        },
        {
          "role": "employee",
          "entity": "tasks",
          "actions": [
            "read"
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
          "entity": "requests",
          "event": "due",
          "recipient": "creator",
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
          "name": "avg_resolution_duration",
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
