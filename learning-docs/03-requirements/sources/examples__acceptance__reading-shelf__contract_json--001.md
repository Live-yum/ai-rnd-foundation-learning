# examples/acceptance/reading-shelf/contract.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可审查的需求与完整合同验收样例。** 自然语言说明目标，JSON计划逐项登记实体、字段、关系、角色、转换和指标。它用于确定性验收，不是生产模型失败后的隐藏答案；改需求需修改并重新批准相应合同。

**对应关系：** 按正文验证Plan → ci_native_bundled --spec → 真实原生工具验收；该文件随教材一并还原。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `examples/acceptance/reading-shelf/contract.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L158。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5078`。本段原文以LF换行结束。

<!-- learning-source: {"path": "examples/acceptance/reading-shelf/contract.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e24d351661b3c6308e388911754bf00a74e26e51b6d4d7ccf309fe22252ebc15"} -->
````json
// examples/acceptance/reading-shelf/contract.json
{
  "id": "reading-shelf",
  "size": "small",
  "title": "个人阅读书架",
  "contract": {
    "data_scope": "per_user",
    "entities": {
      "books": {
        "title": {"kind": "text","required": true,"max_length": 200,"searchable": true},
        "author": {"kind": "text","required": true,"max_length": 200,"searchable": true},
        "category": {"kind": "enum","required": true,"choices": ["technology","literature","science"],"filterable": true},
        "status": {"kind": "enum","required": true,"choices": ["planned","reading","finished"],"filterable": true},
        "pages": {"kind": "integer","required": true,"minimum": 1,"maximum": 10000},
        "started_on": {"kind": "date","required": true,"date_range": true},
        "note": {"kind": "text","required": false,"max_length": 3000}
      }
    }
  },
  "actors": {"reader": {},"other_reader": {}},
  "fixtures": {
    "book": {
      "title": "Practical Graph Learning",
      "author": "Ada",
      "category": "technology",
      "status": "reading",
      "pages": 320,
      "started_on": "2026-01-01",
      "note": "Read chapter one"
    },
    "control": {
      "title": "Ocean Stories",
      "author": "Beryl",
      "category": "literature",
      "status": "planned",
      "pages": 180,
      "started_on": "2026-01-02",
      "note": null
    }
  },
  "expected_checks": [
    "reading-create",
    "reading-combined-query",
    "reading-inclusive-date",
    "reading-invalid-pages",
    "reading-owner-isolation",
    "reading-update",
    "reading-delete",
    "reading-restart"
  ],
  "scenario": [
    {
      "id": "reading-create",
      "requests": [
        {
          "actor": "reader",
          "method": "POST",
          "path": "/api/books",
          "status": 201,
          "fixture": "book",
          "save": "book",
          "assertions": [{"path": ["status"],"equals": "reading"}]
        },
        {"actor": "reader","method": "POST","path": "/api/books","status": 201,"fixture": "control","save": "control"}
      ]
    },
    {
      "id": "reading-combined-query",
      "requests": [
        {
          "actor": "reader",
          "method": "GET",
          "path": "/api/books",
          "status": 200,
          "params": {"q": "Graph","filter_category": "technology","filter_status": "reading"},
          "assertions": [{"path": [],"ids": ["${book.id}"]}]
        }
      ]
    },
    {
      "id": "reading-inclusive-date",
      "requests": [
        {
          "actor": "reader",
          "method": "GET",
          "path": "/api/books",
          "status": 200,
          "params": {"from_started_on": "2026-01-01","to_started_on": "2026-01-01"},
          "assertions": [{"path": [],"ids": ["${book.id}"]}]
        }
      ]
    },
    {
      "id": "reading-invalid-pages",
      "requests": [{"actor": "reader","method": "POST","path": "/api/books","status": 422,"fixture": "book","json": {"pages": 0}}]
    },
    {
      "id": "reading-owner-isolation",
      "requests": [
        {
          "actor": "other_reader",
          "method": "GET",
          "path": "/api/books",
          "status": 200,
          "params": {"q": "Graph"},
          "assertions": [{"path": [],"count": 0}]
        },
        {"actor": "other_reader","method": "GET","path": "/api/books/${book.id}","status": 404},
        {"actor": "other_reader","method": "PUT","path": "/api/books/${book.id}","status": 404,"fixture": "book"},
        {"actor": "other_reader","method": "DELETE","path": "/api/books/${book.id}","status": 404}
      ]
    },
    {
      "id": "reading-update",
      "requests": [
        {
          "actor": "reader",
          "method": "PUT",
          "path": "/api/books/${book.id}",
          "status": 200,
          "fixture": "book",
          "json": {"status": "finished","note": "Completed and reviewed"},
          "save": "updated_book",
          "assertions": [{"path": ["status"],"equals": "finished"},{"path": ["note"],"equals": "Completed and reviewed"}]
        }
      ]
    },
    {
      "id": "reading-delete",
      "requests": [
        {"actor": "reader","method": "DELETE","path": "/api/books/${control.id}","status": 204},
        {"actor": "reader","method": "GET","path": "/api/books/${control.id}","status": 404}
      ]
    },
    {
      "id": "reading-restart",
      "requests": [
        {
          "actor": "reader",
          "method": "GET",
          "path": "/api/books/${book.id}",
          "status": 200,
          "assertions": [{"path": [],"equals": "${updated_book}"}]
        },
        {"actor": "other_reader","method": "GET","path": "/api/books","status": 200,"assertions": [{"path": [],"count": 0}]}
      ],
      "restart": true
    }
  ],
  "browser": [
    {
      "actor": "reader",
      "entity": "books",
      "rows": [{"id": "${book.id}","values": {"title": "Practical Graph Learning","status": "finished","note": "Completed and reviewed"}}],
      "absent": ["${control.id}"]
    },
    {"actor": "other_reader","entity": "books","rows": [],"absent": ["${book.id}"]}
  ]
}
````
