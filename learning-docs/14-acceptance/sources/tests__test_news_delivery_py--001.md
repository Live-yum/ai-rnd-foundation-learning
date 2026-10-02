# tests/test_news_delivery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generator`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_reported_news_requirements_run_in_real_product_process`（L9–L26）：接收`settings`。 控制顺序：L14断言`report["passed"]`；L15断言`{ "search:title", "search:body", "filter:category", "inclusive-date-range:published_o…`；L21断言`report["restart"] is True`；L22断言`(product / "web/index.html").exists()`；L23断言`(product / "database/schema.sqlite.sql").exists()`；L25断言`packaged["cleanroom"]["passed"]`；L26断言`(product / "start.py").exists()`。 调用`news_plan`、`generate_basic`、`verify_basic`、`set`、`(product / "web/index.html").exists`、`(product / "database/schema.sqlite.sql").exists`、`package_basic`、`(product / "start.py").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_date_and_enum_are_real_validations_not_prompt_assumptions`（L29–L50）：接收`settings`。 控制顺序：L41断言`model.model_validate(good).model_dump()["published_on"] == "2026-02-28"`；L42遍历`[ dict(published_on="2026-02-30"), dict(published_on="2026/02/28"…`。 调用`generate_basic`、`news_plan`、`importlib.util.spec_from_file_location`、`importlib.util.module_from_spec`、`spec.loader.exec_module`、`news_plan().entities[0].model_dump`、`module.input_model`、`dict`、`model.model_validate(good).model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_news_delivery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L50。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1939`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_news_delivery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "720a4fe0e2b399dbbb476341c20a8c27313ac4d50312d3d700c2961142f1a4c6"} -->
````python
# tests/test_news_delivery.py
import importlib.util

from news_case import news_plan

from workbench.generator import generate_basic
from workbench.verification import package_basic, verify_basic


def test_reported_news_requirements_run_in_real_product_process(settings):
    plan = news_plan()
    product = settings.data_dir / "runs/news/product"
    generate_basic(plan, product)
    report = verify_basic(plan, product, settings)
    assert report["passed"], report
    assert {
        "search:title",
        "search:body",
        "filter:category",
        "inclusive-date-range:published_on",
    } <= set(report["checks"])
    assert report["restart"] is True
    assert (product / "web/index.html").exists()
    assert (product / "database/schema.sqlite.sql").exists()
    packaged = package_basic(plan, product, settings, report)
    assert packaged["cleanroom"]["passed"]
    assert (product / "start.py").exists()


def test_date_and_enum_are_real_validations_not_prompt_assumptions(settings):
    product = settings.data_dir / "runs/fields/product"
    generate_basic(news_plan(), product)
    spec = importlib.util.spec_from_file_location("standalone_fields", product / "fields.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Load in isolated helper, no app/module side effects.
    entity = news_plan().entities[0].model_dump()
    import pytest

    model = module.input_model(entity)
    good = dict(title="测试", body="文章", published_on="2026-02-28", category=None)
    assert model.model_validate(good).model_dump()["published_on"] == "2026-02-28"
    for bad in [
        dict(published_on="2026-02-30"),
        dict(published_on="2026/02/28"),
        dict(category="任意分类"),
        dict(title="x" * 251),
        dict(body="x" * 3001),
    ]:
        with pytest.raises(ValueError):
            module.validate_options(entity, model.model_validate({**good, **bad}).model_dump())
````
