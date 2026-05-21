# Kill-Switch — Emergency Halt System

## Overview
The Kill-Switch is Athena's ultimate authority. When triggered, ALL agent operations halt immediately — no exceptions, no appeals until after human review. It is the safety net that prevents damage.

## Trigger Conditions

### CRITICAL (immediate halt, no questions)
| Condition | Description | Detection |
|-----------|-------------|-----------|
| `scope_violation` | Request sent to out-of-scope target | Scope-Guard post-check |
| `destructive_action` | Destructive payload attempted without approval | Payload analysis |
| `data_exfiltration_attempt` | Attempt to extract more than PoC data | Response size anomaly |
| `target_damage` | Evidence of target system damage | Error response patterns |
| `user_halt` | Human-requested emergency stop | Direct command |
| `anomalous_behavior` | Unexplained system behavior | Heuristic detection |

### HIGH (graceful halt, complete current safe operation)
| Condition | Description | Detection |
|-----------|-------------|-----------|
| `waf_global_block` | Target WAF blocking all requests | 100% 403 rate |
| `rate_limit_spiral` | Rate limiting causing retry storm | Backoff exhaustion |
| `tool_crash_loop` | Critical tool repeatedly crashing | Process monitor |
| `credential_leak` | API key or token exposed in logs | Secret scanner |

## Kill-Switch Protocol
```
TRIGGER → KILL-SWITCH ACTIVE
  1. Athena broadcasts HALT to all agents
     Message: 🛑 KILLSWITCH | reason=<X> | ALL STOP | await review
  2. All agents:
     - Stop current operation immediately
     - Close all active connections
     - Flush audit logs
     - Enter PAUSED state
     - Respond with ACK + final state snapshot
  3. Athena:
     - Collects all agent state snapshots
     - Compiles incident report
     - Presents to human for review
  4. Human review:
     - Review incident context
     - Decision: RESUME / ADJUST_SCOPE / ABORT_MISSION
  5. If RESUME: Athena broadcasts RESUME with any adjusted parameters
  6. If ABORT: session closed, findings archived, lessons documented
```

## Recovery States
| State | Description | Agent Behavior |
|-------|-------------|----------------|
| `PAUSED` | Kill-switch active, awaiting review | No operations, connections closed |
| `RESUMING` | Human approved resume | Re-initialize connections, continue from checkpoint |
| `ABORTED` | Mission terminated | Archive findings, write lessons, cleanup |
| `DEGRADED` | Resume with restrictions (e.g., no active scanning) | Limited operations only |

## Safety Guarantees
1. Kill-switch CANNOT be disabled by any agent (including Athena without human approval)
2. Kill-switch trigger is logged immutably (audit-log, append-only)
3. After trigger, minimum 5-minute cooldown before any resume
4. Three triggers in one session → mandatory 24-hour cooldown

## Configuration
```yaml
kill_switch:
  enabled: true              # NEVER set to false in production
  auto_triggers:
    scope_violation: critical
    destructive_action: critical
    data_exfiltration: critical
    target_damage: critical
    waf_global_block: high
    rate_limit_spiral: high
  cooldown:
    after_trigger: 300       # seconds (5 min)
    after_third_trigger: 86400  # seconds (24 hours)
  human_override:
    required_for_resume: true
    required_for_disable: true
```
