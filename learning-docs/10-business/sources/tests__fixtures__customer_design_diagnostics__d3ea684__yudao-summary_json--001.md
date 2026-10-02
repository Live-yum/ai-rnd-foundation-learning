# tests/fixtures/customer_design_diagnostics/d3ea684/yudao-summary.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tests/fixtures/customer_design_diagnostics/d3ea684/yudao-summary.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L574。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16693`。本段原文没有结尾换行；手工保存时去掉围栏前为展示添加的最后一个换行，自动还原器会根据SHA判定。

<!-- learning-source: {"path": "tests/fixtures/customer_design_diagnostics/d3ea684/yudao-summary.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b4197e6d957341b5e8e770a37f0f3cd9b2b1bf67ba2483ac1565c5c2c9d9654b"} -->
````json
// tests/fixtures/customer_design_diagnostics/d3ea684/yudao-summary.json
{
  "passed": false,
  "real_provider_attempted": true,
  "acceptance_scope": "full_workflow",
  "model": "deepseek-flash",
  "endpoint": "https://api.deepseek.com",
  "run_identity": [
    "36899875461",
    "1",
    "d3ea6848360054bc83792bb5c6defbe34409b0a9"
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
        "stage": "review",
        "completed": true,
        "uncovered_requirements_count": 1,
        "uncovered_requirement_excerpts": [
          "\u9a8c\u6536\u6807\u51c6\u7b2c 5 \u6761\u201cmanager/service \u53ef\u521b\u5efa\u670d\u52a1\u8bf7\u6c42\u5e76\u6307\u5b9a\u5173\u8054\u5ba2\u6237\u4e0e\u4f18\u5148\u7ea7\u201d\u4e2d\u7684 service \u521b\u5efa\u8bf7\u6c42\u80fd\u529b\u672a\u5b9e\u73b0\uff1a\u5df2\u6279\u51c6 business \u6743\u9650\u5408\u540c\u672a\u7ed9 service \u6388\u4e88 requests.create\uff0c\u8fd0\u884c\u8bc1\u636e\u4ea6\u663e\u793a service \u521b\u5efa\u8bf7\u6c42\u88ab\u62d2\uff08unauthorized_action\u3001denied=true\u3001observed_count=0\uff09\u3002\u8be5\u9a8c\u6536\u9879\u4e0e\u6743\u9650\u5408\u540c\u76f8\u4e92\u77db\u76fe\uff0c\u9700\u5148\u7531\u9700\u6c42\u65b9\u88c1\u5b9a\uff08\u6539\u9a8c\u6536\u6587\u672c\u6216\u8865 create \u6743\u9650\uff09\u540e\u91cd\u65b0\u9a8c\u8bc1\uff0c\u5f53\u524d\u6309\u6743\u9650\u5408\u540c\u4ea4\u4ed8\u7684\u72b6\u6001\u4e0b\u8be5\u9879\u4e0d\u6210\u7acb\u3002"
        ]
      }
    ],
    "terminal_state": "BLOCKED",
    "runtime_diagnostics": {
      "error_excerpt": "\u5ba1\u9605\u53d1\u73b0\u5df2\u6279\u51c6\u4f46\u672a\u8986\u76d6\u7684\u9700\u6c42\uff0c\u5df2\u6682\u505c\u4ea4\u4ed8\uff1a\u9a8c\u6536\u6807\u51c6\u7b2c 5 \u6761\u201cmanager/service \u53ef\u521b\u5efa\u670d\u52a1\u8bf7\u6c42\u5e76\u6307\u5b9a\u5173\u8054\u5ba2\u6237\u4e0e\u4f18\u5148\u7ea7\u201d\u4e2d\u7684 service \u521b\u5efa\u8bf7\u6c42\u80fd\u529b\u672a\u5b9e\u73b0\uff1a\u5df2\u6279\u51c6 business \u6743\u9650\u5408\u540c\u672a\u7ed9 service \u6388\u4e88 requests.create\uff0c\u8fd0\u884c\u8bc1\u636e\u4ea6\u663e\u793a service \u521b\u5efa\u8bf7\u6c42\u88ab\u62d2\uff08unauthorized_action\u3001denied=true\u3001observed_count=0\uff09\u3002\u8be5\u9a8c\u6536\u9879\u4e0e\u6743\u9650\u5408\u540c\u76f8\u4e92\u77db\u76fe\uff0c\u9700\u5148\u7531\u9700\u6c42\u65b9\u88c1\u5b9a\uff08\u6539\u9a8c\u6536\u6587\u672c\u6216\u8865 create \u6743\u9650\uff09\u540e\u91cd\u65b0\u9a8c\u8bc1\uff0c\u5f53\u524d\u6309\u6743\u9650\u5408\u540c\u4ea4\u4ed8\u7684\u72b6\u6001\u4e0b\u8be5\u9879\u4e0d\u6210\u7acb\u3002\u3002\u67e5\u770b model-review.json\uff1b\u4fee\u590d\u5b9e\u73b0\u5e76\u91cd\u65b0\u9a8c\u6536\uff0c\u4e0d\u80fd\u76f4\u63a5\u5ffd\u7565\u62a5\u544a\u3002",
      "native_stage": "accepted",
      "native_template": "yudao-vben"
    },
    "pending_stage": null,
    "model_calls": 3,
    "valid_plan_present": true,
    "business_contract_present": true,
    "business_counts": {
      "roles": 3,
      "resources": 3,
      "relations": 4,
      "permissions": 8,
      "workflows": 2,
      "notifications": 10,
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
        "filterable": false,
        "date_range": false,
        "kind": "text"
      },
      {
        "name": "assignee_id",
        "entity": "requests",
        "required": false,
        "searchable": false,
        "filterable": false,
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
        "filterable": false,
        "date_range": false,
        "kind": "text"
      },
      {
        "name": "assignee_id",
        "entity": "tasks",
        "required": false,
        "searchable": false,
        "filterable": false,
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
    "coverage_reason_excerpts": [],
    "coverage_sources": [],
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
    "error_categories": [],
    "coverage_block_count": 0,
    "coverage_diagnostics": [],
    "unsupported_diagnostics": [],
    "coverage_fields": [],
    "approved_plan_replay": {
      "status": "saved",
      "file": "approved-plan-replay.json",
      "bytes": 20360,
      "sha256": "331949a9d65a16399d5dfd63c9a7031744f765b7e370ef77ee5603b87fdf16d6",
      "exact_normalized_plan": true
    },
    "unapproved_design_replay": {
      "status": "saved",
      "file": "unapproved-design-contract.json",
      "approval_status": "unapproved",
      "execution_authorized": false,
      "bytes": 49388,
      "sha256": "1a42c492a59cfd70c162cdb5c33999e77684cfa0342e1de59280988eb48100a1"
    }
  },
  "actual_http_calls": 4,
  "provider_statuses": [
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
        "prompt_tokens": 9707,
        "completion_tokens": 11016,
        "total_tokens": 20723
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
        "prompt_tokens": 23417,
        "completion_tokens": 6417,
        "total_tokens": 29834
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
      "stage": "review",
      "finish_reason": "stop",
      "content_present": true,
      "reasoning_present": true,
      "usage": {
        "prompt_tokens": 30074,
        "completion_tokens": 7133,
        "total_tokens": 37207
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
