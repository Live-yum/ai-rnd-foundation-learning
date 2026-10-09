# yudao-vben：芋道 Java + Vben5 / Ant Design Vue

## 原生 Java 扩展

- 保留锁定芋道后端与 Vben5 源码，沿用 Java 17、Maven、项目声明的 Node/pnpm 锁和 PostgreSQL/Redis。不能升级依赖来掩盖代码问题或切换到另一个前端模板。
- 获批业务代码位于 `backend/yudao-module-infra/` 下实际 `yudao-module-infra-server` / `yudao-module-infra-api` 子模块的 `src/main/java/`，业务测试在对应 `src/test/java/`。沿用 Controller、Service、Mapper、DO、ReqVO/RespVO 分层与 Bean Validation，复用原生认证、事务和权限注解。
- API 延用 `/admin-api` 与 `code=0, data, msg` 包络；Java/JSON 使用原生 camelCase，批准契约中的 snake_case 经平台映射转换。不能因前端显示而改数据库/契约机器标识。
- 团队业务使用已有 `RndBusiness` 契约和原生表，不复制客户服务等具体案例的业务引擎。所有查询、状态操作、指标与审计仍遵守已批准角色和行权限。
- 普通规则仅编辑 Plop 注册 Java/Vue 文件中 `RND_RULE_BEGIN/END` 的纯表达式区；先处理可空字段，与 Vue 的允许/拒绝含义一致。不得引入反射、进程、网络、对象构造或修改其余源码。

## Vben5 Ant Design 页面

- 产品前端根为 `frontend-product/`，应用为 `apps/web-antd/`；业务页面使用 `src/views/infra/wb{去掉下划线的实体名}/`，接口模块使用 `src/api/`。
- 列表使用 `Page`、`Grid`、`TableAction` 与 `#/adapter/vxe-table`；编辑使用 `Modal`、`Form`、`useVbenModal` 和 `#/adapter/form`。保留 `@vben/common-ui`、Ant Design Vue 的组件体系。
- 所有请求复用 `#/api/request` 的 `requestClient`，遵守统一鉴权、错误与包络处理；禁止页面直连数据库或复制第二套 HTTP/认证客户端。
- 声明式业务面板复用 `RndBusinessPanel`、原生 Card/Table/Timeline/Statistic、ActionModal/ActionForm；有统计图时使用既有 `@vben/plugins/echarts` 与 `EchartsUI`，并显示真实统计 API 数据。
- 不修改应用 layouts、main.ts、bootstrap.ts 及公共布局、设计、样式包；使用组件参数和页面局部布局改善清晰度，保持原生导航、权限、主题和键盘交互。

## 修改后的检查

执行现有 Maven 构建、Vue 类型检查/生产构建和原生浏览器验证；检查列表查询、Modal 表单、行操作、动作错误与状态更新。真实 API 验证字段映射、规则、角色和行权限，并验证 PostgreSQL 重启持久化与独立新库交付。不能用静态 Vue 文件、编译通过、截图或源码生成回执代替这些证据。
