"""add audit log

Revision ID: ba48d343fa87
Revises: 205d166b9de8
Create Date: 2026-10-18 00:00:44.367328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba48d343fa87'
down_revision: Union[str, Sequence[str], None] = '205d166b9de8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Who did what, and when. Rows are added, not edited."""
    op.create_table(
        "audit_log",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("actor", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("entity", sa.Text(), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.execute("ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_log FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY audit_log_tenant_isolation ON audit_log
        USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
        WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """
    )
    op.execute("GRANT SELECT, INSERT ON audit_log TO app_user")


def downgrade() -> None:
    """Remove the audit log."""
    op.execute("DROP POLICY IF EXISTS audit_log_tenant_isolation ON audit_log")
    op.drop_table("audit_log")
