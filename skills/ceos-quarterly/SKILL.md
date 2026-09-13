---
name: ceos-quarterly
description: Use when conducting, scheduling, or reviewing quarterly conversations or 5-5-5 quick check-ins between managers and direct reports
file-access: [data/conversations/, templates/quarterly-conversation.md, templates/quarterly-quick.md, data/vision.md, data/accountability.md, data/rocks/, data/people/]
tools-used: [Read, Write, Glob]
---

# ceos-quarterly

Facilitate the EOS Quarterly Conversation — the formal quarterly check-in between each manager and their direct reports — or the 5-5-5, a lightweight 15-minute version. The full conversation follows a 5-point agenda (30-60 min). The 5-5-5 uses three time-boxed sections (15 min). Both are two-way conversations about alignment, role satisfaction, and obstacles — not performance reviews.

**Not for:** Quarterly planning sessions (use `ceos-quarterly-planning`), people evaluations (use `ceos-people`), or annual planning (use `ceos-annual`). Quarterly Conversations are **1-on-1 check-ins**, not team-wide planning sessions.

## When to Use

- "Run quarterly conversation for [person]" or "quarterly check-in with [name]"
- "5-5-5 with [person]" or "quick quarterly check-in with [name]"
- "Quick conversation with [person]" or "quick check-in"
- "Schedule quarterly conversations" or "who needs a quarterly conversation?"
- "Review quarterly conversations" or "show conversation history for [person]"
- "Quarterly one-on-one" or "manager check-in"
- Any discussion about formal quarterly conversations or quick 5-5-5 check-ins between managers and direct reports

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/conversations/QUARTER/` | Conversation files by quarter (e.g., `data/conversations/2026-Q1/`) |
| `data/vision.md` | Source of Core Values (read-only — use ceos-vto to modify) |
| `data/accountability.md` | Source of seats, owners, and reporting structure |
| `data/rocks/QUARTER/` | Rock files for the quarter (read-only — use ceos-rocks to modify) |
| `data/people/` | People Analyzer evaluations (read-only — use ceos-people to modify) |
| `templates/quarterly-conversation.md` | Template for full conversation files |
| `templates/quarterly-quick.md` | Template for 5-5-5 quick check-in files |

### Conversation File Format

Each conversation is a markdown file at `data/conversations/YYYY-QN/firstname-lastname.md` with YAML frontmatter:

```yaml
person: "Brad Feld"
manager: "Daniel"
quarter: "2026-Q1"
date: "2026-03-15"
core_values_rating: 5       # count of + ratings out of total Core Values
gwc_status: pass             # pass | fail | evaluating
rocks_completion_rate: 80    # percentage (0-100) or null if no Rocks
```

**File naming:** `firstname-lastname.md` — lowercase, hyphenated. Matches the naming convention from `ceos-people`.

### Quick Conversation File Format

Quick 5-5-5 check-ins use a separate file at `data/conversations/YYYY-QN/firstname-lastname-quick.md` with YAML frontmatter:

```yaml
type: quick
person: "Brad Feld"
manager: "Daniel"
quarter: "2026-Q1"
date: "2026-02-14"
core_values_rating: null
gwc_status: null
rocks_completion_rate: null
```

**File naming:** `firstname-lastname-quick.md` — the `-quick` suffix prevents collisions with full conversation files. The `type: quick` frontmatter field distinguishes format.

**Scoring fields:** Always `null` for quick conversations. The 5-5-5 is informal — no formal ratings, pass/fail, or completion percentages.

**Backward compatibility:** Files without a `type` field are treated as `full` (the original format).

### The 5-5-5 Format

The EOS 5-5-5 is a 15-minute check-in with three equal time-boxed sections:

| # | Section | Duration | Focus |
|---|---------|----------|-------|
| 1 | Employee Speaks | 5 min | Core Values, Rocks, Role (GWC) — from the employee's perspective |
| 2 | Manager Speaks | 5 min | Performance, Wins, Concerns — from the manager's perspective |
| 3 | Together | 5 min | Next Steps, Commitments — agreed together |

**Key difference from full conversation:** The 5-5-5 is structured around who speaks, not topic sections. The employee gets uninterrupted time first, then the manager, then they collaborate.

### Quarter Format

Quarters follow `YYYY-QN` format: `2026-Q1`, `2026-Q2`, `2026-Q3`, `2026-Q4`.

To determine the current quarter from today's date:
- Jan-Mar = Q1, Apr-Jun = Q2, Jul-Sep = Q3, Oct-Dec = Q4

### The 5-Point Agenda

| # | Section | Focus |
|---|---------|-------|
| 1 | Core Values Alignment | How are they living the Core Values? |
| 2 | GWC | Do they still Get it, Want it, have Capacity? |
| 3 | Rocks Review | How did their Rocks go this quarter? |
| 4 | Role Expectations | Are roles clear and being met? |
| 5 | Feedback Both Ways | What's working? What's not? What's needed? |

### Key EOS Principles

- **Every direct report gets one conversation per quarter.** This is not optional — it's part of the system.
- **Two-way conversation.** The direct report should talk as much as the manager. It's a dialogue, not a lecture.
- **Reference, don't re-evaluate.** Core Values and GWC reference the People Analyzer results — this isn't a fresh evaluation. Rock completion is discussed, not re-scored.
- **Document everything.** The conversation is recorded and kept for future reference. Git history is the audit trail.

## Process

### Mode: Facilitate

Use when conducting a quarterly conversation with a specific person.

#### Step 1: Setup

1. **Identify the person and manager.** Ask for the person's name if not provided. Ask who is conducting the conversation (the manager).

2. **Determine the quarter.** Default to the current quarter. If near a quarter boundary, ask: "This conversation is for which quarter?"

3. **Check for existing conversation.** Look for `data/conversations/YYYY-QN/firstname-lastname.md`.
   - **Exists:** Ask: "A conversation already exists for [person] in [quarter]. Open it to review, or start a new one?"
   - **New:** Continue with Step 2.

4. **Gather context.** Read these files (silently — don't dump raw data to the user):
   - `data/vision.md` — extract Core Values list
   - `data/accountability.md` — find the person's seat(s) and their manager
   - `data/rocks/QUARTER/` — find Rocks owned by this person
   - `data/people/firstname-lastname.md` — load People Analyzer evaluation if it exists

5. **Create the quarter directory** if it doesn't exist: `data/conversations/YYYY-QN/`

Display a brief preparation summary:

```
Quarterly Conversation — [Person Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Manager: [Manager Name]
Quarter: YYYY-QN
Seat: [From accountability.md]
Core Values: [List from vision.md]
Rocks this quarter: [Count] ([List titles])
People Analyzer: [Status from people/ file, or "No evaluation on file"]

Let's walk through the 5-point agenda.
```

#### Step 2: Section 1 — Core Values Alignment

Read Core Values from `data/vision.md`. Display them and ask the manager to discuss how the person is living each one.

If a People Analyzer evaluation exists (`data/people/firstname-lastname.md`), show the most recent ratings as a reference point:

```
People Analyzer reference (last evaluated: 2026-01-15):
  Integrity: +
  Innovation: +/-
  Transparency: +
```

For each Core Value, prompt: "How is [person] living **[Core Value]**? Rate: `+`, `+/-`, or `-`"

Record ratings in the conversation file. Calculate `core_values_rating` as the count of `+` ratings.

**Important:** This is a reference discussion, not a re-evaluation. If the ratings differ significantly from the People Analyzer, note it: "These ratings differ from the People Analyzer. Would you like to update the People Analyzer after this conversation?"

#### Step 3: Section 2 — GWC

Read the person's seat from `data/accountability.md`. For each seat they hold, ask:

1. **Get it?** "Does [person] truly understand the [seat] role?" (yes/no + notes)
2. **Want it?** "Does [person] genuinely want to do [seat] work?" (yes/no + notes)
3. **Capacity?** "Does [person] have the capacity to excel at [seat]?" (yes/no + notes)

Display the result:

```
GWC — [Person] as [Seat]:
  Get it:     ✓ Yes
  Want it:    ✓ Yes
  Capacity:   ✓ Yes

  Right seat? Yes
```

Set `gwc_status`:
- All three yes = `pass`
- Any no = `fail`
- Not yet discussed = `evaluating`

If GWC differs from the People Analyzer, note it for follow-up.

#### Step 4: Section 3 — Rocks Review

Read all Rocks from `data/rocks/QUARTER/` where `owner` matches the person.

If no Rocks found: Display "No Rocks assigned this quarter." Set `rocks_completion_rate: null`.

If Rocks exist, display:

```
Rocks — [Person], [Quarter]:
  Launch Beta Program: complete ✓
  Partner Outreach: on_track (2/3 milestones done)
  Redesign Onboarding: dropped ✗
```

Prompt: "How do you feel about your Rock performance this quarter? Any context on the results?"

Calculate `rocks_completion_rate`: `(complete / total) * 100`, rounded to nearest integer. Include only `complete` and `dropped` statuses in the calculation — ignore `on_track` and `off_track` (those are mid-quarter Rocks still in progress).

**Important:** Don't re-score Rocks here. Use the status from the Rock files. If the quarter hasn't ended yet and Rocks are still `on_track`/`off_track`, note: "Rocks are still in progress — final scoring happens at quarter end with ceos-rocks."

#### Step 5: Section 4 — Role Expectations

Prompt the manager and direct report to discuss:

1. **Clarity:** "Are the roles and responsibilities for the [seat] clearly defined?"
2. **Delivery:** "Is [person] meeting those expectations?"
3. **Gaps:** "Are there areas where expectations aren't being met — on either side?"

Record responses. This section is qualitative — no scoring.

#### Step 6: Section 5 — Feedback Both Ways

This is the most important section. Both sides share openly.

**Manager → Direct Report:**
- "What's working well about [person]'s performance?"
- "What needs improvement?"

**Direct Report → Manager:**
- "What's working well about your relationship with your manager?"
- "What do you need from your manager that you're not getting?"

Record both sides. Emphasize that this is a dialogue.

#### Step 7: Action Items

Ask: "What action items come out of this conversation?"

Record 1-3 specific, actionable items with owners.

#### Step 8: Save the Conversation

1. **Show the complete conversation file** before writing.
2. Ask: "Save this quarterly conversation?"
3. Write to `data/conversations/YYYY-QN/firstname-lastname.md`.
4. Update frontmatter: `core_values_rating`, `gwc_status`, `rocks_completion_rate`, `date`.
5. Remind: "Run `git commit` to save the conversation."

If the People Analyzer ratings differed, offer: "Would you like to update the People Analyzer for [person]? This would update `data/people/firstname-lastname.md`."

---

### Mode: Quick

Use for a 5-5-5 quick check-in — a lightweight 15-minute conversation between a manager and a direct report. Triggered by phrases like "5-5-5 with [person]", "quick quarterly check-in", or "quick conversation with [person]".

#### Step 1: Setup

1. **Identify the person.** If not specified, ask: "Who is the 5-5-5 with?"
2. **Determine the quarter.** Default to the current quarter.
3. **Check for existing quick file.** Look for `data/conversations/YYYY-QN/firstname-lastname-quick.md`.
   - If exists: Warn: "A 5-5-5 already exists for [person] this quarter. Overwrite, or open the existing one?"
4. **Gather context** (read these files, continue if any are missing):
   - `data/vision.md` — Core Values list
   - `data/accountability.md` — Person's seat and reporting structure
   - `data/rocks/YYYY-QN/` — Person's Rocks for the quarter
   - `data/people/firstname-lastname.md` — Latest People Analyzer evaluation (if exists)
5. **Display prep summary:**

```
5-5-5 Quick Check-In — [Full Name]
Quarter: YYYY-QN
Seat: [Seat from accountability chart]
Manager: [Reporting to]

Core Values: [List from vision.md]
Current Rocks: [List or "No Rocks this quarter"]
Latest People Analyzer: [Summary or "No evaluation on file"]
```

#### Step 2: Employee Speaks (5 min)

Prompt the user to capture what the employee shares. Guide with these three topics:

1. **Core Values:** "How does [person] feel about living the Core Values?"
2. **Rocks:** "How are their Rocks going?" (Reference specific Rocks from data if available.)
3. **Role (GWC):** "How do they feel about their seat — do they Get It, Want It, have the Capacity?"

Record responses in the Employee Speaks section. Keep it conversational — this is the employee's time to talk.

#### Step 3: Manager Speaks (5 min)

Prompt the user (as manager) to share their perspective:

1. **Performance:** "How is [person] doing overall?"
2. **Wins:** "What's going well? What should be recognized?"
3. **Concerns:** "Any issues or areas that need attention?"

Record responses in the Manager Speaks section. The manager shares observations, not evaluations.

#### Step 4: Together (5 min)

Prompt both to agree on next steps:

1. **Next Steps:** "What actions come out of this check-in?"
2. **Commitments:** "What will each person do before the next check-in?"

Record agreed-upon items. Keep it to 2-3 specific, actionable commitments.

#### Step 5: Save

1. **Build the file** using `templates/quarterly-quick.md`, filling in all sections.
2. **Show the complete file** before writing.
3. Ask: "Save this 5-5-5 check-in?"
4. Write to `data/conversations/YYYY-QN/firstname-lastname-quick.md`.
5. Remind: "Run `git commit` to save the check-in."

---

### Mode: Schedule

Use when planning which quarterly conversations need to happen.

#### Step 1: Determine the Quarter

Default to the current quarter. Ask if the user wants a different quarter.

#### Step 2: Read the Accountability Chart

Read `data/accountability.md` to identify:
- All filled seats (person + seat name)
- Reporting structure (who reports to whom)

If the file doesn't exist or has no structure: "No accountability chart found. Create one first with `ceos-vto` or manually at `data/accountability.md`."

#### Step 3: Check Existing Conversations

Read `data/conversations/YYYY-QN/` to find which conversations have already been completed this quarter. Check for both full conversations (`firstname-lastname.md`) and quick check-ins (`firstname-lastname-quick.md`).

#### Step 4: Generate the Schedule

Display a table of all needed conversations:

```
Quarterly Conversations — YYYY-QN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Manager    | Direct Report | Seat        | Status       | Date       |
|------------|---------------|-------------|--------------|------------|
| Brad       | Sarah Chen    | Integrator  | Done         | 2026-03-10 |
| Brad       | Mike Torres   | VP Sales    | Done + Quick | 2026-03-14 |
| Brad       | Alex Kim      | VP Eng      | Quick only   | 2026-02-14 |
| Sarah      | Jamie Lee     | Marketing   | Pending      |            |

Progress: 2/4 full conversations complete (50%)
Note: Alex Kim has a 5-5-5 but still needs a full Quarterly Conversation.
```

**Status values:**
- `Done` — Full conversation completed
- `Quick only` — Only a 5-5-5 check-in exists (flag: still needs a full conversation)
- `Done + Quick` — Both full conversation and 5-5-5 exist
- `Pending` — No conversation of either type

**Edge cases:**
- **Empty seats:** Flag: "📋 [Seat Name] — empty seat (no conversation needed)"
- **Departed people:** If `data/people/firstname-lastname.md` has `departed: true`, flag: "⚠️ [Person] departed — skip conversation?"
- **Self-conversation (Visionary/Integrator):** Include with note: "Self-reflection conversation"
- **Person with multiple seats:** List once with all seats noted
- **Quick only:** Flag: "📋 [Person] has a 5-5-5 check-in but still needs a full Quarterly Conversation."

#### Step 5: Offer to Start

Ask: "Would you like to start a conversation with someone from this list? (Full or 5-5-5?)"

If full, transition to Facilitate mode. If 5-5-5, transition to Quick mode.

---

### Mode: Review

Use when reviewing past quarterly conversations for a person or the full team.

#### Step 1: Determine Scope

Ask: "Review conversations for a specific person, or the full team?"

- **Specific person:** Ask for the name
- **Full team:** Show all conversations

Also ask for the quarter, or default to the current quarter. Offer: "Show current quarter, or all quarters?"

#### Step 2: Read Conversation Files

**For a specific person:** Read all files matching `data/conversations/*/firstname-lastname.md` and `data/conversations/*/firstname-lastname-quick.md` across quarters.

**For the full team:** Read all files from `data/conversations/YYYY-QN/` (both full and quick).

If no files found: "No quarterly conversations found. Run a Facilitate or Quick conversation to get started."

**Backward compatibility:** Files without a `type` frontmatter field are treated as `full`.

#### Step 3: Display Summary

**For a specific person (across quarters):**

```
Quarterly Conversations — Brad Feld
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Quarter | Type  | Manager | CV Rating | GWC    | Rocks Rate | Date       |
|---------|-------|---------|-----------|--------|------------|------------|
| 2026-Q1 | Full  | Daniel  | 5/5       | Pass   | 80%        | 2026-03-15 |
| 2026-Q1 | Quick | Daniel  | --        | --     | --         | 2026-02-14 |
| 2025-Q4 | Full  | Daniel  | 4/5       | Pass   | 100%       | 2025-12-20 |
| 2025-Q3 | Full  | Daniel  | 4/5       | Pass   | 67%        | 2025-09-18 |

Trend: Core Values stable, Rock completion improving
```

**For the full team (one quarter):**

```
Quarterly Conversations — 2026-Q1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Person      | Type  | Manager | CV Rating | GWC    | Rocks Rate | Date       |
|-------------|-------|---------|-----------|--------|------------|------------|
| Brad Feld   | Full  | Daniel  | 5/5       | Pass   | 80%        | 2026-03-15 |
| Sarah Chen  | Full  | Brad    | 4/5       | Pass   | 100%       | 2026-03-12 |
| Sarah Chen  | Quick | Brad    | --        | --     | --         | 2026-02-14 |
| Mike Torres | Full  | Brad    | 3/5       | Fail   | 50%        | 2026-03-14 |

Team summary: 2/3 GWC passing, average Rock rate 77%
```

**Quick entries:** Show `--` for CV Rating, GWC, and Rocks Rate columns (not scored in 5-5-5 format).

#### Step 4: Drill Down

Ask: "Want to view the full conversation for anyone?"

If yes, read and display the complete conversation file.

#### Step 5: Flag Issues

Highlight:
- **GWC failures:** "⚠️ [Person] — GWC fail. Discuss at next L10."
- **Low Rock completion:** If below 80%: "📉 [Person] — Rock completion below 80%."
- **Stale conversations:** If current quarter has no conversation and > 60 days into the quarter: "📅 [Person] — no conversation yet this quarter."
- **Quick only:** If a person has only 5-5-5 check-ins and no full conversation this quarter: "📋 [Person] — only 5-5-5 check-ins this quarter. Schedule a full Quarterly Conversation."

## Output Format

**Facilitate:** Walk through each of the 5 sections with prompts. Show the complete file before saving. Full conversation — 30-60 minutes.

**Quick:** Walk through the 3 time-boxed sections (Employee Speaks, Manager Speaks, Together). Brief, conversational output — fits on one screen. 15 minutes.

**Schedule:** Table of all needed conversations with completion status. Shows both full and quick conversations. Flags persons with only quick check-ins.

**Review:** Summary table with key metrics and Type column. Quick entries show `--` for scoring columns. Offer drill-down.

## Guardrails

- **Always show the complete file before writing.** Never create or modify a conversation file without showing it and getting approval.
- **Core Values come from vision.md.** Always read Core Values from `data/vision.md` — never ask the user to list them.
- **Cross-reference, don't duplicate.** Read People Analyzer ratings and Rock scores from their source files. Don't ask the user to re-enter data that's already on file.
- **One full conversation per person per quarter.** If a full conversation already exists, warn before creating a second one. Allow it (sometimes conversations need to be re-done), but make sure it's intentional. Multiple 5-5-5 quick check-ins per quarter are fine.
- **Quick supplements, doesn't replace.** A 5-5-5 check-in is a lightweight touchpoint between full Quarterly Conversations. It does not substitute for the full conversation. If a person only has a 5-5-5 this quarter and no full conversation, flag it in Schedule mode.
- **Keep quick check-ins quick.** The 5-5-5 should take ~15 minutes. If the conversation expands beyond the three sections, suggest scheduling a full Quarterly Conversation instead of extending the 5-5-5.
- **No formal scoring in quick mode.** Quick check-ins do not produce Core Values ratings, GWC pass/fail, or Rock completion percentages. All scoring fields are `null`. This is intentional — the 5-5-5 is informal by design.
- **Quarterly cadence.** If no conversation has been conducted for a person in > 120 days, flag it in Schedule and Review modes: "📅 Overdue — last conversation was [date]."
- **Two-way conversation.** Always prompt for both manager and direct report feedback in Section 5 (full) or all three sections (quick). Don't let it become one-sided.
- **Reference, don't re-evaluate.** This conversation references People Analyzer and Rock data — it doesn't replace those tools. If the user wants to change a People Analyzer rating, point them to `ceos-people`.
- **Sensitive data warning.** On first use in a session, remind the user: "Quarterly conversations contain sensitive performance data. Ensure your CEOS repo is private."
- **Respect the agenda.** Walk through all 5 sections (full) or all 3 sections (quick) in order. Don't skip sections even if the user tries to rush — each one serves a purpose. But keep each section focused and time-efficient.
- **Don't auto-invoke skills.** When conversation results suggest updating the People Analyzer or creating an issue, offer the option but let the user decide. Say "Would you like to update the People Analyzer?" rather than doing it automatically.

## Integration Notes

### V/TO (ceos-vto)

- **Read:** `ceos-quarterly` reads Core Values from `data/vision.md` for the Core Values Alignment section (Section 1) of the conversation.

### People Analyzer (ceos-people)

- **Read:** `ceos-quarterly` reads People Analyzer evaluations from `data/people/` as reference points for Core Values and GWC discussions. If ratings differ significantly, the skill suggests updating via `ceos-people`.

### Rocks (ceos-rocks)

- **Read:** `ceos-quarterly` reads Rock files from `data/rocks/[quarter]/` to show the person's Rock status during Section 3 (Rocks Review). It does not modify Rock files.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-quarterly` reads `data/accountability.md` to identify the person's seat(s) and reporting structure for GWC evaluation and scheduling.

### To-Dos (ceos-todos)

- **Related:** Action items from quarterly conversations should be created as To-Dos via `ceos-todos` Create mode with `source: quarterly`.

### Write Principle

**Only `ceos-quarterly` writes to `data/conversations/`.** Other skills reference conversation data for context. The quarterly conversation file is the sole record of each manager-direct report check-in.
