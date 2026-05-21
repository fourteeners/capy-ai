"""
Connectivity testing — verify target is reachable before scanning.
"""

import socket
from hermes.tools.registry import tool, ToolCategory


@tool(
    name="verify_connectivity",
    category=ToolCategory.UTILITY,
    agent="aegis",
    description="Verify target connectivity before starting operations",
    tags=["utility", "connectivity", "preflight"],
    requires_scope_check=False,
)
def verify_connectivity(
    hosts: list[str],
    ports: list[int] | None = None,
    timeout: float = 5.0,
) -> dict:
    """
    Quick pre-flight check: are targets reachable?

    Args:
        hosts: List of hostnames or IPs
        ports: Ports to check (default: 80, 443)
        timeout: Per-host timeout in seconds

    Returns:
        dict with 'reachable', 'unreachable', 'reachable_count'
    """
    if ports is None:
        ports = [80, 443]

    reachable = []
    unreachable = []

    for host in hosts:
        host_reachable = False
        for port in ports:
            try:
                sock = socket.create_connection((host, port), timeout=timeout)
                sock.close()
                reachable.append({"host": host, "port": port})
                host_reachable = True
                break
            except (socket.timeout, ConnectionRefusedError, OSError):
                continue

        if not host_reachable:
            unreachable.append(host)

    return {
        "total": len(hosts),
        "reachable_count": len(set(r["host"] for r in reachable)),
        "unreachable_count": len(set(unreachable)),
        "reachable": reachable,
        "unreachable": unreachable,
        "ports_checked": ports,
    }
