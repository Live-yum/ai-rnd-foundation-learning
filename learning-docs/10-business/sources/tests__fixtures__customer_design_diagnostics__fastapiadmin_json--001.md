# tests/fixtures/customer_design_diagnostics/fastapiadmin.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/fastapiadmin.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L1636。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`54535`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/fastapiadmin.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "09fead7bdd076d1f50dacab5574072c78ac15900aa6141f58e4d90e1d9a702c6"} -->
````json
// tests/fixtures/customer_design_diagnostics/fastapiadmin.json
{
  "format": "customer-design-diagnostic-v1",
  "approval_status": "unapproved",
  "execution_authorized": false,
  "purpose": "offline_contract_validation_only",
  "template": "fastapiadmin",
  "requirement": {
    "summary": "在 FastapiAdmin 原生后端 + Vue 管理端上实现内部客户服务管理平台：shared 数据范围，三个业务资源 customers / requests / tasks，三个角色 manager / service / employee（显示名称分别为管理人员、服务人员、普通员工）。覆盖客户档案维护与检索、服务请求全流程跟踪、任务协作、处理备注、命名状态流转（start: new→active、resolve: active→resolved 并自动写 resolved_at）、按角色的行级权限（manager=all，service=assigned，employee=own）、不可修改的审计历史、持久化站内提醒，以及五项按当前角色数据范围计算的统计指标。",
    "users": [
      "管理人员（manager）：管理团队业务、分配负责人、执行状态转换、查看全部记录与审计、查看全部统计",
      "服务人员（service）：只处理分配给自己的请求与任务，可查询客户、修改、添加处理备注、执行状态转换、查看处理历史与审计、查看本人范围的统计",
      "普通员工（employee）：创建并查询自己提交的请求，查询客户资料，接收自己请求被解决后的站内提醒；不能分配、不能改变状态、不能读取团队统计",
      "系统管理员/运维：仅通过部署与运行方式启动系统，不承担业务角色"
    ],
    "data_scope": "shared",
    "features": [
      "客户管理：创建、修改、查询、归档客户档案，查看客户历史服务请求，按条件搜索客户",
      "服务请求管理：创建请求、分配负责人、执行命名状态转换、添加处理记录、查看处理过程、查询历史请求",
      "协作任务管理：在请求下创建协作任务、分配负责人、执行命名状态转换、添加处理记录、查看处理过程、归档",
      "命名状态流转与动作保护：requests/tasks 初始状态 new；start 为「开始处理」（new→active），resolve 为「标记解决」（active→resolved 并自动写入 resolved_at）；状态与负责人只能通过受保护动作变更，普通编辑表单不能绕过",
      "关联查询：客户详情展示其历史服务请求，请求详情展示其关联协作任务，关联查询遵守被关联记录的权限，不泄露其他员工记录",
      "审计历史：三个业务资源均记录不可修改（append-only）的审计历史，可查看状态变化与操作记录",
      "站内提醒：持久化站内消息，覆盖负责人分配、新增处理备注、状态变化、请求解决、逾期提醒；请求解决后提交者可在自己的通知收件箱看到解决提醒",
      "数据统计：请求总数、已解决数、创建至解决的平均解决时长、客户按分类分组、请求按创建时间的每日趋势，均按当前角色数据范围实时计算",
      "角色权限管理：管理人员/服务人员/普通员工三类角色，配合行级范围 all / assigned / own 控制可见与可操作数据",
      "站内团队协作：任务分配、处理备注、状态变化追踪、操作记录与审计追溯，全部在系统内完成",
      "遵循已有项目代码规范与基础设施，保持前后端架构一致，补充必要测试并提供部署运行方式"
    ],
    "acceptance": [
      "以 shared 数据范围建立 customers、requests、tasks 三个业务资源，角色名与显示名称分别为 manager/管理人员、service/服务人员、employee/普通员工；bootstrap_role=manager，新注册用户默认为 employee 且不能自行提升权限",
      "customers 字段：name（必填，≤120，可搜索）、organization（可选，≤160，可搜索）、contact（可选，≤200，可搜索）、category（必填枚举：企业/个人/合作伙伴，可按取值精确筛选）",
      "requests 字段：title（必填，≤200，可搜索）、detail（必填，≤3000，可搜索）、customer_id（必填，关联 customers）、assignee_id（可选，关联 $users）、request_state（必填枚举 new/active/resolved）、resolved_at（可选 datetime）、due_at（可选 datetime）、priority（必填枚举 普通/紧急，可按取值精确筛选）",
      "tasks 字段：title（必填，≤200，可搜索）、detail（必填，≤3000，可搜索）、request_id（必填，关联 requests）、assignee_id（可选，关联 $users）、task_state（必填枚举 new/active/resolved）、resolved_at（可选 datetime）、due_at（可选 datetime）",
      "关系字段在声明合同中为 text 关系键，生成后必须是校验真实外键的关联，不能实现为不校验的备注文本；关联字段在界面上显示当前角色可读的客户名称、请求标题或负责人用户名，不显示整数 ID 或 UUID",
      "请求与任务创建时状态为 new；执行 start 后变为 active；执行 resolve 后变为 resolved 且 resolved_at 自动写入；只有 manager 与 service 可执行转换；任何普通编辑表单都无法直接修改状态或负责人",
      "权限验收：manager 对 customers/requests/tasks 拥有 create/read/update/assign/transition/comment/archive/view_audit（scope=all）；service 对 customers 可 read（all），对 requests/tasks 在 scope=assigned 内可 read/update/comment/transition/view_audit，且只能看到分配给自己的记录；employee 对 customers 可 read（all），对 requests 可 create 且仅能 read 自己提交的记录（scope=own），但无法分配、无法改变状态、无法读取团队统计",
      "服务人员或普通员工越权直接访问他人请求/任务时被拒绝；客户详情与请求详情的关联列表只返回当前角色有权读取的记录",
      "客户详情页可查看该客户的历史服务请求列表；请求详情页可查看其关联协作任务列表",
      "三个业务资源均产生不可修改的审计记录，包含谁在何时执行了创建、修改、分配、状态转换、归档等操作",
      "站内提醒持久化并可重启后保留：分配负责人、新增处理备注、状态变化、请求解决、逾期均产生提醒；请求被解决后，提交者能在自己的通知收件箱看到解决提醒",
      "统计验收：requests 总数（count）、已解决数（count，request_state=resolved）、创建到 resolved_at 的平均解决时长（average_duration，start_field=created_at）、customers 按 category 分组计数（group_count）、requests 按 created_at 的每日趋势（time_count）；指标只对 manager/service 开放，service 的数值按本人可见行计算，全部数值来自真实数据而非预设数字或前端假图",
      "部署与运行验收：使用独立交付数据库、锁定依赖，完成全流程浏览器验证与重启后数据与提醒仍存在的验证；不以孤立 CRUD 操作或其他案例的成功代替端到端流程验收",
      "三实体文本字段 min_length=0（必填只由 required 约束）；datetime 字段仅存储时间戳，不参与搜索、筛选或日期范围；id/created_at/updated_at/created_by/archived_at 由运行时提供，不在实体字段中重复声明，统计直接引用系统 created_at"
    ],
    "questions": [],
    "assumptions": [
      "本案例面向公司内部客服团队使用，不建设面向外部客户的公开门户或匿名提交入口",
      "提醒只在系统内持久化保存与展示，不发送邮件、短信或触达真实客户联系方式",
      "验收数据均为合成账号与合成客户数据",
      "服务人员默认不执行负责人分配动作，分配由管理人员完成；如后续需要服务人员转派，可在已审批设计基础上扩展权限条目"
    ],
    "unsupported": [],
    "limitations": [
      "不接入邮件、短信或真实客户联系方式，提醒仅为站内持久化消息",
      "不提供公众匿名访问、外部客户自助提交或对外网站能力",
      "不提供每用户完全隔离的私有数据空间（per_user 隔离）；本案例使用 shared 数据范围配合角色行权限",
      "不支持任意脚本执行、支付或网络副作用",
      "不做与其他外部系统的数据同步或爬取"
    ],
    "recommendations": [
      "列表默认分页 20 条/页，搜索采用不区分大小写的包含匹配；客户搜索覆盖 name/organization/contact，请求与任务搜索覆盖 title/detail",
      "category 与 priority 使用下拉精确筛选；request_state/task_state 通过命名动作变更，不在编辑表单中直接编辑",
      "归档采用软归档（archived_at），归档记录保留审计历史，默认列表不展示已归档记录",
      "通知收件箱按时间倒序展示，未读高亮并可标记已读；逾期提醒按 due_at 与当前时间比较生成",
      "统计面板默认按当前登录用户的数据范围计算，manager 看全部，service 看本人负责的行，并对无数据情况展示空态而非占位数字",
      "测试覆盖：接口层覆盖权限矩阵（all/assigned/own）、状态转换合法性、resolved_at 自动写入、关联校验、审计不可修改；浏览器层覆盖跨角色端到端流程与重启持久化验证",
      "部署说明给出依赖锁定、独立数据库初始化、启动命令与演示账号初始化方式，保证部署运行步骤可复现"
    ],
    "facts": {
      "business": {
        "scope": "shared",
        "bootstrap_role": "manager",
        "default_registration_role": "employee",
        "custom_rules": [],
        "resources": [
          {
            "entity": "customers",
            "label": "客户",
            "features": [
              "native-crud",
              "append-only-audit",
              "archive-history"
            ],
            "fields": [
              {
                "name": "name",
                "label": "客户名称",
                "kind": "text",
                "required": true,
                "max_length": 120,
                "searchable": true
              },
              {
                "name": "organization",
                "label": "所属组织",
                "kind": "text",
                "required": false,
                "max_length": 160,
                "searchable": true
              },
              {
                "name": "contact",
                "label": "联系方式",
                "kind": "text",
                "required": false,
                "max_length": 200,
                "searchable": true
              },
              {
                "name": "category",
                "label": "客户分类",
                "kind": "enum",
                "required": true,
                "choices": [
                  "企业",
                  "个人",
                  "合作伙伴"
                ],
                "filterable": true
              }
            ]
          },
          {
            "entity": "requests",
            "label": "服务请求",
            "features": [
              "native-crud",
              "foreign-key-relations",
              "assignment",
              "named-state-transitions",
              "handling-notes",
              "append-only-audit",
              "archive-history",
              "in-app-reminders"
            ],
            "fields": [
              {
                "name": "title",
                "label": "请求标题",
                "kind": "text",
                "required": true,
                "max_length": 200,
                "searchable": true
              },
              {
                "name": "detail",
                "label": "请求详情",
                "kind": "text",
                "required": true,
                "max_length": 3000,
                "searchable": true
              },
              {
                "name": "customer_id",
                "label": "关联客户",
                "kind": "text",
                "required": true,
                "relation": "customers"
              },
              {
                "name": "assignee_id",
                "label": "负责人",
                "kind": "text",
                "required": false,
                "relation": "$users"
              },
              {
                "name": "request_state",
                "label": "请求状态",
                "kind": "enum",
                "required": true,
                "choices": [
                  "new",
                  "active",
                  "resolved"
                ],
                "choice_labels": {
                  "new": "待处理",
                  "active": "处理中",
                  "resolved": "已解决"
                }
              },
              {
                "name": "resolved_at",
                "label": "解决时间",
                "kind": "datetime",
                "required": false,
                "searchable": false,
                "filterable": false,
                "date_range": false
              },
              {
                "name": "due_at",
                "label": "截止时间",
                "kind": "datetime",
                "required": false,
                "searchable": false,
                "filterable": false,
                "date_range": false
              },
              {
                "name": "priority",
                "label": "优先级",
                "kind": "enum",
                "required": true,
                "choices": [
                  "普通",
                  "紧急"
                ],
                "filterable": true
              }
            ]
          },
          {
            "entity": "tasks",
            "label": "协作任务",
            "features": [
              "native-crud",
              "foreign-key-relations",
              "assignment",
              "named-state-transitions",
              "handling-notes",
              "append-only-audit",
              "archive-history",
              "in-app-reminders"
            ],
            "fields": [
              {
                "name": "title",
                "label": "任务标题",
                "kind": "text",
                "required": true,
                "max_length": 200,
                "searchable": true
              },
              {
                "name": "detail",
                "label": "任务详情",
                "kind": "text",
                "required": true,
                "max_length": 3000,
                "searchable": true
              },
              {
                "name": "request_id",
                "label": "关联请求",
                "kind": "text",
                "required": true,
                "relation": "requests"
              },
              {
                "name": "assignee_id",
                "label": "负责人",
                "kind": "text",
                "required": false,
                "relation": "$users"
              },
              {
                "name": "task_state",
                "label": "任务状态",
                "kind": "enum",
                "required": true,
                "choices": [
                  "new",
                  "active",
                  "resolved"
                ],
                "choice_labels": {
                  "new": "待处理",
                  "active": "处理中",
                  "resolved": "已解决"
                }
              },
              {
                "name": "resolved_at",
                "label": "解决时间",
                "kind": "datetime",
                "required": false,
                "searchable": false,
                "filterable": false,
                "date_range": false
              },
              {
                "name": "due_at",
                "label": "截止时间",
                "kind": "datetime",
                "required": false,
                "searchable": false,
                "filterable": false,
                "date_range": false
              }
            ]
          }
        ],
        "relations": [
          {
            "entity": "requests",
            "field": "customer_id",
            "target": "customers",
            "kind": "text",
            "required": true,
            "display": "客户名称"
          },
          {
            "entity": "requests",
            "field": "assignee_id",
            "target": "$users",
            "kind": "text",
            "required": false,
            "display": "负责人用户名"
          },
          {
            "entity": "tasks",
            "field": "request_id",
            "target": "requests",
            "kind": "text",
            "required": true,
            "display": "请求标题"
          },
          {
            "entity": "tasks",
            "field": "assignee_id",
            "target": "$users",
            "kind": "text",
            "required": false,
            "display": "负责人用户名"
          },
          {
            "entity": "customers",
            "field": "requests",
            "target": "requests",
            "kind": "reverse",
            "display": "历史服务请求"
          },
          {
            "entity": "requests",
            "field": "tasks",
            "target": "tasks",
            "kind": "reverse",
            "display": "关联协作任务"
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
              "transition",
              "comment",
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
              "transition",
              "comment",
              "archive",
              "view_audit"
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
              "comment",
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
              "comment",
              "transition",
              "view_audit"
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
            "initial_state": "new",
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
                "set_fields": {
                  "resolved_at": "now"
                }
              }
            ],
            "protected_fields": [
              "request_state",
              "assignee_id"
            ]
          },
          {
            "entity": "tasks",
            "initial_state": "new",
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
                "set_fields": {
                  "resolved_at": "now"
                }
              }
            ],
            "protected_fields": [
              "task_state",
              "assignee_id"
            ]
          }
        ],
        "notifications": [
          {
            "event": "assigned",
            "label": "负责人分配",
            "recipients": [
              "assignee_id"
            ]
          },
          {
            "event": "comment_added",
            "label": "新增处理备注",
            "recipients": [
              "assignee_id",
              "created_by"
            ]
          },
          {
            "event": "state_changed",
            "label": "状态变化",
            "recipients": [
              "assignee_id",
              "created_by"
            ]
          },
          {
            "event": "resolved",
            "label": "请求已解决",
            "recipients": [
              "created_by",
              "assignee_id"
            ]
          },
          {
            "event": "overdue",
            "label": "逾期提醒",
            "recipients": [
              "assignee_id"
            ],
            "condition": "due_at < now and state != resolved"
          }
        ],
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
            "group_field": "category"
          },
          {
            "name": "requests_daily_trend",
            "label": "请求每日趋势",
            "type": "time_count",
            "entity": "requests",
            "time_field": "created_at",
            "interval": "day"
          }
        ],
        "metrics_roles": [
          "manager",
          "service"
        ],
        "audit": {
          "entities": [
            "customers",
            "requests",
            "tasks"
          ],
          "immutable": true
        }
      },
      "ui": {
        "role_labels": {
          "manager": "管理人员",
          "service": "服务人员",
          "employee": "普通员工"
        },
        "field_labels": {
          "customers.name": "客户名称",
          "customers.organization": "所属组织",
          "customers.contact": "联系方式",
          "customers.category": "客户分类",
          "requests.title": "请求标题",
          "requests.detail": "请求详情",
          "requests.customer_id": "关联客户",
          "requests.assignee_id": "负责人",
          "requests.request_state": "请求状态",
          "requests.resolved_at": "解决时间",
          "requests.due_at": "截止时间",
          "requests.priority": "优先级",
          "tasks.title": "任务标题",
          "tasks.detail": "任务详情",
          "tasks.request_id": "关联请求",
          "tasks.assignee_id": "负责人",
          "tasks.task_state": "任务状态",
          "tasks.resolved_at": "解决时间",
          "tasks.due_at": "截止时间"
        },
        "relation_display": "关联字段显示当前角色可读的客户名称、请求标题或负责人用户名，不显示整数 ID 或 UUID",
        "frontend": "fastapiadmin-vue"
      },
      "system_fields": {
        "runtime_provided": [
          "id",
          "created_at",
          "updated_at",
          "created_by",
          "archived_at"
        ],
        "note": "不在 entities.fields 中重复声明；统计直接引用系统 created_at"
      },
      "constraints": {
        "text_min_length": 0,
        "datetime_fields": "仅存储时间戳，searchable=false、filterable=false、date_range=false",
        "relation_fields": "逻辑外键不添加搜索、筛选或日期范围",
        "excluded": [
          "外部服务",
          "支付",
          "邮件短信",
          "爬虫",
          "自定义任意代码"
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
        "searchable": null,
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
        "searchable": null,
        "filterable": null,
        "date_range": false,
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
        "date_range": false,
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
        "searchable": null,
        "filterable": null,
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
      "以 shared 数据范围建立 customers、requests、tasks 三个业务资源，角色名与显示名称分别为 manager/管理人员、service/服务人员、employee/普通员工；bootstrap_role=manager，新注册用户默认为 employee 且不能自行提升权限",
      "customers 字段：name（必填，≤120，可搜索）、organization（可选，≤160，可搜索）、contact（可选，≤200，可搜索）、category（必填枚举：企业/个人/合作伙伴，可按取值精确筛选）",
      "requests 字段：title（必填，≤200，可搜索）、detail（必填，≤3000，可搜索）、customer_id（必填，关联 customers）、assignee_id（可选，关联 $users）、request_state（必填枚举 new/active/resolved）、resolved_at（可选 datetime）、due_at（可选 datetime）、priority（必填枚举 普通/紧急，可按取值精确筛选）",
      "tasks 字段：title（必填，≤200，可搜索）、detail（必填，≤3000，可搜索）、request_id（必填，关联 requests）、assignee_id（可选，关联 $users）、task_state（必填枚举 new/active/resolved）、resolved_at（可选 datetime）、due_at（可选 datetime）",
      "关系字段在声明合同中为 text 关系键，生成后必须是校验真实外键的关联，不能实现为不校验的备注文本；关联字段在界面上显示当前角色可读的客户名称、请求标题或负责人用户名，不显示整数 ID 或 UUID",
      "请求与任务创建时状态为 new；执行 start 后变为 active；执行 resolve 后变为 resolved 且 resolved_at 自动写入；只有 manager 与 service 可执行转换；任何普通编辑表单都无法直接修改状态或负责人",
      "权限验收：manager 对 customers/requests/tasks 拥有 create/read/update/assign/transition/comment/archive/view_audit（scope=all）；service 对 customers 可 read（all），对 requests/tasks 在 scope=assigned 内可 read/update/comment/transition/view_audit，且只能看到分配给自己的记录；employee 对 customers 可 read（all），对 requests 可 create 且仅能 read 自己提交的记录（scope=own），但无法分配、无法改变状态、无法读取团队统计",
      "服务人员或普通员工越权直接访问他人请求/任务时被拒绝；客户详情与请求详情的关联列表只返回当前角色有权读取的记录",
      "客户详情页可查看该客户的历史服务请求列表；请求详情页可查看其关联协作任务列表",
      "三个业务资源均产生不可修改的审计记录，包含谁在何时执行了创建、修改、分配、状态转换、归档等操作",
      "站内提醒持久化并可重启后保留：分配负责人、新增处理备注、状态变化、请求解决、逾期均产生提醒；请求被解决后，提交者能在自己的通知收件箱看到解决提醒",
      "统计验收：requests 总数（count）、已解决数（count，request_state=resolved）、创建到 resolved_at 的平均解决时长（average_duration，start_field=created_at）、customers 按 category 分组计数（group_count）、requests 按 created_at 的每日趋势（time_count）；指标只对 manager/service 开放，service 的数值按本人可见行计算，全部数值来自真实数据而非预设数字或前端假图",
      "部署与运行验收：使用独立交付数据库、锁定依赖，完成全流程浏览器验证与重启后数据与提醒仍存在的验证；不以孤立 CRUD 操作或其他案例的成功代替端到端流程验收",
      "三实体文本字段 min_length=0（必填只由 required 约束）；datetime 字段仅存储时间戳，不参与搜索、筛选或日期范围；id/created_at/updated_at/created_by/archived_at 由运行时提供，不在实体字段中重复声明，统计直接引用系统 created_at"
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
          "recipient": "assignee",
          "transition": "start",
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
