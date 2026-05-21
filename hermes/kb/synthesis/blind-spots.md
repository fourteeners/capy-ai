# Blind Spots — What We're Weak At

*Last updated: 2025-01-01 | Author: logos (Analyst)*

## Currently Under-Tested

### 1. HTTP Request Smuggling
- **Coverage gap**: No dedicated tools or detection rules
- **Why**: Requires low-level HTTP parsing, not covered by standard scanners
- **Risk**: Can bypass WAF, poison caches, hijack sessions
- **Plan**: Add HTTP/2 downgrade + CL.TE / TE.CL detection in next tool iteration

### 2. WebSocket Security
- **Coverage gap**: No WebSocket-specific scanning
- **Why**: Standard tools focus on HTTP, not WebSocket handshake
- **Risk**: CSWSH, authorization bypass
- **Plan**: Add WebSocket endpoint enumeration + auth bypass testing

### 3. Prototype Pollution
- **Coverage gap**: No automated detection for prototype pollution
- **Why**: Requires JavaScript runtime analysis
- **Risk**: Can lead to XSS, RCE in Node.js applications
- **Plan**: Add `ppfuzz` or custom prototype pollution detection

### 4. Business Logic Vulnerabilities
- **Coverage gap**: Heavily reliant on manual analysis
- **Why**: Business logic is context-dependent, hard to automate
- **Risk**: Can be highest impact (payment bypass, privilege issues)
- **Plan**: Add workflow-based testing with state machine models

### 5. Web3: MEV / Frontrunning
- **Coverage gap**: No MEV-specific analysis
- **Why**: Requires mempool monitoring, not just contract analysis
- **Risk**: Sandwich attacks, arbitrage extraction
- **Plan**: Add mempool listener + transaction simulation

### 6. Kubernetes / Container Security
- **Coverage gap**: No container-specific tools
- **Why**: Focus is web app, not infrastructure
- **Risk**: Container escape, secrets exposure, API server access
- **Plan**: Add kube-hunter or similar for Kubernetes targets

## Methodology Weaknesses

### Sequential Scanning
- We scan targets one at a time — limited throughput
- Parallel scanning framework exists but not optimized

### Token Usage (Pre-Caveman)
- Before Caveman protocol, inter-agent comms were verbose
- Caveman implementation reduced tokens by ~65%

### Web3-Web2 Bridge
- Web3 frontends often have web2 backends
- We test them separately — should test as integrated system
- Example: smart contract + frontend API + wallet integration

## Action Items
1. [ ] Add HTTP request smuggling detection (priority: HIGH)
2. [ ] Add WebSocket vulnerability scanning (priority: MEDIUM)
3. [ ] Integrate ppfuzz for prototype pollution (priority: MEDIUM)
4. [ ] Add mempool monitoring for MEV analysis (priority: LOW)
5. [ ] Build integrated web3+web2 testing workflow (priority: MEDIUM)
6. [ ] Optimize parallel scanning framework (priority: LOW)
