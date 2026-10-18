"""add skills

Revision ID: 6cef32599cd3
Revises: d7e9ae56e455
Create Date: 2026-10-17 20:26:51.628674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cef32599cd3'
down_revision: Union[str, Sequence[str], None] = 'd7e9ae56e455'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
