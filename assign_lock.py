RELEASE = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
end
return 0
"""


def lock_key(job_id: str) -> str:
    return f"job:{job_id}:assign"


def try_acquire(client, job_id: str, token: str, ttl_seconds: int = 30) -> bool:
    """Take the lock only if no one else holds it. The key dies after ttl_seconds."""
    return client.set(lock_key(job_id), token, nx=True, ex=ttl_seconds) is True


def release(client, job_id: str, token: str) -> bool:
    """Delete the lock only if this token still owns it."""
    removed = client.eval(RELEASE, 1, lock_key(job_id), token)
    return removed == 1