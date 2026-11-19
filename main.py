"""Command-line demo for generating a PawPal+ daily schedule."""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Create a demo owner and print today's generated schedule."""
    today = date.today()

    owner = Owner(name="Jordan", available_minutes=120)

    dog = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=4)
    cat = Pet(name="Mochi", species="cat", breed="Domestic Shorthair", age=3)

    dog.add_task(
        Task(
            title="Dinner",
            category="feeding",
            duration_minutes=15,
            priority="medium",
            preferred_time=time(18, 0),
            recurrence="daily",
            start_date=today,
        )
    )
    dog.add_task(
        Task(
            title="Morning walk",
            category="exercise",
            duration_minutes=30,
            priority="high",
            preferred_time=time(8, 0),
            recurrence="once",
            start_date=today,
        )
    )
    dog.add_task(
        Task(
            title="Training",
            category="enrichment",
            duration_minutes=15,
            priority="medium",
            preferred_time=time(9, 30),
            recurrence="once",
            start_date=today,
        )
    )
    cat.add_task(
        Task(
            title="Play session",
            category="enrichment",
            duration_minutes=20,
            priority="high",
            preferred_time=time(9, 30),
            recurrence="once",
            start_date=today,
        )
    )
    cat.add_task(
        Task(
            title="Medication",
            category="health",
            duration_minutes=10,
            priority="low",
            preferred_time=time(12, 0),
            recurrence="daily",
            start_date=today,
        )
    )

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner=owner, buffer_minutes=10)
    plan = scheduler.generate_plan(today)

    print("Today's Schedule")
    print("================")
    print(plan.get_summary())

    print("\nTasks sorted by preferred time")
    for task in scheduler.sort_by_time(owner.get_all_tasks()):
        preferred_time = task.preferred_time
        if isinstance(preferred_time, time):
            preferred_time = preferred_time.strftime("%H:%M")
        else:
            preferred_time = preferred_time or "unscheduled"
        print(f"  {preferred_time} — {task.title}")

    print("\nUncompleted tasks for Biscuit")
    for task in scheduler.filter_tasks(pet_name="Biscuit", completed=False):
        print(f"  {task.title}")

    next_dinner = scheduler.mark_task_complete(dog.tasks[0])
    if next_dinner is not None:
        print(
            f"\nCompleted {dog.tasks[0].title}; next occurrence: "
            f"{next_dinner.start_date.isoformat()}"
        )

    print("\nConflict warnings")
    for warning in scheduler.detect_conflicts():
        print(f"  {warning}")


if __name__ == "__main__":
    main()
