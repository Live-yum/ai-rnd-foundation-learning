"""Product lifecycle: uv run python manage.py init|serve. No platform required."""

import argparse
from pathlib import Path

from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "serve"])
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    if args.action == "init":
        config = Config(str(ROOT / "alembic.ini"))
        config.set_main_option("script_location", str(ROOT / "migrations"))
        command.upgrade(config, "head")
        print("数据库迁移完成")
    else:
        import uvicorn

        uvicorn.run("app:app", host="127.0.0.1", port=args.port, app_dir=str(ROOT))


if __name__ == "__main__":
    main()
