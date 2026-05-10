# Tasks Manager Agent - Implementation Plan (v1)

## Document Info
- **Phase:** 3.1.2 - Plan
- **Date:** May 9, 2026
- **Status:** Ready for Review

---

## Implementation Order (Incremental)

```
Step 1: Project Setup
    ↓ verify: uv sync works
Step 2: Hello World Agent
    ↓ verify: agent responds
Step 3: Gemini Model + Tracing
    ↓ verify: Gemini LLM works, tracing enabled
Step 4: Streaming Output
    ↓ verify: events stream real-time
Step 5: MCP Connection Test
    ↓ verify: 5 tools discovered
Step 6: Agent + MCP Integration
    ↓ verify: agent uses MCP tools
Step 7: Full CLI
    ↓ verify: conversation flow works
Step 8: Error Handling & Polish
    ↓ verify: graceful errors
```

**Key Principle:** Each step is a checkpoint. Verify before moving on.

---

## Detailed Task Breakdown

### Step 1: Project Setup
**Goal:** Create project structure with uv

| # | Task | Output |
|---|------|--------|
| 1.1 | Create `services/tasks-agent/` folder | Directory |
| 1.2 | Initialize uv project (`uv init`) | pyproject.toml |
| 1.3 | Add dependencies | pyproject.toml updated |
| 1.4 | Create `src/tasks_agent/` package | __init__.py |
| 1.5 | Create `.env.example` | Template file |
| 1.6 | Create `.env` with API keys | Local config (gitignored) |

**pyproject.toml:**
```toml
[project]
name = "tasks-agent"
version = "1.0.0"
description = "Tasks Manager Agent using OpenAI Agents SDK"
requires-python = ">=3.12"

dependencies = [
    "openai-agents>=0.1.0",
    "litellm>=1.40.0",
    "python-dotenv>=1.0.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[project.scripts]
tasks-agent = "tasks_agent.cli:main"
```

**.env.example:**
```bash
OPENAI_API_KEY=sk-...      # Required for tracing
GEMINI_API_KEY=...         # Required for LLM
TASKS_MCP_URL=http://localhost:8000/mcp
AGENT_MODEL=gemini/gemini-3.1-flash-lite-preview
```

**Verify:** `uv sync` runs without errors

---

### Step 2: Hello World SandboxAgent
**Goal:** Verify OpenAI Agents SDK with SandboxAgent works

| # | Task | Output |
|---|------|--------|
| 2.1 | Create `src/tasks_agent/hello.py` | Test script |
| 2.2 | Create minimal SandboxAgent (no MCP) | Agent instance |
| 2.3 | Run with `Runner.run_sync()` | Response printed |

**File:** `src/tasks_agent/hello.py`
```python
"""Step 2: Hello World SandboxAgent - verify SDK works."""
from dotenv import load_dotenv
load_dotenv()

from agents import Runner
from agents.sandbox import SandboxAgent

agent = SandboxAgent(
    name="HelloAgent",
    instructions="You are a friendly assistant. Say hello and introduce yourself briefly."
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, input="Hi there!")
    print(result.final_output)
```

**Run:** `uv run python -m tasks_agent.hello`

**Verify:** SandboxAgent responds with greeting (uses OpenAI by default for this test)

---

### Step 3: Gemini Model + Tracing
**Goal:** Verify Gemini LLM works with SandboxAgent and OpenAI tracing

| # | Task | Output |
|---|------|--------|
| 3.1 | Create `src/tasks_agent/test_gemini.py` | Test script |
| 3.2 | Configure LitellmModel for Gemini | Model instance |
| 3.3 | Use SandboxAgent with Gemini | Agent runs |
| 3.4 | Verify tracing is enabled | Traces visible |

**File:** `src/tasks_agent/test_gemini.py`
```python
"""Step 3: Test SandboxAgent with Gemini model and OpenAI tracing."""
from dotenv import load_dotenv
load_dotenv()

from agents import Runner
from agents.sandbox import SandboxAgent
from agents.extensions.models.litellm_model import LitellmModel

# Gemini model via LiteLLM
gemini_model = LitellmModel(model="gemini/gemini-3.1-flash-lite-preview")

agent = SandboxAgent(
    name="GeminiTest",
    instructions="You are a helpful assistant. Keep responses brief.",
    model=gemini_model,
)

if __name__ == "__main__":
    print("Testing SandboxAgent with Gemini model...")
    result = Runner.run_sync(agent, input="What is 2+2? Just give the number.")
    print(f"Response: {result.final_output}")
    print("Success! SandboxAgent + Gemini working.")
```

**Run:** `uv run python -m tasks_agent.test_gemini`

**Verify:**
- SandboxAgent with Gemini responds correctly
- Check OpenAI dashboard for traces (if tracing enabled)

---

### Step 4: Streaming Output
**Goal:** Verify streaming events work with SandboxAgent

| # | Task | Output |
|---|------|--------|
| 4.1 | Create `src/tasks_agent/test_streaming.py` | Test script |
| 4.2 | Use `Runner.run_streamed()` with SandboxAgent | Streaming result |
| 4.3 | Print events as they arrive | Real-time output |

**File:** `src/tasks_agent/test_streaming.py`
```python
"""Step 4: Test streaming output with SandboxAgent."""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents import Runner
from agents.sandbox import SandboxAgent
from agents.extensions.models.litellm_model import LitellmModel

gemini_model = LitellmModel(model="gemini/gemini-3.1-flash-lite-preview")

agent = SandboxAgent(
    name="StreamTest",
    instructions="You are a helpful assistant.",
    model=gemini_model,
)

async def main():
    print("Testing streaming with SandboxAgent...")
    result = Runner.run_streamed(agent, input="Count from 1 to 5 slowly.")

    async for event in result.stream_events():
        # Print event type for debugging
        print(f"Event: {event.type}")

        # Stream text deltas
        if event.type == "raw_response_event":
            if hasattr(event.data, 'delta') and hasattr(event.data.delta, 'text'):
                print(event.data.delta.text, end='', flush=True)

    print("\n\nStreaming complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:** `uv run python -m tasks_agent.test_streaming`

**Verify:** Text appears incrementally (not all at once)

---

### Step 5: MCP Connection Test
**Goal:** Verify MCP server connection (without agent)

| # | Task | Output |
|---|------|--------|
| 5.1 | Ensure tasks-mcp server is running | Server at :8000 |
| 5.2 | Create `src/tasks_agent/test_mcp.py` | Test script |
| 5.3 | Connect and list tools | 5 tools discovered |

**Pre-requisite:** Start tasks-mcp server
```bash
cd services/tasks-mcp
uv run tasks-mcp
# Server running at http://localhost:8000
```

**File:** `src/tasks_agent/test_mcp.py`
```python
"""Step 5: Test MCP connection independently."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from agents.mcp import MCPServerStreamableHttp

async def main():
    mcp_url = os.getenv("TASKS_MCP_URL", "http://localhost:8000/mcp")
    print(f"Connecting to MCP server: {mcp_url}")

    async with MCPServerStreamableHttp(
        name="tasks-mcp",
        params={"url": mcp_url},
    ) as server:
        tools = await server.list_tools()
        print(f"\nDiscovered {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:50]}...")

    print("\nMCP connection test passed!")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:** `uv run python -m tasks_agent.test_mcp`

**Verify:** Output shows 5 tools:
- tasks_create
- tasks_list
- tasks_get
- tasks_update
- tasks_delete

---

### Step 6: Agent + MCP Integration
**Goal:** Connect agent to MCP server

| # | Task | Output |
|---|------|--------|
| 6.1 | Create `src/tasks_agent/agent.py` | Agent module |
| 6.2 | Create `src/tasks_agent/mcp.py` | MCP config |
| 6.3 | Create `src/tasks_agent/config.py` | Settings |
| 6.4 | Test agent with MCP tools | Tool calls work |

**File:** `src/tasks_agent/config.py`
```python
"""Configuration from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TASKS_MCP_URL = os.getenv("TASKS_MCP_URL", "http://localhost:8000/mcp")
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini/gemini-3.1-flash-lite-preview")
```

**File:** `src/tasks_agent/mcp.py`
```python
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
```

**File:** `src/tasks_agent/agent.py`
```python
"""Tasks Manager Agent configuration."""
from agents.sandbox import SandboxAgent
from agents.extensions.models.litellm_model import LitellmModel
from .config import AGENT_MODEL
from .mcp import create_mcp_server

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
    )
```

**Test file:** `src/tasks_agent/test_integration.py`
```python
"""Step 6: Test agent + MCP integration."""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents import Runner
from .agent import create_agent
from .mcp import create_mcp_server

async def main():
    print("Testing agent + MCP integration...")

    mcp_server = create_mcp_server()
    async with mcp_server:
        agent = create_agent(mcp_server)

        # Test: List tasks
        print("\n> Asking agent to list tasks...")
        result = Runner.run_sync(agent, input="List all tasks")
        print(f"Response:\n{result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:** `uv run python -m tasks_agent.test_integration`

**Verify:** Agent uses tasks_list tool and returns task list

---

### Step 7: Full CLI
**Goal:** Interactive CLI with Rich formatting

| # | Task | Output |
|---|------|--------|
| 7.1 | Create `src/tasks_agent/cli.py` | CLI module |
| 7.2 | Add Rich console formatting | Colored output |
| 7.3 | Implement main loop | Interactive chat |
| 7.4 | Add streaming event handler | Real-time display |

**File:** `src/tasks_agent/cli.py`
```python
"""Tasks Manager Agent CLI."""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.prompt import Prompt
from agents import Runner

from .agent import create_agent
from .mcp import create_mcp_server

console = Console()

def handle_event(event):
    """Handle streaming events."""
    if event.type == "raw_response_event":
        if hasattr(event.data, 'delta') and hasattr(event.data.delta, 'text'):
            console.print(event.data.delta.text, end='')
    elif event.type == "run_item_stream_event":
        if event.item.type == "tool_call_item":
            console.print(f"\n[dim][Tool: {event.item.tool_name}][/dim]", end='')

async def chat_loop(agent):
    """Main chat loop."""
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() in ['quit', 'exit', 'q']:
            break

        if not user_input.strip():
            continue

        console.print("[bold green]Agent[/bold green]: ", end='')

        result = Runner.run_streamed(agent, input=user_input)
        async for event in result.stream_events():
            handle_event(event)

        console.print()  # New line

async def main():
    """Main entry point."""
    console.print("[bold green]Tasks Manager Agent[/bold green]")
    console.print("[dim]Using Gemini LLM with OpenAI tracing[/dim]")
    console.print("[dim]Type 'quit' to exit[/dim]\n")

    mcp_server = create_mcp_server()

    try:
        async with mcp_server:
            agent = create_agent(mcp_server)
            await chat_loop(agent)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

    console.print("\n[dim]Goodbye![/dim]")

def run():
    """Entry point for script."""
    asyncio.run(main())

if __name__ == "__main__":
    run()
```

**Run:** `uv run tasks-agent` or `uv run python -m tasks_agent.cli`

**Verify:** Full conversation flow works:
```
You: Create a task to review PR #123
Agent: [Tool: tasks_create]
I've created the task...

You: List all tasks
Agent: [Tool: tasks_list]
Here are your tasks...

You: quit
Goodbye!
```

---

### Step 8: Error Handling & Polish
**Goal:** Handle errors gracefully

| # | Task | Output |
|---|------|--------|
| 8.1 | Add MCP connection error handling | Friendly message |
| 8.2 | Add model error handling | Retry/fallback info |
| 8.3 | Update `__init__.py` | Clean exports |
| 8.4 | Create README.md | Usage documentation |

**Error scenarios to handle:**
- MCP server not running
- Invalid API keys
- Network timeout

**Verify:**
- Start CLI without MCP server → friendly error
- Invalid API key → clear error message

---

## File Creation Order

```
1. pyproject.toml               # Project config
2. .env.example                 # Template
3. .env                         # Local secrets (gitignored)
4. src/tasks_agent/__init__.py  # Package init
5. src/tasks_agent/hello.py     # Step 2: Hello world
6. src/tasks_agent/test_gemini.py    # Step 3: Gemini test
7. src/tasks_agent/test_streaming.py # Step 4: Streaming test
8. src/tasks_agent/test_mcp.py       # Step 5: MCP test
9. src/tasks_agent/config.py    # Step 6: Config
10. src/tasks_agent/mcp.py      # Step 6: MCP module
11. src/tasks_agent/agent.py    # Step 6: Agent module
12. src/tasks_agent/test_integration.py # Step 6: Integration test
13. src/tasks_agent/cli.py      # Step 7: Full CLI
14. README.md                   # Step 8: Documentation
```

---

## Dependencies Between Steps

```
Step 1 (Setup) ─────────────────────────────────────┐
       │                                             │
       ▼                                             │
Step 2 (Hello World) ───────────────────────────────┤
       │                                             │
       ▼                                             │
Step 3 (Gemini + Tracing) ──────────────────────────┤
       │                                             │
       ▼                                             │
Step 4 (Streaming) ─────────────────────────────────┤
       │                                             │
       ▼                                             │
Step 5 (MCP Connection) ────────────────────────────┤
       │                                             │
       └──────────────► Step 6 (Agent + MCP) ◄──────┘
                              │
                              ▼
                        Step 7 (CLI)
                              │
                              ▼
                        Step 8 (Polish)
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| LiteLLM Gemini API changes | Check litellm docs for correct model ID |
| OpenAI Agents SDK version | Pin version in pyproject.toml |
| MCP connection issues | Test MCP independently (Step 5) before integration |
| Streaming event format | Log all events during development |
| Tracing requires OpenAI key | Verify OPENAI_API_KEY is set even for Gemini |

---

## Pre-Implementation Checklist

- [ ] tasks-mcp server is working (`uv run tasks-mcp`)
- [ ] OPENAI_API_KEY available (for tracing)
- [ ] GEMINI_API_KEY available (for LLM)
- [ ] Python 3.12+ installed
- [ ] uv installed

---

## Implementation Checklist

- [ ] Step 1: Project setup complete, `uv sync` works
- [ ] Step 2: Hello world agent responds
- [ ] Step 3: Gemini model works with tracing
- [ ] Step 4: Streaming output works
- [ ] Step 5: MCP connection discovers 5 tools
- [ ] Step 6: Agent uses MCP tools correctly
- [ ] Step 7: Full CLI conversation works
- [ ] Step 8: Error handling graceful

---

## Post-Implementation Verification

- [ ] `uv run tasks-agent` starts without errors
- [ ] Can create task through natural language
- [ ] Can list tasks with filters
- [ ] Can update and delete tasks
- [ ] MCP server down → friendly error message
- [ ] Streaming output displays in real-time

---

## Approval

**Plan Status:** Ready for Review

**Questions:**
1. Does the incremental approach make sense?
2. Is Step 3 (Gemini + Tracing) clear enough?
3. Ready to start implementation?

Once approved, we proceed to **Phase 3.1.3 - Implement**
