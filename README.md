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

- Sorting tasks chronologically and by priority/time, including unscheduled tasks.
- Filtering tasks by pet name and completion status.
- Creating the next daily and weekly recurrence when a task is completed.
- Detecting duplicate and overlapping task times.
- Edge cases including pets with no tasks, an empty schedule, and tasks exceeding available time.
- Finding the next available slot, including gaps, full days, and custom planning windows.
- JSON persistence round trips for owners, pets, tasks, and temporal values.

Passing verbose test run (`python -m pytest -v`):

```text
============================= test session starts ==============================
platform linux -- Python 3.14.2, pytest-9.2.0, pluggy-1.7.0 -- /home/codespace/.python/current/bin/python
cachedir: .pytest_cache
rootdir: /workspaces/ai110-module2show-pawpal-starter
plugins: platformdirs-4.14.0, anyio-4.15.1
collecting ... collected 17 items

tests/test_pawpal.py::test_task_mark_complete PASSED                     [  5%]
tests/test_pawpal.py::test_pet_add_task PASSED                           [ 11%]
tests/test_pawpal.py::test_sort_by_time_handles_time_strings_and_unscheduled_tasks PASSED [ 17%]
tests/test_pawpal.py::test_sort_by_priority_and_time_prioritizes_high_tasks_before_earlier_tasks PASSED [ 23%]
tests/test_pawpal.py::test_filter_tasks_by_pet_and_completion PASSED     [ 29%]
tests/test_pawpal.py::test_mark_recurring_task_complete_adds_next_occurrence_to_same_pet PASSED [ 35%]
tests/test_pawpal.py::test_mark_weekly_task_complete_advances_one_week PASSED [ 41%]
tests/test_pawpal.py::test_detect_conflicts_reports_same_start_and_overlapping_slots PASSED [ 47%]
tests/test_pawpal.py::test_detect_conflicts_ignores_tasks_on_different_dates PASSED [ 52%]
tests/test_pawpal.py::test_filter_tasks_by_pet_or_completion_independently PASSED [ 58%]
tests/test_pawpal.py::test_pet_with_zero_tasks_has_an_empty_plan PASSED  [ 64%]
tests/test_pawpal.py::test_empty_schedule_without_pets_has_no_conflicts PASSED [ 70%]
tests/test_pawpal.py::test_task_exceeding_available_minutes_is_skipped PASSED [ 76%]
tests/test_pawpal.py::test_find_next_available_slot_returns_gap_between_scheduled_tasks PASSED [ 82%]
tests/test_pawpal.py::test_find_next_available_slot_returns_none_when_day_is_full PASSED [ 88%]
tests/test_pawpal.py::test_find_next_available_slot_starts_at_configured_day_start PASSED [ 94%]
tests/test_pawpal.py::test_owner_json_round_trip_preserves_pet_tasks_and_temporal_values PASSED [100%]

============================== 17 passed in 0.09s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐⭐ 5/5 stars — The suite verifies the key scheduling behaviors and edge cases, and all 12 tests passed.
```

## ✨ Features

- **Sorting by time:** `Scheduler.sort_by_time()` displays preferred-time tasks chronologically and places unscheduled tasks last.
- **Filtering by pet and status:** `Scheduler.filter_tasks()` supports filtering by pet name and completion state (all, pending, or completed).
- **Conflict warnings:** `Scheduler.detect_conflicts()` detects duplicate or overlapping preferred-time slots and shows the affected task names with a suggested action. It leaves changes to the pet owner.
- **Automated daily and weekly recurrence:** `Scheduler.mark_task_complete()` creates the next incomplete daily or weekly occurrence when its recurring task is completed.
- **Time-budget scheduling:** `Scheduler.generate_plan()` considers due tasks, priority, preferred time, available minutes, an optional buffer, and the 08:00–20:00 planning window. It reports scheduled time and explains skipped tasks.
- **Next available slot:** `Scheduler.find_next_available_slot()` finds the earliest slot for a requested duration while respecting existing scheduled items, the planning window, and the configured buffer.
- **JSON persistence:** Owner, pet, and task information is loaded from and saved to `data.json`.

### Priority-Based Scheduling

`Scheduler.sort_by_priority_and_time()` orders tasks High → Medium → Low, then by preferred time within each priority; unscheduled tasks appear last within their priority. The generated plan follows this priority-first ordering while respecting preferred times, the available-minute budget, and the planning window.

The CLI displays the generated schedule as a priority-ordered table. Run `python main.py` to see the current output:

```text
Today's Schedule — 2026-11-19
╒═════════════╤═════════╤══════════════╤════════════════════════╤════════════╤════════════╕
│ Time        │ Pet     │ Task         │ Category               │ Priority   │ Status     │
╞═════════════╪═════════╪══════════════╪════════════════════════╪════════════╪════════════╡
│ 08:00–08:30 │ Biscuit │ Morning walk │ 🐕 Walk / Exercise     │ High       │ ⏳ Pending │
├─────────────┼─────────┼──────────────┼────────────────────────┼────────────┼────────────┤
│ 09:30–09:50 │ Mochi   │ Play session │ 🎾 Enrichment          │ High       │ ⏳ Pending │
├─────────────┼─────────┼──────────────┼────────────────────────┼────────────┼────────────┤
│ 10:00–10:15 │ Biscuit │ Training     │ 🎾 Enrichment          │ Medium     │ ⏳ Pending │
├─────────────┼─────────┼──────────────┼────────────────────────┼────────────┼────────────┤
│ 18:00–18:15 │ Biscuit │ Dinner       │ 🍽️ Feeding             │ Medium     │ ⏳ Pending │
├─────────────┼─────────┼──────────────┼────────────────────────┼────────────┼────────────┤
│ 18:25–18:35 │ Mochi   │ Medication   │ 💊 Medication / Health │ Low        │ ⏳ Pending │
╘═════════════╧═════════╧══════════════╧════════════════════════╧════════════╧════════════╛
Total scheduled: 90 minutes
```

### UI & Output Formatting

- Task categories use `🐕` for walks/exercise, `🍽️` for feeding, `💊` for medication/health, `🧼` for grooming, and `🎾` for enrichment; other categories use `🐾`.
- Status labels use `✅ Completed` and `⏳ Pending`. Schedule conflicts are marked with `⚠️ Conflict`.
- The Streamlit UI includes these labels in task and schedule tables and displays conflicts as prominent warnings.
- The CLI uses `tabulate.tabulate(..., tablefmt="fancy_grid")` to render structured schedule and task tables.

## 💾 Data Persistence

When the Streamlit app starts, it loads `data.json` from the project working directory if the file exists; otherwise it starts with the default owner. The app saves the owner, pets, and tasks after owner details are saved, a pet or task is added, or a task is marked complete. Daily plans are generated from the saved care data and are not persisted.

The JSON conversion preserves task dates and preferred times, supports tagged `date`, `time`, and `datetime` values in nested data, and stores `Enum` values using their underlying value. The file is created automatically the first time data is saved. It contains personal pet-care information, so keep it local and do not commit it.

Persistence changes involve:

- `pawpal_system.py` — model `to_dict()`/`from_dict()` conversion and `Owner.save_to_json()`/`load_from_json()`.
- `app.py` — load existing data at startup and save after owner, pet, and task changes.
- `tests/test_pawpal.py` — round-trip coverage using pytest's temporary-path fixture.
- `.gitignore` — excludes the local `data.json` file from Git.
- `README.md` — persistence workflow and file documentation.

## 🐾 Demo Walkthrough

1. Save the owner's name and available minutes, then add a pet.
2. Add care tasks with a category, duration, priority, start date, recurrence, and optional preferred time.
3. Generate today's schedule. Review the time-budgeted plan, total scheduled minutes, explanations, and skipped tasks. The task list is sorted by preferred time; overlapping preferences appear as warnings that identify the tasks and suggest adjusting a time or duration.
4. Mark a recurring task complete. PawPal+ confirms completion and displays the date of the automatically created next occurrence.
5. Use the pet and status filters to review all, pending, or completed tasks. For a terminal demonstration of priority scheduling, category icons, statuses, recurrence, and conflict detection, run `python main.py` and see the table under **Priority-Based Scheduling** above.

The final class diagram is available in [`diagrams/uml_final.mmd`](./diagrams/uml_final.mmd).
