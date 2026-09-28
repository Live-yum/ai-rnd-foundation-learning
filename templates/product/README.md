# 已批准的 CRUD 后端

本产品与研发平台独立运行，默认数据库是当前目录 `.data/product.db`。
需要 Python 3.14 和 uv，不需要大模型 API Key，也不需要平台在线。

```powershell
uv sync --locked
uv run python manage.py init
uv run python verify.py
uv run python manage.py serve --port 8001
```

打开 `http://127.0.0.1:8001/docs`，先调用 `/auth/register` 注册，密码至少 10 字符。
将返回的 `access_token` 填入 Authorize，再操作 `/api/{entity}`。
实体名与字段见 `approved-spec.json`，只允许 text/integer/boolean。
所有记录按用户隔离。不包含审批引擎、跨实体事务、任意代码插件或公网部署加固。
`custom_rules.py` 是受限 Python 规则文件，由可信解释器解析，**不直接 import/exec**。
不要删除数据文件；表结构升级应新增 Alembic revision，先备份并演练恢复。
