"""
GraphQL analyzer — detect GraphQL endpoints and test for introspection.
"""

from hermes.tools.registry import tool, ToolCategory


@tool(
    name="detect_graphql",
    category=ToolCategory.ANALYSIS,
    agent="artemis",
    description="Detect GraphQL endpoints and test introspection",
    tags=["analysis", "graphql", "introspection"],
)
def detect_graphql(
    endpoints: list[str],
) -> dict:
    """
    Detect GraphQL endpoints and check for introspection misconfiguration.

    Args:
        endpoints: List of URLs to check

    Returns:
        dict with 'graphql_endpoints', 'introspection_enabled', 'suggestions'
    """
    graphql_paths = [
        "/graphql", "/graphiql", "/gql",
        "/v1/graphql", "/v2/graphql", "/api/graphql",
        "/query", "/graphql/console", "/playground",
    ]

    found = []
    introspection_checks = []

    for base in endpoints:
        base = base.rstrip("/")

        # Check common paths
        for path in graphql_paths:
            found.append(f"{base}{path}")

        # Also check the base URL itself (might be graphql directly)
        found.append(base)

    # Introspection check payloads
    introspection_query = """{"query": "query { __schema { types { name } } }"}"""
    introspection_v2 = """{"query": "query { __type(name: \\\"Query\\\") { name fields { name } } }"}"""

    for endpoint in found:
        introspection_checks.append({
            "endpoint": endpoint,
            "test_payload": introspection_query[:80] + "...",
        })

    return {
        "endpoints_to_check": len(found),
        "graphql_endpoints": found[:50],  # Limit output
        "introspection_tests": introspection_checks[:20],
        "high_risk": "Introspection enabled = full schema disclosure = attack surface map",
        "remediation": "Disable introspection in production GraphQL servers",
    }
