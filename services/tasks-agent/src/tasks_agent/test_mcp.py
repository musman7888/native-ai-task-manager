"""Step 5: Test MCP connection independently."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from agents.mcp import MCPServerStreamableHttp


async def main():
    mcp_url = os.getenv("TASKS_MCP_URL", "http://localhost:8000/mcp")
    print(f"Connecting to MCP server: {mcp_url}")
    print("-" * 40)

    try:
        async with MCPServerStreamableHttp(
            name="tasks-mcp",
            params={"url": mcp_url},
        ) as server:
            tools = await server.list_tools()
            print(f"\nDiscovered {len(tools)} tools:")
            for tool in tools:
                desc = tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
                print(f"  - {tool.name}: {desc}")

        print("\n" + "-" * 40)
        print("MCP connection test passed!")

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure tasks-mcp server is running:")
        print("  cd services/tasks-mcp && uv run tasks-mcp")


if __name__ == "__main__":
    asyncio.run(main())
