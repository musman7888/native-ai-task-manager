"""Final test: Create 'session 2 is completed' task and retrieve it."""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents import Runner
from .agent import create_agent, create_run_config
from .mcp import create_mcp_server


async def main():
    print("=" * 50)
    print("Final Test: Create and Get Task")
    print("=" * 50)

    mcp_server = create_mcp_server()
    run_config = create_run_config()

    async with mcp_server:
        agent = create_agent(mcp_server)

        # Create task
        print("\n[1] Creating task 'session 2 is completed'...")
        print("-" * 40)
        result = await Runner.run(
            agent,
            input="Create a task titled 'session 2 is completed'",
            run_config=run_config
        )
        print(f"{result.final_output}")

        # Get it back
        print("\n[2] Retrieving the task...")
        print("-" * 40)
        result = await Runner.run(
            agent,
            input="Get the task 'session 2 is completed'",
            run_config=run_config
        )
        print(f"{result.final_output}")

    print("\n" + "=" * 50)
    print("Test Complete!")


if __name__ == "__main__":
    asyncio.run(main())
