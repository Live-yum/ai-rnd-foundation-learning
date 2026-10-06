"""Controller-owned downloaded-Python startup contract; source inspection only.

These functions never import or execute candidate code. The same trusted
launcher is used inside existing isolation and after the consumer unzips it.
Application bootstrap and restart do not prove an old-schema migration.
"""

import json
from pathlib import PurePosixPath

from workbench.capability_contracts import TaskCommand
from workbench.capability_verification import CheckFailure
from workbench.domain import digest
from workbench.filesystem import inside, manifest, sha, write_json
from workbench.settings import ROOT

CONSUMER_FILE = "RND-CONSUMER.json"


def expected_consumer(plan):
    from workbench.capability_dependencies import readonly_prepare_commands, readonly_start_command

    if plan.selection.template != "python-basic" or plan.selection.database != "sqlite":
        raise CheckFailure("该技术栈尚无已验证的模块ZIP独立启动契约")
    readonly_prepare_commands(plan)
    command = readonly_start_command(plan)
    database = PurePosixPath(plan.runtime.database_path)
    if (
        str(database) != plan.runtime.database_path
        or database.is_absolute()
        or database.parent.as_posix() == "."
        or any(part.startswith(".") or part == "node_modules" for part in database.parts)
        or "\\" in plan.runtime.database_path
        or ":" in plan.runtime.database_path
        or "?" in plan.runtime.database_path
        or "#" in plan.runtime.database_path
        or any(ord(char) < 32 for char in plan.runtime.database_path)
        or database.suffix.lower() not in {".db", ".sqlite", ".sqlite3"}
        or plan.runtime.port in {2280, 55432, 55433}
    ):
        raise CheckFailure("模块ZIP数据库必须使用独立普通子目录中的SQLite文件")
    return {
        "schema": 1,
        "profile": "python-basic-sqlite-asgi-v1",
        "entrypoint": command.argv[3],
        "port": plan.runtime.port,
        "database_path": plan.runtime.database_path,
        "runtime_sha256": digest(plan.runtime.model_dump()),
        "database_environment": ["PRODUCT_DATABASE_URL", "DATABASE_URL"],
        "initialization": "application-startup",
        "existing_schema_migration": "unverified",
    }


def _require_launcher(product):
    launcher = inside(product, "start.py")
    if not launcher.is_file() or sha(launcher) != sha(ROOT / "templates/product/start.py"):
        raise CheckFailure("模块ZIP必须保留当前受信任start.py，不能替换或沿用旧启动器")


def prepare_consumer(product, plan):
    """Called by the controller before the baseline's immutable source inventory."""
    expected = expected_consumer(plan)
    _require_launcher(product)
    target = inside(product, CONSUMER_FILE)
    if target.exists():
        return inspect_consumer(product, plan, required=True)
    write_json(target, expected)
    return inspect_consumer(product, plan, required=True)


def inspect_consumer(product, plan, *, required=False):
    """Fail closed on any present, stale, malformed or mismatched contract.

    An absent contract can identify older isolated forensic fixtures, never a
    successful downloaded-ZIP consumer proof. Delivery must require this result.
    """
    target = inside(product, CONSUMER_FILE)
    if not target.exists():
        if required:
            raise CheckFailure("模块ZIP缺少独立启动契约，不能声称消费者可启动")
        return None
    expected = expected_consumer(plan)
    _require_launcher(product)
    try:
        if not target.is_file() or target.stat().st_size > 4096:
            raise ValueError
        value = json.loads(target.read_text(encoding="utf-8"))
        if type(value) is not dict or digest(value) != digest(expected):
            raise ValueError
        selection = json.loads(inside(product, "selection.json").read_text(encoding="utf-8"))
        if selection != plan.selection.model_dump():
            raise ValueError
    except OSError, ValueError:
        raise CheckFailure("模块ZIP独立启动契约与批准runtime或技术栈不一致") from None
    from workbench.capability_dependencies import _source_contract

    # The declared SQLite directory cannot hide importable application source.
    _source_contract(plan, manifest(product))
    return value


def consumer_start_command(plan):
    """Use only after inspect_consumer; existing product_argv isolation still applies."""
    from workbench.capability_dependencies import readonly_start_command

    expected_consumer(plan)
    python = readonly_start_command(plan).argv[0]
    return TaskCommand(
        argv=[
            python,
            "start.py",
            "--no-install",
            "--host",
            "0.0.0.0",
            "--port",
            str(plan.runtime.port),
        ]
    )


def require_consumer_evidence(product, plan, proof):
    """Require source-bound consumer observations after normal require_evidence.

    This is an additional delivery gate, not a replacement for the independent
    sandbox, database, browser, scenario and cleanup evidence requirements.
    No successful bootstrap/restart can upgrade the migration claim.
    """
    expected = inspect_consumer(product, plan, required=True)
    value = proof.get("consumer") if type(proof) is dict else None
    if (
        type(proof) is not dict
        or proof.get("passed") is not True
        or proof.get("scope") != "aggregate"
        or proof.get("restarted") is not True
        or proof.get("source_digest") != digest(manifest(product))
        or proof.get("plan_digest") != digest(plan.model_dump())
        or type(value) is not dict
        or set(value)
        != {
            "contract",
            "contract_sha256",
            "entrypoint",
            "cold_start",
            "restart",
            "existing_schema_migration",
        }
        or type(value.get("contract")) is not dict
        or digest(value["contract"]) != digest(expected)
        or value.get("contract_sha256") != digest(expected)
        or value.get("entrypoint") != "start.py"
        or value.get("cold_start") is not True
        or value.get("restart") is not True
        or value.get("existing_schema_migration") != "unverified"
    ):
        raise CheckFailure("模块ZIP缺少与本次源码和计划绑定的start.py冷启动及保留数据重启证据")
    return value
