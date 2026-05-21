"""
Secret scanner — detect exposed credentials, tokens, and API keys in text content.
"""

import math
import re
from hermes.tools.registry import tool, ToolCategory


# High-confidence secret patterns
SECRET_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("AWS Access Key", re.compile(r"(?:AKIA|ASIA)[0-9A-Z]{16}"), "AWS IAM"),
    ("AWS Secret Key", re.compile(r"(?:(?:aws|access)[_-]?secret)[^\w]*[=:][^\w]*[\'\"`]([A-Za-z0-9/+]{40})[\'\"`]", re.I), "AWS IAM"),
    ("GitHub Token", re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[0-9a-zA-Z]{36}"), "GitHub"),
    ("GitHub Classic Token", re.compile(r"[0-9a-f]{40}"), "GitHub (low confidence)"),
    ("Stripe Live Key", re.compile(r"sk_live_[0-9a-zA-Z]{24,}"), "Stripe"),
    ("Stripe Test Key", re.compile(r"sk_test_[0-9a-zA-Z]{24,}"), "Stripe"),
    ("Google API Key", re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "Google Cloud"),
    ("Google OAuth", re.compile(r"ya29\.[0-9A-Za-z\-_]+"), "Google OAuth"),
    ("JWT Token", re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"), "Authentication"),
    ("Private Key Header", re.compile(r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----"), "Cryptography"),
    ("Slack Token", re.compile(r"xox[baprs]-[0-9a-zA-Z\-]{10,}"), "Slack"),
    ("Heroku API Key", re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"), "Heroku"),
    ("Generic API Key", re.compile(r"(?:api[_-]?key|apikey|api_secret|access_key)\s*[=:]\s*['\"`]([a-zA-Z0-9._\-]{16,})['\"`]", re.I), "Generic"),
    ("Password in Code", re.compile(r"(?:password|passwd|pwd)\s*[=:]\s*['\"`]([^'\"`\s]{4,})['\"`]", re.I), "Credentials"),
    ("Database URL", re.compile(r"(?:jdbc|mysql|postgres|mongodb|redis)://[^/\s]+@", re.I), "Database"),
    ("Private IP", re.compile(r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}"), "Internal Network"),
    ("Internal URL", re.compile(r"(?:staging|dev|internal|admin)\.(?:[a-z0-9-]+\.)+[a-z]{2,}", re.I), "Internal Infrastructure"),
]


def _entropy(data: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not data:
        return 0.0
    counts = {}
    for c in data:
        counts[c] = counts.get(c, 0) + 1
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


@tool(
    name="scan_secrets",
    category=ToolCategory.RECON,
    agent="aegis",
    description="Scan text content for exposed secrets, tokens, and credentials",
    tags=["recon", "secrets", "credentials", "security"],
)
def scan_secrets(
    content_items: list[dict],  # [{"source": "...", "content": "...", "type": "js|html|text|config"}, ...]
    validate: bool = False,
) -> dict:
    """
    Scan content for exposed secrets, tokens, and credentials.

    Args:
        content_items: List of dicts with 'source', 'content', 'type'
        validate: Try to validate secrets (requires network — use carefully)

    Returns:
        dict with 'findings' categorized by confidence level
    """
    high_confidence = []
    medium_confidence = []
    low_confidence = []

    for item in content_items:
        source = item.get("source", "unknown")
        content = item.get("content", "")
        content_type = item.get("type", "text")

        for name, pattern, category in SECRET_PATTERNS:
            for match in pattern.finditer(content):
                value = match.group(0)
                ent = _entropy(value)

                # Confidence scoring
                confidence = "low"

                if name in ("AWS Access Key", "Stripe Live Key", "GitHub Token",
                           "Private Key Header", "Google API Key", "JWT Token"):
                    confidence = "high"
                elif name in ("GitHub Classic Token",):
                    # High entropy = higher confidence for generic patterns
                    confidence = "high" if ent > 3.5 else "medium"
                elif ent > 4.0 and len(value) > 20:
                    confidence = "high"
                elif ent > 3.0:
                    confidence = "medium"
                else:
                    confidence = "low"

                # Truncate value for safety
                preview = value[:12] + "..." if len(value) > 15 else value[:6] + "..."

                finding = {
                    "source": source,
                    "type": name,
                    "category": category,
                    "preview": preview,
                    "entropy": round(ent, 2),
                    "confidence": confidence,
                }

                if confidence == "high":
                    high_confidence.append(finding)
                elif confidence == "medium":
                    medium_confidence.append(finding)
                else:
                    low_confidence.append(finding)

    return {
        "files_scanned": len(content_items),
        "total_findings": len(high_confidence) + len(medium_confidence) + len(low_confidence),
        "high_confidence": high_confidence,
        "medium_confidence": medium_confidence,
        "low_confidence": low_confidence,
        "validation_attempted": validate,
    }
