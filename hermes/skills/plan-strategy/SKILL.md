# SKILL: Attack Strategy & Planning

## Metadata
- **Skill ID**: `strat-001`
- **Version**: 1.0.0
- **Author**: CAPY Bug Hunter System
- **Category**: Strategy
- **Caveman Level**: full

## Purpose
Profile targets, design attack paths, prioritize by bounty potential, and create executable playbooks for the execution team.

## Core Capabilities

### 1. Target Profiling
```
PROFILE target:
  Passive recon only — NO packets to target
  1. Technology fingerprinting:
     - Wappalyzer/BuiltWith ecosystem
     - HTTP response headers (Server, X-Powered-By, etc.)
     - JavaScript framework signatures
     - Cookie patterns
  2. Infrastructure mapping:
     - DNS: A, AAAA, CNAME, MX, NS, TXT records
     - CDN: Cloudflare, Akamai, Fastly, CloudFront detection
     - Cloud: AWS, GCP, Azure indicators
     - Certificate Transparency: crt.sh, CertSpotter
  3. Historical research:
     - Past breaches and disclosures
     - Bug bounty program history
     - Security audit reports
     - Wayback Machine snapshots
  4. Web3-specific:
     - Smart contract addresses (Etherscan, BscScan, etc.)
     - Protocol integrations and dependencies
     - Audit history (Immunefi, Code4rena, Sherlock)
     - TVL and economic impact
```

### 2. Attack Surface Mapping
```
MAP attack surface:
  Entry points:
    - Web forms (login, registration, search, contact, upload)
    - API endpoints (REST, GraphQL, WebSocket, gRPC)
    - Authentication flows (OAuth, JWT, SAML, session cookies)
    - File handling (upload, download, processing, conversion)
    - Third-party integrations (payment, analytics, chat, CDN)
    - Admin/management interfaces
  Web3 entry points:
    - Public/external functions
    - Proxy/upgrade patterns
    - Oracle dependencies
    - Cross-chain bridges
    - Governance mechanisms
```

### 3. Attack Path Design
```
DESIGN attack paths:
  For each entry point:
    1. What vulnerability classes are applicable?
    2. What is the exploitation complexity? (trivial/easy/moderate/hard)
    3. What is the potential impact? (CVSS-based)
    4. What is the chaining potential? (SSRF→RCE, XSS→ATO, etc.)
    5. What tools are needed?
    6. What bypass techniques if WAF blocks?
  
  Prioritization formula:
    Score = (exploitability × 0.3) + (impact × 0.3) + (bounty × 0.3) + (novelty × 0.1)
```

### 4. Report Drafting
```
DRAFT report:
  Structure:
    1. Title: [Vuln Class] in [Component] leading to [Impact]
    2. Summary: 2-3 sentence impact description
    3. Reproduction Steps: exact commands, inputs, outputs
    4. Impact: business context, data exposure, attack scenario
    5. Remediation: specific fix recommendation
    6. Supporting Materials: screenshots, request/response, PoC code
```

## Skills Used
- `profile_target` — Build target dossier
- `map_attack_surface` — Enumerate entry points
- `design_attack_paths` — Generate ranked attack paths
- `create_playbook` — Executable steps for Ares
- `prioritize_paths` — Rank by bounty potential
- `draft_report` — Submission-ready report
- `search_h1_reports` — Search HackerOne disclosures
- `check_scope` — Verify URL against program scope
- `analyze_smart_contract` — Web3 contract analysis

## Integration
- Hermes profile: `odysseus`
- Personality: `agents/plan-strategy/soul/SOUL.md`
- Sub-agents: strategist (Themistocles), target-profiler (Argus), attack-planner (Perseus)
