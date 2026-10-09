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
