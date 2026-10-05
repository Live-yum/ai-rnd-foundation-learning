# tests/test_capability_native_database_reset.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.capability_verification`、`workbench.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `identity`（L16–L23）：接收`oid`。 调用`dict`。 返回路径：L17的`dict( database="rnd_product", database_oid=oid, cluster="987654321", directory=stack.PG_RO…`。
- `plan`（L26–L29）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`、`Selection`。 返回路径：L27的`SimpleNamespace( selection=Selection(template="fastapiadmin"), runtime=SimpleNamespace(por…`。
- `test_reset_drains_before_identity_check_and_fixed_owned_ddl`（L32–L58）：接收`monkeypatch`。 控制顺序：L53断言`events[:2] == ["drain", "identity"]`；L54断言`len([row for row in events if isinstance(row, list)]) == 3`；L55断言`result["database_oid"] == 101`；L56断言`all(stack.PG_SOCKET in row for row in events if isinstance(row, list))`；L57断言`"dropdb" in " ".join(events[2]) and events[2][-1] == "rnd_product"`；L58断言`"--force" not in events[2]`。 调用`iter`、`identity`、`monkeypatch.setattr`、`events.append`、`stack.recreate_owned_native_database`、`SimpleNamespace`、`plan`、`len`、`isinstance`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reset_drains_before_identity_check_and_fixed_owned_ddl.owned`（L39–L41）：接收`*args`。 调用`events.append`、`next`。 返回路径：L41的`next(replies)`。
- `test_reset_drains_before_identity_check_and_fixed_owned_ddl.execute`（L45–L47）：接收`sandbox`、`argv`、`timeout`。 调用`events.append`、`SimpleNamespace`。 返回路径：L47的`SimpleNamespace(exit_code=0)`。
- `test_identity_drift_prevents_any_drop`（L71–L80）：接收`monkeypatch`、`field`、`value`。 调用`monkeypatch.setattr`、`identity`、`pytest.fail`、`pytest.raises`、`stack.recreate_owned_native_database`、`SimpleNamespace`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_thread_blocks_before_identity_or_ddl`（L83–L92）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`stack.recreate_owned_native_database`、`SimpleNamespace`、`plan`、`identity`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_thread_blocks_before_identity_or_ddl.fail`（L84–L85）：接收`*args`、`**kwargs`。 控制顺序：L85抛异常，停止当前正常路径。 调用`CheckFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reset_rejects_cluster_sandbox_drift_or_unchanged_oid`（L99–L107）：接收`monkeypatch`、`field`、`value`。 调用`iter`、`identity`、`monkeypatch.setattr`、`next`、`SimpleNamespace`、`pytest.raises`、`stack.recreate_owned_native_database`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_identity_reads_only_fixed_private_database`（L110–L126）：接收`monkeypatch`。 控制顺序：L120断言`stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30) == identity()`；L122断言`command[:4] == ["/usr/sbin/runuser", "-u", "postgres", "--"]`；L123断言`"PGOPTIONS=-c search_path=pg_catalog" in command`；L124断言`stack.PG_SOCKET in command and "rnd_product" in command`；L125断言`"pg_catalog.pg_control_system()" in command[-1]`；L126断言`"SELECT oid::pg_catalog.int8 FROM pg_catalog.pg_database" in command[-1]`。 调用`identity`、`body.pop`、`monkeypatch.setattr`、`stack.owned_database_identity`、`SimpleNamespace`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_identity_reads_only_fixed_private_database.execute`（L115–L117）：接收`sandbox`、`argv`、`timeout`。 调用`seen.append`、`SimpleNamespace`、`json.dumps`。 返回路径：L117的`SimpleNamespace(exit_code=0, result=json.dumps(body))`。
- `test_identity_rejects_untrusted_fields_without_coercion`（L144–L152）：接收`monkeypatch`、`field`、`value`。 调用`identity`、`body.pop`、`monkeypatch.setattr`、`SimpleNamespace`、`json.dumps`、`pytest.raises`、`stack.owned_database_identity`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_identity_rejects_missing_malformed_or_oversize_reply`（L156–L159）：接收`monkeypatch`、`body`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`pytest.raises`、`stack.owned_database_identity`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_identity_rejects_failed_command_even_with_valid_json`（L162–L169）：接收`monkeypatch`。 调用`identity`、`body.pop`、`monkeypatch.setattr`、`SimpleNamespace`、`json.dumps`、`pytest.raises`、`stack.owned_database_identity`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_postgres_oid_json_requires_int8_cast`（L173–L192）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L175按`not url`分支；L186断言`type(value["original_oid"]) is str`；L187断言`type(value["numeric_oid"]) is int`；L188断言`value["numeric_oid"] == int(value["original_oid"]) > 0`；L189断言`type(value["maximum_oid"]) is int`；L190断言`value["maximum_oid"] == 2**32 - 1`。 调用`os.getenv`、`pytest.skip`、`create_engine`、`engine.connect`、`connection.exec_driver_sql( "SELECT pg_catalog.json_build_object(…`、`connection.exec_driver_sql`、`type`、`int`、`engine.dispose`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_database_reset.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L192。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7242`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_database_reset.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e73df324651715b65d058b3f45b3d5d4573f7e9e17c2b89fd01ff48f70212b2d"} -->
````python
# tests/test_capability_native_database_reset.py
"""Controller resets only its attested ephemeral cluster; never user databases."""

import json
import os
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine

from workbench import capability_sandbox
from workbench import capability_stack as stack
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection


def identity(oid=100):
    return dict(
        database="rnd_product",
        database_oid=oid,
        cluster="987654321",
        directory=stack.PG_ROOT + "/data",
        sandbox_id="owned-sandbox",
    )


def plan():
    return SimpleNamespace(
        selection=Selection(template="fastapiadmin"), runtime=SimpleNamespace(port=8000)
    )


def test_reset_drains_before_identity_check_and_fixed_owned_ddl(monkeypatch):
    events = []
    replies = iter([identity(), identity(101)])
    monkeypatch.setattr(
        capability_sandbox, "restart_application_identity", lambda *a, **kw: events.append("drain")
    )

    def owned(*args):
        events.append("identity")
        return next(replies)

    monkeypatch.setattr(stack, "owned_database_identity", owned)

    def execute(sandbox, argv, timeout):
        events.append(argv)
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(stack, "control_exec", execute)
    result = stack.recreate_owned_native_database(
        SimpleNamespace(id="owned-sandbox"), plan(), 30, identity()
    )
    assert events[:2] == ["drain", "identity"]
    assert len([row for row in events if isinstance(row, list)]) == 3
    assert result["database_oid"] == 101
    assert all(stack.PG_SOCKET in row for row in events if isinstance(row, list))
    assert "dropdb" in " ".join(events[2]) and events[2][-1] == "rnd_product"
    assert "--force" not in events[2]


@pytest.mark.parametrize(
    "field,value",
    [
        ("cluster", "other"),
        ("sandbox_id", "other"),
        ("database", "userdb"),
        ("directory", "/other/data"),
        ("database_oid", 999),
    ],
)
def test_identity_drift_prevents_any_drop(monkeypatch, field, value):
    monkeypatch.setattr(capability_sandbox, "restart_application_identity", lambda *a, **kw: None)
    monkeypatch.setattr(
        stack, "owned_database_identity", lambda *args: {**identity(), field: value}
    )
    monkeypatch.setattr(stack, "control_exec", lambda *args: pytest.fail("No destructive command"))
    with pytest.raises(CheckFailure, match="身份"):
        stack.recreate_owned_native_database(
            SimpleNamespace(id="owned-sandbox"), plan(), 30, identity()
        )


def test_live_thread_blocks_before_identity_or_ddl(monkeypatch):
    def fail(*args, **kwargs):
        raise CheckFailure("live thread")

    monkeypatch.setattr(capability_sandbox, "restart_application_identity", fail)
    monkeypatch.setattr(stack, "control_exec", lambda *args: pytest.fail("No command"))
    with pytest.raises(CheckFailure, match="live thread"):
        stack.recreate_owned_native_database(
            SimpleNamespace(id="owned-sandbox"), plan(), 30, identity()
        )


@pytest.mark.parametrize(
    "field,value",
    [("cluster", "other"), ("sandbox_id", "other"), ("database_oid", 100)],
)
def test_reset_rejects_cluster_sandbox_drift_or_unchanged_oid(monkeypatch, field, value):
    replies = iter([identity(), {**identity(101), field: value}])
    monkeypatch.setattr(capability_sandbox, "restart_application_identity", lambda *a, **kw: None)
    monkeypatch.setattr(stack, "owned_database_identity", lambda *a: next(replies))
    monkeypatch.setattr(stack, "control_exec", lambda *a: SimpleNamespace(exit_code=0))
    with pytest.raises(CheckFailure, match="新库身份"):
        stack.recreate_owned_native_database(
            SimpleNamespace(id="owned-sandbox"), plan(), 30, identity()
        )


def test_identity_reads_only_fixed_private_database(monkeypatch):
    seen = []
    body = identity()
    body.pop("sandbox_id")

    def execute(sandbox, argv, timeout):
        seen.append(argv)
        return SimpleNamespace(exit_code=0, result=json.dumps(body))

    monkeypatch.setattr(stack, "control_exec", execute)
    assert stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30) == identity()
    command = seen[0]
    assert command[:4] == ["/usr/sbin/runuser", "-u", "postgres", "--"]
    assert "PGOPTIONS=-c search_path=pg_catalog" in command
    assert stack.PG_SOCKET in command and "rnd_product" in command
    assert "pg_catalog.pg_control_system()" in command[-1]
    assert "SELECT oid::pg_catalog.int8 FROM pg_catalog.pg_database" in command[-1]


@pytest.mark.parametrize(
    "field,value",
    [
        ("database", "userdb"),
        ("directory", "/other/data"),
        ("database_oid", "100"),
        ("database_oid", True),
        ("database_oid", 100.0),
        ("database_oid", None),
        ("cluster", ""),
        ("cluster", "other"),
        ("cluster", "1" * 31),
        ("unexpected", True),
    ],
)
def test_identity_rejects_untrusted_fields_without_coercion(monkeypatch, field, value):
    body = identity()
    body.pop("sandbox_id")
    body[field] = value
    monkeypatch.setattr(
        stack, "control_exec", lambda *a: SimpleNamespace(exit_code=0, result=json.dumps(body))
    )
    with pytest.raises(CheckFailure, match="私有临时数据库身份"):
        stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30)


@pytest.mark.parametrize("body", ["", "not-json", "null", "[]", "{}", " " * 4097])
def test_identity_rejects_missing_malformed_or_oversize_reply(monkeypatch, body):
    monkeypatch.setattr(stack, "control_exec", lambda *a: SimpleNamespace(exit_code=0, result=body))
    with pytest.raises(CheckFailure, match="私有临时数据库身份"):
        stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30)


def test_identity_rejects_failed_command_even_with_valid_json(monkeypatch):
    body = identity()
    body.pop("sandbox_id")
    monkeypatch.setattr(
        stack, "control_exec", lambda *a: SimpleNamespace(exit_code=1, result=json.dumps(body))
    )
    with pytest.raises(CheckFailure, match="私有临时数据库身份"):
        stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30)


@pytest.mark.postgres
def test_postgres_oid_json_requires_int8_cast():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set; mandatory in postgres Actions job")
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            value = connection.exec_driver_sql(
                "SELECT pg_catalog.json_build_object("
                "'original_oid',oid,'numeric_oid',oid::pg_catalog.int8,"
                "'maximum_oid',4294967295::pg_catalog.oid::pg_catalog.int8) "
                "FROM pg_catalog.pg_database WHERE datname=current_database()"
            ).scalar_one()
        assert type(value["original_oid"]) is str
        assert type(value["numeric_oid"]) is int
        assert value["numeric_oid"] == int(value["original_oid"]) > 0
        assert type(value["maximum_oid"]) is int
        assert value["maximum_oid"] == 2**32 - 1
    finally:
        engine.dispose()
````
