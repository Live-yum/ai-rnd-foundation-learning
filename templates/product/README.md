# 独立交付产品

后端、前端和数据库选择记录在 `selection.json`；字段、搜索、筛选及验收范围在 `approved-spec.json`。
源码不需要研发平台在线，不需要模型 API Key。

## 一条启动命令

安装 Python 3.14 与 uv，解压后在本目录执行：

```powershell
uv run python start.py
```

程序安装锁定依赖、执行 Alembic 迁移再启动后端。SQLite 不需要任何数据库服务。
PostgreSQL 选择需要 Docker Desktop；没有设置 PRODUCT_DATABASE_URL 时，启动器自动创建本产品独立 PostgreSQL 容器/持久卷和随机密码。
再次启动复用 `.data/deployment.json`，不会重建或清空已有数据。也可显式设置 PRODUCT_DATABASE_URL 使用自己的本机数据库。

默认打开 `http://127.0.0.1:8001/`。选择 simple-admin 时为真实管理页面，支持注册登录、表单、搜索筛选与增删改查；选择 api-only 时使用 `/docs`。
先注册账号（密码至少10字符）。平台令牌不是产品用户令牌。

## 数据库操作

实际升级代码在 `migrations/versions/0001_initial.py`，启动器自动执行 `alembic upgrade head`。
`database/schema.sqlite.sql` 和 `database/schema.postgresql.sql` 是对应的可审查建表语句，供理解或空库部署规划；不要先手工建表再让 Alembic 重复执行。

```powershell
uv run python start.py --init-only
uv run python manage.py init
uv run python verify.py
```

PostgreSQL 独立验证需要设置 VERIFY_DATABASE_URL 指向一个临时空测试库，不得用于生产数据。
完整控制台验收会为 PostgreSQL 自动建立临时验收库，验证后只删除它自己创建的UUID库。

日期要求真实 YYYY-MM-DD，日期区间包含起止；枚举只接受配置选项；过滤、搜索和排序必须与批准的字段能力一致。
所有业务查询始终保留当前用户隔离，不允许通过筛选参数伪造 owner_id。

只监听本机。公开部署前另行配置HTTPS、注册管控、限流、权限审计和备份。
备份SQLite先停止服务；PostgreSQL备份需独立保管凭据和数据。不要删除 `.data` 来处理升级问题。
