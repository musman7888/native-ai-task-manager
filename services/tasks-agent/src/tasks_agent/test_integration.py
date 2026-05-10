"""Step 6: Test agent + MCP integration - Create and Get task."""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents import Runner
from .agent import create_agent, create_run_config
from .mcp import create_mcp_server


async def main():
    print("Testing agent + MCP integration...")
    print("=" * 50)

    mcp_server = create_mcp_server()
    run_config = create_run_config()

    async with mcp_server:
        agent = create_agent(mcp_server)

        # Test 1: Create a task
        print("\n[TEST 1] Creating a task...")
        print("-" * 40)
        result = await Runner.run(
            agent,
            input="Create a task titled 'Review PR #123' with description 'Code review for feature branch'",
            run_config=run_config
        )
        print(f"Agent Response:\n{result.final_output}")

        # Test 2: List tasks to see the created task
        print("\n[TEST 2] Listing all tasks...")
        print("-" * 40)
        result = await Runner.run(
            agent,
            input="List all tasks",
            run_config=run_config
        )
        print(f"Agent Response:\n{result.final_output}")

        # Test 3: Get specific task details (agent should use the task ID from creation)
        print("\n[TEST 3] Getting task details...")
        print("-" * 40)
        result = await Runner.run(
            agent,
            input="Get details of the task you just created",
            run_config=run_config
        )
        print(f"Agent Response:\n{result.final_output}")

    print("\n" + "=" * 50)
    print("Agent + MCP integration test complete!")


if __name__ == "__main__":
    asyncio.run(main())
