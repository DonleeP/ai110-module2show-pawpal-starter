"""Simple tests for the PawPal pet care system."""

from datetime import datetime

from pawpal_system import Frequency, Pet, Scheduler, Task, TaskType


def make_task(id, hour, *, pet_id="p1", frequency=None, completed=False, day=30):
    """Build a Task with sensible defaults so tests stay readable."""
    return Task(
        id=id,
        title=id,
        description="",
        type=TaskType.FEEDING,
        due_date=datetime(2026, 6, day, hour, 0),
        pet_id=pet_id,
        frequency=frequency,
        completed=completed,
    )


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


# --- Sorting correctness -------------------------------------------------


def test_sort_by_time_returns_chronological_order():
    """Sorting: tasks come back ascending by due_date regardless of insert order."""
    scheduler = Scheduler()
    noon = make_task("noon", 12)
    morning = make_task("morning", 8)
    evening = make_task("evening", 18)
    # Add out of order on purpose.
    scheduler.schedule_task(noon)
    scheduler.schedule_task(evening)
    scheduler.schedule_task(morning)

    ordered = scheduler.sort_by_time()

    assert [t.id for t in ordered] == ["morning", "noon", "evening"]


def test_sort_by_time_does_not_mutate_original_list():
    """Sorting: sort_by_time() returns a new list and leaves the schedule untouched."""
    scheduler = Scheduler()
    scheduler.schedule_task(make_task("late", 18))
    scheduler.schedule_task(make_task("early", 8))

    scheduler.sort_by_time()

    # Original insertion order is preserved on the scheduler itself.
    assert [t.id for t in scheduler.tasks] == ["late", "early"]


def test_sort_by_time_empty_schedule():
    """Sorting edge case: sorting an empty schedule returns an empty list."""
    assert Scheduler().sort_by_time() == []


# --- Recurrence logic ----------------------------------------------------


def test_completing_daily_task_creates_task_for_next_day():
    """Recurrence: completing a daily task returns a new task due the following day."""
    task = make_task("feed", 8, frequency=Frequency.DAILY, day=30)

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    # June 30 + 1 day rolls into July.
    assert next_task.due_date == datetime(2026, 7, 1, 8, 0)
    assert next_task.frequency is Frequency.DAILY


def test_one_off_task_has_no_next_occurrence():
    """Recurrence edge case: a task with no frequency spawns nothing on completion."""
    task = make_task("vet", 9, frequency=None)

    assert task.mark_complete() is None


def test_complete_task_auto_schedules_next_occurrence():
    """Recurrence: Scheduler.complete_task adds the recurring follow-up to the schedule."""
    scheduler = Scheduler()
    scheduler.schedule_task(make_task("walk", 8, frequency=Frequency.DAILY, day=30))

    scheduler.complete_task("walk")

    # Original + newly scheduled next occurrence.
    assert len(scheduler.tasks) == 2
    next_task = [t for t in scheduler.tasks if not t.completed][0]
    assert next_task.due_date == datetime(2026, 7, 1, 8, 0)


def test_repeated_completion_does_not_accumulate_id_suffixes():
    """Recurrence edge case: ids stay 'stem@date', not 'stem@date@date'."""
    task = make_task("feed", 8, frequency=Frequency.DAILY, day=30)

    first = task.mark_complete()
    second = first.mark_complete()

    assert first.id == "feed@20260701"
    assert second.id == "feed@20260702"


# --- Conflict detection --------------------------------------------------


def test_detect_conflicts_flags_duplicate_times():
    """Conflict detection: two active tasks at the same time produce a warning."""
    scheduler = Scheduler()
    scheduler.schedule_task(make_task("feed", 8, pet_id="p1"))
    scheduler.schedule_task(make_task("meds", 8, pet_id="p2"))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_detect_conflicts_ignores_different_times():
    """Conflict detection edge case: distinct times produce no warnings."""
    scheduler = Scheduler()
    scheduler.schedule_task(make_task("feed", 8))
    scheduler.schedule_task(make_task("walk", 9))

    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_ignores_completed_tasks():
    """Conflict detection edge case: a completed task at the same time isn't a conflict."""
    scheduler = Scheduler()
    scheduler.schedule_task(make_task("feed", 8, completed=True))
    scheduler.schedule_task(make_task("meds", 8))

    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_three_tasks_same_time():
    """Conflict detection edge case: three tasks at one time yield three pairwise warnings."""
    scheduler = Scheduler()
    scheduler.schedule_task(make_task("a", 8))
    scheduler.schedule_task(make_task("b", 8))
    scheduler.schedule_task(make_task("c", 8))

    assert len(scheduler.detect_conflicts()) == 3


def test_detect_conflicts_empty_schedule():
    """Conflict detection edge case: an empty schedule never raises and returns []."""
    assert Scheduler().detect_conflicts() == []
