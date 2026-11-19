"""Unit tests for PawPal+ task and pet behavior."""

from pawpal_system import Pet, Task


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
