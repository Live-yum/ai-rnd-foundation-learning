# templates/standards/python-basic.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/standards/python-basic.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L20。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2387`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/standards/python-basic.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8d3c36e5c72983d0d4156c056cea0a5dde57e310a83ed47fbfc6b7f2476b4968"} -->
````markdown
<!-- templates/standards/python-basic.md -->
# python-basic：FastAPI + 轻量管理页面

## 模板边界和后端

- 使用已有 FastAPI、SQLAlchemy、Alembic 与 uv 锁定环境；数据库从已批准的 SQLite/PostgreSQL 选型中确定，不能在开发中替换。
- CRUD、认证、用户隔离、字段类型、搜索和筛选交给模板。普通 `per_user` 项目保留 owner 约束；团队项目使用 `Plan.business` 的资源、角色及 own/assigned/all 权限，不把共享误解为所有人可访问。
- `app.py` 负责 API，`fields.py` / `querying.py` / `schema.py` 承担通用字段、查询与存储；声明式业务复用 `business_schema.py` / `business_runtime.py`。不要为特定项目另复制一套路由或业务运行时。
- 额外的单记录规则只进入 `custom_rules.py` 的 `validate(entity, data)`。规则编码任务只能修改该文件，使用平台解释器允许的条件、比较、`data.get`、`len` 与固定 `ValueError`；禁止导入、赋值、循环、文件、网络和任意执行。每条规则保留已批准正反例。
- 团队业务事务由已有业务契约实现；不能用单记录规则模拟跨记录流程。显式批准的源码模块另走精确文件计划与隔离执行，不扩大普通规则编码器权限。

## simple-admin 与 api-only

- 选择 `simple-admin` 时仅复用 `web/index.html`、`web/app.js`、`web/style.css` 的语义 HTML/CSS/JavaScript 结构，不为轻量页面新增 Vue/React 工具链。
- 用同源 `/api` 请求和统一 Bearer 处理；DOM 中显示用户内容使用安全文本方式。列表使用表格，表单有 label、字段级错误和提交状态，对话框支持关闭与焦点返回。
- 业务行为从已批准规格/API 推导。不要把任务、客户或竞赛等示例名固化到通用页面；展示标签与机器字段名分离。
- 选择 `api-only` 时不生成或依赖 Web 页面，也不能将跳过浏览器描述为前端验收通过；保留接口的认证、错误状态、查询与持久化验收。

## 修改后的检查

沿用交付 `README.md` 和锁文件中的启动/验证入口。规则变更检查允许与拒绝样例，数据变更检查必填、枚举、长度和所有权边界；页面变更检查真实 CRUD、空态、校验失败和错误恢复。保留独立 `verify.py`、`verify_business.py` 与浏览器验证文件，不在业务编码任务中改写它们。
````
