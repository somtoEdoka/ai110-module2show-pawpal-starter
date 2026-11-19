"""Unit tests for PawPal+ task and pet behavior."""

from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_mark_complete():
    """Marking a task complete should set completed to True."""
    task = Task(title="Morning walk")

    task.mark_complete()

    assert task.completed is True


def test_pet_add_task():
    """Adding a task should increase the pet's task count by one."""
    pet = Pet(name="Biscuit")
    task = Task(title="Dinner")
    initial_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1


def test_sort_by_time_handles_time_strings_and_unscheduled_tasks():
    scheduler = Scheduler()
    tasks = [
        Task(title="Unscheduled"),
        Task(title="Evening", preferred_time=time(18, 0)),
        Task(title="Morning", preferred_time="08:30"),
        Task(title="Midnight", preferred_time=time(0, 0)),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.title for task in sorted_tasks] == [
        "Midnight",
        "Morning",
        "Evening",
        "Unscheduled",
    ]


def test_filter_tasks_by_pet_and_completion():
    pet = Pet(name="Biscuit")
    pet.add_task(Task(title="Walk"))
    completed_task = Task(title="Dinner", completed=True)
    pet.add_task(completed_task)
    owner = Owner(pets=[pet, Pet(name="Mochi", tasks=[Task(title="Play")])])

    filtered_tasks = Scheduler(owner).filter_tasks("biscuit", completed=True)

    assert filtered_tasks == [completed_task]


def test_mark_recurring_task_complete_adds_next_occurrence_to_same_pet():
    start_date = date(2026, 11, 19)
    pet = Pet(name="Biscuit")
    task = Task(title="Dinner", recurrence="daily", start_date=start_date)
    pet.add_task(task)
    scheduler = Scheduler(Owner(pets=[pet]))

    next_task = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task is not task
    assert next_task.completed is False
    assert next_task.start_date == start_date + timedelta(days=1)
    assert pet.tasks[-1] is next_task


def test_mark_weekly_task_complete_advances_one_week():
    start_date = date(2026, 11, 19)
    pet = Pet(name="Mochi")
    task = Task(title="Grooming", recurrence="weekly", start_date=start_date)
    pet.add_task(task)

    next_task = Scheduler(Owner(pets=[pet])).mark_task_complete(task)

    assert next_task is not None
    assert next_task.start_date == start_date + timedelta(days=7)


def test_detect_conflicts_reports_same_start_and_overlapping_slots():
    scheduler = Scheduler()
    tasks = [
        Task(title="Walk", preferred_time="09:30", duration_minutes=30),
        Task(title="Training", preferred_time=time(9, 30), duration_minutes=15),
        Task(title="Medication", preferred_time=time(9, 45), duration_minutes=10),
        Task(title="Unscheduled", duration_minutes=20),
        Task(title="Invalid time", preferred_time="not a time", duration_minutes=10),
    ]

    warnings = scheduler.detect_conflicts(tasks)

    assert len(warnings) == 2
    assert any("'Walk'" in warning and "'Training'" in warning for warning in warnings)
    assert any("'Walk'" in warning and "'Medication'" in warning for warning in warnings)


def test_detect_conflicts_ignores_tasks_on_different_dates():
    tasks = [
        Task(
            title="Today's walk",
            preferred_time=time(9, 30),
            duration_minutes=30,
            start_date=date(2026, 11, 19),
        ),
        Task(
            title="Tomorrow's walk",
            preferred_time=time(9, 30),
            duration_minutes=30,
            start_date=date(2026, 11, 20),
        ),
    ]

    assert Scheduler().detect_conflicts(tasks) == []


def test_filter_tasks_by_pet_or_completion_independently():
    biscuit_task = Task(title="Walk")
    completed_biscuit_task = Task(title="Dinner", completed=True)
    mochi_task = Task(title="Play")
    owner = Owner(
        pets=[
            Pet(name="Biscuit", tasks=[biscuit_task, completed_biscuit_task]),
            Pet(name="Mochi", tasks=[mochi_task]),
        ]
    )
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks(pet_name="BISCUIT") == [
        biscuit_task,
        completed_biscuit_task,
    ]
    assert scheduler.filter_tasks(completed=False) == [biscuit_task, mochi_task]
    assert scheduler.filter_tasks(pet_name="Unknown") == []


def test_pet_with_zero_tasks_has_an_empty_plan():
    pet = Pet(name="Biscuit")
    scheduler = Scheduler(Owner(available_minutes=30, pets=[pet]))

    plan = scheduler.generate_plan(date(2026, 11, 19))

    assert pet.tasks == []
    assert plan.scheduled_items == []
    assert plan.skipped_tasks == []
    assert plan.total_minutes_scheduled == 0


def test_empty_schedule_without_pets_has_no_conflicts():
    scheduler = Scheduler()

    plan = scheduler.generate_plan(date(2026, 11, 19))

    assert plan.scheduled_items == []
    assert plan.skipped_tasks == []
    assert plan.total_minutes_scheduled == 0
    assert scheduler.detect_conflicts() == []


def test_task_exceeding_available_minutes_is_skipped():
    task = Task(title="Long walk", duration_minutes=31)
    pet = Pet(name="Biscuit", tasks=[task])
    scheduler = Scheduler(Owner(available_minutes=30, pets=[pet]))

    plan = scheduler.generate_plan(date(2026, 11, 19))

    assert plan.scheduled_items == []
    assert plan.skipped_tasks == [(task, "Not enough available time")]
    assert plan.total_minutes_scheduled == 0
