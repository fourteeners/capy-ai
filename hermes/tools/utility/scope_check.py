"""
Scope verification — check URLs against program scope before any request.
"""

from hermes.tools.registry import tool, ToolCategory


@tool(
    name="check_scope",
    category=ToolCategory.UTILITY,
    agent="all",
    description="Verify URL against active program scope before making any request",
    tags=["utility", "scope", "safety"],
    requires_scope_check=False,  # This IS the scope check — no recursion
)
def check_scope(
    url: str,
    program_scopes: list[dict],
    action_type: str = "recon",
    session_id: str = "",
) -> dict:
    """
    Check if a URL is within the defined scope for a program.

    MUST be called before ANY network request. Returns PASS/BLOCK.

    Args:
        url: Full URL to check
        program_scopes: List of scope definitions for active programs
        action_type: recon, scanning, fuzzing, injection_testing, destructive_exploit
        session_id: Active hunt session ID

    Returns:
        dict with 'pass', 'reason', 'matched_rule'
    """
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
    except Exception:
        return {"pass": False, "reason": f"Cannot parse URL: {url}", "matched_rule": "parse_error"}

    if not hostname:
        return {"pass": False, "reason": "No hostname in URL", "matched_rule": "no_hostname"}

    # Check against all program scopes
    for scope_def in program_scopes:
        in_scope = scope_def.get("in_scope", {})
        domains = in_scope.get("domains", [])
        exclude = in_scope.get("exclude", [])

        # Check if hostname matches any in-scope domain
        matched = False
        for domain in domains:
            if _domain_matches(hostname, domain):
                matched = True
                break

        if not matched:
            continue  # Try next scope definition

        # Check exclusions
        for excluded in exclude:
            if _domain_matches(hostname, excluded):
                return {
                    "pass": False,
                    "reason": f"{hostname} is explicitly excluded from scope",
                    "matched_rule": f"excluded: {excluded}",
                }

        # Check test type permissions
        restricted = scope_def.get("restricted", [])
        if action_type in restricted:
            return {
                "pass": False,
                "reason": f"Action '{action_type}' is restricted for this program",
                "matched_rule": "restricted_action",
            }

        # Check if approval needed
        approval_required = scope_def.get("approval_required", [])
        if action_type in approval_required:
            return {
                "pass": True,
                "reason": f"In scope but requires human approval for '{action_type}'",
                "matched_rule": f"in_scope: {domain}",
                "requires_approval": True,
                "action_type": action_type,
            }

        return {
            "pass": True,
            "reason": f"{hostname} matches {domain}",
            "matched_rule": f"in_scope: {domain}",
            "program": scope_def.get("program", "unknown"),
            "session_id": session_id,
        }

    return {
        "pass": False,
        "reason": f"{hostname} does not match any in-scope domain",
        "matched_rule": "no_scope_match",
    }


def _domain_matches(hostname: str, pattern: str) -> bool:
    """Match hostname against a domain pattern with wildcard support."""
    hostname = hostname.lower().strip()
    pattern = pattern.lower().strip()

    if pattern.startswith("*."):
        suffix = pattern[2:]
        return hostname == suffix or hostname.endswith("." + suffix)
    return hostname == pattern
