from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
# we are just writing constructors for the classes and we are not writing any methods
@dataclass(frozen=True)
class Job:
    id: UUID
    tenant_id: UUID
    required_skill_id: UUID
    site_lat: float
    site_lon: float
    sla_due_at: datetime
    required_part_id: UUID | None = None
    priority: int = 1

@dataclass(frozen=True)
class TechnicianCandidate:
    id: UUID
    tenant_id: UUID
    skill_ids: frozenset[UUID]
    shift_start: datetime
    shift_end: datetime
    current_lat: float
    current_lon: float
    open_job_count: int
    parts_on_van: frozenset[UUID] = field(default_factory=frozenset)# field is used to define a default value for the parts_on_van attribute means if empty it will return an empty frozenset 

@dataclass(frozen=True)
class ScoredCandidate:
    technician_id: UUID
    score: int
    reasons: dict[str, int]# dict is a dictionary of strings and integers str: skill and int is score 