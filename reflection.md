# PawPal+ Project Reflection

## 1. System Design

Three core user tasks are adding a pet, scheduling its care, and reviewing today's plan.

**1a. Initial design**

The design separates pet and owner information from care-task details and scheduling. `Owner` keeps the owner's availability, preferences, and pets. Each `Pet` owns a list of `Task` objects. `Scheduler` reads the owner and task data, applies scheduling rules, and creates a `DailyPlan` containing `ScheduledItem` objects and skipped-task explanations. A scheduled item points back to its task, so the plan can show the task's title, priority, and reasoning.

**1b. Design changes**

Reviewing the initial model against the desired scheduling behavior exposed a few missing details:

- Added a generated `task_id` so each task can be identified, for example when removing it from a pet's task list.
- Added `start_date`, `recurrence_interval`, and `recurrence_days` to support due-date checks for one-time, daily, and weekly tasks, including interval and weekday metadata.
- Made scheduled item boundaries `datetime` values so durations and overlap checks use a date and time together. The scheduler uses a configurable planning window, defaulting to 08:00–20:00, and a configurable buffer between scheduled items.
- Added scheduler methods for chronological display sorting, pet/status filtering, due-task filtering, completion with next-occurrence creation, and preferred-time conflict warnings. The final diagram reflects these methods and their relationships.

## 2. Scheduling Logic and Tradeoffs

**2a. Constraints and priorities**

The scheduler first filters out completed tasks and tasks that are not due on the target date. It then orders due tasks by priority (high, medium, then low), preferred time, and title. It schedules tasks within the owner's available-minute budget and the configured 08:00–20:00 window, honoring a preferred time when it is later than the current schedule cursor and adding the configured buffer after each scheduled task. Tasks that cannot fit are returned with a reason rather than silently discarded.

Priority and the time budget were chosen because they make a daily plan useful under limited availability. Preferred times and the planning window make it practical to follow, while skipped-task explanations help the owner understand which constraints prevented a task from being scheduled. `sort_by_time()` is a separate chronological view for reviewing tasks; it does not replace the priority-based ordering used to generate a plan.

**2b. Tradeoffs**

- `Scheduler.detect_conflicts()` reports duplicate or overlapping preferred-time slots as warnings rather than automatically changing a task's time. This keeps the owner in control; the UI names the affected tasks and suggests adjusting a time or duration. The conflict check compares preferred times and, when both tasks have start dates, ignores tasks on different dates.
- The generated plan follows priority order, while the task-list view uses chronological preferred-time order. Keeping these as separate behaviors supports both priority-aware scheduling and an easy-to-scan task list.
- The sorting key is written across multiple lines instead of compressing its fallback and ordering logic into a dense expression. This favors readability; one small inefficiency is that `_time_to_minutes()` is evaluated twice for each task.
- Daily and weekly completion creates the next occurrence one or seven days after the task's `start_date` (or today's date if no start date is set). The recurrence interval and weekday metadata are copied forward, while the next task starts incomplete.

## 3. AI Collaboration

**a. AI strategy**

The most useful assistant features were reviewing the UML against the implemented classes, identifying gaps such as task identifiers and recurrence metadata, generating focused pytest coverage, and making coordinated updates to the Streamlit UI and project documentation. Asking for checks against concrete behaviors—such as the next recurrence date, tasks with no preferred time, and conflicts—was more useful than asking for broad changes without acceptance criteria.

Separate chat sessions for the project phases helped keep design, implementation/testing, UI work, and final documentation focused. Each phase had a clear deliverable to carry forward, such as the final scheduler API, passing test results, or the CLI output, instead of mixing every concern into one long thread.

**b. Judgment and verification**

One design choice I kept deliberately simple was conflict handling. The system can identify overlapping preferred times and has a `resolve_conflict()` helper, but the normal planning flow does not silently move or remove tasks; it reports warnings and lets the owner decide what to change. This preserves owner control and avoids presenting an automatic choice as if it were the owner's preference.

I checked assistant-generated changes against the actual class methods and requirements, ran the tests after adding coverage, and ran `python main.py` to verify the documented CLI example. The UML and README were also checked against the final implementation rather than treated as independent descriptions.

## 4. Testing and Verification

**a. What I tested**

The 12 pytest tests cover basic task and pet behavior; chronological sorting with both `time` objects and strings, including unscheduled tasks; filtering by pet and completion state; daily and weekly recurrence; duplicate and overlapping preferred times; ignoring conflicts on different dates; empty pets and schedules; and tasks that exceed the available-minute budget. These cases check both expected behavior and important boundary conditions so changes to the scheduler are less likely to break its core contract.

**b. Confidence**

I am highly confident in the tested core scheduling logic: the full `python -m pytest -v` run passed all 12 tests. I would not claim complete coverage, because the suite does not automate interactive Streamlit workflows. With more time, I would add UI-level tests and additional cases for recurrence intervals and weekday selections, exact planning-window boundaries, invalid task data, and multiple pets with similar names.

## 5. Reflection

**a. What went well**

The strongest result is that the scheduling behavior is visible in both the CLI and Streamlit UI. Users can inspect a time-sorted and filtered task list, generate a plan with explanations and skipped tasks, see conflicts, and complete recurring tasks to create their next occurrence.

**b. What I would improve**

I would add task editing and deletion controls to the UI, plus automated tests for the Streamlit interactions. I would also consider making the generated plan's priority and preferred-time tradeoff configurable, then add tests that clearly define the expected behavior before changing the algorithm.

**c. Key takeaway**

Being the lead architect means defining the behavior and tradeoffs, checking that the design matches the code, and verifying AI-generated work rather than accepting it on appearance alone. The assistant can accelerate implementation and test-writing, but the human still needs to decide what the system should do when constraints conflict and ensure that users can understand those decisions.
