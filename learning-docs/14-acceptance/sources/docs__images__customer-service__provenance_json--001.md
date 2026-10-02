# docs/images/customer-service/provenance.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：真实浏览器截图的来源与验收边界。** provenance记录模板、Actions运行、平台与上游源码提交以及各PNG的原始SHA；summary保留该历史运行的真实模型与完整工作流结果。它们不是当前提交或其他模板的通过证据。

**对应关系：** 成功运行的原图与回执 → 客服正文图注 → 附录逐字节还原与哈希测试。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `docs/images/customer-service/provenance.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L64。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2139`。本段原文以LF换行结束。

<!-- learning-source: {"path": "docs/images/customer-service/provenance.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "54a601ae41ea61fbeef6db3e18fa3adb1ba3e75377f3dc62d00035580180ee9e"} -->
````json
// docs/images/customer-service/provenance.json
{
  "format": 1,
  "template": "fastapiadmin",
  "source_sha": "a15137ff1aca04d3091a9c4f7cfa99bb09436d07",
  "run_id": 36789925373,
  "run_attempt": 1,
  "run_url": "https://github.com/Live-yum/ai-rnd-foundation-learning/actions/runs/36789925373",
  "genuine_model": true,
  "acceptance_scope": "full_workflow",
  "model": "deepseek-flash",
  "upstream_template_sha": "1cd12c726ad9032c17ef85ce805ce991be60fbdf",
  "workflow_summary": "genuine-workflow-summary.json",
  "evidence_scope": "Historical successful real-model FastapiAdmin run only; not current-commit or other-template acceptance. Browser data and accounts are synthetic test inputs, not simulated UI.",
  "screenshots": [
    {
      "file": "manager-customers-native-form.png",
      "sha256": "4a40727a793588d97d2d406681ec39d822256ba6fa612c47e037d74821114eab",
      "width": 1600,
      "height": 1100,
      "pixel_reviewed": true,
      "modified": false
    },
    {
      "file": "employee-native-list.png",
      "sha256": "ae3e90d11531a31f8d0d3203a4fa5bce0c27e47dfd7f5c8469e9a5aebb0b000a",
      "width": 1600,
      "height": 1100,
      "pixel_reviewed": true,
      "modified": false
    },
    {
      "file": "manager-requests-assignment.png",
      "sha256": "fdf646baa1fffc7a6e6e6d4b8c434f15a50dc8f102c5ee77610d5e4b90b21577",
      "width": 1600,
      "height": 1100,
      "pixel_reviewed": true,
      "modified": false
    },
    {
      "file": "service-handling-history.png",
      "sha256": "d3c16dd3b8c0e769335bd5a2dd897c31579543235c23a8f280b515fdc242238c",
      "width": 1600,
      "height": 1100,
      "pixel_reviewed": true,
      "modified": false
    },
    {
      "file": "employee-resolution-reminders.png",
      "sha256": "d11c174a803b780a384c871b4e64606ff5849199b70a5ea892fddbaee20025ba",
      "width": 1600,
      "height": 1100,
      "pixel_reviewed": true,
      "modified": false
    },
    {
      "file": "manager-native-dashboard.png",
      "sha256": "66bef9518e84d049e4f02a93493724bbb6b0a0415e7064f5aa6c4f4dc1b8ccb8",
      "width": 1600,
      "height": 1100,
      "pixel_reviewed": true,
      "modified": false
    }
  ]
}
````
