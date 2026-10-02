# tests/test_postgres.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.runtime`、`workbench.settings`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_postgres_migrations_transactions_and_checkpoint`（L14–L36）：接收`tmp_path`、`plan`。 控制顺序：L16按`not url`分支；L23断言`store.create_project("pg", key) == store.create_project("pg", key)`；L27断言`store.get_run(run)["status"] == "WAITING_REQUIREMENTS"`；L31断言`store.get_run(run)["status"] == "WAITING_DESIGN"`；L34断言`store.get_run(run)["status"] == "REJECTED"`。 调用`os.getenv`、`pytest.skip`、`Settings`、`Store`、`store.migrate`、`str`、`uuid.uuid4`、`store.create_project`、`new_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_postgres.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L36。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1307`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_postgres.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e69d89e40edd867759b1c969c8fca424117d4645f265d3e110a34c5c469dc07a"} -->
````python
# tests/test_postgres.py
import os
import uuid

import pytest
from conftest import FixtureGateway, decision, new_run

from workbench.runtime import Runtime
from workbench.settings import Settings
from workbench.store import Store

pytestmark = pytest.mark.postgres


def test_postgres_migrations_transactions_and_checkpoint(tmp_path, plan):
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set; mandatory in postgres Actions job")
    settings = Settings(data_dir=tmp_path, database_url=url, install_products=False, _env_file=None)
    store = Store(settings)
    try:
        store.migrate()
        key = str(uuid.uuid4())
        assert store.create_project("pg", key) == store.create_project("pg", key)
        run = new_run(store)
        with Runtime(settings, store, FixtureGateway(plan)) as runtime:
            runtime.tick()
            assert store.get_run(run)["status"] == "WAITING_REQUIREMENTS"
            decision(store, run)
        with Runtime(settings, store, FixtureGateway(plan)) as runtime:
            runtime.tick()
            assert store.get_run(run)["status"] == "WAITING_DESIGN"
            decision(store, run, "reject")
            runtime.tick()
        assert store.get_run(run)["status"] == "REJECTED"
    finally:
        store.engine.dispose()
````
