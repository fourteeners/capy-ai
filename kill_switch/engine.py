"""
Kill-Switch Engine — emergency halt with multi-trigger conditions.

Athena holds kill-switch authority. When triggered, ALL agents halt.
Recovery requires human review + approval.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable


class TriggerSeverity(Enum):
    CRITICAL = "critical"  # Immediate halt, no questions
    HIGH = "high"          # Graceful halt, finish current safe operation


class KillSwitchState(Enum):
    ARMED = "armed"        # Normal operation
    TRIGGERED = "triggered"  # Halt active
    PAUSED = "paused"       # Awaiting human review
    RESUMING = "resuming"   # Human approved resume
    ABORTED = "aborted"     # Mission terminated
    DEGRADED = "degraded"   # Resume with restrictions


@dataclass
class TriggerEvent:
    """Record of a kill-switch trigger."""
    trigger_id: str
    condition: str
    severity: TriggerSeverity
    triggered_by: str  # agent or system component
    session_id: str
    context: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class KillSwitch:
    """
    Emergency halt system.

    Trigger conditions:
        CRITICAL: scope_violation, destructive_action, data_exfiltration, target_damage, user_halt
        HIGH: waf_global_block, rate_limit_spiral, tool_crash_loop, credential_leak

    Cooldowns:
        First trigger: 5 minutes
        Third trigger in session: 24 hours
    """

    COOLDOWN_AFTER_FIRST = 300      # 5 minutes
    COOLDOWN_AFTER_THIRD = 86400    # 24 hours

    def __init__(self):
        self._state = KillSwitchState.ARMED
        self._trigger_history: list[TriggerEvent] = []
        self._listeners: list[Callable] = []
        self._trigger_id_counter = 0
        self._last_trigger_time: float = 0
        self._disabled = False  # NEVER true in production

    @property
    def state(self) -> KillSwitchState:
        return self._state

    @property
    def is_active(self) -> bool:
        return self._state in (KillSwitchState.TRIGGERED, KillSwitchState.PAUSED)

    @property
    def trigger_count(self) -> int:
        return len(self._trigger_history)

    def arm(self) -> None:
        """Arm the kill-switch (normal operation state)."""
        self._state = KillSwitchState.ARMED

    def trigger(
        self,
        condition: str,
        severity: TriggerSeverity,
        triggered_by: str,
        session_id: str,
        context: Optional[dict] = None,
    ) -> TriggerEvent:
        """
        Trigger the kill-switch. Returns the trigger event.

        Raises ValueError if kill-switch is disabled (should never happen in prod).
        """
        if self._disabled:
            raise ValueError("Kill-switch is disabled — this should never happen in production")

        self._trigger_id_counter += 1
        event = TriggerEvent(
            trigger_id=f"KS-{self._trigger_id_counter:04d}",
            condition=condition,
            severity=severity,
            triggered_by=triggered_by,
            session_id=session_id,
            context=context or {},
        )
        self._trigger_history.append(event)
        self._last_trigger_time = time.time()

        self._state = KillSwitchState.TRIGGERED

        # Notify all listeners
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass  # Listener failure should not prevent halt

        return event

    def request_resume(self, approved_by: str, restrictions: Optional[list[str]] = None) -> bool:
        """
        Request resume after kill-switch. Requires human approval identifier.

        Returns True if resume is allowed (cooldown passed + approved).
        """
        if self._state not in (KillSwitchState.TRIGGERED, KillSwitchState.PAUSED):
            return False

        if not approved_by:
            return False

        # Check cooldown
        elapsed = time.time() - self._last_trigger_time
        required_cooldown = self.COOLDOWN_AFTER_THIRD if self.trigger_count >= 3 else self.COOLDOWN_AFTER_FIRST

        if elapsed < required_cooldown:
            return False

        if restrictions:
            self._state = KillSwitchState.DEGRADED
        else:
            self._state = KillSwitchState.RESUMING

        return True

    def confirm_resume(self) -> None:
        """Confirm resume — transition back to armed state."""
        if self._state in (KillSwitchState.RESUMING, KillSwitchState.DEGRADED):
            self._state = KillSwitchState.ARMED

    def abort_mission(self, reason: str = "") -> None:
        """Abort the current mission. Irreversible without new session."""
        self._state = KillSwitchState.ABORTED
        # Log the abort reason
        self._trigger_history.append(TriggerEvent(
            trigger_id=f"KS-{self._trigger_id_counter + 1:04d}-ABORT",
            condition="mission_aborted",
            severity=TriggerSeverity.CRITICAL,
            triggered_by="athena",
            session_id="",
            context={"reason": reason},
        ))

    def register_listener(self, callback: Callable[[TriggerEvent], None]) -> None:
        """Register a callback to be called when kill-switch triggers."""
        self._listeners.append(callback)

    def get_cooldown_remaining(self) -> float:
        """Get remaining cooldown time in seconds."""
        elapsed = time.time() - self._last_trigger_time
        required = self.COOLDOWN_AFTER_THIRD if self.trigger_count >= 3 else self.COOLDOWN_AFTER_FIRST
        return max(0, required - elapsed)

    def get_status(self) -> dict:
        """Get full kill-switch status."""
        return {
            "state": self._state.value,
            "is_active": self.is_active,
            "trigger_count": self.trigger_count,
            "last_trigger": (
                {
                    "condition": self._trigger_history[-1].condition,
                    "severity": self._trigger_history[-1].severity.value,
                    "triggered_by": self._trigger_history[-1].triggered_by,
                }
                if self._trigger_history else None
            ),
            "cooldown_remaining_seconds": self.get_cooldown_remaining(),
            "can_resume": self.get_cooldown_remaining() == 0,
        }

    # CRITICAL trigger shortcuts

    def scope_violation(self, triggered_by: str, session_id: str, url: str, rule: str) -> TriggerEvent:
        return self.trigger("scope_violation", TriggerSeverity.CRITICAL, triggered_by, session_id, {
            "url": url, "scope_rule": rule,
        })

    def destructive_action_attempt(self, triggered_by: str, session_id: str, action: str) -> TriggerEvent:
        return self.trigger("destructive_action", TriggerSeverity.CRITICAL, triggered_by, session_id, {
            "action": action,
        })

    def user_halt(self, session_id: str, reason: str = "") -> TriggerEvent:
        return self.trigger("user_halt", TriggerSeverity.CRITICAL, "user", session_id, {
            "reason": reason,
        })
