"""
Audit-Log Engine — immutable append-only logging for all agent actions.

JSONL format, rolled daily, retention enforced.
Every action, finding, and kill-switch event is logged permanently.
"""

import json
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class AuditLogger:
    """
    Immutable append-only audit logger.

    Logs three types:
    - Action logs: every tool execution, scope check, request
    - Finding logs: every vulnerability finding lifecycle
    - Session logs: hunt session start/end/status
    - Kill-switch logs: every trigger event

    All writes are synchronous for data safety.
    """

    def __init__(
        self,
        base_dir: str = "audit-log",
        retention_days: int = 90,
    ):
        self.base_dir = Path(base_dir)
        self.retention_days = retention_days
        self._current_session_id: Optional[str] = None

        # Ensure directories exist
        for subdir in ["sessions", "findings", "actions"]:
            (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)

    # ---- Session Management ----

    def start_session(
        self,
        target: str,
        program: str = "",
        scope_definition: Optional[dict] = None,
    ) -> str:
        """Start a new hunt session. Returns session_id."""
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        target_hash = str(uuid.uuid4())[:8]
        session_id = f"HUNT-{timestamp}-{target_hash}"

        self._current_session_id = session_id

        entry = {
            "type": "session_start",
            "session_id": session_id,
            "target": target,
            "program": program,
            "scope": scope_definition,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
        }

        self._write("sessions", session_id, entry)
        return session_id

    def end_session(self, session_id: str, status: str = "completed", summary: Optional[dict] = None) -> None:
        """End a hunt session."""
        entry = {
            "type": "session_end",
            "session_id": session_id,
            "ended_at": datetime.utcnow().isoformat(),
            "status": status,
            "summary": summary or {},
        }
        self._write("sessions", session_id, entry)

    # ---- Action Logging ----

    def log_action(
        self,
        agent: str,
        action_type: str,
        target: str,
        command: str,
        scope_check: dict,
        result: dict,
        session_id: Optional[str] = None,
    ) -> str:
        """Log a tool execution action."""
        action_id = str(uuid.uuid4())
        sid = session_id or self._current_session_id or "unknown"

        entry = {
            "action_id": action_id,
            "session_id": sid,
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "action_type": action_type,
            "target": target,
            "scope_check": scope_check,
            "command": command,
            "result": result,
        }

        self._write("actions", sid, entry)
        return action_id

    def log_scope_check(self, url: str, result: dict, agent: str, session_id: Optional[str] = None) -> None:
        """Log a scope verification check."""
        sid = session_id or self._current_session_id or "unknown"

        entry = {
            "action_id": str(uuid.uuid4()),
            "session_id": sid,
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "action_type": "scope_check",
            "target": url,
            "scope_check": result,
            "command": f"check_scope({url})",
            "result": {"status": "PASS" if result.get("passed") else "FAIL"},
        }

        self._write("actions", sid, entry)

    # ---- Finding Logging ----

    def log_finding(
        self,
        vulnerability_class: str,
        endpoint: str,
        confidence: float,
        discovered_by: str,
        session_id: Optional[str] = None,
        cvss_score: Optional[float] = None,
        status: str = "raw",
    ) -> str:
        """Log a vulnerability finding."""
        finding_id = str(uuid.uuid4())
        sid = session_id or self._current_session_id or "unknown"

        entry = {
            "finding_id": finding_id,
            "session_id": sid,
            "timestamp": datetime.utcnow().isoformat(),
            "vulnerability_class": vulnerability_class,
            "endpoint": endpoint,
            "confidence": confidence,
            "cvss_score": cvss_score,
            "status": status,
            "discovered_by": discovered_by,
        }

        self._write("findings", sid, entry)
        return finding_id

    def update_finding_status(
        self,
        finding_id: str,
        new_status: str,
        validated_by: str = "",
        validation_details: Optional[dict] = None,
    ) -> None:
        """Update finding status (validated, false_positive, reported, duplicate)."""
        entry = {
            "type": "finding_update",
            "finding_id": finding_id,
            "timestamp": datetime.utcnow().isoformat(),
            "new_status": new_status,
            "validated_by": validated_by,
            "validation_details": validation_details or {},
        }

        self._write("findings", finding_id, entry)

    # ---- Kill-Switch Logging ----

    def log_kill_switch(self, trigger_event) -> None:
        """Log a kill-switch trigger event."""
        entry = {
            "trigger_id": trigger_event.trigger_id,
            "session_id": trigger_event.session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "trigger_condition": trigger_event.condition,
            "triggered_by": trigger_event.triggered_by,
            "severity": getattr(trigger_event.severity, 'value', str(trigger_event.severity)),
            "context": trigger_event.context,
        }

        self._write("actions", f"killswitch-{trigger_event.trigger_id}", entry)

    # ---- Internal ----

    def _write(self, category: str, key: str, entry: dict) -> None:
        """Append a JSON line to the log file. Synchronous for safety."""
        date_str = datetime.utcnow().strftime("%Y%m%d")
        log_file = self.base_dir / category / f"{date_str}.jsonl"

        # Synchronous write — data safety over speed
        with open(log_file, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def cleanup_old_logs(self) -> int:
        """Remove logs older than retention_days. Returns count of removed files."""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        removed = 0

        for subdir in ["sessions", "findings", "actions"]:
            log_dir = self.base_dir / subdir
            if not log_dir.exists():
                continue

            for file_path in log_dir.glob("*.jsonl"):
                try:
                    date_str = file_path.stem
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    if file_date < cutoff:
                        file_path.unlink()
                        removed += 1
                except (ValueError, OSError):
                    pass

        return removed

    def get_stats(self) -> dict:
        """Get audit log statistics."""
        stats = {"sessions": 0, "actions": 0, "findings": 0, "size_bytes": 0}

        for subdir in ["sessions", "findings", "actions"]:
            log_dir = self.base_dir / subdir
            if not log_dir.exists():
                continue

            for file_path in log_dir.glob("*.jsonl"):
                try:
                    file_size = file_path.stat().st_size
                    stats["size_bytes"] += file_size

                    with open(file_path) as f:
                        line_count = sum(1 for _ in f)
                    stats[subdir] += line_count
                except OSError:
                    pass

        return stats
