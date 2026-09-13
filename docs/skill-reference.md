# Skill Reference

Complete reference for all CEOS skills. Each skill is a Claude Code skill that implements a core EOS tool.

## How Skills Work

CEOS skills are markdown files (`SKILL.md`) that teach Claude Code how to perform EOS workflows. When you start a Claude Code session in your CEOS repository, Claude discovers the installed skills and matches your requests to the right skill automatically.

**Repo detection:** Every skill searches upward from your current directory for the `.ceos` marker file. If you're not in a CEOS repository, the skill will tell you to clone and set up first.

**Trigger phrases:** Each skill responds to natural language. You don't need to remember exact commands — just describe what you want to do and Claude will match it to the right skill.

---

## ceos-vto — Vision/Traction Organizer

Review and update the V/TO — the single document that captures where your company is going and how it plans to get there.

### When to Use

- "Review our vision" or "show me the V/TO"
- "Update our core values" or "change our 10-year target"
- "What's our core focus?" or "what are our 3 uniques?"
- "Are our Rocks aligned with the 1-Year Plan?"
- "Let's update the 3-year picture"

### Key Operations

| Operation | What Happens |
|-----------|-------------|
| **Review** | Reads `data/vision.md`, displays a summary of all 8 sections |
| **Update** | Shows current content of a section, drafts changes, shows diff, asks for approval |
| **Alignment Check** | Cross-references current Rocks against the 1-Year Plan, flags mismatches |

### The 8 V/TO Sections

| Section | Horizon | Key Question |
|---------|---------|-------------|
| Core Values | Permanent | What do we stand for? |
| Core Focus | Permanent | Why do we exist? What's our niche? |
| 10-Year Target | 10 years | What's our big audacious goal? |
| Marketing Strategy | Ongoing | Who do we serve? How are we different? |
| 3-Year Picture | 3 years | What does the company look like? |
| 1-Year Plan | 1 year | What must be true in 12 months? |
| Quarterly Rocks | 90 days | Managed by `ceos-rocks` |
| Issues List | Ongoing | Managed by `ceos-ids` |

### Example

```
You: "Review our vision"

Claude reads data/vision.md and shows:

  Acme Corp — V/TO Summary (last updated: 2026-02-01)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Core Values: Integrity, Speed, Customer First
  Core Focus: Helping SMBs automate their operations
  10-Year Target: $100M ARR
  3-Year Picture: $20M revenue, 50 employees, 3 products
  1-Year Plan: $8M revenue, launch Product #2
  Rocks: 5 set for Q1 2026 (see ceos-rocks)
  Issues: 3 open (see ceos-ids)

  Which section would you like to review or update?
```

### Files

| File | Purpose |
|------|---------|
| `data/vision.md` | The V/TO document (source of truth) |
| `data/accountability.md` | Accountability chart (reference) |
| `data/rocks/` | Current Rocks (for alignment checks) |

---

## ceos-rocks — Quarterly Rocks

Manage quarterly Rocks — the 3-7 most important priorities for the next 90 days. Each Rock has one owner, a measurable outcome, and a due date at quarter end.

### When to Use

- "Set rocks for this quarter" or "let's plan our quarterly priorities"
- "Rock status" or "how are our rocks tracking?"
- "Score rocks" or "end of quarter review"
- "Create a rock" or "add a new rock for [person]"
- "What rocks does [person] own?"

### Three Modes

#### Setting Rocks (Start of Quarter)

Walk through creating each Rock:
1. Reviews the 1-Year Plan for context
2. Collects title, owner, measurable outcome, milestones
3. Optionally collects structured milestones with due dates and attachment references
4. Validates: 3-7 per person, aligned with 1-Year Plan
5. Writes Rock files to `data/rocks/YYYY-QN/`

#### Tracking Rocks (Weekly)

Quick status check:
1. Reads all Rocks for the current quarter
2. Displays status table with milestone progress
3. Updates status (on_track / off_track) with approval

#### Scoring Rocks (End of Quarter)

Binary completion review:
1. For each Rock: "Complete or incomplete?"
2. Updates status to `complete` or `dropped` (no partial credit)
3. Shows completion rate (target: 80%+)

### Example

```
You: "How are our rocks tracking?"

Claude reads data/rocks/2026-Q1/ and shows:

  Rock Status — Q1 2026
  ━━━━━━━━━━━━━━━━━━━━━
  rock-001  Launch Beta Program     brad     on_track   2/3 milestones complete
  rock-002  Hire VP Sales           daniel   off_track  0/4 milestones (1 overdue)
  rock-003  Implement CRM           daniel   on_track   1/2 milestones complete

  Attachments:
    • Beta spec (data/rocks/2026-Q1/rock-001-beta-spec.pdf)

  Any status changes to record?
```

### Rock Status Values

| Status | Meaning | Set When |
|--------|---------|----------|
| `on_track` | Progressing as expected | Default, updated during tracking |
| `off_track` | Behind or at risk | Updated during tracking |
| `complete` | Done — measurable outcome achieved | End-of-quarter scoring |
| `dropped` | No longer a priority | End-of-quarter scoring |

### Files

| File | Purpose |
|------|---------|
| `data/rocks/YYYY-QN/` | Rock files for each quarter |
| `data/vision.md` | 1-Year Plan (for alignment checks) |
| `templates/rock.md` | Template for new Rock files |

---

## ceos-scorecard — Weekly Measurables

Manage the weekly Scorecard — the 5-15 numbers that tell you the health of your business at a glance.

### When to Use

- "Log scorecard" or "enter this week's numbers"
- "Define a new metric" or "add a metric to the scorecard"
- "How are our metrics?" or "scorecard trend"
- "Show the scorecard" or "weekly numbers"
- "Which metrics are off track?"

### Three Modes

#### Define Metrics

Set up or modify the metrics your team tracks:
1. Reads current metrics from `data/scorecard/metrics.md`
2. Collects: metric name, owner, goal, frequency, green/red thresholds
3. Validates: 5-15 metrics total, one owner each, measurable
4. Updates the metrics definition file

#### Log Weekly

Record this week's numbers:
1. Determines current ISO week (YYYY-WNN format)
2. Prompts for each metric's value
3. Auto-calculates on_track / off_track against thresholds
4. Writes to `data/scorecard/weeks/YYYY-WNN.md`

#### Trend Analysis

Review metrics over time:
1. Reads the last 13 weeks of scorecard data
2. Shows per-metric trend with on/off track history
3. Flags concerning patterns:
   - 3+ consecutive weeks off-track
   - Declining trend over 4+ weeks
   - More than 50% of weeks off-track

### Example

```
You: "Log this week's scorecard"

Claude reads metrics.md, then asks for each value:

  Logging Scorecard — 2026-W07
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Weekly Revenue (brad) — Goal: $50K
    This week's value: $52K → on_track ✓

  New Customers (daniel) — Goal: 10
    This week's value: 7 → off_track ✗

  NPS (brad) — Goal: 70
    This week's value: 72 → on_track ✓

  Save this week's scorecard?
```

### Week Format

Weeks follow ISO 8601: `YYYY-WNN` (e.g., `2026-W07`). Week 1 is the week containing the first Thursday of the year.

### Files

| File | Purpose |
|------|---------|
| `data/scorecard/metrics.md` | Metric definitions (names, owners, goals, thresholds) |
| `data/scorecard/weeks/YYYY-WNN.md` | Weekly scorecard entries |
| `templates/scorecard-metrics.md` | Template for metrics definition |
| `templates/scorecard-week.md` | Template for weekly entries |

---

## ceos-l10 — Level 10 Meetings

Facilitate the Level 10 (L10) Meeting — the weekly 90-minute leadership meeting that keeps the team aligned, accountable, and solving problems.

### When to Use

- "Run L10" or "start our L10"
- "Level 10 meeting" or "weekly meeting"
- "Start our meeting" or "let's do our weekly"
- "Review last week's L10" or "what were our to-dos?"

### The 7-Section Agenda

| # | Section | Time | What Happens |
|---|---------|------|-------------|
| 1 | Segue | 5 min | Personal + professional good news |
| 2 | Scorecard Review | 5 min | Review weekly metrics, flag off-track items |
| 3 | Rock Review | 5 min | Quick on/off track check for each Rock |
| 4 | Headlines | 5 min | Customer and employee news — no discussion |
| 5 | To-Do Review | 5 min | Check last week's To-Dos (target: 90%+ done) |
| 6 | IDS | 60 min | Identify, Discuss, Solve top 3 issues |
| 7 | Conclude | 5 min | New To-Dos, cascading messages, rating (target: 8+/10) |

### Data Integration

The L10 skill pulls real data from your CEOS repository:

| Section | Reads From |
|---------|-----------|
| Scorecard Review | `data/scorecard/weeks/` (latest week) |
| Rock Review | `data/rocks/[current-quarter]/` |
| To-Do Review | Previous L10 in `data/meetings/l10/` |
| IDS | `data/issues/open/` + new issues raised |

### Example

```
You: "Run our L10"

Claude creates data/meetings/l10/2026-02-13.md and guides you through:

  L10 Meeting — 2026-02-13
  ━━━━━━━━━━━━━━━━━━━━━━━━

  § 1. Segue (5 min)
  Brad, share one personal and one professional good news.
  ...

  § 2. Scorecard Review (5 min)
  Scorecard — Week 07:
    Weekly Revenue: $52K (goal: $50K) ✓
    New Customers: 7 (goal: 10) ✗ → add to Issues?
  ...

  [continues through all 7 sections]
```

### Files

| File | Purpose |
|------|---------|
| `data/meetings/l10/YYYY-MM-DD.md` | L10 meeting notes |
| `data/scorecard/weeks/` | Latest scorecard data |
| `data/rocks/[quarter]/` | Current Rocks |
| `data/issues/open/` | Open issues |
| `templates/l10-meeting.md` | Meeting template |

---

## ceos-ids — Issue Resolution

Run the IDS (Identify, Discuss, Solve) process — the EOS method for resolving issues systematically.

### When to Use

- "We have an issue" or "add to the issues list"
- "IDS this" or "let's identify discuss solve"
- "What are our open issues?" or "show the issues list"
- "Solve [issue]" or "discuss [issue]"
- "Close this issue" or "mark [issue] as solved"
- During L10 meetings when the IDS section begins

### Four Modes

#### List Issues

Display all open issues sorted by priority:

```
Open Issues (6 total):
━━━━━━━━━━━━━━━━━━━━
P1  issue-003  Slow customer onboarding     [process]  identified
P1  issue-007  Key account churning          [people]   discussed
P2  issue-001  Reporting gaps in dashboard   [data]     identified
P3  issue-005  Misaligned marketing spend    [vision]   identified
P4  issue-002  Office Wi-Fi unreliable       [process]  identified
P5  issue-008  Update team photo on website  [process]  identified
```

#### Create Issue (Identify)

1. Name the issue
2. Dig for root cause using the 5 Whys technique
3. Classify: priority (1-5) and category
4. Generate unique ID
5. Write to `data/issues/open/`

#### Discuss

Capture each person's perspective on an identified issue. Update status to `discussed`.

#### Solve

Create at least one To-Do with an owner and due date. Move the issue to `data/issues/solved/`.

### Issue Priority

| Priority | Meaning |
|----------|---------|
| 1 | Critical — solve first |
| 2 | High — solve soon |
| 3 | Medium — solve when time allows |
| 4 | Low — solve if capacity allows |
| 5 | Nice-to-have — backlog |

### Issue Categories (The 5 EOS Issue Types)

| Category | What It Covers |
|----------|---------------|
| `people` | Right person, right seat issues |
| `process` | Systems, workflows, efficiency |
| `data` | Metrics, reporting, information gaps |
| `vision` | Alignment with V/TO, Core Focus |
| `traction` | Execution, accountability, follow-through |

### IDS Stages

| Stage | Meaning |
|-------|---------|
| `identified` | Root cause found, not yet discussed |
| `discussed` | Perspectives captured, not yet solved |
| `solved` | To-Dos created, ready to move to solved/ |

### Example

```
You: "We have an issue with customer onboarding"

Claude walks through IDS:

  § Identify — What's the real issue?

  "Why is onboarding slow?"
  → "Because the setup process has too many steps"

  "Why does it have too many steps?"
  → "Because we added steps for edge cases that rarely happen"

  "Why weren't those edge cases handled differently?"
  → "Because we never reviewed the flow after launch"

  Root cause: No post-launch review process for customer flows.

  Priority: 1 (Critical)
  Category: process

  § Discuss — [captured during L10 or dedicated session]

  § Solve —
  | Action | Owner | Due Date |
  |--------|-------|----------|
  | Audit onboarding flow, remove unnecessary steps | brad | 2026-02-20 |
  | Create quarterly UX review process | daniel | 2026-02-20 |

  Issue moved to data/issues/solved/
```

### Files

| File | Purpose |
|------|---------|
| `data/issues/open/` | Open issues awaiting resolution |
| `data/issues/solved/` | Resolved issues (archive) |
| `templates/issue.md` | Template for new issue files |

---

## ceos-todos — To-Do Tracking

Track To-Dos — the concrete actions that bridge meetings and execution. Every To-Do has one owner, a due date, and a source. EOS teams target 90%+ weekly completion rate.

### When to Use

- "Show my to-dos" or "what's on my list?"
- "Create a to-do" or "add a to-do for [person]"
- "Mark to-do done" or "complete [to-do]"
- "To-do review" or "how's our completion rate?"
- "What to-dos are overdue?"

### Four Modes

| Mode | What Happens |
|------|-------------|
| **List** | Shows all open To-Dos grouped by owner with due dates and overdue indicators |
| **Create** | Adds a To-Do with title, owner, due date, and source |
| **Complete** | Marks To-Do(s) as done, records completion date |
| **Review** | Weekly completion rate report with patterns and flags |

### To-Do Status Values

| Status | Meaning |
|--------|---------|
| `open` | Not yet done |
| `complete` | Done — binary, no partial credit |

Overdue is computed (not stored): `status: open` + `due` before today.

### Source Values

| Source | Meaning |
|--------|---------|
| `l10` | Created during L10 meeting |
| `ids` | Created during IDS resolution |
| `quarterly` | Created during Quarterly Conversation |
| `adhoc` | Created outside meetings |

### Example

```
You: "Show my to-dos"

Claude reads data/todos/ and shows:

  Open To-Dos (5 total, 1 overdue)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Brad (3 to-dos):
    todo-003  Send revised proposal      due: Feb 20    3 days left
    todo-007  Review hiring pipeline     due: Feb 18    1 day left
    todo-001  Update onboarding doc      due: Feb 10    ⚠️ 4 days overdue

  Daniel (2 to-dos):
    todo-005  Fix dashboard report       due: Feb 22    8 days left
    todo-004  Schedule vendor call       due: Feb 15    due today

  Summary: 5 open | 1 overdue | 2 owners
```

### Files

| File | Purpose |
|------|---------|
| `data/todos/` | To-Do files (one file per To-Do) |
| `templates/todo.md` | Template for new To-Do files |

---

## ceos-accountability — Accountability Chart

Manage the Accountability Chart — the organizational structure that defines seats, owners, and roles. View the current chart, update seats (add, modify, remove), and audit for structural issues.

### When to Use

- "Show the accountability chart" or "who owns what?"
- "Add a new seat" or "we need a VP of Product"
- "Audit the org chart" or "check for empty seats"
- "Update roles for [seat]" or "change seat ownership"
- "How many seats does [person] own?"

### Three Modes

| Mode | What Happens |
|------|-------------|
| **View** | Displays the chart with seats, owners, role counts, and summary stats |
| **Update** | Add, modify, or remove seats. Shows diff before every write |
| **Audit** | Structural checks (5 roles per seat, placeholders, staleness), cross-reference with `data/people/`, multi-seat and empty seat detection |

### Seat Structure

Every seat has:
- **One owner** (a person's name, or `[Name]` if unfilled)
- **Five roles** (the key responsibilities for that seat, per EOS methodology)
- **Position** in the hierarchy (implicit from order in the file)

### Audit Flags

| Flag | Meaning |
|------|---------|
| `✅` | Seat fully defined — owner and 5 roles |
| `⚠️` | Warning — missing person file, name mismatch, or multi-seat owner |
| `🔴` | Error — empty seat, missing roles, or placeholder text |

### Example

```
You: "Audit the accountability chart"

Claude reads data/accountability.md + data/people/ and shows:

  Accountability Chart Audit
  ━━━━━━━━━━━━━━━━━━━━━━━━━━

  | Seat        | Owner       | Roles | Status |
  |-------------|-------------|-------|--------|
  | Visionary   | Brad Feld   | 5/5   | ✅     |
  | Integrator  | Sarah Chen  | 5/5   | ✅     |
  | VP Sales    | Mike Torres | 5/5   | ✅     |
  | Operations  | (empty)     | 3/5   | 🔴     |

  ⚠️  Operations seat is empty — hiring gap
  ⚠️  Mike Torres has no person file — create one?

  Overall: 3/4 seats defined | 1 empty seat
```

### Files

| File | Purpose |
|------|---------|
| `data/accountability.md` | The Accountability Chart (source of truth) |
| `templates/accountability.md` | Template for new charts |
| `data/people/` | Person files (cross-reference for Audit) |

---

## ceos-people — People Analyzer

Evaluate whether team members are the right people (Core Values alignment) in the right seats (GWC: Get it, Want it, Capacity). Manage people evaluations, run quarterly reviews, and flag below-the-bar situations for action.

### When to Use

- "Evaluate [person]" or "run the people analyzer"
- "Are we right people, right seats?"
- "Quarterly people review" or "review the team"
- "Who's below the bar?"
- "GWC check on [person]"

### Three Modes

| Mode | What Happens |
|------|-------------|
| **Evaluate** | Rate a person against Core Values (+, +/-, -) and GWC (Get/Want/Capacity). Three strikes rule flags Core Values misalignment. Suggests status: right_person_right_seat, below_bar, wrong_seat, or evaluating |
| **Review** | Summary table of all people evaluations with status flags, bar percentage (target: 80%+), and stale-evaluation detection |
| **Quarterly** | Walks through every seat on the Accountability Chart, offers re-evaluate or update notes, tracks progress, and flags empty seats for hiring |

### Core Values Rating

| Rating | Meaning |
|--------|---------|
| `+` | Lives this value most of the time |
| `+/-` | Sometimes demonstrates, sometimes doesn't |
| `-` | Rarely or never demonstrates |

Three or more `+/-` or `-` ratings = "wrong person" (Core Values misalignment).

### GWC Dimensions

| Dimension | Question |
|-----------|----------|
| **Get it** | Do they truly understand the role? |
| **Want it** | Do they genuinely want the work? |
| **Capacity** | Can they do it? |

All three must be **true** for "right seat."

### Example

```
You: "Evaluate Brad"

Claude reads data/vision.md for Core Values and data/accountability.md for seat:

  Core Values Evaluation — Brad Feld
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  | Core Value   | Rating | Notes        |
  |--------------|--------|--------------|
  | Integrity    | +      | Consistently |
  | Innovation   | +      |              |
  | Transparency | +      |              |

  GWC — Brad Feld as Visionary:
    Get it:     ✓ Yes
    Want it:    ✓ Yes
    Capacity:   ✓ Yes

  Suggested status: right_person_right_seat
  Save this evaluation?
```

### Files

| File | Purpose |
|------|---------|
| `data/people/` | Person evaluation files (one per person) |
| `data/vision.md` | Core Values source (read-only) |
| `data/accountability.md` | Seat assignments (read-only) |
| `templates/people-analyzer.md` | Template for new evaluations |

---

## ceos-process — Core Processes

Document, simplify, and audit core company processes — the 6th EOS component. Every company has a handful of core processes that must be documented as checklists, simplified to their essential steps, and followed by all (FBA).

### When to Use

- "Document our sales process" or "create a new process"
- "Show our processes" or "what processes do we have?"
- "Audit process FBA scores" or "how well are we following our processes?"
- "Simplify the hiring process" or "reduce this process to essentials"

### Three Modes

| Mode | What Happens |
|------|-------------|
| **Document** | Create or update a core process. Collects title, owner, purpose, and numbered steps (action verbs). Validates: 3-7 core processes, one owner, 5-20 steps. Assigns unique ID |
| **Audit** | FBA (Followed-By-All) score review across all processes. Flags scores below 80%, audits overdue by 90+ days, and processes still in draft |
| **Simplify** | Apply the 20/80 rule — reduce a process to its essential steps. Shows before/after diff with reduction ratio |

### FBA Scoring

| Score Range | Meaning |
|-------------|---------|
| 80-100% | Strong — process is well followed |
| 50-79% | Needs attention — discuss at L10 |
| Below 50% | Weak — IDS priority |

### Example

```
You: "Audit our process FBA scores"

Claude reads data/processes/ and shows:

  Process FBA Audit
  ━━━━━━━━━━━━━━━━━
  | Process              | Owner  | Status | FBA  | Last Audited |
  |----------------------|--------|--------|------|-------------|
  | Customer Onboarding  | brad   | active | 85%  | 2026-01-15  |
  | Sales Process        | daniel | active | 70%  | 2025-12-01  |
  | Deployment Pipeline  | brad   | active | 95%  | 2026-02-01  |

  ⚠️ Sales Process (70%) is below the 80% target
  Want to update any FBA scores?
```

### Files

| File | Purpose |
|------|---------|
| `data/processes/` | Process documentation files |
| `data/vision.md` | Core Focus reference for alignment |
| `templates/process.md` | Template for new process files |

---

## ceos-quarterly — Quarterly Conversations & 5-5-5

Facilitate the EOS Quarterly Conversation — the formal quarterly check-in between each manager and their direct reports — or the 5-5-5, a lightweight 15-minute version. Both are two-way conversations about alignment, role satisfaction, and obstacles — not performance reviews.

**Not to be confused with** `ceos-quarterly-planning`, which is the team planning session. `ceos-quarterly` is the 1-on-1 conversation.

### When to Use

- "Run quarterly conversation for [person]"
- "5-5-5 with [person]" or "quick quarterly check-in"
- "Quick conversation with [person]" or "quick check-in"
- "Schedule quarterly conversations" or "who needs a quarterly?"
- "Review conversation history for [person]"
- "Quarterly one-on-one" or "manager check-in"

### The 5-Point Agenda (Full Conversation)

| # | Section | Focus |
|---|---------|-------|
| 1 | Core Values Alignment | How are they living the Core Values? |
| 2 | GWC | Do they still Get it, Want it, have Capacity? |
| 3 | Rocks Review | How did their Rocks go this quarter? |
| 4 | Role Expectations | Are roles clear and being met? |
| 5 | Feedback Both Ways | What's working? What's not? |

### The 5-5-5 Format (Quick Check-In)

| # | Section | Duration | Focus |
|---|---------|----------|-------|
| 1 | Employee Speaks | 5 min | Core Values, Rocks, Role (GWC) |
| 2 | Manager Speaks | 5 min | Performance, Wins, Concerns |
| 3 | Together | 5 min | Next Steps, Commitments |

### Four Modes

| Mode | What Happens |
|------|-------------|
| **Facilitate** | Walk through the 5-point agenda for a specific person (30-60 min). Pulls context from vision.md, accountability.md, rocks/, and people/. Records the full conversation |
| **Quick** | Walk through the 5-5-5 format for a specific person (15 min). Same context gathering, lighter output. No formal scoring. Records a quick check-in |
| **Schedule** | Maps every seat on the Accountability Chart to show which conversations are done and which are pending. Shows both full and quick conversations. Flags persons with only quick check-ins |
| **Review** | View conversation history for a person or team. Shows Type column (Full/Quick). Quick entries show `--` for scoring columns. Flags persons needing full conversations |

### Examples

```
You: "5-5-5 with Sarah Chen"

Claude gathers context (vision.md, accountability.md, rocks/) and walks through:

  5-5-5 Quick Check-In — Sarah Chen
  Quarter: 2026-Q1 | Manager: Brad

  ## Employee Speaks (5 min)
  Core Values: [prompts for input]
  Rocks: [shows current Rocks, prompts for status]
  Role (GWC): [prompts for how they feel about their seat]

  ## Manager Speaks (5 min)
  Performance: [prompts]
  Wins: [prompts]
  Concerns: [prompts]

  ## Together (5 min)
  Next Steps: [prompts for agreed actions]
  Commitments: [prompts]

  Save to data/conversations/2026-Q1/sarah-chen-quick.md?
```

```
You: "Schedule quarterly conversations"

Claude reads data/accountability.md and data/conversations/2026-Q1/:

  Quarterly Conversations — 2026-Q1
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  | Manager | Direct Report | Seat       | Status       |
  |---------|---------------|------------|--------------|
  | Brad    | Sarah Chen    | Integrator | Done + Quick |
  | Brad    | Mike Torres   | VP Sales   | Quick only   |
  | Brad    | Alex Kim      | VP Eng     | Pending      |

  Progress: 1/3 full conversations complete (33%)
  Note: Mike Torres has a 5-5-5 but still needs a full conversation.
```

### Files

| File | Purpose |
|------|---------|
| `data/conversations/YYYY-QN/` | Conversation files by quarter (full and quick) |
| `data/vision.md` | Core Values source (read-only) |
| `data/accountability.md` | Seats and reporting structure (read-only) |
| `data/rocks/YYYY-QN/` | Rock files for the quarter (read-only) |
| `data/people/` | People Analyzer evaluations (read-only) |
| `templates/quarterly-conversation.md` | Template for full conversations |
| `templates/quarterly-quick.md` | Template for 5-5-5 quick check-ins |

---

## ceos-annual — Annual Planning

Facilitate the EOS Annual Planning session — the comprehensive year-end process where the leadership team refreshes the V/TO, reviews the outgoing year, and sets the plan for the next year. This is the most comprehensive EOS meeting.

### When to Use

- "Run annual planning" or "annual planning session"
- "Plan next year" or "year in review"
- "Refresh our vision" or "update the V/TO for the year"
- "Annual offsite" or "strategic planning session"

### The 7-Section Agenda

| # | Section | Focus |
|---|---------|-------|
| 1 | Year in Review | Score Q4 Rocks, review annual Scorecard trends, celebrate wins |
| 2 | V/TO Refresh | Update 3-Year Picture, set new 1-Year Plan |
| 3 | Issues Sweep | Clear the long-term issues list via IDS |
| 4 | Organizational Checkup | Review Accountability Chart, run People Analyzer |
| 5 | Set Q1 Rocks | First quarter's Rocks aligned to the new 1-Year Plan |
| 6 | Set Scorecard | Review and update weekly measurables |
| 7 | Conclude | Key decisions, cascading messages, next steps |

### Three Modes

| Mode | What Happens |
|------|-------------|
| **Plan** | Full annual planning session with the 7-section agenda. Reads data from all skills (rocks, scorecard, issues, people, vision). Writes decisions to `data/annual/YYYY-planning.md` |
| **Review Year** | Lighter year-in-review without running the full session. Shows Rock completion by quarter and by person, Scorecard trends, and issues resolved |
| **Refresh V/TO** | Walk through V/TO sections for annual updates. Shows current content with proposed changes and diffs for each section |

### Example

```
You: "Run annual planning"

Claude reads data from all CEOS sources and shows:

  Annual Planning — 2027
  ━━━━━━━━━━━━━━━━━━━━━━
  Date: 2026-12-15
  Attendees: Brad, Daniel, Sarah

  Data loaded:
    V/TO: Last updated 2026-06-01
    Rocks: 22 across 4 quarters
    Scorecard: 48 weeks of data
    Open issues: 8
    People evaluations: 5

  Let's walk through the 7-section agenda.

  § 1. Year in Review
  | Quarter | Total | Complete | Rate |
  |---------|-------|----------|------|
  | Q1      | 5     | 4        | 80%  |
  | Q2      | 6     | 5        | 83%  |
  | Q3      | 5     | 3        | 60%  |
  | Q4      | 6     | 5        | 83%  |
  | Year    | 22    | 17       | 77%  |
```

### Files

| File | Purpose |
|------|---------|
| `data/annual/` | Annual planning session files |
| `data/vision.md` | V/TO document (read + update during refresh) |
| `data/rocks/` | Rock files for all quarters (read-only) |
| `data/scorecard/` | Scorecard data for trend analysis (read-only) |
| `data/issues/` | Open and solved issues (read-only) |
| `data/accountability.md` | Accountability Chart (read-only) |
| `data/people/` | People evaluations (read-only) |
| `templates/annual-planning.md` | Template for new planning files |

---

## ceos-quarterly-planning — Quarterly Planning Session

Facilitate the EOS Quarterly Planning Session — the structured half-day meeting where the leadership team scores outgoing Rocks, reviews Scorecard trends, confirms vision alignment, tackles issues, and sets the next quarter's Rocks.

**Not to be confused with** `ceos-quarterly`, which handles 1-on-1 quarterly conversations. `ceos-quarterly-planning` is the team planning session.

### When to Use

- "Run quarterly planning" or "quarterly planning session"
- "Plan next quarter" or "score rocks and plan next quarter"
- "End of quarter review and planning"
- "Quarterly pulse" or "review the quarter"

### The 6-Section Agenda

| # | Section | Time | Focus |
|---|---------|------|-------|
| 1 | Score Outgoing Rocks | 30 min | Score Rocks, celebrate wins |
| 2 | Scorecard Review | 20 min | 13-week trends, identify patterns |
| 3 | V/TO Check | 20 min | Confirm 1-Year Plan alignment |
| 4 | IDS | 60 min | Tackle long-term issues |
| 5 | Set Next Quarter Rocks | 45 min | New Rocks aligned to 1-Year Plan |
| 6 | Conclude | 15 min | Key decisions, action items |

### Two Modes

| Mode | What Happens |
|------|-------------|
| **Plan** | Full quarterly planning session with the 6-section agenda. Scores outgoing Rocks, reviews 13-week Scorecard trends, confirms V/TO alignment, runs IDS on open issues, and sets next quarter's Rocks |
| **Review Quarter** | Lighter quarterly review without the full session. Shows Rock completion (overall and per person), Scorecard trends, and issues summary |

### Example

```
You: "Run quarterly planning"

Claude reads rocks, scorecard, vision, and issues data:

  Quarterly Planning — Q1 → Q2
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Date: 2026-03-28
  Attendees: Brad, Daniel, Sarah

  § 1. Score Outgoing Rocks — Q1
  | Rock              | Owner  | Status      |
  |-------------------|--------|-------------|
  | Launch Beta       | Brad   | complete ✓  |
  | Partner Outreach  | Daniel | on_track → ?|
  | Redesign Onboard  | Sarah  | dropped ✗   |

  Completion: 1/3 (33%) — Below 80% target ⚠️
  Finalize Partner Outreach: Complete or dropped?
```

### Files

| File | Purpose |
|------|---------|
| `data/quarterly/` | Quarterly planning session files |
| `data/rocks/YYYY-QN/` | Rock files for scoring and reference (read-only) |
| `data/scorecard/` | Scorecard data for trend analysis (read-only) |
| `data/vision.md` | 1-Year Plan for Rock alignment (read-only) |
| `data/issues/` | Open and solved issues (read-only) |
| `templates/quarterly-planning.md` | Template for planning files |

---

## ceos-assistance — The Assistance Track

Manage the daily operational delegation workflow between a leader and their assistant using "The Stack" — a batch delegation queue. Implements the 5 disciplines: batching, The Stack, the daily meeting, the assistant's judgment, and weekly review. Complements `ceos-delegate` (strategic delegation) by managing operational delegation (daily handoffs).

### When to Use

- "Add to the stack" or "stack this for my assistant"
- "Run the daily meeting" or "daily standup with my assistant"
- "Weekly assistance review" or "how's delegation going?"
- "Show stuck items" or "what's been on the stack too long?"

### Key Operations

| Operation | What Happens |
|-----------|-------------|
| **Stack** | Add a new item to The Stack with title, urgency (today/this_week/whenever), and details |
| **Daily** | Run the structured 5-15 minute standup — review pending items, hand off, check progress, add new items |
| **Review** | Weekly summary — stack health, stuck items (3+ days), meeting cadence, delegation trends |

### Stack Item Lifecycle

| Status | Meaning | Set When |
|--------|---------|----------|
| `pending` | On the stack, awaiting handoff | Item creation (Stack mode) |
| `handed_off` | Discussed in daily meeting, assistant working on it | Daily mode |
| `done` | Completed | Daily or Stack mode |

### Urgency Values

| Value | Expected Turnaround |
|-------|-------------------|
| `today` | Same day |
| `this_week` | Within the week |
| `whenever` | Best effort, no time pressure |

### Example

```
> "Add to the stack: Schedule board meeting - this_week"

Added to stack: stack-003 "Schedule board meeting" (this_week)
Stack total: 5 pending items

> "Run the daily meeting"

Daily Standup — 2026-02-16
━━━━━━━━━━━━━━━━━━━━━━━━━
Leader: Brad Feld  |  Assistant: Sarah Chen

🔴 TODAY:
  stack-005: "Call insurance broker" (pending)

📋 PENDING:
  stack-003: "Schedule board meeting" (this_week)
  stack-007: "Order office supplies" (whenever)

🔄 IN PROGRESS:
  stack-001: "Book travel for March" (handed_off — 3 days ago)
```

### Files

| File | Purpose |
|------|---------|
| `data/assistance/stack/` | Stack items — one file per delegation item |
| `data/assistance/daily/` | Daily meeting logs — one file per meeting |
| `data/accountability.md` | Leader-assistant relationship source (read-only) |
| `data/delegate/` | D&E audits for cross-reference in Review mode (read-only) |
| `templates/assistance-stack.md` | Template for new stack items |
| `templates/assistance-daily.md` | Template for daily meeting logs |

---

## ceos-cashflow — The 8 Cash Flow Drivers

Assess and optimize the 8 financial levers that impact cash flow — Price, Volume, COGS/Margin, AR Days, AP Days, Inventory/WIP, Operating Expenses, and Debt Structure. Walk through each driver systematically, set baseline and target metrics, assign owners, and track improvement over time.

### When to Use

- "Assess our cash flow" or "review cash flow drivers"
- "How can we improve cash flow?" or "which financial levers should we pull?"
- "Show cash flow history" or "compare our cash flow assessments"

### Key Operations

| Operation | What Happens |
|-----------|-------------|
| **Assess** | Walk through all 8 drivers — current state, improvement potential (high/medium/low/none), owner, baseline metric, target metric. Prioritize top 3-5 drivers. Create assessment file. |
| **Review** | Quarterly check-in comparing current values to baseline/target. Flags stalling or regressing drivers. Optionally saves as a new assessment. |
| **History** | Chronological timeline of all assessments. Per-driver trend analysis. Insights on consistently prioritized vs. improved drivers. |

### The 8 Cash Flow Drivers

| # | Driver | Question | Example Metric |
|---|--------|----------|---------------|
| 1 | Price | Can we increase prices without losing customers? | Average revenue per unit |
| 2 | Volume | Can we increase units sold? | Monthly units sold |
| 3 | COGS / Margin | Can we reduce direct costs? | Gross margin % |
| 4 | Accounts Receivable (AR) Days | Can we collect payments faster? | Average days to collect |
| 5 | Accounts Payable (AP) Days | Can we extend our payment terms? | Average days to pay |
| 6 | Inventory / WIP | Can we reduce working capital tied up? | Inventory turnover ratio |
| 7 | Operating Expenses | Can we reduce overhead? | OpEx as % of revenue |
| 8 | Debt Structure | Can we optimize our financing? | Interest rate / debt-to-equity |

### Example

```
You: "Let's assess our cash flow drivers"
Claude: Reads previous assessments if any → Walks through 8 drivers
        → For each: current state, potential, owner, metrics
        → Ranks drivers by improvement potential
        → Creates data/cashflow/2026-02-16-assessment.md
```

### Files

| File | Purpose |
|------|---------|
| `data/cashflow/` | Cash flow assessment files (one per assessment) |
| `data/accountability.md` | Owner suggestions from the Accountability Chart (read-only) |
| `data/scorecard/metrics.md` | Metric cross-reference (read-only) |
| `templates/cashflow-assessment.md` | Template for new assessments |

---

## ceos-checkup — Organizational Checkup

Measure organizational health using the EOS Organizational Checkup — a 20-question assessment across the Six Key Components (Vision, People, Data, Issues, Process, Traction). Each leadership team member rates 1-5 on each question.

### When to Use

- "Run the organizational checkup" or "let's do the EOS checkup"
- "How healthy is the organization?" or "team health assessment"
- "Score the six key components"
- "Show checkup history" or "compare team ratings"
- "Are we improving on Vision/People/Data?"

### The 20 Questions

The checkup covers 20 canonical questions grouped by component:

| Component | Questions | Count |
|-----------|-----------|-------|
| Vision | Clear vision, Core Values, Core Focus, 10-Year Target, target market, 3 Uniques | 6 |
| People | Proven process, right people, Accountability Chart, right seats | 4 |
| Issues | Leadership trust, issue resolution | 2 |
| Traction | Rocks, Meeting Pulse, meeting discipline | 3 |
| Process | Core Processes documented | 1 |
| Data | Feedback systems, Scorecard, individual numbers, budget | 4 |

### Three Modes

| Mode | What Happens |
|------|-------------|
| **Run** | Conduct a new checkup. Collects 1-5 ratings from each participant for all 20 questions. Calculates per-component and overall scores. Flags components below 3.0 for IDS attention |
| **Review** | Historical checkup results with trend analysis. Shows score progression across checkups with direction arrows (↑↑, ↑, →, ↓, ↓↓). Flags stale checkups (> 120 days) |
| **Compare** | Alignment analysis between team members' ratings. Surfaces high-variance questions (range >= 3) as discussion topics. Helps teams discover where they see the organization differently |

### Score Interpretation

| Score | Rating | Action |
|-------|--------|--------|
| 4.0-5.0 | Strong | Maintain — this component is working |
| 3.0-3.9 | Needs attention | Discuss at L10 — identify specific gaps |
| < 3.0 | Weak | IDS priority — create issues for action plans |

### Example

```
You: "Show checkup history"

Claude reads data/checkups/ and shows:

  Organizational Checkup History
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  | Date       | Overall | Vision | People | Data | Issues | Process | Traction |
  |------------|---------|--------|--------|------|--------|---------|----------|
  | 2026-02-15 | 4.2     | 4.3    | 4.1    | 4.0  | 4.5    | 3.5     | 4.3      |
  | 2025-11-10 | 3.8     | 4.0    | 3.5    | 3.2  | 4.0    | 3.0     | 3.8      |

  Trend: Overall improving (+0.4). Process still weakest (3.5).
  Want to drill into a specific checkup or component?
```

### Files

| File | Purpose |
|------|---------|
| `data/checkups/` | Checkup result files (one per session) |
| `data/vision.md` | V/TO for Vision context (read-only) |
| `data/accountability.md` | Team structure for participant suggestions (read-only) |
| `data/rocks/` | Current Rocks for Traction context (read-only) |
| `data/scorecard/` | Scorecard for Data context (read-only) |
| `data/people/` | People evaluations for People context (read-only) |
| `data/issues/` | Issues for Issues context (read-only) |
| `templates/checkup.md` | Template for new checkup files |

---

## ceos-delegate — Delegate and Elevate

Categorize a leader's tasks into the Delegate and Elevate 4-quadrant matrix based on enjoyment and competency. Identify what to keep, what to delegate, and create action plans for handing off work.

### When to Use

- "Run delegate and elevate for [person]" or "delegation audit"
- "What should I be delegating?" or "am I doing the right work?"
- "Review delegation progress" or "create a delegation plan"
- "What's in my bottom quadrants?"

### The Four Quadrants

| Quadrant | Enjoyment | Competency | Action |
|----------|-----------|------------|--------|
| **Love It / Great At It** | High | High | Keep — this is your highest and best use |
| **Like It / Good At It** | Medium | High | Delegate when possible |
| **Don't Like It / Good At It** | Low | High | Delegate soon — energy drain |
| **Don't Like It / Not Good At It** | Low | Low | Delegate immediately — bottleneck risk |

Goal: spend 80%+ of time in Quadrant 1.

### Three Modes

| Mode | What Happens |
|------|-------------|
| **Audit** | Build the complete task list (starting from Accountability Chart responsibilities). Categorize each task into quadrants via enjoyment + competency questions. Show distribution and flag delegation priorities |
| **Review** | Summary table of all team members with quadrant counts, delegation progress percentage, and stale-audit detection. Shows trends if multiple audits exist |
| **Plan** | Create concrete delegation plans for Q3/Q4 tasks. Suggests delegates from the Accountability Chart, collects training needs and timelines |

### Example

```
You: "Run delegate and elevate for Brad"

Claude reads data/accountability.md for seat responsibilities, then walks through:

  Delegate and Elevate — Brad Feld
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Quadrant Distribution:
  | Quadrant                        | Count | %   | Action                |
  |---------------------------------|-------|-----|-----------------------|
  | Love It / Great At It           | 5     | 36% | Keep                  |
  | Like It / Good At It            | 3     | 21% | Delegate when possible|
  | Don't Like It / Good At It      | 4     | 29% | Delegate soon         |
  | Don't Like It / Not Good At It  | 2     | 14% | Delegate immediately  |

  Q1 focus: 36% — Target: 80%+
  Tasks to delegate: 6 (43% of total)

  🔴 Delegate Immediately:
    1. Weekly expense reports — Not good at it, doesn't enjoy it
    2. Vendor negotiations — Energy drain and quality risk
```

### Files

| File | Purpose |
|------|---------|
| `data/delegate/` | Delegate and Elevate audit files (one per person) |
| `data/accountability.md` | Seat responsibilities for starter list (read-only) |
| `data/people/` | People evaluations for context (read-only) |
| `templates/delegate.md` | Template for new delegation audits |

---

## ceos-lma — LMA Assessment

Assess leadership and management effectiveness using the LMA (Leadership + Management = Accountability) framework — EOS Toolbox tool #11. Rate yourself on 5 Leadership Practices and 5 Management Practices, calculate scores, and optionally gather 360-degree feedback from direct reports.

### When to Use

- "Run LMA assessment" or "LMA for [person]"
- "How am I doing as a manager?" or "leadership assessment"
- "Show LMA scores" or "team LMA summary"
- "360 feedback for [person]"

### The 10 Practices

#### Leadership Practices

| # | Practice | Description |
|---|----------|-------------|
| 1 | Giving clear direction | Setting vision, priorities, and expectations |
| 2 | Providing the necessary tools | Training, resources, systems, authority |
| 3 | Letting go of the vine | Empowering others, not micromanaging |
| 4 | Acting with the greater good in mind | Decisions for the organization, not self |
| 5 | Taking Clarity Breaks | Strategic thinking time away from day-to-day |

#### Management Practices

| # | Practice | Description |
|---|----------|-------------|
| 1 | Keeping expectations clear | Seat, roles, Rocks, and measurables defined |
| 2 | Communicating well | Open, honest, two-way communication |
| 3 | Maintaining the right meeting pulse | Consistent, productive L10 meetings |
| 4 | Having quarterly conversations | Formal quarterly check-ins with direct reports |
| 5 | Rewarding and recognizing | Acknowledging work, addressing underperformance |

### Three Modes

| Mode | What Happens |
|------|-------------|
| **Assess** | Walk through all 10 practices for a specific person. Rate each 1-5. Calculate Leadership score, Management score, and overall LMA score. Flag practices below 3. Cross-references Clarity Break frequency, L10 meeting pulse, and quarterly conversation data for evidence-based context |
| **Review** | Summary of all managers' LMA scores with team averages and trends over time. Highlights lowest-scoring practices across the team. Flags stale assessments (> 120 days) |
| **360** | Gather feedback from direct reports on a manager's 10 practices. Compare self-assessment vs team perception in a side-by-side table. Flag large gaps (>= 2 points) as discussion topics |

### Example

```
You: "Run LMA for Brad"

Claude reads data/accountability.md for seat, data/clarity/ for break frequency,
data/meetings/l10/ for meeting pulse, data/conversations/ for quarterly frequency:

  LMA Assessment — Brad Feld
  ━━━━━━━━━━━━━━━━━━━━━━━━━━

  Cross-Skill Context:
    Clarity Breaks (last 90 days): 3 sessions
    L10 Meeting Pulse (last 8 weeks): 7/8 weeks
    Quarterly Conversations: 2 this quarter

  Leadership Practices:
  | # | Practice                            | Rating |
  |---|-------------------------------------|--------|
  | 1 | Giving clear direction              | 5      |
  | 2 | Providing the necessary tools       | 4      |
  | 3 | Letting go of the vine              | 4      |
  | 4 | Acting with the greater good in mind| 5      |
  | 5 | Taking Clarity Breaks               | 3      |
  Leadership Score: 4.2

  Management Practices:
  | # | Practice                            | Rating |
  |---|-------------------------------------|--------|
  | 1 | Keeping expectations clear          | 4      |
  | 2 | Communicating well                  | 4      |
  | 3 | Maintaining the right meeting pulse | 4      |
  | 4 | Having quarterly conversations      | 4      |
  | 5 | Rewarding and recognizing           | 3      |
  Management Score: 3.8

  Overall LMA: 4.0 / 5.0
  Leadership + Management = Accountability

  No practices flagged — all rated 3 or above.
  Save this LMA assessment?
```

### Files

| File | Purpose |
|------|---------|
| `data/lma/` | LMA assessment files (one per person) |
| `data/accountability.md` | Management relationships and seat info (read-only) |
| `data/people/` | People evaluations for context (read-only) |
| `data/clarity/` | Clarity Break frequency (read-only) |
| `data/meetings/l10/` | L10 meeting pulse (read-only) |
| `data/conversations/` | Quarterly conversation frequency (read-only) |
| `templates/lma-assessment.md` | Template for new LMA assessments |

---

## ceos-clarity

**Clarity Break — structured leadership reflection**

One of the Five Leadership Abilities in EOS. A Clarity Break is scheduled time to step away from day-to-day work and think strategically: "work ON the business, not IN it." Unlike structured EOS tools, the Clarity Break is intentionally unstructured — this skill provides just enough framework to make it habitual without over-formalizing it.

### Modes

| Mode | What It Does |
|------|-------------|
| **Start** | Guide a live Clarity Break — gather business context, prompt reflection, capture insights |
| **Log** | Record a Clarity Break that already happened (retroactive logging) |
| **History** | Review past Clarity Break notes and identify recurring themes |

### Example

**Start mode:**

```
State of the Business
━━━━━━━━━━━━━━━━━━━━━

1-Year Plan: Launch 3 apps, $1M ARR
Rocks: 4/6 on track (Q1 2026)
  Off track: Hire VP Sales, Partner Program
Scorecard: Revenue on track, NPS off track 3 weeks running
Open Issues: 8 total — top 3: Sales pipeline, Onboarding flow, API stability

Reflection
━━━━━━━━━━

What's working well?
> Product-market fit is strong. Customer retention is above target...

What's not working?
> Sales pipeline is too dependent on one channel...

What's missing?
> We don't have a formal onboarding process for new hires...

What needs to change?
> We need to hire a dedicated sales lead before Q2...

Themes: hiring, sales-pipeline, onboarding
Issues identified: "Sales pipeline depends on single channel"
```

**History mode:**

```
Clarity Break History
━━━━━━━━━━━━━━━━━━━━━

2026-02-14  brad  (45 min)  Themes: hiring, product-market-fit
2026-02-07  brad  (30 min)  Themes: sales-pipeline, hiring
2026-01-31  brad  (60 min)  Themes: product-market-fit, team-culture

Total: 3 Clarity Breaks

Recurring Themes (2+ appearances)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  hiring: 2 times (Feb 14, Feb 7)
  product-market-fit: 2 times (Feb 14, Jan 31)
```

### Files

| File | Purpose |
|------|---------|
| `data/clarity/` | Clarity Break notes (one file per session, YYYY-MM-DD.md) |
| `data/vision.md` | V/TO for strategic context (read-only) |
| `data/rocks/` | Current Rocks for progress context (read-only) |
| `data/scorecard/weeks/` | Recent scorecard data for trend context (read-only) |
| `data/issues/open/` | Open issues for awareness context (read-only) |
| `templates/clarity-break.md` | Template for new Clarity Break files |

---

## ceos-dashboard — State of the Business Summary

A read-only dashboard that aggregates data from all CEOS skills into a single view. Quick pulse check before L10 meetings, weekly reviews, or any time the leadership team needs the big picture.

### When to Use

- "Dashboard" or "show me the dashboard"
- "State of the business" or "how are we doing?"
- "Business health" or "pulse check"
- "Overview" or "what's the state of things?"
- Before L10 meetings for a pre-meeting snapshot

### What It Shows

| Section | Data Source | Summary |
|---------|-----------|---------|
| **V/TO Snapshot** | `data/vision.md` | Core Focus, 10-Year Target, 3-Year Picture, 1-Year Plan |
| **Rock Status** | `data/rocks/[quarter]/` | Current quarter counts: on track, off track, complete, dropped |
| **Scorecard Health** | `data/scorecard/weeks/` | This week's metrics: on track vs off track |
| **Open Issues** | `data/issues/open/` | Count by priority, oldest unresolved |
| **People Summary** | `data/people/` | Team size, flagged evaluations (privacy-aware — no names) |

### Design Principles

- **Read-only** — Dashboard never modifies any data files
- **Graceful degradation** — Missing sections show "No data yet — run `ceos-X` to get started"
- **Cross-skill suggestions** — Each section suggests the relevant skill for taking action

### Example

```
You: "How are we doing?"

Claude reads all CEOS data sources and shows:

  State of the Business
  ━━━━━━━━━━━━━━━━━━━━━
  Date: 2026-02-14

  V/TO — Acme Corp
    Core Focus: Helping SMBs automate operations — B2B SaaS
    10-Year Target: $100M ARR
    1-Year Plan: $8M revenue, launch Product #2

  Rocks — Q1 2026
    Total: 6 | On Track: 4 | Off Track: 2
    Off track: Hire VP Sales (daniel), Partner Program (brad)

  Scorecard — W07
    5 on track | 2 off track
    Off track: New Customers (daniel)

  Open Issues — 8 total
    By priority: 2 P1 | 3 P2 | 2 P3 | 1 P4
    Oldest: Slow customer onboarding (45 days)

  People — 5 team members
    Right person, right seat: 3 | Below bar: 1 | Wrong seat: 1
    2 flagged — review with `ceos-people` for details

  ━━━━━━━━━━━━━━━━━━━━━
  Suggested Actions:
    • Review off-track Rocks with `ceos-rocks`
    • Investigate off-track metrics with `ceos-scorecard`
    • Resolve 2 critical (P1) issues with `ceos-ids`
```

### Distinction from ceos-clarity

Dashboard is a **quick status check** — factual counts and summaries. Clarity Break (`ceos-clarity`) is a **strategic reflection tool** — includes context plus guided reflection prompts. Use dashboard for meetings; use clarity for dedicated thinking time.

### Files

| File | Purpose |
|------|---------|
| `data/vision.md` | V/TO document (read-only) |
| `data/rocks/YYYY-QN/` | Rock files for current quarter (read-only) |
| `data/scorecard/weeks/` | Weekly scorecard entries (read-only) |
| `data/issues/open/` | Open issues (read-only) |
| `data/people/` | People evaluations (read-only) |
| `data/accountability.md` | Accountability chart (read-only) |

---

## ceos-kickoff — EOS Implementation Kickoff

Facilitate the EOS implementation kickoff sequence — Focus Day, Vision Building Day 1, and Vision Building Day 2. These are the foundational sessions where a leadership team first implements EOS.

### When to Use

- "Focus Day" or "run our Focus Day"
- "Vision Building Day" or "VB Day 1" or "VB Day 2"
- "Start EOS" or "implement EOS" or "kick off EOS"
- "First EOS session" or "EOS implementation"

### Key Operations

| Mode | What Happens |
|------|-------------|
| **Focus Day** | Introduces EOS tools, drafts V/TO, creates initial Accountability Chart, brainstorms Rocks, previews L10 format |
| **Vision Building Day 1** | Deep dive into Core Values, Core Focus, 10-Year Target, and Marketing Strategy |
| **Vision Building Day 2** | Completes V/TO with 3-Year Picture, 1-Year Plan, sets formal Rocks, brainstorms Issues List |

### Kickoff Sequence

```
Focus Day          →  VB Day 1         →  VB Day 2         →  Regular EOS Rhythm
(Introduce EOS)       (~30 days later)    (~30 days later)    (L10s, Quarterly, Annual)
```

### Example: Focus Day

```
You: "Let's run our Focus Day"
Claude: Asks for date and attendees
        → Walks through 7 agenda sections:
           1. Welcome & EOS Overview
           2. V/TO Introduction (first pass)
           3. Accountability Chart Draft
           4. Initial Rocks Brainstorm
           5. Scorecard Discussion
           6. L10 Preview
           7. Conclude
        → Shows complete file for approval
        → Saves to data/meetings/kickoff/focus-day-2026-02-14.md
        → Suggests: "Use ceos-accountability to formalize the chart"
```

### Example: Vision Building Day 2

```
You: "Let's do VB Day 2"
Claude: Reads prior Focus Day and VB Day 1 files for context
        → Walks through 5 agenda sections:
           1. 3-Year Picture
           2. 1-Year Plan
           3. Quarterly Rocks Setting
           4. Issues List Brainstorm
           5. Conclude
        → V/TO completion checklist (all 8 sections)
        → Saves to data/meetings/kickoff/vb-day-2-2026-02-14.md
        → Suggests: ceos-vto, ceos-rocks, ceos-ids, ceos-scorecard, ceos-accountability
```

### Files Used

| Path | Purpose |
|------|---------|
| `data/meetings/kickoff/` | Saved kickoff session files (focus-day-*.md, vb-day-1-*.md, vb-day-2-*.md) |
| `data/vision.md` | V/TO for context checking (read-only) |
| `data/accountability.md` | Accountability Chart for context (read-only) |
| `data/rocks/` | Existing Rocks for context (read-only) |
| `data/scorecard/` | Existing scorecard for context (read-only) |
| `data/issues/open/` | Existing issues for context (read-only) |
| `templates/focus-day.md` | Focus Day session template |
| `templates/vb-day-1.md` | Vision Building Day 1 template |
| `templates/vb-day-2.md` | Vision Building Day 2 template |

---

## ceos-trust — The Trust Builders

Facilitate vulnerability-based trust exercises that strengthen the leadership team's relationships, communication, and ability to engage in productive conflict.

### When to Use

- "Let's build team trust" or "run a trust exercise"
- "What's the next trust exercise?" or "show trust progress"
- "Schedule trust exercises for the quarter"
- "Show our trust journey" or "trust exercise history"

### Key Operations

| Operation | What Happens |
|-----------|-------------|
| **Facilitate** | Guides the team through one of 10 progressive trust exercises with full facilitation notes |
| **Schedule** | Plans trust exercises for the quarter, recommending next exercise based on history and 30-day spacing |
| **Review** | Shows trust journey progress — exercises completed, participation trends, vulnerability progression |

### The 10 Trust Exercises (Progressive)

| # | Exercise | Vulnerability Level | Typical Duration |
|---|----------|-------------------|------------------|
| 1 | Personal Histories | Low | 30 min |
| 2 | DISC/Kolbe Sharing | Low | 45 min |
| 3 | Lifeline | Medium | 60 min |
| 4 | One Thing | Medium | 30 min |
| 5 | Feedback Round | Medium | 45 min |
| 6 | Strengths Spotlight | Medium | 45 min |
| 7 | Conflict Norms | Medium | 45 min |
| 8 | Accountability Partners | High | 30 min |
| 9 | Team Effectiveness Debrief | High | 60 min |
| 10 | Vulnerability Circle | High | 45 min |

Exercises are designed to be done in order, building comfort with vulnerability progressively. Teams that skip ahead often find the higher exercises uncomfortable without the foundation.

### Example

```
You: "Let's do a trust exercise"
Claude: Checks trust history → Finds exercises 1-3 completed
        → Recommends Exercise 4 (One Thing)
        → Guides facilitation with setup, time management, and debrief questions
        → Records the session in data/trust/
```

### Key Files

| File | Purpose |
|------|---------|
| `data/trust/` | Trust exercise records (one per session) |
| `data/accountability.md` | Team members for participant validation |
| `data/checkups/` | Organizational checkup for trust-related trends |
| `templates/trust-exercise.md` | Template for new exercise records |

---

## Cross-Skill Workflows

The skills are designed to work together through the natural EOS cadence. Here are common multi-skill workflows:

### Weekly L10 → Scorecard + Rocks + IDS

```
1. ceos-l10 starts the meeting
2. § Scorecard Review pulls data from ceos-scorecard
3. § Rock Review pulls data from ceos-rocks
4. Off-track items drop to the Issues list
5. § IDS uses ceos-ids to resolve top 3 issues
6. New To-Dos recorded in meeting notes
```

### Off-Track Rock → Issue → Solution

```
1. ceos-rocks shows a Rock is off_track during tracking
2. Team creates an Issue: "Why is Rock X off track?"
3. ceos-ids runs the 5 Whys to find root cause
4. To-Dos created to get the Rock back on track
5. Next week's L10 reviews progress
```

### Quarterly Planning → V/TO + Rocks

```
1. ceos-vto reviews the 1-Year Plan
2. Team discusses: "What must we accomplish this quarter?"
3. ceos-rocks creates Rocks aligned with the plan
4. ceos-vto runs alignment check: Rocks ↔ 1-Year Plan
5. Misalignments become Issues for IDS
```

### Scorecard Trend → Escalation → IDS

```
1. ceos-scorecard trend analysis shows 3+ weeks off-track
2. Skill suggests creating an Issue
3. ceos-ids investigates root cause
4. Solution To-Dos assigned to metric owner
5. Future scorecards show whether the fix worked
```

### People Evaluation → Quarterly Conversation

```
1. ceos-people evaluates a team member's Core Values and GWC
2. Quarterly conversation (ceos-quarterly) references those ratings
3. If conversation reveals different ratings, ceos-people is updated
4. Below-bar situations create Issues via ceos-ids
```

### Organizational Checkup → Annual Planning

```
1. ceos-checkup assesses all Six Key Components (20 questions)
2. Low-scoring components surface as IDS priorities
3. ceos-annual references checkup trends during Section 4 (Org Checkup)
4. Year-over-year comparison shows whether the team is improving
```

### Delegate and Elevate → Quarterly Planning

```
1. ceos-delegate audits a leader's tasks into 4 quadrants
2. Q3/Q4 tasks identify what to delegate before next quarter
3. ceos-quarterly-planning considers delegation capacity when setting Rocks
4. Delegation plans inform hiring decisions and role changes
```

### Delegate and Elevate → Assistance Track → Todos

```
1. ceos-delegate identifies tasks in Q3/Q4 for delegation
2. ceos-assistance manages daily handoffs via The Stack
3. Review mode cross-references stuck stack items with D&E audit
4. Recurring stack patterns suggest permanent delegation
5. Action items from daily meetings can become ceos-todos
```

### Trust Builders → Checkup → Annual Planning

```
1. ceos-trust facilitates progressive exercises throughout the quarter
2. Trust exercise history shows team vulnerability progression
3. ceos-checkup People component scores reflect team health improvements
4. ceos-annual references trust journey during organizational review
5. Year-over-year trust patterns inform People component development
```

### Cash Flow Assessment → Rocks / Issues

```
1. ceos-cashflow identifies high-potential drivers during assessment
2. Top-priority drivers may become Rocks via ceos-rocks (e.g., "Reduce AR Days from 45 to 30")
3. Stalling drivers surface as Issues for ceos-ids investigation
4. Scorecard metrics (ceos-scorecard) track driver progress between assessments
5. ceos-quarterly-planning references cash flow trends when setting priorities
```
