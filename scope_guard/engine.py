"""
Scope-Guard Engine — pre-execution boundary enforcement.

Every request passes through ScopeGuard before execution.
No bypass possible — enforced at tool boundary level.
"""

import re
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse
from collections import defaultdict


@dataclass
class ScopeDefinition:
    """Single program's scope definition."""
    program: str
    active: bool = True
    in_scope_domains: list[str] = field(default_factory=list)
    in_scope_ips: list[str] = field(default_factory=list)
    excluded_domains: list[str] = field(default_factory=list)
    allowed_actions: list[str] = field(default_factory=lambda: [
        "recon", "scanning", "fuzzing", "injection_testing",
        "auth_testing", "graphql_testing",
    ])
    restricted_actions: list[str] = field(default_factory=lambda: [
        "dos_testing", "social_engineering", "physical_testing",
    ])
    approval_required_actions: list[str] = field(default_factory=lambda: [
        "destructive_exploit", "data_exfiltration_test",
    ])
    rate_limit_per_sec: float = 5.0
    max_concurrent_scans: int = 1
    special_instructions: str = ""


class ScopeGuard:
    """
    Pre-execution boundary enforcement.

    Usage:
        guard = ScopeGuard()
        guard.load_program(hackerone_scope_dict)
        result = guard.check("https://target.com/api", "scanning", "session-123")
        if result.passed:
            make_request()
    """

    def __init__(self):
        self._scopes: dict[str, ScopeDefinition] = {}
        self._request_counts: dict[str, list[float]] = defaultdict(list)  # host -> [timestamps]
        self._violation_count = 0
        self._last_violation: Optional[dict] = None

    def load_program(self, scope_dict: dict) -> str:
        """Load a program scope. Returns program identifier."""
        program = scope_dict.get("program", "unknown")
        in_scope = scope_dict.get("in_scope", {})
        test_types = scope_dict.get("test_types", {})
        rate_limits = scope_dict.get("rate_limits", {})

        # Default values for the scope definition
        _default_allowed = [
            "recon", "scanning", "fuzzing", "injection_testing",
            "auth_testing", "graphql_testing",
        ]
        _default_restricted = ["dos_testing", "social_engineering", "physical_testing"]
        _default_approval = ["destructive_exploit", "data_exfiltration_test"]

        definition = ScopeDefinition(
            program=program,
            active=scope_dict.get("active", True),
            in_scope_domains=in_scope.get("domains", []),
            in_scope_ips=in_scope.get("ips", []),
            excluded_domains=in_scope.get("exclude", []),
            allowed_actions=test_types.get("allowed", _default_allowed),
            restricted_actions=test_types.get("restricted", _default_restricted),
            approval_required_actions=test_types.get("approval_required", _default_approval),
            rate_limit_per_sec=rate_limits.get("requests_per_second", 5.0),
            max_concurrent_scans=rate_limits.get("concurrent_scans", 1),
            special_instructions=scope_dict.get("special_instructions", ""),
        )

        self._scopes[program] = definition
        return program

    def remove_program(self, program: str) -> bool:
        """Remove a program scope."""
        if program in self._scopes:
            del self._scopes[program]
            return True
        return False

    def check(
        self,
        url: str,
        action_type: str,
        session_id: str = "",
        approved_actions: Optional[list[str]] = None,
    ) -> dict:
        """
        Check if a request is in scope. Returns result dict.

        Required before EVERY network request.
        """
        # Parse URL
        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
        except Exception:
            return self._fail("parse_error", f"Cannot parse URL: {url}")

        if not hostname:
            return self._fail("no_hostname", "No hostname in URL")

        # Find matching scope
        matched_scope = None
        matched_rule = ""

        for scope_def in self._scopes.values():
            if not scope_def.active:
                continue

            # Domain match
            domain_match = False
            for pattern in scope_def.in_scope_domains:
                if self._domain_matches(hostname, pattern):
                    domain_match = True
                    matched_rule = f"in_scope_domain: {pattern}"
                    break

            # IP match
            if not domain_match:
                for ip_pattern in scope_def.in_scope_ips:
                    if hostname == ip_pattern:
                        domain_match = True
                        matched_rule = f"in_scope_ip: {ip_pattern}"
                        break

            if not domain_match:
                continue

            # Check exclusions
            for excluded in scope_def.excluded_domains:
                if self._domain_matches(hostname, excluded):
                    self._record_violation(url, f"excluded: {excluded}", session_id)
                    return self._fail("excluded", f"{hostname} is explicitly excluded ({excluded})")

            # Check restricted actions (NEVER allowed)
            if action_type in scope_def.restricted_actions:
                self._record_violation(url, f"restricted_action: {action_type}", session_id)
                return self._fail(
                    "restricted_action",
                    f"Action '{action_type}' is permanently restricted",
                )

            # Check approval required
            if action_type in scope_def.approval_required_actions:
                approved = approved_actions and action_type in approved_actions
                if not approved:
                    return {
                        "passed": True,
                        "requires_approval": True,
                        "reason": f"Action '{action_type}' requires human approval",
                        "matched_rule": matched_rule,
                        "action_type": action_type,
                    }

            # Check rate limits
            if not self._check_rate_limit(hostname, scope_def.rate_limit_per_sec):
                return self._fail(
                    "rate_limited",
                    f"Rate limit exceeded for {hostname} ({scope_def.rate_limit_per_sec}/s)",
                )

            matched_scope = scope_def
            break

        if matched_scope is None:
            self._record_violation(url, "no_scope_match", session_id)
            return self._fail("no_scope_match", f"{hostname} does not match any program scope")

        # Log the request
        self._record_request(hostname)

        return {
            "passed": True,
            "requires_approval": False,
            "reason": f"In scope: {matched_rule}",
            "matched_rule": matched_rule,
            "program": matched_scope.program,
            "session_id": session_id,
        }

    def check_redirect(self, original_url: str, redirect_url: str, **kwargs) -> dict:
        """Re-check scope after a redirect."""
        orig_host = urlparse(original_url).hostname or ""
        redir_host = urlparse(redirect_url).hostname or ""

        if orig_host == redir_host:
            return {"passed": True, "reason": "Same host after redirect"}

        # Different host — full re-check
        return self.check(redirect_url, **kwargs)

    def get_active_scopes(self) -> list[str]:
        """List active program names."""
        return [s.program for s in self._scopes.values() if s.active]

    def get_violation_stats(self) -> dict:
        """Get scope violation statistics."""
        return {
            "total_violations": self._violation_count,
            "last_violation": self._last_violation,
        }

    def _record_request(self, host: str) -> None:
        """Record a request timestamp for rate limiting."""
        now = time.monotonic()
        self._request_counts[host].append(now)
        # Keep only recent timestamps (last 60 seconds)
        cutoff = now - 60
        self._request_counts[host] = [t for t in self._request_counts[host] if t > cutoff]

    def _check_rate_limit(self, host: str, rate: float) -> bool:
        """Check if we're within rate limits for this host."""
        now = time.monotonic()
        cutoff = now - 1.0  # Last 1 second
        recent = sum(1 for t in self._request_counts.get(host, []) if t > cutoff)
        return recent < rate

    def _record_violation(self, url: str, reason: str, session_id: str) -> None:
        """Record a scope violation."""
        self._violation_count += 1
        self._last_violation = {
            "url": url,
            "reason": reason,
            "session_id": session_id,
            "timestamp": time.time(),
        }

    @staticmethod
    def _domain_matches(hostname: str, pattern: str) -> bool:
        """Match hostname against a domain pattern with wildcard."""
        hostname = hostname.lower().strip()
        pattern = pattern.lower().strip()

        if pattern.startswith("*."):
            suffix = pattern[2:]
            return hostname == suffix or hostname.endswith("." + suffix)
        return hostname == pattern

    @staticmethod
    def _fail(reason_code: str, message: str) -> dict:
        return {
            "passed": False,
            "requires_approval": False,
            "reason": message,
            "reason_code": reason_code,
        }
