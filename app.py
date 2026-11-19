from datetime import date, time
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    data_file = Path("data.json")
    st.session_state.owner = (
        Owner.load_from_json(data_file)
        if data_file.is_file()
        else Owner(name="Jordan", available_minutes=120)
    )

owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title("🐾 PawPal+")
st.markdown("Plan your pets' care tasks around your available time.")

st.subheader("Owner details")
with st.form("owner_details"):
    owner_name = st.text_input("Owner name", value=owner.name)
    available_minutes = st.number_input(
        "Available minutes today",
        min_value=0,
        max_value=1440,
        value=int(owner.available_minutes),
    )
    owner_submitted = st.form_submit_button("Save owner details")

if owner_submitted:
    owner.name = owner_name.strip()
    owner.update_availability(int(available_minutes))
    owner.save_to_json()
    st.session_state.pop("daily_plan", None)
    st.session_state.pop("conflict_warnings", None)
    st.success("Owner details saved.")

st.divider()
st.subheader("Pets")

with st.form("add_pet"):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)")
    age = st.number_input("Age in years", min_value=0, max_value=100, value=0)
    pet_submitted = st.form_submit_button("Add pet")

if pet_submitted:
    if not pet_name.strip():
        st.error("Enter a name for your pet.")
    else:
        owner.add_pet(
            Pet(
                name=pet_name.strip(),
                species=species,
                breed=breed.strip(),
                age=int(age),
            )
        )
        owner.save_to_json()
        st.session_state.pop("daily_plan", None)
        st.session_state.pop("conflict_warnings", None)
        st.success(f"Added {pet_name.strip()}.")

if owner.pets:
    st.write(
        ", ".join(
            f"{pet.name} ({pet.species})" for pet in owner.pets
        )
    )
else:
    st.info("No pets yet. Add a pet to start building a care plan.")

st.divider()
st.subheader("Care tasks")

if owner.pets:
    pet_index = st.selectbox(
        "Add a task for",
        options=range(len(owner.pets)),
        format_func=lambda index: (
            f"{owner.pets[index].name} ({owner.pets[index].species})"
        ),
    )
    selected_pet = owner.pets[pet_index]

    with st.form("add_task"):
        task_title = st.text_input("Task title")
        category = st.selectbox(
            "Category",
            ["feeding", "exercise", "health", "enrichment", "grooming", "other"],
        )
        duration_minutes = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        recurrence = st.selectbox("Recurrence", ["once", "daily", "weekly"])
        start_date = st.date_input("Start date", value=date.today())
        preferred_time_value = st.time_input(
            "Preferred time (optional)", value=time(8, 0)
        )
        has_preferred_time = st.checkbox("Use this preferred time")
        task_submitted = st.form_submit_button("Add task")

    if task_submitted:
        if not task_title.strip():
            st.error("Enter a title for the task.")
        else:
            selected_pet.add_task(
                Task(
                    title=task_title.strip(),
                    category=category,
                    duration_minutes=int(duration_minutes),
                    priority=priority,
                    preferred_time=(
                        preferred_time_value if has_preferred_time else None
                    ),
                    recurrence=recurrence,
                    start_date=start_date,
                )
            )
            owner.save_to_json()
            st.session_state.pop("daily_plan", None)
            st.session_state.pop("conflict_warnings", None)
            st.success(f"Added {task_title.strip()} for {selected_pet.name}.")

    st.markdown("**Task list**")
    pet_filter = st.selectbox(
        "Filter by pet",
        ["All pets", *[pet.name for pet in owner.pets]],
    )
    completion_filter = st.selectbox(
        "Filter by status", ["All", "Pending", "Completed"]
    )
    completed_filter = {
        "All": None,
        "Pending": False,
        "Completed": True,
    }[completion_filter]
    visible_tasks = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed=completed_filter,
    )
    task_pet_names = {
        task.task_id: pet.name for pet in owner.pets for task in pet.tasks
    }

    if visible_tasks:
        st.table(
            [
                {
                    "Pet": task_pet_names[task.task_id],
                    "Task": task.title,
                    "Category": task.category,
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority.title(),
                    "Preferred time": (
                        task.preferred_time.strftime("%H:%M")
                        if isinstance(task.preferred_time, time)
                        else task.preferred_time or "Unscheduled"
                    ),
                    "Recurrence": task.recurrence.title(),
                    "Status": "Completed" if task.completed else "Pending",
                }
                for task in scheduler.sort_by_time(visible_tasks)
            ]
        )
    else:
        st.info("No tasks match those filters.")

    incomplete_tasks = scheduler.filter_tasks(completed=False)
    if incomplete_tasks:
        st.markdown("**Update task status**")
        task_by_id = {task.task_id: task for task in incomplete_tasks}
        with st.form("complete_task"):
            task_id = st.selectbox(
                "Mark a task complete",
                options=list(task_by_id),
                format_func=lambda task_id: (
                    f"{task_pet_names[task_id]} — {task_by_id[task_id].title}"
                ),
            )
            complete_submitted = st.form_submit_button("Complete task")

        if complete_submitted:
            completed_task = task_by_id[task_id]
            next_task = scheduler.mark_task_complete(completed_task)
            owner.save_to_json()
            st.session_state.pop("daily_plan", None)
            st.session_state.pop("conflict_warnings", None)
            if next_task is not None:
                st.success(
                    f"Completed {completed_task.title}. Its next occurrence is "
                    f"{next_task.start_date.isoformat()}."
                )
            else:
                st.success(f"Completed {completed_task.title}.")
else:
    st.info("Add a pet before adding care tasks.")

st.divider()
st.subheader("Today's schedule")
st.caption(f"Plan date: {date.today().strftime('%B %d, %Y')}")

with st.form("find_next_available_slot"):
    slot_duration = st.number_input(
        "Find an available slot for (minutes)",
        min_value=1,
        max_value=720,
        value=30,
    )
    find_slot_submitted = st.form_submit_button("Find Next Available Slot")

if find_slot_submitted:
    available_slot = scheduler.find_next_available_slot(
        date.today(), int(slot_duration)
    )
    if available_slot is None:
        st.warning("No available slot fits that duration today.")
    else:
        st.success(
            f"Next available {int(slot_duration)}-minute slot starts at "
            f"{available_slot.strftime('%H:%M')}."
        )

if st.button("Generate today's schedule"):
    target_date = date.today()
    due_tasks = scheduler.filter_due_tasks(owner.get_all_tasks(), target_date)
    st.session_state.conflict_warnings = scheduler.detect_conflicts(due_tasks)
    plan = scheduler.generate_plan(target_date)
    st.session_state.daily_plan = plan

if "daily_plan" in st.session_state:
    plan = st.session_state.daily_plan
    st.write(f"**{plan.pet_name or 'No pets added'}**")
    st.metric("Total time scheduled", f"{plan.total_minutes_scheduled} min")

    if st.session_state.get("conflict_warnings"):
        st.markdown("**Preferred-time conflicts**")
        st.caption(
            "These preferred times overlap. Adjust a task's preferred time or "
            "duration; PawPal+ does not change your preferences automatically."
        )
        for warning in st.session_state.conflict_warnings:
            st.warning(warning)

    if plan.scheduled_items:
        st.markdown("**Scheduled tasks**")
        st.table(
            [
                {
                    "Time": (
                        f"{item.start_time.strftime('%H:%M')}–"
                        f"{item.end_time.strftime('%H:%M')}"
                    ),
                    "Task": item.task.title,
                    "Duration (min)": int(
                        (item.end_time - item.start_time).total_seconds() // 60
                    ),
                    "Priority": item.task.priority.title(),
                    "Reasoning": item.reason,
                }
                for item in plan.scheduled_items
            ]
        )
    else:
        st.info("No tasks were scheduled for today.")

    if plan.skipped_tasks:
        st.markdown("**Skipped tasks**")
        st.table(
            [
                {"Task": task.title, "Reason": reason}
                for task, reason in plan.skipped_tasks
            ]
        )
