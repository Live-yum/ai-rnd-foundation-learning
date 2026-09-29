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
