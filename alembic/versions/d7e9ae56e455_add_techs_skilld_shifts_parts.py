"""add techs skilld shifts parts

Revision ID: d7e9ae56e455
Revises: 67d09138198a
Create Date: 2026-10-12 18:28:41.561159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd7e9ae56e455'
down_revision: Union[str, Sequence[str], None] = '67d09138198a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Technicians, fenced by tenant the same way jobs are."""
    op.create_table(
        "technicians",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("phone", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.execute("ALTER TABLE technicians ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE technicians FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY technicians_tenant_isolation ON technicians
        USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
        WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON technicians TO app_user"
    )


def downgrade() -> None:
    """Remove technicians."""
    op.execute("DROP POLICY IF EXISTS technicians_tenant_isolation ON technicians")
    op.drop_table("technicians")
