# tests/test_capability_native_planner_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.capability_verification`、`workbench.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `setup`（L14–L36）：接收`monkeypatch`、`count`、`read`、`fail_create`、`fail_cleanup`。 调用`monkeypatch.setattr`、`SimpleNamespace`。 返回路径：L36的`calls`。
- `setup.guarded`（L20–L27）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L22按`argv[0] == "app-only"`分支；L26断言`argv[0] == "reader-only"`。 调用`calls.append`。 返回路径：L25的`(1, "") if failed else (0, probe.COMPLETE)`；L27的`0, read`。
- `setup.counts`（L29–L32）：接收`sandbox`、`plan`、`timeout`。 控制顺序：L31断言`plan.runtime.database_tables == [NAME]`。 调用`calls.append`。 返回路径：L32的`{NAME: count}`。
- `execute`（L39–L41）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`、`Selection`、`probe.verify_native_planner_identity`。 返回路径：L41的`probe.verify_native_planner_identity(None, plan, {"DATABASE_PASSWORD": "synthetic"}, 30)`。
- `test_owned_probe_uses_app_ddl_and_separate_reader_then_cleans_up`（L44–L61）：接收`monkeypatch`。 控制顺序：L46断言`execute() == {probe.CHECK: True}`；L47断言`[call[0] for call in calls] == [ "app-only", "production-count", "reader-only", "app-…`；L53断言`"CREATE INDEX" in calls[0][-1]`；L54断言`"IMMUTABLE" in calls[0][-1]`；L55断言`"privileged planner evaluation" in calls[0][-1]`；L56断言`"SET ROLE postgres" in calls[2][-1]`；L57断言`"insufficient_privilege" in calls[2][-1]`；L58断言`"END;\n$probe$" in calls[0][-1]`。后续分支沿下方源码相同行号继续阅读。 调用`setup`、`execute`、`probe.statements`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_probe_never_emits_success_and_still_cleans_up`（L65–L69）：接收`monkeypatch`、`updates`。 控制顺序：L69断言`calls[-1][0] == "app-only" and "DROP TABLE" in calls[-1][-1]`。 调用`setup`、`pytest.raises`、`execute`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_cleanup_prevents_certificate`（L72–L75）：接收`monkeypatch`。 调用`setup`、`pytest.raises`、`execute`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_controller_generated_probe_identifiers_are_allowed`（L81–L83）：接收`name`。 调用`pytest.raises`、`probe.statements`、`pytest.mark.parametrize`、`NAME.upper`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_native_database_is_rejected_before_any_command`（L86–L89）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`probe.verify_native_planner_identity`、`SimpleNamespace`、`Selection`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_planner_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L89。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3431`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_planner_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "01b0c242bac297084b1e2280b9ff37f3b174cf061ae25843113f8e0513d8b9c1"} -->
````python
# tests/test_capability_native_planner_probe.py
"""Planner-probe protocol mocks; never a live PostgreSQL safety certificate."""

from types import SimpleNamespace

import pytest

from scripts import capability_native_planner_probe as probe
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection

NAME = "rnd_planner_" + "a" * 32


def setup(monkeypatch, *, count=1, read="restricted", fail_create=False, fail_cleanup=False):
    calls = []
    monkeypatch.setattr(probe.uuid, "uuid4", lambda: SimpleNamespace(hex="a" * 32))
    monkeypatch.setattr(probe, "product_argv", lambda plan, argv, env: ["app-only", *argv])
    monkeypatch.setattr(probe, "pg_verifier_argv", lambda sql: ["reader-only", sql])

    def guarded(sandbox, argv, timeout):
        calls.append(argv)
        if argv[0] == "app-only":
            cleanup = "DROP TABLE" in argv[-1]
            failed = fail_cleanup if cleanup else fail_create
            return (1, "") if failed else (0, probe.COMPLETE)
        assert argv[0] == "reader-only"
        return 0, read

    def counts(sandbox, plan, timeout):
        calls.append(["production-count", *plan.runtime.database_tables])
        assert plan.runtime.database_tables == [NAME]
        return {NAME: count}

    monkeypatch.setattr(probe, "run_guarded_control", guarded)
    monkeypatch.setattr(probe, "database_counts", counts)
    return calls


def execute():
    plan = SimpleNamespace(selection=Selection(template="fastapiadmin"))
    return probe.verify_native_planner_identity(None, plan, {"DATABASE_PASSWORD": "synthetic"}, 30)


def test_owned_probe_uses_app_ddl_and_separate_reader_then_cleans_up(monkeypatch):
    calls = setup(monkeypatch)
    assert execute() == {probe.CHECK: True}
    assert [call[0] for call in calls] == [
        "app-only",
        "production-count",
        "reader-only",
        "app-only",
    ]
    assert "CREATE INDEX" in calls[0][-1]
    assert "IMMUTABLE" in calls[0][-1]
    assert "privileged planner evaluation" in calls[0][-1]
    assert "SET ROLE postgres" in calls[2][-1]
    assert "insufficient_privilege" in calls[2][-1]
    assert "END;\n$probe$" in calls[0][-1]
    assert "session_user='rnd_verify'" in calls[2][-1]
    assert calls[-1][-1] == probe.statements(NAME)[2]
    assert "TO PROGRAM" not in calls[0][-1] and "pg_read_file" not in calls[0][-1]


@pytest.mark.parametrize("updates", [{"count": 0}, {"read": "postgres"}, {"fail_create": True}])
def test_failed_probe_never_emits_success_and_still_cleans_up(monkeypatch, updates):
    calls = setup(monkeypatch, **updates)
    with pytest.raises(CheckFailure):
        execute()
    assert calls[-1][0] == "app-only" and "DROP TABLE" in calls[-1][-1]


def test_failed_cleanup_prevents_certificate(monkeypatch):
    setup(monkeypatch, fail_cleanup=True)
    with pytest.raises(CheckFailure, match="清理"):
        execute()


@pytest.mark.parametrize(
    "name", ["user_table", "rnd_planner_" + "a" * 32 + ";DROP DATABASE x", NAME.upper()]
)
def test_only_controller_generated_probe_identifiers_are_allowed(name):
    with pytest.raises(CheckFailure):
        probe.statements(name)


def test_non_native_database_is_rejected_before_any_command(monkeypatch):
    monkeypatch.setattr(probe, "run_guarded_control", lambda *a: pytest.fail("command ran"))
    with pytest.raises(CheckFailure):
        probe.verify_native_planner_identity(None, SimpleNamespace(selection=Selection()), {}, 10)
````
