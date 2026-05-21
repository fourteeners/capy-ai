# CAPY Bug Hunter — Tools Manifest

## Reconnaissance Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `enumerate_subdomains` | Multi-tool subdomain discovery | aegis | active |
| `resolve_dns` | DNS resolution & validation | aegis | active |
| `probe_http` | HTTP service detection & fingerprinting | aegis | active |
| `scan_ports` | Port scanning (non-standard services) | aegis | active |
| `discover_content` | Directory & endpoint brute-force | aegis | active |
| `fetch_wayback` | Historical URL discovery | aegis | active |
| `crawl_js` | JS extraction & endpoint discovery | aegis | active |
| `scan_secrets` | Secret & credential scanning in JS | aegis | active |
| `fingerprint_tech` | Technology stack identification | aegis | active |
| `find_contracts` | Web3 smart contract discovery | aegis | active |

## Analysis Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `analyze_response` | HTTP response pattern analysis | artemis | active |
| `detect_waf` | WAF & CDN identification | artemis | active |
| `detect_graphql` | GraphQL endpoint & introspection detection | artemis | active |
| `parse_js_endpoints` | Extract API endpoints from JS | artemis | active |
| `detect_soft_404` | Soft 404 page detection | artemis | active |
| `analyze_cors` | CORS misconfiguration analysis | artemis | active |
| `analyze_jwt` | JWT token analysis & weakness detection | artemis | active |

## Vulnerability Scanning Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `scan_nuclei` | Template-based vulnerability scanning | artemis | active |
| `test_sqli` | SQL injection detection (sqlmap) | artemis | active |
| `test_xss` | XSS detection (dalfox + custom) | artemis | active |
| `test_ssti` | Server-side template injection | artemis | active |
| `test_ssrf` | SSRF detection & validation | artemis | active |
| `test_xxe` | XML external entity injection | artemis | active |
| `test_command_injection` | OS command injection | artemis | active |
| `test_idor` | Insecure direct object reference | artemis | active |
| `test_open_redirect` | Open redirect detection | artemis | active |
| `fuzz_params` | Parameter fuzzing & discovery | artemis | active |
| `fuzz_directories` | Directory brute-force | artemis | active |
| `fuzz_headers` | HTTP header manipulation | artemis | active |
| `fuzz_vhosts` | Virtual host discovery | artemis | active |
| `test_auth_bypass` | Authentication bypass testing | artemis | active |
| `test_graphql_vulns` | GraphQL vulnerability testing | artemis | active |

## Web3 Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `analyze_solidity` | Static analysis with Slither | artemis | active |
| `analyze_bytecode` | Bytecode analysis with Mythril | artemis | active |
| `fuzz_contract` | Contract fuzzing with Echidna/Foundry | artemis | active |
| `trace_transaction` | Transaction trace analysis | artemis | active |
| `detect_proxy_pattern` | Proxy/upgradeable contract detection | aegis | active |
| `analyze_oracle` | Oracle dependency & manipulation analysis | artemis | active |
| `audit_access_control` | Access control audit (foundry) | artemis | active |
| `simulate_exploit` | Local fork exploit simulation | hephaestus | active |

## Exploitation Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `design_poc` | Design minimal proof-of-concept | hephaestus | active |
| `deploy_safe_poc` | Execute non-destructive PoC | hephaestus | active |
| `test_locally` | Test exploit in isolated environment | hephaestus | active |
| `capture_evidence` | Screenshots, logs, reproduction scripts | hephaestus | active |
| `identify_chains` | Find vulnerability escalation paths | hephaestus | active |
| `simulate_impact` | Model potential impact (read-only) | hephaestus | active |

## Validation Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `reproduce_finding` | Reproduce finding from scratch | nemesis | active |
| `test_alternative_payloads` | Test with varied payloads/encodings | nemesis | active |
| `test_systemic` | Check if finding exists on similar endpoints | nemesis | active |
| `run_fp_check` | False positive detection heuristics | nemesis | active |
| `score_confidence` | Final confidence scoring | nemesis | active |
| `package_evidence` | Evidence bundle creation | nemesis | active |

## Reporting Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `draft_report` | Generate submission-ready report | odysseus | active |
| `calculate_cvss` | CVSS v3.1 score calculation | odysseus | active |
| `format_finding` | Standardize finding format | odysseus | active |
| `generate_poc_script` | Generate reproduction script | odysseus | active |

## Orchestration Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `delegate_task` | Assign task to team lead | athena | active |
| `query_status` | Check agent status | athena | active |
| `review_finding` | Quality review a finding | athena | active |
| `approve_report` | Approve for platform submission | athena | active |
| `trigger_kill_switch` | Emergency halt | athena | active |
| `resume_operations` | Resume after kill-switch | athena | active |
| `update_priority` | Reprioritize targets | athena | active |

## Knowledge Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `search_corpus` | Search bug report corpus | prometheus | active |
| `query_cve` | CVE database lookup | prometheus | active |
| `analyze_finding` | Pattern matching & enrichment | prometheus | active |
| `detect_false_positive` | Advanced FP detection | prometheus | active |
| `synthesize_pattern` | Generalize from specific findings | prometheus | active |
| `update_kb` | Write/update knowledge base | prometheus | active |
| `create_skill` | Register new SKILL | prometheus | active |
| `update_tool` | Modify existing tool | prometheus | active |
| `search_web` | External research | prometheus | active |

## Utility Tools

| Tool | Purpose | Agent | Status |
|------|---------|-------|--------|
| `check_scope` | Verify URL against program scope | all | active |
| `log_action` | Write to audit log | all | active |
| `compress_comms` | Apply Caveman protocol | all | active |
| `verify_connectivity` | Test target connectivity | aegis | active |
| `rate_limit_check` | Check current rate limit status | ares | active |
