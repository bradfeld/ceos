# Data Format Specification

Technical specification for the CEOS data format. All EOS data is stored as markdown files with YAML frontmatter — human-readable, git-friendly, and parseable by any language.

## Overview

CEOS uses a deliberately simple data format:

- **YAML frontmatter** for structured data (status, priority, dates, IDs)
- **Markdown body** for human-written content (notes, perspectives, outcomes)
- **File-per-record** pattern — each Rock, Issue, To-Do, and meeting is its own file
- **Directory-as-collection** pattern — `data/rocks/2026-Q1/` contains all Q1 Rocks

This format is the **portable contract** that tools depend on. Any tool that can parse YAML + markdown can read CEOS data — you're not locked into Claude Code.

## General Rules

### Frontmatter

YAML frontmatter is delimited by `---` on its own line:

```markdown
---
key: value
another_key: "quoted value"
---

# Markdown body starts here
```

- All date values use ISO 8601: `YYYY-MM-DD`
- All string values with special characters should be quoted
- Enum values are lowercase with underscores: `on_track`, `off_track`

### File Naming

Files that represent individual records follow the pattern:

```
{type}-{NNN}-{slug}.md
```

- `{type}` — the record type (`rock`, `issue`)
- `{NNN}` — zero-padded numeric ID (`001`, `002`, `042`)
- `{slug}` — title slugified (lowercase, hyphens, no special characters)

Examples:
- `rock-001-launch-beta-program.md`
- `issue-003-slow-customer-onboarding.md`

### ID Generation

IDs are sequential within their type and directory. When creating a new record:

1. Scan all existing files in the relevant directories
2. Find the highest numeric ID
3. Increment by 1

For Issues, check **both** `data/issues/open/` and `data/issues/solved/` to avoid ID collisions.

---

## Rock Format

**Location:** `data/rocks/YYYY-QN/rock-NNN-slug.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `rock-001`) |
| `title` | string | Yes | Short description of the Rock |
| `owner` | string | Yes | One person responsible (never shared) |
| `quarter` | string | Yes | Quarter in `YYYY-QN` format (e.g., `2026-Q1`) |
| `status` | enum | Yes | Current status (see below) |
| `created` | date | Yes | Date the Rock was created |
| `due` | date | Yes | Last day of the quarter |
| `milestones` | array | No | Array of milestone objects (see Milestone Object below) |
| `attachments` | array | No | Array of attachment reference objects (see Attachment Object below) |

### Status Values

| Value | Meaning | Set When |
|-------|---------|----------|
| `on_track` | Progressing as expected | Default; updated during weekly tracking |
| `off_track` | Behind schedule or at risk | Updated during weekly tracking |
| `complete` | Measurable outcome achieved | End-of-quarter scoring only |
| `dropped` | No longer a priority | End-of-quarter scoring only |

### Body Structure

```markdown
# [Rock Title]

## Measurable Outcome

[Specific, verifiable definition of "done"]

## Milestones

- [ ] [First milestone]
- [ ] [Second milestone]
- [ ] [Third milestone]

## Notes

- YYYY-MM-DD: [Progress update or context]
```

### Milestone Object

Each entry in the optional `milestones` array:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Short description of the milestone |
| `due` | date | No | Target completion date (ISO 8601: `YYYY-MM-DD`) |
| `status` | enum | Yes | Current status: `todo`, `in_progress`, `done` |

Milestone status values:

| Value | Meaning |
|-------|---------|
| `todo` | Not started |
| `in_progress` | Work underway |
| `done` | Milestone achieved |

**Overdue** is computed, not stored: a milestone is overdue if `status` is not `done` and `due` is before today's date.

### Attachment Object

Each entry in the optional `attachments` array:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Relative path from CEOS root (e.g., `data/rocks/2026-Q1/spec.pdf`) |
| `label` | string | No | Display label (defaults to filename if omitted) |

Attachments are references only — the skill displays them but does not manage file uploads or validate file existence.

### Example

```markdown
---
id: rock-001
title: "Launch Beta Program"
owner: "brad"
quarter: "2026-Q1"
status: on_track
created: "2026-01-02"
due: "2026-03-31"
milestones:
  - title: "Beta invitation system built"
    due: "2026-02-01"
    status: done
  - title: "First 10 users onboarded"
    due: "2026-02-15"
    status: done
  - title: "Feedback collection process established"
    due: "2026-03-15"
    status: in_progress
attachments:
  - path: "data/rocks/2026-Q1/rock-001-beta-spec.pdf"
    label: "Original beta program spec"
---

# Launch Beta Program

## Measurable Outcome

Beta program launched with 10+ users actively providing feedback.

## Milestones

- [x] Beta invitation system built
- [x] First 10 users onboarded
- [ ] Feedback collection process established

## Notes

- 2026-01-02: Rock created for 2026-Q1
- 2026-01-15: Invitation system complete
- 2026-02-01: 12 users onboarded, ahead of schedule
```

**Note:** The example shows both frontmatter milestones (structured) and markdown checklist milestones (informal). Both are valid. When frontmatter milestones are present, tracking mode uses them for progress computation. The markdown checklist remains for quick human reference.

---

## Issue Format

**Location:** `data/issues/open/issue-NNN-slug.md` (open) or `data/issues/solved/issue-NNN-slug.md` (resolved)

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `issue-001`) |
| `title` | string | Yes | Short description of the issue |
| `priority` | integer | Yes | 1 (critical) to 5 (nice-to-have) |
| `category` | enum | Yes | EOS issue category (see below) |
| `ids_stage` | enum | Yes | Current IDS stage (see below) |
| `created` | date | Yes | Date the issue was identified |

### Priority Values

| Value | Meaning |
|-------|---------|
| `1` | Critical — solve first |
| `2` | High — solve soon |
| `3` | Medium — solve when time allows |
| `4` | Low — solve if capacity allows |
| `5` | Nice-to-have — backlog |

### Category Values (The 5 EOS Issue Types)

| Value | Meaning |
|-------|---------|
| `people` | Right person, right seat issues |
| `process` | Systems, workflows, efficiency |
| `data` | Metrics, reporting, information gaps |
| `vision` | Alignment with V/TO, Core Focus |
| `traction` | Execution, accountability, follow-through |

### IDS Stage Values

| Value | Meaning |
|-------|---------|
| `identified` | Root cause found, not yet discussed |
| `discussed` | Perspectives captured, not yet solved |
| `solved` | To-Dos created, issue resolved |

### Body Structure

```markdown
# [Issue Title]

## Identify

**Stated problem:**
> [What was originally reported]

**Root cause:**
> [After 5 Whys analysis]

## Discuss

- **[Name]:** [Their perspective]
- **[Name]:** [Their perspective]

## Solve

| Action | Owner | Due Date | Done |
|--------|-------|----------|------|
| [Action item] | [Name] | [YYYY-MM-DD] | [ ] |
```

### File Lifecycle

1. Created in `data/issues/open/` with `ids_stage: identified`
2. Updated to `ids_stage: discussed` after discussion
3. Updated to `ids_stage: solved` after To-Dos are created
4. Moved to `data/issues/solved/` when the IDS process is complete

Solved issues are never deleted — they serve as an audit trail.

### Example

```markdown
---
id: issue-003
title: "Slow customer onboarding"
priority: 1
category: process
ids_stage: solved
created: "2026-02-06"
---

# Slow customer onboarding

## Identify

**Stated problem:**
> New customers take 3+ weeks to complete onboarding

**Root cause:**
> Setup flow has 12 steps added for edge cases that affect <5% of users.
> No post-launch review process exists for customer-facing flows.

## Discuss

- **Brad:** We added those steps after two enterprise customers had issues.
  They shouldn't apply to standard tier.
- **Daniel:** Sales team is hearing complaints. It's affecting close rates.

## Solve

| Action | Owner | Due Date | Done |
|--------|-------|----------|------|
| Audit onboarding flow, remove unnecessary steps | brad | 2026-02-20 | [x] |
| Create quarterly UX review process | daniel | 2026-02-20 | [ ] |
```

---

## To-Do Format

**Location:** `data/todos/todo-NNN-slug.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `todo-001`) |
| `title` | string | Yes | Short, action-oriented description |
| `owner` | string | Yes | One person responsible (never shared) |
| `due` | date | Yes | Deadline for completion |
| `status` | enum | Yes | Current status (see below) |
| `source` | enum | Yes | Where the To-Do originated (see below) |
| `created` | date | Yes | Date the To-Do was created |
| `completed_on` | date | No | Date the To-Do was completed (set when status → complete) |

### Status Values

| Value | Meaning |
|-------|---------|
| `open` | Not yet done |
| `complete` | Done — binary, no partial credit |

**Overdue** is computed, not stored: a To-Do is overdue if `status: open` and `due` is before today's date.

### Source Values

| Value | Meaning |
|-------|---------|
| `l10` | Created during an L10 meeting |
| `ids` | Created during IDS issue resolution |
| `quarterly` | Created during a Quarterly Conversation |
| `adhoc` | Created outside of a meeting context |

### Body Structure

```markdown
# [To-Do Title]

## Description

[What needs to be done — specific enough that the owner knows "done"]

## Notes

- YYYY-MM-DD: To-Do created (source: l10)
- YYYY-MM-DD: Completed
```

### Example

```markdown
---
id: todo-003
title: "Send revised proposal to Acme"
owner: "brad"
due: "2026-02-20"
status: complete
source: l10
created: "2026-02-13"
completed_on: "2026-02-18"
---

# Send revised proposal to Acme

## Description

Send the revised proposal with updated pricing to Acme Corp. Include the volume discount table and Q2 timeline.

## Notes

- 2026-02-13: To-Do created (source: l10)
- 2026-02-18: Completed
```

---

## L10 Meeting Format

**Location:** `data/meetings/l10/YYYY-MM-DD.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | date | Yes | Meeting date |
| `attendees` | list | Yes | Names of attendees |
| `rating` | number | No | Average meeting rating (1-10), filled at end |

### Body Structure

The meeting body has 7 numbered sections matching the EOS L10 agenda:

```markdown
# Level 10 Meeting — YYYY-MM-DD

## 1. Segue (5 min)
[Personal/professional good news per attendee]

## 2. Scorecard Review (5 min)
[Metrics table with goal/actual/status]

## 3. Rock Review (5 min)
[Rock status table]

## 4. Headlines (5 min)
[Customer and employee news bullets]

## 5. To-Do Review (5 min)
[To-Do table from previous L10, done/not done]
[Completion rate]

## 6. IDS (60 min)
[Top 3 issues: Identify, Discuss, Solve for each]

## 7. Conclude (5 min)
[New To-Dos table, cascading messages, ratings]
```

### Example Frontmatter

```yaml
---
date: "2026-02-13"
attendees: [brad, daniel, sarah]
rating: 8.3
---
```

---

## Scorecard Week Format

**Location:** `data/scorecard/weeks/YYYY-WNN.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `week` | string | Yes | ISO week in `YYYY-WNN` format (e.g., `2026-W07`) |
| `date` | date | Yes | Date the scorecard was logged |

### Week Format

Weeks follow ISO 8601: `YYYY-WNN` where `NN` is the ISO week number (01-53). Week 1 is the week containing the first Thursday of the year.

### Body Structure

```markdown
# Scorecard — YYYY-WNN

*Logged: YYYY-MM-DD*

| Metric | Owner | Goal | Actual | Status |
|--------|-------|------|--------|--------|
| [name] | [name] | [goal] | [actual] | on_track / off_track |

## Notes

- [Context for off-track metrics]
```

### Status Values

| Value | Meaning |
|-------|---------|
| `on_track` | Meets or exceeds the goal threshold |
| `off_track` | Below the goal threshold |

### Example

```markdown
---
week: "2026-W07"
date: "2026-02-13"
---

# Scorecard — 2026-W07

*Logged: 2026-02-13*

| Metric | Owner | Goal | Actual | Status |
|--------|-------|------|--------|--------|
| Weekly Revenue | brad | $50K | $52K | on_track |
| New Customers | daniel | 10 | 7 | off_track |
| NPS | brad | 70 | 72 | on_track |
| Cash Balance | sarah | $200K | $215K | on_track |

## Notes

- New Customers off-track for second consecutive week. Added to L10 Issues list.
```

---

## Scorecard Metrics Format

**Location:** `data/scorecard/metrics.md`

This file defines the metrics your team tracks. It is not a weekly entry — it's the metric definitions that weekly entries reference.

### Structure

```markdown
# Scorecard Metrics

## [Company Name]

## Metrics

| Metric | Owner | Goal | Frequency | Green | Red |
|--------|-------|------|-----------|-------|-----|
| [name] | [name] | [goal] | Weekly/Monthly | [threshold] | [threshold] |
```

No YAML frontmatter — this is a pure markdown reference document.

### Threshold Format

Green and Red thresholds define when a metric is on_track or off_track:

- `>= $50,000` — on_track when at or above the value
- `< 10` — off_track when below the value

### Example

```markdown
# Scorecard Metrics

## Acme Corp

## Metrics

| Metric | Owner | Goal | Frequency | Green | Red |
|--------|-------|------|-----------|-------|-----|
| Weekly Revenue | brad | $50K | Weekly | >= $50K | < $50K |
| New Customers | daniel | 10 | Weekly | >= 10 | < 10 |
| NPS | brad | 70 | Monthly | >= 70 | < 70 |
| Cash Balance | sarah | $200K | Weekly | >= $200K | < $200K |
| Support Tickets Closed | daniel | 50 | Weekly | >= 50 | < 50 |
```

---

## Vision Format

**Location:** `data/vision.md`

The V/TO (Vision/Traction Organizer) is a pure markdown document — no YAML frontmatter. It contains 8 sections covering the full EOS strategic framework.

### Structure

```markdown
# Vision/Traction Organizer

## [Company Name]

*Last updated: YYYY-MM-DD*

## Core Values
[3-7 guiding principles]

## Core Focus
[Purpose + Niche]

## 10-Year Target
[One big goal]

## Marketing Strategy
[Target Market, 3 Uniques, Proven Process, Guarantee]

## 3-Year Picture
[Revenue, profit, headcount, what it looks like]

## 1-Year Plan
[Revenue goal, profit goal, measurables, goals]

## Quarterly Rocks
[Reference to data/rocks/ — managed by ceos-rocks]

## Issues List
[Reference to data/issues/ — managed by ceos-ids]
```

The Quarterly Rocks and Issues List sections are pointers to other data directories — they're managed by `ceos-rocks` and `ceos-ids` respectively, not edited directly in the V/TO.

---

## Accountability Chart Format

**Location:** `data/accountability.md`

Pure markdown document — no YAML frontmatter. Describes the company's organizational structure using EOS's "right person, right seat" framework.

### Structure

```markdown
# Accountability Chart

## [Company Name]

*Last updated: YYYY-MM-DD*

## [Function Name]

**Owner:** [Name]

| # | Role |
|---|------|
| 1 | [Key responsibility] |
| 2 | [Key responsibility] |
| 3 | [Key responsibility] |
| 4 | [Key responsibility] |
| 5 | [Key responsibility] |
```

Each function is an H2 heading. Roles are listed in a numbered table (5 per seat). The function heading IS the seat — there is no separate "Seat:" field.

---

## Process Format

**Location:** `data/processes/core-process-name.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `process-001`) |
| `title` | string | Yes | Name of the core process |
| `owner` | string | Yes | Person accountable for this process |
| `fba_score` | integer | Yes | Followed By All score (0-100) |
| `last_audited` | date | No | Date of most recent FBA audit |
| `status` | enum | Yes | Current status (see below) |
| `created` | date | Yes | Date the process was created |

### Status Values

| Value | Meaning |
|-------|---------|
| `draft` | Process documented but not yet finalized |
| `active` | Process is finalized and being followed |
| `archived` | Process is no longer in use |

### Body Structure

```markdown
# [Process Title]

## Purpose

> [Why this process exists — what outcome it ensures]

## Process Steps

1. [First step — start with an action verb]
2. [Second step]
3. [Continue as needed — aim for 5-20 steps]

## Owner

**[Name]** is accountable for this process being documented, simplified, and followed by all.

## Audit History

- YYYY-MM-DD: [Audit event]
```

### Example

```markdown
---
id: process-001
title: "Customer Onboarding"
owner: "daniel"
fba_score: 80
last_audited: "2026-02-01"
status: active
created: "2026-01-15"
---

# Customer Onboarding

## Purpose

> Ensures every new customer is onboarded consistently and starts getting value within their first week.

## Process Steps

1. Send welcome email with login credentials
2. Schedule kickoff call within 48 hours
3. Walk through initial setup during kickoff
4. Assign dedicated support contact
5. Follow up at day 3, day 7, and day 14

## Owner

**Daniel** is accountable for this process being documented, simplified, and followed by all.

## Audit History

- 2026-01-15: Process created (status: draft)
- 2026-02-01: FBA audit — 80% (4/5 team members following all steps)
```

---

## People Analyzer Format

**Location:** `data/people/firstname-lastname.md` (active) or `data/people/alumni/firstname-lastname.md` (departed)

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Full name of the person |
| `seat` | string | Yes | Seat from the Accountability Chart |
| `core_values` | map | Yes | Map of Core Value names to ratings (`+`, `+/-`, `-`). Keys come from `data/vision.md` |
| `status` | enum | Yes | Overall evaluation status (see below) |
| `gwc` | object | Yes | Get It / Want It / Capacity assessment (see GWC Object below) |
| `last_evaluated` | date | Yes | Date of most recent evaluation |
| `created` | date | Yes | Date the record was created |
| `departed` | boolean | Yes | `true` if the person has left the organization |

### Status Values

| Value | Meaning |
|-------|---------|
| `right_person_right_seat` | Meets Core Values bar AND passes GWC |
| `below_bar` | Falls short on Core Values or GWC — action plan needed |
| `wrong_seat` | Right person but wrong seat — consider moving |
| `evaluating` | Not yet fully assessed |

### Core Values Rating

| Rating | Meaning |
|--------|---------|
| `+` | Exhibits the value most of the time |
| `+/-` | Exhibits the value sometimes |
| `-` | Rarely exhibits the value |

A person is a "right person" if they have mostly `+` ratings across all Core Values.

### GWC Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `get` | boolean or null | Yes | Do they truly understand the role? (`true`, `false`, or `null` if not yet evaluated) |
| `want` | boolean or null | Yes | Do they genuinely want the role? |
| `capacity` | boolean or null | Yes | Do they have the capacity to do the job well? |

A person is in the "right seat" if all three GWC fields are `true`.

### Body Structure

```markdown
# [Full Name] — People Analyzer

## Core Values Evaluation

| Core Value | Rating | Notes |
|------------|--------|-------|
| [Value 1] | [+/+/-/-] | |

**Right person?** [Yes / No / Evaluating]

## GWC Evaluation — [Seat Name]

### Get It
> [Notes]

### Want It
> [Notes]

### Capacity to Do It
> [Notes]

**Right seat?** [Yes / No / Evaluating]

## Status

**Overall:** [status value]

## Development Plan

- [ ] [Action item if below the bar]

## Evaluation History

- YYYY-MM-DD: [Evaluation event]
```

### Example

```markdown
---
name: "Sarah Chen"
seat: "VP Sales"
core_values:
  Integrity: "+"
  Customer First: "+"
  Continuous Improvement: "+/-"
status: right_person_right_seat
gwc:
  get: true
  want: true
  capacity: true
last_evaluated: "2026-02-01"
created: "2026-01-15"
departed: false
---

# Sarah Chen — People Analyzer

## Core Values Evaluation

| Core Value | Rating | Notes |
|------------|--------|-------|
| Integrity | + | Consistently transparent with team and customers |
| Customer First | + | Drives all decisions from customer perspective |
| Continuous Improvement | +/- | Strong on process, could improve on self-development |

**Right person?** Yes

## GWC Evaluation — VP Sales

### Get It
> Understands the sales cycle, market dynamics, and team culture deeply.

### Want It
> Energized by the role. Voluntarily takes on stretch goals.

### Capacity to Do It
> Has the skills, time, and emotional bandwidth to excel.

**Right seat?** Yes

## Status

**Overall:** right_person_right_seat

## Development Plan

*No development plan needed — above the bar.*

## Evaluation History

- 2026-01-15: Initial evaluation created
- 2026-02-01: Quarterly review — confirmed right person, right seat
```

---

## Quarterly Conversation Format

**Location:** `data/conversations/YYYY-QN/firstname-lastname.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | No | Conversation type: `full` (default) or `quick` |
| `person` | string | Yes | Full name of the direct report |
| `manager` | string | Yes | Full name of the manager |
| `quarter` | string | Yes | Quarter in `YYYY-QN` format (e.g., `2026-Q1`) |
| `date` | date | Yes | Date the conversation took place |
| `core_values_rating` | integer or null | No | Count of `+` ratings out of total Core Values |
| `gwc_status` | enum or null | No | GWC assessment result (see below) |
| `rocks_completion_rate` | number or null | No | Percentage of Rocks completed (0-100), null if no Rocks |

### GWC Status Values

| Value | Meaning |
|-------|---------|
| `pass` | All three GWC dimensions are `true` |
| `fail` | One or more GWC dimensions are `false` |
| `evaluating` | Not yet fully assessed |

### Type Values

| Value | Meaning |
|-------|---------|
| `full` | Standard Quarterly Conversation (30-60 min, 5-section agenda). This is the default — files without a `type` field are treated as `full`. |
| `quick` | 5-5-5 Quick Check-In (15 min, 3 time-boxed sections). Lightweight touchpoint between full conversations. |

**Backward compatibility:** Existing conversation files without a `type` field are treated as `full`. All reading code must handle the missing field gracefully.

### Body Structure (Full Conversation)

```markdown
# Quarterly Conversation — [Full Name]

**Manager:** [Manager Name]
**Quarter:** YYYY-QN
**Date:** YYYY-MM-DD

---

## 1. Core Values Alignment

| Core Value | Rating | Notes |
|------------|--------|-------|

**Summary:** [Overall assessment]

---

## 2. GWC — Get It, Want It, Capacity

### Get It
> [Notes]

### Want It
> [Notes]

### Capacity
> [Notes]

**Right seat?** [Yes / No / Evaluating]

---

## 3. Rocks Review

| Rock | Status | Notes |
|------|--------|-------|

**Completion rate:** [X/Y — Z%]

---

## 4. Role Expectations

**Clarity:** [Are expectations clearly defined?]
**Delivery:** [Are they meeting those expectations?]
**Gaps:** [Areas where expectations aren't being met?]

---

## 5. Feedback — Both Ways

### Manager → Direct Report
> [Feedback]

### Direct Report → Manager
> [Feedback]

---

## Action Items

- [ ] [Action item]

## Conversation History

- YYYY-MM-DD: Quarterly conversation conducted
```

### Example

```markdown
---
person: "Sarah Chen"
manager: "Brad"
quarter: "2026-Q1"
date: "2026-03-28"
core_values_rating: 2
gwc_status: pass
rocks_completion_rate: 75
---

# Quarterly Conversation — Sarah Chen

**Manager:** Brad
**Quarter:** 2026-Q1
**Date:** 2026-03-28

---

## 1. Core Values Alignment

| Core Value | Rating | Notes |
|------------|--------|-------|
| Integrity | + | Consistently transparent |
| Customer First | + | Drives customer-focused decisions |
| Continuous Improvement | +/- | Could invest more in self-development |

**Summary:** Strong culture fit. 2 out of 3 Core Values at +.

---

## 3. Rocks Review

| Rock | Status | Notes |
|------|--------|-------|
| Launch partner program | complete | Launched on schedule |
| Hit $200K quarterly revenue | complete | Exceeded by 5% |
| Hire 2 SDRs | off_track | Only hired 1, pipeline thin |

**Completion rate:** 2/3 — 67%

---

## Action Items

- [ ] Resume SDR hiring push by April 15
- [ ] Start self-development plan for Q2

## Conversation History

- 2026-03-28: Q1 quarterly conversation conducted
```

---

## 5-5-5 Quick Note Format

**Location:** `data/conversations/YYYY-QN/firstname-lastname-quick.md`

The 5-5-5 is a lightweight 15-minute check-in between a manager and direct report. Three time-boxed sections (5 minutes each) cover Core Values, Rocks, and Roles (GWC). Unlike the full Quarterly Conversation, the 5-5-5 is informal — no formal scoring, ratings, or pass/fail assessments.

### Quick Note Frontmatter

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | Must be `quick` |
| `person` | string | Yes | Full name of the direct report |
| `manager` | string | Yes | Full name of the manager |
| `quarter` | string | Yes | Quarter in `YYYY-QN` format |
| `date` | date | Yes | Date the check-in took place |
| `core_values_rating` | null | No | Always `null` for quick (no formal scoring) |
| `gwc_status` | null | No | Always `null` for quick (no formal scoring) |
| `rocks_completion_rate` | null | No | Always `null` for quick (no formal scoring) |

**Scoring fields:** Set to `null` to distinguish "not scored" (quick check-in) from "scored poorly" (full conversation). This is intentional — the 5-5-5 is informal by design.

### Quick Note Body Structure

```markdown
# 5-5-5 Check-In — [Full Name]

**Manager:** [Manager Name]
**Quarter:** YYYY-QN
**Date:** YYYY-MM-DD

---

## Employee Speaks (5 min)

**Core Values:** [How are they living the Core Values?]

**Rocks:** [How are their Rocks going?]

**Role (GWC):** [How do they feel about their seat?]

---

## Manager Speaks (5 min)

**Performance:** [How is the employee doing?]

**Wins:** [What's going well?]

**Concerns:** [Any issues to address?]

---

## Together (5 min)

**Next Steps:**
- [Agreed action or commitment]

**Commitments:**
- [What each person will do before next check-in]

---

## Conversation History

- YYYY-MM-DD: 5-5-5 check-in conducted
```

### Quick Note Example

```markdown
---
type: quick
person: "Sarah Chen"
manager: "Brad"
quarter: "2026-Q1"
date: "2026-02-14"
core_values_rating: null
gwc_status: null
rocks_completion_rate: null
---

# 5-5-5 Check-In — Sarah Chen

**Manager:** Brad
**Quarter:** 2026-Q1
**Date:** 2026-02-14

---

## Employee Speaks (5 min)

**Core Values:** Feeling strong on Integrity and Customer First. Wants to invest more in Continuous Improvement — thinking about a course on data analytics.

**Rocks:** Partner program launch is on track. Revenue Rock is ahead of target. SDR hiring Rock is behind — pipeline is thin.

**Role (GWC):** Loves the role. Gets it, wants it. Feels stretched on capacity with the hiring push but managing.

---

## Manager Speaks (5 min)

**Performance:** Strong quarter so far. Two of three Rocks on track is solid.

**Wins:** Partner program launch was excellent — smooth execution, good feedback from partners.

**Concerns:** SDR hiring needs attention. One hire out of two isn't enough runway for Q2 targets.

---

## Together (5 min)

**Next Steps:**
- Sarah to work with recruiter on expanding SDR candidate pipeline by Feb 21
- Brad to review whether Q2 revenue target needs adjustment given SDR gap

**Commitments:**
- Sarah: Weekly SDR pipeline update to Brad every Friday
- Brad: Approve data analytics course budget by next week

---

## Conversation History

- 2026-02-14: 5-5-5 check-in conducted
```

---

## Annual Planning Format

**Location:** `data/annual/YYYY-planning.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `year` | string | Yes | Year being planned (e.g., `2026`) |
| `date` | date | Yes | Date the planning session took place |
| `attendees` | string | Yes | Comma-separated list of attendees |
| `location` | string | No | Where the session was held |

### Body Structure

The annual planning session has 7 numbered sections:

```markdown
# Annual Planning — YYYY

## 1. Year in Review
[Score Q4 Rocks, review annual Scorecard trends, celebrate wins]

## 2. V/TO Refresh
[Review and update the full Vision/Traction Organizer]

## 3. Issues Sweep
[Clear the long-term issues list via IDS]

## 4. Organizational Checkup
[Review Accountability Chart and People Analyzer]

## 5. Set Q1 Rocks
[First quarter Rocks aligned to new 1-Year Plan]

## 6. Set Scorecard
[Review and update weekly measurables]

## 7. Conclude
[Key decisions, cascading messages, action items, next steps]

## Session Notes
- YYYY-MM-DD: Annual planning session conducted
```

### Example Frontmatter

```yaml
---
year: "2026"
date: "2026-01-10"
attendees: "brad, daniel"
location: "Offsite — Denver"
---
```

---

## Quarterly Planning Format

**Location:** `data/quarterly/YYYY-QN-planning.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `quarter` | string | Yes | Quarter in `YYYY-QN` format (e.g., `2026-Q2`) |
| `date` | date | Yes | Date the planning session took place |
| `attendees` | string | Yes | Comma-separated list of attendees |
| `location` | string | No | Where the session was held |

### Body Structure

The quarterly planning session has 6 numbered sections:

```markdown
# Quarterly Planning — YYYY-QN

## 1. Score Outgoing Rocks
[Review and score the outgoing quarter's Rocks]

## 2. Scorecard Review
[Review 13-week trends and identify patterns]

## 3. V/TO Check
[Confirm vision alignment, review 1-Year Plan progress]

## 4. IDS
[Identify, Discuss, Solve long-term issues]

## 5. Set Next Quarter Rocks
[Rocks for next quarter aligned to 1-Year Plan]

## 6. Conclude
[Key decisions, cascading messages, action items, next steps]

## Session Notes
- YYYY-MM-DD: Quarterly planning session conducted
```

### Example Frontmatter

```yaml
---
quarter: "2026-Q2"
date: "2026-04-01"
attendees: "brad, daniel"
location: "Office"
---
```

---

## Organizational Checkup Format

**Location:** `data/checkups/YYYY-MM-DD.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | date | Yes | Date the checkup was conducted |
| `participants` | array | Yes | Array of participant objects (see Participant Object below) |
| `status` | enum | Yes | Current status (see below) |
| `overall_score` | number or null | No | Average of all 20 questions across all participants (1.0-5.0) |
| `component_scores` | object | No | Per-component averages (see Component Scores below) |

### Participant Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Participant's name |
| `ratings` | array | Yes | Array of 20 integers (1-5), indexed by question number (index 0 = Question 1) |

### Status Values

| Value | Meaning |
|-------|---------|
| `in_progress` | Ratings collected but analysis not yet complete |
| `complete` | All ratings collected and scores computed |

### Rating Scale

| Value | Meaning |
|-------|---------|
| 1 | Strongly disagree |
| 2 | Disagree |
| 3 | Neutral |
| 4 | Agree |
| 5 | Strongly agree |

### Component Scores Object

Scores are averages of specific question groups:

| Field | Questions | Description |
|-------|-----------|-------------|
| `vision` | 1-6 | Clarity of vision, Core Values, Core Focus, 10-Year Target |
| `people` | 7-10 | Right people, right seats, accountability |
| `issues` | 11-12 | Open communication, IDS effectiveness |
| `traction` | 13-15 | Rocks, Meeting Pulse, discipline |
| `process` | 16 | Core Processes documented and followed |
| `data` | 17-20 | Feedback systems, Scorecard, metrics, budget |

### Body Structure

```markdown
# Organizational Checkup — YYYY-MM-DD

## Overall Summary

| Component | Score | Rating |
|-----------|-------|--------|
| Vision | [X.X] | [Strong/Good/Needs Attention/Weak] |
| People | [X.X] | |
| Data | [X.X] | |
| Issues | [X.X] | |
| Process | [X.X] | |
| Traction | [X.X] | |

**Rating guide:** 5.0 = Strong, 4.0+ = Good, 3.0-3.9 = Needs Attention, <3.0 = Weak

## Component Scores

### Vision (Questions 1-6)
[Per-question rating table with participant columns]

### People (Questions 7-10)
[Per-question rating table]

### Data (Questions 17-20)
[Per-question rating table]

### Issues (Questions 11-12)
[Per-question rating table]

### Process (Question 16)
[Per-question rating table]

### Traction (Questions 13-15)
[Per-question rating table]

## Strengths
- [Components or questions scoring 4.0+]

## Opportunities
- [Components or questions scoring below 3.0]

## Action Items

| Action | Owner | Due Date | Related Component |
|--------|-------|----------|-------------------|

## Session Notes
- YYYY-MM-DD: Organizational Checkup conducted
```

### Example Frontmatter

```yaml
---
date: "2026-02-15"
participants:
  - name: "Brad"
    ratings: [5, 4, 5, 4, 3, 4, 4, 5, 4, 4, 5, 4, 4, 3, 4, 3, 4, 4, 3, 4]
  - name: "Daniel"
    ratings: [4, 4, 5, 4, 4, 3, 5, 4, 4, 5, 4, 5, 3, 4, 4, 4, 3, 4, 4, 3]
status: complete
overall_score: 4.0
component_scores:
  vision: 4.2
  people: 4.4
  data: 3.6
  issues: 4.5
  process: 3.5
  traction: 3.7
---
```

---

## Delegate and Elevate Format

**Location:** `data/delegate/firstname-lastname.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `person` | string | Yes | Full name of the person |
| `seat` | string | Yes | Current seat from Accountability Chart |
| `date` | date | Yes | Date of the initial audit |
| `status` | enum | Yes | Current status (see below) |
| `quadrant_counts` | object | Yes | Count of tasks in each quadrant (see Quadrant Counts below) |
| `delegation_progress` | object | No | Delegation tracking (see Delegation Progress below) |
| `last_reviewed` | date | Yes | Date of most recent review |

### Status Values

| Value | Meaning |
|-------|---------|
| `active` | Audit is current and being acted on |
| `reviewed` | Recently reviewed, no immediate actions |
| `stale` | Has not been reviewed in 90+ days |

### Quadrant Counts Object

| Field | Quadrant | Description |
|-------|----------|-------------|
| `love_great` | Love It / Great At It | Keep — highest and best use |
| `like_good` | Like It / Good At It | Delegate when possible |
| `not_like_good` | Don't Like It / Good At It | Delegate soon — competent but draining |
| `not_like_not_good` | Don't Like It / Not Good At It | Delegate immediately — bottleneck risk |

### Delegation Progress Object

| Field | Type | Description |
|-------|------|-------------|
| `delegated` | integer | Tasks successfully delegated |
| `total` | integer | Total tasks marked for delegation (bottom two quadrants) |
| `percent` | integer | Percentage complete (0-100) |

### Body Structure

```markdown
# [Person] — Delegate and Elevate

## Quadrant 1: Love It / Great At It

| # | Task / Responsibility | Source |
|---|----------------------|--------|

## Quadrant 2: Like It / Good At It

| # | Task / Responsibility | Source | Delegated? | To Whom |
|---|----------------------|--------|------------|---------|

## Quadrant 3: Don't Like It / Good At It

| # | Task / Responsibility | Source | Delegated? | To Whom |
|---|----------------------|--------|------------|---------|

## Quadrant 4: Don't Like It / Not Good At It

| # | Task / Responsibility | Source | Delegated? | To Whom |
|---|----------------------|--------|------------|---------|

## Delegation Plan

| Task | Delegate To | Training Needed | Timeline | Status |
|------|-------------|----------------|----------|--------|

## Audit History

- YYYY-MM-DD: [Audit event]
```

### Example

```markdown
---
person: "Brad"
seat: "CTO"
date: "2026-02-01"
status: active
quadrant_counts:
  love_great: 5
  like_good: 3
  not_like_good: 2
  not_like_not_good: 1
delegation_progress:
  delegated: 1
  total: 3
  percent: 33
last_reviewed: "2026-02-01"
---

# Brad — Delegate and Elevate

## Quadrant 1: Love It / Great At It

| # | Task / Responsibility | Source |
|---|----------------------|--------|
| 1 | Architecture decisions | CTO role |
| 2 | AI systems design | CTO role |
| 3 | Infrastructure automation | CTO role |
| 4 | Code review | CTO role |
| 5 | Developer tooling | Personal interest |

## Quadrant 4: Don't Like It / Not Good At It

| # | Task / Responsibility | Source | Delegated? | To Whom |
|---|----------------------|--------|------------|---------|
| 1 | Vendor contract negotiation | CTO role | Yes | Daniel |

## Delegation Plan

| Task | Delegate To | Training Needed | Timeline | Status |
|------|-------------|----------------|----------|--------|
| Vendor contracts | Daniel | No | Immediate | [x] Complete |
| Manual QA testing | Future hire | Yes | 2026-Q2 | [ ] Not started |

## Audit History

- 2026-02-01: Initial Delegate and Elevate audit conducted
```

---

## LMA Assessment Format

**Location:** `data/lma/firstname-lastname.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `person` | string | Yes | Full name of the person |
| `seat` | string | Yes | Current seat from Accountability Chart |
| `date` | date | Yes | Date of the initial assessment |
| `status` | enum | Yes | Current status (see below) |
| `leadership_score` | number or null | No | Average of 5 Leadership Practice ratings (1.0-5.0) |
| `management_score` | number or null | No | Average of 5 Management Practice ratings (1.0-5.0) |
| `overall_score` | number or null | No | Average of leadership and management scores |
| `leadership_practices` | object | Yes | Ratings for 5 Leadership Practices (see below) |
| `management_practices` | object | Yes | Ratings for 5 Management Practices (see below) |
| `feedback` | array | No | Array of 360 feedback objects (see below) |
| `last_assessed` | date | Yes | Date of most recent assessment |

### Status Values

| Value | Meaning |
|-------|---------|
| `active` | Assessment is current and being acted on |
| `reviewed` | Recently reviewed, development plan updated |
| `stale` | Has not been assessed in 120+ days |

### Leadership Practices Object

| Field | Practice | Description |
|-------|----------|-------------|
| `clear_direction` | Giving clear direction | 1-5 or null |
| `necessary_tools` | Providing the necessary tools | 1-5 or null |
| `letting_go` | Letting go of the vine | 1-5 or null |
| `greater_good` | Acting with the greater good in mind | 1-5 or null |
| `clarity_breaks` | Taking Clarity Breaks | 1-5 or null |

### Management Practices Object

| Field | Practice | Description |
|-------|----------|-------------|
| `clear_expectations` | Keeping expectations clear | 1-5 or null |
| `communicating_well` | Communicating well | 1-5 or null |
| `meeting_pulse` | Maintaining the right meeting pulse | 1-5 or null |
| `quarterly_conversations` | Having quarterly conversations | 1-5 or null |
| `rewarding_recognizing` | Rewarding and recognizing | 1-5 or null |

### Feedback Object (360 Mode)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Respondent's name |
| `relationship` | string | Relationship to manager (e.g., "direct report") |
| `ratings` | array | Array of 10 integers (1-5): Leadership 1-5 then Management 1-5 |
| `date` | date | Date feedback was collected |

### Body Structure

```markdown
# [Person] — LMA Assessment

**Seat:** [Seat]
**Last Assessed:** [Date]
**Status:** [Status]

## Leadership Practices

| # | Practice | Rating | Notes |
|---|----------|--------|-------|
| 1 | Giving clear direction | [1-5] | |
| 2 | Providing the necessary tools | [1-5] | |
| 3 | Letting go of the vine | [1-5] | |
| 4 | Acting with the greater good in mind | [1-5] | |
| 5 | Taking Clarity Breaks | [1-5] | |

**Leadership Score:** [X.X]

## Management Practices

| # | Practice | Rating | Notes |
|---|----------|--------|-------|
| 1 | Keeping expectations clear | [1-5] | |
| 2 | Communicating well | [1-5] | |
| 3 | Maintaining the right meeting pulse | [1-5] | |
| 4 | Having quarterly conversations | [1-5] | |
| 5 | Rewarding and recognizing | [1-5] | |

**Management Score:** [X.X]

## LMA Score

| Component | Score |
|-----------|-------|
| Leadership | [X.X] |
| Management | [X.X] |
| **Overall LMA** | **[X.X]** |

## Flagged Practices
[Practices scoring below 3]

## 360 Feedback
[Comparison table if 360 data exists]

## Development Plan
- [ ] [Action items]

## Assessment History
- YYYY-MM-DD: [Assessment event]
```

### Example

```markdown
---
person: "Brad"
seat: "Visionary"
date: "2026-02-15"
status: active
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
  meeting_pulse: 4
  quarterly_conversations: 4
  rewarding_recognizing: 3
feedback:
  - name: "Daniel"
    relationship: "direct report"
    ratings: [4, 4, 5, 4, 3, 4, 4, 3, 4, 3]
    date: "2026-02-15"
last_assessed: "2026-02-15"
---

# Brad — LMA Assessment

**Seat:** Visionary
**Last Assessed:** 2026-02-15
**Status:** Active

---

## Leadership Practices

| # | Practice | Rating | Notes |
|---|----------|--------|-------|
| 1 | Giving clear direction | 5 | Strong vision communication to the team |
| 2 | Providing the necessary tools | 4 | Good on tooling, could improve training |
| 3 | Letting go of the vine | 4 | Improved since last quarter |
| 4 | Acting with the greater good in mind | 5 | Consistently organization-first |
| 5 | Taking Clarity Breaks | 3 | 3 breaks in 90 days — room to improve |

**Leadership Score:** 4.2

---

## Management Practices

| # | Practice | Rating | Notes |
|---|----------|--------|-------|
| 1 | Keeping expectations clear | 4 | Roles well-defined via AC |
| 2 | Communicating well | 4 | Open and transparent |
| 3 | Maintaining the right meeting pulse | 4 | 7/8 L10s in last 8 weeks |
| 4 | Having quarterly conversations | 4 | 2 conversations this quarter |
| 5 | Rewarding and recognizing | 3 | Need to improve recognition cadence |

**Management Score:** 3.8

---

## LMA Score

| Component | Score |
|-----------|-------|
| Leadership | 4.2 |
| Management | 3.8 |
| **Overall LMA** | **4.0** |

---

## Flagged Practices

*No practices below 3 — all at acceptable level.*

## Assessment History

- 2026-02-15: Initial LMA assessment conducted
```

---

## Clarity Break Format

**Location:** `data/clarity/YYYY-MM-DD.md`

Multiple clarity breaks on the same day use a suffix: `YYYY-MM-DD.md`, `YYYY-MM-DD-2.md`, `YYYY-MM-DD-3.md`.

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | date | Yes | Date of the clarity break |
| `person` | string | Yes | Who took the clarity break |
| `duration` | string or null | No | How long the break lasted (e.g., `"45 min"`, `"2 hours"`) |
| `themes` | list | No | High-level themes that emerged |
| `issues_identified` | list | No | Specific issues to bring to the next L10 meeting |

### Body Structure

The Clarity Break is intentionally the least structured data type — it's designed for strategic thinking without rigid constraints.

```markdown
# Clarity Break — YYYY-MM-DD

## State of the Business

[Optional context gathered at the start. Can be skipped for free-form reflection.]

## Reflection

### What's working well?

[Open-ended]

### What's not working?

[Open-ended]

### What's missing?

[Open-ended]

### What needs to change?

[Open-ended]

## Issues Identified

[Issues to bring to the next L10 meeting]

## Notes

[Free-form thoughts, observations, and insights]
```

### Example

```markdown
---
date: "2026-02-15"
person: "Brad"
duration: "1 hour"
themes:
  - product-market fit
  - team capacity
issues_identified:
  - "Need to revisit pricing model before beta expansion"
  - "Engineering bandwidth stretched thin across too many apps"
---

# Clarity Break — 2026-02-15

## State of the Business

Alpha program running with 30 users. Positive feedback but slow feature iteration.

## Reflection

### What's working well?

User feedback loop is tight. Alpha users are engaged and providing actionable insights.

### What's not working?

Spreading engineering effort across 6 apps simultaneously. Each app gets incremental progress but none gets the deep investment needed to break through.

### What's missing?

A clear prioritization framework for which app gets focus each quarter.

### What needs to change?

Consider focusing 80% of engineering effort on AuthorMagic for the next two quarters. Other apps go to maintenance mode.

## Issues Identified

- Need to revisit pricing model before beta expansion
- Engineering bandwidth stretched thin across too many apps

## Notes

The "focus" insight keeps coming up. Read "Traction" chapter on Rocks again — the principle of "less is more" applies at the product level too.
```

---

## Kickoff Session Format

**Location:** `data/meetings/kickoff/` with three file patterns:
- `focus-day-YYYY-MM-DD.md` — Focus Day (EOS introduction)
- `vb-day-1-YYYY-MM-DD.md` — Vision Building Day 1
- `vb-day-2-YYYY-MM-DD.md` — Vision Building Day 2

These are **one-time implementation sessions** that establish EOS in an organization. The typical sequence is: Focus Day first, then VB Day 1 (~30 days later), then VB Day 2 (~30 days after that).

### Frontmatter Fields (Shared)

All three session types share the same frontmatter:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | date | Yes | Date of the session |
| `attendees` | string | Yes | Comma-separated list of attendees |
| `location` | string | No | Where the session was held |

### Focus Day Body Structure

7 sections covering EOS introduction and initial setup:

```markdown
# Focus Day — YYYY-MM-DD

## 1. Welcome & EOS Overview
[Introduce EOS, the Six Key Components]

## 2. V/TO Introduction
[Walk through the Vision/Traction Organizer — first pass at Core Values, Core Focus, 10-Year Target]

## 3. Accountability Chart Draft
[Define major functions/seats and who fills them]

## 4. Initial Rocks Brainstorm
[Brainstorm most important priorities for next 90 days]

## 5. Scorecard Discussion
[Introduce weekly Scorecard concept, propose 5-15 metrics]

## 6. L10 Preview
[Introduce the Level 10 Meeting format, schedule first L10]

## 7. Conclude
[Summary, immediate next steps, schedule upcoming sessions]
```

### Vision Building Day 1 Body Structure

5 sections focused on defining the organization's identity:

```markdown
# Vision Building Day 1 — YYYY-MM-DD

## 1. Core Values Definition
[Finalize 3-7 Core Values — discovered, not invented]

## 2. Core Focus Clarification
[Define Purpose/Cause/Passion and Niche]

## 3. 10-Year Target Setting
[Set one big, audacious, measurable target]

## 4. Marketing Strategy
[Target Market, Three Uniques, Proven Process, Guarantee]

## 5. Conclude
[Summary, action items, preparation for VB Day 2]
```

### Vision Building Day 2 Body Structure

5 sections focused on building the execution plan:

```markdown
# Vision Building Day 2 — YYYY-MM-DD

## 1. 3-Year Picture
[Vivid picture of the organization in 3 years — revenue, profit, headcount]

## 2. 1-Year Plan
[Specific goals for this year, 3-7 measurable targets]

## 3. Quarterly Rocks Setting
[3-7 most important priorities for the next 90 days]

## 4. Issues List Brainstorm
[Surface ALL issues — brain dump, not a solving session]

## 5. Conclude
[Summary, V/TO completion status, action items to formalize everything]
```

### Example Frontmatter (Focus Day)

```yaml
---
date: "2026-01-15"
attendees: "brad, daniel"
location: "Offsite — Boulder"
---
```

---

## Stack Item Format (Assistance Track)

**Location:** `data/assistance/stack/stack-NNN-slug.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `stack-001`) |
| `title` | string | Yes | Short description of the delegation item |
| `from` | string | Yes | Leader adding the item to the stack |
| `to` | string | Yes | Assistant who will handle the item |
| `urgency` | enum | Yes | `today`, `this_week`, or `whenever` |
| `status` | enum | Yes | Current lifecycle status (see below) |
| `created` | date | Yes | Date the item was added to the stack |
| `handed_off` | date | No | Date when discussed in daily meeting and handed to assistant |
| `completed` | date | No | Date when marked done |

### Status Values

| Value | Meaning | Set When |
|-------|---------|----------|
| `pending` | On the stack, not yet handed off | Item creation |
| `handed_off` | Discussed in daily meeting, assistant is working on it | During Daily mode |
| `done` | Completed | During Daily or Stack mode |

### Urgency Values

| Value | Expected Turnaround |
|-------|-------------------|
| `today` | Same day |
| `this_week` | Within the week |
| `whenever` | No time pressure, do when convenient |

### Body Structure

```markdown
# [Item Title]

**From:** [Leader name]
**To:** [Assistant name]
**Urgency:** [today/this_week/whenever]
**Created:** [Date]

## Details

[Description of the task or item being delegated]

## Notes

[Any context, background, or special instructions]

## Outcome

[Filled in when status changes to done — what happened, any follow-up needed]
```

### Example Frontmatter

```yaml
---
id: "stack-003"
title: "Schedule board meeting"
from: "Brad Feld"
to: "Sarah Chen"
urgency: this_week
status: pending
created: "2026-02-16"
handed_off: null
completed: null
---
```

---

## Daily Meeting Log Format (Assistance Track)

**Location:** `data/assistance/daily/YYYY-MM-DD.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | date | Yes | Meeting date |
| `leader` | string | Yes | Leader in the meeting |
| `assistant` | string | Yes | Assistant in the meeting |
| `items_reviewed` | integer | Yes | Number of stack items discussed |
| `items_handed_off` | integer | Yes | Number of items handed off in this meeting |
| `items_completed` | integer | Yes | Number of items marked done |
| `duration_minutes` | integer | No | Approximate meeting duration |

### Body Structure

```markdown
# Daily Standup — [Date]

**Leader:** [Name]
**Assistant:** [Name]

---

## Stack Review

| # | Item | Urgency | Decision | Notes |
|---|------|---------|----------|-------|
| 1 | [Stack item title] | [urgency] | [hand_off/defer/done] | [Context] |

---

## New Items Added

| # | Item | Urgency | Assigned To | Notes |
|---|------|---------|-------------|-------|
| 1 | [New item] | [urgency] | [Person] | [Context] |

---

## Action Items

- [ ] [Action item with owner]

---

## Meeting Notes

[Additional discussion, observations, or follow-up]
```

### Example Frontmatter

```yaml
---
date: "2026-02-16"
leader: "Brad Feld"
assistant: "Sarah Chen"
items_reviewed: 5
items_handed_off: 3
items_completed: 1
duration_minutes: 12
---
```

---

## Cash Flow Assessment Format

**Location:** `data/cashflow/YYYY-MM-DD-assessment.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | date | Yes | Date of the assessment |
| `participants` | list | Yes | Array of participant names |
| `status` | enum | Yes | Current status (see below) |
| `overall_summary` | string | No | Brief summary of cash flow health |
| `drivers` | object | Yes | Object containing 8 driver sub-objects (see Driver Object below) |

### Driver Object

Each of the 8 drivers (`price`, `volume`, `cogs_margin`, `ar_days`, `ap_days`, `inventory_wip`, `opex`, `debt_structure`) contains:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `current_state` | string | Yes | Description of current state for this driver |
| `potential` | enum | Yes | Improvement potential (see below) |
| `owner` | string | Yes | Person responsible for this driver |
| `baseline_metric` | string | Yes | Current measurement (stored as string, not number) |
| `target_metric` | string | Yes | Target measurement to achieve |
| `priority_rank` | integer or null | No | Priority ranking (1 = highest priority), null if not prioritized |
| `notes` | string | No | Additional context or observations |

### Potential Values

| Value | Meaning |
|-------|---------|
| `high` | Significant improvement opportunity |
| `medium` | Moderate improvement opportunity |
| `low` | Minor improvement opportunity |
| `none` | No meaningful improvement available |

### Status Values

| Value | Meaning |
|-------|---------|
| `in_progress` | Assessment started but not yet complete |
| `complete` | All 8 drivers assessed and prioritized |

### Body Structure

```markdown
# Cash Flow Assessment — YYYY-MM-DD

## Driver Summary

| # | Driver | Potential | Owner | Baseline | Target | Priority |
|---|--------|-----------|-------|----------|--------|----------|
| 1 | Price | [potential] | [owner] | [baseline] | [target] | [rank or —] |
| ... | ... | ... | ... | ... | ... | ... |

## 1. Price
**Current State:** [Description]
**Improvement Potential:** [high/medium/low/none]
**Baseline:** [Current metric]
**Target:** [Target metric]
**Owner:** [Name]

[Repeat for all 8 drivers]

## Action Plan

| Action | Driver | Owner | Timeline | Status |
|--------|--------|-------|----------|--------|
```

### Example

```markdown
---
date: "2026-02-16"
participants:
  - "Brad"
  - "Daniel"
status: complete
overall_summary: "Strong pricing power and margin opportunity. AR days are the biggest quick win."
drivers:
  price:
    current_state: "Haven't raised prices in 12 months"
    potential: high
    owner: "Daniel"
    baseline_metric: "$29/mo average"
    target_metric: "$39/mo average"
    priority_rank: 2
    notes: "Competitor pricing supports a higher tier"
  volume:
    current_state: "30 alpha users, growing steadily"
    potential: medium
    owner: "Daniel"
    baseline_metric: "30 users"
    target_metric: "100 users by Q2"
    priority_rank: 3
    notes: ""
  cogs_margin:
    current_state: "AI API costs are primary COGS"
    potential: medium
    owner: "Brad"
    baseline_metric: "62% gross margin"
    target_metric: "75% gross margin"
    priority_rank: null
    notes: "Haiku migration will reduce costs significantly"
  ar_days:
    current_state: "All prepaid subscriptions, no AR issues"
    potential: none
    owner: "Brad"
    baseline_metric: "0 days"
    target_metric: "0 days"
    priority_rank: null
    notes: "SaaS model eliminates AR risk"
  ap_days:
    current_state: "Monthly billing on most vendors"
    potential: low
    owner: "Brad"
    baseline_metric: "Net 30"
    target_metric: "Net 30"
    priority_rank: null
    notes: ""
  inventory_wip:
    current_state: "No physical inventory"
    potential: none
    owner: "Brad"
    baseline_metric: "N/A"
    target_metric: "N/A"
    priority_rank: null
    notes: "SaaS — not applicable"
  opex:
    current_state: "Lean two-person team, infrastructure costs growing"
    potential: low
    owner: "Brad"
    baseline_metric: "$8K/mo"
    target_metric: "$7K/mo"
    priority_rank: null
    notes: "Optimize Vercel and Supabase tiers"
  debt_structure:
    current_state: "No debt, self-funded"
    potential: none
    owner: "Brad"
    baseline_metric: "0 debt"
    target_metric: "0 debt"
    priority_rank: null
    notes: ""
---

# Cash Flow Assessment — 2026-02-16

## Driver Summary

| # | Driver | Potential | Owner | Baseline | Target | Priority |
|---|--------|-----------|-------|----------|--------|----------|
| 1 | Price | high | Daniel | $29/mo avg | $39/mo avg | 2 |
| 2 | Volume | medium | Daniel | 30 users | 100 users | 3 |
| 3 | COGS/Margin | medium | Brad | 62% margin | 75% margin | — |
| 4 | AR Days | none | Brad | 0 days | 0 days | — |
| 5 | AP Days | low | Brad | Net 30 | Net 30 | — |
| 6 | Inventory/WIP | none | Brad | N/A | N/A | — |
| 7 | OpEx | low | Brad | $8K/mo | $7K/mo | — |
| 8 | Debt Structure | none | Brad | 0 debt | 0 debt | — |

## 1. Price
**Current State:** Haven't raised prices in 12 months
**Improvement Potential:** high
**Baseline:** $29/mo average
**Target:** $39/mo average
**Owner:** Daniel

## Action Plan

| Action | Driver | Owner | Timeline | Status |
|--------|--------|-------|----------|--------|
| Research competitor pricing tiers | Price | Daniel | 2026-02-28 | [ ] |
| Plan Haiku migration for AI calls | COGS/Margin | Brad | 2026-03-15 | [ ] |
```

---

## Trust Exercise Format

**Location:** `data/trust/YYYY-MM-DD-exercise-slug.md`

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | date | Yes | Date the exercise was conducted |
| `exercise_number` | integer | Yes | Exercise number in the 10-exercise progression (1-10) |
| `exercise_name` | string | Yes | Name of the exercise (e.g., `"Personal Histories"`) |
| `participants` | list | Yes | Array of participant names |
| `facilitator` | string | Yes | Person who led the exercise |
| `duration_minutes` | integer | No | Actual duration of the exercise |
| `vulnerability_level` | enum | Yes | Exercise vulnerability level (see below) |
| `status` | enum | Yes | Current status (see below) |

### Vulnerability Level Values

| Value | Meaning | Exercises |
|-------|---------|-----------|
| `low` | Minimal personal exposure | 1 (Personal Histories), 2 (DISC/Kolbe) |
| `medium` | Moderate personal sharing | 3 (Lifeline), 4 (One Thing), 5 (Feedback Round), 6 (Strengths Spotlight), 7 (Conflict Norms) |
| `high` | Deep personal vulnerability | 8 (Accountability Partners), 9 (Team Effectiveness), 10 (Vulnerability Circle) |

### Status Values

| Value | Meaning |
|-------|---------|
| `completed` | Exercise has been fully conducted |
| `scheduled` | Exercise is planned but not yet conducted |

### Body Structure

```markdown
# [Exercise Name] — Trust Exercise #[N]

**Date:** YYYY-MM-DD
**Facilitator:** [Name]
**Participants:** [Name 1], [Name 2], ...

---

## Exercise Summary

[Description of what happened during the exercise]

## Key Takeaways

- [Insight or observation from the exercise]
- [Team dynamic that emerged]

## Action Items

- [ ] [Follow-up action if applicable]

## Notes

- YYYY-MM-DD: Exercise conducted
```

### Example

```markdown
---
date: "2026-02-16"
exercise_number: 1
exercise_name: "Personal Histories"
participants:
  - "Brad"
  - "Daniel"
facilitator: "Brad"
duration_minutes: 30
vulnerability_level: low
status: completed
---

# Personal Histories — Trust Exercise #1

**Date:** 2026-02-16
**Facilitator:** Brad
**Participants:** Brad, Daniel

---

## Exercise Summary

Each team member shared answers to 5 personal history questions: hometown, number of siblings, childhood hobbies, biggest challenge growing up, and first job. Both participants engaged openly and discovered common ground in early career experiences.

## Key Takeaways

- Shared experience of growing up in small towns built immediate connection
- First jobs in service industry gave both a customer-first perspective
- Exercise felt natural and comfortable — good foundation for deeper exercises

## Action Items

- [ ] Schedule Exercise 2 (DISC/Kolbe Sharing) for ~30 days from now

## Notes

- 2026-02-16: Exercise conducted as first trust-building activity
```

---

## Directory Structure

```
data/
├── vision.md                          # V/TO document
├── accountability.md                  # Accountability chart
├── rocks/
│   ├── 2026-Q1/
│   │   ├── rock-001-launch-beta.md
│   │   ├── rock-002-hire-vp-sales.md
│   │   └── rock-003-implement-crm.md
│   └── 2026-Q2/
│       └── ...
├── scorecard/
│   ├── metrics.md                     # Metric definitions
│   └── weeks/
│       ├── 2026-W05.md
│       ├── 2026-W06.md
│       └── 2026-W07.md
├── todos/
│   ├── todo-001-update-onboarding-doc.md
│   ├── todo-002-send-partnership-agreement.md
│   └── todo-003-send-revised-proposal.md
├── issues/
│   ├── open/
│   │   ├── issue-005-misaligned-marketing.md
│   │   └── issue-007-key-account-churning.md
│   └── solved/
│       ├── issue-001-reporting-gaps.md
│       ├── issue-002-office-wifi.md
│       └── issue-003-slow-onboarding.md
├── people/
│   ├── sarah-chen.md
│   ├── brad.md
│   └── alumni/
│       └── former-employee.md
├── conversations/
│   ├── 2026-Q1/
│   │   ├── sarah-chen.md
│   │   └── brad.md
│   └── 2026-Q2/
│       └── ...
├── annual/
│   ├── 2025-planning.md
│   └── 2026-planning.md
├── assistance/
│   ├── stack/
│   │   ├── stack-001-schedule-board-meeting.md
│   │   ├── stack-002-order-office-supplies.md
│   │   └── stack-003-book-travel.md
│   └── daily/
│       ├── 2026-02-14.md
│       ├── 2026-02-15.md
│       └── 2026-02-16.md
├── quarterly/
│   ├── 2026-Q1-planning.md
│   └── 2026-Q2-planning.md
├── checkups/
│   ├── 2026-01-15.md
│   └── 2026-04-15.md
├── delegate/
│   ├── brad.md
│   └── sarah-chen.md
├── cashflow/
│   ├── 2026-02-16-assessment.md
│   └── 2026-04-01-assessment.md
├── trust/
│   ├── 2026-02-16-personal-histories.md
│   └── 2026-03-15-disc-kolbe-sharing.md
├── clarity/
│   ├── 2026-02-10.md
│   └── 2026-02-15.md
├── processes/
│   └── core-process-name.md
└── meetings/
    ├── l10/
    │   ├── 2026-02-06.md
    │   └── 2026-02-13.md
    └── kickoff/
        ├── focus-day-2026-01-15.md
        ├── vb-day-1-2026-02-15.md
        └── vb-day-2-2026-03-15.md
```

### Key Conventions

- **Rocks** are organized by quarter: `data/rocks/YYYY-QN/`
- **To-Dos** are flat in `data/todos/` (completed To-Dos stay in place with `status: complete`)
- **Issues** are organized by state: `data/issues/open/` and `data/issues/solved/`
- **Scorecard weeks** use ISO week numbering: `data/scorecard/weeks/YYYY-WNN.md`
- **L10 meetings** use date: `data/meetings/l10/YYYY-MM-DD.md`
- **Vision and Accountability** are single files at the `data/` root
- **People** are one file per person: `data/people/firstname-lastname.md` (departed people in `alumni/`)
- **Conversations** are organized by quarter and person: `data/conversations/YYYY-QN/firstname-lastname.md`
- **Annual planning** uses year: `data/annual/YYYY-planning.md`
- **Quarterly planning** uses quarter: `data/quarterly/YYYY-QN-planning.md`
- **Checkups** use date: `data/checkups/YYYY-MM-DD.md`
- **Delegate and Elevate** are one file per person: `data/delegate/firstname-lastname.md`
- **Assistance Stack** items are one file per item: `data/assistance/stack/stack-NNN-slug.md` (completed items stay in place with `status: done`)
- **Assistance Daily** meetings use date: `data/assistance/daily/YYYY-MM-DD.md`
- **Cash flow assessments** use date: `data/cashflow/YYYY-MM-DD-assessment.md`
- **Trust exercises** use date-slug: `data/trust/YYYY-MM-DD-exercise-slug.md`
- **Clarity breaks** use date: `data/clarity/YYYY-MM-DD.md` (suffix `-2`, `-3` for multiples per day)
- **Kickoff sessions** use type-date: `data/meetings/kickoff/focus-day-YYYY-MM-DD.md`
- **Processes** are per-process files: `data/processes/core-process-name.md`

## Parsing

To parse a CEOS data file in any language:

1. Read the file as text
2. Split on the first two `---` lines to extract YAML frontmatter
3. Parse the YAML block into a key-value structure
4. The remaining text is markdown — parse as needed

Most languages have YAML and markdown parsers available. The format is intentionally simple enough that a regex-based parser works for basic use cases.

## Versioning

The data format follows [Semantic Versioning](https://semver.org/) as part of the CEOS project:

- **Breaking changes** (renaming fields, changing status values, removing fields) require a major version bump and an RFC-style discussion
- **Non-breaking additions** (new optional fields) are minor version changes
- **Documentation and clarifications** are patch version changes

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the process around data format changes.
