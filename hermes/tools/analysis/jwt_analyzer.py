"""
JWT analyzer — detect algorithm confusion, weak signing, token weaknesses.
"""

import base64
import json
from hermes.tools.registry import tool, ToolCategory


@tool(
    name="analyze_jwt",
    category=ToolCategory.ANALYSIS,
    agent="artemis",
    description="Analyze JWT tokens for algorithm confusion, weak keys, and misconfigurations",
    tags=["analysis", "jwt", "auth", "token"],
)
def analyze_jwt(
    tokens: list[str],
) -> dict:
    """
    Analyze JWT tokens for weaknesses.

    Checks:
    - Algorithm: 'none' attack potential if server accepts it
    - Weak algorithms: HS256 with known secrets
    - Expiration: missing or extremely long expiry
    - Sensitive claims: PII in payload

    Args:
        tokens: List of JWT token strings

    Returns:
        dict with analysis per token, vulnerability flags
    """
    results = []
    vulnerabilities = []

    for token in tokens:
        parts = token.split(".")
        if len(parts) != 3:
            results.append({"token_preview": token[:20] + "...", "valid_jwt": False})
            continue

        header_b64, payload_b64, signature = parts

        # Decode header
        try:
            header_str = base64.urlsafe_b64decode(header_b64 + "=" * (-len(header_b64) % 4))
            header = json.loads(header_str)
        except Exception:
            header = {}

        # Decode payload
        try:
            payload_str = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4))
            payload = json.loads(payload_str)
        except Exception:
            payload = {}

        alg = header.get("alg", "unknown")
        issues = []

        # Algorithm checks
        if alg == "none":
            issues.append("ALG_NONE: Server may accept unsigned tokens")
            vulnerabilities.append("JWT Algorithm: none (unsigned token acceptance)")

        if alg == "HS256":
            issues.append("HS256_SYMMETRIC: Symmetric key — check for weak secret")

        if alg == "HS256" and "RS256" not in issues:
            issues.append("ALG_CONFUSION: If server uses RSA but accepts HS256, attack possible")

        # Expiration check
        exp = payload.get("exp")
        if exp:
            import time
            if exp < time.time():
                issues.append("EXPIRED: Token has expired")
            elif exp - time.time() > 365 * 24 * 3600:
                issues.append("LONG_EXPIRY: Token valid for >1 year")
        else:
            issues.append("NO_EXPIRY: Token has no expiration claim")

        # Sensitive data in payload
        sensitive_keys = []
        for key in payload:
            if any(s in key.lower() for s in ["password", "secret", "ssn", "credit", "card", "cvv"]):
                sensitive_keys.append(key)
        if sensitive_keys:
            issues.append(f"SENSITIVE_DATA: {', '.join(sensitive_keys)} in JWT payload")

        # Check issuer
        if "iss" not in payload:
            issues.append("NO_ISSUER: Missing issuer claim")

        # Missing audience
        if "aud" not in payload:
            issues.append("NO_AUDIENCE: Missing audience claim — token may be reusable across services")

        results.append({
            "token_preview": token[:20] + "...",
            "valid_jwt": True,
            "algorithm": alg,
            "header": header,
            "payload_preview": {k: str(v)[:50] for k, v in list(payload.items())[:5]},
            "issues": issues,
            "issue_count": len(issues),
            "risk": "HIGH" if len(issues) >= 3 else ("MEDIUM" if len(issues) >= 1 else "LOW"),
        })

    return {
        "tokens_analyzed": len(tokens),
        "total_issues": sum(len(r.get("issues", [])) for r in results),
        "results": results,
        "vulnerabilities_found": vulnerabilities,
    }
