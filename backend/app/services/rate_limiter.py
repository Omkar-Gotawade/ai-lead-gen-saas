"""Redis-backed rate limiting utilities."""
from datetime import datetime
from fastapi import HTTPException, status

from app.services.redis_service import RedisService


LIMITS = {
    "login": (5, 60),
    "email_generation": (20, 60),
    "campaign_send": (10, 60),
}


def _bucket_key(scope: str, identity: str) -> str:
    now = int(datetime.utcnow().timestamp())
    window = LIMITS[scope][1]
    bucket = now // window
    return f"rate:{scope}:{identity}:{bucket}"


def enforce_rate_limit(scope: str, identity: str) -> None:
    """Enforce fixed-window rate limits backed by Redis."""
    if scope not in LIMITS:
        return

    limit, ttl = LIMITS[scope]
    client = RedisService.get_client()

    # Fail-open if Redis is unavailable to avoid taking down core APIs.
    if not client:
        return

    key = _bucket_key(scope, identity)
    count = client.incr(key)
    if count == 1:
        client.expire(key, ttl)

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for {scope}. Limit is {limit} per {ttl} seconds.",
        )
