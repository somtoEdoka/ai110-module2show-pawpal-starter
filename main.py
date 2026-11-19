"""Command-line demo for generating a PawPal+ daily schedule."""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task
from tabulate import tabulate


CATEGORY_EMOJIS = {
    "exercise": "🐕",
    "feeding": "🍽️",
    "health": "💊",
    "grooming": "🧼",
    "enrichment": "🎾",
}
CATEGORY_LABELS = {
    "exercise": "Walk / Exercise",
    "feeding": "Feeding",
    "health": "Medication / Health",
    "grooming": "Grooming",
    "enrichment": "Enrichment",
}


def category_label(category: str) -> str:
    """Return a category with its matching visual indicator."""
    normalized = category.strip().lower()
    emoji = CATEGORY_EMOJIS.get(normalized, "🐾")
    label = CATEGORY_LABELS.get(normalized, category.title() or "Other")
    return f"{emoji} {label}"


def task_status(completed: bool) -> str:
    """Return a readable status badge."""
    return "✅ Completed" if completed else "⏳ Pending"


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

    pet_names = {
        task.task_id: pet.name for pet in owner.pets for task in pet.tasks
    }
    scheduled_by_id = {
        item.task.task_id: item for item in plan.scheduled_items
    }
    priority_order = scheduler.sort_by_priority_and_time(
        [item.task for item in plan.scheduled_items]
    )
    schedule_rows = []
    for task in priority_order:
        item = scheduled_by_id[task.task_id]
        schedule_rows.append(
            {
                "Time": (
                    f"{item.start_time.strftime('%H:%M')}–"
                    f"{item.end_time.strftime('%H:%M')}"
                ),
                "Pet": pet_names[task.task_id],
                "Task": task.title,
                "Category": category_label(task.category),
                "Priority": task.priority.title(),
                "Status": task_status(task.completed),
            }
        )

    print(f"Today's Schedule — {today.isoformat()}")
    print(tabulate(schedule_rows, headers="keys", tablefmt="fancy_grid"))
    print(f"Total scheduled: {plan.total_minutes_scheduled} minutes")

    if plan.skipped_tasks:
        skipped_rows = [
            {
                "Task": task.title,
                "Status": task_status(task.completed),
                "Reason": reason,
            }
            for task, reason in plan.skipped_tasks
        ]
        print("\nSkipped tasks")
        print(tabulate(skipped_rows, headers="keys", tablefmt="fancy_grid"))

    print("\nTasks sorted by priority and preferred time")
    task_rows = []
    for task in scheduler.sort_by_priority_and_time(owner.get_all_tasks()):
        preferred_time = task.preferred_time
        if isinstance(preferred_time, time):
            preferred_time = preferred_time.strftime("%H:%M")
        else:
            preferred_time = preferred_time or "unscheduled"
        task_rows.append(
            {
                "Preferred time": preferred_time,
                "Pet": pet_names[task.task_id],
                "Task": task.title,
                "Category": category_label(task.category),
                "Priority": task.priority.title(),
                "Status": task_status(task.completed),
            }
        )
    print(tabulate(task_rows, headers="keys", tablefmt="fancy_grid"))

    print("\nUncompleted tasks for Biscuit")
    pending_rows = [
        {
            "Task": task.title,
            "Category": category_label(task.category),
            "Status": task_status(task.completed),
        }
        for task in scheduler.filter_tasks(pet_name="Biscuit", completed=False)
    ]
    print(tabulate(pending_rows, headers="keys", tablefmt="fancy_grid"))

    next_dinner = scheduler.mark_task_complete(dog.tasks[0])
    if next_dinner is not None:
        print(
            f"\n✅ Completed {dog.tasks[0].title}; next occurrence: "
            f"{next_dinner.start_date.isoformat()}"
        )

    print("\nConflict warnings")
    for warning in scheduler.detect_conflicts():
        print(f"  ⚠️ Conflict: {warning.removeprefix('Conflict: ')}")


if __name__ == "__main__":
    main()
