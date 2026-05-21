"""
Analysis tools — WAF detection, GraphQL analysis, response analysis, CORS checks.
"""

from hermes.tools.analysis.waf_detector import detect_waf
from hermes.tools.analysis.graphql_analyzer import detect_graphql
from hermes.tools.analysis.response_analyzer import analyze_response
from hermes.tools.analysis.jwt_analyzer import analyze_jwt

__all__ = ["detect_waf", "detect_graphql", "analyze_response", "analyze_jwt"]
