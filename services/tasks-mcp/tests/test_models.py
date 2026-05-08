"""Tests for Pydantic models."""

import pytest
from uuid import UUID
from pydantic import ValidationError

from tasks_mcp.models import (
    Task,
    TaskStatus,
    TaskPriority,
    ResponseFormat,
    TasksCreateInput,
    TasksListInput,
    TasksGetInput,
    TasksUpdateInput,
    TasksDeleteInput,
)


# =============================================================================
# Task Model Tests
# =============================================================================

class TestTaskModel:
    """Tests for the Task entity model."""

    def test_create_minimal_task(self):
        """Task with only required fields."""
        task = Task(title="Test task")

        assert task.title == "Test task"
        assert task.description is None
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert task.tags == []
        assert isinstance(task.id, UUID)

    def test_create_full_task(self):
        """Task with all fields specified."""
        task = Task(
            title="Full task",
            description="A detailed description",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            tags=["urgent", "backend"],
        )

        assert task.title == "Full task"
        assert task.description == "A detailed description"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.tags == ["urgent", "backend"]

    def test_title_whitespace_stripped(self):
        """Title should have whitespace stripped."""
        task = Task(title="  spaced title  ")
        assert task.title == "spaced title"

    def test_title_too_short(self):
        """Empty title should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            Task(title="")
        assert "string_too_short" in str(exc_info.value).lower()

    def test_title_too_long(self):
        """Title over 200 chars should fail."""
        with pytest.raises(ValidationError) as exc_info:
            Task(title="x" * 201)
        assert "string_too_long" in str(exc_info.value).lower()

    def test_tags_validation_too_long(self):
        """Tag over 50 chars should fail."""
        with pytest.raises(ValidationError) as exc_info:
            Task(title="Test", tags=["x" * 51])
        assert "50 characters" in str(exc_info.value)

    def test_tags_validation_empty_string(self):
        """Empty tag string should fail."""
        with pytest.raises(ValidationError) as exc_info:
            Task(title="Test", tags=["valid", ""])
        assert "empty strings" in str(exc_info.value)

    def test_timestamps_auto_generated(self):
        """created_at and updated_at should be auto-set."""
        task = Task(title="Test")
        assert task.created_at is not None
        assert task.updated_at is not None


# =============================================================================
# TasksCreateInput Tests
# =============================================================================

class TestTasksCreateInput:
    """Tests for create input validation."""

    def test_minimal_input(self):
        """Only title required."""
        input_data = TasksCreateInput(title="New task")
        assert input_data.title == "New task"
        assert input_data.response_format == ResponseFormat.MARKDOWN

    def test_full_input(self):
        """All fields specified."""
        input_data = TasksCreateInput(
            title="New task",
            description="Details here",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            tags=["api", "v1"],
            response_format=ResponseFormat.JSON,
        )
        assert input_data.status == TaskStatus.IN_PROGRESS
        assert input_data.response_format == ResponseFormat.JSON

    def test_extra_fields_forbidden(self):
        """Unknown fields should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TasksCreateInput(title="Test", unknown_field="value")
        assert "extra" in str(exc_info.value).lower()


# =============================================================================
# TasksListInput Tests
# =============================================================================

class TestTasksListInput:
    """Tests for list input validation."""

    def test_defaults(self):
        """Default values should be set."""
        input_data = TasksListInput()
        assert input_data.status is None
        assert input_data.priority is None
        assert input_data.tag is None
        assert input_data.limit == 20
        assert input_data.offset == 0

    def test_limit_bounds(self):
        """Limit must be 1-100."""
        with pytest.raises(ValidationError):
            TasksListInput(limit=0)
        with pytest.raises(ValidationError):
            TasksListInput(limit=101)

    def test_offset_non_negative(self):
        """Offset must be >= 0."""
        with pytest.raises(ValidationError):
            TasksListInput(offset=-1)


# =============================================================================
# TasksGetInput Tests
# =============================================================================

class TestTasksGetInput:
    """Tests for get input validation."""

    def test_valid_uuid(self):
        """Valid UUID should pass."""
        input_data = TasksGetInput(task_id="550e8400-e29b-41d4-a716-446655440000")
        assert input_data.task_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_invalid_uuid(self):
        """Invalid UUID format should fail."""
        with pytest.raises(ValidationError) as exc_info:
            TasksGetInput(task_id="not-a-uuid")
        assert "Invalid task ID format" in str(exc_info.value)


# =============================================================================
# TasksUpdateInput Tests
# =============================================================================

class TestTasksUpdateInput:
    """Tests for update input validation."""

    def test_only_task_id_required(self):
        """Only task_id is required, other fields optional."""
        input_data = TasksUpdateInput(
            task_id="550e8400-e29b-41d4-a716-446655440000"
        )
        assert input_data.title is None
        assert input_data.status is None

    def test_partial_update(self):
        """Can specify subset of fields."""
        input_data = TasksUpdateInput(
            task_id="550e8400-e29b-41d4-a716-446655440000",
            status=TaskStatus.COMPLETED,
        )
        assert input_data.status == TaskStatus.COMPLETED
        assert input_data.title is None


# =============================================================================
# TasksDeleteInput Tests
# =============================================================================

class TestTasksDeleteInput:
    """Tests for delete input validation."""

    def test_valid_input(self):
        """Valid UUID should pass."""
        input_data = TasksDeleteInput(
            task_id="550e8400-e29b-41d4-a716-446655440000"
        )
        assert input_data.task_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_invalid_uuid(self):
        """Invalid UUID should fail."""
        with pytest.raises(ValidationError):
            TasksDeleteInput(task_id="invalid")
