from datetime import datetime

from pawpal_system import Frequency, TaskType, Task, Pet, Owner, Scheduler


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

    def at(hour: int, minute: int = 0) -> datetime:
        return today.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Add tasks to the Scheduler intentionally OUT OF ORDER (18:30, 8:00,
    # 12:00, 7:00) so we can prove sort_by_time() actually reorders them.
    scheduler = Scheduler()
    scheduler.schedule_task(
        Task("t1", "Dinner", "One cup of kibble", TaskType.FEEDING, at(18, 30), rex.id, frequency=Frequency.DAILY)
    )
    scheduler.schedule_task(
        Task("t2", "Morning walk", "30 minute walk", TaskType.WALK, at(8, 0), rex.id, frequency=Frequency.DAILY)
    )
    scheduler.schedule_task(
        Task("t3", "Flea medication", "Monthly flea treatment", TaskType.MEDICATION, at(12, 0), whiskers.id, frequency=Frequency.WEEKLY)
    )
    breakfast = Task("t4", "Breakfast", "Half cup of kibble", TaskType.FEEDING, at(7, 0), whiskers.id)
    breakfast.mark_complete()  # already done earlier today (one-off, no repeat)
    scheduler.schedule_task(breakfast)
    # Deliberately clashes with Whiskers' 12:00 flea medication (different pets).
    scheduler.schedule_task(
        Task("t5", "Vet checkup", "Annual exam", TaskType.VET, at(12, 0), rex.id)
    )

    pet_names = {pet.id: pet.name for pet in owner.pets}

    # 1. Sorting — sort_by_time() puts the out-of-order tasks back in order.
    print(f"Today's Schedule ({today:%A, %B %d, %Y})")
    print("-" * 40)
    print_tasks(scheduler.sort_by_time(), pet_names)

    # 2. Filter by completion status.
    print("\nStill to do (not completed):")
    print("-" * 40)
    todo = scheduler.filter_tasks(completed=False)
    print_tasks(sorted(todo, key=lambda task: task.due_date), pet_names)

    # 3. Filter by pet (resolve the pet's name to its id, since Tasks carry pet_id).
    print(f"\n{rex.name}'s tasks only:")
    print("-" * 40)
    rex_tasks = scheduler.filter_tasks(pet_id=rex.id)
    print_tasks(sorted(rex_tasks, key=lambda task: task.due_date), pet_names)

    # 4. Conflict detection — warn about tasks scheduled at the same time.
    print("\nConflict check:")
    print("-" * 40)
    conflicts = scheduler.detect_conflicts(pet_names)
    if conflicts:
        for warning in conflicts:
            print(warning)
    else:
        print("No conflicts found.")

    # 5. Recurrence — completing the DAILY walk auto-creates tomorrow's walk.
    next_walk = scheduler.complete_task("t2")
    print("\nAfter completing the daily 'Morning walk':")
    print("-" * 40)
    if next_walk is not None:
        print(f"Auto-created next occurrence -> {next_walk.id} due {next_walk.due_date:%a %H:%M}")
    print_tasks(scheduler.sort_by_time(), pet_names)


def print_tasks(tasks: list[Task], pet_names: dict[str, str]) -> None:
    """Print each task as a status/time/pet/title line."""
    if not tasks:
        print("No tasks.")
        return
    for task in tasks:
        status = "x" if task.completed else " "
        pet_name = pet_names.get(task.pet_id, task.pet_id)
        print(f"[{status}] {task.due_date:%H:%M}  {pet_name}: {task.title}")


if __name__ == "__main__":
    main()


