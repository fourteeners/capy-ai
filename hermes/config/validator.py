"""
Config Validator — validates agents.yml, scope definitions, and kill-switch config.

Catches misconfiguration before fleet launch, preventing runtime errors.
"""

import re
from typing import Optional


REQUIRED_AGENT_FIELDS = ["active", "clone-from", "personality"]
VALID_PERSONALITY_VALUES = ["orchestrator", "rnd", "plan-strategy", "execution"]
VALID_CAVEMAN_LEVELS = ["lite", "full", "ultra"]
REQUIRED_ENV_FIELDS = ["API_SERVER_PORT", "API_SERVER_KEY"]
DOMAIN_PATTERN = re.compile(r"^(\*\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
WILDCARD_PATTERN = re.compile(r"^\*\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$")


def validate_agents_config(config: dict) -> dict:
    """
    Validate agents.yml configuration.

    Returns:
        dict with 'valid', 'errors' (list), 'warnings' (list)
    """
    errors = []
    warnings = []

    if not config:
        return {"valid": False, "errors": ["Empty configuration"], "warnings": []}

    agent_names = list(config.keys())
    ports_seen = set()

    for name, agent_config in config.items():
        if not isinstance(agent_config, dict):
            errors.append(f"Agent '{name}': must be a dictionary")
            continue

        # Check required fields
        for field in REQUIRED_AGENT_FIELDS:
            if field not in agent_config:
                errors.append(f"Agent '{name}': missing required field '{field}'")

        # Validate clone-from
        clone_from = agent_config.get("clone-from", "false")
        if clone_from != "false" and clone_from not in agent_names:
            errors.append(f"Agent '{name}': clone-from '{clone_from}' does not exist")

        # Validate personality
        personality = agent_config.get("personality", "")
        if personality and personality not in VALID_PERSONALITY_VALUES:
            errors.append(f"Agent '{name}': invalid personality '{personality}'. Must be one of: {VALID_PERSONALITY_VALUES}")

        # Validate env
        env = agent_config.get("env", {})
        for field in REQUIRED_ENV_FIELDS:
            if field not in env:
                errors.append(f"Agent '{name}': missing env.{field}")

        # Check port conflicts
        port = env.get("API_SERVER_PORT")
        if port:
            try:
                p = int(port)
                if p < 1024 or p > 65535:
                    errors.append(f"Agent '{name}': port {p} out of range (1024-65535)")
                if p in ports_seen:
                    errors.append(f"Agent '{name}': port {p} conflicts with another agent")
                ports_seen.add(p)
            except (ValueError, TypeError):
                errors.append(f"Agent '{name}': invalid port '{port}'")

        # Validate caveman level
        caveman_level = env.get("CAVEMAN_LEVEL", "")
        if caveman_level and caveman_level not in VALID_CAVEMAN_LEVELS:
            errors.append(f"Agent '{name}': invalid CAVEMAN_LEVEL '{caveman_level}'")

    # Validate dependency order (no circular clone-from)
    if len(agent_names) > 1:
        deps_ok = _check_circular_deps(config)
        if not deps_ok:
            errors.append("Circular dependency detected in clone-from chain")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_scope_definition(scope: dict) -> dict:
    """
    Validate a single program scope definition.

    Returns:
        dict with 'valid', 'errors'
    """
    errors = []

    # Required top-level field
    if "program" not in scope:
        errors.append("Missing 'program' field")

    in_scope = scope.get("in_scope", {})
    if not in_scope:
        errors.append("Missing 'in_scope' section")

    domains = in_scope.get("domains", [])
    ips = in_scope.get("ips", [])

    if not domains and not ips:
        errors.append("in_scope must have at least one domain or IP")

    for domain in domains:
        if not WILDCARD_PATTERN.match(domain) and not DOMAIN_PATTERN.match(domain):
            errors.append(f"Invalid domain pattern: '{domain}'")

    # Check test types
    test_types = scope.get("test_types", {})
    allowed = test_types.get("allowed", [])
    restricted = test_types.get("restricted", [])

    for action in allowed:
        if action in restricted:
            errors.append(f"Action '{action}' in both allowed and restricted — check config")

    # Check rate limits
    rate_limits = scope.get("rate_limits", {})
    rps = rate_limits.get("requests_per_second", 0)
    if isinstance(rps, (int, float)) and rps <= 0:
        errors.append("Rate limit requests_per_second must be > 0")
    if isinstance(rps, (int, float)) and rps > 50:
        errors.append("Rate limit > 50 req/s may be excessive — verify with program policy")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def validate_kill_switch_config(config: dict) -> dict:
    """
    Validate kill-switch configuration.

    Returns:
        dict with 'valid', 'errors'
    """
    errors = []

    if not config.get("enabled", True):
        errors.append("Kill-switch must be enabled in production")

    auto_triggers = config.get("auto_triggers", {})
    valid_trigger_types = ["critical", "high"]

    for trigger_name, severity in auto_triggers.items():
        if severity not in valid_trigger_types:
            errors.append(f"Kill-switch trigger '{trigger_name}': invalid severity '{severity}'")

    cooldown = config.get("cooldown", {})
    after_first = cooldown.get("after_trigger", 0)
    after_third = cooldown.get("after_third_trigger", 0)

    if after_first < 0:
        errors.append("Cooldown after_trigger cannot be negative")
    if after_third < after_first:
        errors.append("Cooldown after_third_trigger should be >= after_trigger")

    human = config.get("human_override", {})
    if not human.get("required_for_resume", True):
        errors.append("Human override for resume must be enabled in production")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def validate_all() -> dict:
    """
    Validate all system configurations.

    Returns:
        dict with overall validity + per-section results
    """
    results = {}

    # Validate agents.yml
    try:
        import yaml
        with open("hermes/config/agents.yml") as f:
            agents_config = yaml.safe_load(f)
        results["agents_config"] = validate_agents_config(agents_config)
    except FileNotFoundError:
        results["agents_config"] = {"valid": False, "errors": ["agents.yml not found"]}
    except Exception as e:
        results["agents_config"] = {"valid": False, "errors": [str(e)]}

    return {
        "valid": all(r["valid"] for r in results.values()),
        "results": results,
    }


def _check_circular_deps(config: dict) -> bool:
    """Check for circular dependencies in clone-from chains."""
    graph = {}
    for name, agent_config in config.items():
        clone_from = agent_config.get("clone-from", "false")
        if clone_from != "false":
            graph.setdefault(name, []).append(clone_from)

    # DFS cycle detection
    visited = set()
    stack = set()

    def dfs(node):
        visited.add(node)
        stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if not dfs(neighbor):
                    return False
            elif neighbor in stack:
                return False
        stack.discard(node)
        return True

    return all(dfs(node) for node in graph if node not in visited)
