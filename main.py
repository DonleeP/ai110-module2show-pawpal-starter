from datetime import datetime

from pawpal_system import TaskType, Task, Pet, Owner, Scheduler


def main() -> None:
    owner = Owner(
        id="o1",
        name="Alice Nguyen",
        email="alice@example.com",
        phone="555-0101",
    )

    rex = Pet(
        id="p1",
        name="Rex",
        species="dog",
        breed="Labrador",
        age=3,
        owner_id=owner.id,
    )
    whiskers = Pet(
        id="p2",
        name="Whiskers",
        species="cat",
        breed="Tabby",
        age=5,
        owner_id=owner.id,
    )

    owner.add_pet(rex)
    owner.add_pet(whiskers)

    today = datetime.now()

    rex.add_task(
        Task(
            id="t1",
            title="Morning walk",
            description="30 minute walk around the block",
            type=TaskType.WALK,
            due_date=today.replace(hour=8, minute=0, second=0, microsecond=0),
            pet_id=rex.id,
            recurring=True,
        )
    )
    rex.add_task(
        Task(
            id="t2",
            title="Dinner",
            description="One cup of kibble",
            type=TaskType.FEEDING,
            due_date=today.replace(hour=18, minute=30, second=0, microsecond=0),
            pet_id=rex.id,
            recurring=True,
        )
    )
    whiskers.add_task(
        Task(
            id="t3",
            title="Flea medication",
            description="Apply monthly flea treatment",
            type=TaskType.MEDICATION,
            due_date=today.replace(hour=12, minute=0, second=0, microsecond=0),
            pet_id=whiskers.id,
        )
    )

    print_todays_schedule(owner, today)


def print_todays_schedule(owner: Owner, day: datetime) -> None:
    """Print all of the owner's tasks due on the given day, ordered by time."""
    pet_names = {pet.id: pet.name for pet in owner.pets}
    todays_tasks = sorted(
        (
            task
            for task in owner.view_schedule()
            if task.due_date.date() == day.date()
        ),
        key=lambda task: task.due_date,
    )

    print(f"Today's Schedule ({day:%A, %B %d, %Y})")
    print("-" * 40)
    if not todays_tasks:
        print("No tasks scheduled for today.")
        return
    for task in todays_tasks:
        status = "✓" if task.completed else " "
        pet_name = pet_names.get(task.pet_id, task.pet_id)
        print(f"[{status}] {task.due_date:%H:%M}  {pet_name}: {task.title}")


if __name__ == "__main__":
    main()


