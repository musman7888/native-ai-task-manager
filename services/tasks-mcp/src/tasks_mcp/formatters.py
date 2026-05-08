"""Response formatters for Tasks MCP Server."""

import json
from typing import List, Dict, Any, Optional

from .models import Task, ResponseFormat


def _format_datetime(dt) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def _task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert Task to dictionary for JSON serialization."""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value,
        "tags": task.tags,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


# =============================================================================
# Single Task Formatters
# =============================================================================

def format_task_json(task: Task) -> str:
    """Format a single task as JSON."""
    return json.dumps({"success": True, "task": _task_to_dict(task)}, indent=2)


def format_task_markdown(task: Task) -> str:
    """Format a single task as Markdown."""
    tags_str = ", ".join(task.tags) if task.tags else "(none)"
    desc_section = f"\n## Description\n{task.description}" if task.description else ""

    return f"""# Task: {task.title}

| Field | Value |
|-------|-------|
| **ID** | {task.id} |
| **Status** | {task.status.value} |
| **Priority** | {task.priority.value} |
| **Tags** | {tags_str} |
| **Created** | {_format_datetime(task.created_at)} |
| **Updated** | {_format_datetime(task.updated_at)} |
{desc_section}"""


# =============================================================================
# Task List Formatters
# =============================================================================

def format_task_list_json(
    tasks: List[Task],
    total: int,
    offset: int,
    has_more: bool,
    next_offset: Optional[int]
) -> str:
    """Format task list as JSON."""
    return json.dumps({
        "total": total,
        "count": len(tasks),
        "offset": offset,
        "has_more": has_more,
        "next_offset": next_offset,
        "tasks": [_task_to_dict(t) for t in tasks]
    }, indent=2)


def format_task_list_markdown(
    tasks: List[Task],
    total: int,
    offset: int,
    has_more: bool
) -> str:
    """Format task list as Markdown."""
    if not tasks:
        return "# Tasks\n\nNo tasks found. Use `tasks_create` to add a new task."

    lines = [f"# Tasks ({total} total, showing {len(tasks)})\n"]

    for i, task in enumerate(tasks, 1):
        tags_str = ", ".join(task.tags) if task.tags else "(no tags)"
        short_id = str(task.id)[:8] + "..."

        lines.append(f"## {i}. {task.title} ({short_id})")
        lines.append(f"- **Status:** {task.status.value} | **Priority:** {task.priority.value}")
        lines.append(f"- **Tags:** {tags_str}")
        lines.append(f"- **Created:** {_format_datetime(task.created_at)}")
        lines.append("")

    # Pagination info
    page_num = (offset // len(tasks)) + 1 if tasks else 1
    start_item = offset + 1
    end_item = offset + len(tasks)
    lines.append("---")
    lines.append(f"*Page {page_num} | Showing {start_item}-{end_item} of {total}*")

    if has_more:
        lines.append(f"\n*Use offset={offset + len(tasks)} to see more*")

    return "\n".join(lines)


# =============================================================================
# Operation Response Formatters
# =============================================================================

def format_created_response(task: Task, response_format: ResponseFormat) -> str:
    """Format task creation response."""
    if response_format == ResponseFormat.JSON:
        return format_task_json(task)

    tags_str = ", ".join(task.tags) if task.tags else "(none)"
    return f"""# Task Created Successfully

**ID:** {task.id}
**Title:** {task.title}
**Status:** {task.status.value}
**Priority:** {task.priority.value}
**Tags:** {tags_str}
**Created:** {_format_datetime(task.created_at)}"""


def format_updated_response(
    task: Task,
    changes: Dict[str, Dict[str, Any]],
    response_format: ResponseFormat
) -> str:
    """Format task update response."""
    if response_format == ResponseFormat.JSON:
        return json.dumps({
            "success": True,
            "task": _task_to_dict(task),
            "changes": changes
        }, indent=2)

    if not changes:
        return f"""# Task Unchanged

**ID:** {task.id}
**Title:** {task.title}

No changes were made (values already match)."""

    changes_lines = []
    for field, vals in changes.items():
        changes_lines.append(f"- **{field}:** {vals['old']} → {vals['new']}")

    return f"""# Task Updated Successfully

**ID:** {task.id}

## Changes Made:
{chr(10).join(changes_lines)}

**Updated:** {_format_datetime(task.updated_at)}"""


def format_deleted_response(task: Task, response_format: ResponseFormat) -> str:
    """Format task deletion response."""
    if response_format == ResponseFormat.JSON:
        return json.dumps({
            "success": True,
            "deleted": {
                "id": str(task.id),
                "title": task.title
            },
            "message": "Task permanently deleted"
        }, indent=2)

    return f"""# Task Deleted

**ID:** {task.id}
**Title:** {task.title}

Task has been permanently deleted."""


def format_list_response(
    tasks: List[Task],
    total: int,
    offset: int,
    has_more: bool,
    next_offset: Optional[int],
    response_format: ResponseFormat
) -> str:
    """Format task list response."""
    if response_format == ResponseFormat.JSON:
        return format_task_list_json(tasks, total, offset, has_more, next_offset)
    return format_task_list_markdown(tasks, total, offset, has_more)


def format_get_response(task: Task, response_format: ResponseFormat) -> str:
    """Format single task get response."""
    if response_format == ResponseFormat.JSON:
        return format_task_json(task)
    return format_task_markdown(task)


# =============================================================================
# Error Formatter
# =============================================================================

def format_error(message: str) -> str:
    """Format error message with helpful guidance.

    Args:
        message: Error description with suggestion

    Returns:
        Formatted error string starting with 'Error:'
    """
    return f"Error: {message}"
