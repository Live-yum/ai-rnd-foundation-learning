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
