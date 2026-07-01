from datetime import datetime

import streamlit as st

from pawpal_system import Owner, Pet, Task, TaskType

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
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    # Pull every task across the owner's pets and order it by time.
    schedule = sorted(owner.view_schedule(), key=lambda t: t.due_date)
    if not schedule:
        st.warning("No tasks to schedule yet. Add a task above first.")
    else:
        pet_by_id = {p.id: p.name for p in owner.pets}
        st.write(f"Today's Schedule for {owner.name}:")
        for t in schedule:
            who = pet_by_id.get(t.pet_id, t.pet_id)
            st.write(f"- **{t.due_date.strftime('%H:%M')}**  {who}: {t.title} ({t.type.value})")
