---
name: ceos-annual
description: Use when conducting, reviewing, or planning the annual planning session
file-access: [data/annual/, templates/annual-planning.md, data/vision.md, data/rocks/, data/scorecard/, data/issues/, data/accountability.md, data/people/]
tools-used: [Read, Write, Glob]
---

# ceos-annual

Facilitate the EOS Annual Planning session — the formal year-end process (typically a 2-day offsite) where the leadership team refreshes the V/TO, reviews the outgoing year, sets the new 1-Year Plan, and establishes Q1 Rocks. This is the most comprehensive EOS meeting of the year.

## When to Use

- "Run annual planning" or "annual planning session"
- "Plan next year" or "let's plan for 2027"
- "Review 2026" or "year in review"
- "Refresh our vision" or "update the V/TO for the year"
- "Annual offsite" or "strategic planning session"
- Any end-of-year or start-of-year strategic planning discussion

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/annual/YYYY-planning.md` | Annual planning session notes (one per year) |
| `data/vision.md` | V/TO document (read and update during V/TO Refresh) |
| `data/rocks/YYYY-QN/` | Rock files by quarter (read for year-in-review scoring) |
| `data/scorecard/weeks/` | Weekly scorecard data (read for trend analysis) |
| `data/scorecard/metrics.md` | Scorecard metric definitions (reference for updates) |
| `data/issues/open/` | Open issues (read for issues sweep) |
| `data/issues/solved/` | Solved issues (count for year summary) |
| `data/accountability.md` | Accountability Chart (read for org checkup) |
| `data/people/` | People Analyzer evaluations (read for org checkup) |
| `templates/annual-planning.md` | Template for new annual planning files |

### Annual Planning Agenda

The full annual planning session follows a 7-section agenda:

| # | Section | Focus |
|---|---------|-------|
| 1 | Year in Review | Score Q4 Rocks, review annual Scorecard trends, celebrate wins |
| 2 | V/TO Refresh | Update 3-Year Picture, set new 1-Year Plan with measurable goals |
| 3 | Issues Sweep | Clear the long-term issues list via IDS |
| 4 | Organizational Checkup | Review Accountability Chart, run People Analyzer |
| 5 | Set Q1 Rocks | First quarter's Rocks aligned to the new 1-Year Plan |
| 6 | Set Scorecard | Review and update weekly measurables for the new year |
| 7 | Conclude | Key decisions, cascading messages, next steps |

### Year Determination

When determining the planning year:
- If run in Q4 (Oct-Dec): "Next year" is current year + 1. The "outgoing year" is the current year.
- If run in Q1 (Jan-Mar): "Next year" is the current year. The "outgoing year" is current year - 1.
- If run mid-year (Q2-Q3): Warn that annual planning typically happens at Q4/Q1 boundary. Ask which year to plan for.

### Key EOS Principles

- **Annual Planning reviews the FULL V/TO** — not just the 1-Year Plan. All 8 sections get reviewed.
- **10-Year Target and Core Focus rarely change** (if ever). Confirm they still resonate, but don't pressure updates.
- **3-Year Picture updates** to reflect progress and changing conditions.
- **1-Year Plan is entirely new** each year with 3-7 measurable goals.
- **Q1 Rocks are set during annual planning**, aligned to the new 1-Year Plan.
- **All leadership team members must attend.** If someone is missing, note it but proceed.

## Process

### Mode: Plan

Use when conducting the full annual planning session with the structured 7-section agenda.

#### Step 1: Setup

1. **Determine the planning year.** Ask if not clear from context. Follow the Year Determination rules above.

2. **Check for existing planning file.** Look for `data/annual/YYYY-planning.md`.
   - **Exists:** Ask: "Annual planning for YYYY already exists. Open it to review, append notes, or start fresh?"
   - **New:** Continue with Step 2.

3. **Gather session details:**
   - Attendees (all leadership team members should be present)
   - Location (office, offsite, etc.)
   - Date (default to today)

4. **Gather context.** Read these files silently:
   - `data/vision.md` — current V/TO state
   - `data/rocks/` — all quarters for the outgoing year
   - `data/scorecard/weeks/` — scorecard data for the year
   - `data/issues/open/` — open issues list
   - `data/accountability.md` — current org structure
   - `data/people/` — People Analyzer evaluations

5. **Create the year directory** if it doesn't exist: `data/annual/`

Display a preparation summary:

```
Annual Planning — [Year]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: [Date]
Attendees: [Names]
Location: [Location]

Data loaded:
  V/TO: [Last updated date]
  Rocks: [Count] across [N] quarters
  Scorecard: [N] weeks of data
  Open issues: [Count]
  People evaluations: [Count]

Let's walk through the 7-section agenda.
```

#### Step 2: Section 1 — Year in Review

1. **Score Q4 Rocks.** Read all Rocks from `data/rocks/YYYY-Q4/`. Display current status for each Rock. For any Rocks still `on_track` or `off_track`, ask: "Complete or incomplete?" Update status to `complete` or `dropped`.

   Calculate Q4 completion rate: `(complete / total) * 100`.

   If no Q4 Rock files exist: "No Q4 Rocks on file. Skip Q4 scoring, or enter scores manually?"

2. **Annual Rock Summary.** Read Rocks from all four quarters of the outgoing year. Display a summary table:

   ```
   Annual Rock Summary — YYYY
   ━━━━━━━━━━━━━━━━━━━━━━━━━━
   | Quarter | Total | Complete | Rate |
   |---------|-------|----------|------|
   | Q1      | 5     | 4        | 80%  |
   | Q2      | 6     | 5        | 83%  |
   | Q3      | 5     | 3        | 60%  |
   | Q4      | 6     | 5        | 83%  |
   | Year    | 22    | 17       | 77%  |
   ```

   If below 80% annual average: "Below the 80% target. Discuss: Were Rocks too ambitious, or were there execution issues?"

3. **Scorecard Trends.** Read scorecard files for the year. Identify which metrics consistently hit or missed goals. Display a summary of trends.

   If no scorecard data exists: "No scorecard data for YYYY. Skip trends."

4. **Celebrate Wins.** Prompt: "What were the biggest wins and accomplishments this year?" Record responses.

Record all Year in Review data in the planning file.

#### Step 3: Section 2 — V/TO Refresh

Walk through each V/TO section from `data/vision.md`:

1. **Core Values:** Display current values. Ask: "Do these still resonate? Any changes?" Note: Core Values should rarely change.

2. **Core Focus:** Display purpose and niche. Ask: "Still accurate?" Note: Core Focus should rarely change.

3. **10-Year Target:** Display current target. Ask: "Still the right big goal?" Note: This shifts slowly.

4. **3-Year Picture:** Display current state. Ask: "What's changed? What should the 3-Year Picture look like now?" This section updates to reflect progress.

5. **1-Year Plan:** This is entirely new each year. Ask: "What are the 3-7 measurable goals for [next year]?" Walk through each goal, ensuring it has a specific measurable target.

6. **Marketing Strategy:** Display target market, 3 Uniques, proven process. Ask: "Any updates?"

**Important:** Record proposed V/TO changes in the planning file. Actual updates to `data/vision.md` should be done via `ceos-vto` after the session, or the user can approve inline updates during this step. If the user wants to update vision.md now, show the diff and ask for approval before writing.

#### Step 4: Section 3 — Issues Sweep

1. Read all open issues from `data/issues/open/`.
2. Display the list with age (days since created).
3. Ask: "Which issues should we tackle today? Add any new long-term issues?"
4. For selected issues, run a quick IDS:
   - **Identify** the real issue
   - **Discuss** perspectives
   - **Solve** with an action item, owner, and due date
5. Record IDS results in the planning file.

**Note:** For issues that need full IDS treatment, reference `ceos-ids` for creating formal issue files.

#### Step 5: Section 4 — Organizational Checkup

1. Read `data/accountability.md` for the current Accountability Chart.
2. Display all seats with current owners.
3. Ask: "Are all seats filled with the right people? Any structural changes needed?"
4. If People Analyzer evaluations exist in `data/people/`, reference the latest ratings:

   ```
   People Summary:
     Brad: Core Values 5/5, GWC Pass ✓
     Sarah: Core Values 4/5, GWC Pass ✓
     Mike: Core Values 3/5, GWC Evaluating ⚠️
   ```

5. Discuss any concerns. Record structural changes and people decisions.

**Note:** For formal People Analyzer updates, reference `ceos-people`.

#### Step 6: Section 5 — Set Q1 Rocks

1. Reference the new 1-Year Plan goals (from Step 3).
2. Ask: "What Q1 Rocks will drive progress on these goals?"
3. For each proposed Rock, collect: title, owner, which 1-Year goal it aligns to.
4. Validate:
   - **3-7 Rocks per person.** Flag if outside range.
   - **Alignment.** Each Rock should connect to a 1-Year Plan goal.
5. Record in the planning file.

**Note:** Create individual Rock files using `ceos-rocks` after this session. The planning file captures the decisions; the Rock files are the operational artifacts.

#### Step 7: Section 6 — Set Scorecard

1. Read current Scorecard metrics from `data/scorecard/metrics.md` (if it exists).
2. Display current metrics.
3. Ask three questions:
   - "Which metrics do we keep for next year?"
   - "What new metrics should we add?"
   - "What metrics should we remove?"
4. Record decisions in the planning file.

**Note:** Update the Scorecard metrics file using `ceos-scorecard` after this session.

#### Step 8: Section 7 — Conclude

1. **Key Decisions:** Summarize the major decisions made during the session.
2. **Cascading Messages:** Ask: "What needs to be communicated to the rest of the organization?"
3. **Action Items:** Compile all action items from all sections with owners and due dates.
4. **Next Steps:** List follow-up tasks (commit V/TO updates, create Rock files, update Scorecard, communicate decisions).

#### Step 9: Save the Planning File

1. **Show the complete planning file** before writing.
2. Ask: "Save this annual planning session?"
3. Write to `data/annual/YYYY-planning.md`.
4. Remind: "Run `git commit` to save the planning session."
5. List follow-up actions:
   - "Update vision.md with V/TO changes using `ceos-vto`" (if not done inline)
   - "Create Q1 Rock files using `ceos-rocks`"
   - "Update Scorecard metrics using `ceos-scorecard`"

---

### Mode: Review Year

Use when analyzing the outgoing year's performance without running a full planning session.

#### Step 1: Determine the Year

Ask which year to review. Defaults:
- If run in Q1 (Jan-Mar): Default to previous year (outgoing year)
- If run in Q4 (Oct-Dec): Default to current year (year almost complete)
- Otherwise: Ask which year

#### Step 2: Load Rock Data

Read all Rock files from `data/rocks/YYYY-Q1/`, `data/rocks/YYYY-Q2/`, `data/rocks/YYYY-Q3/`, `data/rocks/YYYY-Q4/`.

For each quarter, calculate:
- Total Rocks
- Complete count (status = `complete`)
- Completion rate: `(complete / total) * 100`

If a quarter has no Rock files: "No Rocks on file for YYYY-QN."

Display the annual summary:

```
Year in Review — YYYY Rock Performance
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Quarter | Total | Complete | Dropped | Rate |
|---------|-------|----------|---------|------|
| Q1      | 5     | 4        | 1       | 80%  |
| Q2      | 6     | 5        | 1       | 83%  |
| Q3      | 5     | 3        | 2       | 60%  |
| Q4      | 6     | 5        | 1       | 83%  |
| Year    | 22    | 17       | 5       | 77%  |

Annual target: 80%+
```

Also display per-person breakdown:

```
By Owner:
  Brad: 8 Rocks, 6 complete (75%)
  Daniel: 7 Rocks, 6 complete (86%)
  Sarah: 7 Rocks, 5 complete (71%)
```

#### Step 3: Scorecard Trends

Read all scorecard files from `data/scorecard/weeks/` that fall within the year.

For each metric, calculate:
- Average value across all weeks
- Hit rate (percentage of weeks at or above goal)
- Trend direction (improving, stable, declining)

Display summary:

```
Scorecard Trends — YYYY
━━━━━━━━━━━━━━━━━━━━━━━

| Metric          | Avg   | Goal  | Hit Rate | Trend     |
|-----------------|-------|-------|----------|-----------|
| Weekly Revenue  | \$48K  | \$50K  | 65%      | Improving |
| New Customers   | 8     | 10    | 45%      | Stable    |
| NPS             | 74    | 70    | 85%      | Improving |
```

If no scorecard data: "No scorecard data for YYYY."

#### Step 4: Issues Resolved

Count solved issues from `data/issues/solved/` with dates within the year. Also count current open issues.

```
Issues — YYYY
━━━━━━━━━━━━━

Resolved: 23 issues
Open: 8 issues remaining
```

#### Step 5: Year Summary

Display a consolidated year report:

```
Year Summary — YYYY
━━━━━━━━━━━━━━━━━━━

Rock Completion: 77% (target 80%)
Scorecard Hit Rate: 65% average across metrics
Issues Resolved: 23
Issues Remaining: 8

Highlights:
  ✓ [Strongest quarter for Rocks]
  ✓ [Best-performing Scorecard metric]
  ⚠️ [Area needing improvement]
```

Ask: "Would you like to save this review to `data/annual/YYYY-planning.md`?"

---

### Mode: Refresh V/TO

Use when walking through V/TO sections for annual updates without the full planning session.

#### Step 1: Read Current V/TO

Read `data/vision.md`. If the file doesn't exist: "No V/TO found. Run `setup.sh init` first, or create one with `ceos-vto`."

Display a summary of the current V/TO state:

```
V/TO Status — Last updated: YYYY-MM-DD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Section             | Status                          |
|---------------------|---------------------------------|
| Core Values         | [Count] values defined          |
| Core Focus          | [Purpose + Niche summary]       |
| 10-Year Target      | [Target summary]                |
| 3-Year Picture      | [Key points]                    |
| 1-Year Plan         | [Goal count] goals              |
| Marketing Strategy  | [Target market summary]         |
```

#### Step 2: Select Sections

Ask: "Which V/TO sections do you want to refresh?"

Options:
- **All sections** — Walk through every section in order
- **Forward-looking only** — 3-Year Picture, 1-Year Plan, Marketing Strategy (most commonly updated)
- **Specific section** — Choose one to focus on

#### Step 3: Walk Through Each Selected Section

For each section:

1. **Display current content** in full.
2. **Prompt for updates:**
   - Core Values / Core Focus / 10-Year Target: "This should rarely change. Confirm it still resonates, or discuss changes?"
   - 3-Year Picture: "What's changed? What should the 3-Year Picture look like now?"
   - 1-Year Plan: "What are the 3-7 measurable goals for [year]?" (entirely new each year)
   - Marketing Strategy: "Any updates to target market, 3 Uniques, proven process, or guarantee?"
3. **Draft the update** with the user's input.
4. **Show the diff** — before/after for the changed section.
5. **Ask for approval** before writing.

#### Step 4: Write Updates

After all sections are reviewed:

1. Show a summary of all changes.
2. Ask: "Apply these changes to `data/vision.md`?"
3. Write the updated file.
4. Update the "Last updated" date.
5. Remind: "Run `git commit` to save the V/TO updates."

#### Step 5: Follow-Up

After V/TO is refreshed, offer:
- "Would you like to check Rock alignment against the updated 1-Year Plan?"
- "Would you like to run a full annual planning session?"

## Output Format

**Plan:** Progressive display of each agenda section during the session. Show the complete planning file before saving.

**Review Year:** Summary tables with Rock completion rates (per quarter and per person), Scorecard trends, and issues count. Offer to save the review.

**Refresh V/TO:** Section-by-section display with diffs for any changes. Summary of all changes before writing.

## Guardrails

- **Always show the complete file before writing.** Never create or modify a planning file without showing it and getting approval.
- **Cross-reference existing data.** Read Rock scores, Scorecard numbers, and issues from their source files. Don't ask users to re-enter data that's already tracked.
- **Don't auto-invoke other skills.** Mention `ceos-vto`, `ceos-rocks`, `ceos-scorecard`, `ceos-ids`, and `ceos-people` as follow-up tools, but let the user decide when to use them.
- **Respect the planning cadence.** If annual planning is run mid-year or twice in one year, flag it: "Annual planning typically runs at the Q4/Q1 boundary. Continue anyway?" Allow it — some companies do mid-year strategic resets.
- **Annual Planning reviews the FULL V/TO.** In Plan mode, walk through all sections. Remind that 10-Year Target and Core Focus should rarely change, but they still get reviewed.
- **One file per year.** If a planning file already exists for the year, warn before creating a second one. Allow it (sessions sometimes need to be re-run), but make sure it's intentional.
- **All leadership must attend.** If the attendees list seems incomplete compared to `data/accountability.md`, note it: "Some leadership team members may be missing from the attendee list."
- **Show diffs for V/TO changes.** When modifying `data/vision.md` (in Plan mode step 3 or Refresh V/TO mode), always show before/after for each section and get approval.
- **Don't skip sections in Plan mode.** Walk through all 7 agenda sections in order. Each serves a purpose. But keep each section focused — this is a full-day session, not a lecture.
- **Sensitive strategic data warning.** On first use in a session, remind the user: "Annual planning notes contain sensitive strategic data. Ensure your CEOS repo is private."
- **1-Year Plan alignment.** When setting Q1 Rocks (Section 5), verify each Rock connects to a 1-Year Plan goal. Flag any that don't align.

## Integration Notes

### V/TO (ceos-vto)

- **Read/Write:** `ceos-annual` reads `data/vision.md` for the current V/TO state and may update it during the V/TO Refresh section (Section 2). Inline updates to `data/vision.md` are allowed with user approval; alternatively, formal updates can be deferred to `ceos-vto` after the session.

### Rocks (ceos-rocks)

- **Read/Write:** `ceos-annual` reads Rock files from all quarters for the year-in-review scoring and creates Q1 Rock decisions during Section 5. Formal Rock file creation should be done via `ceos-rocks` after the session.

### Scorecard (ceos-scorecard)

- **Read:** `ceos-annual` reads scorecard data from `data/scorecard/weeks/` for trend analysis during the Year in Review (Section 1). Scorecard metric updates (Section 6) are recorded in the planning file; formal updates to `data/scorecard/metrics.md` should be done via `ceos-scorecard`.

### People Analyzer (ceos-people)

- **Read:** `ceos-annual` reads People Analyzer evaluations from `data/people/` during the Organizational Checkup (Section 4). Formal People Analyzer updates should be done via `ceos-people`.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-annual` reads `data/accountability.md` during the Organizational Checkup (Section 4) to review the org structure and identify empty or misaligned seats.

### IDS (ceos-ids)

- **Read:** `ceos-annual` reads open issues from `data/issues/open/` and solved issues from `data/issues/solved/` during the Issues Sweep (Section 3). Formal issue creation and resolution should be done via `ceos-ids`.

### Orchestration Principle

`ceos-annual` is the most comprehensive orchestrator — it reads data from nearly all other skills during the planning session. The annual planning file at `data/annual/YYYY-planning.md` captures decisions; individual skills handle the operational artifacts (Rock files, scorecard updates, V/TO changes, etc.).
