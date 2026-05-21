"""
Response analyzer — detect patterns, soft 404s, error pages.
"""

from hermes.tools.registry import tool, ToolCategory


def _word_count(text: str) -> int:
    return len(text.split())


@tool(
    name="analyze_response",
    category=ToolCategory.ANALYSIS,
    agent="artemis",
    description="Analyze HTTP responses for patterns, soft 404s, error messages",
    tags=["analysis", "response", "404", "error"],
)
def analyze_response(
    responses: list[dict],  # [{"url": "...", "status": N, "body": "...", "headers": {...}}, ...]
) -> dict:
    """
    Analyze HTTP responses to detect soft 404s, error patterns, and anomalies.

    Args:
        responses: List of response dicts with url, status, body, headers

    Returns:
        dict with 'soft_404s', 'error_pages', 'response_stats'
    """
    # Calculate baseline for soft 404 detection
    status_200 = [r for r in responses if r.get("status") == 200]
    if status_200:
        avg_words = sum(_word_count(r.get("body", "")) for r in status_200) / len(status_200)
        avg_lines = sum(r.get("body", "").count("\n") for r in status_200) / len(status_200)
    else:
        avg_words = 0
        avg_lines = 0

    soft_404s = []
    error_pages = []
    status_distribution = {}

    error_patterns = [
        "not found", "404", "page not found", "no results",
        "does not exist", "could not be found", "nothing here",
        "stack trace", "exception:", "syntax error",
        "sql error", "database error", "fatal error",
        "warning:", "deprecated:", "debug mode",
    ]

    for resp in responses:
        url = resp.get("url", "unknown")
        status = resp.get("status", 0)
        body = resp.get("body", "").lower()

        # Status distribution
        status_distribution[status] = status_distribution.get(status, 0) + 1

        # Soft 404 detection
        if status == 200 and avg_words > 0:
            wc = _word_count(body)
            if wc < avg_words * 0.2:  # Less than 20% of average word count
                soft_404s.append({"url": url, "word_count": wc, "avg_word_count": round(avg_words)})

        # Error page detection
        matched_errors = [p for p in error_patterns if p in body]
        if matched_errors:
            error_pages.append({
                "url": url,
                "status": status,
                "patterns_matched": matched_errors,
            })

    return {
        "total_analyzed": len(responses),
        "status_distribution": status_distribution,
        "soft_404s": soft_404s,
        "soft_404_count": len(soft_404s),
        "error_pages": error_pages,
        "error_page_count": len(error_pages),
        "baseline_word_count": round(avg_words),
    }
