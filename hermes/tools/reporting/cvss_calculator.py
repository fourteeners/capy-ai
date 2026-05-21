"""
CVSS v3.1 calculator — compute severity scores and severity ratings.
"""

from hermes.tools.registry import tool, ToolCategory


SEVERITY_RATINGS = [
    (0.0, 0.1, "NONE"),
    (0.1, 4.0, "LOW"),
    (4.0, 7.0, "MEDIUM"),
    (7.0, 9.0, "HIGH"),
    (9.0, 10.1, "CRITICAL"),
]


def _severity_from_score(score: float) -> str:
    for low, high, rating in SEVERITY_RATINGS:
        if low <= score < high:
            return rating
    return "NONE"


@tool(
    name="calculate_cvss",
    category=ToolCategory.REPORTING,
    agent="odysseus",
    description="Calculate CVSS v3.1 score from vector components",
    tags=["reporting", "cvss", "severity", "scoring"],
)
def calculate_cvss(
    attack_vector: str = "N",      # N=Network, A=Adjacent, L=Local, P=Physical
    attack_complexity: str = "L",   # L=Low, H=High
    privileges_required: str = "N", # N=None, L=Low, H=High
    user_interaction: str = "N",    # N=None, R=Required
    scope: str = "U",               # U=Unchanged, C=Changed
    confidentiality: str = "N",     # N=None, L=Low, H=High
    integrity: str = "N",           # N=None, L=Low, H=High
    availability: str = "N",        # N=None, L=Low, H=High
) -> dict:
    """
    Calculate CVSS v3.1 base score.

    Uses simplified CVSS v3.1 calculation based on standard weights.
    For production use, integrate with cvss library for precise scores.

    Args:
        attack_vector: Network (N), Adjacent (A), Local (L), Physical (P)
        attack_complexity: Low (L), High (H)
        privileges_required: None (N), Low (L), High (H)
        user_interaction: None (N), Required (R)
        scope: Unchanged (U), Changed (C)
        confidentiality: None (N), Low (L), High (H)
        integrity: None (N), Low (L), High (H)
        availability: None (N), Low (L), High (H)

    Returns:
        dict with score, severity, vector string, and component breakdown
    """
    # Exploitability weights
    av_map = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20}
    ac_map = {"L": 0.77, "H": 0.44}
    pr_map_u = {"N": 0.85, "L": 0.62, "H": 0.27}
    pr_map_c = {"N": 0.85, "L": 0.68, "H": 0.50}
    ui_map = {"N": 0.85, "R": 0.62}

    # Impact weights
    c_map = {"N": 0.0, "L": 0.22, "H": 0.56}
    i_map = {"N": 0.0, "L": 0.22, "H": 0.56}
    a_map = {"N": 0.0, "L": 0.22, "H": 0.56}

    # Exploitability sub-score
    av = av_map.get(attack_vector, 0.85)
    ac = ac_map.get(attack_complexity, 0.77)
    pr = pr_map_u.get(privileges_required, 0.85) if scope == "U" else pr_map_c.get(privileges_required, 0.85)
    ui = ui_map.get(user_interaction, 0.85)

    exploitability = 8.22 * av * ac * pr * ui

    # Impact sub-score
    c_impact = c_map.get(confidentiality, 0.0)
    i_impact = i_map.get(integrity, 0.0)
    a_impact = a_map.get(availability, 0.0)

    iss = 1 - ((1 - c_impact) * (1 - i_impact) * (1 - a_impact))

    if scope == "U":
        impact = 6.42 * iss
    else:
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15

    # Round up
    if impact <= 0:
        score = 0.0
    else:
        if scope == "U":
            score = min(exploitability + impact, 10)
        else:
            score = min(1.08 * (exploitability + impact), 10)

    score = round(score, 1)
    severity = _severity_from_score(score)

    vector = (
        f"CVSS:3.1/AV:{attack_vector}/AC:{attack_complexity}/PR:{privileges_required}/"
        f"UI:{user_interaction}/S:{scope}/C:{confidentiality}/I:{integrity}/A:{availability}"
    )

    return {
        "score": score,
        "severity": severity,
        "vector": vector,
        "components": {
            "exploitability": round(exploitability, 2),
            "impact": round(impact, 2),
        },
        "breakdown": {
            "attack_vector": f"AV:{attack_vector}",
            "attack_complexity": f"AC:{attack_complexity}",
            "privileges_required": f"PR:{privileges_required}",
            "user_interaction": f"UI:{user_interaction}",
            "scope": f"S:{scope}",
            "cia_impact": f"C:{confidentiality}/I:{integrity}/A:{availability}",
        },
    }
