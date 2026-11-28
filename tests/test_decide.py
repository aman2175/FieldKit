from uuid import uuid4

from dispatch_engine.decide import decide, DecideFacts
from dispatch_engine.scoring import ScoredCandidate


def scored(score: int, shift: int =20, part: int =20)-> ScoredCandidate:
    return ScoredCandidate(
        technician_id=uuid4(),
        score=score,
        reasons={"skill": 40, "shift": shift,"part":part, "distance":0 , "load":0, "sla":0}

    )


def facts(**overrides) -> DecideFacts:
    base = dict(
        customer_known=True,
        site_ready=True,
        is_vip=False,
        is_emergency=False,
        is_suspected_duplicate=False,
        job_requires_part=True,
    )
    base.update(overrides)
    return DecideFacts(**base)

def test_all_green():
    winner=scored(90)
    second=scored(50, part=0)
    result=decide(scored=[winner, second], facts=facts())
    assert result.auto_assign is True
    assert result.reason == "all green"
    assert result.technician_id == winner.technician_id

def test_vip():
    winner=scored(90)
    result=decide([winner], facts(is_vip=True))
    assert result.auto_assign is False
    assert result.reason == "vip_requires_human_review"
    assert result.top_3 == (winner,)


def test_no_candidates():
    result = decide([], facts())
    assert result.auto_assign is False
    assert result.reason == "No candidates scored"
def test_low_score_gap():
    result = decide([scored(80), scored(70)], facts())
    assert result.auto_assign is False
    assert result.reason == "score_gap_too_small"
def test_part_missing():
    result = decide([scored(90, part=0)], facts())
    assert result.reason == "part_missing"