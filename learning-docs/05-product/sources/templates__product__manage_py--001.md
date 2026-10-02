# templates/product/manage.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 产品自己的迁移/启动及一次性bootstrap-admin入口：管理员密码在隐藏终端交互输入，初始化与事件同事务完成；普通注册不能抢占管理员，也不修改平台控制数据库。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `main`（L12–L29）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L18按`args.action == "bootstrap-admin"`分支；L21按`args.action in {"init", "start"}`分支；L26按`args.action in {"serve", "start"}`分支。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`bootstrap_admin`、`Config`、`str`、`config.set_main_option`、`command.upgrade`、`print`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bootstrap_admin`（L32–L87）：接收`username`。 控制顺序：L42按`not BUSINESS`分支；L43抛异常，停止当前正常路径；L47按`not username or len(username) > 100 or len(password) < 10 or len(password) > 200 or p…`分支；L54抛异常，停止当前正常路径；L86抛异常，停止当前正常路径。 调用`SystemExit`、`(username or input("管理员用户名: ")).strip`、`input`、`getpass.getpass`、`len`、`engine.begin`、`connection.execute`、`insert(metadata.tables["business_setup"]).values`、`insert`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `templates/product/manage.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L91。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3138`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/manage.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "401883b32df3fdeb08f2e03089b988404b19ad8a5dc50cd1400859189bc2ac09"} -->
````python
# templates/product/manage.py
"""Product lifecycle: uv run python manage.py init|serve. No platform required."""

import argparse
from pathlib import Path

from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "serve", "start", "bootstrap-admin"])
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--username")
    args = parser.parse_args()
    if args.action == "bootstrap-admin":
        bootstrap_admin(args.username)
        return
    if args.action in {"init", "start"}:
        config = Config(str(ROOT / "alembic.ini"))
        config.set_main_option("script_location", str(ROOT / "migrations"))
        command.upgrade(config, "head")
        print("数据库迁移完成")
    if args.action in {"serve", "start"}:
        import uvicorn

        uvicorn.run("app:app", host="127.0.0.1", port=args.port, app_dir=str(ROOT))


def bootstrap_admin(username=None):
    import getpass
    import json
    import uuid

    from app import password_hash
    from schema import BUSINESS, engine, metadata
    from sqlalchemy import insert
    from sqlalchemy.exc import IntegrityError

    if not BUSINESS:
        raise SystemExit("当前产品未启用业务角色")
    username = (username or input("管理员用户名: ")).strip()
    password = getpass.getpass("管理员密码（至少10字符）: ")
    confirmation = getpass.getpass("再次输入密码: ")
    if (
        not username
        or len(username) > 100
        or len(password) < 10
        or len(password) > 200
        or password != confirmation
    ):
        raise SystemExit("用户名或密码不符合要求，未创建账号")
    try:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["business_setup"]).values(key="bootstrap_admin")
            )
            identity = str(uuid.uuid4())
            connection.execute(
                insert(metadata.tables["users"]).values(
                    id=identity,
                    username=username,
                    password=password_hash(password),
                    role=BUSINESS["bootstrap_role"],
                )
            )
            from business_policy import utc

            connection.execute(
                insert(metadata.tables["business_audit"]).values(
                    id=str(uuid.uuid4()),
                    entity="$users",
                    record_id=identity,
                    actor_id=identity,
                    action="bootstrap_admin",
                    created_at=utc(),
                    before_json=None,
                    after_json=json.dumps(
                        {"username": username, "role": BUSINESS["bootstrap_role"]}
                    ),
                )
            )
    except IntegrityError:
        raise SystemExit("管理员已初始化或用户名已存在；原账号未修改") from None
    print("管理员已创建；密码未保存到配置或日志")


if __name__ == "__main__":
    main()
````
