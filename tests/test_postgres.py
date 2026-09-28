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
