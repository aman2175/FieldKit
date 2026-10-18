"""add shifts

Revision ID: 2fd50307ac9f
Revises: 6cef32599cd3
Create Date: 2026-10-17 23:47:08.953281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fd50307ac9f'
down_revision: Union[str, Sequence[str], None] = '6cef32599cd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """When a technician is on the clock."""
    op.create_table(
        "shifts",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("technician_id", sa.UUID(), sa.ForeignKey("technicians.id"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.execute("ALTER TABLE shifts ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE shifts FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY shifts_tenant_isolation ON shifts
        USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
        WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """
    )
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON shifts TO app_user")


def downgrade() -> None:
    """Remove shifts."""
    op.execute("DROP POLICY IF EXISTS shifts_tenant_isolation ON shifts")
    op.drop_table("shifts")
