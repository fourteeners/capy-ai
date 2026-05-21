"""
DNS resolution — resolves subdomains to IPs using system resolver and dnsx.
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from hermes.tools.registry import tool, ToolCategory


def _resolve_one(domain: str) -> dict:
    """Resolve a single domain to IP addresses."""
    try:
        ips = socket.getaddrinfo(domain, None, socket.AF_INET)
        ip_list = sorted(set(addr[4][0] for addr in ips))
        return {"domain": domain, "ips": ip_list, "resolved": True, "error": None}
    except socket.gaierror as e:
        return {"domain": domain, "ips": [], "resolved": False, "error": str(e)}
    except Exception as e:
        return {"domain": domain, "ips": [], "resolved": False, "error": str(e)}


@tool(
    name="resolve_dns",
    category=ToolCategory.RECON,
    agent="aegis",
    description="DNS resolution with parallel workers",
    tags=["recon", "dns", "resolve"],
)
def resolve_dns(
    domains: list[str],
    max_workers: int = 20,
) -> dict:
    """
    Resolve list of domains to IP addresses in parallel.

    Args:
        domains: List of domains to resolve
        max_workers: Max parallel resolution threads

    Returns:
        dict with 'resolved', 'unresolved', 'ips' mapping, 'stats'
    """
    resolved = []
    unresolved = []
    ip_map = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_resolve_one, d): d for d in domains}
        for future in as_completed(futures):
            result = future.result()
            if result["resolved"]:
                resolved.append(result)
                ip_map[result["domain"]] = result["ips"]
            else:
                unresolved.append(result)

    return {
        "total": len(domains),
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "resolved": resolved,
        "unresolved": unresolved,
        "ip_map": ip_map,
    }
