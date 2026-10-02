# tests/fixtures/customer_design_diagnostics/0e8ebdd/yudao-summary.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/0e8ebdd/yudao-summary.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L1065。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`28816`。本段原文没有结尾换行；手工保存时去掉围栏前为展示添加的最后一个换行，自动还原器会根据SHA判定。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/0e8ebdd/yudao-summary.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "755265754504037327c38c643592894c51cd9789ac399023f1037b6b299c5631"} -->
````json
// tests/fixtures/customer_design_diagnostics/0e8ebdd/yudao-summary.json
{
  "passed": false,
  "real_provider_attempted": true,
  "acceptance_scope": "full_workflow",
  "model": "deepseek-flash",
  "endpoint": "https://api.deepseek.com",
  "run_identity": [
    "36826237130",
    "1",
    "0e8ebdd0c74a86538b648d55b9fe56dcc71a9de9"
  ],
  "smoke": {
    "passed": true,
    "http_status": 200,
    "actual_provider_request": true
  },
  "failure_phase": "workflow",
  "failure_code": "workflow_not_ready",
  "failure_details": {
    "model_stages": [
      {
        "stage": "recommend",
        "completed": true,
        "questions_count": 0,
        "unsupported_count": 0,
        "field_requirements_count": 19
      },
      {
        "stage": "plan",
        "completed": true,
        "unsupported_count": 0
      },
      {
        "stage": "plan",
        "completed": true,
        "unsupported_count": 0
      },
      {
        "stage": "plan",
        "completed": true,
        "unsupported_count": 0
      }
    ],
    "terminal_state": "BLOCKED",
    "runtime_diagnostics": {
      "error_excerpt": "\u667a\u80fd\u63a8\u8350\u5df2\u6682\u505c\uff08design\uff09\uff1a\u5df2\u786e\u8ba4\u5b57\u6bb5 requests.customer_id.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True\uff1b\u5df2\u786e\u8ba4\u5b57\u6bb5 requests.assignee_id.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True\uff1b\u5df2\u786e\u8ba4\u5b57\u6bb5 requests.request_state.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True\uff1b\u5df2\u786e\u8ba4\u5b57\u6bb5 requests.priority.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True\uff1b\u5df2\u786e\u8ba4\u5b57\u6bb5 tasks.request_id.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True\uff1b\u5df2\u786e\u8ba4\u5b57\u6bb5 tasks.assignee_id.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True\uff1b\u5df2\u786e\u8ba4\u5b57\u6bb5 tasks.task_state.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True\uff1b\u8bbe\u8ba1\u672a\u8986\u76d6\u5df2\u786e\u8ba4\u7684 searchable: requests::detail\u3001customer_id\u3001assignee_id\u3001request_state\u3001resolved_at\u3001due_at\u3001priority\uff0c\u652f\u6301 title/detail \u5173\u952e\u8bcd\u641c\u7d22\u4e0e \uff1b\u8bbe\u8ba1\u672a\u8986\u76d6\u5df2\u786e\u8ba4\u7684 se\u3002\u672c\u9636\u6bb5\u4e24\u8f6e\u81ea\u52a8\u4fee\u6b63\u4ecd\u672a\u901a\u8fc7\uff0c\u672a\u8df3\u8fc7\u9a8c\u6536\u3002\u4f7f\u7528 uv run rnd chat --run 83833fa9-fab7-4d7f-ac7f-2c941fcaa376 \u67e5"
    },
    "pending_stage": "design",
    "model_calls": 6,
    "valid_plan_present": true,
    "business_contract_present": true,
    "business_counts": {
      "roles": 3,
      "resources": 3,
      "relations": 4,
      "permissions": 8,
      "workflows": 2,
      "notifications": 11,
      "metrics": 5
    },
    "plan_contract": [
      {
        "name": "customers",
        "fields": [
          {
            "name": "name",
            "required": true,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 120,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "organization",
            "required": false,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 160,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "contact",
            "required": false,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "category",
            "required": true,
            "searchable": false,
            "filterable": true,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "enum",
            "choices_count": 3
          }
        ]
      },
      {
        "name": "requests",
        "fields": [
          {
            "name": "title",
            "required": true,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "detail",
            "required": true,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 3000,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "customer_id",
            "required": true,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "assignee_id",
            "required": false,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "request_state",
            "required": true,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "enum",
            "choices_count": 3
          },
          {
            "name": "resolved_at",
            "required": false,
            "searchable": false,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "datetime",
            "choices_count": 0
          },
          {
            "name": "due_at",
            "required": false,
            "searchable": false,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "datetime",
            "choices_count": 0
          },
          {
            "name": "priority",
            "required": true,
            "searchable": true,
            "filterable": true,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "enum",
            "choices_count": 2
          }
        ]
      },
      {
        "name": "tasks",
        "fields": [
          {
            "name": "title",
            "required": true,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "detail",
            "required": true,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 3000,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "request_id",
            "required": true,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "assignee_id",
            "required": false,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "text",
            "choices_count": 0
          },
          {
            "name": "task_state",
            "required": true,
            "searchable": true,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "enum",
            "choices_count": 3
          },
          {
            "name": "resolved_at",
            "required": false,
            "searchable": false,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "datetime",
            "choices_count": 0
          },
          {
            "name": "due_at",
            "required": false,
            "searchable": false,
            "filterable": false,
            "date_range": false,
            "min_length": 0,
            "max_length": 200,
            "kind": "datetime",
            "choices_count": 0
          }
        ]
      }
    ],
    "requirement_contract": [
      {
        "name": "name",
        "entity": "customers",
        "required": true,
        "searchable": true,
        "min_length": 0,
        "max_length": 120,
        "kind": "text"
      },
      {
        "name": "organization",
        "entity": "customers",
        "required": false,
        "searchable": true,
        "min_length": 0,
        "max_length": 160,
        "kind": "text"
      },
      {
        "name": "contact",
        "entity": "customers",
        "required": false,
        "searchable": true,
        "min_length": 0,
        "max_length": 200,
        "kind": "text"
      },
      {
        "name": "category",
        "entity": "customers",
        "required": true,
        "searchable": false,
        "filterable": true,
        "kind": "enum",
        "choices_count": 3
      },
      {
        "name": "title",
        "entity": "requests",
        "required": true,
        "searchable": true,
        "min_length": 0,
        "max_length": 200,
        "kind": "text"
      },
      {
        "name": "detail",
        "entity": "requests",
        "required": true,
        "searchable": true,
        "min_length": 0,
        "max_length": 3000,
        "kind": "text"
      },
      {
        "name": "customer_id",
        "entity": "requests",
        "required": true,
        "searchable": false,
        "date_range": false,
        "kind": "text"
      },
      {
        "name": "assignee_id",
        "entity": "requests",
        "required": false,
        "searchable": false,
        "date_range": false,
        "kind": "text"
      },
      {
        "name": "request_state",
        "entity": "requests",
        "required": true,
        "searchable": false,
        "kind": "enum",
        "choices_count": 3
      },
      {
        "name": "resolved_at",
        "entity": "requests",
        "required": false,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "kind": "datetime"
      },
      {
        "name": "due_at",
        "entity": "requests",
        "required": false,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "kind": "datetime"
      },
      {
        "name": "priority",
        "entity": "requests",
        "required": true,
        "searchable": false,
        "filterable": true,
        "kind": "enum",
        "choices_count": 2
      },
      {
        "name": "title",
        "entity": "tasks",
        "required": true,
        "searchable": true,
        "min_length": 0,
        "max_length": 200,
        "kind": "text"
      },
      {
        "name": "detail",
        "entity": "tasks",
        "required": true,
        "searchable": true,
        "min_length": 0,
        "max_length": 3000,
        "kind": "text"
      },
      {
        "name": "request_id",
        "entity": "tasks",
        "required": true,
        "searchable": false,
        "date_range": false,
        "kind": "text"
      },
      {
        "name": "assignee_id",
        "entity": "tasks",
        "required": false,
        "searchable": false,
        "date_range": false,
        "kind": "text"
      },
      {
        "name": "task_state",
        "entity": "tasks",
        "required": true,
        "searchable": false,
        "kind": "enum",
        "choices_count": 3
      },
      {
        "name": "resolved_at",
        "entity": "tasks",
        "required": false,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "kind": "datetime"
      },
      {
        "name": "due_at",
        "entity": "tasks",
        "required": false,
        "searchable": false,
        "filterable": false,
        "date_range": false,
        "kind": "datetime"
      }
    ],
    "unsupported_excerpts": [],
    "coverage_reason_excerpts": [
      "\u5df2\u786e\u8ba4\u5b57\u6bb5 requests.customer_id.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True",
      "\u5df2\u786e\u8ba4\u5b57\u6bb5 requests.assignee_id.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True",
      "\u5df2\u786e\u8ba4\u5b57\u6bb5 requests.request_state.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True",
      "\u5df2\u786e\u8ba4\u5b57\u6bb5 requests.priority.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True",
      "\u5df2\u786e\u8ba4\u5b57\u6bb5 tasks.request_id.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True",
      "\u5df2\u786e\u8ba4\u5b57\u6bb5 tasks.assignee_id.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True",
      "\u5df2\u786e\u8ba4\u5b57\u6bb5 tasks.task_state.searchable=False\uff0c\u8bbe\u8ba1\u4e3a True",
      "\u8bbe\u8ba1\u672a\u8986\u76d6\u5df2\u786e\u8ba4\u7684 searchable: requests::detail\u3001customer_id\u3001assignee_id\u3001request_state\u3001resolved_at\u3001due_at\u3001priority\uff0c\u652f\u6301 title/detail \u5173\u952e\u8bcd\u641c\u7d22\u4e0e ",
      "\u8bbe\u8ba1\u672a\u8986\u76d6\u5df2\u786e\u8ba4\u7684 searchable: tasks::detail\u3001request_id\u3001assignee_id\u3001task_state\u3001resolved_at\u3001due_at\uff0c\u652f\u6301 title/detail \u5173\u952e\u8bcd\u641c\u7d22"
    ],
    "coverage_sources": [
      {
        "code": "constraint_mismatch",
        "source": {
          "section": "field_requirements",
          "index": 6
        },
        "source_markers": [],
        "targets": [
          {
            "entity": "requests",
            "field": "customer_id"
          }
        ],
        "attribute": "searchable",
        "expected": false,
        "actual": true
      },
      {
        "code": "constraint_mismatch",
        "source": {
          "section": "field_requirements",
          "index": 7
        },
        "source_markers": [],
        "targets": [
          {
            "entity": "requests",
            "field": "assignee_id"
          }
        ],
        "attribute": "searchable",
        "expected": false,
        "actual": true
      },
      {
        "code": "constraint_mismatch",
        "source": {
          "section": "field_requirements",
          "index": 8
        },
        "source_markers": [],
        "targets": [
          {
            "entity": "requests",
            "field": "request_state"
          }
        ],
        "attribute": "searchable",
        "expected": false,
        "actual": true
      },
      {
        "code": "constraint_mismatch",
        "source": {
          "section": "field_requirements",
          "index": 11
        },
        "source_markers": [],
        "targets": [
          {
            "entity": "requests",
            "field": "priority"
          }
        ],
        "attribute": "searchable",
        "expected": false,
        "actual": true
      },
      {
        "code": "constraint_mismatch",
        "source": {
          "section": "field_requirements",
          "index": 14
        },
        "source_markers": [],
        "targets": [
          {
            "entity": "tasks",
            "field": "request_id"
          }
        ],
        "attribute": "searchable",
        "expected": false,
        "actual": true
      },
      {
        "code": "constraint_mismatch",
        "source": {
          "section": "field_requirements",
          "index": 15
        },
        "source_markers": [],
        "targets": [
          {
            "entity": "tasks",
            "field": "assignee_id"
          }
        ],
        "attribute": "searchable",
        "expected": false,
        "actual": true
      },
      {
        "code": "constraint_mismatch",
        "source": {
          "section": "field_requirements",
          "index": 16
        },
        "source_markers": [],
        "targets": [
          {
            "entity": "tasks",
            "field": "task_state"
          }
        ],
        "attribute": "searchable",
        "expected": false,
        "actual": true
      },
      {
        "code": "uncovered_operation",
        "source": {
          "section": "features",
          "index": 2,
          "clause": 1
        },
        "source_markers": [
          "search"
        ],
        "targets": [
          {
            "entity": "requests",
            "field": "title"
          },
          {
            "entity": "requests",
            "field": "detail"
          },
          {
            "entity": "requests",
            "field": "customer_id"
          },
          {
            "entity": "requests",
            "field": "assignee_id"
          },
          {
            "entity": "requests",
            "field": "request_state"
          },
          {
            "entity": "requests",
            "field": "resolved_at"
          },
          {
            "entity": "requests",
            "field": "due_at"
          },
          {
            "entity": "requests",
            "field": "priority"
          }
        ],
        "attribute": "searchable",
        "expected": true,
        "actual": false,
        "source_excerpt": "\u670d\u52a1\u8bf7\u6c42\u7ba1\u7406\uff1a\u521b\u5efa\u3001\u4fee\u6539\u3001\u67e5\u8be2\u3001\u5f52\u6863\u8bf7\u6c42\uff0c\u5b57\u6bb5\u542b title\u3001detail\u3001customer_id\u3001assignee_id\u3001request_state\u3001resolved_at\u3001due_at\u3001priority\uff0c\u652f\u6301 title/detail \u5173\u952e\u8bcd\u641c\u7d22\u4e0e priority \u7cbe\u786e\u7b5b\u9009\u3002"
      },
      {
        "code": "uncovered_operation",
        "source": {
          "section": "features",
          "index": 3,
          "clause": 1
        },
        "source_markers": [
          "search"
        ],
        "targets": [
          {
            "entity": "tasks",
            "field": "title"
          },
          {
            "entity": "tasks",
            "field": "detail"
          },
          {
            "entity": "tasks",
            "field": "request_id"
          },
          {
            "entity": "tasks",
            "field": "assignee_id"
          },
          {
            "entity": "tasks",
            "field": "task_state"
          },
          {
            "entity": "tasks",
            "field": "resolved_at"
          },
          {
            "entity": "tasks",
            "field": "due_at"
          }
        ],
        "attribute": "searchable",
        "expected": true,
        "actual": false,
        "source_excerpt": "\u534f\u4f5c\u4efb\u52a1\u7ba1\u7406\uff1a\u7ba1\u7406\u4eba\u5458\u521b\u5efa tasks \u5e76\u5206\u914d\u8d1f\u8d23\u4eba\uff0c\u5b57\u6bb5\u542b title\u3001detail\u3001request_id\u3001assignee_id\u3001task_state\u3001resolved_at\u3001due_at\uff0c\u652f\u6301 title/detail \u5173\u952e\u8bcd\u641c\u7d22\u3002"
      }
    ],
    "native_plan_validation": {
      "code": "valid",
      "entity_labels": [
        {
          "entity": "customers",
          "length": 4,
          "single_line": true,
          "allowed_characters": true,
          "valid_length": true
        },
        {
          "entity": "requests",
          "length": 4,
          "single_line": true,
          "allowed_characters": true,
          "valid_length": true
        },
        {
          "entity": "tasks",
          "length": 4,
          "single_line": true,
          "allowed_characters": true,
          "valid_length": true
        }
      ]
    },
    "error_categories": [
      "requirement_coverage"
    ],
    "coverage_block_count": 9,
    "coverage_diagnostics": [
      {
        "codes": [
          "unclassified_design_block"
        ],
        "origin": "requirement_coverage",
        "attributes": [
          "searchable"
        ],
        "fields": [
          "customer_id"
        ]
      },
      {
        "codes": [
          "unclassified_design_block"
        ],
        "origin": "requirement_coverage",
        "attributes": [
          "searchable"
        ],
        "fields": [
          "assignee_id"
        ]
      },
      {
        "codes": [
          "unclassified_design_block"
        ],
        "origin": "requirement_coverage",
        "attributes": [
          "searchable"
        ],
        "fields": [
          "request_state"
        ]
      },
      {
        "codes": [
          "unclassified_design_block"
        ],
        "origin": "requirement_coverage",
        "attributes": [
          "searchable"
        ],
        "fields": [
          "priority"
        ]
      },
      {
        "codes": [
          "unclassified_design_block"
        ],
        "origin": "requirement_coverage",
        "attributes": [
          "searchable"
        ],
        "fields": [
          "request_id"
        ]
      },
      {
        "codes": [
          "unclassified_design_block"
        ],
        "origin": "requirement_coverage",
        "attributes": [
          "searchable"
        ],
        "fields": [
          "assignee_id"
        ]
      },
      {
        "codes": [
          "unclassified_design_block"
        ],
        "origin": "requirement_coverage",
        "attributes": [
          "searchable"
        ],
        "fields": [
          "task_state"
        ]
      },
      {
        "codes": [
          "uncovered_operation"
        ],
        "origin": "requirement_coverage",
        "attributes": [
          "searchable"
        ],
        "fields": [
          "assignee_id",
          "customer_id",
          "detail",
          "due_at",
          "priority",
          "request_state",
          "resolved_at",
          "title"
        ]
      },
      {
        "codes": [
          "uncovered_operation"
        ],
        "origin": "requirement_coverage",
        "attributes": [
          "searchable"
        ],
        "fields": [
          "assignee_id",
          "detail",
          "due_at",
          "request_id",
          "resolved_at",
          "task_state",
          "title"
        ]
      }
    ],
    "unsupported_diagnostics": [],
    "coverage_fields": [
      "assignee_id",
      "customer_id",
      "detail",
      "due_at",
      "priority",
      "request_id",
      "request_state",
      "resolved_at",
      "task_state",
      "title"
    ],
    "approved_plan_replay": {
      "status": "unavailable"
    },
    "unapproved_design_replay": {
      "status": "saved",
      "file": "unapproved-design-contract.json",
      "approval_status": "unapproved",
      "execution_authorized": false,
      "bytes": 48753,
      "sha256": "dd7bf0dbe805ae9d1527b899bd014fd87e1c69179b2134748cdf7d49b0d7c115"
    }
  },
  "actual_http_calls": 7,
  "provider_statuses": [
    200,
    200,
    200,
    200,
    200,
    200,
    200
  ],
  "provider_receipts": [
    {
      "http_status": 200,
      "stage": "recommend",
      "finish_reason": "stop",
      "content_present": true,
      "reasoning_present": true,
      "usage": {
        "prompt_tokens": 9631,
        "completion_tokens": 8340,
        "total_tokens": 17971
      },
      "schema_valid": true,
      "provider": "deepseek",
      "output_mode": "json_object",
      "format_reason": "provider_json_mode",
      "contract_version": 2,
      "structured_output": "langchain.with_structured_output",
      "requested_output_mode": "json_object"
    },
    {
      "http_status": 200,
      "stage": "plan",
      "finish_reason": "stop",
      "content_present": true,
      "reasoning_present": true,
      "usage": {
        "prompt_tokens": 23140,
        "completion_tokens": 5277,
        "total_tokens": 28417
      },
      "schema_valid": true,
      "provider": "deepseek",
      "output_mode": "json_object",
      "format_reason": "provider_json_mode",
      "contract_version": 2,
      "structured_output": "langchain.with_structured_output",
      "requested_output_mode": "json_object"
    },
    {
      "http_status": 200,
      "stage": "plan",
      "finish_reason": "stop",
      "content_present": true,
      "reasoning_present": true,
      "usage": {
        "prompt_tokens": 27349,
        "completion_tokens": 38400,
        "total_tokens": 65749
      },
      "schema_valid": false,
      "schema_error_types": [
        "value_error"
      ],
      "schema_errors": [
        {
          "type": "value_error",
          "message": "Value error, \u5173\u952e\u8bcd\u641c\u7d22\u53ea\u80fd\u4f7f\u7528\u6587\u672c/\u679a\u4e3e\u5b57\u6bb5",
          "field_path": [
            "entities",
            1,
            "fields",
            5
          ]
        },
        {
          "type": "value_error",
          "message": "Value error, \u5173\u952e\u8bcd\u641c\u7d22\u53ea\u80fd\u4f7f\u7528\u6587\u672c/\u679a\u4e3e\u5b57\u6bb5",
          "field_path": [
            "entities",
            1,
            "fields",
            6
          ]
        },
        {
          "type": "value_error",
          "message": "Value error, \u5173\u952e\u8bcd\u641c\u7d22\u53ea\u80fd\u4f7f\u7528\u6587\u672c/\u679a\u4e3e\u5b57\u6bb5",
          "field_path": [
            "entities",
            2,
            "fields",
            5
          ]
        },
        {
          "type": "value_error",
          "message": "Value error, \u5173\u952e\u8bcd\u641c\u7d22\u53ea\u80fd\u4f7f\u7528\u6587\u672c/\u679a\u4e3e\u5b57\u6bb5",
          "field_path": [
            "entities",
            2,
            "fields",
            6
          ]
        }
      ],
      "requested_output_mode": "json_object"
    },
    {
      "http_status": 200,
      "stage": "plan",
      "finish_reason": "stop",
      "content_present": true,
      "reasoning_present": true,
      "usage": {
        "prompt_tokens": 31234,
        "completion_tokens": 4623,
        "total_tokens": 35857
      },
      "schema_valid": true,
      "provider": "deepseek",
      "output_mode": "json_object",
      "format_reason": "provider_json_mode",
      "contract_version": 2,
      "structured_output": "langchain.with_structured_output",
      "requested_output_mode": "json_object"
    },
    {
      "http_status": 200,
      "stage": "plan",
      "finish_reason": "stop",
      "content_present": true,
      "reasoning_present": true,
      "usage": {
        "prompt_tokens": 27436,
        "completion_tokens": 13238,
        "total_tokens": 40674
      },
      "schema_valid": false,
      "schema_error_types": [
        "value_error"
      ],
      "schema_errors": [
        {
          "type": "value_error",
          "message": "Value error, \u5173\u952e\u8bcd\u641c\u7d22\u53ea\u80fd\u4f7f\u7528\u6587\u672c/\u679a\u4e3e\u5b57\u6bb5",
          "field_path": [
            "entities",
            1,
            "fields",
            5
          ]
        },
        {
          "type": "value_error",
          "message": "Value error, \u5173\u952e\u8bcd\u641c\u7d22\u53ea\u80fd\u4f7f\u7528\u6587\u672c/\u679a\u4e3e\u5b57\u6bb5",
          "field_path": [
            "entities",
            1,
            "fields",
            6
          ]
        },
        {
          "type": "value_error",
          "message": "Value error, \u5173\u952e\u8bcd\u641c\u7d22\u53ea\u80fd\u4f7f\u7528\u6587\u672c/\u679a\u4e3e\u5b57\u6bb5",
          "field_path": [
            "entities",
            2,
            "fields",
            5
          ]
        },
        {
          "type": "value_error",
          "message": "Value error, \u5173\u952e\u8bcd\u641c\u7d22\u53ea\u80fd\u4f7f\u7528\u6587\u672c/\u679a\u4e3e\u5b57\u6bb5",
          "field_path": [
            "entities",
            2,
            "fields",
            6
          ]
        }
      ],
      "requested_output_mode": "json_object"
    },
    {
      "http_status": 200,
      "stage": "plan",
      "finish_reason": "stop",
      "content_present": true,
      "reasoning_present": true,
      "usage": {
        "prompt_tokens": 31228,
        "completion_tokens": 3999,
        "total_tokens": 35227
      },
      "schema_valid": true,
      "provider": "deepseek",
      "output_mode": "json_object",
      "format_reason": "provider_json_mode",
      "contract_version": 2,
      "structured_output": "langchain.with_structured_output",
      "requested_output_mode": "json_object"
    }
  ]
}
````
