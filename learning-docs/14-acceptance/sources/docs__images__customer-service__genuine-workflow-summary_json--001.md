# docs/images/customer-service/genuine-workflow-summary.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：真实浏览器截图的来源与验收边界。** provenance记录模板、Actions运行、平台与上游源码提交以及各PNG的原始SHA；summary保留该历史运行的真实模型与完整工作流结果。它们不是当前提交或其他模板的通过证据。

**对应关系：** 成功运行的原图与回执 → 客服正文图注 → 附录逐字节还原与哈希测试。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `docs/images/customer-service/genuine-workflow-summary.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L84。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1976`。本段原文以LF换行结束。

<!-- learning-source: {"path": "docs/images/customer-service/genuine-workflow-summary.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "897c49010f338f8def2bab2767aab9f721a22462933e04d9d6628da33d724cc5"} -->
````json
// docs/images/customer-service/genuine-workflow-summary.json
{
  "passed": true,
  "real_provider_attempted": true,
  "acceptance_scope": "full_workflow",
  "model": "deepseek-flash",
  "endpoint": "https://api.deepseek.com",
  "run_identity": [
    "36789925373",
    "1",
    "a15137ff1aca04d3091a9c4f7cfa99bb09436d07"
  ],
  "smoke": {
    "passed": true,
    "http_status": 200,
    "actual_provider_request": true
  },
  "workflow": {
    "passed": true,
    "real_model": true,
    "single_initial_smart_consent": true,
    "explicit_customer_obligations_preserved": true,
    "template": "fastapiadmin",
    "ready": true,
    "ui_download": true,
    "download_hash_matches": true,
    "independent_database": true,
    "real_browser": true,
    "restart": true,
    "model_calls": 3,
    "page_errors": 0,
    "aider_edit": "not_exercised",
    "continue_native_index": "not_exercised",
    "daytona": "not_exercised",
    "old_blocked_recovery": "not_exercised_in_real_run"
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
        "prompt_tokens": 8835,
        "completion_tokens": 11386,
        "total_tokens": 20221
      },
      "schema_valid": true
    },
    {
      "http_status": 200,
      "stage": "plan",
      "finish_reason": "stop",
      "content_present": true,
      "reasoning_present": true,
      "usage": {
        "prompt_tokens": 16267,
        "completion_tokens": 6808,
        "total_tokens": 23075
      },
      "schema_valid": true
    },
    {
      "http_status": 200,
      "stage": "review",
      "finish_reason": "stop",
      "content_present": true,
      "reasoning_present": true,
      "usage": {
        "prompt_tokens": 9295,
        "completion_tokens": 2131,
        "total_tokens": 11426
      },
      "schema_valid": true
    }
  ]
}
````
