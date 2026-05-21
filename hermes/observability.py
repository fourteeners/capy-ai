"""
Observability — metrics, health checks, structured logging.

Provides:
- Prometheus-compatible metrics export
- Agent/system health check
- Structured JSON logging
"""

import json
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class AgentHealth:
    """Health status for a single agent."""
    name: str
    status: str = "unknown"  # healthy, degraded, unhealthy, offline
    last_heartbeat: Optional[datetime] = None
    uptime_seconds: float = 0
    tools_available: int = 0
    sessions_active: int = 0
    errors_since_start: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "uptime_seconds": round(self.uptime_seconds, 1),
            "tools_available": self.tools_available,
            "sessions_active": self.sessions_active,
            "errors_since_start": self.errors_since_start,
        }


class MetricsCollector:
    """
    Collects and exports system metrics.

    Thread-safe. Designed for Prometheus scraping via HTTP endpoint.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._start_time = time.time()
        self._agent_health: dict[str, AgentHealth] = {}

    # ---- Counters ----

    def inc_counter(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

    def get_counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    # ---- Gauges ----

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def get_gauge(self, name: str) -> float:
        return self._gauges.get(name, 0.0)

    # ---- Histograms ----

    def observe(self, name: str, value: float) -> None:
        with self._lock:
            self._histograms.setdefault(name, []).append(value)

    def get_histogram_stats(self, name: str) -> dict:
        values = self._histograms.get(name, [])
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    # ---- Agent Health ----

    def update_agent_health(self, name: str, status: str, **kwargs) -> None:
        with self._lock:
            if name not in self._agent_health:
                self._agent_health[name] = AgentHealth(name=name)
            h = self._agent_health[name]
            h.status = status
            h.last_heartbeat = datetime.now(timezone.utc)
            h.uptime_seconds = time.time() - self._start_time
            for key, value in kwargs.items():
                if hasattr(h, key):
                    setattr(h, key, value)

    def get_system_health(self) -> dict:
        """Get full system health report."""
        with self._lock:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": round(time.time() - self._start_time, 1),
                "agents": {
                    name: h.to_dict()
                    for name, h in self._agent_health.items()
                },
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
            }

    # ---- Prometheus Export ----

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []

        with self._lock:
            # Counters
            for name, value in self._counters.items():
                lines.append(f"# HELP capy_{name} Counter: {name}")
                lines.append(f"# TYPE capy_{name} counter")
                lines.append(f"capy_{name} {value}")

            # Gauges
            for name, value in self._gauges.items():
                lines.append(f"# HELP capy_{name} Gauge: {name}")
                lines.append(f"# TYPE capy_{name} gauge")
                lines.append(f"capy_{name} {value}")

            # Histograms
            for name, values in self._histograms.items():
                stats = self.get_histogram_stats(name)
                lines.append(f"# HELP capy_{name}_count Histogram: {name}")
                lines.append(f"# TYPE capy_{name}_count counter")
                lines.append(f"capy_{name}_count {stats['count']}")
                lines.append(f"# TYPE capy_{name}_sum counter")
                lines.append(f"capy_{name}_sum {stats['sum']}")

        return "\n".join(lines) + "\n"


# Global metrics collector
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    return _metrics


def health_check() -> dict:
    """Simple health check for monitoring systems."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents": {
            name: h.status for name, h in _metrics._agent_health.items()
        },
    }


class StructuredLogger:
    """
    Structured JSON logger for agent actions.

    Usage:
        log = StructuredLogger(agent="athena", session_id="HUNT-...")
        log.info("task_delegated", target="example.com", to="ares")
    """

    def __init__(self, agent: str = "system", session_id: str = ""):
        self.agent = agent
        self.session_id = session_id

    def _emit(self, level: str, event: str, **kwargs) -> None:
        entry = {
            "level": level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.agent,
            "session_id": self.session_id,
            "event": event,
            **kwargs,
        }
        # In production: emit to log file/stdout/syslog
        # For now: structured stdout
        print(json.dumps(entry, default=str))

        # Add to metrics
        metrics = get_metrics()
        metrics.inc_counter(f"log_{level}")
        metrics.inc_counter(f"event_{event}")

    def info(self, event: str, **kwargs) -> None:
        self._emit("INFO", event, **kwargs)

    def warn(self, event: str, **kwargs) -> None:
        self._emit("WARN", event, **kwargs)

    def error(self, event: str, **kwargs) -> None:
        self._emit("ERROR", event, **kwargs)
        get_metrics().inc_counter("errors_total")

    def critical(self, event: str, **kwargs) -> None:
        self._emit("CRITICAL", event, **kwargs)
        get_metrics().inc_counter("criticals_total")
