# 大规模项目：设施维护运营中心

我要一个园区内部的设施维护运营系统，覆盖站点、设备、故障、维修工单、巡检、备件申请六个模块。使用 python-basic、simple-admin 前端、SQLite 数据库。只允许 sites、assets、faults、work_orders、inspections、parts_requests 六个实体及下表字段。全部业务数据 shared，由 coordinator、reporter、technician、auditor 四个角色的明确授权控制。账号由协调员创建，不开放自助注册；初始化管理角色 coordinator，默认非管理角色 reporter。

协调员维护主数据、分派工单和巡检、闭环故障；报障人员只看到自己提交的故障；维修员只处理分配给自己的工单和巡检，其备件申请按创建者隔离；审计员只能查看数据、历史、审计和统计。界面中文，英文实体、字段、角色、动作和枚举值是稳定接口契约，请原样保留，可另加中文显示标签。本轮“大规模”指当前模板内的业务复杂度：六模块、四角色、四状态机、八关系、五指标；不代表高并发、分布式部署或生产负载验收。工单、巡检与备件申请由用户明确创建，状态流转不自动创建其他实体，不要求设备遥测、排程优化、采购财务或外部系统集成。

## 字段清单

未特别标注的文本字段最大长度为 200；未声明的 searchable、filterable、date_range 均为 false。所有普通 required 字段必须提交；负责人、状态及状态时间遵守业务专用操作。系统 id、创建者、创建时间等由模板提供，不加入业务字段清单。

| 实体 | 字段 | 约束 |
| --- | --- | --- |
| sites | name | text；必填；最大长度 200；关键词搜索 |
| sites | zone | enum；必填；枚举 north, south；精确筛选 |
| assets | name | text；必填；最大长度 200；关键词搜索 |
| assets | site_id | text；必填 |
| assets | asset_code | text；必填；最大长度 60 |
| assets | condition | enum；必填；枚举 operational, maintenance, retired；精确筛选 |
| faults | title | text；必填；最大长度 200；关键词搜索 |
| faults | asset_id | text；必填 |
| faults | severity | enum；必填；枚举 low, high, critical；精确筛选 |
| faults | details | text；必填；最大长度 3000 |
| faults | fault_state | enum；必填；枚举 new, triaged, closed；精确筛选 |
| work_orders | title | text；必填；最大长度 200；关键词搜索 |
| work_orders | fault_id | text；可空 |
| work_orders | asset_id | text；必填 |
| work_orders | assignee_id | text；可空 |
| work_orders | priority | enum；必填；枚举 routine, urgent；精确筛选 |
| work_orders | state | enum；必填；枚举 queued, active, done；精确筛选 |
| work_orders | due_at | datetime；可空 |
| work_orders | completed_at | datetime；可空 |
| inspections | title | text；必填；最大长度 200；关键词搜索 |
| inspections | asset_id | text；必填 |
| inspections | assignee_id | text；可空 |
| inspections | result_state | enum；必填；枚举 scheduled, passed, failed；精确筛选 |
| inspections | scheduled_on | date；必填 |
| inspections | checked_at | datetime；可空 |
| parts_requests | title | text；必填；最大长度 200；关键词搜索 |
| parts_requests | work_order_id | text；必填 |
| parts_requests | quantity | integer；必填；最小值 1；最大值 9999 |
| parts_requests | supply_state | enum；必填；枚举 requested, supplied；精确筛选 |

## 明确的业务契约

以下 JSON 是本次用户需求中的可执行业务约束，不是审批结果或模型答案。请由需求分析记录并由设计生成完整 Plan.business，保留全部条目；可补充各处必需的中文 label。权限是完整的 grant-only 授权表：没有列出的角色/实体/动作一律拒绝，不取多个角色权限的并集。所有实体启用 archive、notes、audit；archive 保留关联和历史。日期时间使用带时区的 ISO 8601；统计时间为 UTC，时长单位 seconds。无需额外扩展代码。

```json
{
  "roles": [{"name": "coordinator"},{"name": "reporter"},{"name": "technician"},{"name": "auditor"}],
  "registration": {"enabled": false,"default_role": "reporter"},
  "bootstrap_role": "coordinator",
  "role_admin_roles": ["coordinator"],
  "resources": [
    {"entity": "sites","assignee_field": null,"archive": true,"notes": true,"audit": true},
    {"entity": "assets","assignee_field": null,"archive": true,"notes": true,"audit": true},
    {"entity": "faults","assignee_field": null,"archive": true,"notes": true,"audit": true},
    {"entity": "work_orders","assignee_field": "assignee_id","archive": true,"notes": true,"audit": true},
    {"entity": "inspections","assignee_field": "assignee_id","archive": true,"notes": true,"audit": true},
    {"entity": "parts_requests","assignee_field": null,"archive": true,"notes": true,"audit": true}
  ],
  "relations": [
    {"entity": "assets","field": "site_id","target_entity": "sites","on_delete": "restrict"},
    {"entity": "faults","field": "asset_id","target_entity": "assets","on_delete": "restrict"},
    {"entity": "work_orders","field": "fault_id","target_entity": "faults","on_delete": "restrict"},
    {"entity": "work_orders","field": "asset_id","target_entity": "assets","on_delete": "restrict"},
    {"entity": "work_orders","field": "assignee_id","target_entity": "$users","on_delete": "restrict"},
    {"entity": "inspections","field": "asset_id","target_entity": "assets","on_delete": "restrict"},
    {"entity": "inspections","field": "assignee_id","target_entity": "$users","on_delete": "restrict"},
    {"entity": "parts_requests","field": "work_order_id","target_entity": "work_orders","on_delete": "restrict"}
  ],
  "permissions": [
    {
      "role": "coordinator",
      "entity": "sites",
      "actions": ["create","read","update","archive","add_note","read_history","read_audit","read_metrics"],
      "scope": "all"
    },
    {
      "role": "coordinator",
      "entity": "assets",
      "actions": ["create","read","update","archive","add_note","read_history","read_audit","read_metrics"],
      "scope": "all"
    },
    {
      "role": "coordinator",
      "entity": "faults",
      "actions": ["create","read","update","archive","add_note","read_history","read_audit","read_metrics","transition"],
      "scope": "all"
    },
    {
      "role": "coordinator",
      "entity": "work_orders",
      "actions": ["create","read","update","archive","add_note","read_history","read_audit","read_metrics","transition","assign"],
      "scope": "all"
    },
    {
      "role": "coordinator",
      "entity": "inspections",
      "actions": ["create","read","update","archive","add_note","read_history","read_audit","read_metrics","transition","assign"],
      "scope": "all"
    },
    {
      "role": "coordinator",
      "entity": "parts_requests",
      "actions": ["create","read","update","archive","add_note","read_history","read_audit","read_metrics","transition"],
      "scope": "all"
    },
    {"role": "reporter","entity": "sites","actions": ["read"],"scope": "all"},
    {"role": "reporter","entity": "assets","actions": ["read"],"scope": "all"},
    {"role": "reporter","entity": "faults","actions": ["create","read","add_note","read_history"],"scope": "own"},
    {"role": "technician","entity": "sites","actions": ["read"],"scope": "all"},
    {"role": "technician","entity": "assets","actions": ["read"],"scope": "all"},
    {"role": "technician","entity": "faults","actions": ["read","add_note","read_history"],"scope": "all"},
    {"role": "technician","entity": "work_orders","actions": ["read","update","transition","add_note","read_history"],"scope": "assigned"},
    {"role": "technician","entity": "inspections","actions": ["read","update","transition","add_note","read_history"],"scope": "assigned"},
    {"role": "technician","entity": "parts_requests","actions": ["create","read","add_note","read_history"],"scope": "own"},
    {"role": "auditor","entity": "sites","actions": ["read","read_history","read_audit","read_metrics"],"scope": "all"},
    {"role": "auditor","entity": "assets","actions": ["read","read_history","read_audit","read_metrics"],"scope": "all"},
    {"role": "auditor","entity": "faults","actions": ["read","read_history","read_audit","read_metrics"],"scope": "all"},
    {"role": "auditor","entity": "work_orders","actions": ["read","read_history","read_audit","read_metrics"],"scope": "all"},
    {"role": "auditor","entity": "inspections","actions": ["read","read_history","read_audit","read_metrics"],"scope": "all"},
    {"role": "auditor","entity": "parts_requests","actions": ["read","read_history","read_audit","read_metrics"],"scope": "all"}
  ],
  "workflows": [
    {
      "entity": "faults",
      "status_field": "fault_state",
      "initial": "new",
      "transitions": [
        {"name": "triage","from_states": ["new"],"to_state": "triaged","roles": ["coordinator"],"set_timestamp": null},
        {"name": "close","from_states": ["triaged"],"to_state": "closed","roles": ["coordinator"],"set_timestamp": null}
      ]
    },
    {
      "entity": "work_orders",
      "status_field": "state",
      "initial": "queued",
      "transitions": [
        {"name": "start","from_states": ["queued"],"to_state": "active","roles": ["coordinator","technician"],"set_timestamp": null},
        {"name": "finish","from_states": ["active"],"to_state": "done","roles": ["coordinator","technician"],"set_timestamp": "completed_at"}
      ]
    },
    {
      "entity": "inspections",
      "status_field": "result_state",
      "initial": "scheduled",
      "transitions": [
        {
          "name": "pass_check",
          "from_states": ["scheduled"],
          "to_state": "passed",
          "roles": ["coordinator","technician"],
          "set_timestamp": "checked_at"
        },
        {
          "name": "fail_check",
          "from_states": ["scheduled"],
          "to_state": "failed",
          "roles": ["coordinator","technician"],
          "set_timestamp": "checked_at"
        }
      ]
    },
    {
      "entity": "parts_requests",
      "status_field": "supply_state",
      "initial": "requested",
      "transitions": [{"name": "confirm_supply","from_states": ["requested"],"to_state": "supplied","roles": ["coordinator"],"set_timestamp": null}]
    }
  ],
  "notifications": [
    {"entity": "work_orders","event": "assigned","recipient": "assignee","transition": null,"due_field": null,"channel": "in_app"},
    {"entity": "work_orders","event": "transitioned","recipient": "creator","transition": "finish","due_field": null,"channel": "in_app"},
    {"entity": "work_orders","event": "note_added","recipient": "creator","transition": null,"due_field": null,"channel": "in_app"},
    {"entity": "work_orders","event": "due","recipient": "assignee","transition": null,"due_field": "due_at","channel": "in_app"},
    {"entity": "inspections","event": "assigned","recipient": "assignee","transition": null,"due_field": null,"channel": "in_app"},
    {"entity": "inspections","event": "transitioned","recipient": "creator","transition": "pass_check","due_field": null,"channel": "in_app"},
    {"entity": "inspections","event": "transitioned","recipient": "creator","transition": "fail_check","due_field": null,"channel": "in_app"}
  ],
  "metrics": [
    {
      "name": "asset_count",
      "entity": "assets",
      "kind": "count",
      "filters": [],
      "group_by": null,
      "start_field": null,
      "end_field": null,
      "time_field": null,
      "unit": "seconds",
      "bucket": "day",
      "timezone": "UTC"
    },
    {
      "name": "open_faults",
      "entity": "faults",
      "kind": "count",
      "filters": [{"field": "fault_state","op": "ne","value": "closed"}],
      "group_by": null,
      "start_field": null,
      "end_field": null,
      "time_field": null,
      "unit": "seconds",
      "bucket": "day",
      "timezone": "UTC"
    },
    {
      "name": "work_order_states",
      "entity": "work_orders",
      "kind": "group_count",
      "group_by": "state",
      "filters": [],
      "start_field": null,
      "end_field": null,
      "time_field": null,
      "unit": "seconds",
      "bucket": "day",
      "timezone": "UTC"
    },
    {
      "name": "mean_repair_seconds",
      "entity": "work_orders",
      "kind": "average_duration",
      "start_field": "created_at",
      "end_field": "completed_at",
      "filters": [],
      "group_by": null,
      "time_field": null,
      "unit": "seconds",
      "bucket": "day",
      "timezone": "UTC"
    },
    {
      "name": "inspections_by_day",
      "entity": "inspections",
      "kind": "time_count",
      "time_field": "created_at",
      "filters": [],
      "group_by": null,
      "start_field": null,
      "end_field": null,
      "unit": "seconds",
      "bucket": "day",
      "timezone": "UTC"
    }
  ]
}
```

## 可执行验收

- 依次创建站点、设备、报障、工单、巡检和备件申请，关联记录选择显示可读名称且后端验证行权限。
- 报障默认 new，只有协调员可 triage 至 triaged，再 close 至 closed。报障人员不能流转状态，也看不到其他报障人员的故障。
- 工单默认 queued，由协调员分派给具备处理权限的用户；维修员只能读取和操作分配给自己的工单。start 为 active，finish 为 done，同时服务端写入 completed_at。状态、负责人和完成时间必须通过专用操作写入。
- 维修员对工单添加维修备注，另建备件申请（数量正整数）；提交后申请维修员只能查看和追加备注，其他维修员不能访问。供料状态 supply_state 默认为 requested，仅协调员能用 confirm_supply 操作变为 supplied，创建或普通编辑均不能伪造供料状态。
- 巡检默认 scheduled，分派后协调员或被分配维修员可 pass_check 为 passed 或 fail_check 为 failed，同时写入 checked_at。
- 分派、完成、备注与到期提醒按下列契约发送；到期检查只对非终态工单且 due_at 已到的记录发送，重复刷新不能产生重复提醒，用户只能读取自己的提醒。
- 审计员不能创建、修改、分派或流转；只能查看授权范围的数据、不可修改历史、审计和指标。五个指标基于实际数据库计算：设备计数、未关闭故障计数、工单状态分组、已完成工单平均处理秒数、按 UTC 日的巡检创建计数。
- 独立 HTTP 验收串起上述业务，并检验无权限操作失败。真实浏览器显示各角色的列表、关联、流程操作、提醒、统计；ZIP 在干净目录安装启动，重启保留数据和权限。

## 生成方式

通过当前平台正常的需求分析、设计、生成、独立验收和交付关卡（模型审阅为可选项）执行。未明确的展示细节可采用合理默认并记录；不得删改上述业务义务、增加不必要的功能或编造测试通过。
