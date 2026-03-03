"""set default orders_count for sellers

Revision ID: 4a2dfaf2bb10
Revises: ffbaf5869d9d
Create Date: 2026-03-03 09:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4a2dfaf2bb10"
down_revision: Union[str, Sequence[str], None] = "ffbaf5869d9d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "sellers",
        "orders_count",
        existing_type=sa.Integer(),
        server_default="0",
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "sellers",
        "orders_count",
        existing_type=sa.Integer(),
        server_default=None,
        existing_nullable=False,
    )
