"""Persist selected backend/frontend/database and explicit automated-decision consent."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # ADD COLUMN is supported by both SQLite and PostgreSQL; keep existing run rows/checkpoints.
    op.add_column(
        "runs", sa.Column("options", sa.JSON(), nullable=False, server_default=sa.text("'{}'"))
    )
    op.add_column(
        "runs", sa.Column("auto_mode", sa.Boolean(), nullable=False, server_default=sa.false())
    )


def downgrade():
    with op.batch_alter_table("runs") as batch:
        batch.drop_column("auto_mode")
        batch.drop_column("options")
