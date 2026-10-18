"""add customers and sites

Revision ID: f6d8e4f4e851
Revises: 2fd50307ac9f
Create Date: 2026-10-17 23:54:14.262058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6d8e4f4e851'
down_revision: Union[str, Sequence[str], None] = '2fd50307ac9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Who the work is for, and where it happens."""
    op.create_table(
        "customers",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("phone", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=True),
    )
    op.create_table(
        "sites",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
    )
    for table in ("customers", "sites"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"""
            CREATE POLICY {table}_tenant_isolation ON {table}
            USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
            """
        )
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO app_user")


def downgrade() -> None:
    """Remove sites, then customers."""
    op.execute("DROP POLICY IF EXISTS sites_tenant_isolation ON sites")
    op.drop_table("sites")
    op.execute("DROP POLICY IF EXISTS customers_tenant_isolation ON customers")
    op.drop_table("customers")
