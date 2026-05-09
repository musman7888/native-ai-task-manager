# Tasks MCP Server

MCP Server for task management - enables AI agents to create, read, update, and delete tasks through the Model Context Protocol.

## Features

| Tool | Description |
|------|-------------|
| `tasks_create` | Create new tasks with title, description, status, priority, and tags |
| `tasks_list` | List tasks with filtering by status, priority, tag + pagination |
| `tasks_get` | Get detailed info about a specific task |
| `tasks_update` | Update task fields (partial updates supported) |
| `tasks_delete` | Permanently delete a task |

## Quick Start

### Local Development

```bash
# Install dependencies
uv sync

# Run server
uv run tasks-mcp

# Run tests
uv run pytest
```

### Docker

```bash
# Build locally
docker build -t tasks-mcp:v1 .

# Run container
docker run -p 8000:8000 tasks-mcp:v1

# Or pull from GHCR
docker pull ghcr.io/musman7888/tasks-mcp:latest
docker run -p 8000:8000 ghcr.io/musman7888/tasks-mcp:latest
```

## Connect to Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "tasks-mcp": {
      "type": "url",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## API

### Task Model

```json
{
  "id": "uuid",
  "title": "string (1-200 chars)",
  "description": "string (optional)",
  "status": "pending | in_progress | completed",
  "priority": "low | medium | high",
  "tags": ["string"],
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

### Response Formats

All tools support `response_format` parameter:
- `markdown` (default) - Human-readable output
- `json` - Structured JSON output

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Server bind address |
| `MCP_PORT` | `8000` | Server port |

## CI/CD

This service uses GitHub Actions for CI/CD:
- **Triggers:** Changes to `services/tasks-mcp/**`
- **Pipeline:** Test → Build → Push to GHCR
- **Image:** `ghcr.io/musman7888/tasks-mcp:latest`

## Tech Stack

- Python 3.12+
- FastMCP (MCP SDK)
- Pydantic v2 (validation)
- UV (package manager)
- Docker (containerization)
