"""
Report formatter — generate submission-ready vulnerability reports.
"""

from hermes.tools.registry import tool, ToolCategory


@tool(
    name="format_finding_for_submission",
    category=ToolCategory.REPORTING,
    agent="odysseus",
    description="Format a validated finding into a submission-ready vulnerability report",
    tags=["reporting", "format", "submission", "bounty"],
)
def format_finding_for_submission(
    finding: dict,
    platform: str = "hackerone",
) -> dict:
    """
    Format a validated finding into a submission-ready report.

    Args:
        finding: Dict with vulnerability_class, endpoint, description, cvss,
                evidence, reproduction_steps, impact
        platform: Target platform (hackerone, immunefi, bugcrowd, custom)

    Returns:
        dict with formattable report sections
    """
    vuln_class = finding.get("vulnerability_class", "Unknown")
    endpoint = finding.get("endpoint", "")
    cvss = finding.get("cvss", {})

    severity = cvss.get("severity", "MEDIUM")
    score = cvss.get("score", "N/A")

    # Platform-specific title formats
    title_formats = {
        "hackerone": f"[{severity}] {vuln_class} in {endpoint}",
        "immunefi": f"{vuln_class} vulnerability in {endpoint}",
        "bugcrowd": f"{severity} — {vuln_class} — {endpoint}",
        "custom": f"{severity}: {vuln_class} on {endpoint}",
    }

    title = title_formats.get(platform, title_formats["custom"])

    report = {
        "title": title,
        "platform": platform,
        "severity": severity,
        "cvss_score": score,
        "sections": {
            "summary": {
                "label": "Summary",
                "content": (
                    f"A {vuln_class} vulnerability was identified in {endpoint}. "
                    f"This could allow an attacker to {finding.get('impact_description', 'impact the system')}. "
                    f"CVSS v3.1 Score: {score} ({severity})."
                ),
            },
            "reproduction": {
                "label": "Steps to Reproduce",
                "content": finding.get("reproduction_steps", [
                    f"1. Navigate to {endpoint}",
                    "2. [Add specific reproduction steps]",
                    "3. Observe the vulnerability",
                ]),
            },
            "impact": {
                "label": "Impact",
                "content": finding.get("impact", "Describe the business and technical impact here."),
            },
            "remediation": {
                "label": "Remediation",
                "content": finding.get("remediation", "Provide specific fix recommendations."),
            },
            "evidence": {
                "label": "Supporting Evidence",
                "content": finding.get("evidence", ["Attach screenshots, request/response pairs, PoC scripts"]),
            },
        },
        "metadata": {
            "finding_id": finding.get("finding_id", "unknown"),
            "session_id": finding.get("session_id", "unknown"),
            "discovered_at": finding.get("discovered_at", "unknown"),
            "validated_by": finding.get("validated_by", "unknown"),
        },
    }

    return report
