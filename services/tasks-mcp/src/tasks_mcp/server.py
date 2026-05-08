"""FastMCP Server for Tasks MCP.

This server provides tools for AI agents to manage tasks through
the Model Context Protocol (MCP).
"""

from mcp.server.fastmcp import FastMCP

from .models import (
    TasksCreateInput,
    TasksListInput,
    TasksGetInput,
    TasksUpdateInput,
    TasksDeleteInput,
    ResponseFormat,
)
from .store import get_store
from .formatters import (
    format_created_response,
    format_list_response,
    format_get_response,
    format_updated_response,
    format_deleted_response,
    format_error,
)


# Initialize FastMCP server
mcp = FastMCP("tasks_mcp")


# =============================================================================
# Tool: tasks_create
# =============================================================================

@mcp.tool(
    name="tasks_create",
    annotations={
        "title": "Create Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
async def tasks_create(params: TasksCreateInput) -> str:
    """Create a new task in the task management system.

    Use this tool when the user wants to add a new task, todo item, or action item.
    The task will be assigned a unique ID and timestamps automatically.

    Args:
        params: TasksCreateInput containing:
            - title (str, required): Task title (1-200 chars)
            - description (str, optional): Detailed description
            - status (str, optional): pending, in_progress, completed, cancelled
            - priority (str, optional): low, medium, high
            - tags (list, optional): Tags for categorization
            - response_format (str): markdown or json

    Returns:
        str: Formatted response with created task details

    Examples:
        - "Create a task to review PR #123" -> title="Review PR #123"
        - "Add high priority task for security audit" -> title="Security audit", priority="high"
    """
    store = get_store()

    task = store.create(
        title=params.title,
        description=params.description,
        status=params.status,
        priority=params.priority,
        tags=params.tags or [],
    )

    return format_created_response(task, params.response_format)


# =============================================================================
# Tool: tasks_list
# =============================================================================

@mcp.tool(
    name="tasks_list",
    annotations={
        "title": "List Tasks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def tasks_list(params: TasksListInput) -> str:
    """List all tasks with optional filtering and pagination.

    Use this tool to see existing tasks, filter by status/priority/tag,
    or paginate through large task lists.

    Args:
        params: TasksListInput containing:
            - status (str, optional): Filter by status
            - priority (str, optional): Filter by priority
            - tag (str, optional): Filter by single tag
            - limit (int): Max results (1-100, default 20)
            - offset (int): Skip results for pagination
            - response_format (str): markdown or json

    Returns:
        str: Formatted list of tasks with pagination info

    Examples:
        - "Show all tasks" -> no filters
        - "Show pending high-priority tasks" -> status="pending", priority="high"
        - "Show tasks tagged 'security'" -> tag="security"
    """
    store = get_store()

    tasks, total, has_more, next_offset = store.list(
        status=params.status,
        priority=params.priority,
        tag=params.tag,
        limit=params.limit,
        offset=params.offset,
    )

    return format_list_response(
        tasks=tasks,
        total=total,
        offset=params.offset,
        has_more=has_more,
        next_offset=next_offset,
        response_format=params.response_format,
    )


# =============================================================================
# Tool: tasks_get
# =============================================================================

@mcp.tool(
    name="tasks_get",
    annotations={
        "title": "Get Task",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def tasks_get(params: TasksGetInput) -> str:
    """Get detailed information about a specific task by ID.

    Use this tool when you need full details of a single task,
    including its complete description.

    Args:
        params: TasksGetInput containing:
            - task_id (str, required): Task UUID
            - response_format (str): markdown or json

    Returns:
        str: Formatted task details or error if not found

    Examples:
        - "Show task 550e8400-e29b-41d4-a716-446655440000"
        - "Get details for task ID abc123..." (will validate UUID format)
    """
    store = get_store()

    task = store.get(params.task_id)

    if task is None:
        return format_error(
            f"Task not found with ID '{params.task_id}'. "
            "Use `tasks_list` to see available tasks."
        )

    return format_get_response(task, params.response_format)


# =============================================================================
# Tool: tasks_update
# =============================================================================

@mcp.tool(
    name="tasks_update",
    annotations={
        "title": "Update Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def tasks_update(params: TasksUpdateInput) -> str:
    """Update an existing task's fields.

    Use this tool to modify task properties like title, description,
    status, priority, or tags. Only specified fields will be updated.

    Args:
        params: TasksUpdateInput containing:
            - task_id (str, required): Task UUID to update
            - title (str, optional): New title
            - description (str, optional): New description
            - status (str, optional): New status
            - priority (str, optional): New priority
            - tags (list, optional): New tags (replaces existing)
            - response_format (str): markdown or json

    Returns:
        str: Formatted response showing changes made

    Examples:
        - "Mark task X as completed" -> task_id=X, status="completed"
        - "Change priority to high" -> task_id=X, priority="high"
        - "Update title to 'New Title'" -> task_id=X, title="New Title"
    """
    store = get_store()

    # Check if any update fields provided
    has_updates = any([
        params.title is not None,
        params.description is not None,
        params.status is not None,
        params.priority is not None,
        params.tags is not None,
    ])

    if not has_updates:
        return format_error(
            "No fields provided to update. "
            "Specify at least one of: title, description, status, priority, tags"
        )

    task, changes = store.update(
        task_id=params.task_id,
        title=params.title,
        description=params.description,
        status=params.status,
        priority=params.priority,
        tags=params.tags,
    )

    if task is None:
        return format_error(
            f"Task not found with ID '{params.task_id}'. "
            "Use `tasks_list` to see available tasks."
        )

    return format_updated_response(task, changes, params.response_format)


# =============================================================================
# Tool: tasks_delete
# =============================================================================

@mcp.tool(
    name="tasks_delete",
    annotations={
        "title": "Delete Task",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def tasks_delete(params: TasksDeleteInput) -> str:
    """Permanently delete a task.

    Use this tool to remove a task from the system. This action cannot
    be undone - the task will be permanently deleted.

    Args:
        params: TasksDeleteInput containing:
            - task_id (str, required): Task UUID to delete
            - response_format (str): markdown or json

    Returns:
        str: Confirmation of deletion or error if not found

    Examples:
        - "Delete task 550e8400-e29b-41d4-a716-446655440000"
        - "Remove the completed task" (after identifying the task ID)
    """
    store = get_store()

    task = store.delete(params.task_id)

    if task is None:
        return format_error(
            f"Task not found with ID '{params.task_id}'. "
            "It may have already been deleted."
        )

    return format_deleted_response(task, params.response_format)


# =============================================================================
# Entry Point
# =============================================================================

def main():
    """Run the MCP server with streamable HTTP transport."""
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
