# AI Native Tasks Manager - Session History
<!-- NOTE: Keep this file compact. Only update status/progress. Do not add explanations here. -->

## Project Overview
Building an AI-native task management system with:
- **Tasks MCP Server** (Phase 2.1) - Backend API via MCP protocol
- **Tasks Agent** (Phase 3.1) - AI agent using OpenAI Agents SDK + Gemini LLM

## Environment
- **Platform:** Windows 11 + Docker Desktop
- **Python:** 3.12+
- **Package Manager:** uv
- **Sandbox:** DockerSandboxClient (Windows requires Docker)
- **LLM:** Gemini (`gemini-3.1-flash-lite-preview`) via LiteLLM

---

# Session 1: Tasks MCP Server (Phase 2.1) ✅ COMPLETE

**Date:** May 8-9, 2026

## What Was Built
MCP server exposing 5 task management tools via HTTP streamable transport.

## Files Created
```
services/tasks-mcp/
├── pyproject.toml
├── .env.example
└── src/tasks_mcp/
    ├── __init__.py
    ├── server.py       # MCP server with 5 tools
    ├── models.py       # Pydantic models (Task, CreateTask, etc.)
    ├── store.py        # In-memory task storage
    └── formatters.py   # Response formatting
```

## MCP Tools Implemented
| Tool | Description |
|------|-------------|
| `tasks_create` | Create a new task |
| `tasks_list` | List tasks with filters |
| `tasks_get` | Get task by ID |
| `tasks_update` | Update task fields |
| `tasks_delete` | Delete a task |

## Session 1 Progress
| # | Step | Status |
|---|------|--------|
| 1 | Project setup with uv | ✅ Done |
| 2 | Pydantic models | ✅ Done |
| 3 | In-memory store | ✅ Done |
| 4 | MCP server with tools | ✅ Done |
| 5 | HTTP streamable transport | ✅ Done |
| 6 | Test all 5 tools | ✅ Done |

## Quick Command
```bash
cd services/tasks-mcp && uv run tasks-mcp
# Server runs at http://localhost:8000/mcp
```

---

# Session 2: Tasks Agent (Phase 3.1) ✅ Steps 1-6 Complete

**Date:** May 9, 2026

## What Was Built
SandboxAgent using OpenAI Agents SDK with Gemini LLM, connected to Tasks MCP Server.

## Files Created
```
services/tasks-agent/
├── pyproject.toml           # openai-agents[docker]>=0.14.0
├── .env                     # API keys (gitignored)
├── .env.example
└── src/tasks_agent/
    ├── __init__.py
    ├── hello.py             # Step 2: Hello world test
    ├── test_gemini.py       # Step 3: Gemini model test
    ├── test_streaming.py    # Step 4: Streaming test
    ├── test_mcp.py          # Step 5: MCP connection test
    ├── config.py            # Step 6: Environment config
    ├── mcp.py               # Step 6: MCP server factory
    ├── agent.py             # Step 6: SandboxAgent with MCP
    ├── test_integration.py  # Step 6: Integration test
    └── final_test.py        # Final verification
```

## Key Discoveries
- **`capabilities=[]`**: Required to disable hosted tools for Gemini compatibility
- **DockerSandboxClient**: Windows requires Docker (macOS uses UnixLocalSandboxClient)
- **Async Context**: Use `await Runner.run()` inside async functions, not `run_sync()`
- **Streaming Events**: `ResponseTextDeltaEvent.delta` contains text directly

## Issues Resolved
| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: agents.sandbox` | Upgrade to `openai-agents>=0.14.0` |
| `UnixLocalSandboxClient` not on Windows | Use `DockerSandboxClient` |
| `Hosted tools not supported` | Add `capabilities=[]` |
| `run_sync() in async context` | Use `await Runner.run()` |

## Session 2 Progress
| # | Step | Status |
|---|------|--------|
| 1 | Project Setup | ✅ Done |
| 2 | Hello World SandboxAgent | ✅ Done |
| 3 | Gemini + Tracing Test | ✅ Done |
| 4 | Streaming Output | ✅ Done |
| 5 | MCP Connection Test | ✅ Done |
| 6 | Agent + MCP Integration | ✅ Done |
| 7 | Full CLI | ⏸️ Tomorrow |
| 8 | Error Handling | ⏸️ Tomorrow |

## Final Test Result
```
Task Created: "session 2 is completed"
ID: b37d18c7-1dba-4b85-882f-9bc6a741037f
Status: pending | Priority: medium
Created: 2026-05-09 17:09:36 UTC
```

## Comparison with Reference Repo (macOS)
| Feature | Reference | Ours |
|---------|-----------|------|
| Sandbox | UnixLocalSandboxClient | DockerSandboxClient ✓ |
| capabilities=[] | Yes | Yes ✓ |
| Streaming | No | Yes ✓ (bonus!) |
| Session History | SQLite | Not yet |
| FastAPI API | Yes | Not yet |

---

## Quick Commands
```bash
# Terminal 1: Start MCP server
cd services/tasks-mcp && uv run tasks-mcp

# Terminal 2: Run agent tests
cd services/tasks-agent
uv run python -m tasks_agent.test_integration
uv run python -m tasks_agent.final_test
```

---

## Next Session (Session 3)
- [ ] Step 7: Full CLI with Rich formatting
- [ ] Step 8: Error handling & polish
- [ ] Optional: Session history, provider switching, FastAPI API
- [ ] GitHub repo setup and push
