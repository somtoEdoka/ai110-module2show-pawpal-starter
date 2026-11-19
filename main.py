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
            title="Dinner",
            category="feeding",
            duration_minutes=15,
            priority="medium",
            preferred_time=time(18, 0),
            recurrence="daily",
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


if __name__ == "__main__":
    main()
