"""Step 2: Hello World SandboxAgent - verify SDK works with Gemini + Docker."""
from dotenv import load_dotenv
load_dotenv()

from docker import from_env as docker_from_env
from agents import Runner
from agents.run import RunConfig
from agents.sandbox import SandboxAgent, SandboxRunConfig, Manifest
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions
from agents.extensions.models.litellm_model import LitellmModel

# Use Gemini via LiteLLM
gemini_model = LitellmModel(model="gemini/gemini-3.1-flash-lite-preview")

# SandboxAgent with capabilities=[] allows Gemini (disables hosted tools)
agent = SandboxAgent(
    name="HelloAgent",
    instructions="You are a friendly assistant. Say hello and introduce yourself briefly.",
    model=gemini_model,
    capabilities=[],  # Key: disables grammar-based tools, enables Gemini compatibility
)

# RunConfig with Docker sandbox (required for Windows)
run_config = RunConfig(
    sandbox=SandboxRunConfig(
        client=DockerSandboxClient(docker_from_env()),
        options=DockerSandboxClientOptions(image="python:3.12-slim"),
        manifest=Manifest(root="/workspace", entries={}),
    )
)

if __name__ == "__main__":
    print("Testing SandboxAgent with Gemini + Docker...")
    print("-" * 40)
    result = Runner.run_sync(agent, input="Hi there!", run_config=run_config)
    print(result.final_output)
    print("-" * 40)
    print("Success! SandboxAgent with Gemini + Docker is working.")
