"""
Rate limiter — enforce per-target request rate limits.
"""

import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """
    Token bucket rate limiter. Enforces maximum requests per second per host.
    """

    def __init__(self, default_rate: float = 5.0):
        self.default_rate = default_rate
        self._buckets: dict[str, dict] = {}  # host -> {"tokens": float, "last_refill": float, "rate": float}
        self._lock = Lock()

    def configure_host(self, host: str, rate: float) -> None:
        """Set rate limit for a specific host."""
        with self._lock:
            self._buckets[host] = {
                "tokens": rate,
                "last_refill": time.monotonic(),
                "rate": rate,
            }

    def acquire(self, host: str) -> bool:
        """
        Try to acquire a token. Returns True if allowed, False if rate limited.

        If the host hasn't been configured, uses default rate.
        """
        with self._lock:
            if host not in self._buckets:
                self._buckets[host] = {
                    "tokens": self.default_rate,
                    "last_refill": time.monotonic(),
                    "rate": self.default_rate,
                }

            bucket = self._buckets[host]
            now = time.monotonic()
            elapsed = now - bucket["last_refill"]

            # Refill tokens
            bucket["tokens"] = min(bucket["rate"], bucket["tokens"] + elapsed * bucket["rate"])
            bucket["last_refill"] = now

            if bucket["tokens"] >= 1.0:
                bucket["tokens"] -= 1.0
                return True
            return False

    def wait_for_token(self, host: str, timeout: float = 30.0) -> bool:
        """Block until a token is available, or timeout."""
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            if self.acquire(host):
                return True
            time.sleep(0.1)
        return False

    def get_status(self, host: str) -> dict:
        """Get current rate limit status for a host."""
        with self._lock:
            if host not in self._buckets:
                return {"host": host, "rate": self.default_rate, "available_tokens": self.default_rate}
            bucket = self._buckets[host]
            now = time.monotonic()
            elapsed = now - bucket["last_refill"]
            tokens = min(bucket["rate"], bucket["tokens"] + elapsed * bucket["rate"])
            return {
                "host": host,
                "rate": bucket["rate"],
                "available_tokens": round(tokens, 2),
                "can_request": tokens >= 1.0,
            }

    def get_all_status(self) -> list[dict]:
        """Get status for all tracked hosts."""
        return [self.get_status(host) for host in self._buckets]


# Global rate limiter instance
_global_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter."""
    return _global_limiter
