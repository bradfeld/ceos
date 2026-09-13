---
name: ceos-lma
description: Use when assessing leadership and management effectiveness using the LMA framework
file-access: [data/lma/, templates/lma-assessment.md, data/accountability.md, data/people/, data/clarity/, data/meetings/l10/, data/conversations/]
tools-used: [Read, Write, Glob]
---

# ceos-lma

Assess leadership and management effectiveness using the LMA (Leadership + Management = Accountability) framework — EOS Toolbox tool #11. Walk a manager through rating themselves on 5 Leadership Practices and 5 Management Practices, calculate scores, flag areas needing attention, and optionally gather 360-degree feedback from direct reports.

**Not for:** Evaluating whether someone is a fit for their seat (use `ceos-people`), defining organizational structure (use `ceos-accountability`), or running quarterly conversations (use `ceos-quarterly`). LMA assesses *whether* you're practicing leadership and management habits, not *whether* you're the right person for the role.

## When to Use

- "Run LMA assessment" or "LMA checklist" or "LMA for [person]"
- "How am I doing as a manager?" or "how am I doing as a leader?"
- "Leadership assessment" or "management assessment"
- "Am I creating accountability?" or "am I holding my team accountable?"
- "LMA review" or "show LMA scores" or "team LMA summary"
- "360 feedback for [person]" or "get feedback from my team"
- "Run LMA" or "leadership and management check"

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/lma/` | LMA assessment files (one per person) |
| `templates/lma-assessment.md` | Template for new LMA assessments |
| `data/accountability.md` | Source of management relationships and seat info (read-only — use ceos-accountability to modify) |
| `data/people/` | People Analyzer evaluations (read-only — reference for context) |
| `data/clarity/` | Clarity Break records (read-only — informs Leadership Practice #5) |
| `data/meetings/l10/` | L10 meeting notes (read-only — informs Management Practice #3) |
| `data/conversations/` | Quarterly conversation records (read-only — informs Management Practice #4) |

### LMA File Format

Each person has a markdown file at `data/lma/firstname-lastname.md` with YAML frontmatter:

```yaml
person: "Brad Feld"
seat: "Visionary"
date: "2026-02-15"
status: active            # active | reviewed | stale
leadership_score: 4.2
management_score: 3.8
overall_score: 4.0
leadership_practices:
  clear_direction: 5
  necessary_tools: 4
  letting_go: 4
  greater_good: 5
  clarity_breaks: 3
management_practices:
  clear_expectations: 4
  communicating_well: 4
  meeting_pulse: 3
  quarterly_conversations: 4
  rewarding_recognizing: 4
feedback: []
last_assessed: "2026-02-15"
```

**File naming:** `firstname-lastname.md` — lowercase, hyphenated. Person-centric (survives role changes).

### Status Values

| Status | Meaning | When |
|--------|---------|------|
| `active` | Current assessment, may need development actions | After initial assessment or re-assessment |
| `reviewed` | Assessment reviewed, development plan updated | After a Review session |
| `stale` | Assessment is > 120 days old | Flagged automatically by Review mode |

### The 10 Practices

#### Leadership Practices

| # | Practice | Description | Data Source |
|---|----------|-------------|-------------|
| 1 | Giving clear direction | Setting vision, priorities, and expectations so people know where they're going | Self-assessment |
| 2 | Providing the necessary tools | Ensuring people have what they need — training, resources, systems, authority | Self-assessment |
| 3 | Letting go of the vine | Empowering others instead of micromanaging; trusting the team to execute | Self-assessment |
| 4 | Acting with the greater good in mind | Making decisions for the organization's benefit, not personal interest | Self-assessment |
| 5 | Taking Clarity Breaks | Stepping away to think strategically — "work ON the business, not IN it" | `data/clarity/` frequency |

#### Management Practices

| # | Practice | Description | Data Source |
|---|----------|-------------|-------------|
| 1 | Keeping expectations clear | Each direct report knows their seat, roles, Rocks, and measurables | Self-assessment |
| 2 | Communicating well | Open, honest, two-way communication with the team | Self-assessment |
| 3 | Maintaining the right meeting pulse | Running consistent, productive weekly meetings (L10s) | `data/meetings/l10/` regularity |
| 4 | Having quarterly conversations | Formal quarterly check-ins with each direct report | `data/conversations/` frequency |
| 5 | Rewarding and recognizing | Acknowledging great work and addressing underperformance | Self-assessment |

### Rating Scale

| Rating | Meaning |
|--------|---------|
| 1 | Never / Not at all |
| 2 | Rarely |
| 3 | Sometimes |
| 4 | Usually |
| 5 | Consistently |

Scores below 3 indicate a practice that needs focused development.

## Process

### Mode: Assess

Use when running an LMA self-assessment for a specific person. Recommended quarterly — ideally before Quarterly Planning sessions.

#### Step 1: Identify the Person

Ask for the person's name. Check if `data/lma/firstname-lastname.md` already exists.

- **Exists:** Read the file, show previous scores: "You have an existing LMA assessment from [date] (Leadership: [X], Management: [Y], Overall: [Z]). Re-assess (start fresh scores) or update (revise notes only)?"
- **New person:** Will create from `templates/lma-assessment.md`

#### Step 2: Pull Context from Accountability Chart

Read `data/accountability.md` to find the person's seat(s) and identify their direct reports.

- **Has a seat:** Display: "[Person] holds the [Seat] seat with [N] direct reports."
- **No seat found:** Warn: "[Person] has no seat defined in the Accountability Chart. LMA requires a management/leadership context. Add them via `ceos-accountability`, or proceed with manual context."

#### Step 3: Gather Cross-Skill Context

Read data from related skills to provide evidence-based context for specific practices:

**Clarity Breaks (Leadership Practice #5):**
- Read `data/clarity/` via Glob. Count files from the last 90 days.
- Display: "[N] Clarity Breaks in the last 90 days" or "No Clarity Break records found. Consider running `ceos-clarity` to establish Clarity Break habits."

**L10 Meeting Pulse (Management Practice #3):**
- Read `data/meetings/l10/` via Glob. Check meeting frequency over the last 8 weeks.
- Display: "[N] L10 meetings in the last 8 weeks ([frequency])" or "No L10 meeting records found. Consider running `ceos-l10` to establish meeting pulse."

**Quarterly Conversations (Management Practice #4):**
- Read `data/conversations/` via Glob. Check for conversations in the current and previous quarter.
- Display: "[N] quarterly conversations recorded" or "No quarterly conversation records found."

Show context summary before rating:

```
Cross-Skill Context for [Person]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Clarity Breaks (last 90 days): [N] sessions
  L10 Meeting Pulse (last 8 weeks): [N]/8 weeks
  Quarterly Conversations (current + prev quarter): [N] conversations
```

#### Step 4: Rate Leadership Practices

Present each of the 5 Leadership Practices one at a time with its description and any relevant context data. Collect a 1-5 rating for each.

For Practice #5 (Clarity Breaks), include the context data: "Your records show [N] Clarity Breaks in the last 90 days."

After all 5 are rated, calculate Leadership Score as the average (one decimal place).

```
Leadership Practices — [Person]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| # | Practice | Rating | Notes |
|---|----------|--------|-------|
| 1 | Giving clear direction | [1-5] | [user notes] |
| 2 | Providing the necessary tools | [1-5] | |
| 3 | Letting go of the vine | [1-5] | |
| 4 | Acting with the greater good in mind | [1-5] | |
| 5 | Taking Clarity Breaks | [1-5] | [N] breaks in 90 days |

Leadership Score: [X.X] / 5.0
```

#### Step 5: Rate Management Practices

Present each of the 5 Management Practices with description and relevant context data. Collect a 1-5 rating for each.

For Practice #3 (Meeting Pulse), include: "Records show [N]/8 L10 meetings in the last 8 weeks."
For Practice #4 (Quarterly Conversations), include: "[N] quarterly conversations recorded."

Calculate Management Score as the average (one decimal place).

```
Management Practices — [Person]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| # | Practice | Rating | Notes |
|---|----------|--------|-------|
| 1 | Keeping expectations clear | [1-5] | |
| 2 | Communicating well | [1-5] | |
| 3 | Maintaining the right meeting pulse | [1-5] | [N]/8 L10s |
| 4 | Having quarterly conversations | [1-5] | [N] conversations |
| 5 | Rewarding and recognizing | [1-5] | |

Management Score: [X.X] / 5.0
```

#### Step 6: Calculate LMA Score

Overall LMA Score = average of Leadership Score and Management Score (one decimal place).

```
LMA Score — [Person]
━━━━━━━━━━━━━━━━━━━━

  Leadership:  [X.X] / 5.0
  Management:  [X.X] / 5.0
  ─────────────────────────
  Overall LMA: [X.X] / 5.0

  Leadership + Management = Accountability
```

#### Step 7: Flag Practices Below 3

List any practices scoring below 3 with suggested development actions:

```
Flagged Practices (Below 3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ [Practice Name] — rated [N]/5
   Suggested: [specific, actionable development suggestion]

⚠️ [Practice Name] — rated [N]/5
   Suggested: [specific suggestion]
```

If no practices are below 3: "No practices flagged — all rated 3 or above."

#### Step 8: Save the File

Show the complete file before writing. Ask: "Save this LMA assessment?"

Write to `data/lma/firstname-lastname.md` using the template. Update:
- YAML frontmatter: all scores, practice ratings, date, status
- Markdown body: populate practice tables with ratings and notes
- Assessment History: add dated entry

If re-assessing, preserve existing Assessment History entries and add a new one.

---

### Mode: Review

Use when reviewing LMA results across all managers or for checking team-wide patterns.

#### Step 1: Read All LMA Files

Read all files from `data/lma/` via `Glob("data/lma/*.md")`. Parse YAML frontmatter.

If no files exist: "No LMA assessments found. Run an Assess for your first team member."

#### Step 2: Display Summary Table

```
LMA Review — Team Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━

| Name | Seat | Last Assessed | Leadership | Management | Overall LMA | Flag |
|------|------|--------------|------------|------------|-------------|------|
| Brad Feld | Visionary | 2026-02-15 | 4.2 | 3.8 | 4.0 | |
| Sarah Chen | Integrator | 2026-01-10 | 3.6 | 4.4 | 4.0 | |
| Mike Torres | VP Sales | 2025-09-15 | 3.0 | 2.8 | 2.9 | ⚠️ Mgmt |

Team averages:
  Leadership: [X.X]
  Management: [X.X]
  Overall LMA: [X.X]
```

#### Step 3: Identify Team-Wide Patterns

Aggregate practice scores across all managers. Find the lowest-scoring practices:

```
Lowest-Scoring Practices (Team Average)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Practice | Type | Team Avg | Below 3 Count |
|----------|------|---------|---------------|
| Taking Clarity Breaks | Leadership | 2.5 | 2/3 managers |
| Maintaining meeting pulse | Management | 3.0 | 1/3 managers |
```

#### Step 4: Flag Stale Assessments

Check `last_assessed` date for each person. If > 120 days ago:

"📅 [Person]'s LMA assessment is [N] days old. Consider re-running before the next Quarterly Planning session."

#### Step 5: Show Trends

If a person has multiple assessment history entries (from re-assessments), show the trend:

```
LMA Trend — [Person]
━━━━━━━━━━━━━━━━━━━━

| Date | Leadership | Management | Overall | Direction |
|------|-----------|------------|---------|-----------|
| 2025-11-01 | 3.4 | 3.2 | 3.3 | |
| 2026-02-15 | 4.2 | 3.8 | 4.0 | ↑ Improving |
```

#### Step 6: Drill Down

Ask: "Want to view details for a specific person, or run a new Assess?"

---

### Mode: 360

Use when gathering feedback from direct reports to compare against a manager's self-assessment. This creates a gap analysis between self-perception and team perception.

#### Step 1: Identify the Manager

Ask for the manager's name. Read `data/lma/firstname-lastname.md`.

- **Has self-assessment:** Load it, show current self-ratings.
- **No self-assessment:** "No LMA self-assessment found for [person]. Run an Assess first — 360 feedback requires a self-assessment to compare against."

#### Step 2: Identify Direct Reports

Read `data/accountability.md` to find people who report to this manager.

- **Has direct reports:** Display the list: "[Person] manages: [Name 1], [Name 2], [Name 3]"
- **No direct reports found:** "360 mode requires direct reports. [Person] has none listed in the Accountability Chart. Use `ceos-accountability` to update the org chart, or name respondents manually."

Ask which direct reports will provide feedback (may be a subset).

#### Step 3: Collect Feedback

For each respondent, rate the manager on all 10 practices (1-5). Use the same rating scale:

"[Respondent Name] is rating [Manager Name]'s leadership and management practices."

Present all 10 practices and collect ratings. This can be done one respondent at a time — the feedback array is additive. Each session adds one respondent's feedback.

Store each respondent's feedback in the `feedback` frontmatter array:

```yaml
feedback:
  - name: "Sarah Chen"
    relationship: "direct report"
    ratings: [4, 3, 5, 4, 3, 4, 4, 3, 4, 3]  # 10 ratings in practice order
    date: "2026-02-15"
```

The ratings array follows practice order: Leadership 1-5, then Management 1-5.

#### Step 4: Compare Self vs Team

After at least one respondent's feedback is collected, display the comparison:

```
360 Comparison — [Manager Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Leadership Practices:
| # | Practice | Self | Team Avg | Gap |
|---|----------|------|---------|-----|
| 1 | Giving clear direction | 5 | 4.0 | -1.0 |
| 2 | Providing the necessary tools | 4 | 3.5 | -0.5 |
| 3 | Letting go of the vine | 4 | 4.5 | +0.5 |
| 4 | Acting with the greater good | 5 | 4.5 | -0.5 |
| 5 | Taking Clarity Breaks | 3 | 3.0 | 0.0 |

Management Practices:
| # | Practice | Self | Team Avg | Gap |
|---|----------|------|---------|-----|
| 1 | Keeping expectations clear | 4 | 3.0 | -1.0 |
| 2 | Communicating well | 4 | 3.5 | -0.5 |
| 3 | Maintaining meeting pulse | 3 | 4.0 | +1.0 |
| 4 | Having quarterly conversations | 4 | 3.0 | -1.0 ⚠️ |
| 5 | Rewarding and recognizing | 4 | 2.5 | -1.5 ⚠️ |
```

#### Step 5: Flag Large Gaps

Flag any practice where the absolute gap between self and team average is >= 2 points:

```
Significant Gaps (≥ 2 points)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ [Practice Name] — Self: [X], Team: [Y] (gap: [Z])
   This is worth discussing with the team. Large gaps indicate a
   difference between how you perceive your effectiveness and how
   your team experiences it.
```

If no gaps >= 2: "No significant gaps detected. Self-assessment and team feedback are generally aligned."

#### Step 6: Save Updated File

Show the complete updated file before writing. Ask: "Save this 360 feedback?"

Update:
- YAML frontmatter: add respondent to `feedback` array
- Markdown body: update 360 Feedback table with respondent's data
- Assessment History: add dated entry for 360 feedback collection

## Output Format

**Assess:** Practice rating tables (Leadership and Management), calculated scores, flagged practices below 3, and complete file shown before save.

**Review:** Summary table with all managers, Leadership/Management/Overall scores, stale flags, team-wide practice patterns, and trends if multiple assessments exist.

**360:** Side-by-side comparison table (Self vs Team Average vs Gap) for all 10 practices. Flagged gaps >= 2 points. Complete file shown before save.

## Guardrails

- **Always show the complete file before writing.** Never modify an LMA file without showing the change and getting approval.
- **Validate ratings are 1-5.** Reject values outside this range with: "Ratings must be between 1 (Never) and 5 (Consistently)."
- **Don't auto-invoke other skills.** When LMA results suggest running a Clarity Break or scheduling a quarterly conversation, mention the option but let the user decide. Say "Would you like to start a Clarity Break?" rather than doing it automatically.
- **Don't confuse with People Analyzer.** LMA is a self-assessment of leadership/management effectiveness. People Analyzer (`ceos-people`) evaluates whether someone is the right person in the right seat. If the user seems to be evaluating a person's fit, suggest `ceos-people` instead.
- **360 requires existing self-assessment.** Don't allow 360 feedback without a self-assessment to compare against. The comparison is the value.
- **Sensitive data warning.** On first use in a session, remind the user: "LMA assessments contain information about leadership effectiveness. This repo should be private."
- **Respect the quarterly cadence.** Suggest running LMA before Quarterly Planning sessions. Flag assessments > 120 days old. But don't nag — once per session is enough.
- **One rating per practice.** Don't allow split ratings (e.g., "3.5"). Use whole numbers 1-5 only.
- **Cross-skill data is context, not deterministic.** Low Clarity Break count doesn't automatically mean a low Leadership #5 rating. Present the data and let the user decide their rating.

## Integration Notes

### Accountability Chart (ceos-accountability)

- **Direction:** Read
- **What data:** `data/accountability.md` — seat names, owners, and reporting relationships
- **Purpose:** Identifies who the manager is, what seat they hold, and who their direct reports are. Essential for both Assess (context) and 360 (respondent identification).

### People Analyzer (ceos-people)

- **Direction:** Read
- **What data:** `data/people/firstname-lastname.md` — GWC assessment, current status
- **Purpose:** Optional context during Assess. If a person is `below_bar`, LMA can help identify whether it's a leadership gap (not empowering them) or a management gap (unclear expectations).

### Clarity Break (ceos-clarity)

- **Direction:** Read
- **What data:** `data/clarity/` — Clarity Break notes and frequency
- **Purpose:** Provides evidence for Leadership Practice #5 (Taking Clarity Breaks). Count of recent breaks gives objective context for the self-rating.

### L10 Meetings (ceos-l10)

- **Direction:** Read
- **What data:** `data/meetings/l10/` — L10 meeting notes
- **Purpose:** Provides evidence for Management Practice #3 (Maintaining the right meeting pulse). Meeting frequency and regularity give objective context.

### Quarterly Conversations (ceos-quarterly)

- **Direction:** Read
- **What data:** `data/conversations/` — Quarterly conversation records
- **Purpose:** Provides evidence for Management Practice #4 (Having quarterly conversations). Conversation frequency gives objective context.

### Quarterly Planning (ceos-quarterly-planning)

- **Direction:** Related
- **What data:** No direct data access
- **Purpose:** LMA is ideally run before Quarterly Planning sessions. Leadership and management effectiveness directly impacts Rock execution and team accountability.

### Annual Planning (ceos-annual)

- **Direction:** Related
- **What data:** No direct data access
- **Purpose:** Annual planning is a natural time to re-assess LMA. Leaders reassess their effectiveness as they plan the new year.

### Delegate and Elevate (ceos-delegate)

- **Direction:** Related
- **What data:** No direct data access
- **Purpose:** Related development tool. LMA assesses *how* you lead and manage. Delegate and Elevate assesses *what work* you should focus on. Both serve leadership development.

### Write Principle

**Only `ceos-lma` writes to `data/lma/`.** Other skills may reference LMA assessments for leadership development context, but do not modify them.
