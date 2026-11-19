# PawPal+ Project Reflection

## 1. System Design
    Three core tasks include: add a pet, schedule a walk, see today's tasks
**1a. Initial design**

The initial design separates pet and owner data from task details and scheduling. `Owner` keeps the owner's availability, preferences, and pets; `Pet` stores pet information and its tasks; `Task` represents a care activity and its scheduling attributes. `ScheduledItem` represents a task placed in a time slot, `DailyPlan` collects scheduled and skipped tasks for a pet and date, and `Scheduler` generates plans and explains scheduling decisions.

**1b. Design changes**

The AI review highlighted three gaps, so the skeleton was refined before implementing scheduling logic:

- Added a generated `task_id` so tasks can be identified reliably for tracking and removal.
- Added `start_date`, `recurrence_interval`, and `recurrence_days` so daily, weekly, and custom recurrence rules have enough metadata to determine due dates.
- Changed scheduled item boundaries to `datetime` and added an 8:00–20:00 scheduler window. These provide an unambiguous date-and-time basis for duration, buffer, overnight, and overlap checks, while making the planning window explicit.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
