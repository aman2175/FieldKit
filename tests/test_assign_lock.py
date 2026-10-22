import sys
from pathlib import Path
import uuid
import redis
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from assign_lock import release, try_acquire
def test_second_dispatcher_does_not_get_the_lock():
    client=redis.Redis(host='localhost', port=6379, decode_responses=True)
    job_id=str(uuid.uuid4())
    first = str(uuid.uuid4())
    second = str(uuid.uuid4())
    client.delete(f"job:{job_id}:assign")#clear the lock if exist

    assert try_acquire(client, job_id, first) is True
    assert try_acquire(client, job_id, second) is False
    assert release(client, job_id, second) is False
    assert release(client, job_id, first) is True
    assert try_acquire(client, job_id, second) is True
    client.delete(f"job:{job_id}:assign")

