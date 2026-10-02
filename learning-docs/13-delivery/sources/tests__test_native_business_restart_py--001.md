# tests/test_native_business_restart.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.portable_checks`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_restart_snapshot_uses_real_declared_ids_and_closes_client`（L12–L54）：接收`monkeypatch`。 控制顺序：L38断言`before["customers"]["id"] == "1" and len(before["customers"]["sha256"]) == 64`；L48断言`len(closed) == 4`。 调用`monkeypatch.setattr`、`snapshot_business_records`、`len`、`require_preserved_business_records`、`pytest.raises`、`deepcopy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_restart_snapshot_uses_real_declared_ids_and_closes_client.Client`（L19–L27）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_restart_snapshot_uses_real_declared_ids_and_closes_client.Client.__init__`（L20–L21）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_restart_snapshot_uses_real_declared_ids_and_closes_client.Client.rows`（L23–L24）：接收`entity`、`**kwargs`。 返回路径：L24的`rows[entity]`。
- `test_restart_snapshot_uses_real_declared_ids_and_closes_client.Client.close`（L26–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`closed.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_delivered_launcher_captures_before_process_exit_and_checks_before_browser`（L57–L65）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L63断言`first < second_process < checked < browser`；L64断言`'outcome["restart"] = True' in source`；L65断言`'outcome["restart_preserved_records"] = True' in source`。 调用`(ROOT / "templates/deployment/run.py").read_text`、`source.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_business_restart.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L65。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2568`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_business_restart.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3ada19a4a46757137bfe3818529e4af6d8454a0400cad0a3fde15fb701dab291"} -->
````python
# tests/test_native_business_restart.py
"""The delivered process must preserve exact first-process records after restart."""

from copy import deepcopy

import pytest

from workbench import business_probe
from workbench.portable_checks import require_preserved_business_records, snapshot_business_records
from workbench.settings import ROOT


def test_restart_snapshot_uses_real_declared_ids_and_closes_client(monkeypatch):
    closed = []
    rows = {
        "customers": [{"id": "1", "name": "Synthetic customer"}],
        "requests": [{"id": "2", "request_state": "resolved"}],
    }

    class Client:
        def __init__(self, *args):
            pass

        def rows(self, entity, **kwargs):
            return rows[entity]

        def close(self):
            closed.append(True)

    monkeypatch.setattr(business_probe, "BusinessClient", Client)
    args = (
        "fastapiadmin",
        "http://127.0.0.1",
        "synthetic-token",
        [{"entity": entity} for entity in rows],
        {"records": {"customers": "1", "requests": "2"}},
    )
    before = snapshot_business_records(*args)
    assert before["customers"]["id"] == "1" and len(before["customers"]["sha256"]) == 64
    after = snapshot_business_records(*args)
    require_preserved_business_records(before, after)
    rows["requests"][0]["request_state"] = "new"
    changed = snapshot_business_records(*args)
    with pytest.raises(ValueError, match="changed or lost"):
        require_preserved_business_records(before, changed)
    rows["requests"] = []
    with pytest.raises(ValueError, match="lost the original"):
        snapshot_business_records(*args)
    assert len(closed) == 4
    with pytest.raises(ValueError):
        require_preserved_business_records({}, {})
    wrong_identity = deepcopy(after)
    wrong_identity["customers"]["id"] = "8"
    with pytest.raises(ValueError):
        require_preserved_business_records(before, wrong_identity)


def test_delivered_launcher_captures_before_process_exit_and_checks_before_browser():
    source = (ROOT / "templates/deployment/run.py").read_text(encoding="utf-8")
    first = source.index("before_restart = snapshot_business_records(")
    second_process = source.index("base, _ = stack.enter_context(running_backend(")
    checked = source.index("require_preserved_business_records(before_restart, after_restart)")
    browser = source.index('outcome["browser"] = run_business_browser(')
    assert first < second_process < checked < browser
    assert 'outcome["restart"] = True' in source
    assert 'outcome["restart_preserved_records"] = True' in source
````
