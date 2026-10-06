# templates/product/README.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 交付包内的独立启动和使用说明模板；生成器还会写入规格、选择和SQL，使用户离开研发平台后仍知道运行哪个入口。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/product/README.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L63。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4903`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/README.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7e81ee369543003fb94e96c694b8c8a000b94679675c121accda67b1b68a3337"} -->
````markdown
<!-- templates/product/README.md -->
# 独立交付产品

后端、前端和数据库选择记录在 `selection.json`；字段、搜索、筛选及验收范围在 `approved-spec.json`。
源码不需要研发平台在线，不需要模型 API Key。

若包内包含 `RND-CONSUMER.json`，这是自定义 Python 模块产品，适用下面的“自定义模块启动契约”；不要对它运行基础模板的 `manage.py init` 或 `verify.py`。

## 一条启动命令

安装 Python 3.14 与 uv，解压后在本目录执行：

```powershell
uv run python start.py
```

程序安装锁定依赖、执行 Alembic 迁移再启动后端。SQLite 不需要任何数据库服务。
PostgreSQL 选择需要 Docker Desktop；没有设置 PRODUCT_DATABASE_URL 时，启动器自动创建本产品独立 PostgreSQL 容器/持久卷和随机密码。
再次启动复用 `.data/deployment.json`，不会重建或清空已有数据。也可显式设置 PRODUCT_DATABASE_URL 使用自己的本机数据库。

默认打开 `http://127.0.0.1:8001/`。选择 simple-admin 时为真实管理页面，支持注册登录、表单、搜索筛选与增删改查；选择 api-only 时使用 `/docs`。
平台令牌不是产品用户令牌。客服产品及其他带 `approved-spec.json.business` 的产品需先初始化业务管理员；迁移完成后，在本目录另开终端执行：

```powershell
uv run python manage.py bootstrap-admin --username manager
```

按隐藏终端提示输入两次密码（至少10字符），不要将密码写进命令或配置。该入口只能成功初始化一次，不会重置已有管理员。随后使用该账号登录，在业务权限界面创建或调整客服、普通员工等产品角色；普通注册只能得到合同中的默认非管理员角色。没有业务合同的普通实体产品直接注册账号即可。

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
客服产品的客户、请求和任务通过真实外键关联，按已批准业务合同中的角色及 all/own/assigned 行范围授权。创建人、状态、负责人和解决时间不能通过普通编辑伪造；分配和命名状态转换使用专用操作。历史记录、站内提醒与统计同样受权限控制，归档保留审计。无业务合同的 per_user 产品继续逐用户隔离；两种模式都不能通过筛选参数伪造 owner_id。

只监听本机。公开部署前另行配置HTTPS、注册管控、限流、权限审计和备份。
备份SQLite先停止服务；PostgreSQL备份需独立保管凭据和数据。不要删除 `.data` 来处理升级问题。

## 自定义模块启动契约

包含 `RND-CONSUMER.json` 的 Python/SQLite 产品同样运行 `uv run --no-project --python 3.14 python start.py`。
启动器安装原锁定依赖，使用契约中的 ASGI 入口和端口；默认只监听 `127.0.0.1`，健康检查及页面以该产品的验收合同为准。
`--no-install` 仅用于已具备相同锁定依赖的解释器，不证明首次联网安装成功。

数据库默认保存到契约中的产品相对路径，通常为 `data/application.db`。可用 `PRODUCT_DATABASE_URL` 显式指定本机 SQLite 文件。
启动器将 `PRODUCT_DATABASE_URL` 和兼容别名 `DATABASE_URL` 设置为同一绝对文件地址；不会采用终端里可能属于其他项目的 `DATABASE_URL`。
隔离验收使用相同启动器、入口、环境变量约定与数据库相对路径；为隔离代理显式监听 `0.0.0.0`，解压后的默认地址仍限本机。

自定义应用在自身启动时初始化数据库，不执行基础模板的 Alembic 建表，避免把两种业务结构写入同一数据库。
冷启动和保留记录的重复启动只证明当前结构的初始化与重启，不证明旧版本结构升级。
当前契约明确标记 `existing_schema_migration: unverified`，因此不支持 `--init-only`，也不能用于宣称已有旧结构数据库可安全升级。
升级既有数据需要另外提供并验证版本化迁移；不要删除数据库或绕过错误继续运行。
此契约仅适用 Python/SQLite，不能作为 FastapiAdmin 或其他原生产品的独立启动、升级证据。
````
