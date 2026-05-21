# Audit Log — Session Traceability System

## Overview
Every action taken by every agent is logged immutably. The audit log serves three purposes: compliance (prove what we did and did not do), learning (what worked, what didn't), and debugging (why did something go wrong).

## Log Schema

### Session Log
```json
{
  "session_id": "HUNT-20250101-120000-a1b2c3d4",
  "target": "example.com",
  "program": "hackerone/example",
  "scope": {...},
  "status": "active | paused | completed | aborted",
  "created_at": "ISO8601",
  "agents_involved": ["athena", "ares", "odysseus", "prometheus"],
  "findings_count": 0,
  "kill_switch_triggers": 0
}
```

### Action Log
```json
{
  "action_id": "uuid",
  "session_id": "HUNT-...",
  "timestamp": "ISO8601",
  "agent": "ares.aegis",
  "action_type": "recon.subdomain_enum",
  "target": "example.com",
  "scope_check": {
    "result": "PASS",
    "rule": "*.example.com in scope"
  },
  "command": "subfinder -d example.com -o output.txt",
  "result": {
    "status": "success",
    "output_summary": "Found 23 subdomains",
    "duration_ms": 4532
  }
}
```

### Finding Log
```json
{
  "finding_id": "uuid",
  "session_id": "HUNT-...",
  "discovered_by": "ares.artemis",
  "vulnerability_class": "SQLI",
  "endpoint": "https://example.com/api/users?id=",
  "method": "GET",
  "confidence": 0.92,
  "cvss_score": 7.5,
  "status": "raw | validated | false_positive | reported | duplicate",
  "validation": {
    "validated_by": "ares.nemesis",
    "reproduction_count": 3,
    "payloads_tested": ["' OR '1'='1", "' OR SLEEP(5)--", "UNION SELECT..."],
    "confidence_final": 0.92
  },
  "report": {
    "drafted_by": "odysseus",
    "approved_by": "athena",
    "submitted_to": "hackerone",
    "report_id": "123456"
  }
}
```

### Kill-Switch Log
```json
{
  "trigger_id": "uuid",
  "session_id": "HUNT-...",
  "timestamp": "ISO8601",
  "trigger_condition": "scope_violation",
  "triggered_by": "scope_guard",
  "context": {
    "agent": "ares.aegis",
    "intended_action": "subdomain_enum",
    "target": "out-of-scope.example.com",
    "scope_rule_violated": "only *.example.com in scope"
  },
  "resolution": {
    "reviewed_by": "human",
    "decision": "ABORT_MISSION",
    "notes": "Target was related company, not in program scope"
  }
}
```

## Retention
- Session logs: 90 days (configurable)
- Finding logs: permanent (KB integration)
- Action logs: 90 days
- Kill-switch logs: permanent
- Default rotation: compress + archive after retention period

## Access Control
- Write access: all agents (append-only)
- Read access:
  - Athena: full access (orchestration + review)
  - Prometheus: findings + actions (for learning)
  - Ares/Odysseus: own session logs only
  - Human: full access

## Implementation
- JSONL format for log files (one JSON object per line)
- Directory: `audit-log/sessions/`, `audit-log/findings/`, `audit-log/actions/`
- Rolled daily: `actions-YYYYMMDD.jsonl`
- All writes are synchronous (no buffered logging — data safety)
