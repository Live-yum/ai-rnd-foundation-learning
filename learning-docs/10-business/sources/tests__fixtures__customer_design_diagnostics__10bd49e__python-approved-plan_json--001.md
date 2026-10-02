# tests/fixtures/customer_design_diagnostics/10bd49e/python-approved-plan.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/10bd49e/python-approved-plan.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L748。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`21216`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/10bd49e/python-approved-plan.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f4638440b66622db35ffd919613aa608656889eb5a1d96ee80651fbf7e0c19f0"} -->
````json
// tests/fixtures/customer_design_diagnostics/10bd49e/python-approved-plan.json
{
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
          "choice_labels": {
            "个人": "个人",
            "企业": "企业",
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
        },
        {
          "name": "published_on",
          "label": "客户档案发布日期",
          "choice_labels": {},
          "kind": "date",
          "required": false,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": false,
          "filterable": true,
          "date_range": true
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
          "label": "处理状态",
          "choice_labels": {
            "active": "处理中",
            "new": "待处理",
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
            "active": "处理中",
            "new": "待处理",
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
    "manager 可创建、修改、查询、归档客户并查看客户审计历史；service 与 employee 仅可查询客户",
    "客户列表支持 name/organization/contact 关键词搜索与 category（企业/个人/合作伙伴）精确筛选，返回结果符合条件",
    "客户详情页可列出关联的历史服务请求，且只显示当前角色有权读取的请求",
    "employee 可创建请求（title/detail/customer_id/priority 必填），创建后 request_state=new，且只能查询自己提交的请求",
    "manager 或 service 可对请求执行 assign 分配负责人，被分配人收到站内提醒",
    "请求状态只能通过命名动作改变：start 使 new→active，resolve 使 active→resolved 并自动写入 resolved_at；employee 调用任意转换被拒绝，通过普通表单直接改 request_state 或 assignee_id 被拒绝",
    "请求与任务支持添加处理备注，备注后对应负责人收到站内提醒，处理过程可查看",
    "service 账号只能查询、修改、添加备注、转换、查看历史与审计分配给自己的请求/任务，访问他人记录被拒绝且关联查询不泄露他人记录",
    "tasks 由 manager 创建并分配，tasks.request_id 校验存在性（无效关系键被拒绝），请求详情可查看关联任务且遵守行权限",
    "customers、requests、tasks 的每次变更产生不可修改的审计记录，可通过 read_history/read_audit 权限查看",
    "请求解决后，提交者（creator）在本人通知收件箱中看到对应提醒；通知为持久化站内消息，读取状态仅对该接收人私有",
    "为请求/任务设置 due_at 后，逾期产生负责人站内提醒",
    "统计接口返回：requests 总数、已解决数（request_state=resolved）、创建至 resolved_at 的平均解决时长（秒，无样本返回 null）、customers 按 category 分组计数、requests 按 created_at 的每日趋势；manager 看到全量，service 只看到本人可见行，employee 无统计权限",
    "普通员工调用统计接口与分配/状态转换接口均被服务端拒绝（非仅前端隐藏）",
    "在独立交付数据库上完成上述完整流程的浏览器与重启测试，重启后客户、请求、任务、备注、审计与通知数据仍然存在",
    "项目包含必要自动化测试并可通过文档中的方式在本地/交付环境运行",
    "统计设计说明：数量类指标使用 count，效率类指标使用 average_duration（start_field=created_at、end_field=resolved_at、unit=seconds，无样本返回 null），客户分布使用 group_count(group_by=category)，每日趋势使用 time_count(time_field=created_at、bucket=day、timezone=UTC，按 UTC 日分桶）；所有指标均按调用者 read_metrics 行权限范围实时计算，不使用预设数字或前端假图",
    "字段取值设计说明：request_state/task_state 存储机器值 new/active/resolved 并按 choice_labels 显示为待处理/处理中/已解决，priority 与 category 存储并显示中文枚举值；name/organization 等文本字段 min_length=0，必填仅由 required 约束；id/created_at/updated_at/created_by/archived_at 由运行时提供，不重复声明为业务字段",
    "关联展示设计说明：customer_id、request_id、assignee_id 以逻辑 ID 文本存储并由运行时的外键关系做存在性校验，列表与详情返回客户名称、请求标题、负责人用户名的可读名称，不直接展示 UUID 或整数 ID",
    "日期类型设计说明：customers.published_on 为真实日期类型（kind=date，格式 YYYY-MM-DD，例如 2024-05-06），记录客户档案发布/生效日期，可选填，支持含起止边界的日期区间筛选；requests/tasks 的 resolved_at 与 due_at 是 datetime 时间戳（date_range=false），不作为真实日期类型使用"
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
        "label": "每日请求趋势",
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
````
