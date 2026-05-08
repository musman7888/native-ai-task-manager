# Tasks MCP Server - Specification (v1)

## Document Info
- **Version:** 1.0 (In-Memory)
- **Date:** May 8, 2026
- **Status:** Draft - Pending Review

---

## 1. Overview

### Purpose
The Tasks MCP Server provides AI agents with tools to manage tasks through the Model Context Protocol. It enables creating, reading, updating, and deleting tasks via well-defined tool interfaces.

### Scope (v1)
- In-memory task storage (no persistence)
- Basic CRUD operations
- Streamable HTTP transport
- JSON and Markdown response formats

### Out of Scope (v1)
- Database persistence (v2)
- User authentication (v2)
- Task assignments (v2)
- Notifications (Phase 5)
- Reminders/due dates with alerts (v2)

---

## 2. Data Models

### 2.1 Task Model

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task:
    id: str              # UUID, auto-generated
    title: str           # Required, 1-200 chars
    description: str     # Optional, max 2000 chars
    status: TaskStatus   # Default: pending
    priority: TaskPriority  # Default: medium
    tags: List[str]      # Optional, max 10 tags
    created_at: datetime # Auto-set on creation
    updated_at: datetime # Auto-updated on modification
```

### 2.2 Field Constraints

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `id` | string | Auto | UUID v4, immutable |
| `title` | string | Yes | 1-200 characters |
| `description` | string | No | 0-2000 characters |
| `status` | enum | No | pending, in_progress, completed, cancelled |
| `priority` | enum | No | low, medium, high |
| `tags` | array | No | Max 10 items, each 1-50 chars |
| `created_at` | datetime | Auto | ISO 8601 format |
| `updated_at` | datetime | Auto | ISO 8601 format |

### 2.3 Example Task Object

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Review pull request #123",
  "description": "Check the new authentication module for security issues",
  "status": "pending",
  "priority": "high",
  "tags": ["code-review", "security"],
  "created_at": "2026-05-08T14:30:00Z",
  "updated_at": "2026-05-08T14:30:00Z"
}
```

---

## 3. Tool Specifications

### 3.1 tasks_create

**Purpose:** Create a new task

**Annotations:**
```python
{
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False
}
```

**Input Schema:**
```python
class TasksCreateInput(BaseModel):
    title: str = Field(
        ...,
        description="Task title (e.g., 'Review PR #123')",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed task description",
        max_length=2000
    )
    status: Optional[TaskStatus] = Field(
        default=TaskStatus.PENDING,
        description="Initial status: pending, in_progress, completed, cancelled"
    )
    priority: Optional[TaskPriority] = Field(
        default=TaskPriority.MEDIUM,
        description="Priority level: low, medium, high"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Tags for categorization",
        max_length=10
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: markdown or json"
    )
```

**Output (Success - Markdown):**
```markdown
# Task Created Successfully

**ID:** 550e8400-e29b-41d4-a716-446655440000
**Title:** Review pull request #123
**Status:** pending
**Priority:** high
**Tags:** code-review, security
**Created:** 2026-05-08 14:30:00 UTC
```

**Output (Success - JSON):**
```json
{
  "success": true,
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Review pull request #123",
    "description": "Check the new authentication module",
    "status": "pending",
    "priority": "high",
    "tags": ["code-review", "security"],
    "created_at": "2026-05-08T14:30:00Z",
    "updated_at": "2026-05-08T14:30:00Z"
  }
}
```

**Errors:**
| Error | Message |
|-------|---------|
| Validation | "Error: Title is required and must be 1-200 characters" |
| Validation | "Error: Tags cannot exceed 10 items" |

---

### 3.2 tasks_list

**Purpose:** List all tasks with optional filtering

**Annotations:**
```python
{
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False
}
```

**Input Schema:**
```python
class TasksListInput(BaseModel):
    status: Optional[TaskStatus] = Field(
        default=None,
        description="Filter by status"
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="Filter by priority"
    )
    tag: Optional[str] = Field(
        default=None,
        description="Filter by tag (single tag)"
    )
    limit: Optional[int] = Field(
        default=20,
        description="Maximum results to return",
        ge=1,
        le=100
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of results to skip",
        ge=0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: markdown or json"
    )
```

**Output (Success - Markdown):**
```markdown
# Tasks (3 total, showing 3)

## 1. Review pull request #123 (550e8400...)
- **Status:** pending | **Priority:** high
- **Tags:** code-review, security
- **Created:** 2026-05-08 14:30:00 UTC

## 2. Write unit tests (661f9511...)
- **Status:** in_progress | **Priority:** medium
- **Tags:** testing
- **Created:** 2026-05-08 10:00:00 UTC

## 3. Update documentation (772a0622...)
- **Status:** completed | **Priority:** low
- **Tags:** docs
- **Created:** 2026-05-07 09:00:00 UTC

---
*Page 1 | Showing 1-3 of 3*
```

**Output (Success - JSON):**
```json
{
  "total": 3,
  "count": 3,
  "offset": 0,
  "has_more": false,
  "next_offset": null,
  "tasks": [
    { "id": "550e8400...", "title": "Review pull request #123", ... },
    { "id": "661f9511...", "title": "Write unit tests", ... },
    { "id": "772a0622...", "title": "Update documentation", ... }
  ]
}
```

**Output (Empty):**
```markdown
# Tasks

No tasks found. Use `tasks_create` to add a new task.
```

---

### 3.3 tasks_get

**Purpose:** Get a single task by ID

**Annotations:**
```python
{
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False
}
```

**Input Schema:**
```python
class TasksGetInput(BaseModel):
    task_id: str = Field(
        ...,
        description="Task ID (UUID format)",
        pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: markdown or json"
    )
```

**Output (Success - Markdown):**
```markdown
# Task: Review pull request #123

| Field | Value |
|-------|-------|
| **ID** | 550e8400-e29b-41d4-a716-446655440000 |
| **Status** | pending |
| **Priority** | high |
| **Tags** | code-review, security |
| **Created** | 2026-05-08 14:30:00 UTC |
| **Updated** | 2026-05-08 14:30:00 UTC |

## Description
Check the new authentication module for security issues
```

**Output (Success - JSON):**
```json
{
  "success": true,
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Review pull request #123",
    "description": "Check the new authentication module",
    "status": "pending",
    "priority": "high",
    "tags": ["code-review", "security"],
    "created_at": "2026-05-08T14:30:00Z",
    "updated_at": "2026-05-08T14:30:00Z"
  }
}
```

**Errors:**
| Error | Message |
|-------|---------|
| Not Found | "Error: Task not found with ID '550e8400...'. Use `tasks_list` to see available tasks." |
| Invalid ID | "Error: Invalid task ID format. Expected UUID (e.g., '550e8400-e29b-41d4-a716-446655440000')" |

---

### 3.4 tasks_update

**Purpose:** Update an existing task

**Annotations:**
```python
{
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False
}
```

**Input Schema:**
```python
class TasksUpdateInput(BaseModel):
    task_id: str = Field(
        ...,
        description="Task ID to update",
        pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    )
    title: Optional[str] = Field(
        default=None,
        description="New title",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="New description",
        max_length=2000
    )
    status: Optional[TaskStatus] = Field(
        default=None,
        description="New status"
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="New priority"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="New tags (replaces existing)",
        max_length=10
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: markdown or json"
    )
```

**Output (Success - Markdown):**
```markdown
# Task Updated Successfully

**ID:** 550e8400-e29b-41d4-a716-446655440000

## Changes Made:
- **status:** pending → completed
- **priority:** high → medium

**Updated:** 2026-05-08 15:00:00 UTC
```

**Output (Success - JSON):**
```json
{
  "success": true,
  "task": { ... },
  "changes": {
    "status": { "old": "pending", "new": "completed" },
    "priority": { "old": "high", "new": "medium" }
  }
}
```

**Errors:**
| Error | Message |
|-------|---------|
| Not Found | "Error: Task not found with ID '550e8400...'" |
| No Changes | "Error: No fields provided to update. Specify at least one of: title, description, status, priority, tags" |

---

### 3.5 tasks_delete

**Purpose:** Delete a task permanently

**Annotations:**
```python
{
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": True,
    "openWorldHint": False
}
```

**Input Schema:**
```python
class TasksDeleteInput(BaseModel):
    task_id: str = Field(
        ...,
        description="Task ID to delete",
        pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: markdown or json"
    )
```

**Output (Success - Markdown):**
```markdown
# Task Deleted

**ID:** 550e8400-e29b-41d4-a716-446655440000
**Title:** Review pull request #123

Task has been permanently deleted.
```

**Output (Success - JSON):**
```json
{
  "success": true,
  "deleted": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Review pull request #123"
  },
  "message": "Task permanently deleted"
}
```

**Errors:**
| Error | Message |
|-------|---------|
| Not Found | "Error: Task not found with ID '550e8400...'. It may have already been deleted." |

---

## 4. Error Handling

### 4.1 Error Response Format

All errors return a string starting with "Error:" followed by:
1. What went wrong
2. Suggestion for resolution

**Examples:**
```
Error: Task not found with ID '550e8400...'. Use `tasks_list` to see available tasks.

Error: Title is required and must be 1-200 characters. Example: 'Review PR #123'

Error: Invalid status 'done'. Valid options: pending, in_progress, completed, cancelled
```

### 4.2 Error Categories

| Category | HTTP-like Code | Description |
|----------|----------------|-------------|
| Validation | 400 | Invalid input data |
| Not Found | 404 | Resource doesn't exist |
| Server Error | 500 | Unexpected internal error |

---

## 5. Server Configuration

### 5.1 Server Details

```python
Server Name: tasks_mcp
Transport: Streamable HTTP
Default Port: 8000
Base URL: http://localhost:8000
```

### 5.2 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TASKS_MCP_PORT` | No | 8000 | Server port |
| `TASKS_MCP_HOST` | No | 127.0.0.1 | Server host |
| `TASKS_MCP_LOG_LEVEL` | No | INFO | Logging level |

---

## 6. Project Structure

```
services/tasks-mcp/
├── pyproject.toml          # uv project configuration
├── README.md               # Usage documentation
├── src/
│   └── tasks_mcp/
│       ├── __init__.py     # Package init, version
│       ├── server.py       # FastMCP server & tool definitions
│       ├── models.py       # Pydantic models (Task, inputs)
│       ├── store.py        # In-memory task store
│       └── formatters.py   # JSON/Markdown response formatting
└── tests/
    ├── __init__.py
    ├── test_models.py      # Model validation tests
    ├── test_store.py       # Store operation tests
    └── test_server.py      # Integration tests
```

---

## 7. Usage Examples

### Example 1: Create and Complete a Task
```
Agent: Create a task to review PR #123 with high priority
→ tools.tasks_create(title="Review PR #123", priority="high")

Agent: Mark the task as completed
→ tools.tasks_update(task_id="550e8400...", status="completed")
```

### Example 2: List and Filter Tasks
```
Agent: Show me all pending high-priority tasks
→ tools.tasks_list(status="pending", priority="high")

Agent: Show tasks tagged with 'security'
→ tools.tasks_list(tag="security")
```

### Example 3: Get Details and Delete
```
Agent: Show me details of task 550e8400...
→ tools.tasks_get(task_id="550e8400...")

Agent: Delete that task
→ tools.tasks_delete(task_id="550e8400...")
```

---

## 8. Acceptance Criteria

### Functional Requirements
- [ ] Can create a task with title (required) and optional fields
- [ ] Can list all tasks with pagination
- [ ] Can filter tasks by status, priority, and tag
- [ ] Can get a single task by ID
- [ ] Can update any field of an existing task
- [ ] Can delete a task by ID
- [ ] Returns both JSON and Markdown formats

### Non-Functional Requirements
- [ ] All inputs validated via Pydantic
- [ ] Actionable error messages
- [ ] Tool annotations correctly set
- [ ] Response time < 100ms for all operations
- [ ] Server starts without errors

---

## 9. Review Checklist

Before implementation, verify:

- [ ] Data model covers all required fields
- [ ] All tools have clear input/output schemas
- [ ] Error messages are actionable
- [ ] Pagination is properly defined
- [ ] Response formats (JSON/Markdown) are consistent
- [ ] Tool annotations match behavior
- [ ] Project structure is clear

---

## Approval

**Spec Status:** Draft - Ready for Review

Please review and confirm before proceeding to implementation.
