# templates/standards/fastapiadmin.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/standards/fastapiadmin.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L21。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2360`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/standards/fastapiadmin.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "73f61f7cd9cfa7a5805a71404874a7055f6a9c0eee5bb63206b62d50c47e9835"} -->
````markdown
<!-- templates/standards/fastapiadmin.md -->
# fastapiadmin：原生 Python 后端 + Vue / Element Plus

## 原生后端扩展

- 保留锁定 FastapiAdmin 源码与原生代码生成器，使用已有 Python/uv 和 PostgreSQL/Redis 环境。业务代码放 `backend/app/plugin/`；批准的业务测试放 `backend/tests/`。
- 沿用原生 controller/service/schema/model 分层、依赖注入、认证和权限注册；模型和路由命名对齐批准实体，不以外置小 FastAPI 服务代替原框架。
- API 延用 `/api/v1` 和原生 `ApiResponse`，通过实际 OpenAPI/生成源码核对字段和包络。业务数据保持原生存储和迁移约定，不加第二个 SQLite 数据库。
- 团队流程复用 `module_business` 的声明式资源、关联、角色、状态和审计契约。数据 shared 的含义是由业务权限决定范围；每个 API 仍执行行权限。
- 普通规则定制只编辑 Plop 注册文件的 `RND_RULE_BEGIN/END` 表达式区；Python 与 Vue 实现同一已批准条件。不能修改认证、SQL、依赖、路由挂载或正反例。

## 原生 Vue 页面

- 页面沿用 `frontend/web/src/views/module_rnd/{entity}/index.vue`；获批的复用组件与请求模块分别放 `src/components/`、`src/api/`。
- 列表、查询、编辑使用 `FaSearchBar`、`FaTable`、`FaDialog`、`FaForm`。有声明式业务时保留 `ElCard`、`ElTimeline`、`ElTimelineItem`、`ElStatistic` 的真实业务数据接入。
- 请求复用 `@utils` 的 `request`，遵守已有拦截器、错误反馈、分页与 `ApiResponse` 处理，不自行另写令牌存储或绕过权限控制。
- 保留 `src/layouts/`、`src/styles/`、`src/main.ts` 字节身份，不全局换肤或绕开菜单、登录和授权；页面内部用原有间距、组件与响应式布局完成清晰交互。
- API 字段保持原生 Python 的 snake_case；前端按真实接口绑定，不擅自转 camelCase。状态、枚举和动作显示中文标签，存储标识保持稳定。

## 修改后的检查

执行现有原生构建/类型检查及浏览器流程，检查菜单可达、表单校验、请求失败、空态、权限按钮和刷新后数据。后端验证真实 API、数据库持久化、重启、正反规则以及角色/行权限。shell 哈希、Vue 组件解析与独立新库恢复都须保留；源码导出或构建成功不能冒充已通过运行验收。
````
