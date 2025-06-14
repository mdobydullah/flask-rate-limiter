import time
import hashlib
import redis
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


class RateLimiter:
    def __init__(self, ttl=3600, mode='fixed'):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD", None),
            decode_responses=True
        )
        self.app_name = os.getenv("APP_NAME", "app")
        self.ttl = ttl
        self.mode = mode  # 'token' or 'fixed'

    def _hash_route(self, path: str) -> str:
        return hashlib.sha256(path.encode()).hexdigest()[:16]

    def is_allowed_dynamic(self, identifier, path, max_tokens, refill_rate):
        route_hash = self._hash_route(path)

        key_tokens = f"{self.app_name}:rateLimit:{identifier}-{route_hash}:tokens"
        key_timestamp = f"{self.app_name}:rateLimit:{identifier}-{route_hash}:ts"

        if self.mode == 'fixed':
            return fixed_window(self.redis, key_tokens, max_tokens, self.ttl)
        elif self.mode == 'token':
            return token_bucket(self.redis, key_tokens, key_timestamp, max_tokens, refill_rate, self.ttl)


def fixed_window(redis_client, key, limit, ttl):
    ttl_remaining = redis_client.ttl(key)

    if ttl_remaining == -2:
        # First request → set to (limit - 1)
        redis_client.set(key, limit - 1, ex=ttl)
        return True, limit - 1

    remaining_raw = redis_client.get(key)
    remaining = int(remaining_raw) if remaining_raw is not None else 0

    if remaining <= 0:
        return False, 0

    redis_client.decr(key)
    return True, remaining - 1


def token_bucket(redis_client, key_tokens, key_timestamp, limit, refill_rate, ttl):
    now = int(time.time())

    tokens_raw = redis_client.get(key_tokens)
    tokens = float(tokens_raw) if tokens_raw is not None else limit

    last_ts_raw = redis_client.get(key_timestamp)
    last_ts = int(last_ts_raw) if last_ts_raw else now

    # Calculate elapsed time and refill tokens
    elapsed = max(0, now - last_ts)
    refill = elapsed * refill_rate
    tokens = min(tokens + refill, limit)
    tokens = int(tokens)

    if tokens < 1:
        return False, 0  # Not allowed, 0 remaining

    tokens -= 1
    redis_client.set(key_tokens, tokens, ex=ttl)
    redis_client.set(key_timestamp, now, ex=ttl)

    return True, tokens  # Allowed, return remaining tokens
