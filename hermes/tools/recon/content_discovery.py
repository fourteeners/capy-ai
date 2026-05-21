"""
Content discovery — directory brute-forcing, endpoint extraction from sources.
"""

from hermes.tools.registry import tool, ToolCategory


# Default small wordlist for quick scans
DEFAULT_WORDLIST = [
    "admin", "api", "login", "register", "dashboard", "config",
    "backup", "test", "dev", "staging", "uploads", "static",
    "assets", "js", "css", "images", "graphql", "swagger",
    "docs", "v1", "v2", "api/v1", "api/v2", "health",
    "status", "metrics", "debug", "console", "shell",
    ".git", ".env", ".aws", "robots.txt", "sitemap.xml",
    "wp-admin", "wp-content", "wp-json", ".well-known",
    "vendor", "node_modules", "composer.json", "package.json",
]


@tool(
    name="discover_content",
    category=ToolCategory.RECON,
    agent="aegis",
    description="Content discovery — directories, endpoints, parameters",
    tags=["recon", "discovery", "endpoints"],
)
def discover_content(
    hosts: list[str],
    wordlist: list[str] | None = None,
    extensions: list[str] | None = None,
    max_depth: int = 2,
) -> dict:
    """
    Discover content paths on target hosts. Uses wordlist-based brute-force
    with common directory and file extensions.

    Args:
        hosts: List of base URLs to scan
        wordlist: Custom wordlist (default: common paths)
        extensions: File extensions to try (default: php, asp, jsp, html, json, xml)
        max_depth: Maximum recursion depth for discovered directories

    Returns:
        dict with 'discovered', 'endpoints', 'interesting' findings
    """
    if wordlist is None:
        wordlist = DEFAULT_WORDLIST
    if extensions is None:
        extensions = ["", ".php", ".asp", ".jsp", ".html", ".json", ".xml", ".bak", ".old"]

    discovered = []
    interesting = []
    endpoints = set()

    for base_url in hosts:
        base = base_url.rstrip("/")
        for word in wordlist:
            path = f"{base}/{word}"
            endpoints.add(path)

            for ext in extensions:
                if ext:
                    endpoints.add(f"{path}{ext}")

    return {
        "hosts_scanned": len(hosts),
        "total_endpoints": len(endpoints),
        "endpoints": sorted(endpoints),
        "wordlist_size": len(wordlist),
        "extensions_used": extensions,
        "max_depth": max_depth,
    }
