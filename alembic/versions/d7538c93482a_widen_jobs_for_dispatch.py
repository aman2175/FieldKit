"""widen jobs for dispatch

Revision ID: d7538c93482a
Revises: ba48d343fa87
Create Date: 2026-10-18 00:02:13.815652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7538c93482a'
down_revision: Union[str, Sequence[str], None] = 'ba48d343fa87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """A job points at a customer, a site, and a skill, and records its clock."""
    op.add_column("jobs", sa.Column("customer_id", sa.UUID(), sa.ForeignKey("customers.id"), nullable=True))
    op.add_column("jobs", sa.Column("site_id", sa.UUID(), sa.ForeignKey("sites.id"), nullable=True))
    op.add_column("jobs", sa.Column("skill_id", sa.UUID(), sa.ForeignKey("skills.id"), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("assigned_tech_id", sa.UUID(), sa.ForeignKey("technicians.id"), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("status", sa.Text(), nullable=False, server_default="open"),
    )
    op.add_column(
        "jobs",
        sa.Column("job_type", sa.Text(), nullable=False, server_default="repair"),
    )
    op.add_column("jobs", sa.Column("sla_due_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("jobs", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("jobs", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_check_constraint(
        "jobs_status_known",
        "jobs",
        "status IN ('open', 'assigned', 'started', 'completed', 'exception')",
    )
    op.create_check_constraint(
        "jobs_type_known",
        "jobs",
        "job_type IN ('repair', 'new_activation')",
    )


def downgrade() -> None:
    """Remove the dispatch columns from jobs."""
    op.drop_constraint("jobs_type_known", "jobs", type_="check")
    op.drop_constraint("jobs_status_known", "jobs", type_="check")
    op.drop_column("jobs", "completed_at")
    op.drop_column("jobs", "started_at")
    op.drop_column("jobs", "sla_due_at")
    op.drop_column("jobs", "job_type")
    op.drop_column("jobs", "status")
    op.drop_column("jobs", "assigned_tech_id")
    op.drop_column("jobs", "skill_id")
    op.drop_column("jobs", "site_id")
    op.drop_column("jobs", "customer_id")
