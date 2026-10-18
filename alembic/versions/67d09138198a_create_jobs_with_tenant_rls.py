"""Create jobs table with tenant RLS (row-level security).

Revision ID: 67d09138198a
Revises: None
Create Date: 2026-10-11 21:05:01.175506

This is the first migration. It creates:
- a dedicated Postgres login for the app (`app_user`)
- the `jobs` table (one row per job, with `tenant_id` on every row)
- a row-level security (RLS) policy that enforces tenant isolation in the database
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67d09138198a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create jobs with database-enforced tenant isolation."""

    # Create a dedicated Postgres login for the application/tests.
    # This is the role our API will connect as. It is not the table owner and
    # not a superuser, so row-level security (RLS) really applies to it.
    op.execute("CREATE ROLE app_user LOGIN PASSWORD 'app_user'")

    # Create the jobs table.
    # - id:          job id (UUID primary key)
    # - tenant_id:   which company owns this job (UUID, required)
    # - title:       short description so the row is not empty (required)
    # Every row carries a tenant_id so the RLS policy can decide visibility.
    op.create_table(
        "jobs",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
    )

    # Turn on row-level security for jobs.
    # ENABLE RLS  = table obeys policies for normal roles.
    # FORCE RLS   = even the table owner is forced through policies (no owner bypass).
    op.execute("ALTER TABLE jobs ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE jobs FORCE ROW LEVEL SECURITY")

    # jobs_tenant_isolation = per-row tenant fence.
    #
    # app.tenant_id is a *per-connection note* (set by the app/test) saying
    # "this request is tenant X". It is stored with:
    #
    #   SELECT set_config('app.tenant_id', '<tenant-uuid>', true);
    #
    # current_setting('app.tenant_id', true)::uuid reads that note back as a UUID.
    # - USING:
    #     On read/update, only rows where jobs.tenant_id == app.tenant_id are visible.
    # - WITH CHECK:
    #     On insert/update, you may only write rows whose tenant_id == app.tenant_id.
    #
    # If the app never set app.tenant_id, current_setting(..., true) returns NULL.
    # NULL matches no tenant_id, so the policy fails closed and returns no rows.
    op.execute(
        """
        CREATE POLICY jobs_tenant_isolation ON jobs
        USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
        WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """
    )

    # Allow app_user to use the jobs table at all.
    # RLS still filters *which* rows app_user can see or change.
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON jobs TO app_user")


def downgrade() -> None:
    """Drop jobs table, RLS policy, and app_user (reverse of upgrade)."""

    # Remove the tenant fence and the table if this migration is rolled back.
    op.execute("DROP POLICY IF EXISTS jobs_tenant_isolation ON jobs")
    op.drop_table("jobs")
    op.execute("DROP ROLE IF EXISTS app_user")
