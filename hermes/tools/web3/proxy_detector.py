"""
Proxy pattern detector — detect upgradeable proxy patterns in smart contracts.
"""

from hermes.tools.registry import tool, ToolCategory


PROXY_PATTERNS = {
    "EIP-1967": {
        "implementation_slot": "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc",
        "admin_slot": "0xb53127684a568b31730ae13b9f8a6016e243fcac26bfb1df3d8c3cf0969aa9b7",
        "risk": "MEDIUM",
        "note": "Standard UUPS/Transparent proxy. Check admin is not compromised.",
    },
    "OpenZeppelin Transparent": {
        "signatures": ["admin()", "implementation()", "upgradeTo(address)"],
        "risk": "MEDIUM",
        "note": "Well-tested but admin key is single point of failure.",
    },
    "UUPS": {
        "signatures": ["proxiableUUID()", "upgradeTo(address)", "upgradeToAndCall(address,bytes)"],
        "risk": "HIGH",
        "note": "Upgrade logic in implementation — storage collision risk if not careful.",
    },
    "Beacon Proxy": {
        "signatures": ["beacon()", "implementation()", "upgrade(address)"],
        "risk": "MEDIUM",
        "note": "Single beacon upgrades many proxies simultaneously.",
    },
    "Diamond (EIP-2535)": {
        "signatures": ["diamondCut((address,uint8,bytes4[])[],address,bytes)", "facetAddress(bytes4)"],
        "risk": "LOW",
        "note": "Complex but powerful. Facet management is key risk.",
    },
    "Custom Proxy": {
        "signatures": ["delegatecall"],
        "risk": "HIGH",
        "note": "Non-standard proxy — needs manual review. High risk of storage collision.",
    },
}


@tool(
    name="detect_proxy_pattern",
    category=ToolCategory.WEB3,
    agent="aegis",
    description="Detect proxy/upgradeable patterns in smart contracts",
    tags=["web3", "proxy", "upgradeable", "detection"],
)
def detect_proxy_pattern(
    contract_addresses: list[str],
    bytecode_hints: list[dict] | None = None,  # [{"address": "0x...", "bytecode_fragment": "..."}]
) -> dict:
    """
    Detect proxy/upgradeable patterns in smart contracts.

    Proxy detection is critical for Web3 security because upgradeability
    means the contract logic can change — the admin key becomes a
    single point of failure.

    Args:
        contract_addresses: List of contract addresses to analyze
        bytecode_hints: Optional bytecode fragments for pattern matching

    Returns:
        dict with proxy detection results per contract
    """
    results = {}
    proxy_contracts = []

    for addr in contract_addresses:
        patterns_found = []
        risks = []

        if bytecode_hints:
            for hint in bytecode_hints:
                if hint.get("address", "").lower() == addr.lower():
                    fragment = hint.get("bytecode_fragment", "")

                    for pattern_name, pattern_data in PROXY_PATTERNS.items():
                        if "signatures" in pattern_data:
                            for sig in pattern_data["signatures"]:
                                if sig.lower() in fragment.lower():
                                    patterns_found.append(pattern_name)
                                    risks.append({"pattern": pattern_name, "risk": pattern_data["risk"]})
                                    break

        results[addr] = {
            "is_proxy": len(patterns_found) > 0,
            "patterns_detected": patterns_found,
            "risks": risks,
            "recommendation": (
                "Review admin key security, check for storage collisions, "
                "verify upgrade timelock" if patterns_found else
                "No proxy patterns detected (bytecode analysis limited)"
            ),
        }

        if patterns_found:
            proxy_contracts.append(addr)

    return {
        "contracts_analyzed": len(contract_addresses),
        "proxy_contracts": proxy_contracts,
        "proxy_count": len(proxy_contracts),
        "results": results,
        "critical_note": "Proxy admin key = single point of failure. If compromised, all proxy logic can be replaced.",
    }
