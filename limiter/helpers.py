from functools import wraps
from flask import request, jsonify
from .core import RateLimiter


def parse_rate(rate_str):
    num, unit = rate_str.lower().split('/')
    num = int(num)

    if unit in ['s', 'sec', 'second']:
        return num, num, 1
    elif unit in ['m', 'min', 'minute']:
        return num, num / 60, 60
    elif unit in ['h', 'hour']:
        return num, num / 3600, 3600
    else:
        raise ValueError("Invalid rate format")


# Flask decorator
def ratelimit(key='ip', rate='5/m', mode='fixed'):
    max_tokens, refill_rate, ttl = parse_rate(rate)
    limiter = RateLimiter(ttl=ttl, mode=mode)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identifier = request.headers.get('X-Forwarded-For', request.remote_addr) if key == 'ip' else key
            path = request.path

            allowed, remaining = limiter.is_allowed_dynamic(identifier, path, max_tokens, refill_rate)

            if not allowed:
                return jsonify({"error": "Too Many Requests"}), 429

            return fn(*args, **kwargs)

        return wrapper

    return decorator
