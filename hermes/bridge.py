"""
Hermes Skill Bridge — connects Hermes agent skills to tool implementations.

Maps SKILL.md workflows to actual tool invocations via the ToolRegistry.
Allows Hermes agents to discover and call tools through the skill system.
"""

from hermes.tools.registry import get_registry, ToolRegistry, ToolCategory, ToolMeta

# Direct imports for tool registration
from hermes.tools.recon.subdomain_enum import enumerate_subdomains
from hermes.tools.recon.dns_resolve import resolve_dns
from hermes.tools.recon.http_probe import probe_http
from hermes.tools.recon.content_discovery import discover_content
from hermes.tools.recon.js_analyzer import analyze_js
from hermes.tools.recon.tech_fingerprint import fingerprint_tech
from hermes.tools.recon.secret_scanner import scan_secrets
from hermes.tools.analysis.waf_detector import detect_waf
from hermes.tools.analysis.graphql_analyzer import detect_graphql
from hermes.tools.analysis.response_analyzer import analyze_response
from hermes.tools.analysis.jwt_analyzer import analyze_jwt
from hermes.tools.exploitation.poc_engine import (
    design_poc, deploy_safe_poc, identify_chains, simulate_impact,
)
from hermes.tools.web3.contract_analyzer import analyze_smart_contract
from hermes.tools.web3.proxy_detector import detect_proxy_pattern
from hermes.tools.reporting.cvss_calculator import calculate_cvss
from hermes.tools.reporting.report_formatter import format_finding_for_submission
from hermes.tools.utility.scope_check import check_scope
from hermes.tools.utility.connectivity import verify_connectivity


class HermesSkillBridge:
    """
    Bridge between Hermes skill system and tool implementations.

    Hermes agents use SKILL.md workflows. This bridge maps those workflows
    to actual tool calls via the ToolRegistry.
    """

    def __init__(self):
        self.registry = get_registry()

    def get_agent_tools(self, agent_name: str) -> list[dict]:
        """Get all tools available to an agent, in Hermes-readable format."""
        tool_metas = self.registry.list_by_agent(agent_name)

        # Also include shared tools (agent="all")
        shared = [
            meta for name, (meta, _) in self.registry._tools.items()
            if meta.agent == "all"
        ]

        all_metas = tool_metas + shared

        return [
            {
                "name": meta.name,
                "description": meta.description,
                "category": meta.category.value,
                "requires_scope_check": meta.requires_scope_check,
                "requires_approval": meta.requires_approval,
                "tags": meta.tags,
            }
            for meta in all_metas
        ]

    def get_skill_tool_map(self, skill_name: str) -> list[str]:
        """Map a SKILL to its required tools."""
        skill_tools = {
            "orch-001": [
                "delegate_task", "query_status", "review_finding",
                "approve_report", "trigger_kill_switch",
                "check_scope", "update_priority",
            ],
            "rnd-001": [
                "search_corpus", "query_cve", "analyze_finding",
                "detect_false_positive", "synthesize_pattern",
                "update_kb", "create_skill", "update_tool",
            ],
            "strat-001": [
                "profile_target", "map_attack_surface",
                "design_attack_paths", "create_playbook",
                "prioritize_paths", "draft_report",
                "check_scope", "analyze_smart_contract",
            ],
            "exec-001": [
                "enumerate_subdomains", "resolve_dns",
                "probe_http", "discover_content",
                "analyze_js", "fingerprint_tech", "scan_secrets",
                "detect_waf", "detect_graphql", "analyze_jwt",
                "design_poc", "deploy_safe_poc", "identify_chains",
                "calculate_cvss", "format_finding_for_submission",
                "verify_connectivity",
            ],
        }

        return skill_tools.get(skill_name, [])

    def get_recon_pipeline(self) -> list[str]:
        """Get the ordered recon pipeline tool sequence."""
        return [
            "enumerate_subdomains",
            "resolve_dns",
            "probe_http",
            "fingerprint_tech",
            "discover_content",
            "analyze_js",
            "scan_secrets",
        ]

    def get_hunt_pipeline(self) -> list[str]:
        """Get the ordered vulnerability hunting tool sequence."""
        return [
            "detect_waf",
            "detect_graphql",
            "analyze_response",
            "analyze_jwt",
            # Actual vuln scanning tools (nuclei, sqlmap, etc.)
            # are called via subprocess/mcp, not Python tools
        ]

    def get_poc_pipeline(self) -> list[str]:
        """Get the PoC development tool sequence."""
        return [
            "design_poc",
            "identify_chains",
            "simulate_impact",
            "deploy_safe_poc",  # Requires approval
        ]

    def get_report_pipeline(self) -> list[str]:
        """Get the reporting tool sequence."""
        return [
            "calculate_cvss",
            "format_finding_for_submission",
        ]

    def validate_workflow(self, workflow_steps: list[str]) -> dict:
        """Validate that all tools in a workflow exist in the registry."""
        missing = []
        available = []

        for step in workflow_steps:
            if self.registry.get(step) is not None:
                available.append(step)
            else:
                missing.append(step)

        return {
            "valid": len(missing) == 0,
            "available": available,
            "missing": missing,
            "total_steps": len(workflow_steps),
        }

    def get_full_workflow(self) -> dict:
        """Get the complete hunt workflow with all tool stages."""
        return {
            "stages": {
                "recon": {
                    "tools": self.get_recon_pipeline(),
                    "validation": self.validate_workflow(self.get_recon_pipeline()),
                },
                "hunt": {
                    "tools": self.get_hunt_pipeline(),
                    "validation": self.validate_workflow(self.get_hunt_pipeline()),
                },
                "poc": {
                    "tools": self.get_poc_pipeline(),
                    "validation": self.validate_workflow(self.get_poc_pipeline()),
                    "note": "deploy_safe_poc requires human approval",
                },
                "report": {
                    "tools": self.get_report_pipeline(),
                    "validation": self.validate_workflow(self.get_report_pipeline()),
                },
            },
            "total_tools_registered": len(self.registry),
        }


# Initialize — imports trigger @tool decorator registrations
_bridge = HermesSkillBridge()
