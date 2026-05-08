"""Pydantic models for Tasks MCP Server."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator


# =============================================================================
# Enums
# =============================================================================

class TaskStatus(str, Enum):
    """Task status options."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


# =============================================================================
# Task Model
# =============================================================================

class Task(BaseModel):
    """Task entity model."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    id: UUID = Field(default_factory=uuid4, description="Unique task identifier")
    title: str = Field(..., description="Task title", min_length=1, max_length=200)
    description: Optional[str] = Field(
        default=None,
        description="Detailed task description",
        max_length=2000
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current task status"
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority level"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization",
        max_length=10
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp"
    )

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate each tag length."""
        if v:
            for tag in v:
                if len(tag) > 50:
                    raise ValueError(f"Tag '{tag[:20]}...' exceeds 50 characters")
                if len(tag) < 1:
                    raise ValueError("Tags cannot be empty strings")
        return v


# =============================================================================
# Tool Input Models
# =============================================================================

class TasksCreateInput(BaseModel):
    """Input model for tasks_create tool."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    title: str = Field(
        ...,
        description="Task title (e.g., 'Review PR #123', 'Write documentation')",
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
        description="Tags for categorization (max 10 tags, each max 50 chars)",
        max_length=10
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable, 'json' for machine-readable"
    )


class TasksListInput(BaseModel):
    """Input model for tasks_list tool."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )

    status: Optional[TaskStatus] = Field(
        default=None,
        description="Filter by status: pending, in_progress, completed, cancelled"
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="Filter by priority: low, medium, high"
    )
    tag: Optional[str] = Field(
        default=None,
        description="Filter by tag (single tag match)",
        max_length=50
    )
    limit: int = Field(
        default=20,
        description="Maximum number of results to return",
        ge=1,
        le=100
    )
    offset: int = Field(
        default=0,
        description="Number of results to skip for pagination",
        ge=0
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class TasksGetInput(BaseModel):
    """Input model for tasks_get tool."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )

    task_id: str = Field(
        ...,
        description="Task ID (UUID format, e.g., '550e8400-e29b-41d4-a716-446655440000')"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

    @field_validator('task_id')
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Validate UUID format."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError(
                f"Invalid task ID format '{v}'. "
                "Expected UUID (e.g., '550e8400-e29b-41d4-a716-446655440000')"
            )
        return v


class TasksUpdateInput(BaseModel):
    """Input model for tasks_update tool."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )

    task_id: str = Field(
        ...,
        description="Task ID to update (UUID format)"
    )
    title: Optional[str] = Field(
        default=None,
        description="New task title",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="New task description",
        max_length=2000
    )
    status: Optional[TaskStatus] = Field(
        default=None,
        description="New status: pending, in_progress, completed, cancelled"
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="New priority: low, medium, high"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="New tags (replaces existing tags)",
        max_length=10
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

    @field_validator('task_id')
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Validate UUID format."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError(
                f"Invalid task ID format '{v}'. "
                "Expected UUID (e.g., '550e8400-e29b-41d4-a716-446655440000')"
            )
        return v


class TasksDeleteInput(BaseModel):
    """Input model for tasks_delete tool."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )

    task_id: str = Field(
        ...,
        description="Task ID to delete (UUID format)"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

    @field_validator('task_id')
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Validate UUID format."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError(
                f"Invalid task ID format '{v}'. "
                "Expected UUID (e.g., '550e8400-e29b-41d4-a716-446655440000')"
            )
        return v
