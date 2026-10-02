# workbench/business_python.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：基础Python产品的业务合同挂载。** 把共享的有限业务策略与产品自身Schema/认证连接，生成独立运行所需配置及文件；不依赖开发工作台进程或真实模型服务。

**对应关系：** generate_basic → 完整业务合同 → 产品自身运行时和独立验收。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `prepare_product`（L10–L31）：接收`plan`、`destination`。 控制顺序：L11按`not plan.business`分支。 调用`shutil.copyfile`、`render_business_sql`、`atomic_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `render_business_sql`（L34–L52）：接收`plan`、`destination`。 控制顺序：L42遍历`[("sqlite", "sqlite://"), ("postgresql", "postgresql://")]`。 调用`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`、`module.build_metadata`、`plan.model_dump`、`create_mock_engine`、`metadata.create_all`、`atomic_text`、`"\n\n".join`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `render_business_sql.emit`（L45–L46）：接收`statement`、`*args`、`**kwargs`。 调用`statements.append`、`str(statement.compile(dialect=engine.dialect)).strip`、`str`、`statement.compile`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/business_python.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L52。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1760`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/business_python.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e47b038187e60cf02d1d4518bc99a93d4c6b476e70421e252171e0d7d218d9e6"} -->
````python
# workbench/business_python.py
"""Deterministic migration hook for the optional business-aware Python product."""

import importlib.util
import shutil

from workbench.filesystem import atomic_text
from workbench.settings import ROOT


def prepare_product(plan, destination):
    if not plan.business:
        return
    shutil.copyfile(
        ROOT / "templates/business/common/policy.py", destination / "business_policy.py"
    )
    render_business_sql(plan, destination)
    atomic_text(
        destination / "migrations/versions/0001_initial.py",
        '''"""Frozen business metadata, with actual foreign keys and immutable event tables."""
from alembic import op
from schema import metadata
revision = "0001"
down_revision = None

def upgrade():
    metadata.create_all(op.get_bind(), checkfirst=False)

def downgrade():
    raise RuntimeError("Business data is retained; destructive automatic downgrade is disabled")
''',
    )


def render_business_sql(plan, destination):
    from sqlalchemy import create_mock_engine

    path = ROOT / "templates/product/business_schema.py"
    spec = importlib.util.spec_from_file_location("reviewed_business_schema", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    metadata = module.build_metadata(plan.model_dump())
    for name, url in [("sqlite", "sqlite://"), ("postgresql", "postgresql://")]:
        statements = []

        def emit(statement, *args, **kwargs):
            statements.append(str(statement.compile(dialect=engine.dialect)).strip() + ";")

        engine = create_mock_engine(url, emit)
        metadata.create_all(engine, checkfirst=False)
        atomic_text(
            destination / "database" / ("schema." + name + ".sql"), "\n\n".join(statements) + "\n"
        )
````
