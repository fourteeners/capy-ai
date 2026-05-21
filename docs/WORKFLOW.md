# WORKFLOW.md — Operational Workflows

## Table of Contents
1. [Full Hunt Workflow](#full-hunt-workflow)
2. [Quick Recon Workflow](#quick-recon-workflow)
3. [Research-Only Workflow](#research-only-workflow)
4. [Emergency Procedures](#emergency-procedures)
5. [Learning Cycle](#learning-cycle)
6. [Tool Evolution Workflow](#tool-evolution-workflow)

---

## Full Hunt Workflow

The complete end-to-end bug bounty hunt. From target assignment to validated findings.

### Duration: 2-6 hours (typical), up to 24h (deep hunt)

### Pre-Flight Checklist
- [ ] Target assigned by Athena (or user directive)
- [ ] Program rules loaded (scope, exclusions, payouts)
- [ ] Scope-Guard initialized for this target
- [ ] Audit log session created: `HUNT-{YYYYMMDD}-{HHMMSS}-{target_hash}`
- [ ] Kill-switch status: ARMED
- [ ] Rate limits configured

### Phase 1: Intelligence Gathering (30-60 min)
**Owner: Prometheus + Odysseus (parallel)**

#### 1a. Research (Prometheus → Mnemosyne)
- Search corpus for similar targets
- Query CVE database for target's tech stack
- Check Cassandra's threat intel for recent relevant CVEs
- Produce: Technology vulnerability map

#### 1b. Target Profiling (Odysseus → Argus)
- Passive recon only (no packets to target)
- Technology fingerprinting
- Infrastructure mapping
- Historical incident research
- Program rule analysis
- Produce: Complete target dossier

### Phase 2: Strategy Development (30-45 min)
**Owner: Odysseus**

#### 2a. Attack Surface Mapping (Odysseus)
- Enumerate entry points
- Map authentication flows
- Identify third-party integrations
- Web3: enumerate contracts, proxies, oracles

#### 2b. Attack Path Design (Odysseus → Perseus)
- For each entry point: applicable vulnerability classes
- Rank paths by exploitability × impact × bounty
- Design chains: how do low-severity findings escalate?

#### 2c. Strategic Review (Odysseus + Themistocles)
- Themistocles generates alternatives
- Debate and refine
- Select final attack paths

#### 2d. Playbook Generation (Perseus)
- Decompose selected paths into exact commands
- Define success/failure criteria
- Specify fallback options
- Produce: Executable playbook for Ares

### Phase 3: Execution (1-4 hours)
**Owner: Ares**

#### 3a. Reconnaissance (Aegis) — 15-60 min
```
subfinder + amass → dnsx → httpx → naabu → ffuf → katana → subjs
Output: Live hosts, open ports, technologies, endpoints, JS, secrets
Gate: 0 live hosts → halt and report to Athena
```

#### 3b. Vulnerability Hunting (Artemis) — 30-120 min
```
nuclei → sqlmap → dalfox → ffuf (params) → auth tests → web3 analysis
Output: Raw findings (class, endpoint, evidence, confidence)
Gate: Findings with confidence < 0.5 → discarded
```

#### 3c. PoC Development (Hephaestus) — 10-60 min per finding
```
Analyze finding → Design minimal PoC → Test → Deploy safe PoC → Capture evidence
⚠️ NON-DESTRUCTIVE ONLY
⚠️ Destructive testing → FLAG FOR HUMAN APPROVAL
```

#### 3d. Validation (Nemesis) — 5-15 min per finding
```
Reproduce 3× → Test 3+ alternative payloads → Test systemic → FP check → Score
Gate: Confidence < 0.8 → back to Artemis
```

### Phase 4: Quality Review (30-60 min)
**Owner: Athena**

- Review each validated finding
- Cross-check scope compliance
- Verify evidence completeness
- Approve or reject each finding
- If novel pattern discovered → alert Prometheus

### Phase 5: Reporting (30-60 min)
**Owner: Odysseus**

- Draft submission-ready reports
- Include: reproduction steps, impact, remediation
- Format per platform requirements (HackerOne, Immunefi, etc.)
- Submit with human approval

### Phase 6: Learning (30 min, automated)
**Owner: Prometheus**

- Session post-mortem: what worked, what didn't, what was new
- Update KB with lessons learned
- Create/modify tools based on gaps found
- Push pattern updates to detection rules

---

## Quick Recon Workflow

Fast surface-level reconnaissance. No vulnerability testing.

### Duration: 15-30 min

```
User: "Scan example.com"
  │
Athena → Ares (Aegis):
  ► enumerate_subdomains
  ► resolve_dns
  ► probe_http
  ► fingerpint_tech
  ► discover_content (top 1000 paths)
  ► analyze_js (quick scan)
  ► find_contracts (if web3)
  │
Athena: Present recon report to user
```

---

## Research-Only Workflow

Investigate a vulnerability class, technique, or target without any scanning.

### Duration: Variable

```
User: "Research JWT algorithm confusion"
  │
Athena → Prometheus (Mnemosyne):
  ► search_corpus("JWT algorithm confusion")
  ► query_cve(related CVEs)
  ► search_web("JWT algorithm confusion bypass 2025")
  ► synthesize_pattern(findings)
  ► update_kb("vulnerability-classes/web2/auth/jwt-confusion")
  │
Prometheus → Athena: Research brief
Athena → User: Summary + KB link
```

---

## Emergency Procedures

### Kill-Switch Trigger
```
Condition Detected (e.g., scope violation)
  │
Scope-Guard → Athena: 🛑 SCOPE VIOLATION
  │
Athena: Broadcast KILL-SWITCH to ALL agents
  Message: "🛑 KILLSWITCH | reason=scope_violation | ALL STOP"
  │
All agents:
  • Halt current operation immediately
  • Close all active connections
  • Flush audit logs
  • Respond with ACK + state snapshot
  │
Athena: Compile incident report → Present to human
  │
Human review → Decision: RESUME / ADJUST / ABORT
```

### WAF Block Response
```
Ares (Artemis): "⚠️ WAF | Cloudflare block | all req 403"
  │
Ares: Pause scanning. Report to Athena.
  │
Athena → Odysseus: "WAF block on target X. Design bypass."
  │
Odysseus → Perseus: Generate bypass playbook
  Options: HTTP/2 smuggling, alternative encoding, different endpoint, mobile API
  │
Odysseus → Athena: "Bypass playbook ready."
  │
Athena: Approve or reject bypass attempt
  │
Ares: Execute bypass playbook or move to next target
```

### Rate Limit Spiral
```
Ares: "⚠️ RATE | 429 cascade | all endpoints"
  │
Ares: Auto-pause. Exponential backoff exhausted.
  │
Athena: Evaluate. Options:
  1. Increase backoff ceiling (if safe)
  2. Reduce concurrency
  3. Pause this target, move to next
  4. Flag for off-hours scanning
```

---

## Learning Cycle

### Continuous (every session)
```
Session Complete
  │
Prometheus:
  ├── Review execution log → What worked? What failed?
  ├── Review findings → Any novel patterns?
  ├── Review tool performance → FP rate, detection rate
  ├── Update KB → New wiki pages or updates
  └── Notify team → Relevant agents get KB updates
```

### Weekly (automated)
```
Weekly Cron
  │
Prometheus (Logos):
  ├── Cluster reports → New patterns?
  ├── Trend analysis → What's emerging?
  ├── Gap analysis → What are we missing?
  └── Publish pattern alert if >3 similar reports found

Prometheus:
  ├── Tool performance review → FP > 20% flagged for review
  ├── Unused tools (>60 days) → Flagged for retirement
  └── New CVE correlation → Update detection rules
```

### Monthly (review + human)
```
Monthly Review
  │
Athena: Present monthly summary to human
  • Targets hunted
  • Findings discovered
  • Bounties earned
  • New patterns discovered
  • Tools created/updated/retired
  • KB growth metrics
  • Recommendations for next month
```

---

## Tool Evolution Workflow

### Create New Tool
```
Trigger: Novel vulnerability pattern with no existing detection

Prometheus:
  1. Mnemosyne deep-dives on the pattern
  2. Prometheus designs detection logic
  3. Create tool SKILL in hermes/skills/shared/
  4. Register in TOOLS_MANIFEST.md
  5. Test against known-vulnerable benchmark
  6. Deploy to relevant agents
  7. Monitor: 30-day evaluation period
```

### Adapt Existing Tool
```
Trigger: FP rate > 20% OR new bypass technique discovered

Prometheus:
  1. Analyze failure mode (specific FP examples)
  2. Modify detection rules
  3. Add/update bypass techniques
  4. Increment version
  5. Test against benchmark corpus
  6. Deploy update
  7. Log change to KB
```

### Retire Tool
```
Trigger: Unused > 60 days OR superseded

Prometheus:
  1. Flag for review
  2. Confirm replacement exists and is better
  3. Archive SKILL to hermes/skills/archive/
  4. Remove from TOOLS_MANIFEST.md
  5. Update KB with retirement note
```

---

## Semi-Auto Mode Workflow

The system operates in semi-automatic mode: fully autonomous until exploitation, then requires human approval for any live exploit.

### Auto (No Approval Required)
- Passive reconnaissance (OSINT, certificate transparency, WHOIS)
- Active reconnaissance (subdomain enum, port scanning, HTTP probing) — within rate limits
- Vulnerability scanning (nuclei, sqlmap detection, XSS testing)
- Fuzzing (directories, parameters, headers)
- Non-destructive PoC development (time-based, DNS callback, HTTP callback)
- Finding validation
- Report drafting

### Approval Required (Human Gate)
- Destructive exploitation (data modification, file writes, state changes)
- Data exfiltration beyond minimal PoC (e.g., extracting a database)
- Denial of service testing
- Social engineering
- Physical testing
- Any action flagged as `approval_required` in scope-guard

### Approval Flow
```
Hephaestus: "Destructive test needed: SQLI INSERT to prove impact"
  │
Athena: Review finding context
  │
Athena → User: "Approval needed: Destructive SQLI test on example.com/api/users.
                Impact: could create a test user record.
                Risk: minimal (single INSERT, no existing data modified).
                Approve?"
  │
User: "Approved."
  │
Athena → Hephaestus: "Proceed. Scope: single INSERT only. Rollback after test."
  │
Hephaestus: Execute → Capture → Clean up → Report
```
