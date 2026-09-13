---
name: ceos-people
description: Use when evaluating team members — Core Values alignment and GWC (right people, right seats)
file-access: [data/people/, templates/people-analyzer.md, data/vision.md, data/accountability.md]
tools-used: [Read, Write, Glob]
---

# ceos-people

Evaluate whether team members are the right people (Core Values alignment) in the right seats (GWC: Get it, Want it, Capacity to do it). Manage people evaluations, run quarterly reviews, and flag below-the-bar situations for action.

## When to Use

- "Evaluate [person]" or "run the people analyzer for [name]"
- "Are we right people, right seats?" or "show our people evaluations"
- "Quarterly people review" or "let's review the team"
- "Is [person] in the right seat?" or "GWC check on [name]"
- "Who's below the bar?" or "show below-bar team members"
- Any discussion about team fit, Core Values alignment, or seat assignment

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/people/` | Person evaluation files (one per person) |
| `data/people/alumni/` | Departed team members (historical reference) |
| `data/vision.md` | Source of Core Values (read-only — use ceos-vto to modify) |
| `data/accountability.md` | Source of seats and owners (reference for GWC) |
| `templates/people-analyzer.md` | Template for new person evaluations |

### Person File Format

Each person is a markdown file at `data/people/firstname-lastname.md` with YAML frontmatter:

```yaml
name: "Brad Feld"
seat: "Visionary"
core_values:
  # Each Core Value from vision.md, rated +, +/-, or -
status: right_person_right_seat  # right_person_right_seat | below_bar | wrong_seat | evaluating
gwc:
  get: true       # true | false | null
  want: true
  capacity: true
last_evaluated: "2026-01-15"
created: "2026-01-02"
departed: false
```

**File naming:** `firstname-lastname.md` — lowercase, hyphenated. Person-centric (survives role changes).

### Status Values

| Status | Meaning | When |
|--------|---------|------|
| `right_person_right_seat` | Passes both Core Values and GWC | All Core Values are + or mostly +, all GWC = true |
| `below_bar` | Fails Core Values OR GWC | Three strikes on values, or any GWC = false |
| `wrong_seat` | Right person, wrong seat | Core Values pass but GWC fails for current seat |
| `evaluating` | Not yet assessed | New hire (< 90 days) or incomplete evaluation |

### Core Values Rating

| Rating | Meaning |
|--------|---------|
| `+` | Lives this value most of the time |
| `+/-` | Sometimes demonstrates, sometimes doesn't |
| `-` | Rarely or never demonstrates this value |

**Three strikes rule:** Three or more `+/-` or `-` ratings = "wrong person" (Core Values misalignment). This is a critical flag that requires action.

### GWC Dimensions

| Dimension | Question | Notes |
|-----------|----------|-------|
| **Get it** | Do they truly understand the role? | Intuitive grasp of the job, culture, systems |
| **Want it** | Do they genuinely want the work? | Not just title/pay — the actual daily work |
| **Capacity** | Can they do it? | Time, skill, knowledge, emotional capacity |

All three must be **true** for "right seat." Any single **false** = wrong seat.

## Process

### Mode: Evaluate

Use when evaluating a specific person against Core Values and GWC.

#### Step 1: Identify the Person

Ask for the person's name. Check if `data/people/firstname-lastname.md` already exists.

- **Exists:** Read the file, show current evaluation, ask: "Re-evaluate or update notes?"
- **New person:** Create from `templates/people-analyzer.md`

#### Step 2: Core Values Evaluation

Read Core Values from `data/vision.md`. For each Core Value, ask the user to rate: `+`, `+/-`, or `-`.

Display a rating table as you go:

```
Core Values Evaluation — [Person Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Core Value    | Rating | Notes           |
|---------------|--------|-----------------|
| Integrity     | +      | Consistently    |
| Innovation    | +/-    | Room to grow    |
| Transparency  | +      |                 |
| Grit          | -      | Avoids hard work|
```

#### Step 3: Three Strikes Detection

After all Core Values are rated, count `+/-` and `-` ratings:

- **3+ negative ratings (`+/-` or `-`):** Flag immediately:
  ```
  ⚠️  THREE STRIKES — Core Values misalignment detected.
  [Person] has 3+ values rated +/- or -. This signals "wrong person."
  Action required: coaching conversation, role change, or exit plan.
  ```
- **1-2 negative ratings:** Note but continue: "Some values need attention. Continue to GWC."
- **All `+`:** "Strong Core Values alignment. Right person."

Determine **right_person**: All or mostly `+` ratings = yes. Three strikes = no.

#### Step 4: GWC Evaluation

Read the person's current seat from `data/accountability.md`. If the person owns multiple seats, evaluate GWC for each seat separately.

For each seat, ask three binary questions:

1. **Get it?** Does [person] truly understand the [seat] role? (yes/no)
2. **Want it?** Does [person] genuinely want to do [seat] work? (yes/no)
3. **Capacity?** Does [person] have the capacity to excel at [seat]? (yes/no)

Display the result:

```
GWC — [Person Name] as [Seat Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Get it:     ✓ Yes
Want it:    ✓ Yes
Capacity:   ✗ No — struggling with volume

Right seat? No (Capacity gap)
```

Determine **right_seat**: All three must be **true**. Any **false** = wrong seat.

#### Step 5: Suggest Status

Based on the evaluation:

| Core Values | GWC | Suggested Status |
|-------------|-----|-----------------|
| Right person | Right seat | `right_person_right_seat` |
| Right person | Wrong seat | `wrong_seat` |
| Wrong person | Any | `below_bar` |
| Incomplete | Any | `evaluating` |

Present the suggestion: "Based on this evaluation, I'd suggest **[status]**. Do you agree, or would you set it differently?"

**Always let the user confirm or override.** Status is a leadership judgment call, not a formula.

#### Step 6: Write the File

Show the complete evaluation file before writing. Ask: "Save this evaluation?"

Update `last_evaluated` to today's date. Add a dated entry to the Evaluation History section.

#### Step 7: Below-Bar Action

If status is `below_bar` or `wrong_seat`, offer:

"[Person] is below the bar. Would you like to create an issue for a 30-day action plan? This will create a file in `data/issues/open/` for IDS discussion."

If yes, use the issue template pattern from `data/issues/open/` to create an issue with:
- Title referencing the person and the gap
- 30-day timeline
- Specific actions from the evaluation

---

### Mode: Review

Use when reviewing the current state of all people evaluations.

#### Step 1: Read All Evaluations

Read all files from `data/people/` (exclude `alumni/` subdirectory). Parse the YAML frontmatter for each person.

If no files exist: "No people evaluations found. Run an Evaluate for your first team member."

#### Step 2: Display Summary Table

```
People Analyzer — Team Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Name          | Seat        | Status                  | Last Evaluated | Flag    |
|---------------|-------------|-------------------------|----------------|---------|
| Brad Feld     | Visionary   | right_person_right_seat | 2026-01-15     |         |
| Sarah Chen    | Integrator  | right_person_right_seat | 2026-01-15     |         |
| Mike Torres   | VP Sales    | wrong_seat              | 2025-12-01     | ⚠️ Seat |
| Alex Kim      | VP Eng      | below_bar               | 2025-11-15     | 🔴 Bar  |
| Jamie Lee     | Marketing   | evaluating              | 2026-01-28     | 🆕 New  |

The Bar: 3/5 (60%) at or above — Target: 80%+
```

#### Step 3: Highlight Issues

Flag the following:

- **Below bar:** `🔴` — requires action plan
- **Wrong seat:** `⚠️` — person is right, seat is wrong (find a better fit)
- **Stale evaluation:** If `last_evaluated` is > 120 days ago, flag: `📅 Overdue`
- **Evaluating:** `🆕` — new hire or incomplete evaluation

#### Step 4: Bar Percentage

Calculate: `(right_person_right_seat count) / (total evaluated, excluding "evaluating")`.

If below 80%: "Below the 80% target. Consider bringing people discussions to the next L10."

#### Step 5: Drill Down

Ask: "Want to drill into any person, or run a new Evaluate?"

---

### Mode: Quarterly

Use for the formal quarterly review of all seats against the Accountability Chart.

#### Step 1: Read the Accountability Chart

Read `data/accountability.md` to get all seats and their current owners.

If the file doesn't exist or is empty: "No accountability chart found. Create one first with `ceos-accountability` or manually at `data/accountability.md`."

#### Step 2: Map Seats to People

For each seat in the accountability chart:

- **Has an owner with a person file:** Load the evaluation
- **Has an owner without a person file:** Flag: "No evaluation on file. Evaluate now?"
- **Empty seat (no owner):** Flag: "Empty seat — [Seat Name]. Hire or reassign?"

Display the seat map:

```
Quarterly People Review
━━━━━━━━━━━━━━━━━━━━━━━

| Seat        | Owner         | Status                  | Action Needed?  |
|-------------|---------------|-------------------------|-----------------|
| Visionary   | Brad Feld     | right_person_right_seat | No              |
| Integrator  | Sarah Chen    | right_person_right_seat | No              |
| VP Sales    | Mike Torres   | wrong_seat              | Re-evaluate GWC |
| VP Eng      | Alex Kim      | below_bar               | Action plan due |
| Marketing   | (empty)       | —                       | Hire needed     |
```

#### Step 3: Walk Through Each Seat

For each filled seat, ask: "**Re-evaluate**, **update notes**, or **skip**?"

- **Re-evaluate:** Run the full Evaluate mode (Step 2-6 from Evaluate)
- **Update notes:** Just add a dated note to the Evaluation History
- **Skip:** Move to next seat

Track progress:

```
Progress: 3/5 seats reviewed [████████░░░░] 60%
```

#### Step 4: Handle Empty Seats

For each empty seat, offer:

"The [Seat Name] seat is empty. Would you like to create an issue for hiring? This will go to `data/issues/open/` for IDS discussion."

#### Step 5: Quarterly Summary

After reviewing all seats, display:

```
Quarterly People Review — Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Seats filled:    4/5 (80%)
Right People, Right Seats: 2/4 (50%)
Below the bar:   1
Wrong seat:      1
Empty seats:     1
Evaluating:      0

Action items created: 2
Next quarterly review: [quarter-end date]
```

If any seats are below bar or empty: "These should be discussed at the next L10. Bring them to the Issues List."

## Output Format

**Evaluate:** Show the complete evaluation file before writing. Display Core Values table and GWC results inline.

**Review:** Summary table with status flags, bar percentage. Offer drill-down.

**Quarterly:** Seat-by-seat walkthrough with progress tracker. End with quarterly summary.

## Guardrails

- **Always show diff before writing.** Never modify a person file without showing the change and getting approval.
- **Three strikes rule.** If 3+ Core Values are `+/-` or `-`, always flag it prominently. Do not minimize.
- **All three GWC required.** Don't allow partial GWC evaluation. All three (Get, Want, Capacity) must be answered.
- **Don't delete person files.** For departed team members, set `departed: true` and move to `data/people/alumni/`.
- **Core Values come from vision.md.** Always read Core Values from `data/vision.md` — never ask the user to list them (they're already defined in the V/TO).
- **Status is judgment, not formula.** The skill suggests a status based on scores, but the user always confirms. Leadership judgment matters more than a mechanical calculation.
- **Sensitive data warning.** On first use, remind the user: "People evaluations contain sensitive performance data. Use a private repo, not a public one."
- **Cross-reference accountability.md.** When evaluating GWC, always check the person's seat from `data/accountability.md` rather than asking the user to recall it.
- **Don't auto-invoke other skills.** Mention `ceos-vto`, `ceos-quarterly`, and `ceos-ids` when relevant, but let the user decide when to switch workflows.
- **Quarterly cadence.** Flag if no quarterly review has been run in > 100 days. People evaluations are meant to be regular, not ad-hoc.

## Integration Notes

### V/TO (ceos-vto)

- **Read:** `ceos-people` reads Core Values from `data/vision.md` for the Core Values evaluation. It does not write to the V/TO file.
- **Suggested flow:** If Core Values are updated via `ceos-vto`, existing people evaluations may need refreshing.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-people` reads `data/accountability.md` for the person's seat(s) during GWC evaluation. It does not write to the accountability file.
- **Suggested flow:** If a person's seat changes in the accountability chart, their GWC evaluation should be re-run for the new seat.

### Quarterly Conversations (ceos-quarterly)

- **Read:** `ceos-quarterly` references People Analyzer evaluations from `data/people/` during quarterly conversations. Core Values and GWC ratings serve as reference points, not re-evaluations.
- **Suggested flow:** If quarterly conversation ratings differ significantly from People Analyzer, suggest updating via `ceos-people`.

### IDS (ceos-ids)

- **Related:** Below-bar situations may create Issues for action plans. When a person's status is `below_bar` or `wrong_seat`, `ceos-people` offers to create an issue in `data/issues/open/`.
- **Suggested flow:** Use `ceos-ids` for formal issue tracking of people-related action plans.

### Annual Planning (ceos-annual)

- **Read:** `ceos-annual` references People Analyzer evaluations during the Organizational Checkup section (Section 4) of the annual planning session.

### Write Principle

**Only `ceos-people` writes to `data/people/`.** Other skills read person evaluations for reference. The quarterly conversation skill references evaluations but directs updates back to `ceos-people`.
