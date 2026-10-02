# ui/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L73。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4772`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3202c1d1113dca89d8a8795d62947632754cb0df02d0797a30b7fc2f7e5bd0f4"} -->
````markdown
<!-- ui/README.md -->
# AI 研发平台：Vue 3 + Ant Design Vue 前端

此目录是工作台的可编辑源码。`workbench/web/` 是随 Python 服务分发的本地构建产物。页面使用真实 API；没有演示运行、假进度或运行时 CDN。

## 本地开发与构建

推荐 Node.js 22 LTS。第一次安装需要访问官方 npm registry；生产页面不需要外部网络下载前端库。

```bash
cd ui
npm ci
npm run test
npm run check
npm run build
```

构建固定输出 `../workbench/web/index.html`、`app.js`、`style.css`。FastAPI 将页面提供在 `/`、`/ui` 和 `/ui/`，本地资源在 `/ui/app.js`、`/ui/style.css`。前端使用 hash 路由，刷新任何子页面不需要额外的服务端路由规则。

开发时先从仓库根目录启动本地后端，再运行：

```bash
cd ui
npm run dev
```

Vite 默认将 API 请求代理到 `http://127.0.0.1:8000`。前端源码修改不会影响已构建页面，发布前必须重新运行 `npm run build`。

## 文件结构

- `src/App.vue`：响应式侧栏、移动底部导航、工作空间连接、hash 路由与未保存配置保护
- `src/api.ts`：统一带 Bearer 认证的请求、下载、增量 SSE 协议解析
- `src/state.ts`：真实项目、运行、消息与事件状态；连接恢复和会话失效保护
- `src/presentation.ts`：真实状态标签、阶段映射、公开消息归并与审核提交字段
- `src/components/HomeView.vue`：自然语言输入、模板/前端/数据库选择和明确的智能推荐授权
- `src/components/ProjectsView.vue`：项目列表、最近运行与交付中心
- `src/components/RunView.vue`：流式对话、人工审核、串行步骤、故障恢复、报告与交付
- `src/components/Questionnaire.vue`：来自后端合同的单选、多选、其他说明与自由文本回退
- `src/components/SettingsView.vue`：默认模型配置及四个阶段覆盖，API Key 只写与版本冲突处理
- `src/components/DataDocument.vue`：安全的结构化文档展示，文本经 Vue 转义，不渲染任意 HTML
- `src/style.css`：基于已批准桌面/移动设计的浅靛蓝、白色视觉体系

## API 与安全边界

访问令牌只留在当前页面内存；不会写入 localStorage、sessionStorage 或 URL。页面刷新后需要重新连接。锁定会清空项目和运行数据，并使晚到的请求响应失效，避免旧数据重新出现。

模型配置使用 `GET/PATCH /settings/models`。读取仅显示密钥是否已配置；只有明确替换或清除时才提交 `api_key`。更换非空服务地址要求新专用密钥。保存采用 `expected_revision`；409 后需读取最新配置并重新核对。当前仅有格式校验，页面不会做收费模型连接测试，也不会把格式有效写成连接成功。

项目创建先确认技术组合，之后提交真实运行。默认是人工确认；持续智能推荐需要显式授权。前端防止重复点击，并让未确定结果的重试复用相同 Idempotency-Key。

每个审核动作提交 `gate_id`、`version`、`digest` 和动作要求的明确布尔值。批准同时要求后端 `can_approve=true` 与操作者已阅读；409 不会自动重新批准。确认对话框绑定打开时的运行与关卡，导航离开时销毁，避免把旧确认应用到另一轮运行。

## 流式对话与进度

1. 读取 `/runs/{id}/transcript` 的持久消息与 `cursor`
2. 读取真实历史事件作为阶段证据
3. 使用 fetch 连接 `/runs/{id}/stream?after={cursor}`，在请求头传 Bearer 认证和 Last-Event-ID
4. 按持久事件 ID 去重，按 `message_id` 追加公开摘要 delta；完成事件替换为后端校验后的最终公开文本
5. 连接中断按游标恢复；切换运行或离开页面时取消订阅，后台 Worker 不受影响

生成中的文本标明“待校验”。未通过结构校验的文本不能当作已确认产物。进度只显示后端实际阶段事件，不显示虚构百分比、剩余时间或停止按钮。服务正常发送 idle 时不误报断线。

`READY` 表示运行级验收与交付确认完成；`SOURCE_READY` 只表示源码级交付，不代表已经完成运行环境验收。只有这两种完成状态能请求受保护的 ZIP 下载，后端仍会校验哈希。

## 验证

```bash
npm run test
npm run check
npm run format:check
npm run build
```

单元测试覆盖 SSE 分片/中文/表情/认证与游标、消息替换、版本和摘要、结构化问题必答/Other 切换/自由文本、幂等请求键和配置读取失败的降级。仓库的 `scripts/ci_guided_browser.py` 与 `scripts/guided_browser.cjs` 另用真实本地 FastAPI、明确的模型测试 fixture 和 Chromium 验证流式与审批到下载的完整链路，不使用真实付费模型。
````
