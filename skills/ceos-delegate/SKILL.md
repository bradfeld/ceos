---
name: ceos-delegate
description: Use when categorizing tasks for delegation using the Delegate and Elevate 4-quadrant framework
file-access: [data/delegate/, templates/delegate.md, data/accountability.md, data/people/]
tools-used: [Read, Write, Glob]
---

# ceos-delegate

Categorize a leader's tasks and responsibilities into the Delegate and Elevate 4-quadrant matrix based on enjoyment and competency. Identify what to keep, what to delegate, and create action plans for handing off work that doesn't belong in the leader's "Love It / Great At It" quadrant.

**Not for:** People evaluation (use `ceos-people`), organizational structure (use `ceos-accountability`), or performance conversations (use `ceos-quarterly`). Delegate and Elevate is a **leadership development tool** — it helps leaders focus on their highest and best use, not assess fit or performance.

## When to Use

- "Run delegate and elevate for [person]" or "delegation audit"
- "What should I be delegating?" or "am I doing the right work?"
- "Review delegation progress" or "how's [person]'s delegation going?"
- "Create a delegation plan" or "help me hand off these tasks"
- "What's in my bottom quadrants?" or "show my D&E results"
- "Time for a delegation audit" or "let's do delegate and elevate"
- Any discussion about task delegation, leadership focus, or highest-and-best-use

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/delegate/` | Delegate and Elevate audit files (one per person) |
| `templates/delegate.md` | Template for new delegation audits |
| `data/accountability.md` | Source of seat responsibilities (read-only — use ceos-accountability to modify) |
| `data/people/` | People Analyzer evaluations (read-only — reference for context) |

### Delegate File Format

Each person has a markdown file at `data/delegate/firstname-lastname.md` with YAML frontmatter:

```yaml
person: "Brad Feld"
seat: "Visionary"
date: "2026-02-15"
status: active            # active | reviewed | stale
quadrant_counts:
  love_great: 5           # Love It / Great At It — keep
  like_good: 3            # Like It / Good At It — delegate when possible
  not_like_good: 4        # Don't Like It / Good At It — delegate soon
  not_like_not_good: 2    # Don't Like It / Not Good At It — delegate immediately
delegation_progress:
  delegated: 3            # Tasks successfully delegated
  total: 6                # Total tasks in bottom two quadrants
  percent: 50
last_reviewed: "2026-02-15"
```

**File naming:** `firstname-lastname.md` — lowercase, hyphenated. Person-centric (survives role changes).

### The Four Quadrants

| Quadrant | Enjoyment | Competency | Action | Priority |
|----------|-----------|------------|--------|----------|
| **Love It / Great At It** | High | High | Keep | — |
| **Like It / Good At It** | Medium | High | Delegate when possible | Low |
| **Don't Like It / Good At It** | Low | High | Delegate soon | Medium |
| **Don't Like It / Not Good At It** | Low | Low | Delegate immediately | High |

The goal is to spend 80%+ of time in Quadrant 1. Tasks in Quadrants 3 and 4 drain energy and often become bottlenecks because the leader delays or underperforms them.

### Status Values

| Status | Meaning | When |
|--------|---------|------|
| `active` | Current audit, delegation in progress | After initial audit or re-audit |
| `reviewed` | Audit reviewed, delegation actions updated | After a Review or Plan session |
| `stale` | Audit is > 120 days old | Flagged automatically by Review mode |

## Process

### Mode: Audit

Use when running a Delegate and Elevate audit for a specific person. This is typically done 1-2x per year per leadership team member.

#### Step 1: Identify the Person

Ask for the person's name. Check if `data/delegate/firstname-lastname.md` already exists.

- **Exists:** Read the file, show current quadrant distribution: "You have an existing audit from [date]. Re-audit (start fresh) or update (add/move tasks)?"
- **New person:** Will create from `templates/delegate.md`

#### Step 2: Pull Context from Accountability Chart

Read `data/accountability.md` to find the person's seat(s) and their 5 key responsibilities per seat.

- **Has a seat:** Display responsibilities as a starter list: "Based on the Accountability Chart, here are [person]'s seat responsibilities. We'll use these as a starting point — you can add, remove, or modify."
- **Multiple seats:** Display all seats grouped separately: "Seat 1: [name] — [5 roles]. Seat 2: [name] — [5 roles]."
- **No seat found:** Warn: "[Person] has no seat defined in the Accountability Chart. List their tasks/responsibilities manually."

Optionally check `data/people/firstname-lastname.md` for additional context (GWC assessment, current status). Don't display unless relevant — this is about tasks, not performance.

#### Step 3: List All Tasks and Responsibilities

Walk the user through building a complete task list. Start with the seat responsibilities from Step 2, then expand:

"Beyond seat responsibilities, what else does [person] spend time on? Think about:
- Recurring meetings they run or attend
- Administrative tasks (email, reports, approvals)
- Projects they're leading or contributing to
- Tasks they've inherited or picked up informally
- Things 'only they can do' (real or perceived)"

Collect tasks as a numbered list. Aim for 10-20 tasks total. If the user lists fewer than 8, prompt: "Leaders typically have 12-20 distinct responsibilities. Are there tasks you're forgetting?"

#### Step 4: Categorize Each Task

For each task, ask two questions:

1. **Enjoyment:** "Do you love doing this, like it, or not like it?"
2. **Competency:** "Are you great at this, good at it, or not good at it?"

Map the answers to quadrants:

| Enjoyment | Competency | Quadrant |
|-----------|------------|----------|
| Love it | Great at it | Q1: Love It / Great At It |
| Like it | Good at it | Q2: Like It / Good At It |
| Love it | Good at it | Q2: Like It / Good At It |
| Like it | Great at it | Q1: Love It / Great At It |
| Don't like it | Good/Great at it | Q3: Don't Like It / Good At It |
| Don't like it | Not good at it | Q4: Don't Like It / Not Good At It |

**Batch processing:** For efficiency, present 3-5 tasks at a time rather than one by one. Display a table and let the user categorize in batches.

#### Step 5: Display Quadrant Distribution

After all tasks are categorized, show the summary:

```
Delegate and Elevate — [Person Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quadrant Distribution:

| Quadrant | Count | % | Action |
|----------|-------|---|--------|
| Love It / Great At It | 5 | 36% | Keep |
| Like It / Good At It | 3 | 21% | Delegate when possible |
| Don't Like It / Good At It | 4 | 29% | Delegate soon |
| Don't Like It / Not Good At It | 2 | 14% | Delegate immediately |

Total tasks: 14
Quadrant 1 focus: 36% — Target: 80%+
Tasks to delegate: 6 (43% of total)
```

#### Step 6: Identify Delegation Priorities

Highlight the bottom two quadrants with urgency:

```
🔴 Delegate Immediately (Q4):
  1. [Task] — Not good at it, doesn't enjoy it. Bottleneck risk.
  2. [Task] — Energy drain and quality risk.

🟡 Delegate Soon (Q3):
  1. [Task] — Competent but draining. Find someone who loves it.
  2. [Task] — Good at it but resents it. Delegate before burnout.
  3. [Task] — High skill, low passion. Perfect for a rising team member.
  4. [Task] — Taking time from Q1 work.
```

#### Step 7: Save the File

Show the complete file before writing. Ask: "Save this Delegate and Elevate audit?"

Write to `data/delegate/firstname-lastname.md` using the template. Update:
- YAML frontmatter: quadrant counts, delegation progress (total = Q3 + Q4 count, delegated = 0)
- Markdown body: populate all four quadrant tables with tasks
- Audit History: add dated entry

---

### Mode: Review

Use when reviewing Delegate and Elevate results across the team or for a specific person.

#### Step 1: Read All Delegate Files

Read all files from `data/delegate/` via `Glob("data/delegate/*.md")`. Parse YAML frontmatter.

If no files exist: "No Delegate and Elevate audits found. Run an Audit for your first team member."

#### Step 2: Display Summary Table

```
Delegate and Elevate — Team Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Name | Seat | Last Audit | Q1 | Q2 | Q3 | Q4 | Delegation % | Flag |
|------|------|------------|----|----|----|----|-------------|------|
| Brad Feld | Visionary | 2026-02-15 | 5 | 3 | 4 | 2 | 50% | |
| Sarah Chen | Integrator | 2026-01-10 | 8 | 2 | 1 | 0 | 100% | |
| Mike Torres | VP Sales | 2025-09-15 | 3 | 4 | 5 | 3 | 25% | 📅 Stale |

Team averages:
  Q1 focus: 53% — Target: 80%+
  Delegation completion: 58%
```

#### Step 3: Track Delegation Progress

For each person, parse their delegate file for "Delegated?" column values:

- Count tasks in Q3 and Q4 that are marked as delegated
- Calculate delegation progress percentage
- Compare to last review if multiple audit history entries exist

```
Delegation Progress — [Person Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Delegated: 3 / 6 tasks (50%)
  ████████████░░░░░░░░░░░░ 50%

  Completed delegations:
  ✓ [Task A] → [Person X] — Done
  ✓ [Task B] → [Person Y] — Done
  ✓ [Task C] → [Person Z] — Done

  Remaining:
  ○ [Task D] — No owner assigned yet
  ○ [Task E] — Training in progress
  ○ [Task F] — Not started
```

#### Step 4: Flag Stale Audits

Check `last_reviewed` date for each person. If > 120 days ago:

"📅 [Person]'s audit is [N] days old. Consider re-running before the next Quarterly Planning session."

#### Step 5: Quadrant Trends

If a person has multiple audit history entries (from re-audits), show the trend:

```
Quadrant Trend — [Person Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Date | Q1 | Q2 | Q3 | Q4 | Q1 % |
|------|----|----|----|----|------|
| 2025-08-15 | 3 | 4 | 5 | 3 | 20% |
| 2026-02-15 | 5 | 3 | 4 | 2 | 36% |

Direction: Improving (+16% Q1 focus)
```

#### Step 6: Drill Down

Ask: "Want to view details for a specific person, or run a new Audit?"

---

### Mode: Plan

Use when creating a concrete delegation plan for tasks in the bottom two quadrants.

#### Step 1: Select Person and Load Audit

Ask for the person's name. Read `data/delegate/firstname-lastname.md`.

If no audit exists: "No audit found for [person]. Run an Audit first to identify tasks for delegation."

#### Step 2: Review Delegation Candidates

Display tasks from Quadrants 3 and 4 that haven't been delegated yet:

```
Tasks Ready for Delegation — [Person Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Delegate Immediately (Q4):
  1. [Task A] — Not good at it, doesn't enjoy it

🟡 Delegate Soon (Q3):
  2. [Task B] — Good at it but draining
  3. [Task C] — Competent but would rather not

Which tasks would you like to create delegation plans for? (all / select by number)
```

#### Step 3: Collect Delegation Details

For each selected task, ask:

1. **Who to delegate to?** — Check Accountability Chart for candidates in related seats. Suggest if possible: "Based on the org chart, [Person X] in [Seat Y] might be a fit. Or name someone else."
2. **Training needed?** — "Does the delegate need training? If yes, what specifically?"
3. **Timeline:** — "When should this delegation be complete? (e.g., 2 weeks, end of quarter)"

#### Step 4: Create Action Plan

Build the delegation plan in the delegate file:

```
Delegation Plan
━━━━━━━━━━━━━━

| Task | Delegate To | Training Needed | Timeline | Status |
|------|-------------|----------------|----------|--------|
| [Task A] | Sarah Chen | Yes — shadow for 1 week | 2026-03-01 | Not started |
| [Task B] | Mike Torres | No — already has skills | 2026-02-28 | Not started |
| [Task C] | New hire (VP Ops) | Yes — full onboarding | 2026-Q2 | Blocked (hiring) |
```

#### Step 5: Note To-Do Integration

Display: "Delegation actions saved to the delegate file. These can be promoted to tracked To-Dos with owners and due dates via `ceos-todos`."

#### Step 6: Save Updated File

Show the complete updated file before writing. Ask: "Save this delegation plan?"

Update:
- YAML frontmatter: `delegation_progress.total` = count of Q3+Q4 tasks, `last_reviewed` = today
- Markdown body: populate delegation plan table
- Audit History: add dated entry for plan creation

## Output Format

**Audit:** Quadrant distribution table with counts and percentages. Delegation priority flags (Q4 = immediate, Q3 = soon). Complete file shown before save.

**Review:** Summary table with all team members, quadrant counts, delegation progress %, and stale flags. Quadrant trends if multiple audits exist. Progress bars for delegation completion.

**Plan:** Delegation candidate list from Q3/Q4. Action plan table with delegate, training, timeline, and status. Complete file shown before save.

## Guardrails

- **Always show the complete file before writing.** Never modify a delegate file without showing the change and getting approval.
- **One quadrant per task.** Each task can only be in one quadrant. If a user tries to add the same task to multiple quadrants, ask them to choose.
- **Don't force delegation.** Some Q3 tasks may need to stay temporarily (no one else can do them yet). Flag them but don't pressure.
- **Seat responsibilities are starter prompts, not requirements.** The Accountability Chart provides a starting list, but tasks can come from anywhere — meetings, informal responsibilities, inherited work.
- **Don't confuse with People Analyzer.** Delegate and Elevate is about tasks and leadership focus, not about whether a person is a fit. If the user seems to be evaluating a person's performance, suggest `ceos-people` instead.
- **Sensitive data warning.** On first use in a session, remind the user: "Delegate and Elevate audits contain information about leadership capacity and task ownership. This repo should be private."
- **Don't auto-invoke other skills.** When delegation results suggest creating To-Dos or IDS issues, mention the option but let the user decide. Say "Would you like to create a To-Do for this?" rather than doing it automatically.
- **Respect the quarterly cadence.** Suggest running D&E before Quarterly Planning sessions. Flag audits > 120 days old. But don't nag — once per session is enough.

## Integration Notes

### Accountability Chart (ceos-accountability)

- **Direction:** Read
- **What data:** `data/accountability.md` — seat names, owners, and 5 key responsibilities per seat
- **Purpose:** Provides the starter list of tasks/responsibilities during Audit mode. The seat responsibilities give structure to what might otherwise be a blank-page exercise.

### People Analyzer (ceos-people)

- **Direction:** Read
- **What data:** `data/people/firstname-lastname.md` — GWC assessment, current status
- **Purpose:** Optional context during Audit. If a person is `wrong_seat`, their D&E audit might reveal why — they may be great at tasks outside their current seat. If `below_bar`, D&E can help identify whether it's a skill gap (Q4 tasks) or an energy gap (Q3 tasks).

### To-Dos (ceos-todos)

- **Direction:** Related
- **What data:** `data/todos/` — delegation actions can be promoted to tracked To-Dos via `ceos-todos`
- **Purpose:** Delegation actions from Plan mode can become tracked To-Dos with owners and due dates. Currently stored as markdown checklists in the delegate file.

### Quarterly Planning (ceos-quarterly-planning)

- **Direction:** Related
- **What data:** No direct data access
- **Purpose:** Delegate and Elevate is ideally run before or during Quarterly Planning sessions. Delegation decisions often surface during quarterly reviews when leaders assess their capacity for new Rocks.

### Annual Planning (ceos-annual)

- **Direction:** Related
- **What data:** No direct data access
- **Purpose:** Annual planning often triggers a fresh D&E audit as leaders reassess their focus for the coming year.

### Write Principle

**Only `ceos-delegate` writes to `data/delegate/`.** Other skills may reference delegation audits for leadership development context, but do not modify them.
