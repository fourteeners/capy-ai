"""
Technology fingerprinting — identify web frameworks, servers, CDNs from headers and responses.
"""

import re
from hermes.tools.registry import tool, ToolCategory


# Tech fingerprint database
TECH_SIGNATURES: dict[str, dict] = {
    # Web servers
    "Nginx": {"headers": {"Server": re.compile(r"nginx", re.I)}},
    "Apache": {"headers": {"Server": re.compile(r"apache", re.I)}},
    "Cloudflare": {"headers": {"Server": re.compile(r"cloudflare", re.I), "CF-Ray": re.compile(r".")}},
    "AWS CloudFront": {"headers": {"X-Cache": re.compile(r"cloudfront", re.I)}},
    "Varnish": {"headers": {"X-Varnish": re.compile(r".")}},

    # Backend frameworks
    "Express": {"headers": {"X-Powered-By": re.compile(r"express", re.I)}},
    "Django": {"cookies": {re.compile(r"csrftoken"): re.compile(r".")}, "headers": {"X-Powered-By": re.compile(r"django", re.I)}},
    "Rails": {"headers": {"X-Powered-By": re.compile(r"phusion|rails", re.I)}},
    "Laravel": {"cookies": {re.compile(r"laravel_session"): re.compile(r".")}},
    "Spring Boot": {"headers": {"X-Application-Context": re.compile(r".")}},
    "ASP.NET": {"headers": {"X-AspNet-Version": re.compile(r"."), "X-Powered-By": re.compile(r"asp\.net", re.I)}},
    "Flask": {"headers": {"Server": re.compile(r"werkzeug", re.I)}},
    "FastAPI": {"headers": {"Server": re.compile(r"uvicorn", re.I)}},
    "Next.js": {"headers": {"X-Powered-By": re.compile(r"next\.js", re.I)}},
    "Nuxt.js": {"headers": {"X-Powered-By": re.compile(r"nuxt", re.I)}},

    # Frontend frameworks (from HTML body)
    "React": {"body": re.compile(r'react(?:\.production|\.development)?\.(?:min\.)?js|data-reactroot|__REACT_DEVTOOLS__', re.I)},
    "Vue.js": {"body": re.compile(r'vue(?:\.runtime)?\.(?:min\.)?js|data-v-[\da-f]{8}|__vue__', re.I)},
    "Angular": {"body": re.compile(r'ng-version=|angular\.module|_nghost-', re.I)},
    "jQuery": {"body": re.compile(r'jquery[.\-]?\d+\.\d+\.\d+', re.I)},
    "Bootstrap": {"body": re.compile(r'bootstrap(?:\.min)?\.(?:css|js)', re.I)},
    "Tailwind CSS": {"body": re.compile(r'tailwindcss', re.I)},

    # CDN & Infrastructure
    "Akamai": {"headers": {"X-Akamai-Transformed": re.compile(r".")}},
    "Fastly": {"headers": {"X-Served-By": re.compile(r"fastly", re.I)}},
    "Heroku": {"headers": {"Via": re.compile(r"heroku", re.I)}},
    "Vercel": {"headers": {"Server": re.compile(r"vercel", re.I)}},
    "Netlify": {"headers": {"Server": re.compile(r"netlify", re.I)}},

    # CMS
    "WordPress": {
        "headers": {"X-Powered-By": re.compile(r"wordpress", re.I)},
        "body": re.compile(r"wp-content|wp-includes|wordpress", re.I),
    },
    "Shopify": {"headers": {"X-Shopify-Stage": re.compile(r".")}},
    "Drupal": {"headers": {"X-Drupal-Cache": re.compile(r".")}},
}


@tool(
    name="fingerprint_tech",
    category=ToolCategory.RECON,
    agent="aegis",
    description="Technology stack fingerprinting from HTTP response headers and body",
    tags=["recon", "fingerprint", "tech-detect"],
)
def fingerprint_tech(
    hosts_data: list[dict],  # [{"url": "...", "headers": {...}, "body": "...", "cookies": {...}}, ...]
) -> dict:
    """
    Fingerprint technology stack from HTTP response data.

    Args:
        hosts_data: List of dicts with 'url', 'headers', 'body', 'cookies'

    Returns:
        dict with per-host technology map and aggregate statistics
    """
    results = {}
    aggregate_tech = {}

    for host in hosts_data:
        url = host.get("url", "unknown")
        headers = host.get("headers", {})
        body = host.get("body", "")
        cookies = host.get("cookies", {})

        detected = []

        for tech_name, sig in TECH_SIGNATURES.items():
            matched = False

            # Check headers
            if "headers" in sig:
                for header_name, pattern in sig["headers"].items():
                    value = headers.get(header_name, "")
                    if isinstance(value, str) and pattern.search(value):
                        matched = True
                        break

            # Check cookies
            if not matched and "cookies" in sig:
                for cookie_pattern, value_pattern in sig.get("cookies", {}).items():
                    for cookie_name in cookies:
                        if cookie_pattern.search(cookie_name):
                            matched = True
                            break

            # Check body
            if not matched and "body" in sig:
                if isinstance(sig["body"], re.Pattern):
                    if sig["body"].search(body):
                        matched = True
                elif isinstance(sig["body"], list):
                    for bp in sig["body"]:
                        if bp.search(body):
                            matched = True
                            break

            if matched:
                detected.append(tech_name)
                aggregate_tech[tech_name] = aggregate_tech.get(tech_name, 0) + 1

        results[url] = {
            "technologies": detected,
            "tech_count": len(detected),
        }

    return {
        "hosts_analyzed": len(hosts_data),
        "results": results,
        "aggregate": aggregate_tech,
        "unique_technologies": len(aggregate_tech),
    }
