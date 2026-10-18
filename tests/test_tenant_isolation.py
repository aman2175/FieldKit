import uuid
import psycopg
import pytest

ADMIN_DSN="postgresql://fieldkit:fieldkit@localhost:5434/fieldkit"
APP_DSN="postgresql://app_user:app_user@localhost:5434/fieldkit"


@pytest.fixture
def seed_jobs():
    """INSERT ONE JOB FOR TENAT A N ONE FOR TENANAT AS ADMIN USER"""
    tenant_a=uuid.uuid4()
    tenant_b=uuid.uuid4()

    job_a=uuid.uuid4()
    job_b=uuid.uuid4()

    with psycopg.connect(ADMIN_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM jobs")
            cur.execute("INSERT INTO jobs (id, tenant_id, title) VALUES (%s,%s,%s)", (job_a, tenant_a,"JOB FOR A"))
            cur.execute("INSERT INTO jobs (id, tenant_id, title) VALUES (%s,%s,%s)", (job_b, tenant_b,"JOB FOR B"))
        conn.commit()
    return {
        "tenant_a":tenant_a,
        "tenant_b":tenant_b,
        "job_a":job_a,
        "job_b":job_b,
    }
def _visible_job_ids(conn) -> set[uuid.UUID]:
    """Return the set of job ids visible on this connection."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM jobs")
        return {row[0] for row in cur.fetchall()}

def test_tenant_isolation(seed_jobs):
    """Tenant A sees only A's job; tenant B sees only B's job."""
    jobs = seed_jobs
    with psycopg.connect(APP_DSN) as conn:
        with conn.cursor() as cur:
            #ACT AS TENAT A
            cur.execute("SELECT set_config('app.tenant_id', %s , true)", (str(jobs["tenant_a"]),))
            ids_as_a=_visible_job_ids(conn)
            assert ids_as_a=={jobs["job_a"]}
            #ACT AS TENAT B
            cur.execute("SELECT set_config('app.tenant_id', %s , true)", (str(jobs["tenant_b"]),))
            ids_as_b=_visible_job_ids(conn)
            assert ids_as_b=={jobs["job_b"]}


