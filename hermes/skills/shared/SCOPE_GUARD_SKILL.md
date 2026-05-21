# SKILL: Scope-Guard Enforcement

## Metadata
- **Skill ID**: `shared-scope-001`
- **Version**: 1.0.0
- **Author**: CAPY Bug Hunter System
- **Category**: Shared / Safety
- **Required By**: ALL agents

## Purpose
Enforce scope boundaries for every network request. No agent may send a request without passing through this skill. This is non-negotiable.

## Scope Check Function
```python
def scope_check(url: str, method: str, action_type: str, session_id: str) -> dict:
    """
    Returns: { "pass": bool, "reason": str, "rule": str }
    """
    # 1. Parse URL
    hostname = extract_hostname(url)
    
    # 2. Load active scopes for this session
    scopes = load_scopes(session_id)
    if not scopes:
        return {"pass": False, "reason": "No scope defined for session", "rule": "none"}
    
    # 3. Match hostname against in_scope
    if not match_scope(hostname, scopes.in_scope.domains, scopes.in_scope.ips):
        return {"pass": False, "reason": f"{hostname} not in scope", "rule": "domain_not_in_scope"}
    
    # 4. Check exclusions
    if match_scope(hostname, scopes.in_scope.exclude, []):
        return {"pass": False, "reason": f"{hostname} explicitly excluded", "rule": "domain_excluded"}
    
    # 5. Check test type
    if action_type in scopes.restricted:
        return {"pass": False, "reason": f"{action_type} is restricted", "rule": "restricted_test_type"}
    
    # 6. Check approval for sensitive actions
    if action_type in scopes.approval_required:
        if not has_approval(action_type, session_id):
            return {"pass": False, "reason": f"{action_type} requires human approval", "rule": "approval_required"}
    
    # 7. Check rate limits
    if is_rate_limited(hostname, scopes.rate_limits):
        return {"pass": False, "reason": "Rate limit exceeded", "rule": "rate_limit"}
    
    return {"pass": True, "reason": "In scope", "rule": "passed"}
```

## Integration
- Hook into ALL agent tool calls that make network requests
- Pre-execution: synchronous check before any request
- Post-redirect: re-check if redirect changes hostname
- External resources: check before fetching JS, images, APIs from third-party hosts

## Agent Requirements
- All agents: call `scope_check()` before ANY network request
- Ares: strict mode — any scope failure = halt and report
- Athena: can override scope check ONLY with explicit human approval

## Logging
- Every scope check logged to audit-log
- Pass: `{"action": "scope_check", "result": "PASS", ...}`
- Fail: `{"action": "scope_check", "result": "FAIL", "reason": "...", ...}`
