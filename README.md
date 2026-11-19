# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
Today's Schedule
================
Daily plan for Biscuit, Mochi on 2026-11-19:
  08:00 — Morning walk (30 min) [priority: high]
  09:30 — Play session (20 min) [priority: high]
  18:00 — Dinner (15 min) [priority: medium]
  18:25 — Medication (10 min) [priority: low]
Total scheduled: 75 minutes
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The automated test suite covers:

- Sorting tasks chronologically, including unscheduled tasks.
- Filtering tasks by pet name and completion status.
- Creating the next daily and weekly recurrence when a task is completed.
- Detecting duplicate and overlapping task times.
- Edge cases including pets with no tasks, an empty schedule, and tasks exceeding available time.

Passing verbose test run (`python -m pytest -v`):

```text
============================= test session starts ==============================
platform linux -- Python 3.14.2, pytest-9.2.0, pluggy-1.7.0 -- /home/codespace/.python/current/bin/python
cachedir: .pytest_cache
rootdir: /workspaces/ai110-module2show-pawpal-starter
plugins: platformdirs-4.14.0, anyio-4.15.1
collecting ... collected 12 items

tests/test_pawpal.py::test_task_mark_complete PASSED                     [  8%]
tests/test_pawpal.py::test_pet_add_task PASSED                           [ 16%]
tests/test_pawpal.py::test_sort_by_time_handles_time_strings_and_unscheduled_tasks PASSED [ 25%]
tests/test_pawpal.py::test_filter_tasks_by_pet_and_completion PASSED     [ 33%]
tests/test_pawpal.py::test_mark_recurring_task_complete_adds_next_occurrence_to_same_pet PASSED [ 41%]
tests/test_pawpal.py::test_mark_weekly_task_complete_advances_one_week PASSED [ 50%]
tests/test_pawpal.py::test_detect_conflicts_reports_same_start_and_overlapping_slots PASSED [ 58%]
tests/test_pawpal.py::test_detect_conflicts_ignores_tasks_on_different_dates PASSED [ 66%]
tests/test_pawpal.py::test_filter_tasks_by_pet_or_completion_independently PASSED [ 75%]
tests/test_pawpal.py::test_pet_with_zero_tasks_has_an_empty_plan PASSED  [ 83%]
tests/test_pawpal.py::test_empty_schedule_without_pets_has_no_conflicts PASSED [ 91%]
tests/test_pawpal.py::test_task_exceeding_available_minutes_is_skipped PASSED [100%]

============================== 12 passed in 0.03s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐⭐ 5/5 stars — The suite verifies the key scheduling behaviors and edge cases, and all 12 tests passed.
```

## ✨ Features

- **Sorting by time:** `Scheduler.sort_by_time()` displays preferred-time tasks chronologically and places unscheduled tasks last.
- **Filtering by pet and status:** `Scheduler.filter_tasks()` supports filtering by pet name and completion state (all, pending, or completed).
- **Conflict warnings:** `Scheduler.detect_conflicts()` detects duplicate or overlapping preferred-time slots and shows the affected task names with a suggested action. It leaves changes to the pet owner.
- **Automated daily and weekly recurrence:** `Scheduler.mark_task_complete()` creates the next incomplete daily or weekly occurrence when its recurring task is completed.
- **Time-budget scheduling:** `Scheduler.generate_plan()` considers due tasks, priority, preferred time, available minutes, an optional buffer, and the 08:00–20:00 planning window. It reports scheduled time and explains skipped tasks.

## 🐾 Demo Walkthrough

1. Save the owner's name and available minutes, then add a pet.
2. Add care tasks with a category, duration, priority, start date, recurrence, and optional preferred time.
3. Generate today's schedule. Review the time-budgeted plan, total scheduled minutes, explanations, and skipped tasks. The task list is sorted by preferred time; overlapping preferences appear as warnings that identify the tasks and suggest adjusting a time or duration.
4. Mark a recurring task complete. PawPal+ confirms completion and displays the date of the automatically created next occurrence.
5. Use the pet and status filters to review all, pending, or completed tasks. For a terminal demonstration of sorting, filtering, recurrence, and conflict detection, run `python main.py`.

Sample CLI output from `python main.py`:

```text
Today's Schedule
================
Daily plan for Biscuit, Mochi on 2026-11-19:
  08:00 — Morning walk (30 min) [priority: high]
  09:30 — Play session (20 min) [priority: high]
  10:00 — Training (15 min) [priority: medium]
  18:00 — Dinner (15 min) [priority: medium]
  18:25 — Medication (10 min) [priority: low]
Total scheduled: 90 minutes

Tasks sorted by preferred time
  08:00 — Morning walk
  09:30 — Training
  09:30 — Play session
  12:00 — Medication
  18:00 — Dinner

Uncompleted tasks for Biscuit
  Dinner
  Morning walk
  Training

Completed Dinner; next occurrence: 2026-11-20

Conflict warnings
  Conflict: 'Training' (09:30:00) and 'Play session' (09:30:00) have overlapping time slots.
```

The final class diagram is available in [`diagrams/uml_final.mmd`](./diagrams/uml_final.mmd).
