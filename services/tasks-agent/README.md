# Tasks Manager Agent

AI agent for task management using OpenAI Agents SDK with Gemini LLM and MCP integration.

## Features

- Natural language task management
- Gemini LLM via LiteLLM
- OpenAI tracing/observability
- MCP integration with Tasks MCP Server
- Streaming CLI output

## Quick Start

```bash
# Install dependencies
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the agent
uv run tasks-agent
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | For SDK tracing |
| `GEMINI_API_KEY` | Yes | For LLM inference |
| `TASKS_MCP_URL` | No | MCP server URL (default: http://localhost:8000/mcp) |

## Prerequisites

- Tasks MCP Server running at `http://localhost:8000`
- Python 3.12+
- uv package manager
