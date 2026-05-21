# Caveman Communication Protocol

## Why
Token efficiency = cost efficiency + speed efficiency. Inter-agent comms are operational, not social. Every token should carry operational payload.

## Level Assignment
| Agent | Level | Rationale |
|-------|-------|-----------|
| Athena (CEO) | lite | Needs clarity for complex decisions |
| Prometheus (RnD) | full | Research output needs structure |
| Odysseus (Strategy) | full | Attack plans need precision |
| Ares (Execution) | ultra | Speed is everything; output is structured |
| All sub-agents | ultra | Maximum throughput |

## Message Types

### STATUS (phase transitions)
```
Format: [PHASE] [STATUS] | [METRICS] | [NEXT]
Example: RECON complete | 23 hosts | 14 web | → HUNT
```

### FINDING (vulnerability report)
```
Format: [CLASS] | [ENDPOINT] | [TYPE] | [CONFIDENCE]
Example: SQLI | /api/users?id= | time-blind | conf=0.92
```

### ALERT (anomaly detection)
```
Format: ⚠️ [TYPE] | [DETAILS] | [ACTION]
Example: ⚠️ WAF | Cloudflare block | paused
```

### DELEGATION (task assignment)
```
Format: [TASK] [TARGET] | [SCOPE] | [PRIORITY] | [DEADLINE]
Example: HUNT target X | scope *.X.com | pri HIGH | ETA 45min
```

### EMERGENCY (kill-switch)
```
Format: 🛑 KILLSWITCH | [REASON] | [CONTEXT]
Example: 🛑 KILLSWITCH | scope violation | /admin redirect out of scope
```

## Exceptions
- Research briefs (Prometheus): structured prose allowed for KB entries
- Final reports (Odysseus): professional prose for submission to platforms
- User-facing comms (Athena): normal language when talking to human
- Emergency contexts: full caveman dropped for safety clarity

## Enforcement
- Message boundary check: all inter-agent messages validated against template
- Non-conforming messages: flagged with [COMMS: non-caveman]
- Repeated violations: escalated to Athena for agent retraining
