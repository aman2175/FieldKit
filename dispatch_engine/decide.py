from dataclasses import dataclass , field
from dispatch_engine.scoring import ScoredCandidate
from uuid import UUID

MIN_SCORE_GAP=15

@dataclass(frozen=True)
class DecideFacts:
    customer_known: bool
    site_ready: bool
    is_vip: bool
    is_emergency: bool
    is_suspected_duplicate: bool
    job_requires_part: bool

@dataclass(frozen=True)
class Decision:
    auto_assign: bool
    reason: str
    technician_id:UUID | None = None
    top_3: tuple[ScoredCandidate, ScoredCandidate, ScoredCandidate] = field(default_factory=tuple)

def decide(scored: list[ScoredCandidate], facts: DecideFacts) -> Decision:
    top_3=tuple(scored[:3])
    if not scored:
        return Decision(auto_assign=False, reason="No candidates scored")
    top=scored[0]
    if not facts.customer_known:
        return Decision(auto_assign=False, reason="unknown customer", top_3=top_3)
    
    if not facts.site_ready:
        return Decision(auto_assign=False, reason="site not ready", top_3=top_3)
    
    if facts.is_vip:
        return Decision(auto_assign=False, reason="vip_requires_human_review", top_3=top_3)

    if facts.is_emergency:
        return Decision(auto_assign=False, reason="emergency_requires_human_review", top_3=top_3)
    
    if facts.is_suspected_duplicate:
        return Decision(auto_assign=False, reason="suspected_duplicate_requires_human_review", top_3=top_3)

    if facts.job_requires_part and top.reasons.get("part", 0) == 0:
        return Decision(auto_assign=False, reason="part_missing", top_3=top_3)
    
    if top.reasons.get("shift", 0) == 0:
        return Decision(auto_assign=False, reason="shift_missing", top_3=top_3)
    
    if len(scored) >= 2 and (scored[0].score - scored[1].score)<MIN_SCORE_GAP:
        return Decision(auto_assign=False, reason="score_gap_too_small", top_3=top_3)


    return Decision(auto_assign=True, reason="all green", technician_id=top.technician_id)
