"""
Web3 tools — smart contract analysis, transaction tracing, proxy detection.
"""

from hermes.tools.web3.contract_analyzer import analyze_smart_contract
from hermes.tools.web3.proxy_detector import detect_proxy_pattern

__all__ = ["analyze_smart_contract", "detect_proxy_pattern"]
