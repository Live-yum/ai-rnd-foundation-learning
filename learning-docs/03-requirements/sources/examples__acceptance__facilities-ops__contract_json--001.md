# examples/acceptance/facilities-ops/contract.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可审查的需求与完整合同验收样例。** 自然语言说明目标，JSON计划逐项登记实体、字段、关系、角色、转换和指标。它用于确定性验收，不是生产模型失败后的隐藏答案；改需求需修改并重新批准相应合同。

**对应关系：** 按正文验证Plan → ci_native_bundled --spec → 真实原生工具验收；该文件随教材一并还原。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `examples/acceptance/facilities-ops/contract.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L606。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`25102`。本段原文以LF换行结束。

<!-- learning-source: {"path": "examples/acceptance/facilities-ops/contract.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8afe7380c068118617851d2b71efd1f9729b4045e057469148c3ac3dc0387655"} -->
````json
// examples/acceptance/facilities-ops/contract.json
{
  "id": "facilities-ops",
  "size": "large",
  "title": "设施维护运营中心",
  "contract": {
    "data_scope": "shared",
    "entities": {
      "sites": {
        "name": {"kind": "text","required": true,"max_length": 200,"searchable": true},
        "zone": {"kind": "enum","required": true,"choices": ["north","south"],"filterable": true}
      },
      "assets": {
        "name": {"kind": "text","required": true,"max_length": 200,"searchable": true},
        "site_id": {"kind": "text","required": true},
        "asset_code": {"kind": "text","required": true,"max_length": 60},
        "condition": {"kind": "enum","required": true,"choices": ["operational","maintenance","retired"],"filterable": true}
      },
      "faults": {
        "title": {"kind": "text","required": true,"max_length": 200,"searchable": true},
        "asset_id": {"kind": "text","required": true},
        "severity": {"kind": "enum","required": true,"choices": ["low","high","critical"],"filterable": true},
        "details": {"kind": "text","required": true,"max_length": 3000},
        "fault_state": {"kind": "enum","required": true,"choices": ["new","triaged","closed"],"filterable": true}
      },
      "work_orders": {
        "title": {"kind": "text","required": true,"max_length": 200,"searchable": true},
        "fault_id": {"kind": "text","required": false},
        "asset_id": {"kind": "text","required": true},
        "assignee_id": {"kind": "text","required": false},
        "priority": {"kind": "enum","required": true,"choices": ["routine","urgent"],"filterable": true},
        "state": {"kind": "enum","required": true,"choices": ["queued","active","done"],"filterable": true},
        "due_at": {"kind": "datetime","required": false},
        "completed_at": {"kind": "datetime","required": false}
      },
      "inspections": {
        "title": {"kind": "text","required": true,"max_length": 200,"searchable": true},
        "asset_id": {"kind": "text","required": true},
        "assignee_id": {"kind": "text","required": false},
        "result_state": {"kind": "enum","required": true,"choices": ["scheduled","passed","failed"],"filterable": true},
        "scheduled_on": {"kind": "date","required": true},
        "checked_at": {"kind": "datetime","required": false}
      },
      "parts_requests": {
        "title": {"kind": "text","required": true,"max_length": 200,"searchable": true},
        "work_order_id": {"kind": "text","required": true},
        "quantity": {"kind": "integer","required": true,"minimum": 1,"maximum": 9999},
        "supply_state": {"kind": "enum","required": true,"choices": ["requested","supplied"],"filterable": true}
      }
    },
    "business": {
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
  },
  "actors": {
    "coordinator": {"role": "coordinator"},
    "reporter": {"role": "reporter"},
    "other_reporter": {"role": "reporter"},
    "technician": {"role": "technician"},
    "other_technician": {"role": "technician"},
    "auditor": {"role": "auditor"}
  },
  "fixtures": {
    "site": {"name": "Riverside Campus","zone": "north"},
    "asset": {"name": "Cooling Pump A","asset_code": "PUMP-001","condition": "maintenance"},
    "fault": {"title": "Pump pressure alarm","severity": "high","details": "Pressure outside normal range"},
    "other_fault": {"title": "Independent lighting issue","severity": "low","details": "Synthetic second reporter record"},
    "work_order": {"title": "Restore cooling pump","priority": "urgent","due_at": "2020-01-01T00:00:00Z"},
    "inspection": {"title": "Post-repair safety inspection","scheduled_on": "2026-10-08"},
    "parts_request": {"title": "Replacement pressure valve","quantity": 2}
  },
  "expected_checks": [
    "facilities-linked-resources",
    "facilities-reporter-isolation",
    "facilities-triage-permission",
    "facilities-assignment",
    "facilities-technician-isolation",
    "facilities-due-notice",
    "facilities-workflow-and-note",
    "facilities-parts-scope",
    "facilities-inspection",
    "facilities-auditor-read-only",
    "facilities-metrics",
    "facilities-restart"
  ],
  "scenario": [
    {
      "id": "facilities-linked-resources",
      "requests": [
        {"actor": "coordinator","method": "POST","path": "/api/sites","status": 201,"fixture": "site","save": "site"},
        {
          "actor": "coordinator",
          "method": "POST",
          "path": "/api/assets",
          "status": 201,
          "fixture": "asset",
          "json": {"site_id": "${site.id}"},
          "save": "asset"
        },
        {
          "actor": "reporter",
          "method": "POST",
          "path": "/api/faults",
          "status": 201,
          "fixture": "fault",
          "json": {"asset_id": "${asset.id}"},
          "save": "fault"
        },
        {
          "actor": "other_reporter",
          "method": "POST",
          "path": "/api/faults",
          "status": 201,
          "fixture": "other_fault",
          "json": {"asset_id": "${asset.id}"},
          "save": "other_fault"
        },
        {
          "actor": "coordinator",
          "method": "POST",
          "path": "/api/work_orders",
          "status": 201,
          "fixture": "work_order",
          "json": {"fault_id": "${fault.id}","asset_id": "${asset.id}"},
          "save": "order"
        },
        {
          "actor": "coordinator",
          "method": "POST",
          "path": "/api/inspections",
          "status": 201,
          "fixture": "inspection",
          "json": {"asset_id": "${asset.id}"},
          "save": "inspection"
        }
      ]
    },
    {
      "id": "facilities-reporter-isolation",
      "requests": [
        {"actor": "reporter","method": "GET","path": "/api/faults","status": 200,"assertions": [{"path": [],"ids": ["${fault.id}"]}]},
        {"actor": "other_reporter","method": "GET","path": "/api/faults/${fault.id}","status": 404}
      ]
    },
    {
      "id": "facilities-triage-permission",
      "requests": [
        {"actor": "reporter","method": "POST","path": "/api/faults/${fault.id}/transition","status": 403,"json": {"transition": "triage"}},
        {
          "actor": "coordinator",
          "method": "POST",
          "path": "/api/faults/${fault.id}/transition",
          "status": 200,
          "json": {"transition": "triage"},
          "assertions": [{"path": ["fault_state"],"equals": "triaged"}]
        }
      ]
    },
    {
      "id": "facilities-assignment",
      "requests": [
        {
          "actor": "coordinator",
          "method": "POST",
          "path": "/api/work_orders/${order.id}/assign",
          "status": 422,
          "json": {"user_id": "${actors.reporter.id}"}
        },
        {
          "actor": "coordinator",
          "method": "POST",
          "path": "/api/work_orders/${order.id}/assign",
          "status": 200,
          "json": {"user_id": "${actors.technician.id}"},
          "assertions": [{"path": ["assignee_id"],"equals": "${actors.technician.id}"}]
        },
        {
          "actor": "coordinator",
          "method": "POST",
          "path": "/api/inspections/${inspection.id}/assign",
          "status": 200,
          "json": {"user_id": "${actors.technician.id}"},
          "assertions": [{"path": ["assignee_id"],"equals": "${actors.technician.id}"}]
        }
      ]
    },
    {
      "id": "facilities-technician-isolation",
      "requests": [
        {"actor": "other_technician","method": "GET","path": "/api/work_orders/${order.id}","status": 404},
        {"actor": "other_technician","method": "GET","path": "/api/inspections/${inspection.id}","status": 404},
        {
          "actor": "technician",
          "method": "PUT",
          "path": "/api/work_orders/${order.id}",
          "status": 422,
          "json": {"assignee_id": "${actors.other_technician.id}"}
        }
      ]
    },
    {
      "id": "facilities-due-notice",
      "requests": [
        {
          "actor": "technician",
          "method": "GET",
          "path": "/business/notifications",
          "status": 200,
          "save": "first_notices",
          "assertions": [
            {"path": [],"where": {"event": "assigned","record_id": "${order.id}"},"count": 1},
            {"path": [],"where": {"event": "due","record_id": "${order.id}"},"count": 1}
          ]
        },
        {
          "actor": "technician",
          "method": "GET",
          "path": "/business/notifications",
          "status": 200,
          "assertions": [{"path": [],"equals": "${first_notices}"}]
        },
        {"actor": "other_technician","method": "GET","path": "/business/notifications","status": 200,"assertions": [{"path": [],"count": 0}]}
      ]
    },
    {
      "id": "facilities-workflow-and-note",
      "requests": [
        {"actor": "technician","method": "POST","path": "/api/work_orders/${order.id}/transition","status": 409,"json": {"transition": "finish"}},
        {
          "actor": "technician",
          "method": "POST",
          "path": "/api/work_orders/${order.id}/transition",
          "status": 200,
          "json": {"transition": "start"},
          "assertions": [{"path": ["state"],"equals": "active"}]
        },
        {
          "actor": "technician",
          "method": "POST",
          "path": "/api/work_orders/${order.id}/notes",
          "status": 201,
          "json": {"body": "Inspected valve and recorded corrective action"}
        },
        {
          "actor": "technician",
          "method": "POST",
          "path": "/api/work_orders/${order.id}/transition",
          "status": 200,
          "json": {"transition": "finish"},
          "save": "completed_order",
          "assertions": [{"path": ["state"],"equals": "done"},{"path": ["completed_at"],"timestamp": true}]
        },
        {
          "actor": "coordinator",
          "method": "POST",
          "path": "/api/faults/${fault.id}/transition",
          "status": 200,
          "json": {"transition": "close"},
          "save": "closed_fault",
          "assertions": [{"path": ["fault_state"],"equals": "closed"}]
        },
        {
          "actor": "coordinator",
          "method": "GET",
          "path": "/api/work_orders/${order.id}/notes",
          "status": 200,
          "assertions": [{"path": [],"contains": {"body": "Inspected valve and recorded corrective action"}}]
        }
      ]
    },
    {
      "id": "facilities-parts-scope",
      "requests": [
        {
          "actor": "technician",
          "method": "POST",
          "path": "/api/parts_requests",
          "fixture": "parts_request",
          "json": {"work_order_id": "${order.id}","supply_state": "supplied"},
          "status": 422
        },
        {
          "actor": "technician",
          "method": "POST",
          "path": "/api/parts_requests",
          "status": 201,
          "fixture": "parts_request",
          "json": {"work_order_id": "${order.id}"},
          "save": "parts",
          "assertions": [{"path": ["supply_state"],"equals": "requested"}]
        },
        {"actor": "other_technician","method": "GET","path": "/api/parts_requests/${parts.id}","status": 404},
        {
          "actor": "technician",
          "method": "POST",
          "path": "/api/parts_requests/${parts.id}/transition",
          "json": {"transition": "confirm_supply"},
          "status": 403
        },
        {
          "actor": "coordinator",
          "method": "POST",
          "path": "/api/parts_requests/${parts.id}/transition",
          "json": {"transition": "confirm_supply"},
          "status": 200,
          "save": "supplied_parts",
          "assertions": [{"path": ["supply_state"],"equals": "supplied"}]
        }
      ]
    },
    {
      "id": "facilities-inspection",
      "requests": [
        {
          "actor": "technician",
          "method": "POST",
          "path": "/api/inspections/${inspection.id}/transition",
          "status": 200,
          "json": {"transition": "pass_check"},
          "save": "checked_inspection",
          "assertions": [{"path": ["result_state"],"equals": "passed"},{"path": ["checked_at"],"timestamp": true}]
        }
      ]
    },
    {
      "id": "facilities-auditor-read-only",
      "requests": [
        {
          "actor": "auditor",
          "method": "GET",
          "path": "/api/work_orders/${order.id}",
          "status": 200,
          "assertions": [{"path": ["state"],"equals": "done"}]
        },
        {"actor": "auditor","method": "PUT","path": "/api/assets/${asset.id}","status": 403,"json": {"condition": "retired"}},
        {
          "actor": "auditor",
          "method": "GET",
          "path": "/api/work_orders/${order.id}/history",
          "status": 200,
          "assertions": [{"path": [],"contains": {"action": "assigned"}},{"path": [],"contains": {"action": "transitioned:finish"}}]
        }
      ]
    },
    {
      "id": "facilities-metrics",
      "requests": [
        {
          "actor": "auditor",
          "method": "GET",
          "path": "/business/metrics",
          "status": 200,
          "assertions": [
            {"path": [],"count": 5},
            {"path": [],"contains": {"name": "asset_count","value": 1}},
            {"path": [],"contains": {"name": "open_faults","value": 1}},
            {"path": [],"contains": {"name": "work_order_states","groups": [{"key": "done","count": 1}]}},
            {"path": [],"contains": {"name": "mean_repair_seconds","samples": 1,"unit": "seconds"}},
            {"path": ["value"],"where": {"name": "mean_repair_seconds"},"one": true,"gte": 0}
          ]
        }
      ]
    },
    {
      "id": "facilities-restart",
      "requests": [
        {
          "actor": "technician",
          "method": "GET",
          "path": "/api/work_orders/${order.id}",
          "status": 200,
          "assertions": [{"path": [],"equals": "${completed_order}"}]
        },
        {
          "actor": "technician",
          "method": "GET",
          "path": "/api/inspections/${inspection.id}",
          "status": 200,
          "assertions": [{"path": [],"equals": "${checked_inspection}"}]
        },
        {
          "actor": "reporter",
          "method": "GET",
          "path": "/api/faults/${fault.id}",
          "status": 200,
          "assertions": [{"path": [],"equals": "${closed_fault}"}]
        },
        {"actor": "other_technician","method": "GET","path": "/api/parts_requests/${parts.id}","status": 404}
      ],
      "restart": true
    }
  ],
  "browser": [
    {"actor": "coordinator","entity": "assets","rows": [{"id": "${asset.id}","values": {"name": "Cooling Pump A","condition": "maintenance"}}]},
    {
      "actor": "reporter",
      "entity": "faults",
      "rows": [{"id": "${fault.id}","values": {"title": "Pump pressure alarm","fault_state": "closed"}}],
      "absent": ["${other_fault.id}"]
    },
    {"actor": "technician","entity": "work_orders","rows": [{"id": "${order.id}","values": {"title": "Restore cooling pump","state": "done"}}]},
    {"actor": "technician","entity": "inspections","rows": [{"id": "${inspection.id}","values": {"result_state": "passed"}}]},
    {
      "actor": "auditor",
      "entity": "parts_requests",
      "rows": [{"id": "${parts.id}","values": {"title": "Replacement pressure valve","quantity": 2,"supply_state": "supplied"}}],
      "readonly": true
    }
  ]
}
````
