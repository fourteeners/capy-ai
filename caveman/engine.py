"""
Caveman Protocol Engine — token-efficient inter-agent communication.

Based on Julius Brussee's caveman protocol. Cuts 40-75% output tokens
while maintaining full technical accuracy.

Level mapping:
    lite (~40%): Athena — drop filler, keep sentences
    full (~60%): Prometheus, Odysseus — fragments, drop articles
    ultra (~75%): Ares, sub-agents — telegraphic, pipe-delimited
"""

import re
from enum import Enum
from typing import Optional


class CavemanLevel(Enum):
    LITE = "lite"
    FULL = "full"
    ULTRA = "ultra"


class CavemanProtocol:
    """
    Token compression engine for inter-agent communication.

    Usage:
        cp = CavemanProtocol()
        compressed = cp.compress(message, CavemanLevel.ULTRA, "finding")
    """

    # Level -> agent assignments
    LEVEL_ASSIGNMENTS = {
        "athena": CavemanLevel.LITE,
        "prometheus": CavemanLevel.FULL,
        "odysseus": CavemanLevel.FULL,
        "ares": CavemanLevel.ULTRA,
    }

    @classmethod
    def for_agent(cls, agent_name: str) -> CavemanLevel:
        """Get the caveman level for an agent."""
        name = agent_name.lower()
        return cls.LEVEL_ASSIGNMENTS.get(name, CavemanLevel.FULL)

    def compress(self, message: str, level: CavemanLevel, message_type: str = "status") -> str:
        """
        Compress a message to the specified caveman level.

        For ULTRA, uses structured templates. For LITE/FULL, applies
        text transformation rules.
        """
        if level == CavemanLevel.LITE:
            return self._compress_lite(message)
        elif level == CavemanLevel.FULL:
            return self._compress_full(message)
        elif level == CavemanLevel.ULTRA:
            return self._compress_ultra(message, message_type)
        return message

    def validate_template(self, message: str, expected_type: str, level: CavemanLevel) -> dict:
        """
        Validate that a message follows the expected caveman template.
        Returns dict with 'valid', 'errors', 'warnings'.
        """
        if level != CavemanLevel.ULTRA:
            # LITE and FULL don't enforce templates
            return {"valid": True, "errors": [], "warnings": []}

        errors = []
        warnings = []

        templates = {
            "status": {
                "required": [],
                "suggested": ["→", "|"],
            },
            "finding": {
                "required": ["|"],
                "suggested": ["conf="],
            },
            "alert": {
                "required": ["⚠️"],
                "suggested": ["|"],
            },
            "emergency": {
                "required": ["🛑", "KILLSWITCH"],
                "suggested": [],
            },
        }

        tmpl = templates.get(expected_type, {"required": [], "suggested": []})

        for req in tmpl["required"]:
            if req not in message:
                errors.append(f"Missing required pattern: '{req}'")

        for sug in tmpl["suggested"]:
            if sug not in message:
                warnings.append(f"Missing suggested pattern: '{sug}'")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def estimate_tokens(self, message: str) -> int:
        """Rough token estimate (~4 chars per token)."""
        return max(1, len(message) // 4)

    def compare(self, original: str, compressed: str) -> dict:
        """Compare original vs compressed token counts."""
        orig_tokens = self.estimate_tokens(original)
        comp_tokens = self.estimate_tokens(compressed)
        saved = orig_tokens - comp_tokens
        pct = (saved / orig_tokens * 100) if orig_tokens > 0 else 0

        return {
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "tokens_saved": saved,
            "reduction_pct": round(pct, 1),
        }

    # ---- Compression Rules ----

    @staticmethod
    def _compress_lite(text: str) -> str:
        """LITE: drop filler, keep sentences (~40% reduction)."""
        # Drop greetings
        for phrase in ["hello", "hi there", "hey", "greetings", "thank you", "thanks"]:
            text = re.sub(rf"\b{phrase}\b,?\s*", "", text, flags=re.IGNORECASE)

        # Drop filler phrases
        fillers = [
            r"\bI think\b", r"\bI believe\b", r"\bin my opinion\b",
            r"\bjust\s+", r"\breally\s+", r"\bvery\s+", r"\bquite\s+",
            r"\bactually\b", r"\bbasically\b", r"\bliterally\b",
        ]
        for filler in fillers:
            text = re.sub(filler, "", text, flags=re.IGNORECASE)

        # Shorten common phrases
        replacements = [
            (r"I (?:would|'d) (?:like to |recommend )", "Recommend: "),
            (r"Let me (?:check|see|look)", "Checking."),
            (r"(?:I am|I'm) going to", "Will"),
            (r"in order to", "to"),
            (r"due to the fact that", "because"),
            (r"at this point in time", "now"),
        ]
        for pattern, repl in replacements:
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

        # Clean up extra spaces
        text = re.sub(r"\s{2,}", " ", text).strip()

        return text

    @staticmethod
    def _compress_full(text: str) -> str:
        """FULL: fragments, drop articles/auxiliaries (~60% reduction)."""
        text = CavemanProtocol._compress_lite(text)

        # Drop articles
        for article in [r"\bthe\b", r"\ba\b", r"\ban\b"]:
            text = re.sub(article, "", text, flags=re.IGNORECASE)

        # Drop auxiliary verbs
        auxes = [r"\bis\b", r"\bare\b", r"\bwas\b", r"\bwere\b", r"\bbeen\b"]
        for aux in auxes:
            text = re.sub(aux, "", text, flags=re.IGNORECASE)

        # Compact: → for flow, | for alternatives, ⚠️ for warnings
        text = re.sub(r"\s*->\s*|\s+then\s+", " → ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+or\s+", " | ", text, flags=re.IGNORECASE)

        text = re.sub(r"\s{2,}", " ", text).strip()
        return text

    @staticmethod
    def _compress_ultra(text: str, message_type: str = "status") -> str:
        """
        ULTRA: telegraphic, pipe-delimited templates (~75% reduction).

        Template formats by type:
            status:  [PHASE] [RESULT] | [METRICS] | [NEXT]
            finding: [CLASS] | [ENDPOINT] | [METHOD] | [CONF]
            alert:   ⚠️ [TYPE] | [DETAILS]
            emergency: 🛑 KILLSWITCH | [REASON]
        """
        # For ultra, we don't transform arbitrary text
        # Ultra agents use the template formats directly
        # This method validates conformance
        if message_type == "status":
            # Ensure pipe-delimited template format
            if "|" not in text:
                text = text.replace(". ", " | ").rstrip(".")
            return text
        elif message_type == "finding":
            return text
        elif message_type == "alert":
            if not text.startswith("⚠️"):
                text = "⚠️ " + text
            return text
        elif message_type == "emergency":
            if "🛑" not in text:
                text = "🛑 " + text
            return text

        # Generic ultra compression
        text = CavemanProtocol._compress_full(text)
        # Remove remaining sentence structure
        text = re.sub(r"\.\s*", " | ", text)
        text = re.sub(r"[.,;:!?]", "", text)
        text = re.sub(r"\s{2,}", " ").strip()
        return text
