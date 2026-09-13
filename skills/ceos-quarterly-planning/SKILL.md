---
name: ceos-quarterly-planning
description: Use when conducting or reviewing a quarterly planning session for the leadership team
file-access: [data/quarterly/, templates/quarterly-planning.md, data/rocks/, data/scorecard/, data/vision.md, data/issues/, data/accountability.md]
tools-used: [Read, Write, Glob]
---

# ceos-quarterly-planning

Facilitate the EOS Quarterly Planning Session — the structured half-day meeting where the leadership team scores outgoing Rocks, reviews Scorecard trends, confirms vision alignment, tackles issues via IDS, and sets the next quarter's Rocks. This is "quarterly pulsing" — the bridge between weekly L10 meetings and the Annual Planning session.

## When to Use

- "Run quarterly planning" or "quarterly planning session"
- "Plan next quarter" or "let's plan Q2"
- "Score rocks and plan next quarter"
- "End of quarter review and planning"
- "Quarterly session" or "quarterly pulse"
- "Review the quarter and set new rocks"
- Any leadership team meeting focused on transitioning between quarters

**Not for:** 1-on-1 quarterly conversations (use `ceos-quarterly`), annual planning with V/TO refresh (use `ceos-annual`), or weekly meetings (use `ceos-l10`).

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/quarterly/YYYY-QN-planning.md` | Quarterly planning session notes (one per quarter) |
| `data/rocks/YYYY-QN/` | Rock files for each quarter (read for scoring and reference) |
| `data/scorecard/weeks/` | Weekly scorecard data (read for 13-week trend analysis) |
| `data/scorecard/metrics.md` | Scorecard metric definitions (reference for targets) |
| `data/vision.md` | V/TO document (read 1-Year Plan for Rock alignment) |
| `data/issues/open/` | Open issues (read for IDS sweep) |
| `data/issues/solved/` | Solved issues (count for quarter summary) |
| `templates/quarterly-planning.md` | Template for new quarterly planning files |
| `data/accountability.md` | Accountability Chart (seat owners for Rock-owner alignment) |

### Planning File Format

Each quarterly planning session is a markdown file at `data/quarterly/YYYY-QN-planning.md` with YAML frontmatter:

```yaml
quarter: "2026-Q1"
date: "2026-03-28"
attendees: "Brad, Daniel, Sarah"
location: "Office"
```

### Quarter Format

Quarters follow `YYYY-QN` format: `2026-Q1`, `2026-Q2`, `2026-Q3`, `2026-Q4`.

To determine the current quarter from today's date:
- Jan-Mar = Q1, Apr-Jun = Q2, Jul-Sep = Q3, Oct-Dec = Q4

### Quarterly Planning Agenda

The full quarterly planning session follows a 6-section agenda:

| # | Section | Focus | Time |
|---|---------|-------|------|
| 1 | Score Outgoing Rocks | Score the outgoing quarter's Rocks, celebrate wins | 30 min |
| 2 | Scorecard Review | Review 13-week trends, identify patterns | 20 min |
| 3 | V/TO Check | Confirm vision alignment, review 1-Year Plan progress | 20 min |
| 4 | IDS | Tackle long-term issues via Identify, Discuss, Solve | 60 min |
| 5 | Set Next Quarter Rocks | Define next quarter's Rocks aligned to 1-Year Plan | 45 min |
| 6 | Conclude | Key decisions, cascading messages, action items | 15 min |

### Quarter Determination

When determining which quarter to plan:

- **Last 2-3 weeks of a quarter** (typical): The "outgoing quarter" is the current quarter. The "next quarter" is the upcoming one. Example: Running in mid-March → outgoing = Q1, next = Q2.
- **First 2 weeks of a quarter**: Ask: "Planning for outgoing quarter (QN-1) or current quarter (QN)?" Teams sometimes run quarterly planning slightly late.
- **Mid-quarter** (month 1-2): Warn: "Quarterly planning typically runs at quarter end (final 2-3 weeks). Continue anyway?" Allow it.

### Key EOS Principles

- **Quarterly pulsing is the execution heartbeat.** It bridges weekly L10s (tactical) and Annual Planning (strategic). Without it, teams drift.
- **This is NOT a V/TO refresh.** The quarterly session confirms alignment and reviews 1-Year Plan progress, but does not revisit Core Values, Core Focus, or 10-Year Target (those are annual only).
- **Rock completion target is 80%.** Teams should complete at least 80% of their Rocks each quarter. Below 80% indicates Rocks are too ambitious or execution is lacking.
- **Every Rock must align to a 1-Year Plan goal.** When setting next quarter's Rocks, each Rock should connect to a specific 1-Year Plan goal.
- **3-7 Rocks per person.** Fewer than 3 suggests under-commitment; more than 7 means focus is spread too thin.
- **All leadership team members should attend.** If someone is missing, note it but proceed.

## Process

### Mode: Plan

Use when conducting the full quarterly planning session with the structured 6-section agenda.

#### Step 1: Setup

1. **Determine the quarters.** Identify the "outgoing quarter" (being scored) and the "next quarter" (being planned). Follow the Quarter Determination rules above. Ask if not clear from context.

2. **Check for existing planning file.** Look for `data/quarterly/YYYY-QN-planning.md` (using the outgoing quarter).
   - **Exists:** Ask: "Quarterly planning for YYYY-QN already exists. Open it to review, append notes, or start fresh?"
   - **New:** Continue with step 3.

3. **Gather session details:**
   - Attendees (all leadership team members should be present)
   - Location (office, offsite, etc.)
   - Date (default to today)

4. **Gather context.** Read these files silently:
   - `data/rocks/YYYY-QN/` — outgoing quarter's Rocks (for scoring)
   - `data/scorecard/weeks/` — scorecard data for the past 13 weeks
   - `data/scorecard/metrics.md` — metric definitions and goals
   - `data/vision.md` — 1-Year Plan goals (for alignment)
   - `data/issues/open/` — open issues list (for IDS)
   - `data/accountability.md` — seat owners (for Rock-owner alignment in Section 5)

5. **Create the quarter directory** if it doesn't exist: `data/quarterly/`

Display a preparation summary:

```
Quarterly Planning — [Outgoing Quarter] → [Next Quarter]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: [Date]
Attendees: [Names]
Location: [Location]

Data loaded:
  Rocks (outgoing): [Count] rocks for [Outgoing Quarter]
  Scorecard: [N] weeks of data
  1-Year Plan: [Goal count] goals
  Open issues: [Count]

Let's walk through the 6-section agenda.
```

#### Step 2: Section 1 — Score Outgoing Rocks

1. **Read all Rock files** from `data/rocks/YYYY-QN/` for the outgoing quarter. Display current status for each Rock:

   ```
   Outgoing Rocks — [Quarter]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━
   | Rock | Owner | Status | Notes |
   |------|-------|--------|-------|
   | Launch Beta | Brad | complete ✓ | Launched week 8 |
   | Partner Outreach | Daniel | on_track → ? | 2/3 done |
   | Redesign Onboarding | Sarah | dropped ✗ | Deprioritized |
   ```

2. **Finalize unscored Rocks.** For any Rocks still `on_track` or `off_track`, prompt: "Mark as complete or dropped?"

3. **Calculate completion rate:** `(complete / total) * 100`.

   If below 80%: "Below the 80% target. Discuss: Were Rocks too ambitious, or were there execution issues?"

   If no Rock files exist: "No Rocks on file for [Quarter]. Skip Rock scoring, or enter scores manually?"

4. **Celebrate wins.** Prompt: "What were the biggest wins this quarter?" Record responses.

Record all scoring data in the planning file.

#### Step 3: Section 2 — Scorecard Review

1. **Calculate the 13-week window.** Determine which ISO weeks (YYYY-WNN) fall within the outgoing quarter, plus the prior week for trend context.

2. **Read scorecard files** from `data/scorecard/weeks/` for those weeks.

3. **For each metric**, calculate:
   - Average value across the 13 weeks
   - Hit rate (percentage of weeks at or above goal)
   - Trend direction (improving, stable, declining — compare first 6 weeks vs last 6 weeks)

4. **Display summary:**

   ```
   Scorecard Review — [Quarter]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━
   | Metric | Avg | Goal | Hit Rate | Trend |
   |--------|-----|------|----------|-------|
   | Weekly Revenue | $48K | $50K | 65% | Improving ↑ |
   | New Customers | 8 | 10 | 45% | Stable → |
   | NPS | 74 | 70 | 85% | Improving ↑ |
   ```

5. **Discuss.** Prompt: "Which metrics need attention? Any targets to adjust for next quarter?"

   If no scorecard data: "No Scorecard data for the quarter. Skip Scorecard review."

Record trends and discussion in the planning file.

#### Step 4: Section 3 — V/TO Check

This is a **light alignment check**, not a full V/TO refresh (that's annual).

1. **Read `data/vision.md`** and extract the 1-Year Plan goals.

2. **Display 1-Year Plan progress:**

   ```
   1-Year Plan Progress Check
   ━━━━━━━━━━━━━━━━━━━━━━━━━━
   | # | Goal | Progress | On Track? |
   |---|------|----------|-----------|
   | 1 | $2M ARR | $1.2M (60%) | Yes ✓ |
   | 2 | Launch 3 products | 2/3 launched | Yes ✓ |
   | 3 | Hire VP Sales | Not started | No ✗ |
   ```

3. **Prompt for discussion:**
   - "Are we still aligned on the 1-Year Plan?"
   - "Any goals that need adjustment?" (Note: major changes should be flagged for annual planning)
   - "Are there strategic concerns to discuss?"

4. **Record alignment notes** in the planning file. If major concerns arise, note: "Flag for annual planning: [concern]"

**Important:** This section does NOT update `data/vision.md`. If the user wants to update the V/TO, point them to `ceos-vto` after the session.

#### Step 5: Section 4 — IDS

1. **Read all open issues** from `data/issues/open/`.

2. **Display** the list with age (days since created):

   ```
   Open Issues
   ━━━━━━━━━━━
   | Issue | Age | Priority |
   |-------|-----|----------|
   | Hiring pipeline slow | 45d | High |
   | Customer churn Q1 | 12d | Normal |
   | Tech debt in auth | 90d | Low |
   ```

3. **Add new issues.** Prompt: "Any new issues to add before we start IDS?"

4. **Prioritize.** Ask: "Which issues should we tackle today?" Typically 3-5 issues fit in the time box.

5. **For each selected issue**, run IDS:
   - **Identify** the real issue (often different from the symptom)
   - **Discuss** perspectives (set a timer — keep it focused)
   - **Solve** with a specific action item, owner, and due date

6. Record IDS results in the planning file.

   If no open issues exist: "No open issues on file. Skip IDS, or add new issues?"

**Note:** For issues that need formal tracking, reference `ceos-ids` for creating issue files.

#### Step 6: Section 5 — Set Next Quarter Rocks

1. **Reference the 1-Year Plan** from `data/vision.md`. Display the goals so Rocks can be aligned.

2. **Prompt:** "What Rocks for [Next Quarter] will drive progress on the 1-Year Plan?"

3. **For each proposed Rock**, collect:
   - Title (specific, measurable outcome)
   - Owner (one person)
   - Which 1-Year Plan goal it aligns to

4. **Validate:**
   - **3-7 Rocks per person.** Flag if outside range: "Brad has 8 Rocks — consider consolidating."
   - **Alignment.** Each Rock should connect to a 1-Year Plan goal. Flag any that don't: "This Rock doesn't align to a specific 1-Year goal. Is it still a priority?"
   - **Measurability.** Each Rock should have a clear done/not-done criteria.
   - **Seat alignment.** Cross-reference Rock owners against `data/accountability.md`. Each Rock's subject area should match the owner's seat responsibilities. Flag mismatches: "This Rock falls under [Seat] responsibilities. Should [Seat Owner] own it?"

5. **Display the full Rock list** for approval:

   ```
   Next Quarter Rocks — [Next Quarter]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   | Rock | Owner | Aligned To |
   |------|-------|------------|
   | Launch product #3 | Brad | Goal 2: Launch 3 products |
   | Hire VP Sales | Daniel | Goal 3: Hire VP Sales |
   | Reduce churn to <5% | Sarah | Goal 1: $2M ARR |
   ```

Record in the planning file.

**Note:** Create individual Rock files using `ceos-rocks` after this session. The planning file captures the decisions; the Rock files are the operational artifacts.

#### Step 7: Section 6 — Conclude

1. **Key Decisions.** Summarize the major decisions made during the session.

2. **Cascading Messages.** Ask: "What needs to be communicated to the rest of the organization?"

3. **Action Items.** Compile all action items from all sections with owners and due dates:

   ```
   Action Items
   ━━━━━━━━━━━━
   | Action | Owner | Due Date |
   |--------|-------|----------|
   | Create Q2 Rock files via ceos-rocks | Brad | [Date] |
   | Update Scorecard targets via ceos-scorecard | Sarah | [Date] |
   | Resolve hiring pipeline issue | Daniel | [Date] |
   ```

4. **Next Steps.** List follow-up tasks:
   - Create Rock files for next quarter using `ceos-rocks`
   - Update Scorecard targets if changed using `ceos-scorecard`
   - Create issue files for new issues using `ceos-ids`
   - Communicate decisions to the organization

#### Step 8: Save the Planning File

1. **Show the complete planning file** before writing.
2. Ask: "Save this quarterly planning session?"
3. Write to `data/quarterly/YYYY-QN-planning.md` (using the outgoing quarter in the filename).
4. Remind: "Run `git commit` to save the planning session."
5. List follow-up actions:
   - "Create next quarter's Rock files using `ceos-rocks`"
   - "Update Scorecard targets if changed using `ceos-scorecard`"
   - "Create issue files for new issues using `ceos-ids`"

---

### Mode: Review Quarter

Use when analyzing a quarter's performance without running a full planning session. This is a lighter, read-only summary.

#### Step 1: Determine the Quarter

Ask which quarter to review. Defaults:
- If run in the first 2 weeks of a quarter: Default to the previous quarter (just completed)
- If run at quarter end (last 2-3 weeks): Default to the current quarter (wrapping up)
- Otherwise: Ask which quarter

#### Step 2: Load and Score Rock Data

Read all Rock files from `data/rocks/YYYY-QN/`.

For each Rock, note:
- Title, owner, status
- If status is `on_track` or `off_track`: note as "still in progress"

Calculate:
- Total Rocks
- Complete count (status = `complete`)
- Dropped count (status = `dropped`)
- Completion rate: `(complete / total) * 100`

Display:

```
Rock Performance — YYYY-QN
━━━━━━━━━━━━━━━━━━━━━━━━━━

| Rock | Owner | Status |
|------|-------|--------|
| Launch Beta | Brad | complete ✓ |
| Partner Outreach | Daniel | complete ✓ |
| Redesign Onboarding | Sarah | dropped ✗ |

Completion: 2/3 (67%) — Below 80% target ⚠️
```

Also display per-person breakdown:

```
By Owner:
  Brad: 2 Rocks, 2 complete (100%)
  Daniel: 2 Rocks, 1 complete (50%)
  Sarah: 1 Rock, 0 complete (0%)
```

If no Rock files exist: "No Rocks on file for YYYY-QN."

#### Step 3: Scorecard Trends

Read scorecard files from `data/scorecard/weeks/` that fall within the quarter's 13-week window.

For each metric, calculate:
- Average value across the weeks
- Hit rate (percentage of weeks at or above goal)
- Trend direction (improving, stable, declining)

Display:

```
Scorecard Trends — YYYY-QN
━━━━━━━━━━━━━━━━━━━━━━━━━━

| Metric | Avg | Goal | Hit Rate | Trend |
|--------|-----|------|----------|-------|
| Weekly Revenue | $48K | $50K | 65% | Improving ↑ |
| New Customers | 8 | 10 | 45% | Stable → |
| NPS | 74 | 70 | 85% | Improving ↑ |
```

If no scorecard data: "No Scorecard data for YYYY-QN."

#### Step 4: Issues Summary

Count issues:
- Read `data/issues/solved/` — count issues resolved during the quarter (by date)
- Read `data/issues/open/` — count current open issues

```
Issues — YYYY-QN
━━━━━━━━━━━━━━━━

Resolved this quarter: [N] issues
Currently open: [N] issues
```

#### Step 5: Quarter Summary

Display a consolidated report:

```
Quarter Summary — YYYY-QN
━━━━━━━━━━━━━━━━━━━━━━━━━

Rock Completion: 67% (target 80%) ⚠️
Scorecard Hit Rate: 65% average across metrics
Issues Resolved: 5
Issues Remaining: 8

Highlights:
  ✓ [Best-performing area]
  ✓ [Notable achievement]
  ⚠️ [Area needing improvement]
```

Ask: "Would you like to save this review to `data/quarterly/YYYY-QN-planning.md`?"

If yes, write the summary. If a planning file already exists for this quarter, ask before overwriting.

## Output Format

**Plan:** Progressive display of each agenda section during the session. Show preparation summary at the start, then walk through each section interactively. Show the complete planning file before saving.

**Review Quarter:** Summary tables with Rock completion rates (overall and per person), Scorecard trends (13-week window), and issues count. Consolidated quarter summary at the end. Offer to save the review.

## Guardrails

- **Always show the complete file before writing.** Never create or modify a planning file without showing it and getting approval.
- **Cross-reference existing data.** Read Rock scores, Scorecard numbers, and issues from their source files. Don't ask users to re-enter data that's already tracked.
- **Don't auto-invoke skills.** When quarterly planning results suggest using another skill (e.g., creating Rock files, updating Scorecard), mention the option but let the user decide. Say "Would you like to create Rock files using ceos-rocks?" rather than doing it automatically.
- **Sensitive data warning.** On first use in a session, remind the user: "Quarterly planning notes contain sensitive strategic data (performance metrics, personnel decisions, strategic priorities). Ensure your CEOS repo is private."
- **Quarterly planning does NOT refresh the V/TO.** The V/TO Check (Section 3) confirms alignment and reviews 1-Year Plan progress, but does NOT walk through Core Values, Core Focus, or 10-Year Target. Those are reserved for annual planning. If the user wants to update `data/vision.md`, point them to `ceos-vto`.
- **One file per quarter.** If a planning file already exists for the quarter, warn before creating a second one. Allow it (sessions sometimes need to be re-run), but make sure it's intentional.
- **Respect the agenda.** Walk through all 6 sections in order. Each serves a purpose. But keep each section focused — this is a half-day session, not a full-day one.
- **Rock alignment.** When setting next quarter's Rocks (Section 5), verify each Rock connects to a 1-Year Plan goal. Flag any that don't align — they may still be valid, but should be discussed.
- **3-7 Rocks per person.** Flag if anyone has fewer than 3 or more than 7 Rocks. This is a guideline, not a hard rule, but deviations should be conscious decisions.
- **Don't skip sections in Plan mode.** Walk through all 6 sections. If the user wants to skip a section, note it in the file: "Section X: Skipped per team decision."
- **Finalize Rock scores.** In Section 1, Rocks that are still `on_track` or `off_track` must be scored as `complete` or `dropped`. The outgoing quarter needs closure.
- **The planning doc and the rock files must stay in sync.** When Rocks are scored or created, the change belongs in both places: the `status` field in the individual rock file's frontmatter, and the rock scorecard table in the quarterly planning document. When one person updates the rock files and another updates the planning doc, a reconciliation pass is needed to bring them back into alignment. The planning doc is the consolidated narrative view; the rock files are the source of truth for status.

  ```
  // Good
    # First change: set rock-001 status to 'dropped' in its frontmatter
    # Second change: update the Q1 planning doc table to show 'Dropped', matching the rock file

  // Bad
    # Updating the planning doc table without changing the rock file's frontmatter status
    # Or: updating the rock file's status without reflecting it in the planning doc
  ```

## Integration Notes

### Rocks (ceos-rocks)

- **Read:** `ceos-quarterly-planning` reads Rock files from `data/rocks/YYYY-QN/` for scoring in Section 1 (Score Outgoing Rocks) and for reference when setting next quarter's Rocks in Section 5. It does not modify Rock files.
- **Related:** After the session, `ceos-rocks` should be used to create individual Rock files for the next quarter.

### Scorecard (ceos-scorecard)

- **Read:** `ceos-quarterly-planning` reads scorecard data from `data/scorecard/weeks/` for 13-week trend analysis in Section 2. It also reads `data/scorecard/metrics.md` for metric definitions and goals.
- **Related:** After the session, `ceos-scorecard` should be used to update metric targets if they changed.

### V/TO (ceos-vto)

- **Read:** `ceos-quarterly-planning` reads `data/vision.md` for the 1-Year Plan goals — used in the V/TO Check (Section 3) and for Rock alignment in Section 5. It does NOT modify `data/vision.md`.
- **Related:** If major V/TO changes surface during the session, they should be flagged for annual planning or handled via `ceos-vto`.

### IDS (ceos-ids)

- **Read:** `ceos-quarterly-planning` reads open issues from `data/issues/open/` for the IDS sweep in Section 4. In Review Quarter mode, it reads `data/issues/solved/` for the quarter summary.
- **Related:** After the session, `ceos-ids` should be used to create formal issue files for any new issues identified.

### L10 (ceos-l10)

- **Related:** L10 is the weekly cadence; quarterly planning is the quarterly cadence. They complement each other — the L10 handles weekly tactical issues, while quarterly planning handles strategic transitions between quarters. Action items from quarterly planning may appear as To-Dos in subsequent L10s.

### Annual Planning (ceos-annual)

- **Related:** Annual planning is the yearly superset that includes V/TO refresh, year-in-review, and Q1 Rock setting. Quarterly planning fills the 3 inter-annual quarters (Q2, Q3, Q4 planning). Annual planning sets the 1-Year Plan; quarterly planning executes against it.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-quarterly-planning` reads `data/accountability.md` during Section 5 (Set Next Quarter Rocks) to validate that Rock owners match seat responsibilities. Each Rock's subject area should map to the owner's seat in the Accountability Chart.
- **Suggested flow:** If a Rock doesn't align with the owner's seat, suggest: "This Rock falls under [Seat] responsibilities. Should [Seat Owner] own it instead?"

### Orchestration Principle

`ceos-quarterly-planning` reads data from multiple skills during the planning session (rocks, scorecard, vision, issues) but writes only to `data/quarterly/`. Individual skills handle their own operational artifacts — `ceos-rocks` creates Rock files, `ceos-scorecard` updates metrics, `ceos-ids` manages issues. The quarterly planning file captures decisions; the skills create the operational follow-through.
