"""
MCP Server Configuration — defines all security tool servers and their tools.

HexStrike-inspired: 150+ security tools organized into MCP server groups.
Each server group maps to a transport type (subprocess, python, http).
"""

TOOL_SERVERS: dict[str, dict] = {
    # ============================================================
    # Reconnaissance Server — subdomain, DNS, HTTP, discovery
    # ============================================================
    "recon-server": {
        "transport": "subprocess",
        "description": "Reconnaissance tools: subdomain enum, DNS, HTTP probing, content discovery",
        "tools": [
            {
                "name": "subfinder",
                "description": "Passive subdomain enumeration via multiple sources",
                "category": "RECON",
                "timeout": 120,
                "rate_limit": 0,
                "parameters": {"domain": "string", "output": "string", "silent": "bool"},
            },
            {
                "name": "amass_enum",
                "description": "OWASP Amass subdomain enumeration",
                "category": "RECON",
                "timeout": 300,
                "parameters": {"domain": "string", "passive": "bool"},
            },
            {
                "name": "dnsx",
                "description": "DNS resolution and probing",
                "category": "RECON",
                "timeout": 60,
                "parameters": {"domains_file": "string", "json": "bool"},
            },
            {
                "name": "httpx_probe",
                "description": "HTTP/HTTPS service probing with tech detection",
                "category": "RECON",
                "timeout": 120,
                "parameters": {"hosts_file": "string", "tech_detect": "bool", "json": "bool"},
            },
            {
                "name": "naabu_scan",
                "description": "Fast port scanning",
                "category": "RECON",
                "timeout": 180,
                "parameters": {"host": "string", "ports": "string", "rate": "int"},
            },
            {
                "name": "ffuf_fuzz",
                "description": "Directory and parameter fuzzing",
                "category": "RECON",
                "timeout": 300,
                "parameters": {"url": "string", "wordlist": "string", "extensions": "string"},
            },
            {
                "name": "katana_crawl",
                "description": "Web crawler for endpoint discovery",
                "category": "RECON",
                "timeout": 600,
                "parameters": {"url": "string", "depth": "int", "js": "bool"},
            },
            {
                "name": "waybackurls",
                "description": "Fetch URLs from Wayback Machine",
                "category": "RECON",
                "timeout": 60,
                "parameters": {"domain": "string"},
            },
        ],
    },

    # ============================================================
    # Vulnerability Scanner Server — nuclei, sqlmap, dalfox, etc.
    # ============================================================
    "vuln-scanner-server": {
        "transport": "subprocess",
        "description": "Vulnerability scanners: nuclei (templates), sqlmap (SQLi), dalfox (XSS)",
        "tools": [
            {
                "name": "nuclei_scan",
                "description": "Template-based vulnerability scanning",
                "category": "ANALYSIS",
                "timeout": 600,
                "parameters": {"target": "string", "templates": "string", "severity": "string", "json": "bool"},
            },
            {
                "name": "sqlmap_scan",
                "description": "Automated SQL injection detection and exploitation",
                "category": "EXPLOITATION",
                "timeout": 600,
                "parameters": {"url": "string", "data": "string", "technique": "string", "batch": "bool"},
            },
            {
                "name": "dalfox_scan",
                "description": "XSS vulnerability scanner with DOM analysis",
                "category": "ANALYSIS",
                "timeout": 300,
                "parameters": {"url": "string", "data": "string", "json": "bool"},
            },
            {
                "name": "tplmap_scan",
                "description": "Server-Side Template Injection detection",
                "category": "ANALYSIS",
                "timeout": 120,
                "parameters": {"url": "string", "data": "string", "os_shell": "bool"},
            },
            {
                "name": "commix_scan",
                "description": "Command injection detection and exploitation",
                "category": "EXPLOITATION",
                "timeout": 180,
                "parameters": {"url": "string", "data": "string"},
            },
            {
                "name": "graphql_scanner",
                "description": "GraphQL introspection and vulnerability scanning",
                "category": "ANALYSIS",
                "timeout": 60,
                "parameters": {"url": "string"},
            },
        ],
    },

    # ============================================================
    # Web3 / Smart Contract Server — slither, mythril, foundry
    # ============================================================
    "web3-server": {
        "transport": "subprocess",
        "description": "Smart contract analysis: slither, mythril, foundry, echidna",
        "tools": [
            {
                "name": "slither_analyze",
                "description": "Slither static analysis for Solidity",
                "category": "WEB3",
                "timeout": 300,
                "parameters": {"target": "string", "detectors": "string", "json": "bool"},
            },
            {
                "name": "mythril_analyze",
                "description": "Mythril symbolic execution for smart contracts",
                "category": "WEB3",
                "timeout": 600,
                "parameters": {"address": "string", "rpc": "string"},
            },
            {
                "name": "foundry_test",
                "description": "Foundry forge test suite execution",
                "category": "WEB3",
                "timeout": 600,
                "parameters": {"contract": "string", "fork_url": "string", "verbosity": "int"},
            },
            {
                "name": "echidna_fuzz",
                "description": "Echidna property-based fuzzing",
                "category": "WEB3",
                "timeout": 1800,
                "parameters": {"contract": "string", "config": "string", "test_limit": "int"},
            },
            {
                "name": "cast_call",
                "description": "Read smart contract state via cast call",
                "category": "WEB3",
                "timeout": 30,
                "parameters": {"address": "string", "signature": "string", "rpc_url": "string"},
            },
        ],
    },

    # ============================================================
    # Exploitation Server — PoC deployment, callbacks, validation
    # ============================================================
    "exploit-server": {
        "transport": "python",
        "description": "Safe PoC deployment, callback handlers, impact validation",
        "tools": [
            {
                "name": "dns_callback_test",
                "description": "Test vulnerability via DNS callback (SSRF, XXE, blind RCE)",
                "category": "EXPLOITATION",
                "handler": "hermes.tools.exploitation.callback_handlers:dns_callback_test",
            },
            {
                "name": "http_callback_test",
                "description": "Test vulnerability via HTTP callback (SSRF, blind XSS)",
                "category": "EXPLOITATION",
                "handler": "hermes.tools.exploitation.callback_handlers:http_callback_test",
            },
            {
                "name": "time_delay_test",
                "description": "Test vulnerability via time-based detection (SQLi, command injection)",
                "category": "EXPLOITATION",
                "handler": "hermes.tools.exploitation.callback_handlers:time_delay_test",
            },
            {
                "name": "validate_exploit",
                "description": "Validate exploit success non-destructively",
                "category": "EXPLOITATION",
                "handler": "hermes.tools.exploitation.callback_handlers:validate_exploit",
            },
        ],
    },

    # ============================================================
    # Intelligence Server — OSINT, threat intel, GitHub dorking
    # ============================================================
    "intel-server": {
        "transport": "python",
        "description": "OSINT and threat intelligence tools",
        "tools": [
            {
                "name": "github_dork",
                "description": "Search GitHub for leaked secrets, configs, credentials",
                "category": "RECON",
                "handler": "hermes.tools.mcp.handlers:github_dork",
            },
            {
                "name": "shodan_query",
                "description": "Query Shodan for exposed services",
                "category": "RECON",
                "handler": "hermes.tools.mcp.handlers:shodan_query",
            },
            {
                "name": "censys_query",
                "description": "Query Censys for certificate and host data",
                "category": "RECON",
                "handler": "hermes.tools.mcp.handlers:censys_query",
            },
            {
                "name": "crt_sh_query",
                "description": "Certificate Transparency log search via crt.sh",
                "category": "RECON",
                "handler": "hermes.tools.mcp.handlers:crt_sh_query",
            },
        ],
    },
}

# Command templates for subprocess-based tools
COMMAND_TEMPLATES: dict[str, str] = {
    "subfinder": "subfinder -d {domain} -silent",
    "amass_enum": "amass enum -d {domain} -passive",
    "dnsx": "dnsx -l {domains_file} -silent",
    "httpx_probe": "httpx -l {hosts_file} -tech-detect -silent -status-code -title",
    "naabu_scan": "naabu -host {host} -p {ports}",
    "ffuf_fuzz": "ffuf -u {url}/FUZZ -w {wordlist} -e {extensions}",
    "katana_crawl": "katana -u {url} -d {depth} -jc",
    "waybackurls": "waybackurls {domain}",
    "nuclei_scan": "nuclei -target {target} -t {templates} -severity {severity}",
    "sqlmap_scan": "sqlmap -u {url} --data {data} --technique {technique} --batch",
    "dalfox_scan": "dalfox url {url} --data {data}",
    "tplmap_scan": "tplmap -u {url} --data {data}",
    "commix_scan": "commix --url={url} --data={data}",
    "graphql_scanner": "graphql-scanner -u {url}",
    "slither_analyze": "slither {target} --detect {detectors}",
    "mythril_analyze": "mythril analyze -a {address} --rpc {rpc}",
    "foundry_test": "forge test --match-contract {contract} --fork-url {fork_url}",
    "echidna_fuzz": "echidna {contract} --config {config} --test-limit {test_limit}",
    "cast_call": "cast call {address} {signature} --rpc-url {rpc_url}",
}
