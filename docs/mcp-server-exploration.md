# Tasks MCP Server - Exploration Notes

## Date: May 8, 2026
## Phase: 2.1.0 - Explore

---

## What is MCP?

**Model Context Protocol (MCP)** is an open protocol that enables LLMs to interact with external services through well-designed tools. Think of it as "USB-C for AI" - a standardized way to connect AI systems with data sources and capabilities.

### Key Concepts
- **Host**: LLM application (Claude Desktop, Claude Code, etc.)
- **Client**: Connector within the host
- **Server**: Service providing tools/capabilities (what we're building)
- **Tools**: Functions the AI can execute
- **Resources**: Data the AI can access

---

## Decisions Made

### 1. Transport: Streamable HTTP
- **Chosen**: Streamable HTTP (not stdio)
- **Why**: More production-like, enables remote access, multi-client support
- **Trade-off**: Slightly more complex than stdio, but better learning

### 2. Deployment Strategy: Both
- **Start**: Local development with HTTP
- **Later**: Deploy to Kubernetes cluster
- **Benefit**: Learn both local dev and K8s deployment patterns

### 3. Language: Python 3.12+
- **Framework**: FastMCP (official Python SDK)
- **Validation**: Pydantic models
- **Package Manager**: uv (per AGENTS.md)

### 4. Server Naming
- **Name**: `tasks_mcp`
- **Convention**: `{service}_mcp` for Python

### 5. Tool Naming Convention
- **Pattern**: `tasks_{action}_{resource}`
- **Examples**: `tasks_create`, `tasks_list`, `tasks_get`

### 6. Response Formats
- **Support both**: JSON and Markdown
- **JSON**: For programmatic processing
- **Markdown**: For human readability

### 7. State Management (Iterative)
| Version | Storage | Purpose |
|---------|---------|---------|
| v1 | In-memory (dict) | Get it working |
| v2 | SQLite | Persistence, validation |
| v3 | PostgreSQL | Production-ready |

### 8. Input Validation
- **Approach**: Pydantic models with Field constraints
- **Benefits**: Auto-validation, schema generation, type hints

### 9. Pagination
- **Style**: Offset-based (`limit`, `offset`)
- **Default**: 20 items per page
- **Metadata**: `has_more`, `next_offset`, `total_count`

---

## Tools to Implement (v1)

| Tool | Action | Read/Write | Annotations |
|------|--------|------------|-------------|
| `tasks_create` | Create task | Write | destructiveHint: false |
| `tasks_list` | List all tasks | Read | readOnlyHint: true |
| `tasks_get` | Get by ID | Read | readOnlyHint: true |
| `tasks_update` | Update task | Write | idempotentHint: true |
| `tasks_delete` | Delete task | Write | destructiveHint: true |

---

## Tool Annotations Reference

| Annotation | Default | Description |
|------------|---------|-------------|
| `readOnlyHint` | false | Tool does NOT modify data |
| `destructiveHint` | true | Tool MAY delete/modify data |
| `idempotentHint` | false | Safe to retry (same result) |
| `openWorldHint` | true | Interacts with external systems |

---

## Project Structure (Planned)

```
services/
└── tasks-mcp/
    ├── pyproject.toml      # uv project config
    ├── src/
    │   └── tasks_mcp/
    │       ├── __init__.py
    │       ├── server.py      # FastMCP server
    │       ├── models.py      # Pydantic models
    │       ├── store.py       # Data storage (in-memory v1)
    │       └── formatters.py  # Response formatting
    ├── tests/
    │   └── test_server.py
    ├── Dockerfile          # (v3)
    └── README.md
```

---

## Key Resources

- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Best Practices](./reference/mcp_best_practices.md) (local skill)
- [Python MCP Guide](./reference/python_mcp_server.md) (local skill)

---

## Questions Resolved

| Question | Answer |
|----------|--------|
| stdio vs HTTP? | HTTP (production-like) |
| Local vs K8s? | Both (iterative) |
| TypeScript vs Python? | Python (per AGENTS.md) |
| In-memory vs DB? | In-memory first, then DB |

---

## Next Step

→ **Phase 2.1.1**: Write specification document defining:
- Task data model
- Tool signatures
- API contracts
- Error handling patterns
