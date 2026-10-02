# tests/fixtures/customer_design_diagnostics/0e8ebdd/python-summary.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/0e8ebdd/python-summary.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L635。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18684`。本段原文没有结尾换行；手工保存时去掉围栏前为展示添加的最后一个换行，自动还原器会根据SHA判定。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/0e8ebdd/python-summary.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b64b86827ef6ecd63df33ca9fdb3c08ac9b2b9917adc2f32a9e1f1871159f929"} -->
````json
// tests/fixtures/customer_design_diagnostics/0e8ebdd/python-summary.json
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
        "unsupported_count": 1
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
      "error_excerpt": "\u667a\u80fd\u63a8\u8350\u5df2\u6682\u505c\uff08design\uff09\uff1a\u4e1a\u52a1\u6307\u6807\u7f3a\u5c11\u5df2\u786e\u8ba4\u7684\u7b5b\u9009\u6761\u4ef6: \u7edf\u8ba1\u5305\u542b requests \u603b\u6570\u3001\u6309 request_state=resolved \u7b5b\u9009\u7684\u5df2\u89e3\u51b3\u6570\u3001\u7531 created_at \u81f3 resolved_at \u8ba1\u7b97\u7684\u5e73\u5747\u89e3\u51b3\u65f6\u957f\uff08\u79d2\uff09\u3001customers \u6309 category \u7684\u5206\u7ec4\u8ba1\u6570\u3001requests \u6309 created_at \u7684\u6bcf\u65e5\u8d8b\u52bf\uff1b\u670d\u52a1\u4eba\u5458\u6307\u6807\u53ea\u7edf\u8ba1\u672c\u4eba\u53ef\u89c1\u884c\u3002\uff1b\u5df2\u786e\u8ba4\u6761\u4ef6\u7f3a\u5c11\u5bf9\u5e94\u5b57\u6bb5 published_on: \u7cfb\u7edf\u81ea\u52a8\u63d0\u4f9b id/created_at/updated_at/created_by/archived_at\uff0c\u5b9e\u4f53\u5b57\u6bb5\u4e25\u683c\u7b49\u4e8e\u5c01\u95ed\u6e05\u5355\uff0c\u4e0d\u51fa\u73b0 published_on \u6216\u5176\u4ed6\u6848\u4f8b\u5b57\u6bb5\u3002\u672c\u9636\u6bb5\u4e24\u8f6e\u81ea\u52a8\u4fee\u6b63\u4ecd\u672a\u901a\u8fc7\uff0c\u672a\u8df3\u8fc7\u9a8c\u6536\u3002\u4f7f\u7528 uv run rnd chat --run 56bca47c-7db2-4352-9c50-97669238e60b \u67e5\u770b\u963b\u585e\u8be6\u60c5\uff0c\u53ef\u7ee7\u7eed\u63a8\u8350\u3001\u8865\u5145\u8981\u6c42\u6216\u5207\u6362\u624b\u52a8\uff1b\u65e0\u9700\u65b0\u5efa\u8fd0\u884c\u3002"
    },
    "pending_stage": "design",
    "model_calls": 4,
    "valid_plan_present": true,
    "business_contract_present": true,
    "business_counts": {
      "roles": 3,
      "resources": 3,
      "relations": 4,
      "permissions": 8,
      "workflows": 2,
      "notifications": 12,
      "metrics": 8
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
            "searchable": false,
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
            "searchable": false,
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
            "searchable": false,
            "filterable": true,
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
            "searchable": false,
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
            "searchable": false,
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
            "searchable": false,
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
            "searchable": false,
            "filterable": true,
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
      "\u4e1a\u52a1\u6307\u6807\u7f3a\u5c11\u5df2\u786e\u8ba4\u7684\u7b5b\u9009\u6761\u4ef6: \u7edf\u8ba1\u5305\u542b requests \u603b\u6570\u3001\u6309 request_state=resolved \u7b5b\u9009\u7684\u5df2\u89e3\u51b3\u6570\u3001\u7531 created_at \u81f3 resolved_at \u8ba1\u7b97\u7684\u5e73\u5747\u89e3\u51b3\u65f6\u957f\uff08\u79d2\uff09\u3001customers \u6309 category \u7684\u5206\u7ec4\u8ba1\u6570\u3001requests \u6309 created_at \u7684\u6bcf\u65e5\u8d8b\u52bf\uff1b\u670d\u52a1\u4eba\u5458\u6307\u6807\u53ea\u7edf\u8ba1\u672c\u4eba\u53ef\u89c1\u884c\u3002",
      "\u5df2\u786e\u8ba4\u6761\u4ef6\u7f3a\u5c11\u5bf9\u5e94\u5b57\u6bb5 published_on: \u7cfb\u7edf\u81ea\u52a8\u63d0\u4f9b id/created_at/updated_at/created_by/archived_at\uff0c\u5b9e\u4f53\u5b57\u6bb5\u4e25\u683c\u7b49\u4e8e\u5c01\u95ed\u6e05\u5355\uff0c\u4e0d\u51fa\u73b0 published_on \u6216\u5176\u4ed6\u6848\u4f8b\u5b57\u6bb5"
    ],
    "coverage_sources": [
      {
        "code": "missing_metric_predicate",
        "source": {
          "section": "acceptance",
          "index": 7,
          "metric_clause": 0
        },
        "source_markers": [
          "filter",
          "metric"
        ],
        "targets": [
          {
            "entity": "customers",
            "field": "category"
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
            "entity": "tasks",
            "field": "resolved_at"
          }
        ],
        "attribute": "metric_filter",
        "expected": true,
        "actual": false,
        "source_excerpt": "\u7edf\u8ba1\u5305\u542b requests \u603b\u6570\u3001\u6309 request_state=resolved \u7b5b\u9009\u7684\u5df2\u89e3\u51b3\u6570\u3001\u7531 created_at \u81f3 resolved_at \u8ba1\u7b97\u7684\u5e73\u5747\u89e3\u51b3\u65f6\u957f\uff08\u79d2\uff09\u3001customers \u6309 category \u7684\u5206\u7ec4\u8ba1\u6570\u3001requests \u6309 created_at \u7684\u6bcf\u65e5\u8d8b\u52bf\uff1b\u670d\u52a1\u4eba\u5458\u6307\u6807\u53ea\u7edf\u8ba1\u672c\u4eba\u53ef\u89c1\u884c\u3002"
      },
      {
        "code": "legacy_missing_field",
        "source": {
          "section": "acceptance",
          "index": 10,
          "clause": 0
        },
        "source_markers": [],
        "targets": [],
        "attribute": null,
        "expected": null,
        "actual": null,
        "source_excerpt": "\u7cfb\u7edf\u81ea\u52a8\u63d0\u4f9b id/created_at/updated_at/created_by/archived_at\uff0c\u5b9e\u4f53\u5b57\u6bb5\u4e25\u683c\u7b49\u4e8e\u5c01\u95ed\u6e05\u5355\uff0c\u4e0d\u51fa\u73b0 published_on \u6216\u5176\u4ed6\u6848\u4f8b\u5b57\u6bb5\u3002"
      }
    ],
    "error_categories": [
      "requirement_coverage"
    ],
    "coverage_block_count": 2,
    "coverage_diagnostics": [
      {
        "codes": [
          "missing_metric_predicate"
        ],
        "origin": "requirement_coverage",
        "attributes": [],
        "fields": [
          "category",
          "request_state",
          "resolved_at"
        ]
      },
      {
        "codes": [
          "legacy_missing_field"
        ],
        "origin": "requirement_coverage",
        "attributes": [],
        "fields": []
      }
    ],
    "unsupported_diagnostics": [],
    "coverage_fields": [
      "category",
      "request_state",
      "resolved_at"
    ],
    "approved_plan_replay": {
      "status": "unavailable"
    },
    "unapproved_design_replay": {
      "status": "saved",
      "file": "unapproved-design-contract.json",
      "approval_status": "unapproved",
      "execution_authorized": false,
      "bytes": 49293,
      "sha256": "a492b0e6e379b6062698bfde77b05a52ba81aab7e7b47d2a84e15e5173fd7ab6"
    }
  },
  "actual_http_calls": 5,
  "provider_statuses": [
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
        "prompt_tokens": 9659,
        "completion_tokens": 9919,
        "total_tokens": 19578
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
        "prompt_tokens": 13717,
        "completion_tokens": 5942,
        "total_tokens": 19659
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
        "prompt_tokens": 17905,
        "completion_tokens": 18204,
        "total_tokens": 36109
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
        "prompt_tokens": 18515,
        "completion_tokens": 13571,
        "total_tokens": 32086
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
