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
    top_3: tuple[ScoredCandidate, ScoredCandidate, ScoredCandidate] = field(deafault_factory=tuple)

