# Caveman Learning Engine — Experience-Based Skill Evolution

## Overview
The Caveman Learning Engine implements the "learning from experience" requirement. After every hunt session, failed or successful, the system extracts lessons and evolves. This is NOT a separate system — it is embedded in Prometheus's research loop and the Caveman protocol.

## Learning Sources

### 1. Bug Report Corpus
```
SOURCE: corpus/bug-reports/{hackerone,immunefi,other}/
PROCESS:
  - Parse each report: vulnerability class, target type, exploitation method
  - Extract: what technique worked? what tool was used? what bypass was needed?
  - Generalize: does this generalize to other targets/tech stacks?
  - Create: detection rule, attack path template, or new SKILL
FREQUENCY: Continuous (every new report added to corpus)
```

### 2. Session Post-Mortems
```
SOURCE: audit-log/sessions/HUNT-*/
PROCESS (after every session):
  - Review: what was tested, what was found, what was missed
  - Identify: tool performance (FP rate, detection rate, speed)
  - Identify: methodology gaps (what should we have tested but didn't?)
  - Identify: new patterns (anything novel discovered?)
  - Create: session learning artifact → KB
FREQUENCY: After every hunt session (automated)
```

### 3. Tool Performance Metrics
```
SOURCE: audit-log/actions/ (tool execution logs)
PROCESS (weekly):
  - Calculate: FP rate per tool, detection rate, avg execution time
  - Flag: tools with FP rate > 20% or detection rate < 50%
  - Identify: obsolete tools (not used in 60+ days)
  - Recommend: update, replace, or retire
FREQUENCY: Weekly automated review
```

### 4. Pattern Evolution
```
SOURCE: Logos (Analyst) cluster analysis
PROCESS:
  - Cluster: vulnerability reports by class, tech, technique, bounty
  - Detect: emerging patterns (3+ similar reports = pattern)
  - Detect: blind spots (vuln classes we haven't found recently)
  - Recommend: new detection rules, new attack paths, new tools
FREQUENCY: Weekly, or on-demand
```

## Skill Evolution Pipeline

### Skill Creation
```
TRIGGER: Novel vulnerability pattern discovered
PROCESS:
  1. Mnemosyne (Researcher) deep-dives
  2. Prometheus synthesizes into structured knowledge
  3. Create new SKILL.md in hermes/skills/
  4. Register in shared skill registry
  5. Test on known-vulnerable targets
  6. Deploy to all relevant agents
  7. Monitor performance for 30 days
```

### Skill Adaptation
```
TRIGGER: Tool FP rate exceeds threshold OR new bypass technique discovered
PROCESS:
  1. Prometheus analyzes failure mode
  2. Modify SKILL.md: update detection rules, add bypasses, refine heuristics
  3. Increment version
  4. Test against benchmark corpus
  5. Deploy update
  6. Log change to KB for audit trail
```

### Skill Retirement
```
TRIGGER: Tool unused for 60+ days OR superseded by better tool
PROCESS:
  1. Flag for review
  2. Confirm: is there a better replacement?
  3. Archive SKILL.md to hermes/skills/archive/
  4. Remove from active registry
  5. Update KB: note retirement reason
```

## Methodology Evolution

### Variation Engine
```
PURPOSE: Prevent methodological stagnation
PROCESS:
  1. For each hunt session, Odysseus varies at least ONE parameter:
     - Tool choice (e.g., use dalfox instead of nuclei-xss)
     - Encoding strategy (e.g., try Unicode bypass even if not blocked)
     - Entry point priority (e.g., test API before web forms)
     - Chain order (e.g., try auth bypass before injection)
  2. Log variation to audit-log
  3. Compare results against baseline (same target, standard methodology)
  4. If variation outperforms baseline: adopt as new default
  5. If variation underperforms: note in KB, don't repeat
```

### A/B Testing Framework
```
PURPOSE: Data-driven methodology optimization
PROCESS:
  1. For targets with multiple similar endpoints:
     - Group A: test with standard methodology
     - Group B: test with experimental methodology
  2. Compare: findings count, FP rate, time per finding, bounty value
  3. Statistical significance threshold: p < 0.05 or 10+ trials
  4. Winner becomes new standard
```

## Knowledge Base Integration

### Every learning artifact updates the KB
```
Learning Event → Prometheus analysis → KB update → Agent notification
```

### KB triggers agent adaptation
```
KB update → relevant agents check KB → adapt behavior based on new knowledge
```

### Compounding effect
```
Session 1: KB has 10 patterns → Session 10: KB has 100+ patterns
Each session benefits from ALL prior learning
This is the LLM Wiki compounding effect in action
```

## Implementation Notes
- Learning engine is part of Prometheus's core loop, not a separate service
- KB updates trigger agent notifications automatically
- Tool performance metrics are calculated from audit-log (no additional instrumentation needed)
- All learning decisions are logged for auditability
- Human can override any automated learning decision
