# SKILL: Caveman Communication Protocol

## Metadata
- **Skill ID**: `shared-comms-001`
- **Version**: 1.0.0
- **Author**: CAPY Bug Hunter System
- **Category**: Shared / Communication
- **Required By**: ALL agents (level varies)

## Purpose
Reduce inter-agent communication tokens by 40-75% while maintaining full operational clarity. Based on Julius Brussee's Caveman protocol.

## Level Mapping
| Level | Token Reduction | Agents |
|-------|----------------|--------|
| `lite` | ~40% | Athena (CEO) |
| `full` | ~60% | Prometheus (RnD), Odysseus (Strategy) |
| `ultra` | ~75% | Ares (Execution), all sub-agents |

## Rules by Level

### LITE
- Drop greetings, pleasantries, filler
- "I think we should" → "Recommend:"
- Status: one line, metrics only
- Questions: direct, one at a time

### FULL
- Fragments, not sentences
- Drop articles (a, an, the)
- Drop auxiliary verbs
- → for flow, | for alternatives, ⚠️ for warnings
- Numbers over words

### ULTRA
- Telegraphic: keywords only
- Pipe-delimited key:value
- Status: [PHASE] [RESULT] [NEXT]
- Finding: [CLASS]|[ENDPOINT]|[METHOD]|[CONF]
- Fixed templates for message types

## Message Templates (Ultra)

### Status
```
RECON done | 23 live | 14 web → HUNT
HUNT 45% | 2 high found | ETA 12min
VALIDATE done | 6 confirmed | 2 FP
```

### Finding
```
SQLI | POST /api/users?id= | time-blind | conf=0.92
XSS | GET /search?q= | reflected | conf=0.78
SSRF | POST /webhook | metadata potential | conf=0.65
```

### Alert
```
⚠️ WAF | Cloudflare block | paused
⚠️ SCOPE | redirect out-of-scope | halted
⚠️ RATE | 429 on /api | backing off 8s
```

### Emergency
```
🛑 KILLSWITCH | scope_violation | /admin → external CDN
```

## Exceptions
- Research briefs (Prometheus): structured prose for KB
- Final reports (Odysseus): professional prose for platform submission
- User-facing (Athena): natural language for human interaction
- Emergency: clarity overrides compression

## Enforcement
- Message boundary check on all inter-agent comms
- Non-conforming: flagged [COMMS: non-caveman]
- Repeated violations: escalated to Athena for retraining
