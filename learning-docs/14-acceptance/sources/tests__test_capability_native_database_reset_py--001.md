# tests/test_capability_native_database_reset.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.capability_verification`、`workbench.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `identity`（L14–L21）：接收`oid`。 调用`dict`。 返回路径：L15的`dict( database="rnd_product", database_oid=oid, cluster="987654321", directory=stack.PG_RO…`。
- `plan`（L24–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`、`Selection`。 返回路径：L25的`SimpleNamespace( selection=Selection(template="fastapiadmin"), runtime=SimpleNamespace(por…`。
- `test_reset_drains_before_identity_check_and_fixed_owned_ddl`（L30–L56）：接收`monkeypatch`。 控制顺序：L51断言`events[:2] == ["drain", "identity"]`；L52断言`len([row for row in events if isinstance(row, list)]) == 3`；L53断言`result["database_oid"] == 101`；L54断言`all(stack.PG_SOCKET in row for row in events if isinstance(row, list))`；L55断言`"dropdb" in " ".join(events[2]) and events[2][-1] == "rnd_product"`；L56断言`"--force" not in events[2]`。 调用`iter`、`identity`、`monkeypatch.setattr`、`events.append`、`stack.recreate_owned_native_database`、`SimpleNamespace`、`plan`、`len`、`isinstance`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reset_drains_before_identity_check_and_fixed_owned_ddl.owned`（L37–L39）：接收`*args`。 调用`events.append`、`next`。 返回路径：L39的`next(replies)`。
- `test_reset_drains_before_identity_check_and_fixed_owned_ddl.execute`（L43–L45）：接收`sandbox`、`argv`、`timeout`。 调用`events.append`、`SimpleNamespace`。 返回路径：L45的`SimpleNamespace(exit_code=0)`。
- `test_identity_drift_prevents_any_drop`（L63–L72）：接收`monkeypatch`、`field`、`value`。 调用`monkeypatch.setattr`、`identity`、`pytest.fail`、`pytest.raises`、`stack.recreate_owned_native_database`、`SimpleNamespace`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_thread_blocks_before_identity_or_ddl`（L75–L84）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`stack.recreate_owned_native_database`、`SimpleNamespace`、`plan`、`identity`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_thread_blocks_before_identity_or_ddl.fail`（L76–L77）：接收`*args`、`**kwargs`。 控制顺序：L77抛异常，停止当前正常路径。 调用`CheckFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_identity_reads_only_fixed_private_database`（L87–L100）：接收`monkeypatch`。 控制顺序：L97断言`stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30) == identity()`；L99断言`stack.PG_SOCKET in command and "rnd_product" in command`；L100断言`"pg_catalog.pg_control_system()" in command[-1]`。 调用`identity`、`body.pop`、`monkeypatch.setattr`、`stack.owned_database_identity`、`SimpleNamespace`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_identity_reads_only_fixed_private_database.execute`（L92–L94）：接收`sandbox`、`argv`、`timeout`。 调用`seen.append`、`SimpleNamespace`、`json.dumps`。 返回路径：L94的`SimpleNamespace(exit_code=0, result=json.dumps(body))`。

</details>

**创建路径：** `tests/test_capability_native_database_reset.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L100。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3547`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_database_reset.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "889da4b47f3a8ffb7e8c7213d94b00475e833195bd887ce15dc9dc816c3ffde8"} -->
````python
# tests/test_capability_native_database_reset.py
"""Controller resets only its attested ephemeral cluster; never user databases."""

import json
from types import SimpleNamespace

import pytest

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
    [("cluster", "other"), ("sandbox_id", "other"), ("database", "userdb"), ("database_oid", 999)],
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
    assert stack.PG_SOCKET in command and "rnd_product" in command
    assert "pg_catalog.pg_control_system()" in command[-1]
````
