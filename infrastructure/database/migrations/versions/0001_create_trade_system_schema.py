"""Create the schema for the Trade System database."""

from alembic import op
from sqlalchemy.schema import CreateSchema, DropSchema

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(CreateSchema("trade_system"))


def downgrade() -> None:
    op.execute(DropSchema("trade_system"))
