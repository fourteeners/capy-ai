"""
MCP Bridge — HexStrike-style security tool orchestration via MCP.

Bridges 150+ security tools (subfinder, nuclei, sqlmap, dalfox, ffuf, etc.)
to the ToolRegistry through MCP server integration.
"""

from hermes.tools.mcp.bridge import MCPBridge
from hermes.tools.mcp.server_config import TOOL_SERVERS

__all__ = ["MCPBridge", "TOOL_SERVERS"]
