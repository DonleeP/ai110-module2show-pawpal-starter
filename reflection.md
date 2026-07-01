# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design includes Owner, Pet, Scheduler, and Task. Owner owns Pet relationship, Pet has Task relationship, and Scheduler manages Task relationship. Owner has an id,name,email,phone, and pets... Pet has id,name,species,breed,age,ownerId, and tasks... Scheduler has tasks... and Task has id,title,description,type,dueDate,recurring,completed,petId.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

No, my design didnt change during implementation

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

--- detect_conflicts() only flags tasks that share the exact same start time, not overlapping durations.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI all throughout the process of this project, mainly when the assignment mentioned talking to the AI agent and making the changes the AI offered if they were good. I made sure to use "Ask before edits".
- What kinds of prompts or questions were most helpful?
The most helpful questions were like "Based on my skeletons in pawpal_system.py, how should the Scheduler retrieve all tasks from the Owner's pets?"

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One moment I didn't accept a change AI suggested was when it wanted to go deeper and make the option for the conflict scheduler would look deeper than just if two things started at the same time.
- How did you evaluate or verify what the AI suggested?
Looking at the code before granting it access to make changes. And if I wasn't sure I would decline.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested behaviors like Sorting Correctness, Recurrence Logic, and Conflict Detection.

**b. Confidence**

- How confident are you that your scheduler works correctly?
4- pretty confident
- What edge cases would you test next if you had more time?
nulls? I don't know
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
adding pets to owners

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
conflicting tasks

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Taking advantage of AI to make test cases.
