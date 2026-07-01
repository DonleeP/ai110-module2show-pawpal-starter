"""PawPal pet care system.

Class skeletons generated from diagrams/uml_draft.mmd.
Pet and Task use dataclasses to keep the data-holding objects clean.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class TaskType(Enum):
    """The kind of care activity a Task represents."""

    FEEDING = "feeding"
    WALK = "walk"
    VET = "vet"
    GROOMING = "grooming"
    MEDICATION = "medication"


class Frequency(Enum):
    """How often a recurring Task repeats."""

    DAILY = "daily"
    WEEKLY = "weekly"

    @property
    def delta(self) -> timedelta:
        """How far to advance a due date to reach the next occurrence.

        Returns:
            A ``timedelta`` of one day for ``DAILY`` and one week for
            ``WEEKLY``. Using ``timedelta`` keeps calendar arithmetic correct
            across month and year boundaries.
        """
        if self is Frequency.DAILY:
            return timedelta(days=1)
        return timedelta(weeks=1)


@dataclass
class Task:
    """A single pet-care activity."""

    id: str
    title: str
    description: str
    type: TaskType
    due_date: datetime
    pet_id: str
    frequency: Frequency | None = None
    completed: bool = False

    @property
    def recurring(self) -> bool:
        """True if this task repeats on a schedule."""
        return self.frequency is not None

    def mark_complete(self) -> "Task | None":
        """Mark this task as done and, if recurring, spawn its next occurrence.

        Sets ``completed`` to ``True``. If the task repeats (has a
        ``frequency``), a fresh Task for the next occurrence is produced so the
        caller can add it to the schedule.

        Returns:
            The next-occurrence Task for a recurring task, or ``None`` for a
            one-off task.
        """
        self.completed = True
        return self.next_occurrence()

    def next_occurrence(self) -> "Task | None":
        """Build the next instance of a recurring task.

        The new due date is this task's due date advanced by the frequency's
        ``timedelta`` (daily -> +1 day, weekly -> +7 days). ``timedelta``
        handles month/year rollover, so e.g. June 30 + 1 day becomes July 1.
        The new id reuses this task's stem (any prior ``@date`` suffix is
        stripped first) and stamps the new date, so repeated completions
        produce unique, non-accumulating ids.

        Returns:
            A new, uncompleted Task at the next due date, or ``None`` if this
            task is one-off (``frequency is None``).
        """
        if self.frequency is None:
            return None
        new_due = self.due_date + self.frequency.delta
        # Derive a stable id: strip any prior "@date" suffix so repeated
        # completions don't accumulate suffixes, then stamp the new date.
        stem = self.id.split("@", 1)[0]
        return Task(
            id=f"{stem}@{new_due:%Y%m%d}",
            title=self.title,
            description=self.description,
            type=self.type,
            due_date=new_due,
            pet_id=self.pet_id,
            frequency=self.frequency,
        )

    def reschedule(self, new_date: datetime) -> None:
        """Move this task to a new due date."""
        self.due_date = new_date

    def is_overdue(self) -> bool:
        """Return True if the task is past due and not completed."""
        return not self.completed and self.due_date < datetime.now()


@dataclass
class Pet:
    """A pet belonging to an Owner, holding its own care tasks."""

    id: str
    name: str
    species: str
    breed: str
    age: int
    owner_id: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def get_upcoming_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]


class Owner:
    """A pet owner with contact details and a collection of pets."""

    def __init__(self, id: str, name: str, email: str, phone: str) -> None:
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet by id."""
        self.pets = [pet for pet in self.pets if pet.id != pet_id]

    def view_schedule(self) -> list[Task]:
        """Return all tasks across this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Orchestrates care tasks across all pets."""

    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def schedule_task(self, task: Task) -> None:
        """Add a task to the schedule."""
        self.tasks.append(task)

    def cancel_task(self, task_id: str) -> None:
        """Remove a task from the schedule by id."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def complete_task(self, task_id: str) -> Task | None:
        """Mark a scheduled task complete and auto-add its next occurrence.

        Args:
            task_id: The id of the task to complete. Unknown ids are ignored.

        Returns:
            The newly scheduled next-occurrence Task if the completed task was
            recurring, otherwise ``None`` (also ``None`` if no task matched).
        """
        for task in self.tasks:
            if task.id == task_id:
                next_task = task.mark_complete()
                if next_task is not None:
                    self.schedule_task(next_task)
                return next_task
        return None

    def sort_by_time(self) -> list[Task]:
        """Return the scheduled tasks ordered by their due time.

        Uses a lambda as the ``key`` so ``sorted()`` compares each Task by its
        ``due_date`` instead of the Task object itself. ``datetime`` values
        compare chronologically, so this is equivalent to (but safer than)
        sorting the "HH:MM" strings, which only works within a single day.

        Returns:
            A new list of the tasks sorted ascending by ``due_date``. The
            scheduler's own list is left unchanged.
        """
        return sorted(self.tasks, key=lambda task: task.due_date)

    def detect_conflicts(self, pet_names: dict[str, str] | None = None) -> list[str]:
        """Return warning messages for tasks scheduled at the same time.

        Lightweight strategy: sort by due time, then compare each task only
        against the ones immediately after it, stopping as soon as the time
        differs (the list is sorted, so no later task can match). Two active
        (not completed) tasks at the exact same ``due_date`` are a conflict,
        whether they belong to the same pet or different pets.

        Returns a (possibly empty) list of strings — it never raises, so the
        caller can print warnings and keep running.
        """
        pet_names = pet_names or {}
        active = [task for task in self.sort_by_time() if not task.completed]
        warnings: list[str] = []
        for i, first in enumerate(active):
            for second in active[i + 1:]:
                if second.due_date != first.due_date:
                    break  # sorted: nothing further shares this time
                scope = "same pet" if first.pet_id == second.pet_id else "different pets"
                who_a = pet_names.get(first.pet_id, first.pet_id)
                who_b = pet_names.get(second.pet_id, second.pet_id)
                warnings.append(
                    f"WARNING: conflict at {first.due_date:%H:%M} - "
                    f"'{first.title}' ({who_a}) and '{second.title}' ({who_b}) [{scope}]"
                )
        return warnings

    def filter_tasks(
        self,
        *,
        completed: bool | None = None,
        pet_id: str | None = None,
    ) -> list[Task]:
        """Return tasks matching the given filters.

        Each filter is optional: pass ``completed=True/False`` to filter by
        completion status, ``pet_id`` to filter by pet. Filters combine (AND),
        and omitting one (leaving it ``None``) means "don't filter on it".
        """
        result = self.tasks
        if completed is not None:
            result = [task for task in result if task.completed == completed]
        if pet_id is not None:
            result = [task for task in result if task.pet_id == pet_id]
        return result

    def get_tasks_for_day(self, date: datetime) -> list[Task]:
        """Return tasks due on the given day."""
        raise NotImplementedError

    def get_overdue_tasks(self) -> list[Task]:
        """Return tasks that are past due and not completed."""
        raise NotImplementedError

    def send_reminder(self, task: Task) -> None:
        """Send a reminder for the given task."""
        raise NotImplementedError
