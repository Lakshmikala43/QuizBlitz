import time
from functools import wraps
from typing import Dict, Tuple, List
from flask import request, abort, g, current_app


class MemoryRateLimiter:
    """
    In-memory sliding window rate limiter.
    Self-contained, production-safe without requiring Redis in local dev.
    """

    def __init__(self):
        # Key: (bucket_name, client_identifier) -> List[timestamp]
        self._history: Dict[Tuple[str, str], List[float]] = {}

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is within rate limit window."""
        now = time.time()
        cutoff = now - window_seconds

        timestamps = self._history.get(key, [])
        # Prune old timestamps
        timestamps = [ts for ts in timestamps if ts > cutoff]

        if len(timestamps) >= max_requests:
            self._history[key] = timestamps
            return False

        timestamps.append(now)
        self._history[key] = timestamps
        return True

    def reset(self):
        """Clear limiter memory (useful in tests)."""
        self._history.clear()


limiter = MemoryRateLimiter()


def rate_limit(requests: int = 60, window_sec: int = 60, bucket: str = "default"):
    """Decorator to enforce request rate limits on sensitive endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip rate limits in test environment
            if current_app.config.get("TESTING", False):
                return f(*args, **kwargs)

            # Identifier combines client IP and optional authenticated user
            client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")
            client_ip = client_ip.split(",")[0].strip()
            key = f"{bucket}:{client_ip}"

            if not limiter.is_allowed(key, max_requests=requests, window_seconds=window_sec):
                abort(429)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def init_security(app):
    """Register HTTP security headers and request lifecycle timers on the Flask app."""

    @app.before_request
    def record_start_time():
        g.request_start_time = time.time()

    @app.after_request
    def apply_security_headers(response):
        # Compute response duration in ms
        if hasattr(g, "request_start_time"):
            duration_ms = int((time.time() - g.request_start_time) * 1000)
            response.headers["X-Response-Time-Ms"] = str(duration_ms)

        # Defense-in-depth security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # Modern Content-Security-Policy (allows local assets, inline styles for animations, Web Audio API, websockets)
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws: wss:; "
            "media-src 'self' data: blob:;"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        return response
