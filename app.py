from datetime import datetime

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# Streamlit reruns this whole script on every interaction, so only build the
# Owner the FIRST time — check the session_state "vault" before creating.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(id="o1", name=owner_name, email="", phone="")
owner = st.session_state.owner
owner.name = owner_name

st.markdown("### Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name", value="Mochi")
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and new_pet_name:
        # Owner.add_pet is the method that handles the submitted data.
        new_pet = Pet(
            id=f"p{len(owner.pets) + 1}",
            name=new_pet_name,
            species=new_species,
            breed="",
            age=0,
            owner_id=owner.id,
        )
        owner.add_pet(new_pet)
        st.success(f"Added {new_pet.name} to {owner.name}'s pets.")

if not owner.pets:
    st.info("No pets yet. Add one above to start scheduling tasks.")
    st.stop()

# Pick the pet we're currently scheduling for.
pet_names = [p.name for p in owner.pets]
selected_name = st.selectbox("Scheduling for", pet_names)
pet = next(p for p in owner.pets if p.name == selected_name)

st.markdown("### Tasks")
st.caption("Added tasks are stored on your Pet inside st.session_state, so they persist across reruns.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_type = st.selectbox("Type", [t.value for t in TaskType])
with col3:
    task_hour = st.number_input("Hour (0-23)", min_value=0, max_value=23, value=8)

if st.button("Add task"):
    due = datetime.now().replace(hour=int(task_hour), minute=0, second=0, microsecond=0)
    task = Task(
        id=f"t{len(pet.tasks) + 1}",
        title=task_title,
        description="",
        type=TaskType(task_type),
        due_date=due,
        pet_id=pet.id,
    )
    pet.add_task(task)

if pet.tasks:
    st.write(f"Current tasks for {pet.name}:")
    st.table(
        [
            {
                "time": t.due_date.strftime("%H:%M"),
                "title": t.title,
                "type": t.type.value,
                "done": "✓" if t.completed else "",
            }
            for t in pet.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Sorted, conflict-checked, and filterable — powered by the Scheduler class.")

# Let the owner narrow the view before generating the plan.
fcol1, fcol2 = st.columns(2)
with fcol1:
    pet_filter = st.selectbox(
        "Show tasks for", ["All pets"] + [p.name for p in owner.pets]
    )
with fcol2:
    status_filter = st.selectbox("Status", ["All", "Upcoming", "Completed"])

if st.button("Generate schedule"):
    # Load every task across the owner's pets into a Scheduler, then let the
    # Scheduler do the sorting, filtering, and conflict detection.
    scheduler = Scheduler()
    for t in owner.view_schedule():
        scheduler.schedule_task(t)

    pet_by_id = {p.id: p.name for p in owner.pets}

    # Translate the UI filters into Scheduler.filter_tasks arguments.
    filter_kwargs: dict = {}
    if pet_filter != "All pets":
        filter_kwargs["pet_id"] = next(p.id for p in owner.pets if p.name == pet_filter)
    if status_filter == "Upcoming":
        filter_kwargs["completed"] = False
    elif status_filter == "Completed":
        filter_kwargs["completed"] = True

    allowed_ids = {t.id for t in scheduler.filter_tasks(**filter_kwargs)}
    # Keep Scheduler's chronological order, but only the tasks that pass filters.
    schedule = [t for t in scheduler.sort_by_time() if t.id in allowed_ids]

    if not schedule:
        st.warning("No tasks match this view. Add a task or widen the filters above.")
    else:
        # Surface conflicts first — they're the most important thing for the
        # owner to see and act on.
        conflicts = scheduler.detect_conflicts(pet_names=pet_by_id)
        if conflicts:
            st.warning(
                f"⚠️ {len(conflicts)} scheduling conflict"
                f"{'s' if len(conflicts) > 1 else ''} found — "
                "two tasks want the same time slot. Consider rescheduling one:"
            )
            for c in conflicts:
                # Strip the "WARNING: " prefix; Streamlit's icon already signals it.
                st.warning(c.replace("WARNING: ", ""), icon="⏰")
        else:
            st.success("✅ No scheduling conflicts — this plan is clear to go!")

        st.write(f"#### Today's Schedule for {owner.name}")
        st.table(
            [
                {
                    "Time": t.due_date.strftime("%H:%M"),
                    "Pet": pet_by_id.get(t.pet_id, t.pet_id),
                    "Task": t.title,
                    "Type": t.type.value,
                    "Status": "✓ done" if t.completed else "upcoming",
                }
                for t in schedule
            ]
        )
