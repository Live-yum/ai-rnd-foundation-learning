# workbench/capability_consumer.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_verification`、`workbench.domain`、`workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `expected_consumer`（L20–L52）：接收`plan`。 控制顺序：L23按`plan.selection.template != "python-basic" or plan.selection.database != "sqlite"`分支；L24抛异常，停止当前正常路径；L28按`str(database) != plan.runtime.database_path or database.is_absolute() or database.par…`分支；L41抛异常，停止当前正常路径。 调用`CheckFailure`、`readonly_prepare_commands`、`readonly_start_command`、`PurePosixPath`、`str`、`database.is_absolute`、`database.parent.as_posix`、`any`、`part.startswith`等。 返回路径：L42的`{ "schema": 1, "profile": "python-basic-sqlite-asgi-v1", "entrypoint": command.argv[3], "p…`。
- `_require_launcher`（L55–L58）：接收`product`。 控制顺序：L57按`not launcher.is_file() or sha(launcher) != sha(ROOT / "templates/product/start.py")`分支；L58抛异常，停止当前正常路径。 调用`inside`、`launcher.is_file`、`sha`、`CheckFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `prepare_consumer`（L61–L69）：接收`product`、`plan`。 源码说明：Called by the controller before the baseline's immutable source inventory.。 控制顺序：L66按`target.exists()`分支。 调用`expected_consumer`、`_require_launcher`、`inside`、`target.exists`、`inspect_consumer`、`write_json`。 返回路径：L67的`inspect_consumer(product, plan, required=True)`；L69的`inspect_consumer(product, plan, required=True)`。
- `inspect_consumer`（L72–L100）：接收`product`、`plan`、`required`。 源码说明：Fail closed on any present, stale, malformed or mismatched contract. An absent contract can identify older isolated forensic fixtures, never a successful downloaded-ZIP consumer proof. Delivery must r。 控制顺序：L79按`not target.exists()`分支；L80按`required`分支；L81抛异常，停止当前正常路径；L86按`not target.is_file() or target.stat().st_size > 4096`分支；L87抛异常，停止当前正常路径；L89按`type(value) is not dict or digest(value) != digest(expected)`分支；L90抛异常，停止当前正常路径；L92按`selection != plan.selection.model_dump()`分支。后续分支沿下方源码相同行号继续阅读。 调用`inside`、`target.exists`、`CheckFailure`、`expected_consumer`、`_require_launcher`、`target.is_file`、`target.stat`、`json.loads`、`target.read_text`等。 返回路径：L82的`None`；L100的`value`。
- `consumer_start_command`（L103–L119）：接收`plan`。 源码说明：Use only after inspect_consumer; existing product_argv isolation still applies.。 调用`expected_consumer`、`readonly_start_command`、`TaskCommand`、`str`。 返回路径：L109的`TaskCommand( argv=[ python, "start.py", "--no-install", "--host", "0.0.0.0", "--port", str…`。
- `require_consumer_evidence`（L122–L157）：接收`product`、`plan`、`proof`。 源码说明：Require source-bound consumer observations after normal require_evidence. This is an additional delivery gate, not a replacement for the independent sandbox, database, browser, scenario and cleanup ev。 控制顺序：L131按`type(proof) is not dict or proof.get("passed") is not True or proof.get("scope") != "…`分支；L156抛异常，停止当前正常路径。 调用`inspect_consumer`、`type`、`proof.get`、`digest`、`manifest`、`plan.model_dump`、`set`、`value.get`、`CheckFailure`。 返回路径：L157的`value`。

</details>

**创建路径：** `workbench/capability_consumer.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L157。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6413`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_consumer.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c6203c989993facccdf1c5cd82f4de9fdd1164982982f698f323cc16bf880788"} -->
````python
# workbench/capability_consumer.py
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
````
