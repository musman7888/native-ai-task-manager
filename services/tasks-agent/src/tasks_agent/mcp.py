"""MCP server connection."""
from agents.mcp import MCPServerStreamableHttp
from .config import TASKS_MCP_URL


def create_mcp_server():
    """Create MCP server connection."""
    return MCPServerStreamableHttp(
        name="tasks-mcp",
        params={"url": TASKS_MCP_URL},
        cache_tools_list=True,
    )
