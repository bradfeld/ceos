---
name: ceos-l10
description: Use when running or reviewing a Level 10 weekly leadership meeting
file-access: [data/meetings/l10/, templates/l10-meeting.md, data/scorecard/weeks/, data/rocks/, data/issues/open/, data/accountability.md]
tools-used: [Read, Write, Glob]
---

# ceos-l10

Facilitate the Level 10 (L10) Meeting — the weekly 90-minute leadership meeting that keeps the team aligned, accountable, and solving problems. The L10 follows a strict 7-section agenda with time boxes.

## When to Use

- "Run L10" or "start our L10"
- "Level 10 meeting" or "weekly meeting"
- "Start our meeting" or "let's do our weekly"
- "Review last week's L10" or "what were our to-dos?"
- Any weekly leadership team meeting

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/meetings/l10/YYYY-MM-DD.md` | L10 meeting notes |
| `data/scorecard/weeks/` | Latest scorecard (pulled during Scorecard section) |
| `data/rocks/[quarter]/` | Current Rocks (pulled during Rock Review) |
| `data/issues/open/` | Open issues (surfaced during IDS section) |
| `data/meetings/l10/` | Previous L10s (for To-Do review) |
| `templates/l10-meeting.md` | Meeting template |
| `data/accountability.md` | Accountability Chart (seat owners for To-Do assignment validation) |

### Meeting Structure (90 minutes)

| # | Section | Time | Purpose |
|---|---------|------|---------|
| 1 | Segue | 5 min | Personal/professional good news |
| 2 | Scorecard | 5 min | Review weekly numbers |
| 3 | Rock Review | 5 min | Status of quarterly Rocks |
| 4 | Headlines | 5 min | Customer and employee news |
| 5 | To-Do Review | 5 min | Check last week's To-Dos |
| 6 | IDS | 60 min | Identify, Discuss, Solve top issues |
| 7 | Conclude | 5 min | New To-Dos, cascading messages, rating |

## Process

### Step 1: Set Up the Meeting

1. **Date**: Use today's date, or ask if scheduling for a different day.
2. **Attendees**: Ask who's attending. Default to the attendees from the most recent L10 if available.
3. Create the meeting file from `templates/l10-meeting.md` at `data/meetings/l10/YYYY-MM-DD.md`.

If an L10 already exists for today, ask: "There's already an L10 for today. Open it, or create a new one?"

### Step 2: Segue (5 minutes)

Prompt each attendee to share one personal and one professional good news. This builds connection before diving into business.

Record responses in the Segue section.

"Let's start with a segue. [Name], share one personal and one professional good news."

### Step 3: Scorecard Review (5 minutes)

1. Read the most recent weekly scorecard from `data/scorecard/weeks/`.
2. Display the metrics table with status.
3. For each **off-track** metric, note it for the Issues list.

```
Scorecard — Week 07:
  Weekly Revenue: $52K (goal: $50K) ✓
  New Customers: 7 (goal: 10) ✗ → add to Issues?
  NPS: 72 (goal: 70) ✓
```

Ask: "Any off-track items to add to today's Issues list?"

If no scorecard exists for this week: "No scorecard logged for this week yet. Skip, or enter numbers now?"

### Step 4: Rock Review (5 minutes)

1. Read all Rocks in `data/rocks/[current-quarter]/`.
2. Display status for each Rock.
3. Quick check — on track or off track? No discussion yet (save that for IDS).

```
Rock Review — Q1 2026:
  Launch Beta (brad): on_track
  Hire VP Sales (daniel): off_track → add to Issues?
  Implement CRM (daniel): on_track
```

Ask: "Any off-track Rocks to add to today's Issues list?"

### Step 5: Headlines (5 minutes)

Prompt for customer and employee headlines — good news, bad news, updates. Quick hits only. No discussion.

"What headlines do we need to share? Customer news, employee news, anything the team should know."

Record as bullet points.

### Step 6: To-Do Review (5 minutes)

1. Read the **most recent previous L10** from `data/meetings/l10/`.
2. Find the "New To-Dos" table from the Conclude section.
3. For each To-Do, ask: "Done or not done?"

```
To-Do Review (from L10 2026-02-06):
  ☐ Send proposal to Acme (brad) — Done? [yes/no]
  ☐ Schedule interviews (daniel) — Done? [yes/no]
```

4. Calculate completion rate. Target is 90%+.
5. If below 90%, note it but don't dwell — it's data, not a guilt trip.

### Step 7: IDS (60 minutes)

This is the core of the L10 — where the real work happens.

#### Step 7a: Build the Issues List

Collect issues from:
- Off-track Scorecard items (from Step 3)
- Off-track Rocks (from Step 4)
- Open issues from `data/issues/open/`
- New issues raised by attendees

Ask: "What other issues should we add to today's list?"

#### Step 7b: Prioritize

List all issues and ask the team to pick the **top 3** most important ones. These get solved today. The rest stay on the list for next week.

#### Step 7c: IDS Each Issue

For each of the top 3 issues, follow the IDS process:

1. **Identify** — What is the real issue? Dig past symptoms. Use the 5 Whys if the root cause isn't obvious.
2. **Discuss** — Each person shares their perspective. Stay focused — no tangents, no solving yet.
3. **Solve** — What's the action? Create at least one To-Do with an owner and due date. Cross-reference `data/accountability.md` to validate that the To-Do owner matches the seat responsible for that area.

Record the IDS work in the meeting notes. If this creates a new issue file, use `ceos-ids` to write it — `ceos-l10` reads `data/issues/open/` but does not write there directly.

### Step 8: Conclude (5 minutes)

#### New To-Dos

Compile all To-Dos created during the meeting (from IDS and any other sections):

| To-Do | Owner | Due Date |
|-------|-------|----------|
| [Action] | [Name] | [YYYY-MM-DD] |

#### Cascading Messages

Ask: "What needs to be communicated to the rest of the organization?"

#### Meeting Rating

Each attendee rates the meeting 1-10. Record ratings and calculate average. Target: 8+.

If average is below 8: "Below the 8/10 target. What could we improve for next week?"

### Step 9: Save the Meeting

1. Show the completed meeting file.
2. Ask for any final edits.
3. Write to `data/meetings/l10/YYYY-MM-DD.md`.
4. Update the frontmatter with the average rating.
5. Remind: "Run `git commit` to save the meeting notes."

## Transcript Mode

A hybrid workflow designed for teams who want to stay off screens during the meeting and use Apple Voice Memos (or any voice transcription) to feed Claude at two natural break points.

### When to Use

- "Here's my transcript" or "fill this in from my recording"
- "Transcript mode" or "hybrid L10"
- Any time a voice memo transcript is pasted instead of running the meeting live

### How It Works

The meeting runs in two recorded segments with Claude engaged at each break.

#### Break 1 — Before IDS

Stop the recording after To-Do Review. Paste the transcript and tell Claude:
- Who was in the meeting (names, since Voice Memos doesn't label speakers)
- That this covers sections 1–5

Claude will:
1. Parse the transcript and fill sections 1–5 of the meeting file
2. Build the Issues list from off-track Scorecard items, off-track Rocks, open issues in `data/issues/open/`, and anything raised in the conversation
3. Suggest top 3 prioritization based on what was discussed and existing issue data
4. Flag any gaps (missing scorecard numbers, unclear To-Do status) before IDS starts

The team walks into IDS with a ranked Issues list already prepared.

#### Break 2 — Before Conclude

Stop the recording after IDS. Paste the transcript.

Claude will:
1. Parse each issue discussed and fill the IDS section (Identify, Discuss, Solve)
2. Extract all To-Dos with owners and due dates
3. Flag any To-Dos missing an owner or due date
4. Draft cascading messages based on decisions made
5. Present the complete Conclude section ready to read back to the room

The team spends Conclude confirming the To-Do list and rating the meeting — nothing to reconstruct from memory.

### Transcript Tips

- **Name the attendees upfront.** Paste a quick header before the transcript: `Attendees: Brad, Dana, Sam, Jordan`. Voice Memos doesn't label speakers; Claude infers from context but a name list helps.
- **Don't clean up the transcript.** Filler words, crosstalk, and incomplete sentences are fine — Claude works from meaning, not polish.
- **One paste per break.** Don't combine both segments into one paste. The break point is where Claude's IDS prep adds the most value.
- **Implicit issues are fair game.** If the same problem surfaces three times across different topics, Claude will flag it as a potential root cause issue even if it wasn't formally added to the list.

### Guardrails

- **Never infer owners.** If a To-Do doesn't have a clear owner in the transcript, Claude asks rather than guesses.
- **Never infer due dates.** Same rule — prompt for missing dates rather than defaulting to "next week."
- **Preserve verbatim for IDS.** The Discuss sub-section should use close paraphrases from the transcript, not summaries. This matters for anyone who missed the meeting.
- **Still save at the end.** The complete meeting file is written once — after Break 2 and the Conclude confirmation — not incrementally.

---

## Output Format

The meeting file follows the template structure in `templates/l10-meeting.md`:
- YAML frontmatter: date, attendees, rating
- 7 numbered sections with content from the meeting
- To-Do table in the Conclude section

During the meeting, display each section header with its time box as you move through the agenda.

## Guardrails

- **Respect time boxes.** The L10 is 90 minutes total. Don't let any section (especially IDS) expand beyond its allocation without acknowledging the trade-off.
- **IDS gets the most time.** If the team is rushing through Segue/Scorecard/Rocks/Headlines/To-Dos, that's fine — bank the extra time for IDS. But don't skip any section entirely.
- **Top 3 only.** During IDS, solve the top 3 issues. Don't try to solve everything — the rest go to next week's list.
- **Pull real data.** Scorecard and Rock Review should use actual data from `data/scorecard/weeks/` and `data/rocks/`. Don't ask the user to recite numbers that are already on file.
- **Reference previous L10.** To-Do review must check the actual previous meeting file, not rely on memory.
- **Don't auto-invoke skills.** When IDS work creates an issue worth tracking, mention that `ceos-ids` can create the issue file, but let the user decide. Same for scorecard logging (`ceos-scorecard`).
- **One meeting per day.** If an L10 already exists for the date, confirm before overwriting.
- **Save at the end.** Write the complete meeting file at the end, not incrementally during the meeting.
- **Sensitive data warning.** On first use, remind the user: "L10 meeting notes may contain sensitive business discussions and personnel matters. Use a private repo."

## Integration Notes

### Scorecard (ceos-scorecard)

- **Read:** `ceos-l10` reads the latest weekly scorecard from `data/scorecard/weeks/` during Section 2 (Scorecard Review). Each metric owner reports their number and off-track items are flagged for the Issues list.
- **Suggested flow:** Off-track metrics that persist for 3+ weeks should become Issues via `ceos-ids`.

### Rocks (ceos-rocks)

- **Read:** `ceos-l10` reads Rock files from `data/rocks/[current-quarter]/` during Section 3 (Rock Review). Each Rock owner reports on_track or off_track status.
- **Suggested flow:** Off-track Rocks should be discussed further in the IDS section.

### To-Dos (ceos-todos)

- **Read/Write:** `ceos-l10` reads previous meeting To-Dos during Section 5 (To-Do Review) and creates new To-Dos during Section 7 (Conclude). To-Dos created during L10 use `source: l10`.
- **Suggested flow:** Use `ceos-todos` Create mode for formal To-Do tracking after the meeting.

### IDS (ceos-ids)

- **Read:** `ceos-l10` reads open issues from `data/issues/open/` during Section 6 (IDS). The L10 surfaces the prioritized list; `ceos-ids` handles the formal Identify, Discuss, Solve work on individual issues.
- **Suggested flow:** New issues surfaced during L10 should be created via `ceos-ids` Create mode.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-l10` reads `data/accountability.md` during IDS (Step 7c) to validate that To-Do owners match seat responsibilities. When assigning action items, the person who owns the relevant seat should own the To-Do.
- **Suggested flow:** If a To-Do is assigned to someone outside the responsible seat, flag it: "This action falls under the [Seat] responsibilities. Should [Seat Owner] own it instead?"

### Orchestration Principle

`ceos-l10` is the orchestrator — it reads data from multiple skills during the meeting but defers to each skill for formal create/update operations. The meeting file at `data/meetings/l10/YYYY-MM-DD.md` is the only file `ceos-l10` writes directly.
