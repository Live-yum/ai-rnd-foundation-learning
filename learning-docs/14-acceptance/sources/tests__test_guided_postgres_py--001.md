# tests/test_guided_postgres.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generator`、`workbench.settings`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `admin_url`（L18–L22）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L20按`not url`分支。 调用`os.getenv`、`pytest.skip`、`make_url`。 返回路径：L22的`make_url(url)`。
- `test_selected_postgresql_news_product_really_uses_postgresql`（L25–L41）：接收`tmp_path`。 控制顺序：L36断言`report["passed"] and report["database"] == "real-isolated-postgresql"`；L38断言`result["cleanroom"]["passed"] and result["cleanroom"]["database"] == "real-isolated-p…`。 调用`admin_url`、`Settings`、`base.render_as_string`、`generate_basic`、`news_plan`、`verify_basic`、`package_basic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_standalone_native_initialization_owns_only_its_empty_database`（L44–L65）：接收`tmp_path`。 控制顺序：L59断言`not ready`；L60断言`module.ownership(target, manifest) == (marker, False)`。 调用`admin_url`、`base.set(drivername="postgresql").render_as_string`、`base.set`、`uuid.uuid4`、`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`、`psycopg.connect`、`c.execute`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_guided_postgres.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L65。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2514`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_guided_postgres.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d51acee2be59ac978cbda05ee2cc94eac7584a0bb6d478b2dda0d39ac57d13bb"} -->
````python
# tests/test_guided_postgres.py
import importlib.util
import os
import uuid

import psycopg
import pytest
from news_case import news_plan
from psycopg import sql
from sqlalchemy.engine import make_url

from workbench.generator import generate_basic
from workbench.settings import ROOT, Settings
from workbench.verification import package_basic, verify_basic

pytestmark = pytest.mark.postgres


def admin_url():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("PostgreSQL service is required in the dedicated CI job")
    return make_url(url)


def test_selected_postgresql_news_product_really_uses_postgresql(tmp_path):
    base = admin_url()
    settings = Settings(
        data_dir=tmp_path / "state",
        install_products=False,
        product_postgres_url=base.render_as_string(hide_password=False),
        _env_file=None,
    )
    product = tmp_path / "run/product"
    generate_basic(news_plan(), product, {"template": "python-basic", "database": "postgresql"})
    report = verify_basic(news_plan(), product, settings)
    assert report["passed"] and report["database"] == "real-isolated-postgresql", report
    result = package_basic(news_plan(), product, settings, report)
    assert (
        result["cleanroom"]["passed"]
        and result["cleanroom"]["database"] == "real-isolated-postgresql"
    )


def test_standalone_native_initialization_owns_only_its_empty_database(tmp_path):
    base = admin_url()
    conn = base.set(drivername="postgresql").render_as_string(hide_password=False)
    name = "ownership_" + uuid.uuid4().hex[:12] + "_codegen"
    spec = importlib.util.spec_from_file_location(
        "standalone_native_run", ROOT / "templates/deployment/run.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with psycopg.connect(conn, autocommit=True) as c:
        c.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    target = base.set(database=name).render_as_string(hide_password=False)
    try:
        manifest = {"spec_digest": "a" * 64, "sql_digest": "b" * 64}
        marker, ready = module.ownership(target, manifest)
        assert not ready
        assert module.ownership(target, manifest) == (marker, False)
        with pytest.raises(ValueError):
            module.ownership(target, {"spec_digest": "c" * 64, "sql_digest": "b" * 64})
    finally:
        with psycopg.connect(conn, autocommit=True) as c:
            c.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))
````
