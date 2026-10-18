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
    """Skills and the link from a technician to a skill"""
    op.create_table(
        "skills", 
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable =False),
        sa.Column("name", sa.Text(), nullable =False),
        sa.UniqueConstraint("tenant_id", "name", name="skills_tenant_name_unique"),
    )
    op.create_table(
        "technician_skills",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("technician_id", sa.UUID(), sa.ForeignKey("technicians.id"), nullable=False),
        sa.Column("skill_id", sa.UUID(), sa.ForeignKey("skills.id"), nullable=False),
        sa.PrimaryKeyConstraint("technician_id", "skill_id"),
    )
    for table in ("skills", "technician_skills"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY {table}_tenant_isolation ON {table}
            USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
            """)
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO app_user")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS technician_skills_tenant_isolation ON technician_skills")
    op.drop_table("technician_skills")
    op.execute("DROP POLICY IF EXISTS skills_tenant_isolation ON skills")
    op.drop_table("skills")

