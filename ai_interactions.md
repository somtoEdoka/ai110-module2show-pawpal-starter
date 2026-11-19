# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Add a `Scheduler.find_next_available_slot(target_date, duration_minutes)` algorithm that finds the earliest available window within the configured day, respecting scheduled tasks and the buffer. Add a Streamlit helper, focused tests for an available gap and a full day, and document the workflow here.

**What did the agent do?**

Modified `pawpal_system.py`, `app.py`, `tests/test_pawpal.py`, and this `ai_interactions.md` file. The scheduler searches the generated daily plan from `day_start`, checks gaps in chronological order, applies the configured buffer around the candidate slot, and returns `None` when the requested duration does not fit. The UI accepts a requested duration and reports the next start time or that no slot fits. Tests cover a gap between scheduled tasks, a full day, and a custom planning-window start.

**What did you have to verify or fix manually?**

I reviewed the buffer rule to ensure the candidate slot leaves the configured separation from existing tasks both before and after the slot. I also checked that the custom day-start case and a fully occupied day produce the expected results. No test failures or post-test code corrections were needed.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

### Weekly Recurrence Rescheduling: Gemini vs. GitHub Copilot

> Transparency: GitHub Copilot was used to build and review this project. Gemini was not available in this workflow, so no Gemini response is invented; its column records the comparison prompt and the fact that its output could not be assessed.

| Category | Gemini | GitHub Copilot |
|----------|--------|----------------|
| **Model / tool used** | Gemini (not queried for this project; no response collected). | GitHub Copilot in VS Code, used while implementing and reviewing the scheduler. |
| **Prompt / task** | Comparison prompt drafted, but not sent: “Design weekly recurring task rescheduling using `recurrence_days`, an interval, and `timedelta`. Support multiple selected weekdays, explain how completion creates the next occurrence, and suggest focused tests.” | Project task: implement and verify due-date handling for weekly tasks and create the next occurrence when a task is completed. |
| **Response summary** | No Gemini response was collected, so there is no model output to summarize. | `Task.is_due_today()` checks allowed weekdays and the week interval. `Scheduler.mark_task_complete()` creates the next weekly occurrence using `timedelta(days=7)` and carries forward recurrence metadata. |
| **What was useful** | Not assessed without an actual response. Running the same prompt through Gemini would be useful as an independent design review. | The implementation supports multiple `recurrence_days`, keeps due-date checks in `Task`, and keeps next-occurrence creation in `Scheduler`. |
| **What was flawed / tradeoffs** | No response to evaluate; this is not a measured model-to-model comparison. | Advancing by a fixed seven days is simple and predictable. The weekday/interval rules should remain covered by tests, especially when multiple weekdays are selected. |
| **Final decision** | No Gemini recommendation was used. | Keep the current implementation: it balances readable weekday and interval checks with multi-day weekly support, and uses `timedelta(days=7)` for the next weekly occurrence. |

**Final implementation choice:** retain the Copilot-assisted design in `Task.is_due_today()` and `Scheduler.mark_task_complete()`. This keeps recurrence eligibility separate from occurrence creation and preserves the selected weekdays and interval when advancing the task.
