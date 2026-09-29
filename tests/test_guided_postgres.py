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
