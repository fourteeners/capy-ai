# SKILL: Bug Bounty Orchestration

## Metadata
- **Skill ID**: `orch-001`
- **Version**: 1.0.0
- **Author**: CAPY Bug Hunter System
- **Category**: Orchestration
- **Caveman Level**: lite

## Purpose
Coordinate multi-agent bug bounty operations. Receive user directives, delegate to team leads, monitor progress, enforce scope, and control the kill-switch.

## Triggers
- User directive: "scan X", "hunt X", "check X"
- Scheduled cron: daily/weekly recon sweep
- Event-driven: new CVE, new program, intel alert
- Anomaly detection: scope violation, rate limit, tool crash

## Workflow

### 1. Triage Incoming Signal
```
RECEIVE signal
  ├── Is it a new target? → Task Odysseus: profile + plan
  ├── Is it a recon request? → Task Ares: recon pipeline
  ├── Is it a full hunt? → Task Odysseus (plan) + Ares (execute) in sequence
  ├── Is it research? → Task Prometheus: investigate
  ├── Is it an alert? → Assess severity → delegate accordingly
  └── Is it an emergency? → Kill-switch evaluation
```

### 2. Task Delegation
```
DELEGATE to team lead:
  - Specify: what, on what target, with what constraints, by when
  - Include: scope boundaries, rate limits, special instructions
  - Set: priority (critical/high/medium/low)
  - Log: delegation to audit-log
```

### 3. Progress Monitoring
```
MONITOR active tasks:
  - Poll team leads for status every N minutes (configurable)
  - Track: phase, progress %, findings so far, blockers
  - Alert if: stalled > 15 min, error rate > threshold, scope concern
```

### 4. Quality Gate
```
REVIEW findings from Ares:
  - Verify: scope compliance, confidence score, evidence completeness
  - Cross-check: against known false positive patterns (with Prometheus)
  - Approve: for report drafting (to Odysseus)
  - Reject: with specific feedback
```

### 5. Emergency Response
```
KILL-SWITCH EVALUATION:
  Trigger conditions:
    - Scope violation detected
    - Destructive payload attempted without approval
    - Anomalous target response (possible damage)
    - User-requested halt
  Action:
    - Broadcast halt to ALL agents
    - Log trigger reason with full context
    - Await human review before resuming
```

## Skills Used
- `delegate_task` — Assign work to team leads
- `query_status` — Check agent status
- `review_finding` — Quality-gate a finding
- `trigger_kill_switch` — Emergency halt
- `resume_operations` — Resume after kill-switch review
- `query_kb` — Search knowledge base
- `update_priority` — Reprioritize targets

## Integration
- Hermes profile: `athena`
- Personality: `agents/orchestrator/soul/SOUL.md`
- Sub-agent spawning for parallel monitoring
