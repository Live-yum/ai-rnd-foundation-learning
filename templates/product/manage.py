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
