"""
Smart contract analyzer — static analysis, vulnerability detection for Solidity contracts.
"""

from hermes.tools.registry import tool, ToolCategory


COMMON_WEB3_VULNS = {
    "reentrancy": {
        "severity": "HIGH",
        "description": "External call before state update allows re-entrant calls that drain funds",
        "detection_signatures": [
            r"\.call\{value:",
            r"\.transfer\(",
            r"\.send\(",
        ],
        "mitigation": "Use Checks-Effects-Interactions pattern or ReentrancyGuard",
    },
    "access_control": {
        "severity": "HIGH",
        "description": "Missing or insufficient access controls on privileged functions",
        "detection_signatures": [
            r"onlyOwner",
            r"require\(msg\.sender",
            r"Ownable",
        ],
        "mitigation": "Implement proper role-based access control (OpenZeppelin AccessControl)",
    },
    "arithmetic": {
        "severity": "MEDIUM",
        "description": "Integer overflow/underflow in arithmetic operations (pre-Solidity 0.8)",
        "detection_signatures": [
            r"\+",
            r"-",
            r"\*",
        ],
        "mitigation": "Use Solidity >= 0.8.0 (built-in overflow checks) or SafeMath",
    },
    "oracle_manipulation": {
        "severity": "HIGH",
        "description": "Reliance on manipulable price oracle (spot price from DEX pair)",
        "detection_signatures": [
            r"getReserves\(",
            r"getAmountsOut",
            r"balanceOf\(.*pair",
        ],
        "mitigation": "Use time-weighted average price (TWAP) or Chainlink oracles",
    },
    "frontrunning": {
        "severity": "MEDIUM",
        "description": "Transaction ordering dependence allows MEV extraction",
        "detection_signatures": [
            r"block\.timestamp",
            r"block\.number",
            r"tx\.origin",
        ],
        "mitigation": "Use commit-reveal schemes or private mempool",
    },
    "flash_loan": {
        "severity": "HIGH",
        "description": "Protocol vulnerable to flash loan manipulation of pricing or governance",
        "detection_signatures": [
            r"flashLoan\(",
            r"flash_loan",
        ],
        "mitigation": "Price checks before and after flash loan, 2-block TWAP minimum",
    },
    "delegatecall": {
        "severity": "CRITICAL",
        "description": "Unsafe delegatecall can lead to storage collision and contract takeover",
        "detection_signatures": [
            r"\.delegatecall\(",
            r"address\(.*\)\.delegatecall",
        ],
        "mitigation": "Use stateless library contracts only, never delegatecall to user-controlled addresses",
    },
    "selfdestruct": {
        "severity": "MEDIUM",
        "description": "selfdestruct can be used to force-send ETH, breaking invariants",
        "detection_signatures": [
            r"selfdestruct\(",
            r"suicide\(",
        ],
        "mitigation": "Never rely on address(this).balance for accounting logic",
    },
}


@tool(
    name="analyze_smart_contract",
    category=ToolCategory.WEB3,
    agent="artemis",
    description="Static analysis of smart contracts for common Web3 vulnerabilities",
    tags=["web3", "smart-contract", "solidity", "audit"],
)
def analyze_smart_contract(
    contract_source: str = "",
    contract_address: str = "",
    network: str = "ethereum",
) -> dict:
    """
    Analyze a smart contract for common Web3 vulnerabilities.

    Args:
        contract_source: Solidity source code (if available)
        contract_address: Contract address (for bytecode analysis)
        network: Blockchain network (ethereum, bsc, polygon, arbitrum, optimism)

    Returns:
        dict with vulnerability findings and recommendations
    """
    findings = []

    if contract_source:
        for vuln_name, vuln_data in COMMON_WEB3_VULNS.items():
            detected_signatures = []
            for sig in vuln_data["detection_signatures"]:
                import re
                if re.search(sig, contract_source):
                    detected_signatures.append(sig)

            if detected_signatures:
                findings.append({
                    "vulnerability": vuln_name,
                    "severity": vuln_data["severity"],
                    "description": vuln_data["description"],
                    "matched_patterns": detected_signatures,
                    "mitigation": vuln_data["mitigation"],
                })

    return {
        "contract_address": contract_address if contract_address else "source_analysis_only",
        "network": network,
        "findings": findings,
        "finding_count": len(findings),
        "high_severity": [f for f in findings if f["severity"] in ("HIGH", "CRITICAL")],
        "recommendation": "Run slither and mythril for deeper bytecode-level analysis",
    }
