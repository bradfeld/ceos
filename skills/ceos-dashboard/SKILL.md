---
name: ceos-dashboard
description: Use when you want a quick snapshot of overall business health across all EOS components
file-access: [data/vision.md, data/rocks/, data/scorecard/, data/issues/open/, data/people/, data/accountability.md]
tools-used: [Read, Glob]
---

# ceos-dashboard

State of the Business summary — a read-only dashboard that aggregates data from all CEOS skills into a single view. Quick pulse check before L10 meetings, weekly reviews, or any time the leadership team needs the big picture.

## When to Use

- "Dashboard" or "show me the dashboard"
- "State of the business" or "how are we doing?"
- "Business health" or "pulse check"
- "Overview" or "what's the state of things?"
- "Quick summary" or "where do we stand?"
- Before L10 meetings for a pre-meeting snapshot

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/vision.md` | V/TO document (Core Focus, targets, plans) |
| `data/rocks/YYYY-QN/` | Rock files for current quarter |
| `data/scorecard/metrics.md` | Metric definitions |
| `data/scorecard/weeks/YYYY-WNN.md` | Weekly scorecard entries |
| `data/issues/open/` | Open issues awaiting resolution |
| `data/people/` | Person evaluation files |
| `data/accountability.md` | Accountability chart (team structure) |

### Design Principles

- **Read-only.** Dashboard never modifies any data files. It reads and summarizes.
- **Graceful degradation.** Missing data sections show guidance, not errors. New CEOS repos with partial setup work fine.
- **Cross-skill coordination.** Each section suggests the relevant skill for taking action. Dashboard presents the data; other skills change it.

## Process

The dashboard has a single mode — it reads all available data and presents a summary.

### Step 1: Determine Current Period

Calculate from today's date:
- **Current quarter:** Jan-Mar = Q1, Apr-Jun = Q2, Jul-Sep = Q3, Oct-Dec = Q4. Format: `YYYY-QN`
- **Current ISO week:** Format: `YYYY-WNN` (Week 1 is the week containing the first Thursday of the year)

### Step 2: V/TO Snapshot

Read `data/vision.md`.

**If the file exists:**
1. Extract the company name from the document header
2. Extract Core Focus (Purpose + Niche) — show as one line
3. Extract 10-Year Target — show as one line
4. Extract 3-Year Picture — show revenue/headcount targets if present
5. Extract 1-Year Plan — show key goals

Display as a compact summary:

```
V/TO — [Company Name]
  Core Focus: [Purpose — Niche]
  10-Year Target: [Target]
  3-Year Picture: [Key metrics]
  1-Year Plan: [Key goals]
```

**If the file does not exist:**
```
V/TO: Not configured. Run `ceos-vto` to set your vision.
```

### Step 3: Rock Status

Read all `.md` files in `data/rocks/[current-quarter]/`.

**If the directory exists and contains files:**
1. Parse each Rock's YAML frontmatter for `status` and `owner`
2. Count by status: `on_track`, `off_track`, `complete`, `dropped`
3. Calculate total Rock count
4. If frontmatter `milestones` array exists, count milestone progress (done vs total)

Display:

```
Rocks — [Quarter]
  Total: [N] | On Track: [N] | Off Track: [N] | Complete: [N] | Dropped: [N]
  [If off-track Rocks exist, list them by owner:]
  Off track: [Rock title] ([owner]), [Rock title] ([owner])
```

**If the directory does not exist or is empty:**
```
Rocks: No Rocks set for [quarter]. Run `ceos-rocks` to set priorities.
```

### Step 4: Scorecard Health

Read `data/scorecard/weeks/[current-ISO-week].md`.

**If the file exists:**
1. Parse the metrics table from the markdown body
2. Count metrics with `on_track` status vs `off_track` status
3. List any off-track metric names

Display:

```
Scorecard — [Week]
  [N] on track | [N] off track
  [If off-track metrics exist:]
  Off track: [Metric name] ([owner]), [Metric name] ([owner])
```

**If the file does not exist:**

Fall back: check for the most recent week file in `data/scorecard/weeks/` (sorted by filename descending). If one exists within the last 2 weeks, show it with a note: "(latest available: [week])".

If no recent files exist:
```
Scorecard: No data for this week. Run `ceos-scorecard` to log.
```

If `data/scorecard/` directory doesn't exist:
```
Scorecard: Not set up yet. Run `ceos-scorecard` to define metrics and log weekly.
```

### Step 5: Open Issues

Read all `.md` files in `data/issues/open/`.

**If the directory exists and contains files:**
1. Parse each issue's YAML frontmatter for `priority` (1-5) and `created` date
2. Count total open issues
3. Count by priority level
4. Calculate age of the oldest issue (days since `created`)

Display:

```
Open Issues — [N] total
  By priority: [N] P1 | [N] P2 | [N] P3 | [N] P4 | [N] P5
  Oldest: [issue title] ([N] days)
```

**If the directory is empty or does not exist:**
```
Open Issues: None. Great work!
```

### Step 6: People Summary

Read all `.md` files in `data/people/` (exclude the `alumni/` subdirectory).

**If the directory exists and contains files:**
1. Parse each person's YAML frontmatter for `status` and `departed`
2. Skip any files where `departed: true`
3. Count total active team members
4. Count by status: `right_person_right_seat`, `below_bar`, `wrong_seat`, `evaluating`
5. Flag any `below_bar` or `wrong_seat` counts (but do NOT expose names — privacy)

Display:

```
People — [N] team members
  Right person, right seat: [N] | Below bar: [N] | Wrong seat: [N] | Evaluating: [N]
```

If there are below_bar or wrong_seat members:
```
  [N] flagged — review with `ceos-people` for details
```

**If the directory is empty or does not exist:**
```
People: No evaluations on file. Run `ceos-people` to evaluate team members.
```

### Step 7: Action Suggestions

After displaying all sections, provide a brief list of suggested next actions based on the data:

- If any Rocks are off-track: "Review off-track Rocks with `ceos-rocks`"
- If any Scorecard metrics are off-track: "Investigate off-track metrics with `ceos-scorecard`"
- If open issues exist with P1 priority: "Resolve critical issues with `ceos-ids`"
- If any people are below_bar or wrong_seat: "Review flagged team members with `ceos-people`"
- If V/TO is missing: "Set your vision with `ceos-vto`"
- If no Rocks exist: "Set quarterly priorities with `ceos-rocks`"

Only show suggestions where action is needed. If everything looks healthy, show:
```
All clear — no immediate action items.
```

## Output Format

The complete dashboard output:

```
State of the Business
━━━━━━━━━━━━━━━━━━━━━
Date: YYYY-MM-DD

V/TO — Acme Corp
  Core Focus: Helping SMBs automate operations — B2B SaaS
  10-Year Target: \$100M ARR
  3-Year Picture: \$20M revenue, 50 employees, 3 products
  1-Year Plan: \$8M revenue, launch Product #2

Rocks — Q1 2026
  Total: 6 | On Track: 4 | Off Track: 2 | Complete: 0 | Dropped: 0
  Off track: Hire VP Sales (daniel), Partner Program (brad)

Scorecard — W07
  5 on track | 2 off track
  Off track: New Customers (daniel), Support Response Time (sarah)

Open Issues — 8 total
  By priority: 2 P1 | 3 P2 | 2 P3 | 1 P4 | 0 P5
  Oldest: Slow customer onboarding (45 days)

People — 5 team members
  Right person, right seat: 3 | Below bar: 1 | Wrong seat: 1 | Evaluating: 0
  2 flagged — review with `ceos-people` for details

━━━━━━━━━━━━━━━━━━━━━
Suggested Actions:
  • Review off-track Rocks with `ceos-rocks`
  • Investigate off-track metrics with `ceos-scorecard`
  • Resolve 2 critical (P1) issues with `ceos-ids`
  • Review flagged team members with `ceos-people`
```

**Graceful degradation example** (new repo with only V/TO set up):

```
State of the Business
━━━━━━━━━━━━━━━━━━━━━
Date: YYYY-MM-DD

V/TO — Acme Corp
  Core Focus: Helping SMBs automate operations — B2B SaaS
  10-Year Target: \$100M ARR

Rocks: No Rocks set for Q1 2026. Run `ceos-rocks` to set priorities.

Scorecard: Not set up yet. Run `ceos-scorecard` to define metrics and log weekly.

Open Issues: None. Great work!

People: No evaluations on file. Run `ceos-people` to evaluate team members.

━━━━━━━━━━━━━━━━━━━━━
Suggested Actions:
  • Set quarterly priorities with `ceos-rocks`
  • Define scorecard metrics with `ceos-scorecard`
  • Evaluate team members with `ceos-people`
```

## Guardrails

- **Read-only ALWAYS.** Dashboard never modifies any data files. It reads, summarizes, and reports. If a user asks to change something from the dashboard context, direct them to the appropriate skill.
- **Suggest skills for action.** Every section that shows a problem ends with a skill suggestion. The user decides whether to act — dashboard never auto-invokes other skills.
- **No auto-invoke.** Never call other skills automatically. Mention `ceos-rocks`, `ceos-scorecard`, `ceos-ids`, `ceos-people`, and `ceos-vto` when relevant, but let the user decide when to switch workflows.
- **Graceful degradation.** Missing data is normal for new CEOS repos. Show helpful guidance ("Run `ceos-X` to get started"), not errors. Never crash or stop because one data source is missing — continue with the others.
- **Current state only.** Dashboard shows the current snapshot — current quarter Rocks, current week Scorecard, currently open Issues. For historical analysis or trends, direct users to specific skills (e.g., `ceos-scorecard` Trend Analysis mode).
- **Privacy-aware.** Don't expose individual names in the People section flags. Show counts ("2 flagged") and suggest `ceos-people` for details. People evaluations are sensitive.
- **Malformed data tolerance.** If a file has invalid YAML frontmatter, skip it with a console note ("Skipping [filename] — invalid frontmatter") and continue. One bad file shouldn't break the entire dashboard.
- **Quarter detection.** Always auto-detect the current quarter from today's date. Don't prompt the user for the quarter — dashboard is meant to be instant.
- **Sensitive data warning.** On first use, remind the user: "Dashboard data may include sensitive business information. Use a private repo."

## Integration Notes

### V/TO (ceos-vto)

- **Read:** Dashboard reads `data/vision.md` for the V/TO Snapshot section. Extracts Core Focus, 10-Year Target, 3-Year Picture, and 1-Year Plan.
- **Suggested flow:** If V/TO is missing, suggest: "Set your vision with `ceos-vto`."

### Rocks (ceos-rocks)

- **Read:** Dashboard reads `data/rocks/[current-quarter]/` for Rock Status. Counts by status, lists off-track Rocks.
- **Suggested flow:** If Rocks are off-track, suggest: "Review off-track Rocks with `ceos-rocks`."

### Scorecard (ceos-scorecard)

- **Read:** Dashboard reads `data/scorecard/weeks/[current-week].md` for Scorecard Health. Falls back to the most recent available week if current week hasn't been logged.
- **Suggested flow:** If metrics are off-track, suggest: "Investigate off-track metrics with `ceos-scorecard`."

### IDS (ceos-ids)

- **Read:** Dashboard reads `data/issues/open/` for Open Issues summary. Counts by priority, identifies the oldest unresolved issue.
- **Suggested flow:** If P1 issues exist, suggest: "Resolve critical issues with `ceos-ids`."

### People Analyzer (ceos-people)

- **Read:** Dashboard reads `data/people/` (excluding `alumni/`) for People Summary. Counts by status, flags below_bar and wrong_seat without exposing names.
- **Suggested flow:** If flagged people exist, suggest: "Review flagged team members with `ceos-people`."

### Clarity Break (ceos-clarity)

- **Distinction:** Both dashboard and ceos-clarity show "State of the Business" context. Dashboard is a **quick status check** — factual counts and summaries. Clarity Break is a **strategic reflection tool** — includes the same context plus guided reflection prompts. Use dashboard for meetings and quick checks; use ceos-clarity for dedicated thinking time.

### Read-Only Principle

**Dashboard never writes to any data files.** It is a pure read-only aggregator across all CEOS data directories. Each data domain has a single writer skill:

| Data | Writer Skill |
|------|-------------|
| `data/vision.md` | `ceos-vto` |
| `data/rocks/` | `ceos-rocks` |
| `data/scorecard/` | `ceos-scorecard` |
| `data/issues/` | `ceos-ids` |
| `data/people/` | `ceos-people` |
| `data/accountability.md` | `ceos-accountability` |

Dashboard reads from all of them, writes to none of them.
