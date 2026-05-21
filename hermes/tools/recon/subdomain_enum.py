"""
Subdomain enumeration — orchestrates subfinder, amass, assetfinder, chaos.

Non-intrusive by default. Uses passive sources only unless active=True.
Results deduplicated and filtered by scope.
"""

import subprocess
import re
from typing import Optional

from hermes.tools.registry import tool, ToolCategory


DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)


def _run_tool(cmd: list[str], timeout: int = 120) -> list[str]:
    """Run a CLI tool and return stdout lines. Returns empty list on failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def _deduplicate(domains: list[str]) -> list[str]:
    """Deduplicate and sort domain list."""
    return sorted(set(d.lower().strip() for d in domains if d.strip()))


def _validate_domain(domain: str) -> bool:
    """Basic domain format validation."""
    return bool(DOMAIN_RE.match(domain))


def _filter_in_scope(domains: list[str], scope_domains: list[str]) -> list[str]:
    """Filter subdomains that match scope wildcards."""
    if not scope_domains:
        return domains

    result = []
    for domain in domains:
        for scope in scope_domains:
            if scope.startswith("*."):
                suffix = scope[2:]
                if domain == suffix or domain.endswith("." + suffix):
                    result.append(domain)
                    break
            elif domain == scope:
                result.append(domain)
                break
    return result


@tool(
    name="enumerate_subdomains",
    category=ToolCategory.RECON,
    agent="aegis",
    description="Multi-tool passive subdomain enumeration",
    tags=["recon", "subdomain", "enum", "passive"],
)
def enumerate_subdomains(
    domain: str,
    passive: bool = True,
    scope: Optional[list[str]] = None,
    timeout: int = 300,
) -> dict:
    """
    Enumerate subdomains for a target domain using multiple tools.

    Args:
        domain: Target domain (e.g., example.com)
        passive: Use only passive sources (no direct scanning)
        scope: List of scope wildcards to filter by (e.g., ["*.example.com"])
        timeout: Total timeout in seconds

    Returns:
        dict with 'subdomains', 'count', 'sources', 'filtered' keys
    """
    all_subs: list[str] = []
    sources_used: list[str] = []

    # Passive enumeration (always run)
    # subfinder
    sf_results = _run_tool(["subfinder", "-d", domain, "-silent"], timeout=min(timeout, 120))
    all_subs.extend(sf_results)
    if sf_results:
        sources_used.append("subfinder")

    # assetfinder
    af_results = _run_tool(["assetfinder", "--subs-only", domain], timeout=min(timeout, 60))
    all_subs.extend(af_results)
    if af_results:
        sources_used.append("assetfinder")

    # crt.sh (certificate transparency)
    crt_results = _run_tool(
        ["curl", "-s", f"https://crt.sh/?q=%25.{domain}&output=json"],
        timeout=min(timeout, 30),
    )
    if crt_results:
        try:
            import json
            data = json.loads("\n".join(crt_results))
            crt_domains = []
            for entry in data:
                name = entry.get("name_value", "")
                crt_domains.extend(
                    d.strip().lower()
                    for d in name.split("\n")
                    if _validate_domain(d.strip())
                )
            all_subs.extend(crt_domains)
            sources_used.append("crt.sh")
        except (json.JSONDecodeError, KeyError):
            pass

    # Deduplicate
    unique = _deduplicate(all_subs)

    # Validate
    valid = [d for d in unique if _validate_domain(d)]

    # Filter by scope if provided
    filtered = _filter_in_scope(valid, scope) if scope else valid

    return {
        "domain": domain,
        "subdomains": filtered,
        "total_found": len(valid),
        "in_scope": len(filtered),
        "sources": sources_used,
        "passive_only": passive,
    }
