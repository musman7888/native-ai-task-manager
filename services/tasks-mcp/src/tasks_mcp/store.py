"""In-memory task store for Tasks MCP Server."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from .models import Task, TaskStatus, TaskPriority


class TaskStore:
    """In-memory storage for tasks.

    This is the v1 implementation using a simple dictionary.
    Will be replaced with SQLite (v2) and PostgreSQL (v3) later.
    """

    def __init__(self) -> None:
        """Initialize empty task store."""
        self._tasks: Dict[str, Task] = {}

    def create(
        self,
        title: str,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.PENDING,
        priority: TaskPriority = TaskPriority.MEDIUM,
        tags: Optional[List[str]] = None,
    ) -> Task:
        """Create a new task.

        Args:
            title: Task title (required)
            description: Task description (optional)
            status: Initial status (default: pending)
            priority: Priority level (default: medium)
            tags: List of tags (optional)

        Returns:
            Created Task object
        """
        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            tags=tags or [],
        )
        self._tasks[str(task.id)] = task
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: Task UUID as string

        Returns:
            Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def list(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        tag: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Task], int, bool, Optional[int]]:
        """List tasks with optional filtering and pagination.

        Args:
            status: Filter by status
            priority: Filter by priority
            tag: Filter by tag (single tag)
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            Tuple of (tasks, total_count, has_more, next_offset)
        """
        # Start with all tasks
        tasks = list(self._tasks.values())

        # Apply filters
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        if priority is not None:
            tasks = [t for t in tasks if t.priority == priority]
        if tag is not None:
            tasks = [t for t in tasks if tag in t.tags]

        # Sort by created_at (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Get total count before pagination
        total = len(tasks)

        # Apply pagination
        paginated = tasks[offset:offset + limit]

        # Calculate pagination metadata
        has_more = total > offset + len(paginated)
        next_offset = offset + len(paginated) if has_more else None

        return paginated, total, has_more, next_offset

    def update(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        tags: Optional[List[str]] = None,
    ) -> Tuple[Optional[Task], Dict[str, Dict[str, Any]]]:
        """Update an existing task.

        Args:
            task_id: Task UUID as string
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            priority: New priority (optional)
            tags: New tags (optional, replaces existing)

        Returns:
            Tuple of (updated_task, changes_dict) or (None, {}) if not found
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None, {}

        changes: Dict[str, Dict[str, Any]] = {}

        # Track and apply changes
        if title is not None and title != task.title:
            changes['title'] = {'old': task.title, 'new': title}
            task.title = title

        if description is not None and description != task.description:
            changes['description'] = {
                'old': task.description or '(empty)',
                'new': description or '(empty)'
            }
            task.description = description

        if status is not None and status != task.status:
            changes['status'] = {'old': task.status.value, 'new': status.value}
            task.status = status

        if priority is not None and priority != task.priority:
            changes['priority'] = {'old': task.priority.value, 'new': priority.value}
            task.priority = priority

        if tags is not None and tags != task.tags:
            changes['tags'] = {'old': task.tags, 'new': tags}
            task.tags = tags

        # Update timestamp if changes were made
        if changes:
            task.updated_at = datetime.now(timezone.utc)

        return task, changes

    def delete(self, task_id: str) -> Optional[Task]:
        """Delete a task by ID.

        Args:
            task_id: Task UUID as string

        Returns:
            Deleted Task if found, None otherwise
        """
        return self._tasks.pop(task_id, None)

    def count(self) -> int:
        """Get total number of tasks.

        Returns:
            Total task count
        """
        return len(self._tasks)

    def clear(self) -> None:
        """Clear all tasks (useful for testing)."""
        self._tasks.clear()


# Global store instance (singleton pattern for v1)
_store: Optional[TaskStore] = None


def get_store() -> TaskStore:
    """Get the global task store instance.

    Returns:
        TaskStore singleton instance
    """
    global _store
    if _store is None:
        _store = TaskStore()
    return _store
