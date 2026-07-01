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

## ✨ Features

PawPal+ implements the following scheduling algorithms and behaviors:

- **Sorting by time** — `Scheduler.sort_by_time()` returns tasks ordered chronologically by `due_date` (not by insertion order), using full `datetime` comparison so ordering stays correct across days, not just within "HH:MM" of a single day.
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags any two *active* tasks that share the exact same start time. It works on the sorted list and stops comparing as soon as the time differs, and it labels each clash as `same pet` or `different pets` so the owner can judge severity.
- **Filtering** — `Scheduler.filter_tasks(completed=..., pet_id=...)` narrows the task list by completion status and/or pet. Filters are optional and combine with AND; omitting one means "don't filter on it."
- **Daily / weekly recurrence** — completing a recurring task (`Task.mark_complete()` → `Task.next_occurrence()`, or `Scheduler.complete_task()`) auto-creates its next instance. The new due date is advanced with `timedelta` (so month/year rollover is correct, e.g. Jun 30 → Jul 1), and the new id restamps the date so repeated completions don't accumulate suffixes.
- **Completion tracking** — `Task.completed` plus `Pet.get_upcoming_tasks()` distinguish done vs. still-to-do tasks throughout the app.
- **Overdue detection** — `Task.is_overdue()` reports tasks past their due date that aren't yet completed.
- **Roll-up across pets** — `Owner.view_schedule()` gathers every task across all of an owner's pets into one list the Scheduler can plan over.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:
Today's Schedule (Tuesday, June 30, 2026)
----------------------------------------
[ ] 08:00  Rex: Morning walk
[ ] 12:00  Whiskers: Flea medication
[ ] 18:30  Rex: Dinner
```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
================================================================================= test session starts =================================================================================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\dtw31\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 14 items                                                                                                                                                                     

tests\test_pawpal.py ..............                                                                                                                                              [100%]

================================================================================= 14 passed in 0.04s ==================================================================================

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks chronologically by `due_date` |
| Filtering | `Scheduler.filter_tasks(completed=..., pet_id=...)` | Filter by completion status and/or pet |
| Conflict detection | `Scheduler.detect_conflicts(pet_names=...)` | Warns on tasks sharing the same start time |
| Recurring tasks | `Task.mark_complete()` → `Task.next_occurrence()`, `Scheduler.complete_task()` | Auto-creates the next daily/weekly instance |

## 📸 Demo Walkthrough

### The UI (`app.py`)

Launch the Streamlit app with `streamlit run app.py`. From there a user can:

- **Set the owner** — enter the owner's name.
- **Add pets** — submit a name and species; each pet is stored in `st.session_state` so it persists across Streamlit's reruns.
- **Pick a pet to plan for** — select which pet you're currently scheduling tasks for.
- **Add tasks** — give a task a title, type (feeding / walk / vet / grooming / medication), and an hour of the day.
- **Filter the view** — before generating, narrow by pet ("All pets" or one specific pet) and by status ("All", "Upcoming", "Completed").
- **Generate the schedule** — loads every task into a `Scheduler`, sorts it, applies the filters, checks for conflicts, and renders the plan.

### Example workflow

1. Enter the owner name (e.g. *Jordan*).
2. Add a pet — *Mochi*, a dog.
3. Add a couple of tasks — a `walk` at 08:00 and a `feeding` at 12:00.
4. (Optional) Add a second task at 12:00 to see conflict detection fire.
5. Choose your filters (e.g. *All pets*, *Upcoming*).
6. Click **Generate schedule** to see the sorted, conflict-checked plan in a table.

### Key Scheduler behaviors shown

- **Sorting** — tasks entered in any order come back sorted by time in the results table.
- **Conflict warnings** — two tasks at the same time surface as an amber `st.warning` (with a summary count) above the schedule; a clean plan shows an `st.success` "no conflicts" banner instead.
- **Filtering** — the pet/status dropdowns map directly to `Scheduler.filter_tasks(...)`.
- **Recurrence** — completing a daily/weekly task auto-schedules its next occurrence.

### Sample CLI output (`python main.py`)

`main.py` is a headless demo of the same logic — it seeds two pets and five tasks (added deliberately out of order, with a 12:00 clash) and prints each Scheduler behavior:

```text
Today's Schedule (Tuesday, June 30, 2026)
----------------------------------------
[x] 07:00  Whiskers: Breakfast
[ ] 08:00  Rex: Morning walk
[ ] 12:00  Whiskers: Flea medication
[ ] 12:00  Rex: Vet checkup
[ ] 18:30  Rex: Dinner

Still to do (not completed):
----------------------------------------
[ ] 08:00  Rex: Morning walk
[ ] 12:00  Whiskers: Flea medication
[ ] 12:00  Rex: Vet checkup
[ ] 18:30  Rex: Dinner

Rex's tasks only:
----------------------------------------
[ ] 08:00  Rex: Morning walk
[ ] 12:00  Rex: Vet checkup
[ ] 18:30  Rex: Dinner

Conflict check:
----------------------------------------
WARNING: conflict at 12:00 - 'Flea medication' (Whiskers) and 'Vet checkup' (Rex) [different pets]

After completing the daily 'Morning walk':
----------------------------------------
Auto-created next occurrence -> t2@20260701 due Wed 08:00
[x] 07:00  Whiskers: Breakfast
[x] 08:00  Rex: Morning walk
[ ] 12:00  Whiskers: Flea medication
[ ] 12:00  Rex: Vet checkup
[ ] 18:30  Rex: Dinner
[ ] 08:00  Rex: Morning walk
```
