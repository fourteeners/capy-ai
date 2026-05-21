"""
Central tool registry — all tools register here. Agents discover and invoke tools
through this registry. The Hermes skill bridge maps SKILL.md steps to registry entries.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
import time
import functools


class ToolCategory(Enum):
    RECON = "recon"
    ANALYSIS = "analysis"
    EXPLOITATION = "exploitation"
    WEB3 = "web3"
    REPORTING = "reporting"
    VALIDATION = "validation"
    ORCHESTRATION = "orchestration"
    KNOWLEDGE = "knowledge"
    UTILITY = "utility"


class ToolStatus(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    RETIRED = "retired"


@dataclass
class ToolMeta:
    """Metadata for a registered tool."""
    name: str
    category: ToolCategory
    description: str
    agent: str  # primary agent that owns this tool
    status: ToolStatus = ToolStatus.ACTIVE
    version: str = "1.0.0"
    requires_scope_check: bool = True
    requires_approval: bool = False
    rate_limit_per_sec: float = 0  # 0 = no limit
    tags: list[str] = field(default_factory=list)


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any = None
    error: str = ""
    duration_ms: float = 0
    metadata: dict = field(default_factory=dict)


class ToolRegistry:
    """Singleton registry for all tools in the system."""

    _instance: Optional["ToolRegistry"] = None
    _tools: dict[str, tuple[ToolMeta, Callable]] = {}
    _usage_stats: dict[str, list[float]] = {}  # tool_name -> [duration_ms, ...]

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
            cls._instance._usage_stats = {}
        return cls._instance

    def register(
        self,
        meta: ToolMeta,
        func: Callable,
    ) -> None:
        """Register a tool with metadata and implementation."""
        self._tools[meta.name] = (meta, func)
        self._usage_stats[meta.name] = []

    def get(self, name: str) -> Optional[tuple[ToolMeta, Callable]]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_by_category(self, category: ToolCategory) -> list[ToolMeta]:
        """List all tools in a category."""
        return [
            meta for name, (meta, _) in self._tools.items()
            if meta.category == category
        ]

    def list_by_agent(self, agent: str) -> list[ToolMeta]:
        """List all tools owned by an agent."""
        return [
            meta for name, (meta, _) in self._tools.items()
            if meta.agent == agent
        ]

    def list_all(self) -> list[ToolMeta]:
        """List all registered tools."""
        return [meta for _, (meta, _) in self._tools.items()]

    def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name. Logs timing for metrics."""
        entry = self._tools.get(name)
        if entry is None:
            return ToolResult(success=False, error=f"Tool '{name}' not registered")

        meta, func = entry

        if meta.status == ToolStatus.RETIRED:
            return ToolResult(success=False, error=f"Tool '{name}' has been retired")

        start = time.monotonic()
        try:
            result = func(**kwargs)
            duration_ms = (time.monotonic() - start) * 1000
            self._usage_stats[name].append(duration_ms)
            return ToolResult(success=True, data=result, duration_ms=duration_ms)
        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            self._usage_stats[name].append(duration_ms)
            return ToolResult(success=False, error=str(e), duration_ms=duration_ms)

    def get_stats(self, name: str) -> dict:
        """Get usage statistics for a tool."""
        durations = self._usage_stats.get(name, [])
        if not durations:
            return {"tool": name, "calls": 0}

        return {
            "tool": name,
            "calls": len(durations),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
        }

    def get_fp_rate(self, name: str) -> Optional[float]:
        """Estimated false positive rate (populated by Nemesis validation)."""
        meta, _ = self._tools.get(name, (None, None))
        if meta is None:
            return None
        return meta.metadata.get("fp_rate")

    def __len__(self) -> int:
        return len(self._tools)


# Singleton accessor
def get_registry() -> ToolRegistry:
    return ToolRegistry()


# Decorator for easy registration
def tool(
    name: str,
    category: ToolCategory,
    agent: str,
    description: str = "",
    requires_scope_check: bool = True,
    requires_approval: bool = False,
    rate_limit_per_sec: float = 0,
    tags: Optional[list[str]] = None,
):
    """Decorator to register a function as a tool."""
    def decorator(func: Callable) -> Callable:
        meta = ToolMeta(
            name=name,
            category=category,
            description=description or func.__doc__ or "",
            agent=agent,
            requires_scope_check=requires_scope_check,
            requires_approval=requires_approval,
            rate_limit_per_sec=rate_limit_per_sec,
            tags=tags or [],
        )
        get_registry().register(meta, func)

        @functools.wraps(func)
        def wrapper(**kwargs):
            return get_registry().execute(name, **kwargs)
        return wrapper
    return decorator
