"""
MCP Python handlers — implements Python-based MCP tools.

These handlers are called directly (no subprocess) for tools that
require API keys, complex logic, or Python-native processing.
"""

import json
import urllib.request
import urllib.parse
from typing import Optional


def github_dork(query: str, token: str = "", org: str = "") -> dict:
    """
    Search GitHub for leaked secrets, configs, credentials.

    Args:
        query: Search query (e.g., "org:target password OR secret OR key")
        token: GitHub personal access token (optional, increases rate limit)
        org: Target organization name
    """
    if org and not query:
        query = f"org:{org} password OR secret OR key OR token OR credential"

    encoded = urllib.parse.quote(query)
    url = f"https://api.github.com/search/code?q={encoded}&per_page=30"

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            items = data.get("items", [])
            return {
                "total_results": data.get("total_count", 0),
                "results": [
                    {
                        "repo": item.get("repository", {}).get("full_name", ""),
                        "path": item.get("path", ""),
                        "url": item.get("html_url", ""),
                    }
                    for item in items[:10]
                ],
                "query": query,
            }
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return {"error": "GitHub API rate limit exceeded. Use a token.", "results": []}
        return {"error": f"GitHub API error: {e.code}", "results": []}
    except Exception as e:
        return {"error": str(e), "results": []}


def shodan_query(query: str, api_key: str = "") -> dict:
    """
    Query Shodan for exposed services (passive only).

    Args:
        query: Shodan search query (e.g., "org:Target Inc")
        api_key: Shodan API key
    """
    if not api_key:
        return {"error": "Shodan API key required", "results": []}

    encoded = urllib.parse.quote(query)
    url = f"https://api.shodan.io/shodan/host/search?key={api_key}&query={encoded}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            matches = data.get("matches", [])
            return {
                "total": data.get("total", 0),
                "results": [
                    {
                        "ip": m.get("ip_str", ""),
                        "port": m.get("port", 0),
                        "org": m.get("org", ""),
                        "hostnames": m.get("hostnames", []),
                        "domains": m.get("domains", []),
                    }
                    for m in matches[:20]
                ],
                "query": query,
            }
    except Exception as e:
        return {"error": str(e), "results": []}


def censys_query(query: str, api_id: str = "", api_secret: str = "") -> dict:
    """
    Query Censys for certificate and host data.

    Args:
        query: Censys search query
        api_id: Censys API ID
        api_secret: Censys API secret
    """
    if not api_id or not api_secret:
        return {"error": "Censys API credentials required", "results": []}

    url = "https://search.censys.io/api/v2/hosts/search"
    import base64
    auth = base64.b64encode(f"{api_id}:{api_secret}".encode()).decode()

    data = json.dumps({"q": query, "per_page": 20}).encode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            hits = result.get("result", {}).get("hits", [])
            return {
                "total": result.get("result", {}).get("total", 0),
                "results": [
                    {"ip": h.get("ip", ""), "services": [s.get("service_name", "") for s in h.get("services", [])]}
                    for h in hits[:10]
                ],
            }
    except Exception as e:
        return {"error": str(e), "results": []}


def crt_sh_query(domain: str) -> dict:
    """
    Query crt.sh for SSL certificate transparency logs.

    Args:
        domain: Domain to search (e.g., "%.example.com")
    """
    url = f"https://crt.sh/?q={urllib.parse.quote(domain)}&output=json"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CAPY-BugHunter/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            subdomains = set()
            for entry in data:
                names = entry.get("name_value", "").split("\n")
                for name in names:
                    name = name.strip().lower()
                    if name and not name.startswith("*"):
                        subdomains.add(name)

            return {
                "domain": domain,
                "subdomains": sorted(subdomains),
                "count": len(subdomains),
                "source": "crt.sh",
            }
    except Exception as e:
        return {"error": str(e), "subdomains": [], "count": 0}
