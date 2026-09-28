# 本地 AI 研发平台 · Python 3.14

Python + uv + FastAPI + SQLite + LangGraph。三项模型配置即可体验默认后端流程：真实需求澄清 → 需求审批 → 设计审批 → 确定性 CRUD 生成 → 可选受限规则编码 → 独立 HTTP 验收 → 干净解压复验 → 交付审批。

```powershell
uv python install 3.14
uv sync --locked
uv run rnd init
```

编辑根目录 `.env`：

```dotenv
BASE_URL=https://你的兼容服务/v1
API_KEY=你的密钥
MODE=模型名称
```

```powershell
uv run rnd start
```

另开同目录终端：

```powershell
uv run rnd chat
```

按提示逐步回答，在需求、设计、交付关卡分别输入“批准”或“拒绝”。恢复用 `uv run rnd chat --run UUID`；下载用 `uv run rnd download UUID`。Swagger：`http://127.0.0.1:8000/docs`；访问令牌：`uv run rnd token`。

默认产品无需外部数据库，支持逐用户 text/integer/boolean CRUD 和受限单记录规则。不支持任意软件、关系/共享/RBAC/支付/跨表事务。生成器不调用模型；规则不通过exec执行。

FastapiAdmin、芋道 + Vben 原生接口导出已经提供适配器、固定源码和契约测试，但需额外原生服务/令牌/专用开发数据库。输出明确为 **SOURCE_READY（源码导出）**，不是完整原生运行验收成功。查看 `uv run rnd templates`。

完整创建顺序、文件内容、测试、迁移、恢复和故障排查见根目录 **从零实现AI研发平台_逐步实操手册_完整版_v3.md**。手册从实际源码生成：

```powershell
uv run python -m scripts.build_handbook
uv run python -m scripts.build_handbook --check
uv run pytest -m "not postgres" -q
uv run python -m scripts.ci_clean_install
```

最后一项为显式模型夹具 + 真实独立产品依赖/SQLite/HTTP/干净解压验收，不消耗模型费。真实模型验收请使用你本机的三项配置；CI不声称已验证用户账户。

本机单操作人、单Worker，不绑定公网。不要分享 `.env`、`.data` 或本机访问令牌。
