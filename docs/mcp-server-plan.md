# Tasks MCP Server - Implementation Plan (v1)

## Document Info
- **Phase:** 2.1.2 - Plan
- **Date:** May 8, 2026
- **Status:** Ready for Review

---

## Implementation Order

```
Step 1: Project Setup
    ↓
Step 2: Models (Pydantic)
    ↓
Step 3: Store (In-Memory)
    ↓
Step 4: Formatters (JSON/Markdown)
    ↓
Step 5: Server + Tools
    ↓
Step 6: Test & Verify
```

---

## Detailed Task Breakdown

### Step 1: Project Setup
**Goal:** Create project structure with uv

| # | Task | Output |
|---|------|--------|
| 1.1 | Create `services/tasks-mcp/` folder | Directory |
| 1.2 | Initialize uv project (`uv init`) | pyproject.toml |
| 1.3 | Add dependencies (mcp, pydantic, httpx) | pyproject.toml updated |
| 1.4 | Create `src/tasks_mcp/` package | __init__.py |
| 1.5 | Create empty module files | models.py, store.py, formatters.py, server.py |
| 1.6 | Create `tests/` folder | test files |

**Dependencies:**
```toml
[project]
dependencies = [
    "mcp>=1.0.0",
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]
```

---

### Step 2: Models (Pydantic)
**Goal:** Define all data models with validation

| # | Task | Output |
|---|------|--------|
| 2.1 | Create `TaskStatus` enum | Enum class |
| 2.2 | Create `TaskPriority` enum | Enum class |
| 2.3 | Create `ResponseFormat` enum | Enum class |
| 2.4 | Create `Task` model | Pydantic BaseModel |
| 2.5 | Create `TasksCreateInput` model | Input validation |
| 2.6 | Create `TasksListInput` model | Input validation |
| 2.7 | Create `TasksGetInput` model | Input validation |
| 2.8 | Create `TasksUpdateInput` model | Input validation |
| 2.9 | Create `TasksDeleteInput` model | Input validation |

**File:** `src/tasks_mcp/models.py`

---

### Step 3: Store (In-Memory)
**Goal:** Create task storage with CRUD operations

| # | Task | Output |
|---|------|--------|
| 3.1 | Create `TaskStore` class | Class with dict storage |
| 3.2 | Implement `create(task_data)` | Returns Task |
| 3.3 | Implement `get(task_id)` | Returns Task or None |
| 3.4 | Implement `list(filters, limit, offset)` | Returns list + pagination |
| 3.5 | Implement `update(task_id, updates)` | Returns Task + changes |
| 3.6 | Implement `delete(task_id)` | Returns deleted Task |

**File:** `src/tasks_mcp/store.py`

---

### Step 4: Formatters (JSON/Markdown)
**Goal:** Create response formatters for both output formats

| # | Task | Output |
|---|------|--------|
| 4.1 | Create `format_task_json(task)` | JSON string |
| 4.2 | Create `format_task_markdown(task)` | Markdown string |
| 4.3 | Create `format_task_list_json(tasks, pagination)` | JSON string |
| 4.4 | Create `format_task_list_markdown(tasks, pagination)` | Markdown string |
| 4.5 | Create `format_created_response(task, format)` | Formatted response |
| 4.6 | Create `format_updated_response(task, changes, format)` | Formatted response |
| 4.7 | Create `format_deleted_response(task, format)` | Formatted response |
| 4.8 | Create `format_error(message)` | Error string |

**File:** `src/tasks_mcp/formatters.py`

---

### Step 5: Server + Tools
**Goal:** Create FastMCP server with all 5 tools

| # | Task | Output |
|---|------|--------|
| 5.1 | Initialize FastMCP server | Server instance |
| 5.2 | Implement `tasks_create` tool | Working tool |
| 5.3 | Implement `tasks_list` tool | Working tool |
| 5.4 | Implement `tasks_get` tool | Working tool |
| 5.5 | Implement `tasks_update` tool | Working tool |
| 5.6 | Implement `tasks_delete` tool | Working tool |
| 5.7 | Add `__main__` entry point | Runnable server |

**File:** `src/tasks_mcp/server.py`

---

### Step 6: Test & Verify
**Goal:** Ensure everything works

| # | Task | Output |
|---|------|--------|
| 6.1 | Write model validation tests | test_models.py |
| 6.2 | Write store operation tests | test_store.py |
| 6.3 | Run server manually | Server starts |
| 6.4 | Test with MCP Inspector | Tools work |
| 6.5 | Fix any issues found | Working server |

---

## File Creation Order

```
1. pyproject.toml           # Project config
2. src/tasks_mcp/__init__.py # Package init
3. src/tasks_mcp/models.py   # Data models (no deps)
4. src/tasks_mcp/store.py    # Storage (depends on models)
5. src/tasks_mcp/formatters.py # Formatting (depends on models)
6. src/tasks_mcp/server.py   # Server (depends on all above)
7. tests/test_models.py      # Model tests
8. tests/test_store.py       # Store tests
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| FastMCP API changes | Check latest SDK docs before coding |
| Pydantic v2 syntax | Use v2 patterns (model_config, field_validator) |
| HTTP transport config | Follow MCP best practices guide |
| UUID generation | Use Python's `uuid.uuid4()` |

---

## Dependencies Between Steps

```
Step 1 (Setup) ─────────────────────────────────────┐
                                                     │
Step 2 (Models) ────────────────────────────────────┤
        │                                            │
        ├──► Step 3 (Store) ────────────────────────┤
        │                                            │
        └──► Step 4 (Formatters) ───────────────────┤
                                                     │
                    Step 5 (Server) ◄────────────────┘
                           │
                           ▼
                    Step 6 (Test)
```

---

## Estimated Effort

| Step | Tasks | Complexity |
|------|-------|------------|
| 1. Setup | 6 | Low |
| 2. Models | 9 | Low |
| 3. Store | 6 | Medium |
| 4. Formatters | 8 | Medium |
| 5. Server | 7 | Medium |
| 6. Test | 5 | Low |
| **Total** | **41** | - |

---

## Implementation Checklist

### Pre-Implementation
- [ ] Review Python SDK README (WebFetch)
- [ ] Verify uv is installed
- [ ] Verify Python 3.12+ available

### Implementation
- [ ] Step 1: Project Setup complete
- [ ] Step 2: Models complete
- [ ] Step 3: Store complete
- [ ] Step 4: Formatters complete
- [ ] Step 5: Server complete
- [ ] Step 6: Tests passing

### Post-Implementation
- [ ] Server starts without errors
- [ ] All 5 tools respond correctly
- [ ] JSON format works
- [ ] Markdown format works
- [ ] Error messages are helpful

---

## Approval

**Plan Status:** Ready for Review

**Questions:**
1. Does the implementation order make sense?
2. Any steps missing?
3. Ready to start coding?

Once approved, we proceed to **Phase 2.1.3 - Implement**
