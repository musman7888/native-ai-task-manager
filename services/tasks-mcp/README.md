# Tasks MCP Server

MCP Server for task management - enables AI agents to create, read, update, and delete tasks.

## Features

- **tasks_create** - Create new tasks with title, description, status, priority, and tags
- **tasks_list** - List tasks with filtering and pagination
- **tasks_get** - Get detailed info about a specific task
- **tasks_update** - Update task fields
- **tasks_delete** - Permanently delete a task

## Installation

```bash
uv sync
```

## Running

```bash
uv run tasks-mcp
```

## Development

Run tests:
```bash
uv run pytest
```
