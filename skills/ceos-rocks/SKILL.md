---
name: ceos-rocks
description: Use when setting, tracking, or scoring quarterly Rocks
file-access: [data/rocks/, templates/rock.md, data/vision.md, data/accountability.md]
tools-used: [Read, Write, Glob]
---

# ceos-rocks

Manage quarterly Rocks — the 3-7 most important priorities for the next 90 days. Each Rock has one owner, a measurable outcome, and a due date at quarter end.

## When to Use

- "Set rocks for this quarter" or "let's plan our quarterly priorities"
- "Rock status" or "how are our rocks tracking?"
- "Score rocks" or "end of quarter review"
- "Create a rock" or "add a new rock for [person]"
- "What rocks does [person] own?"
- Any quarterly planning or review conversation

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/rocks/QUARTER/` | Rock files for each quarter (e.g., `data/rocks/2026-Q1/`) |
| `data/vision.md` | V/TO document (1-Year Plan for alignment checks) |
| `templates/rock.md` | Template for creating new Rock files |
| `data/accountability.md` | Accountability Chart (seat owners for Rock-owner alignment) |

### Rock File Format

Each Rock is a markdown file with YAML frontmatter:

```yaml
id: rock-001
title: "Launch Beta Program"
owner: "brad"
quarter: "2026-Q1"
status: on_track       # on_track | off_track | complete | dropped
created: "2026-01-02"
due: "2026-03-31"
```

**Status values:**
- `on_track` — progressing as expected
- `off_track` — behind or at risk
- `complete` — done (set during end-of-quarter scoring)
- `dropped` — no longer a priority (set during end-of-quarter scoring)

**File naming:** `rock-NNN-slug.md` where NNN is a zero-padded ID and slug is the title slugified (lowercase, hyphens, no special chars).

**Milestones:** Rocks support two milestone formats:
- **Structured (frontmatter):** Array of milestone objects with `title`, optional `due` date, and `status` (`todo`/`in_progress`/`done`). Enables date-based progress tracking and overdue detection.
- **Markdown checklist (body):** Traditional `- [ ]` / `- [x]` checklist items in the Milestones section. Simple and human-friendly.

Both are valid. Tracking mode prefers frontmatter milestones when present, falls back to markdown checklist parsing otherwise.

**Attachments:** Optional `attachments` array in frontmatter references supporting documents. Each attachment has a `path` (relative to CEOS root) and optional `label`. The skill displays references but does not manage files.

### Quarter Format

Quarters follow `YYYY-QN` format: `2026-Q1`, `2026-Q2`, `2026-Q3`, `2026-Q4`.

To determine the current quarter from today's date:
- Jan-Mar = Q1, Apr-Jun = Q2, Jul-Sep = Q3, Oct-Dec = Q4

## Process

### Mode: Setting Rocks

Use when creating new Rocks at the start of a quarter.

#### Step 1: Determine the Quarter

Check if the user specified a quarter. If not, use the current quarter. If creating Rocks for a past quarter, warn: "That quarter has already started/ended. Continue anyway?"

Create the quarter directory if it doesn't exist: `data/rocks/YYYY-QN/`

#### Step 2: Review Context

Before creating Rocks, read and briefly summarize:
- The **1-Year Plan** from `data/vision.md` (what are we trying to achieve this year?)
- Any **existing Rocks** for this quarter (avoid duplicates)

#### Step 3: Walk Through Each Rock

For each Rock, collect:

1. **Title** — short, specific description (e.g., "Launch Beta Program")
2. **Owner** — one person (Rocks are never shared)
3. **Measurable outcome** — what does "done" look like?
4. **Milestones** — 2-4 checkpoints toward completion
5. **Structured milestones (optional)** — Ask: "Add due dates to milestones?"
   - If yes, collect for each milestone: title, due date (`YYYY-MM-DD`), status (default: `todo`)
   - Store as `milestones` array in frontmatter
   - If no, use markdown checklist only (traditional format)
   - If more than 7 milestones, warn: "EOS recommends 3-5 milestones per Rock. Are all of these essential checkpoints?"
6. **Attachments (optional)** — Ask: "Any supporting documents to reference?"
   - If yes, collect: path (relative to CEOS root) and optional label for each
   - Store as `attachments` array in frontmatter

#### Step 4: Validate

- **3-7 Rocks per person.** If someone has fewer than 3, ask if they should own more. If more than 7, flag: "Too many Rocks for [person]. EOS recommends 3-7. Which ones are the real priorities?"
- **Alignment check.** Does each Rock connect to a 1-Year Plan goal? Flag any that don't.
- **Due date.** Set to the last day of the quarter.
- **Seat alignment.** Cross-reference Rock owners against `data/accountability.md`. Flag mismatches if a Rock's subject area doesn't match the owner's seat responsibilities, for example: "This Rock falls under the [Seat] responsibilities. Should [Seat Owner] own it instead?"

#### Step 5: Generate the ID

Read existing Rock files across **every** quarter directory under `data/rocks/`. Find the highest `rock-NNN` ID and increment. If no Rock files exist anywhere, start at `rock-001`.

- **Rock IDs are globally sequential across quarters.** Numeric IDs run sequentially across the whole repository rather than resetting each quarter, so a new quarter continues from the highest existing ID. This avoids collisions and keeps a Rock reference stable no matter which quarter it came from.

  ```
  // Good
    # After Q1 has rock-001 through rock-007:
    data/rocks/2026-Q2/rock-008-launch-beta.md
    data/rocks/2026-Q2/rock-009-hire-vp-sales.md

  // Bad
    # Don't restart numbering each quarter:
    data/rocks/2026-Q2/rock-001-launch-beta.md
    data/rocks/2026-Q2/rock-002-hire-vp-sales.md
  ```

#### Step 6: Write the File

Use `templates/rock.md` as the template. Substitute:
- Frontmatter fields (id, title, owner, quarter, status=on_track, created=today, due=quarter-end)
- Body sections (measurable outcome, milestones)

Write to `data/rocks/YYYY-QN/rock-NNN-slug.md`.

Show the user the complete file before writing. Ask: "Create this Rock?"

#### Step 7: Repeat or Finish

Ask: "Create another Rock, or are we done for now?"

When finished, display a summary table of all Rocks for the quarter:

| Rock | Owner | Due |
|------|-------|-----|
| Launch Beta Program | brad | 2026-03-31 |
| Hire VP Sales | daniel | 2026-03-31 |

---

### Mode: Tracking Rocks

Use for weekly or ad-hoc status checks.

#### Step 1: Read All Rocks

Read all Rock files in `data/rocks/[current-quarter]/`. Parse the frontmatter for status.

#### Step 2: Display Status

Show a status table:

| Rock | Owner | Status | Milestones | Notes |
|------|-------|--------|------------|-------|
| Launch Beta Program | brad | on_track | 2/3 complete | On schedule |
| Hire VP Sales | daniel | off_track | 0/4 complete (1 overdue) | No candidates yet |

**Milestone progress computation:**
- **If frontmatter has `milestones` array**: Count entries with `status: done` vs total. Display: "N/M complete". If any milestone has `due` in the past and `status` is not `done`, append "(X overdue)".
- **Else**: Parse markdown checklist in body (count `[x]` vs total `[ ]` and `[x]`). Display: "N/M done".

**Attachment display:** If frontmatter has `attachments` array, show after the status table:

```
Attachments:
  • Beta spec (data/rocks/2026-Q1/rock-001-beta-spec.pdf)
  • Requirements doc (data/rocks/2026-Q1/requirements.pdf)
```

#### Step 3: Update Status

If a Rock's status needs to change:
1. Show the current status
2. Ask what the new status should be (on_track or off_track)
3. Show the diff in the frontmatter
4. Ask for approval before writing
5. Add a dated note to the Notes section

---

### Mode: Scoring Rocks (End of Quarter)

Use at the end of a quarter for the completion review.

#### Step 1: Load All Rocks

Read all Rock files in `data/rocks/[quarter]/`.

#### Step 2: Score Each Rock

For each Rock, ask: **"Complete or incomplete?"**

- EOS scoring is binary. No partial credit. The measurable outcome was either achieved or it wasn't.
- Update status to `complete` or `dropped` (if the Rock was abandoned or deprioritized)
- A Rock that was worked on but not finished gets `dropped` — it can become a new Rock next quarter

- **Append a timestamped entry to the Notes section.** Whenever a rock file is created or updated, add a dated line to its Notes section, in the form `- YYYY-MM-DD: [what happened]`. At end-of-quarter scoring, append a scoring entry rather than only flipping the frontmatter status. The result is an audit trail inside each file, so the history of a Rock is readable without consulting git.

  ```
  // Good
    ## Notes

    *Track progress, blockers, and context here during the quarter.*

    - 2026-02-15: Rock created for 2026-Q1
    - 2026-04-03: Q1 scoring — dropped

  // Bad
    ## Notes

    *Track progress, blockers, and context here during the quarter.*

    - 2026-02-15: Rock created for 2026-Q1
    # (status changed to dropped, but no scoring entry was added)
  ```

- **Use `dropped`, not `not_done`, for a Rock abandoned as no longer a priority.** The two are not interchangeable. `not_done` means the Rock was pursued and missed; `dropped` means it stopped being relevant or was re-scoped away — a deliberate deprioritization. Scoring an abandoned Rock as `not_done` reads as a failure to deliver and loses the signal that the team chose to stop. Keep the quarterly planning doc's scorecard table using the same word as the rock file.

  ```
  // Good
    # Rock intentionally abandoned after re-scoping:
    status: dropped
    # In Notes:
    - 2026-04-03: Q1 scoring — dropped

  // Bad
    # Same Rock, recorded as merely incomplete:
    status: not_done
  ```

#### Step 3: Show the diff for each status change, ask for approval.

#### Step 4: Summary

Display the quarter scorecard:

```
Q1 2026 Rock Scorecard
━━━━━━━━━━━━━━━━━━━━━━
Complete: 4/6 (67%)
Target: 80%+

✓ Launch Beta Program (brad)
✓ Hire VP Sales (daniel)
✓ Implement CRM (daniel)
✗ Redesign Onboarding (brad) — dropped
✓ ISO Certification (sarah)
✗ Partner Program (brad) — dropped
```

If completion rate is below 80%, flag it: "Below the 80% target. Consider: Were Rocks too ambitious, or were there execution issues? This is a good topic for the next L10."

## Output Format

**Setting:** Show each Rock file before writing. End with a summary table.
**Tracking:** Status table with milestone progress (from frontmatter milestones if present, else markdown checklist). Overdue milestones flagged. Attachments listed if present.
**Scoring:** Quarter scorecard with completion rate.

## Guardrails

- **Always show diff before writing.** Never modify a Rock file without showing the change and getting approval.
- **One owner per Rock.** If the user tries to assign a Rock to multiple people, explain that EOS Rocks have one owner. Suggest splitting into separate Rocks.
- **3-7 per person.** Warn (don't block) if someone is outside this range.
- **Binary scoring only.** Don't allow "partial" or percentage-based scoring. Complete or dropped.
- **Milestone status values.** Only accept `todo`, `in_progress`, `done` for structured milestones. If the user provides another value during creation, show the allowed values.
- **Respect quarter boundaries.** Rocks in `data/rocks/2026-Q1/` belong to Q1. Don't move them between quarters — create new Rocks in the next quarter instead.
- **Cross-reference V/TO.** When setting Rocks, check alignment with the 1-Year Plan from `data/vision.md`. Use `ceos-vto` if deeper vision review is needed.
- **ID uniqueness.** Always check existing files before assigning an ID to avoid collisions.
- **Don't auto-invoke other skills.** Mention `ceos-vto`, `ceos-l10`, and `ceos-annual` when relevant, but let the user decide when to switch workflows.
- **Sensitive data warning.** On first use, remind the user: "Rocks may contain sensitive business priorities. Use a private repo."

## Integration Notes

### V/TO (ceos-vto)

- **Read:** `ceos-rocks` reads `data/vision.md` to check the 1-Year Plan when setting Rocks. Each Rock should connect to a 1-Year Plan goal.
- **Suggested flow:** If Rocks don't align with the 1-Year Plan, suggest: "Review the V/TO with `ceos-vto` to ensure strategic alignment."

### L10 Meetings (ceos-l10)

- **Read:** `ceos-l10` reads Rock files during Section 4 (Rock Review) of the L10 meeting. Each Rock owner reports on_track or off_track status.
- **Suggested flow:** Off-track Rocks should be discussed further in the IDS section of the L10.

### Quarterly Conversations (ceos-quarterly)

- **Read:** `ceos-quarterly` references Rock progress during quarterly conversations. Rock ownership and status provide context for individual performance discussions.

### Annual Planning (ceos-annual)

- **Read/Write:** During annual planning, the team scores the outgoing quarter's Rocks and sets Q1 Rocks for the new year. `ceos-annual` orchestrates this; `ceos-rocks` handles the actual Rock creation and scoring.

### To-Dos (ceos-todos)

- **Related:** Rock milestones may generate To-Dos during L10 meetings. These To-Dos are tracked in `data/todos/` via `ceos-todos` with `source: l10`.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-rocks` reads `data/accountability.md` when setting Rocks to validate that Rock owners match seat responsibilities. A Rock about sales pipeline should belong to whoever owns the Sales & Marketing seat.
- **Suggested flow:** If a Rock doesn't align with the owner's seat, suggest: "This Rock falls under the [Seat] responsibilities. Should [Seat Owner] own it instead?"

### Read-Only Principle

Other skills read `data/rocks/` for reference. **Only `ceos-rocks` writes to Rock files.** This preserves a single source of truth for quarterly priorities.
