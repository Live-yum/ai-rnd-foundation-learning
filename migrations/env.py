from alembic import context

from workbench.settings import Settings
from workbench.store import Base, Store


def migrate(connection):
    context.configure(connection=connection, target_metadata=Base.metadata,
                      include_object=lambda obj, name, kind, reflected, compare: (
                          kind != "table" or name in Base.metadata.tables),
                      compare_type=True, render_as_batch=connection.dialect.name == "sqlite")
    with context.begin_transaction():
        context.run_migrations()


connection = context.config.attributes.get("connection")
if connection is not None:
    migrate(connection)
elif context.is_offline_mode():
    context.configure(url=Settings().db_url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    store = Store(Settings())
    try:
        with store.engine.begin() as connection:
            migrate(connection)
    finally:
        store.engine.dispose()
