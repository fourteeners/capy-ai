# SKILL: Bug Bounty Execution

## Metadata
- **Skill ID**: `exec-001`
- **Version**: 1.0.0
- **Author**: CAPY Bug Hunter System
- **Category**: Execution
- **Caveman Level**: ultra

## Purpose
Execute reconnaissance, vulnerability hunting, exploit development, and validation against bug bounty targets. Non-destructive, scope-aware, evidence-driven.

## ⚠️ CRITICAL BOUNDARIES
1. **NEVER** touch out-of-scope targets
2. **NEVER** execute destructive payloads without human approval
3. **NEVER** exceed rate limits
4. **NEVER** leave artifacts on target systems
5. **ALWAYS** verify scope before every request
6. **ALWAYS** validate findings 3x before reporting

## Core Capabilities

### 1. Reconnaissance Pipeline (Aegis)
```
RECON pipeline:
  1. Subdomain enum: subfinder, amass, assetfinder, chaos
  2. DNS resolution: dnsx (gate: 0 results → stop)
  3. HTTP probing: httpx (live hosts, status codes, tech stack)
  4. Port scanning: naabu (optional, non-standard services)
  5. Content discovery: ffuf, katana, gau, waybackurls
  6. JS analysis: subjs, nuclei-secrets templates
  7. Web3 recon: contract discovery, RPC enumeration
  
  Tools: subfinder, amass, dnsx, httpx, naabu, ffuf, katana,
         gau, waybackurls, subjs, nuclei (recon templates)
```

### 2. Vulnerability Hunting (Artemis)
```
HUNT pipeline:
  1. Template scanning: nuclei with tech-specific + CVE templates
  2. Parameter discovery: arjun, paramspider
  3. Injection testing:
     - SQLi: sqlmap (--batch, --level=3, --risk=2)
     - XSS: dalfox, custom payloads
     - SSTI: tplmap, custom payloads
     - Command injection: commix, custom payloads
  4. Fuzzing: ffuf (dirs, files, params, headers, vhosts)
  5. Auth testing: token manipulation, IDOR, JWT analysis
  6. Misconfigurations: CORS, CSP, security headers, TLS
  7. Web3 testing: slither, mythril, foundry, echidna
  
  Tools: nuclei, sqlmap, dalfox, ffuf, arjun, paramspider,
         graphql-scanner, slither, mythril, foundry
```

### 3. PoC Development (Hephaestus)
```
POC_DEV for finding:
  1. Analyze vulnerability mechanics
  2. Design minimal, non-destructive PoC
  3. Test locally if environment can be replicated
  4. Single monitored request against target
  5. Capture evidence (screenshots, req/res logs)
  6. Identify chaining opportunities
  7. ⚠️ If destructive test needed → FLAG FOR HUMAN APPROVAL
  
  Read-only exploitation ONLY:
  - Time-based: prove SQLi via SLEEP() not data extraction
  - DNS callback: prove SSRF via DNS lookup not metadata access
  - HTTP callback: prove XSS via callback not cookie theft
  - Contract call: prove access via view function not state change
```

### 4. Validation (Nemesis)
```
VALIDATE finding:
  1. Reproduce from scratch 3×
  2. Test with 3+ alternative payloads
  3. Test on 3+ similar endpoints (systemic check)
  4. Run FP detection heuristics
  5. Assign confidence score (0-1)
  6. Threshold: 0.8 for CONFIRMED
  
  FP detection:
  - Response deduplication (hash comparison)
  - Soft 404 detection (word/line count analysis)
  - WAF false positive patterns
  - Scanner-known false positives
```

## Skills Used
### Recon
- `enumerate_subdomains` — Multi-tool subdomain discovery
- `resolve_dns` — DNS resolution with dnsx
- `probe_http` — HTTP probing with httpx
- `scan_ports` — Port scanning with naabu
- `discover_content` — Directory/endpoint discovery
- `analyze_js` — JS extraction and secret scanning
- `fingerprint_tech` — Technology identification
- `find_contracts` — Web3 contract discovery

### Hunting
- `scan_templates` — Nuclei template scanning
- `fuzz_params` — Parameter fuzzing
- `test_sqli` — SQL injection testing
- `test_xss` — XSS testing
- `test_auth` — Authorization testing
- `test_graphql` — GraphQL vulnerability testing
- `analyze_contract` — Smart contract analysis

### Exploit
- `design_poc` — Design PoC approach
- `test_locally` — Local environment testing
- `deploy_safe_poc` — Monitored target execution
- `capture_evidence` — Evidence collection
- `identify_chains` — Escalation path finding
- `flag_for_approval` — Human approval request

### Validation
- `reproduce_finding` — Fresh reproduction
- `test_alternative_payloads` — Payload variation
- `test_systemic` — Similar endpoint testing
- `run_fp_check` — False positive heuristics
- `score_confidence` — Confidence scoring
- `package_evidence` — Evidence bundle creation

## Integration
- Hermes profile: `ares`
- Personality: `agents/execution/soul/SOUL.md`
- Sub-agents: recon (Aegis), vuln-hunter (Artemis), exploit-dev (Hephaestus), validator (Nemesis)
