# examples/plans/customer-service.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可审查的需求与完整合同验收样例。** 自然语言说明目标，JSON计划逐项登记实体、字段、关系、角色、转换和指标。它用于确定性验收，不是生产模型失败后的隐藏答案；改需求需修改并重新批准相应合同。

**对应关系：** 按正文验证Plan → ci_native_bundled --spec → 真实原生工具验收；该文件随教材一并还原。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `examples/plans/customer-service.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L731。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17484`。本段原文以LF换行结束。

<!-- learning-source: {"path": "examples/plans/customer-service.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "170d91d811b28b1f2b27ce251c00ea004f001db60f79dfa0f799694cae73a42c"} -->
````json
// examples/plans/customer-service.json
{
  "title": "内部客户服务管理系统",
  "data_scope": "shared",
  "entities": [
    {
      "name": "customers",
      "description": "客户管理",
      "fields": [
        {
          "name": "name",
          "kind": "text",
          "required": true,
          "max_length": 120,
          "min_length": 0,
          "choices": [],
          "searchable": true,
          "filterable": false,
          "date_range": false,
          "label": "客户名称"
        },
        {
          "name": "organization",
          "kind": "text",
          "required": false,
          "max_length": 160,
          "min_length": 0,
          "choices": [],
          "searchable": true,
          "filterable": false,
          "date_range": false,
          "label": "所属单位"
        },
        {
          "name": "contact",
          "kind": "text",
          "required": false,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": true,
          "filterable": false,
          "date_range": false,
          "label": "联系信息"
        },
        {
          "name": "category",
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
          "date_range": false,
          "label": "客户分类"
        }
      ]
    },
    {
      "name": "requests",
      "description": "服务请求",
      "fields": [
        {
          "name": "title",
          "kind": "text",
          "required": true,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": true,
          "filterable": false,
          "date_range": false,
          "label": "标题"
        },
        {
          "name": "detail",
          "kind": "text",
          "required": true,
          "max_length": 3000,
          "min_length": 0,
          "choices": [],
          "searchable": true,
          "filterable": false,
          "date_range": false,
          "label": "详情"
        },
        {
          "name": "customer_id",
          "kind": "text",
          "required": true,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": false,
          "filterable": false,
          "date_range": false,
          "label": "关联客户"
        },
        {
          "name": "assignee_id",
          "kind": "text",
          "required": false,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": false,
          "filterable": false,
          "date_range": false,
          "label": "负责人"
        },
        {
          "name": "request_state",
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
          "date_range": false,
          "label": "请求状态",
          "choice_labels": {
            "new": "待处理",
            "active": "处理中",
            "resolved": "已解决"
          }
        },
        {
          "name": "resolved_at",
          "kind": "datetime",
          "required": false,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": false,
          "filterable": false,
          "date_range": false,
          "label": "解决时间"
        },
        {
          "name": "due_at",
          "kind": "datetime",
          "required": false,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": false,
          "filterable": false,
          "date_range": false,
          "label": "截止时间"
        },
        {
          "name": "priority",
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
          "date_range": false,
          "label": "优先级"
        }
      ]
    },
    {
      "name": "tasks",
      "description": "协作任务",
      "fields": [
        {
          "name": "title",
          "kind": "text",
          "required": true,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": true,
          "filterable": false,
          "date_range": false,
          "label": "标题"
        },
        {
          "name": "detail",
          "kind": "text",
          "required": true,
          "max_length": 3000,
          "min_length": 0,
          "choices": [],
          "searchable": true,
          "filterable": false,
          "date_range": false,
          "label": "详情"
        },
        {
          "name": "assignee_id",
          "kind": "text",
          "required": false,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": false,
          "filterable": false,
          "date_range": false,
          "label": "负责人"
        },
        {
          "name": "task_state",
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
          "date_range": false,
          "label": "任务状态",
          "choice_labels": {
            "new": "待处理",
            "active": "处理中",
            "resolved": "已解决"
          }
        },
        {
          "name": "resolved_at",
          "kind": "datetime",
          "required": false,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": false,
          "filterable": false,
          "date_range": false,
          "label": "解决时间"
        },
        {
          "name": "due_at",
          "kind": "datetime",
          "required": false,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": false,
          "filterable": false,
          "date_range": false,
          "label": "截止时间"
        },
        {
          "name": "request_id",
          "kind": "text",
          "required": true,
          "max_length": 200,
          "min_length": 0,
          "choices": [],
          "searchable": false,
          "filterable": false,
          "date_range": false,
          "label": "关联请求"
        }
      ]
    }
  ],
  "acceptance": [
    "客户档案与按条件搜索、关联服务历史可用",
    "服务请求分配、状态流转、处理记录与历史可用",
    "团队任务分配、站内提醒、不可改写操作记录可用",
    "数量、处理效率、客户分布与每日趋势统计可用",
    "管理、服务和普通员工权限在服务端生效",
    "独立数据库部署与各模板原生页面浏览器验证通过"
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
        "notes": true,
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
          "read",
          "create",
          "update",
          "archive",
          "add_note",
          "read_history",
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
          "read_history",
          "read_metrics"
        ],
        "scope": "all"
      },
      {
        "role": "employee",
        "entity": "customers",
        "actions": [
          "read",
          "read_history"
        ],
        "scope": "all"
      },
      {
        "role": "manager",
        "entity": "requests",
        "actions": [
          "read",
          "create",
          "update",
          "archive",
          "add_note",
          "read_history",
          "read_audit",
          "read_metrics",
          "assign",
          "transition"
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
          "read",
          "create",
          "add_note",
          "read_history"
        ],
        "scope": "own"
      },
      {
        "role": "manager",
        "entity": "tasks",
        "actions": [
          "read",
          "create",
          "update",
          "archive",
          "add_note",
          "read_history",
          "read_audit",
          "read_metrics",
          "assign",
          "transition"
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
          "read_audit",
          "read_metrics"
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
            "from_states": [
              "new"
            ],
            "to_state": "active",
            "roles": [
              "manager",
              "service"
            ],
            "set_timestamp": null,
            "label": "开始处理"
          },
          {
            "name": "resolve",
            "from_states": [
              "active"
            ],
            "to_state": "resolved",
            "roles": [
              "manager",
              "service"
            ],
            "set_timestamp": "resolved_at",
            "label": "标记解决"
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
            "from_states": [
              "new"
            ],
            "to_state": "active",
            "roles": [
              "manager",
              "service"
            ],
            "set_timestamp": null,
            "label": "开始处理"
          },
          {
            "name": "resolve",
            "from_states": [
              "active"
            ],
            "to_state": "resolved",
            "roles": [
              "manager",
              "service"
            ],
            "set_timestamp": "resolved_at",
            "label": "标记解决"
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
        "entity": "tasks",
        "event": "note_added",
        "recipient": "creator",
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
      }
    ],
    "metrics": [
      {
        "name": "total",
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
        "name": "resolved_total",
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
        "name": "resolution",
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
          }
        ],
        "unit": "seconds",
        "bucket": "day",
        "timezone": "UTC"
      },
      {
        "name": "by_customer",
        "label": "客户服务分布",
        "entity": "requests",
        "kind": "group_count",
        "group_by": "customer_id",
        "start_field": null,
        "end_field": null,
        "time_field": null,
        "filters": [],
        "unit": "seconds",
        "bucket": "day",
        "timezone": "UTC"
      },
      {
        "name": "daily",
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
      },
      {
        "name": "customer_total",
        "label": "客户数量",
        "entity": "customers",
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
        "name": "customer_categories",
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
      }
    ]
  },
  "unsupported": []
}
````
