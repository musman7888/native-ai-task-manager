"""Tasks Manager Agent configuration."""
from docker import from_env as docker_from_env
from agents.run import RunConfig
from agents.sandbox import SandboxAgent, SandboxRunConfig, Manifest
from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions
from agents.extensions.models.litellm_model import LitellmModel
from .config import AGENT_MODEL

INSTRUCTIONS = """
You are the Tasks Manager Agent - a helpful assistant for managing tasks.

Available tools:
- tasks_create: Create a new task
- tasks_list: List tasks with optional filters
- tasks_get: Get details of a specific task
- tasks_update: Update an existing task
- tasks_delete: Delete a task

Be concise and helpful. Show task IDs in responses.
"""


def create_agent(mcp_server):
    """Create the tasks manager SandboxAgent."""
    return SandboxAgent(
        name="TasksManager",
        instructions=INSTRUCTIONS,
        model=LitellmModel(model=AGENT_MODEL),
        mcp_servers=[mcp_server],
        capabilities=[],  # Required for non-OpenAI models (Gemini)
    )


def create_run_config():
    """Create RunConfig with Docker sandbox (required for Windows)."""
    return RunConfig(
        sandbox=SandboxRunConfig(
            client=DockerSandboxClient(docker_from_env()),
            options=DockerSandboxClientOptions(image="python:3.12-slim"),
            manifest=Manifest(root="/workspace", entries={}),
        )
    )
