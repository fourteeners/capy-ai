"""
Rate-limit-aware HTTP client with retry logic and scope integration.

Replaces raw subprocess calls to httpx with a native Python HTTP client
that respects rate limits, implements exponential backoff, and integrates
with Scope-Guard for pre-request validation.
"""

import time
import random
import urllib.request
import urllib.error
from typing import Optional


class HTTPClient:
    """
    Rate-limit-aware HTTP client with retry logic.

    Usage:
        client = HTTPClient(rate_limiter=limiter, scope_guard=guard)
        resp = client.get("https://target.com/api")
    """

    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    BACKOFF_BASE = 1.0
    BACKOFF_MAX = 32.0
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    ]

    def __init__(self, rate_limiter=None, scope_guard=None, session_id: str = ""):
        self._rate_limiter = rate_limiter
        self._scope_guard = scope_guard
        self._session_id = session_id
        self._stats = {"requests": 0, "retries": 0, "errors": 0, "bytes_sent": 0, "bytes_received": 0}

    def get(self, url: str, headers: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """HTTP GET with rate limiting, retry, and scope check."""
        return self._request("GET", url, headers=headers, timeout=timeout)

    def post(self, url: str, data: bytes = b"", headers: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """HTTP POST with rate limiting, retry, and scope check."""
        return self._request("POST", url, data=data, headers=headers, timeout=timeout)

    def head(self, url: str, headers: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """HTTP HEAD with rate limiting and retry."""
        return self._request("HEAD", url, headers=headers, timeout=timeout)

    def _request(self, method: str, url: str, data: bytes = b"", headers: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
        """Core request with rate limiting, retry, and scope enforcement."""
        # Scope check
        if self._scope_guard:
            scope_result = self._scope_guard.check(url, "recon", self._session_id)
            if not scope_result.get("passed"):
                return {
                    "success": False,
                    "status_code": 0,
                    "error": f"Scope violation: {scope_result.get('reason')}",
                    "scope_blocked": True,
                }

        # Rate limit
        if self._rate_limiter:
            from urllib.parse import urlparse
            host = urlparse(url).hostname or "unknown"
            if not self._rate_limiter.wait_for_token(host, timeout=10):
                return {
                    "success": False,
                    "status_code": 0,
                    "error": "Rate limit exceeded",
                    "rate_limited": True,
                }

        # Random User-Agent
        req_headers = {"User-Agent": random.choice(self.USER_AGENTS)}
        if headers:
            req_headers.update(headers)

        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    body = resp.read()
                    resp_headers = dict(resp.headers)

                    self._stats["requests"] += 1
                    self._stats["bytes_received"] += len(body)

                    return {
                        "success": True,
                        "status_code": resp.status,
                        "headers": resp_headers,
                        "body": body,
                        "body_str": body.decode("utf-8", errors="replace"),
                        "url": url,
                    }

            except urllib.error.HTTPError as e:
                self._stats["requests"] += 1
                status = e.code

                # Rate limited — back off and retry
                if status == 429:
                    retry_after = int(e.headers.get("Retry-After", self.BACKOFF_BASE * (2 ** attempt)))
                    self._stats["retries"] += 1
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(min(retry_after, self.BACKOFF_MAX))
                        continue

                # WAF block — don't retry
                if status in (403, 406):
                    body = e.read().decode("utf-8", errors="replace")
                    return {
                        "success": False,
                        "status_code": status,
                        "error": f"Blocked (WAF): HTTP {status}",
                        "waf_blocked": True,
                        "body": body,
                    }

                last_error = {"success": False, "status_code": status, "error": str(e)}
                break

            except urllib.error.URLError as e:
                self._stats["retries"] += 1
                last_error = {"success": False, "status_code": 0, "error": str(e)}
                if attempt < self.MAX_RETRIES - 1:
                    backoff = min(self.BACKOFF_BASE * (2 ** attempt), self.BACKOFF_MAX)
                    time.sleep(backoff)
                    continue
                break

            except Exception as e:
                self._stats["errors"] += 1
                last_error = {"success": False, "status_code": 0, "error": str(e)}
                break

        self._stats["errors"] += 1
        return last_error or {"success": False, "status_code": 0, "error": "Unknown error"}

    def probe(self, url: str, timeout: int = 10) -> dict:
        """
        Lightweight probe — HEAD request, just check if endpoint is alive.
        Returns minimal info: status, headers, technologies detected.
        """
        result = self.head(url, timeout=timeout)
        if not result["success"]:
            return result

        # Quick tech fingerprint from headers
        tech_hints = []
        headers = {k.lower(): v for k, v in result.get("headers", {}).items()}
        if "cf-ray" in headers:
            tech_hints.append("Cloudflare")
        if "x-powered-by" in headers:
            tech_hints.append(headers["x-powered-by"])
        if "server" in headers:
            tech_hints.append(headers["server"])

        return {
            "success": True,
            "status_code": result["status_code"],
            "technologies": tech_hints,
            "url": url,
        }

    def get_stats(self) -> dict:
        """Get client usage statistics."""
        return dict(self._stats)

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        self._stats = {"requests": 0, "retries": 0, "errors": 0, "bytes_sent": 0, "bytes_received": 0}
