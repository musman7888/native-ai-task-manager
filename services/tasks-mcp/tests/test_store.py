"""Tests for TaskStore operations."""

import pytest
from datetime import datetime, timezone

from tasks_mcp.store import TaskStore, get_store
from tasks_mcp.models import TaskStatus, TaskPriority


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def store():
    """Fresh TaskStore instance for each test."""
    return TaskStore()


@pytest.fixture
def populated_store(store):
    """Store with sample tasks for testing."""
    store.create(title="Task 1", priority=TaskPriority.HIGH, tags=["urgent"])
    store.create(title="Task 2", status=TaskStatus.IN_PROGRESS)
    store.create(title="Task 3", priority=TaskPriority.LOW, tags=["backlog"])
    store.create(title="Task 4", status=TaskStatus.COMPLETED)
    store.create(title="Task 5", tags=["urgent", "api"])
    return store


# =============================================================================
# Create Tests
# =============================================================================

class TestStoreCreate:
    """Tests for task creation."""

    def test_create_minimal(self, store):
        """Create task with only title."""
        task = store.create(title="Test task")

        assert task.title == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert store.count() == 1

    def test_create_full(self, store):
        """Create task with all fields."""
        task = store.create(
            title="Full task",
            description="Details",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            tags=["api", "v1"],
        )

        assert task.title == "Full task"
        assert task.description == "Details"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.tags == ["api", "v1"]

    def test_create_assigns_unique_ids(self, store):
        """Each task gets a unique ID."""
        task1 = store.create(title="Task 1")
        task2 = store.create(title="Task 2")

        assert task1.id != task2.id


# =============================================================================
# Get Tests
# =============================================================================

class TestStoreGet:
    """Tests for task retrieval."""

    def test_get_existing(self, store):
        """Get an existing task by ID."""
        created = store.create(title="Test")
        retrieved = store.get(str(created.id))

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Test"

    def test_get_nonexistent(self, store):
        """Get returns None for unknown ID."""
        result = store.get("550e8400-e29b-41d4-a716-446655440000")
        assert result is None


# =============================================================================
# List Tests
# =============================================================================

class TestStoreList:
    """Tests for task listing and filtering."""

    def test_list_empty(self, store):
        """Empty store returns empty list."""
        tasks, total, has_more, next_offset = store.list()

        assert tasks == []
        assert total == 0
        assert has_more is False
        assert next_offset is None

    def test_list_all(self, populated_store):
        """List all tasks without filters."""
        tasks, total, has_more, next_offset = populated_store.list()

        assert len(tasks) == 5
        assert total == 5
        assert has_more is False

    def test_list_filter_by_status(self, populated_store):
        """Filter by status."""
        tasks, total, _, _ = populated_store.list(status=TaskStatus.IN_PROGRESS)

        assert len(tasks) == 1
        assert all(t.status == TaskStatus.IN_PROGRESS for t in tasks)

    def test_list_filter_by_priority(self, populated_store):
        """Filter by priority."""
        tasks, total, _, _ = populated_store.list(priority=TaskPriority.HIGH)

        assert len(tasks) == 1
        assert all(t.priority == TaskPriority.HIGH for t in tasks)

    def test_list_filter_by_tag(self, populated_store):
        """Filter by single tag."""
        tasks, total, _, _ = populated_store.list(tag="urgent")

        assert len(tasks) == 2
        assert all("urgent" in t.tags for t in tasks)

    def test_list_pagination(self, populated_store):
        """Pagination with limit and offset."""
        # First page
        tasks1, total, has_more, next_offset = populated_store.list(limit=2)
        assert len(tasks1) == 2
        assert total == 5
        assert has_more is True
        assert next_offset == 2

        # Second page
        tasks2, _, has_more2, next_offset2 = populated_store.list(limit=2, offset=2)
        assert len(tasks2) == 2
        assert has_more2 is True
        assert next_offset2 == 4

        # Last page
        tasks3, _, has_more3, next_offset3 = populated_store.list(limit=2, offset=4)
        assert len(tasks3) == 1
        assert has_more3 is False
        assert next_offset3 is None

    def test_list_sorted_by_created_at_desc(self, store):
        """Tasks sorted by created_at descending (newest first)."""
        import time

        task1 = store.create(title="First")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        task2 = store.create(title="Second")

        tasks, _, _, _ = store.list()

        assert tasks[0].id == task2.id  # Newest first
        assert tasks[1].id == task1.id


# =============================================================================
# Update Tests
# =============================================================================

class TestStoreUpdate:
    """Tests for task updates."""

    def test_update_title(self, store):
        """Update task title."""
        task = store.create(title="Original")
        updated, changes = store.update(str(task.id), title="Updated")

        assert updated.title == "Updated"
        assert "title" in changes
        assert changes["title"]["old"] == "Original"
        assert changes["title"]["new"] == "Updated"

    def test_update_status(self, store):
        """Update task status."""
        task = store.create(title="Test")
        updated, changes = store.update(
            str(task.id),
            status=TaskStatus.COMPLETED
        )

        assert updated.status == TaskStatus.COMPLETED
        assert "status" in changes

    def test_update_multiple_fields(self, store):
        """Update multiple fields at once."""
        task = store.create(title="Test", priority=TaskPriority.LOW)
        updated, changes = store.update(
            str(task.id),
            title="Updated",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
        )

        assert updated.title == "Updated"
        assert updated.priority == TaskPriority.HIGH
        assert updated.status == TaskStatus.IN_PROGRESS
        assert len(changes) == 3

    def test_update_no_changes(self, store):
        """Update with same values returns no changes."""
        task = store.create(title="Test")
        updated, changes = store.update(str(task.id), title="Test")

        assert updated.title == "Test"
        assert changes == {}

    def test_update_nonexistent(self, store):
        """Update nonexistent task returns None."""
        result, changes = store.update(
            "550e8400-e29b-41d4-a716-446655440000",
            title="New"
        )

        assert result is None
        assert changes == {}

    def test_update_timestamps(self, store):
        """Update modifies updated_at timestamp."""
        task = store.create(title="Test")
        original_updated_at = task.updated_at

        import time
        time.sleep(0.01)

        updated, changes = store.update(str(task.id), title="Updated")

        assert updated.updated_at > original_updated_at


# =============================================================================
# Delete Tests
# =============================================================================

class TestStoreDelete:
    """Tests for task deletion."""

    def test_delete_existing(self, store):
        """Delete existing task."""
        task = store.create(title="Test")
        task_id = str(task.id)

        deleted = store.delete(task_id)

        assert deleted is not None
        assert deleted.id == task.id
        assert store.get(task_id) is None
        assert store.count() == 0

    def test_delete_nonexistent(self, store):
        """Delete nonexistent task returns None."""
        result = store.delete("550e8400-e29b-41d4-a716-446655440000")
        assert result is None


# =============================================================================
# Utility Tests
# =============================================================================

class TestStoreUtilities:
    """Tests for utility methods."""

    def test_count(self, store):
        """Count returns number of tasks."""
        assert store.count() == 0

        store.create(title="Task 1")
        assert store.count() == 1

        store.create(title="Task 2")
        assert store.count() == 2

    def test_clear(self, populated_store):
        """Clear removes all tasks."""
        assert populated_store.count() == 5

        populated_store.clear()

        assert populated_store.count() == 0


# =============================================================================
# Singleton Tests
# =============================================================================

class TestGetStore:
    """Tests for the singleton pattern."""

    def test_get_store_returns_same_instance(self):
        """get_store returns the same instance."""
        # Note: This modifies global state
        store1 = get_store()
        store2 = get_store()

        assert store1 is store2
