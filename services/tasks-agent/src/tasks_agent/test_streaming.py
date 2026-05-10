"""Step 4: Test streaming output with SandboxAgent."""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from docker import from_env as docker_from_env
from agents import Runner
from agents.run import RunConfig
from agents.sandbox import SandboxAgent, SandboxRunConfig, Manifest
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions
from agents.extensions.models.litellm_model import LitellmModel

# Gemini model via LiteLLM
gemini_model = LitellmModel(model="gemini/gemini-3.1-flash-lite-preview")

# SandboxAgent with capabilities=[] for Gemini compatibility
agent = SandboxAgent(
    name="StreamTest",
    instructions="You are a helpful assistant.",
    model=gemini_model,
    capabilities=[],
)

# Docker sandbox configuration (required for Windows)
run_config = RunConfig(
    sandbox=SandboxRunConfig(
        client=DockerSandboxClient(docker_from_env()),
        options=DockerSandboxClientOptions(image="python:3.12-slim"),
        manifest=Manifest(root="/workspace", entries={}),
    )
)


async def main():
    print("Testing streaming with SandboxAgent...")
    print("-" * 40)
    print("Response: ", end='', flush=True)

    result = Runner.run_streamed(agent, input="Count from 1 to 5 slowly.", run_config=run_config)

    async for event in result.stream_events():
        # Stream text deltas from raw_response_event
        if event.type == "raw_response_event":
            # ResponseTextDeltaEvent has delta as a string
            if type(event.data).__name__ == "ResponseTextDeltaEvent":
                if hasattr(event.data, 'delta') and event.data.delta:
                    print(event.data.delta, end='', flush=True)

    print("\n" + "-" * 40)
    print("Streaming complete!")


if __name__ == "__main__":
    asyncio.run(main())
