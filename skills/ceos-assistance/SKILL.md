---
name: ceos-assistance
description: Use when managing daily operational delegation through The Stack and structured leader-assistant standups
file-access: [data/assistance/, templates/assistance-stack.md, templates/assistance-daily.md, data/accountability.md, data/delegate/]
tools-used: [Read, Write, Glob]
---

# ceos-assistance

Manage the daily operational delegation workflow between a leader and their assistant using "The Stack" — a batch delegation queue. This skill implements the 5 disciplines of The Assistance Track: batching, The Stack, the daily meeting, the assistant's judgment, and a weekly review. It complements `ceos-delegate`, which handles *strategic* delegation (what SHOULD be delegated), by managing *operational* delegation (HOW items are delegated day-to-day).

**Not for:** Strategic delegation decisions (use `ceos-delegate`), task tracking without a leader-assistant relationship (use `ceos-todos`), or meeting facilitation (use `ceos-l10`). The Assistance Track is specifically about the daily delegation workflow between a leader and their dedicated assistant.

## When to Use

- "Add to the stack" or "stack this for my assistant"
- "Run the daily meeting" or "daily standup with my assistant"
- "Review the stack" or "what's on the stack?"
- "Weekly assistance review" or "how's delegation going this week?"
- "Show stuck items" or "what's been on the stack too long?"
- "Hand off [item] to [assistant]" or "mark [item] as done"
- Any discussion about daily delegation queues, assistant standups, or The Assistance Track

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/assistance/stack/` | Stack items — one file per delegation item |
| `data/assistance/daily/` | Daily meeting logs — one file per meeting |
| `templates/assistance-stack.md` | Template for new stack items |
| `templates/assistance-daily.md` | Template for daily meeting logs |
| `data/accountability.md` | Source of leader-assistant relationships (read-only — use ceos-accountability to modify) |
| `data/delegate/` | Delegate and Elevate audits (read-only — reference for delegation context) |

### Stack Item Format

Each stack item is a markdown file at `data/assistance/stack/stack-NNN-slug.md` with YAML frontmatter:

```yaml
id: "stack-001"
title: "Schedule board meeting"
from: "Brad Feld"
to: "Sarah Chen"
urgency: this_week        # today | this_week | whenever
status: pending           # pending | handed_off | done
created: "2026-02-16"
handed_off: null           # Date when handed to assistant
completed: null            # Date when marked done
```

**File naming:** `stack-NNN-slug.md` — zero-padded numeric ID, title slugified.

### Daily Meeting Log Format

Each daily meeting is a markdown file at `data/assistance/daily/YYYY-MM-DD.md` with YAML frontmatter:

```yaml
date: "2026-02-16"
leader: "Brad Feld"
assistant: "Sarah Chen"
items_reviewed: 5
items_handed_off: 3
items_completed: 1
duration_minutes: 15
```

### Urgency Values

| Value | Meaning | Expected Turnaround |
|-------|---------|-------------------|
| `today` | Needs attention today | Same day |
| `this_week` | Should be completed this week | Within the week |
| `whenever` | No time pressure, do when convenient | Best effort |

### Status Values

| Value | Meaning | When Set |
|-------|---------|----------|
| `pending` | On the stack, not yet handed off | Item creation |
| `handed_off` | Discussed in daily meeting, assistant is working on it | During Daily mode |
| `done` | Completed | During Daily or Stack mode |

### The 5 Disciplines

The Assistance Track is built on 5 disciplines that make delegation work:

1. **Batching** — Don't interrupt your assistant throughout the day. Collect items on The Stack.
2. **The Stack** — A single queue of everything you need to delegate. Items wait here until the daily meeting.
3. **The Daily Meeting** — A structured 5-15 minute standup to review The Stack, hand off items, and check on progress.
4. **The Assistant's Judgment** — Once handed off, trust the assistant to handle it. Don't micromanage.
5. **The Weekly Review** — A weekly check on stuck items, completion rates, and delegation health.

### Leader-Assistant Relationship

The leader-assistant relationship is derived from `data/accountability.md`. Look for reporting relationships where one person's seat includes assistant-type responsibilities (Executive Assistant, Office Manager, etc.).

If no clear assistant relationship is found in the accountability chart, ask the user: "Who is your assistant? (I couldn't find a clear assistant relationship in the accountability chart.)"

## Process

### Mode: Stack

Use when adding new items to The Stack. This is the primary way a leader batches delegation throughout the day.

#### Step 1: Identify the Relationship

Determine the leader and assistant. If only one leader-assistant pair exists in `data/accountability.md`, use it automatically. If multiple exist or none is clear, ask the user.

Check for existing stack items to determine the next ID:

1. Scan `data/assistance/stack/` for all `stack-NNN-*.md` files
2. Also check `data/assistance/daily/` meeting logs for any referenced IDs
3. Find the highest numeric ID
4. Increment by 1

#### Step 2: Capture the Item

Ask for the item details:

1. **Title:** Short description of the task ("Schedule board meeting", "Order new monitors")
2. **Urgency:** today, this_week, or whenever
3. **Details:** Any additional context or instructions (optional)

For quick stacking, accept a one-liner: "Stack: Schedule board meeting - this_week" and parse it.

#### Step 3: Create the Stack Item

Create a new file from `templates/assistance-stack.md`:

- Generate the next sequential ID (`stack-NNN`)
- Slugify the title for the filename
- Fill in the frontmatter fields
- Add any details to the body

Show the file before writing. Ask: "Add this to the stack?"

#### Step 4: Confirm

After writing, display a brief confirmation:

```
Added to stack: stack-003 "Schedule board meeting" (this_week)
Stack total: 5 pending items
```

---

### Mode: Daily

Use when running the structured daily standup between a leader and their assistant. This is the 5-15 minute meeting where The Stack is reviewed and items are handed off.

#### Step 1: Load the Stack

Read all files from `data/assistance/stack/` via `Glob("data/assistance/stack/stack-*.md")`. Parse YAML frontmatter.

If no items exist: "The stack is empty. Nothing to review today. Add items with Stack mode throughout the day."

Separate items by status:
- **Pending** — needs to be discussed and handed off
- **Handed off** — check on progress
- **Today urgency** — highlight these first regardless of status

#### Step 2: Display the Agenda

```
Daily Standup — [Date]
━━━━━━━━━━━━━━━━━━━━━
Leader: [Name]  |  Assistant: [Name]

🔴 TODAY (needs attention now):
  stack-005: "Call insurance broker" (pending)
  stack-003: "Send revised proposal" (handed_off — 2 days ago)

📋 PENDING (hand off today):
  stack-007: "Order office supplies" (this_week)
  stack-008: "Research conference venues" (whenever)

🔄 IN PROGRESS (check status):
  stack-001: "Schedule board meeting" (handed_off — 1 day ago)
  stack-004: "Book travel for March" (handed_off — 3 days ago)
```

#### Step 3: Walk Through Each Item

For each item in the agenda, ask the leader:

**For pending items:**
- "Hand off to [assistant]?" → Update status to `handed_off`, set `handed_off` date
- "Defer?" → Keep as pending, optionally update urgency
- "Cancel?" → Remove from stack (delete file)

**For handed-off items:**
- "Done?" → Update status to `done`, set `completed` date
- "Still in progress?" → No change, note in meeting log
- "Stuck?" → Note the blocker, optionally escalate urgency

**For today-urgency items:**
- Highlight with extra emphasis. These should be resolved or actively worked on by end of day.

#### Step 4: Capture New Items

After reviewing existing items: "Any new items to add to the stack?"

If yes, follow Stack mode Steps 2-3 for each new item.

#### Step 5: Save the Meeting Log

Create a daily meeting log from `templates/assistance-daily.md`:

- File: `data/assistance/daily/YYYY-MM-DD.md`
- Fill in frontmatter: date, leader, assistant, counts
- Populate the Stack Review table with decisions from Step 3
- Populate the New Items table from Step 4
- Record any action items discussed

Show the complete meeting log before writing. Ask: "Save this daily meeting log?"

#### Step 6: Update Stack Items

After the meeting log is saved, update all stack item files based on the decisions:

- Set `handed_off` date on newly handed-off items
- Set `completed` date and status on done items
- Update urgency if changed
- Delete cancelled items

Display a brief summary:

```
Daily standup complete:
  Handed off: 2 items
  Completed: 1 item
  Still pending: 3 items
  New items added: 1
  Duration: ~10 minutes
```

---

### Mode: Review

Use when running the weekly review of The Assistance Track. This checks delegation health, identifies stuck items, and surfaces patterns.

#### Step 1: Load All Data

Read all stack items from `data/assistance/stack/` and all daily meeting logs from `data/assistance/daily/`. Parse YAML frontmatter for both.

If no data exists: "No Assistance Track data found. Start by adding items with Stack mode and running Daily meetings."

#### Step 2: Stack Health Summary

```
Assistance Track — Weekly Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stack Status:
  Pending: 4 items
  Handed off: 3 items
  Completed this week: 5 items
  Total active: 7 items

Urgency breakdown:
  Today: 1 item ⚠️
  This week: 3 items
  Whenever: 3 items
```

#### Step 3: Flag Stuck Items

Items that have been on the stack for more than 3 days without progress are flagged:

```
⚠️ Stuck Items (3+ days without progress):
  stack-004: "Book travel for March" — handed_off 5 days ago
    → Consider: Follow up with [assistant], escalate urgency, or reassign
  stack-006: "Update CRM contacts" — pending 4 days ago
    → Consider: Has this been discussed in a daily meeting?
```

For each stuck item, offer options:
- Escalate urgency (e.g., `whenever` → `this_week`)
- Add a note about the blocker
- Reassign to someone else
- Close as no longer needed

#### Step 4: Meeting Cadence Check

Review daily meeting logs for the past week:

```
Daily Meeting Cadence:
  Meetings this week: 4 / 5 expected
  Missing: Wednesday (2026-02-12)
  Avg items per meeting: 3.5
  Avg duration: 12 minutes
```

If fewer than 3 meetings in a week: "⚠️ Only [N] daily meetings this week. The daily standup is the core discipline — consistency matters more than perfection."

#### Step 5: Delegation Trends

If enough data exists (2+ weeks of daily meetings):

```
Delegation Trends (last 2 weeks):
  Items added: 12
  Items completed: 8
  Completion rate: 67%
  Avg time to completion: 2.3 days
  Most common urgency: this_week (58%)
```

#### Step 6: Cross-Reference with Delegate and Elevate

Optionally read `data/delegate/` to check if any Quadrant 3 or 4 tasks from the D&E audit are showing up as stuck stack items. This connects strategic delegation decisions to daily execution:

"Note: stack-004 'Book travel for March' relates to the Q3 task 'Travel logistics' from [person]'s D&E audit. Consider permanent delegation of this category."

#### Step 7: Suggest Actions

Based on the review, suggest 1-3 specific actions:

```
Suggested Actions:
  1. Follow up on 2 stuck items (stack-004, stack-006)
  2. Schedule the missed Wednesday daily meeting
  3. Consider delegating 'travel logistics' permanently (shows up repeatedly)

Would you like to take action on any of these?
```

## Output Format

**Stack:** Brief confirmation with item ID, title, urgency, and current stack count.

**Daily:** Structured agenda sorted by urgency (today first), followed by pending, then in-progress. Interactive walkthrough with decisions recorded. Summary showing handoffs, completions, and new items.

**Review:** Dashboard-style summary with stack health, stuck items, meeting cadence, and delegation trends. Actionable suggestions based on patterns. Complete data shown before any file modifications.

## Guardrails

- **Always show the complete file before writing.** Never create or modify a stack item or meeting log without showing the content and getting approval.
- **Don't auto-invoke other skills.** When review results suggest creating To-Dos or running D&E, mention the option but let the user decide. Say "Would you like to create a To-Do for this?" rather than doing it automatically.
- **Sensitive data warning.** On first use in a session, remind the user: "Assistance Track data includes delegation details and daily meeting notes. This repo should be private."
- **Respect the batch discipline.** Don't encourage adding items AND immediately handing them off. The point of The Stack is to batch — items should generally wait for the next daily meeting to be handed off. Exception: `today` urgency items may warrant immediate handoff.
- **Don't micromanage the assistant.** Once an item is `handed_off`, trust the assistant. The Review mode flags stuck items, but the daily meeting is for status checks, not detailed oversight.
- **One leader-assistant pair per session.** If the organization has multiple leaders with assistants, each session should focus on one relationship. Ask which pair at the start if ambiguous.
- **Stack IDs are permanent.** Once a `stack-NNN` ID is assigned, it's never reused, even if the item is completed or deleted. This ensures meeting logs always reference valid IDs.

## Integration Notes

### Accountability Chart (ceos-accountability)

- **Direction:** Read
- **What data:** `data/accountability.md` — seat names, owners, reporting relationships
- **Purpose:** Identifies the leader-assistant relationship. The assistant is typically the person in a seat with assistant-type responsibilities (Executive Assistant, Office Manager) who reports to the leader. If the accountability chart doesn't define this clearly, the user specifies the relationship.

### Delegate and Elevate (ceos-delegate)

- **Direction:** Read
- **What data:** `data/delegate/firstname-lastname.md` — quadrant assignments, delegation progress
- **Purpose:** Review mode cross-references stuck stack items with Q3/Q4 tasks from D&E audits. Recurring stack items in the same category may indicate a task that should be permanently delegated rather than repeatedly stacked. This connects strategic delegation decisions to daily operational execution.

### To-Dos (ceos-todos)

- **Direction:** Related
- **What data:** `data/todos/` — actions from the daily meeting can be promoted to tracked To-Dos via `ceos-todos`
- **Purpose:** Some items from the daily standup may need formal tracking with due dates and completion rates beyond the stack's simpler lifecycle. Currently stored as action items in the meeting log.

### Write Principle

**Only `ceos-assistance` writes to `data/assistance/`.** Other skills may reference assistance data for delegation context, but do not modify stack items or daily meeting logs.
