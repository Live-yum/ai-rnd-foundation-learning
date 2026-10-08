# examples/acceptance/reading-shelf/requirement.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可审查的需求与完整合同验收样例。** 自然语言说明目标，JSON计划逐项登记实体、字段、关系、角色、转换和指标。它用于确定性验收，不是生产模型失败后的隐藏答案；改需求需修改并重新批准相应合同。

**对应关系：** 按正文验证Plan → ci_native_bundled --spec → 真实原生工具验收；该文件随教材一并还原。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `examples/acceptance/reading-shelf/requirement.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L31。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2475`。本段原文以LF换行结束。

<!-- learning-source: {"path": "examples/acceptance/reading-shelf/requirement.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2e40aa805ee85166c9a145db91753610a684a693dc73b97fbdde125471596d75"} -->
````markdown
<!-- examples/acceptance/reading-shelf/requirement.md -->
# 小规模项目：个人阅读书架

我要一个可以注册、登录的个人阅读书架，用于管理待阅读、在读、已读书目。使用 python-basic、simple-admin 前端、SQLite 数据库。不同用户的数据必须隔离；每个用户都能新增、查看、修改和删除自己的书目。

界面中文，字段和枚举显示标签可用自然中文；下表中的英文实体名、字段名和枚举存储值是稳定的接口契约，请严格保留。只允许 books 这一个实体及表内字段，不添加实体、字段、业务角色、工作流或自定义规则。

## 字段清单

未特别标注的文本字段最大长度为 200；未声明的 searchable、filterable、date_range 均为 false。所有普通 required 字段必须提交；负责人、状态及状态时间遵守业务专用操作。系统 id、创建者、创建时间等由模板提供，不加入业务字段清单。

| 实体 | 字段 | 约束 |
| --- | --- | --- |
| books | title | text；必填；最大长度 200；关键词搜索 |
| books | author | text；必填；最大长度 200；关键词搜索 |
| books | category | enum；必填；枚举 technology, literature, science；精确筛选 |
| books | status | enum；必填；枚举 planned, reading, finished；精确筛选 |
| books | pages | integer；必填；最小值 1；最大值 10000 |
| books | started_on | date；必填；包含首尾的日期范围 |
| books | note | text；可空；最大长度 3000 |

## 可执行验收

- 新建书目，按 title/author 关键词与 category/status 精确筛选组合查询；started_on 起止日期均包含边界。其他未声明的字段不增加查询条件。
- pages 必须是 1 到 10000 的整数，拒绝 0 与负数；无效输入不落库。
- 第二个账号不能读取、搜索、修改或删除第一个账号的书目。
- 修改阅读状态与备注后刷新仍在，删除后不能再获取。服务重启后保留未删除书目和登录后的数据隔离。
- 生成的真实浏览器页面必须支持上述表单、列表、搜索、筛选和删除操作；交付 ZIP 在独立目录安装并启动，通过 HTTP、浏览器和重启验收。

## 生成方式

通过当前平台正常的需求分析、设计、生成、独立验收和交付关卡（模型审阅为可选项）执行。未明确的展示细节可采用合理默认并记录；不得删改上述业务义务、增加不必要的功能或编造测试通过。
````
