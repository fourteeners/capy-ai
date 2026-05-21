"""
MCP Bridge — connects Hermes agents to MCP servers running security tools.

Maps tool registry entries to MCP tool invocations.
Supports local (subprocess) and remote (HTTP) MCP servers.
"""

import json
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from hermes.tools.registry import get_registry, ToolCategory, ToolMeta, ToolStatus


@dataclass
class MCPToolDefinition:
    """Definition of an MCP-exposed security tool."""
    name: str
    server: str
    description: str
    category: ToolCategory
    parameters: dict = field(default_factory=dict)
    timeout_seconds: int = 300
    rate_limit_per_sec: float = 0


class MCPBridge:
    """
    Bridge between Hermes ToolRegistry and MCP security tool servers.

    Usage:
        bridge = MCPBridge()
        bridge.register_mcp_tools()
        result = bridge.call_tool("subfinder", {"domain": "example.com"})
    """

    def __init__(self):
        self.registry = get_registry()
        self._mcp_definitions: dict[str, MCPToolDefinition] = {}
        self._tool_stats: dict[str, dict] = {}

    def register_mcp_tool(self, tool_def: MCPToolDefinition) -> None:
        """Register a single MCP tool with the registry."""
        self._mcp_definitions[tool_def.name] = tool_def

        # Create a wrapper that calls MCP
        def mcp_wrapper(**kwargs):
            return self.call_tool(tool_def.name, **kwargs)

        meta = ToolMeta(
            name=tool_def.name,
            category=tool_def.category,
            description=tool_def.description,
            agent="mcp",
            status=ToolStatus.ACTIVE,
            version="1.0.0",
            requires_scope_check=True,
            rate_limit_per_sec=tool_def.rate_limit_per_sec,
            tags=[tool_def.server, "mcp"],
        )

        self.registry.register(meta, mcp_wrapper)

    def register_all_from_config(self) -> int:
        """Register all tools from MCP server configs. Returns count."""
        from hermes.tools.mcp.server_config import TOOL_SERVERS
        count = 0
        for server_name, server_config in TOOL_SERVERS.items():
            for tool_def in server_config.get("tools", []):
                self.register_mcp_tool(MCPToolDefinition(
                    name=tool_def["name"],
                    server=server_name,
                    description=tool_def.get("description", ""),
                    category=ToolCategory[tool_def.get("category", "RECON").upper()],
                    parameters=tool_def.get("parameters", {}),
                    timeout_seconds=tool_def.get("timeout", 300),
                    rate_limit_per_sec=tool_def.get("rate_limit", 0),
                ))
                count += 1
        return count

    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call an MCP tool by name. Routes to correct server and transport.

        Supports:
        - Local subprocess (CLI tools: subfinder, nuclei, etc.)
        - Local Python (analysis tools)
        - HTTP MCP server (remote tools)
        """
        tool_def = self._mcp_definitions.get(tool_name)
        if not tool_def:
            return {"error": f"Unknown MCP tool: {tool_name}"}

        server = tool_def.server
        timeout = tool_def.timeout_seconds

        start = time.monotonic()
        result = self._dispatch(server, tool_name, kwargs, timeout)
        duration = time.monotonic() - start

        # Track stats
        self._tool_stats.setdefault(tool_name, {"calls": 0, "errors": 0, "total_duration": 0})
        self._tool_stats[tool_name]["calls"] += 1
        self._tool_stats[tool_name]["total_duration"] += duration
        if isinstance(result, dict) and result.get("error"):
            self._tool_stats[tool_name]["errors"] += 1

        return result

    def _dispatch(self, server: str, tool_name: str, kwargs: dict, timeout: int) -> Any:
        """Dispatch to the correct transport based on server config."""
        from hermes.tools.mcp.server_config import TOOL_SERVERS

        server_config = TOOL_SERVERS.get(server, {})
        transport = server_config.get("transport", "subprocess")

        if transport == "subprocess":
            return self._subprocess_call(server_config, tool_name, kwargs, timeout)
        elif transport == "python":
            return self._python_call(server_config, tool_name, kwargs)
        elif transport == "http":
            return self._http_call(server_config, tool_name, kwargs, timeout)
        else:
            return {"error": f"Unknown transport: {transport}"}

    def _subprocess_call(self, config: dict, tool_name: str, kwargs: dict, timeout: int) -> dict:
        """Execute a CLI tool via subprocess."""
        command_template = config.get("command_template", "")
        if not command_template:
            return {"error": f"No command template for {tool_name}"}

        # Build command from template
        cmd_parts = command_template.split()
        resolved_cmd = []
        for part in cmd_parts:
            if part.startswith("{") and part.endswith("}"):
                key = part[1:-1]
                val = kwargs.get(key)
                if val is not None:
                    if isinstance(val, list):
                        resolved_cmd.extend(str(v) for v in val)
                    else:
                        resolved_cmd.append(str(val))
            else:
                resolved_cmd.append(part)

        if not resolved_cmd:
            return {"error": "Empty command after resolution"}

        try:
            proc = subprocess.run(
                resolved_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "returncode": proc.returncode,
                "success": proc.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Tool timed out after {timeout}s", "success": False}
        except FileNotFoundError:
            return {"error": f"Tool binary not found: {resolved_cmd[0]}", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def _python_call(self, config: dict, tool_name: str, kwargs: dict) -> dict:
        """Execute a Python-based tool."""
        handler_path = config.get("handler")
        if not handler_path:
            return {"error": f"No Python handler for {tool_name}"}

        try:
            import importlib
            module_path, func_name = handler_path.rsplit(":", 1)
            module = importlib.import_module(module_path)
            handler = getattr(module, func_name)
            return handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}

    def _http_call(self, config: dict, tool_name: str, kwargs: dict, timeout: int) -> dict:
        """Execute a tool via HTTP MCP server."""
        base_url = config.get("base_url", "")
        endpoint = config.get("endpoints", {}).get(tool_name, f"/tools/{tool_name}")

        try:
            import urllib.request
            url = f"{base_url.rstrip('/')}{endpoint}"
            data = json.dumps(kwargs).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e), "success": False}

    def get_stats(self, tool_name: str) -> dict:
        """Get call statistics for an MCP tool."""
        return self._tool_stats.get(tool_name, {"calls": 0, "errors": 0, "total_duration": 0})

    def get_all_stats(self) -> dict:
        """Get stats for all MCP tools."""
        return dict(self._tool_stats)


# Singleton
_mcp_bridge: Optional[MCPBridge] = None


def get_mcp_bridge() -> MCPBridge:
    global _mcp_bridge
    if _mcp_bridge is None:
        _mcp_bridge = MCPBridge()
    return _mcp_bridge
