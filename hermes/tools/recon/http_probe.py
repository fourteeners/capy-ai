"""
HTTP probing — checks which hosts have live web services and fingerprints technology.
"""

import subprocess
from typing import Optional

from hermes.tools.registry import tool, ToolCategory


@tool(
    name="probe_http",
    category=ToolCategory.RECON,
    agent="aegis",
    description="HTTP/HTTPS probing with httpx — live host detection",
    tags=["recon", "http", "probe"],
)
def probe_http(
    hosts: list[str],
    ports: Optional[list[int]] = None,
    timeout: int = 120,
) -> dict:
    """
    Probe hosts for live HTTP/HTTPS services using httpx.

    Args:
        hosts: List of hostnames or IPs to probe
        ports: Custom port list (default: 80, 443, 8080, 8443, 3000, 5000, 8000)
        timeout: Timeout for httpx in seconds

    Returns:
        dict with 'live_hosts', 'status_codes', 'technologies', 'tls_info'
    """
    if ports is None:
        ports = [80, 443, 8080, 8443, 3000, 5000, 8000]

    # Write hosts to temp file for httpx
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for host in hosts:
            f.write(host + "\n")
        hosts_file = f.name

    live_hosts = []

    try:
        # httpx with technology detection
        cmd = [
            "httpx",
            "-l", hosts_file,
            "-silent",
            "-json",
            "-tech-detect",
            "-title",
            "-status-code",
            "-content-length",
            "-websocket",
            "-follow-redirects",
            "-timeout", str(timeout),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    import json
                    entry = json.loads(line)
                    live_hosts.append({
                        "url": entry.get("url", ""),
                        "host": entry.get("host", ""),
                        "status_code": entry.get("status_code"),
                        "title": entry.get("title", ""),
                        "technologies": entry.get("tech", []),
                        "websocket": entry.get("websocket", False),
                        "content_length": entry.get("content_length"),
                        "tls": entry.get("tls", {}),
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    finally:
        os.unlink(hosts_file)

    # Categorize by status
    status_groups = {}
    tech_count = {}
    for host in live_hosts:
        code = host.get("status_code", 0)
        key = f"{code // 100}xx"
        status_groups[key] = status_groups.get(key, 0) + 1
        for tech in host.get("technologies", []):
            tech_count[tech] = tech_count.get(tech, 0) + 1

    return {
        "total_probed": len(hosts),
        "live_count": len(live_hosts),
        "live_hosts": live_hosts,
        "status_distribution": status_groups,
        "technology_distribution": tech_count,
    }
