"""add photo_url to users

Revision ID: 9d7ab6c91f2e
Revises: 4a2dfaf2bb10
Create Date: 2026-03-06 16:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d7ab6c91f2e"
down_revision: Union[str, Sequence[str], None] = "4a2dfaf2bb10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("photo_url", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "photo_url")
