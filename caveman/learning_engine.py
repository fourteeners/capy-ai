"""
Caveman Learning Engine — experience-based skill evolution.

Post-session post-mortems, tool performance metrics, methodology A/B testing,
skill creation/adaptation/retirement pipeline.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class ToolMetrics:
    """Performance metrics for a single tool."""
    tool_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration_ms: float = 0
    false_positives: int = 0
    true_positives: int = 0
    last_used: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0
        return self.successful_calls / self.total_calls

    @property
    def fp_rate(self) -> float:
        total = self.false_positives + self.true_positives
        if total == 0:
            return 0
        return self.false_positives / total

    @property
    def avg_duration_ms(self) -> float:
        if self.total_calls == 0:
            return 0
        return self.total_duration_ms / self.total_calls

    @property
    def is_stale(self) -> bool:
        """Tool not used in 60 days."""
        if not self.last_used:
            return True
        return datetime.utcnow() - self.last_used > timedelta(days=60)

    @property
    def needs_review(self) -> bool:
        """Tool needs review: FP > 20% or not reviewed in 30 days."""
        if self.fp_rate > 0.2:
            return True
        if self.last_reviewed and datetime.utcnow() - self.last_reviewed > timedelta(days=30):
            return True
        return False


@dataclass
class SessionPostMortem:
    """Learning artifact from a completed hunt session."""
    session_id: str
    target: str
    duration_seconds: float
    findings_count: int
    validated_count: int
    false_positives: int
    tools_used: list[str]
    methodology_variation: str  # What was varied this session?
    what_worked: list[str]
    what_failed: list[str]
    what_was_new: list[str]
    lessons: list[str]
    kb_updates: list[str]  # Pages updated in KB


class LearningEngine:
    """
    Experience-based skill evolution system.

    After every session: post-mortem → KB update → tool metrics → methodology review.
    """

    def __init__(self):
        self._tool_metrics: dict[str, ToolMetrics] = {}
        self._post_mortems: list[SessionPostMortem] = []
        self._methodology_variations: list[dict] = []  # A/B test results

    # ---- Tool Metrics ----

    def record_tool_call(self, tool_name: str, success: bool, duration_ms: float) -> None:
        """Record a tool execution for metrics."""
        if tool_name not in self._tool_metrics:
            self._tool_metrics[tool_name] = ToolMetrics(tool_name=tool_name)

        tm = self._tool_metrics[tool_name]
        tm.total_calls += 1
        tm.total_duration_ms += duration_ms
        tm.last_used = datetime.utcnow()

        if success:
            tm.successful_calls += 1
        else:
            tm.failed_calls += 1

    def record_finding_result(self, tool_name: str, was_true_positive: bool) -> None:
        """Record whether a tool's finding was a true or false positive."""
        if tool_name not in self._tool_metrics:
            self._tool_metrics[tool_name] = ToolMetrics(tool_name=tool_name)

        tm = self._tool_metrics[tool_name]
        if was_true_positive:
            tm.true_positives += 1
        else:
            tm.false_positives += 1

    def mark_reviewed(self, tool_name: str) -> None:
        """Mark a tool as reviewed."""
        if tool_name in self._tool_metrics:
            self._tool_metrics[tool_name].last_reviewed = datetime.utcnow()

    def get_tool_metrics(self, tool_name: str) -> Optional[ToolMetrics]:
        """Get metrics for a specific tool."""
        return self._tool_metrics.get(tool_name)

    def get_all_metrics(self) -> list[ToolMetrics]:
        """Get metrics for all tools."""
        return list(self._tool_metrics.values())

    def get_stale_tools(self) -> list[ToolMetrics]:
        """Get tools that haven't been used in 60+ days."""
        return [tm for tm in self._tool_metrics.values() if tm.is_stale]

    def get_tools_needing_review(self) -> list[ToolMetrics]:
        """Get tools with FP > 20% or not reviewed in 30 days."""
        return [tm for tm in self._tool_metrics.values() if tm.needs_review]

    # ---- Post-Mortems ----

    def create_post_mortem(
        self,
        session_id: str,
        target: str,
        duration_seconds: float,
        findings_count: int,
        validated_count: int,
        false_positives: int,
        tools_used: list[str],
        methodology_variation: str = "baseline",
    ) -> SessionPostMortem:
        """Create a session post-mortem. Filled incrementally."""
        pm = SessionPostMortem(
            session_id=session_id,
            target=target,
            duration_seconds=duration_seconds,
            findings_count=findings_count,
            validated_count=validated_count,
            false_positives=false_positives,
            tools_used=tools_used,
            methodology_variation=methodology_variation,
            what_worked=[],
            what_failed=[],
            what_was_new=[],
            lessons=[],
            kb_updates=[],
        )
        self._post_mortems.append(pm)
        return pm

    def analyze_post_mortem(self, pm: SessionPostMortem) -> dict:
        """Analyze a post-mortem for patterns and recommendations."""
        fp_rate = pm.false_positives / pm.findings_count if pm.findings_count > 0 else 0
        validation_rate = pm.validated_count / pm.findings_count if pm.findings_count > 0 else 0
        findings_per_hour = (
            pm.findings_count / (pm.duration_seconds / 3600)
            if pm.duration_seconds > 0 else 0
        )

        recommendations = []

        if fp_rate > 0.3:
            recommendations.append("FP rate > 30% — review tool detection thresholds")
        if validation_rate < 0.5:
            recommendations.append("Low validation rate — investigate FP patterns")
        if findings_per_hour < 1:
            recommendations.append("Low findings rate — consider scope expansion or deeper recon")

        return {
            "session_id": pm.session_id,
            "fp_rate": round(fp_rate, 2),
            "validation_rate": round(validation_rate, 2),
            "findings_per_hour": round(findings_per_hour, 1),
            "recommendations": recommendations,
            "methodology_variation": pm.methodology_variation,
        }

    # ---- Methodology A/B Testing ----

    def record_variation(
        self,
        variation_name: str,
        target_class: str,
        baseline_findings: int,
        variation_findings: int,
        baseline_time: float,
        variation_time: float,
    ) -> dict:
        """Record a methodology variation A/B test result."""
        improvement = variation_findings - baseline_findings
        time_delta = variation_time - baseline_time

        result = {
            "variation": variation_name,
            "target_class": target_class,
            "baseline_findings": baseline_findings,
            "variation_findings": variation_findings,
            "improvement": improvement,
            "improvement_pct": (improvement / baseline_findings * 100) if baseline_findings > 0 else 0,
            "time_delta_seconds": round(time_delta, 1),
            "verdict": "BETTER" if improvement > 0 else ("SAME" if improvement == 0 else "WORSE"),
            "timestamp": datetime.utcnow().isoformat(),
        }

        self._methodology_variations.append(result)
        return result

    def should_adopt_variation(self, variation_name: str) -> bool:
        """Check if a variation has enough evidence to become the new default."""
        relevant = [
            v for v in self._methodology_variations
            if v["variation"] == variation_name
        ]

        if len(relevant) < 3:
            return False

        better_count = sum(1 for v in relevant if v["verdict"] == "BETTER")
        return better_count >= len(relevant) * 0.67  # 2/3 threshold

    # ---- Learning Summary ----

    def get_learning_summary(self) -> dict:
        """Get overall learning engine status."""
        return {
            "tools_tracked": len(self._tool_metrics),
            "stale_tools": len(self.get_stale_tools()),
            "tools_needing_review": len(self.get_tools_needing_review()),
            "post_mortems": len(self._post_mortems),
            "methodology_variations_tested": len(self._methodology_variations),
            "variations_ready_to_adopt": [
                v["variation"] for v in self._methodology_variations
                if self.should_adopt_variation(v["variation"])
            ],
        }
