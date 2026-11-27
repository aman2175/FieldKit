from datetime import datetime, timezone, timedelta
from uuid import uuid4 , UUID
from dispatch_engine.scoring import score_job, Job, TechnicianCandidate, ScoredCandidate
from pytest import fixture, mark

TENANT_ID=uuid4()
SKILL_FIBRE=uuid4()
SKILL_HVAC=uuid4()
PART_COMPRESSOR=uuid4()
NOW=datetime(2026, 11, 26, 10, 0, 0, tzinfo=timezone.utc)

SHIFT_START = NOW - timedelta(hours=2)
SHIFT_END = NOW + timedelta(hours=6)
OFF_SHIFT_START = NOW - timedelta(hours=10)
OFF_SHIFT_END = NOW - timedelta(hours=2)

def make_tech(
    tech_id: UUID,
    skills: frozenset[UUID],
    parts: frozenset[UUID] = frozenset(),
    on_shift: bool = True,
    open_jobs: int = 0,
) -> TechnicianCandidate:
    return TechnicianCandidate(
        id=tech_id,
        tenant_id=TENANT_ID,
        skill_ids=skills,
        shift_start=SHIFT_START if on_shift else OFF_SHIFT_START,
        shift_end=SHIFT_END if on_shift else OFF_SHIFT_END,
        current_lat=40.7128,
        current_lon=-74.0060,
        open_job_count=open_jobs,
        parts_on_van=parts,
    )

tech_a = make_tech(
    tech_id=uuid4(),
    skills=frozenset([SKILL_HVAC]),
    parts=frozenset([PART_COMPRESSOR]),
    on_shift=True,
    open_jobs=0,
)
tech_b = make_tech(
    tech_id=uuid4(),
    skills=frozenset([SKILL_HVAC]),
    parts=frozenset(),           # no compressor
    on_shift=True,
    open_jobs=0,
)
tech_c = make_tech(
    tech_id=uuid4(),
    skills=frozenset([SKILL_FIBRE]),   # wrong skill
    parts=frozenset([PART_COMPRESSOR]),
    on_shift=True,
    open_jobs=0,
)
tech_d = make_tech(
    tech_id=uuid4(),
    skills=frozenset([SKILL_HVAC]),
    parts=frozenset([PART_COMPRESSOR]),
    on_shift=False,               # off shift
    open_jobs=0,
)

job=Job(
id=uuid4(),
tenant_id=TENANT_ID,
required_skill_id=SKILL_HVAC,
site_lat=40.7128,
site_lon=-74.0060,
sla_due_at=NOW + timedelta(hours=4),
required_part_id=PART_COMPRESSOR,
)

def test_score():
    csn=[tech_a, tech_b, tech_c, tech_d]

    results=score_job(job,csn, NOW)
    tech_ids_in=[r.technician_id for r in results] 
    assert tech_c.id not in tech_ids_in

    assert len(results) == 3

    assert results[0].technician_id == tech_a.id
    assert results[1].technician_id == tech_b.id
    assert results[2].technician_id == tech_d.id
    assert results[0].reasons["skill"] == 40
    assert results[0].reasons["shift"] == 20
    assert results[0].reasons["part"] == 20
    assert results[0].reasons["distance"] == 20
    assert results[0].reasons["sla"] == 0

