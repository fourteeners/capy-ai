"""
Scope-Guard: Boundary enforcement system. No request proceeds without passing scope check.
"""

from scope_guard.engine import ScopeGuard

__all__ = ["ScopeGuard"]
