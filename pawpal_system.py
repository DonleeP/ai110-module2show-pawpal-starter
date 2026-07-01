"""PawPal pet care system.

Class skeletons generated from diagrams/uml_draft.mmd.
Pet and Task use dataclasses to keep the data-holding objects clean.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskType(Enum):
    """The kind of care activity a Task represents."""

    FEEDING = "feeding"
    WALK = "walk"
    VET = "vet"
    GROOMING = "grooming"
    MEDICATION = "medication"


@dataclass
class Task:
    """A single pet-care activity."""

    id: str
    title: str
    description: str
    type: TaskType
    due_date: datetime
    pet_id: str
    recurring: bool = False
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

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
        raise NotImplementedError

    def cancel_task(self, task_id: str) -> None:
        """Remove a task from the schedule by id."""
        raise NotImplementedError

    def get_tasks_for_day(self, date: datetime) -> list[Task]:
        """Return tasks due on the given day."""
        raise NotImplementedError

    def get_overdue_tasks(self) -> list[Task]:
        """Return tasks that are past due and not completed."""
        raise NotImplementedError

    def send_reminder(self, task: Task) -> None:
        """Send a reminder for the given task."""
        raise NotImplementedError
