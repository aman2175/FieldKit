from dataclasses import dataclass, field # it is auto generated code for data holding classes no need to write entire class
from datetime import datetime
from uuid import UUID
import math

# Scoring weights — tune here, not in the function body.
# Higher = more important. Negative = penalty.
SKILL_MATCH_POINTS = 40        # hard requirement; without it the tech is filtered out
SHIFT_FIT_POINTS = 20          # visit fits inside the tech's shift
PART_ON_VAN_POINTS = 20        # required part already in her truck
DISTANCE_NEAR_POINTS = 20      # site < 10 km
DISTANCE_MID_POINTS = 10       # site < 30 km
LOAD_PENALTY_PER_JOB = -5      # subtracted per already-open job
SLA_URGENT_POINTS = 10         # SLA due in < 4 hours

NEAR_DISTANCE_KM = 10
MID_DISTANCE_KM = 30
SLA_URGENT_HOURS = 4

def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float)->float:
    R=6371.0 # radius of the earth in km
    phi1=math.radians(lat1)
    phi2=math.radians(lat2)
    dphi= math.radians(lat2-lat1)
    dlambda= math.radians(lon2-lon1)
    # USING HAVERSINE FORMULA TO CALCULATE THE DISTANCE BETWEEN TWO POINTS ON THE EARTH=======
    a=math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))



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
    # this mean everytime this will create new set for me unique and for container we use field
@dataclass(frozen=True)
class ScoredCandidate:
    technician_id: UUID
    score: int
    reasons: dict[str, int]# dict is a dictionary of strings and integers str: skill and int is score 


def score_job(
    job:Job,
    candidates: list[TechnicianCandidate],
    now: datetime,) -> list[ScoredCandidate]:
    results: list[ScoredCandidate] = []
    
    for t in candidates:
        reasons: dict[str, int] = {}
        if job.required_skill_id not in t.skill_ids:
            continue
        
        reasons["skill"]=SKILL_MATCH_POINTS

        if t.shift_start<=now<=t.shift_end:
            reasons["shift"]=SHIFT_FIT_POINTS
        else:
            reasons["shift"]=0
        
        if job.required_part_id is not None and job.required_part_id  in t.parts_on_van:
            reasons["part"]=PART_ON_VAN_POINTS
        else:
            reasons["part"]=0

        km = _distance_km(job.site_lat, job.site_lon, t.current_lat, t.current_lon)

        if km < NEAR_DISTANCE_KM:
            reasons["distance"] = DISTANCE_NEAR_POINTS
        elif km < MID_DISTANCE_KM:
            reasons["distance"] = DISTANCE_MID_POINTS
        else:
            reasons["distance"] = 0

        reasons["load"]=LOAD_PENALTY_PER_JOB * t.open_job_count

        hours_till_sla=(job.sla_due_at - now).total_seconds() / 3600

        if hours_till_sla < SLA_URGENT_HOURS:
            reasons["sla"] = SLA_URGENT_POINTS
        else:
            reasons["sla"] = 0

        scores= sum(reasons.values())
        results.append(ScoredCandidate(t.id, scores, reasons))
    results.sort(key=lambda x: x.score, reverse=True)
    return results
