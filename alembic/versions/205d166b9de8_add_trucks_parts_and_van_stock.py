"""add trucks parts and van stock

Revision ID: 205d166b9de8
Revises: f6d8e4f4e851
Create Date: 2026-10-17 23:59:59.707349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '205d166b9de8'
down_revision: Union[str, Sequence[str], None] = 'f6d8e4f4e851'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Vans, parts, and how many of each part are on a van."""
    op.create_table(
        "trucks",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
    )
    op.create_table(
        "parts",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.UniqueConstraint("tenant_id", "name", name="parts_tenant_name_unique"),
    )
    op.create_table(
        "van_stock",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("truck_id", sa.UUID(), sa.ForeignKey("trucks.id"), nullable=False),
        sa.Column("part_id", sa.UUID(), sa.ForeignKey("parts.id"), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("truck_id", "part_id"),
    )
    for table in ("trucks", "parts", "van_stock"):
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
    """Remove stock, then parts and trucks."""
    op.execute("DROP POLICY IF EXISTS van_stock_tenant_isolation ON van_stock")
    op.drop_table("van_stock")
    op.execute("DROP POLICY IF EXISTS parts_tenant_isolation ON parts")
    op.drop_table("parts")
    op.execute("DROP POLICY IF EXISTS trucks_tenant_isolation ON trucks")
    op.drop_table("trucks")
