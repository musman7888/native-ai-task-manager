"""Step 3: Test SandboxAgent with Gemini model and OpenAI tracing."""
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
    name="GeminiTest",
    instructions="You are a helpful assistant. Keep responses brief.",
    model=gemini_model,
    capabilities=[],  # Required for non-OpenAI models
)

# Docker sandbox configuration (required for Windows)
run_config = RunConfig(
    sandbox=SandboxRunConfig(
        client=DockerSandboxClient(docker_from_env()),
        options=DockerSandboxClientOptions(image="python:3.12-slim"),
        manifest=Manifest(root="/workspace", entries={}),
    )
)

if __name__ == "__main__":
    print("Testing SandboxAgent with Gemini model...")
    print("-" * 40)

    result = Runner.run_sync(agent, input="What is 2+2? Just give the number.", run_config=run_config)
    print(f"Response: {result.final_output}")

    print("-" * 40)
    print("Success! SandboxAgent + Gemini working.")
    print("\nNote: OpenAI tracing is non-fatal if it fails (quota/network issues).")
