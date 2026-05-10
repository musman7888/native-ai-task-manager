# Tasks Manager Agent - Specification (v1)

## Document Info
- **Version:** 1.0 (Simple Agent + MCP)
- **Date:** May 9, 2026
- **Status:** Draft - Pending Review

---

## 1. Overview

### Purpose
The Tasks Manager Agent is the primary user-facing orchestrator for task management. It interprets natural language requests, manages tasks through the Tasks MCP Server, and provides conversational responses via CLI.

### Scope (v1)
- OpenAI Agents SDK (simple Agent, no sandbox)
- **Multi-model support**: OpenAI + Gemini
- MCP integration via `MCPServerStreamableHttp`
- CLI interface with streaming output
- Natural language task management
- Task CRUD operations through MCP tools
- No approval policies (simple flow)

### Out of Scope (v1)
- Sandbox capabilities (v2)
- Web UI (Phase 6)
- Appointment booking handoff (v2)
- Multi-user authentication (v2)
- Persistent conversation history (v2)
- Voice interface (future)

### Design Principles (v1)
- **SandboxAgent**: Use `SandboxAgent` class for future extensibility
- **Incremental**: Build step-by-step, verify each step
- **Gemini LLM**: Use Gemini via LiteLLM for inference
- **OpenAI Tracing**: Use OpenAI API key for observability
- **No approval**: Tools execute immediately (no confirmation workflow)

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User (CLI)                           │
└─────────────────────────┬───────────────────────────────────┘
                          │ Natural Language
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Tasks Manager Agent                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            OpenAI Agents SDK (SandboxAgent)          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ Instructions│  │ Capabilities│  │   Manifest  │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MCP Integration Layer                   │   │
│  │            (MCPServerStreamableHttp)                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ MCP Tools (HTTP)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Tasks MCP Server                         │
│           (http://localhost:8000/mcp)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  tasks_create | tasks_list | tasks_get |            │   │
│  │  tasks_update | tasks_delete                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent SDK** | `openai-agents` | Agent orchestration |
| **LLM (Primary)** | OpenAI GPT-4o | High-quality responses |
| **LLM (Alt)** | Gemini 3.1 Flash Lite | Fast, cost-effective alternative |
| **MCP Client** | `MCPServerStreamableHttp` | Connect to Tasks MCP Server |
| **CLI** | Python `asyncio` + Rich | User interaction |
| **Package Manager** | `uv` | Dependencies and runtime |
| **Config** | `python-dotenv` | Environment variables |

### 2.3 Key SDK Components

| Component | Class | Purpose |
|-----------|-------|---------|
| **Agent** | `SandboxAgent` | Sandbox-enabled agent with capabilities |
| **MCP Server** | `MCPServerStreamableHttp` | HTTP-based MCP connection |
| **Runner** | `Runner.run_streamed()` | Async execution with streaming |
| **Sandbox Config** | `SandboxRunConfig` | Runtime sandbox configuration |
| **Model Provider** | `LitellmModel` | Gemini via LiteLLM |

---

## 3. Agent Configuration

### 3.1 SandboxAgent Definition

```python
from agents.sandbox import SandboxAgent
from agents.mcp import MCPServerStreamableHttp
from agents.extensions.models.litellm_model import LitellmModel
import os

# MCP Server Connection
tasks_mcp_server = MCPServerStreamableHttp(
    name="tasks-mcp",
    params={"url": os.getenv("TASKS_MCP_URL", "http://localhost:8000/mcp")},
    cache_tools_list=True,
)

# Agent Definition (SandboxAgent with Gemini LLM)
tasks_agent = SandboxAgent(
    name="TasksManager",
    instructions=AGENT_INSTRUCTIONS,
    mcp_servers=[tasks_mcp_server],
    model=LitellmModel(model="gemini/gemini-3.1-flash-lite-preview"),
)
```

### 3.2 LLM Configuration

```python
from agents.extensions.models.litellm_model import LitellmModel

# Gemini via LiteLLM (uses GEMINI_API_KEY)
gemini_model = LitellmModel(model="gemini/gemini-3.1-flash-lite-preview")

# SandboxAgent with Gemini
agent = SandboxAgent(
    name="TasksManager",
    model=gemini_model,
    ...
)
```

**Environment Setup:**
```bash
# .env file
OPENAI_API_KEY=sk-...                           # Required for tracing
GEMINI_API_KEY=...                              # Required for LLM inference
AGENT_MODEL=gemini/gemini-3.1-flash-lite-preview
```

### 3.3 Agent Instructions

```python
AGENT_INSTRUCTIONS = """
You are the Tasks Manager Agent - a helpful assistant for managing tasks.

## Your Capabilities
You can help users with:
- Creating new tasks with titles, descriptions, priorities, and tags
- Listing tasks with filtering by status, priority, or tag
- Viewing detailed information about specific tasks
- Updating task fields (status, priority, title, description, tags)
- Deleting tasks when requested

## Available MCP Tools
- `tasks_create`: Create a new task
- `tasks_list`: List tasks with optional filters
- `tasks_get`: Get details of a specific task
- `tasks_update`: Update an existing task
- `tasks_delete`: Delete a task

## Guidelines
1. When listing tasks, summarize the results clearly
2. If a user's request is ambiguous, ask for clarification
3. Use markdown formatting for clear, readable responses
4. When creating tasks, suggest appropriate priorities if not specified
5. Show task IDs in responses so users can reference them

## Response Style
- Be concise but helpful
- Use bullet points for lists
- Highlight important information (IDs, status changes)
"""
```

### 3.4 Model Configuration

| Model | ID | Use Case |
|-------|-----|----------|
| **OpenAI GPT-4o** | `gpt-4o` | Primary - high quality |
| **Gemini Flash Lite** | `gemini/gemini-3.1-flash-lite-preview` | Alternative - fast & cheap |

**Note:** No `temperature` override - use SDK defaults for simplicity.

---

## 4. MCP Integration

### 4.1 Server Connection

```python
from agents.mcp import MCPServerStreamableHttp
import os

def create_mcp_server():
    """Create MCP server connection."""
    return MCPServerStreamableHttp(
        name="tasks-mcp",
        params={
            "url": os.getenv("TASKS_MCP_URL", "http://localhost:8000/mcp")
        },
        cache_tools_list=True,  # Cache tool definitions for performance
    )
```

### 4.2 Tool Discovery

The agent automatically discovers these MCP tools:

| MCP Tool | Agent Use Case |
|----------|----------------|
| `tasks_create` | "Create a task to review PR" |
| `tasks_list` | "Show me all pending tasks" |
| `tasks_get` | "What's the status of task X?" |
| `tasks_update` | "Mark task X as completed" |
| `tasks_delete` | "Delete task X" |

### 4.3 No Approval Policy

For v1 simplicity, tools execute immediately without approval workflow:

```python
# Simple MCP config - no approval required
tasks_mcp_server = MCPServerStreamableHttp(
    name="tasks-mcp",
    params={"url": mcp_url},
    # No require_approval parameter = tools run immediately
)
```

---

## 5. Runner Configuration

### 5.1 Execution Flow

```python
from agents import Agent, Runner

async def run_agent(agent: Agent, user_input: str):
    """Execute agent with streaming output."""

    result = Runner.run_streamed(agent, input=user_input)
    # Note: Using SDK default max_turns

    async for event in result.stream_events():
        handle_event(event)

    return result.final_output
```

### 5.2 Event Handling

```python
def handle_event(event):
    """Process streaming events for CLI output."""

    if event.type == "raw_response_event":
        # Stream text as it arrives
        if hasattr(event, 'delta'):
            print(event.delta, end='', flush=True)

    elif event.type == "run_item_stream_event":
        if event.item.type == "tool_call_item":
            print(f"\n[Tool: {event.item.tool_name}]")
        elif event.item.type == "tool_call_output_item":
            print(f"[Done]")
```

### 5.3 RunConfig

| Option | Value | Notes |
|--------|-------|-------|
| `max_turns` | SDK default | Don't override |
| `tracing_disabled` | `False` | Enable for debugging |

---

## 6. CLI Interface

### 6.1 Main Entry Point

```python
import asyncio
from rich.console import Console
from rich.prompt import Prompt

console = Console()

async def main():
    """Main CLI loop."""
    console.print("[bold green]Tasks Manager Agent[/bold green]")
    console.print("Type 'quit' to exit\n")

    async with tasks_mcp_server:
        while True:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")

            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            console.print("[bold green]Agent[/bold green]: ", end='')
            await run_agent(tasks_agent, user_input)
            console.print()

if __name__ == "__main__":
    asyncio.run(main())
```

### 6.2 CLI Features

| Feature | Implementation |
|---------|----------------|
| **Streaming output** | Real-time token display |
| **Rich formatting** | Colors, bold text |
| **Tool indicators** | Show when tools are called |
| **Graceful exit** | Handle quit/exit commands |

---

## 7. Incremental Implementation Steps

**Key Principle:** Build step-by-step, verify each step works before moving on.

### Step 1: Project Setup
```bash
# Create project structure
mkdir -p services/tasks-agent/src/tasks_agent
cd services/tasks-agent
uv init
```
**Verify:** `uv sync` runs without errors

### Step 2: Hello World Agent
```python
# Simple agent without MCP - just test SDK works
from agents import Agent, Runner

agent = Agent(name="HelloAgent", instructions="Say hello")
result = Runner.run_sync(agent, input="Hi")
print(result.final_output)
```
**Verify:** Agent responds with greeting

### Step 3: Multi-Model Test
```python
# Test both OpenAI and Gemini models work
from agents.extensions.models.litellm_model import LitellmModel

# Test OpenAI
agent_openai = Agent(name="Test", model="gpt-4o", ...)
# Test Gemini
agent_gemini = Agent(name="Test", model=LitellmModel(model="gemini/gemini-3.1-flash-lite-preview"), ...)
```
**Verify:** Both models respond correctly

### Step 4: Streaming Output
```python
# Test streaming works
result = Runner.run_streamed(agent, input="Tell me a joke")
async for event in result.stream_events():
    print(event)
```
**Verify:** Events stream in real-time

### Step 5: MCP Connection (No Agent)
```python
# Test MCP server connection independently
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(
    name="tasks-mcp",
    params={"url": "http://localhost:8000/mcp"}
) as server:
    tools = await server.list_tools()
    print(tools)
```
**Verify:** 5 tools discovered (tasks_create, tasks_list, etc.)

### Step 6: Agent + MCP Integration
```python
# Connect agent to MCP
agent = Agent(
    name="TasksManager",
    mcp_servers=[tasks_mcp_server],
    ...
)
result = Runner.run_sync(agent, input="List all tasks")
```
**Verify:** Agent uses MCP tools correctly

### Step 7: Full CLI
```python
# Interactive CLI loop with Rich formatting
```
**Verify:** Full conversation flow works

### Step 8: Error Handling
```python
# Test error scenarios
# - MCP server down
# - Invalid model
```
**Verify:** Graceful error messages

---

## 8. Conversation Examples

### Example 1: Create Task
```
You: Create a task to review PR #456 with high priority

Agent: [Calling: tasks_create]
[Tool completed]

I've created a new task for you:

**Task Created**
- **ID:** 7a8b9c0d-...
- **Title:** Review PR #456
- **Priority:** High
- **Status:** Pending

Would you like to add any tags or description to this task?
```

### Example 2: List and Filter
```
You: Show me all pending high-priority tasks

Agent: [Calling: tasks_list]
[Tool completed]

Here are your pending high-priority tasks:

1. **Review PR #456** (7a8b9c0d-...)
   - Created: Today at 2:30 PM
   - Tags: none

2. **Fix security vulnerability** (1e2f3g4h-...)
   - Created: Yesterday
   - Tags: security, urgent

You have 2 high-priority pending tasks.
```

### Example 3: Update with Confirmation
```
You: Mark the PR review task as completed

Agent: [Calling: tasks_update]
[Tool completed]

Done! Task "Review PR #456" has been marked as completed.

Summary:
- Status: pending → completed
- Updated: Just now
```

### Example 4: Delete Task
```
You: Delete the security task

Agent: [Tool: tasks_delete]
[Done]

Task "Fix security vulnerability" has been permanently deleted.
```

**Note:** No confirmation prompt in v1 (simple flow, no approval policy).

---

## 9. Error Handling

### 9.1 MCP Connection Errors

```python
class MCPConnectionError(Exception):
    """Raised when MCP server is unreachable."""
    pass

async def check_mcp_health():
    """Verify MCP server is available."""
    try:
        await tasks_mcp_server.connect()
    except Exception as e:
        raise MCPConnectionError(
            f"Cannot connect to Tasks MCP Server. "
            f"Is it running at http://localhost:8000? Error: {e}"
        )
```

### 9.2 Error Categories

| Error Type | User Message | Recovery |
|------------|--------------|----------|
| MCP unreachable | "Task service unavailable. Please ensure the server is running." | Retry connection |
| Tool error | "Failed to complete action: {error}" | Show specific error |
| Invalid input | "I need more information: {details}" | Ask for clarification |
| Max turns | "This request is taking too long. Please try a simpler query." | Reset conversation |

---

## 10. Project Structure

```
services/tasks-agent/
├── pyproject.toml              # uv project configuration
├── README.md                   # Usage documentation
├── .env.example                # Environment template
├── src/
│   └── tasks_agent/
│       ├── __init__.py         # Package init, version
│       ├── agent.py            # Agent configuration
│       ├── models.py           # Multi-model support (OpenAI/Gemini)
│       ├── mcp.py              # MCP server connection
│       ├── cli.py              # CLI interface (main entry)
│       └── config.py           # Settings from .env
└── tests/
    ├── __init__.py
    ├── test_agent.py           # Agent behavior tests
    └── test_mcp.py             # MCP integration tests
```

---

## 11. Dependencies

### 11.1 pyproject.toml

```toml
[project]
name = "tasks-agent"
version = "1.0.0"
description = "Tasks Manager Agent using OpenAI Agents SDK"
requires-python = ">=3.12"

dependencies = [
    "openai-agents>=0.1.0",   # Agent SDK
    "litellm>=1.40.0",        # Multi-model support (Gemini)
    "python-dotenv>=1.0.0",   # .env file loading
    "rich>=13.0.0",           # CLI formatting
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[project.scripts]
tasks-agent = "tasks_agent.cli:main"
```

---

## 12. Environment Variables

### 12.1 .env File (Development)

```bash
# .env
OPENAI_API_KEY=sk-...                           # Required for tracing
GEMINI_API_KEY=...                              # Required for LLM inference
TASKS_MCP_URL=http://localhost:8000/mcp
AGENT_MODEL=gemini/gemini-3.1-flash-lite-preview
LOG_LEVEL=INFO
```

### 12.2 Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | **Yes** | - | OpenAI API key (for SDK tracing) |
| `GEMINI_API_KEY` | **Yes** | - | Google Gemini API key (for LLM) |
| `TASKS_MCP_URL` | No | `http://localhost:8000/mcp` | MCP server URL |
| `AGENT_MODEL` | No | `gemini/gemini-3.1-flash-lite-preview` | LLM model ID |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### 12.3 Dual API Key Architecture

```
┌─────────────────────────────────────────────────────┐
│            OpenAI Agents SDK                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│   ┌─────────────────┐    ┌─────────────────────┐   │
│   │    Tracing      │    │   LLM Inference     │   │
│   │                 │    │                     │   │
│   │  OPENAI_API_KEY │    │  GEMINI_API_KEY     │   │
│   │  (observability)│    │  (via LiteLLM)      │   │
│   └────────┬────────┘    └──────────┬──────────┘   │
│            │                        │              │
└────────────┼────────────────────────┼──────────────┘
             ▼                        ▼
      OpenAI Tracing           Google Gemini API
```

### 12.4 Kubernetes (Future)
For K8s deployment, secrets will be mounted as environment variables via:
- `Secret` objects for API keys (both OpenAI and Gemini)
- `ConfigMap` for non-sensitive config

---

## 13. Acceptance Criteria

### Functional Requirements
- [ ] Agent connects to Tasks MCP Server via HTTP
- [ ] User can create tasks through natural language
- [ ] User can list tasks with filters (status, priority, tag)
- [ ] User can view task details by ID or description
- [ ] User can update task fields
- [ ] User can delete tasks
- [ ] Streaming responses display in real-time
- [ ] Both OpenAI and Gemini models work
- [ ] Graceful handling of MCP server unavailability

### Non-Functional Requirements
- [ ] Response streaming begins within 500ms
- [ ] MCP tool calls complete within 2 seconds
- [ ] Configuration via .env file works
- [ ] Clear error messages for all failure modes
- [ ] Works on Python 3.12+

---

## 14. Testing Strategy

### 14.1 Unit Tests
- Agent instructions produce expected tool calls
- Event handlers format output correctly
- Error handling covers all failure modes

### 14.2 Integration Tests
- End-to-end: user input → agent → MCP → response
- MCP connection retry behavior
- Streaming output completeness

### 14.3 Manual Tests
- Interactive CLI session
- All conversation examples work as documented
- Delete confirmation flow

---

## 15. Review Checklist

Before implementation, verify:

- [ ] Simple Agent (not SandboxAgent) is appropriate for v1
- [ ] Multi-model support (OpenAI + Gemini) is configured
- [ ] No approval policy matches requirements
- [ ] Incremental implementation steps are clear
- [ ] MCP tools properly configured
- [ ] .env file approach for secrets is acceptable
- [ ] Dependencies minimal and justified

---

## 16. References

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Tasks MCP Server Spec](./mcp-server-spec.md)
- [Project Constitution](../AGENTS.md)

---

## Approval

**Spec Status:** Draft - Ready for Review

Please review and confirm before proceeding to implementation.
