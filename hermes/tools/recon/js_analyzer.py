"""
JavaScript analysis — extract endpoints, detect libraries, find source maps.
"""

import re
from hermes.tools.registry import tool, ToolCategory


# Endpoint patterns in JS
ENDPOINT_PATTERNS = [
    re.compile(r"['\"`](https?://[a-zA-Z0-9._/\-?=&:%]+)['\"`]", re.IGNORECASE),
    re.compile(r"['\"`](/api/[a-zA-Z0-9._/\-?=&:%]*)['\"`]", re.IGNORECASE),
    re.compile(r"['\"`](/graphql[^'\"`]*)['\"`]", re.IGNORECASE),
    re.compile(r"['\"`](/v\d+/[a-zA-Z0-9._/\-?=&:%]*)['\"`]", re.IGNORECASE),
    re.compile(r"fetch\(\s*['\"`]([^'\"`]+)['\"`]", re.IGNORECASE),
    re.compile(r"axios\.(?:get|post|put|delete|patch)\(\s*['\"`]([^'\"`]+)['\"`]", re.IGNORECASE),
    re.compile(r"\.open\(\s*['\"`](GET|POST|PUT|DELETE|PATCH)['\"`]\s*,\s*['\"`]([^'\"`]+)['\"`]", re.IGNORECASE),
]

# Library detection patterns
LIBRARY_PATTERNS = {
    "React": re.compile(r"React(?:DOM)?\s*(?:\.|\[)"),
    "Vue": re.compile(r"new\s+Vue\s*\("),
    "Angular": re.compile(r"angular\.module\s*\("),
    "jQuery": re.compile(r"jquery[.\-]?\d", re.IGNORECASE),
    "Axios": re.compile(r"axios\.(?:get|post|put|delete)", re.IGNORECASE),
    "Lodash": re.compile(r"_\.[a-z]+\(", re.IGNORECASE),
    "D3": re.compile(r"d3\.\w+\("),
    "Bootstrap": re.compile(r"bootstrap[.\-]", re.IGNORECASE),
}

# Source map pattern
SOURCE_MAP_RE = re.compile(r"//#\s*sourceMappingURL=(.+\.map)")

# Sensitive path patterns
SENSITIVE_PATHS = [
    re.compile(r"(api[_-]?key|apikey|secret|token|password|auth)\s*[:=]\s*['\"`]([^'\"`]{8,})['\"`]", re.IGNORECASE),
    re.compile(r"['\"`](AKIA[0-9A-Z]{16})['\"`]"),  # AWS Access Key
    re.compile(r"['\"`](sk-(?:live|test)_[0-9a-zA-Z]{24,})['\"`]"),  # Stripe
    re.compile(r"['\"`](gh[pousr]_[0-9a-zA-Z]{36})['\"`]"),  # GitHub token
    re.compile(r"['\"`](ya29\.[0-9A-Za-z\-_]+)['\"`]"),  # Google OAuth
    re.compile(r"['\"`](firebase[^'\"`]{20,})['\"`]", re.IGNORECASE),
]


@tool(
    name="analyze_js",
    category=ToolCategory.RECON,
    agent="aegis",
    description="JavaScript analysis — endpoints, libraries, secrets, source maps",
    tags=["recon", "js", "analysis", "secrets"],
)
def analyze_js(
    js_files: list[dict],  # [{"url": "...", "content": "..."}, ...]
) -> dict:
    """
    Analyze JavaScript files for endpoints, libraries, secrets, and source maps.

    Args:
        js_files: List of dicts with 'url' and 'content' keys

    Returns:
        dict with 'endpoints', 'libraries', 'secrets', 'source_maps'
    """
    all_endpoints = set()
    all_libraries = {}
    all_secrets = []
    source_maps = []

    for js_file in js_files:
        url = js_file.get("url", "unknown")
        content = js_file.get("content", "")

        # Extract endpoints
        for pattern in ENDPOINT_PATTERNS:
            for match in pattern.finditer(content):
                if pattern is ENDPOINT_PATTERNS[6]:  # XMLHttpRequest pattern
                    endpoint = match.group(2)
                else:
                    endpoint = match.group(1) if pattern is not ENDPOINT_PATTERNS[6] else match.group(1)
                all_endpoints.add(endpoint)

        # Detect libraries
        for lib_name, pattern in LIBRARY_PATTERNS.items():
            if pattern.search(content):
                all_libraries[lib_name] = all_libraries.get(lib_name, 0) + 1

        # Find source maps
        for match in SOURCE_MAP_RE.finditer(content):
            source_maps.append({"file": url, "source_map": match.group(1)})

        # Scan for secrets
        for pattern in SENSITIVE_PATHS:
            for match in pattern.finditer(content):
                secret_value = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                # Truncate for safety (don't log full secrets)
                truncated = secret_value[:8] + "..." if len(secret_value) > 11 else secret_value[:4] + "..."
                all_secrets.append({
                    "file": url,
                    "pattern": pattern.pattern[:60],
                    "preview": truncated,
                })

    return {
        "files_analyzed": len(js_files),
        "endpoints": sorted(all_endpoints),
        "endpoint_count": len(all_endpoints),
        "libraries": all_libraries,
        "source_maps": source_maps,
        "potential_secrets": all_secrets,
        "secret_count": len(all_secrets),
    }
