# Bug Bounty Methodology — CAPY Standard

## Phase 1: Target Selection & Scoping

### Target Selection Criteria
1. **Responsive programs** — Fast triage + competitive bounties
2. **Wide scope** — Wildcard domains, multiple assets, API endpoints
3. **New programs** — Less competition, fresh attack surface
4. **Tech stack match** — Our tools/skills align with target technology
5. **Bounty range** — Payouts justify the time investment

### Scope Mapping
- Parse program policy page
- Identify all in-scope domains, IPs, mobile apps, APIs
- Note exclusions and special conditions
- Set rate limits and test restrictions

## Phase 2: Reconnaissance

### Passive Recon (Zero packets to target)
1. **DNS enumeration** — crt.sh, SecurityTrails, DNSDumpster
2. **Subdomain discovery** — subfinder, amass (passive mode), assetfinder, chaos
3. **Wayback Machine** — gau, waybackurls, waymore
4. **GitHub dorking** — Organization repos, employee profiles, leaked configs
5. **Google dorking** — site:target.com filetype: extensions
6. **Shodan/Censys** — Passive infrastructure fingerprinting
7. **LinkedIn/Glassdoor** — Technology stack hints from job postings

### Active Recon
1. **DNS resolution** — dnsx, massdns
2. **HTTP probing** — httpx with tech detection, title, status
3. **Port scanning** — naabu (top ports), nmap (thorough)
4. **Content discovery** — ffuf, katana, dirsearch
5. **JS analysis** — subjs, LinkFinder, nuclei-secrets
6. **Screenshot** — gowitness/eyewitness for visual triage

## Phase 3: Vulnerability Discovery

### By Technology Stack
| Technology | Priority Tests |
|------------|---------------|
| Express/Node.js | Prototype pollution, JWT confusion, SSRF, deserialization |
| Django/Python | SSTI, SQL injection, admin panel exposure, DEBUG mode |
| Rails/Ruby | Mass assignment, YAML deserialization, ERB injection |
| Spring/Java | Actuator exposure, EL injection, deserialization |
| PHP/Laravel | SQLi, LFI, deserialization, .env exposure |
| React/SPA | API auth bypass, CORS, GraphQL, state manipulation |
| GraphQL | Introspection, field suggestions, batching attacks, depth DoS |
| Kubernetes | API server exposure, etcd, kubelet, dashboard |
| AWS | S3 bucket enumeration, metadata SSRF, IAM misconfig |

### By Vulnerability Class
See: `corpus/vulnerability-patterns/web2/` and `corpus/vulnerability-patterns/web3/`

## Phase 4: Validation & Escalation

1. **Reproduce** — Minimum 3 times from scratch
2. **Eliminate false positives** — Response dedup, soft 404, WAF blocks
3. **Escalate impact** — Find chains: low → medium → high → critical
4. **Document** — Exact reproduction, screenshots, request/response pairs

## Phase 5: Reporting

1. **Title** — Vulnerability class + affected component + impact
2. **Summary** — 2-3 sentence business impact
3. **Reproduction** — Step-by-step with exact commands
4. **Impact** — What an attacker could do
5. **Remediation** — Specific fix recommendation
6. **Supporting materials** — Screenshots, PoC video, script
