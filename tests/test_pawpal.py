"""Simple tests for the PawPal pet care system."""

from datetime import datetime

from pawpal_system import Pet, Task, TaskType


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() flips completed from False to True."""
    task = Task(
        id="t1",
        title="Morning walk",
        description="30 minute walk",
        type=TaskType.WALK,
        due_date=datetime(2026, 6, 30, 8, 0),
        pet_id="p1",
    )
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task to a Pet grows its task list by one."""
    pet = Pet(id="p1", name="Rex", species="dog", breed="Lab", age=3, owner_id="o1")
    assert len(pet.tasks) == 0

    task = Task(
        id="t1",
        title="Dinner",
        description="One cup of kibble",
        type=TaskType.FEEDING,
        due_date=datetime(2026, 6, 30, 18, 30),
        pet_id="p1",
    )
    pet.add_task(task)

    assert len(pet.tasks) == 1
