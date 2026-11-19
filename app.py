from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)

owner = st.session_state.owner

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
    st.session_state.pop("daily_plan", None)
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
        st.session_state.pop("daily_plan", None)
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
                )
            )
            st.session_state.pop("daily_plan", None)
            st.success(f"Added {task_title.strip()} for {selected_pet.name}.")

    for pet in owner.pets:
        with st.expander(f"{pet.name}'s tasks", expanded=True):
            if pet.tasks:
                st.table(
                    [
                        {
                            "Task": task.title,
                            "Category": task.category,
                            "Duration (min)": task.duration_minutes,
                            "Priority": task.priority.title(),
                        }
                        for task in pet.tasks
                    ]
                )
            else:
                st.caption("No tasks for this pet yet.")
else:
    st.info("Add a pet before adding care tasks.")

st.divider()
st.subheader("Today's schedule")
st.caption(f"Plan date: {date.today().strftime('%B %d, %Y')}")

if st.button("Generate today's schedule"):
    plan = Scheduler(owner).generate_plan(date.today())
    st.session_state.daily_plan = plan

if "daily_plan" in st.session_state:
    plan = st.session_state.daily_plan
    st.write(f"**{plan.pet_name or 'No pets added'}**")
    st.metric("Total time scheduled", f"{plan.total_minutes_scheduled} min")

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
