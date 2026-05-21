# Scope-Guard — Target Boundary Enforcement

## Overview
Scope-Guard is the non-negotiable boundary enforcement system. No request, scan, or probe leaves any agent without passing through Scope-Guard. Violation = immediate halt.

## Architecture
```
Request → Scope-Guard → [PASS] → Execution → Audit-Log
                       → [FAIL] → Block + Alert Athena + Audit-Log
```

## Scope Definition

### Program Scope Format (per target)
```yaml
program: hackerone/example
active: true
added: 2025-01-01
scopes:
  in_scope:
    domains:
      - "*.example.com"
      - "api.example.co"
    ips: []
    exclude:
      - "docs.example.com"
      - "status.example.com"
  out_of_scope:
    domains:
      - "*.example.net"
    notes: "CDN and third-party services"
  test_types:
    allowed:
      - recon
      - scanning
      - fuzzing
      - injection_testing
      - auth_testing
    restricted:
      - dos_testing        # NEVER
      - social_engineering # NEVER
      - physical_testing   # NEVER
    approval_required:
      - destructive_exploit
      - data_exfiltration_test
  rate_limits:
    requests_per_second: 5
    concurrent_scans: 1
  special_instructions: "No scanning during business hours (9-5 EST)"
```

## Scope Check Protocol
```
SCOPE_CHECK before ANY request:
  1. Parse target URL → extract hostname, port, path
  2. Load active program scopes
  3. Match hostname against in_scope domains/ips
     ├── Wildcard match (e.g., *.example.com)
     ├── Exact match
     └── No match → BLOCK
  4. Check against exclude list
     ├── Match exclude → BLOCK
     └── No match → continue
  5. Check test_type against allowed/restricted
     ├── Restricted → BLOCK (NEVER allow)
     ├── Approval required → CHECK approval status
     └── Allowed → continue
  6. Check rate limits
     ├── Exceeded → QUEUE or THROTTLE
     └── Within limits → continue
  7. Follow redirect?
     ├── Yes → re-run scope check on redirect URL
     └── No → continue
  8. Log scope check to audit-log
  9. Return: PASS / BLOCK / QUEUE
```

## Violation Response
```
SCOPE VIOLATION detected:
  1. IMMEDIATELY block the request
  2. Log full context to audit-log (agent, target, intended action, scope rule violated)
  3. Alert Athena with details
  4. Athena evaluates: was this a near-miss or actual violation?
     - Near-miss (caught by guard): warning to agent
     - Actual violation (request sent before check): KILL-SWITCH
  5. If kill-switch triggered: full halt, human review required
```

## Implementation Notes
- Scope-Guard runs as a pre-execution hook, not a separate service
- Check is synchronous: no request proceeds without explicit PASS
- Cache scope rules locally (refresh every 60 min from program definitions)
- All scope checks are logged for audit compliance
- Agents CANNOT bypass Scope-Guard (enforced at Hermes tool boundary)
