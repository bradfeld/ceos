---
name: ceos-scorecard
description: Use when defining metrics, logging weekly scorecard numbers, or analyzing trends
file-access: [data/scorecard/, templates/scorecard-metrics.md, templates/scorecard-week.md, data/accountability.md]
tools-used: [Read, Write, Glob]
---

# ceos-scorecard

Manage the weekly Scorecard — the 5-15 numbers that tell you the health of your business at a glance. Define metrics, log weekly values, and spot trends before they become problems.

## When to Use

- "Log scorecard" or "enter this week's numbers"
- "Define a new metric" or "add a metric to the scorecard"
- "How are our metrics?" or "scorecard trend"
- "Show the scorecard" or "weekly numbers"
- "Which metrics are off track?"
- Any weekly Scorecard review (typically during L10 meetings)

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/scorecard/metrics.md` | Metric definitions (names, owners, goals, thresholds) |
| `data/scorecard/weeks/YYYY-WNN.md` | Weekly scorecard entries |
| `templates/scorecard-metrics.md` | Template for metrics definition file |
| `templates/scorecard-week.md` | Template for weekly entries |
| `data/accountability.md` | Accountability Chart (seat owners for metric ownership validation) |

### Week Format

Weeks follow ISO 8601: `YYYY-WNN` (e.g., `2026-W07`). Week 1 is the week containing the first Thursday of the year.

### Metric Status

Each metric value is compared against its goal:
- **on_track** (green) — meets or exceeds the goal threshold
- **off_track** (red) — below the goal threshold

The thresholds are defined in `data/scorecard/metrics.md`.

## Process

### Mode: Define Metrics

Use when setting up the Scorecard or adding new metrics.

#### Step 1: Read Current Metrics

Read `data/scorecard/metrics.md`. If the file doesn't exist, tell the user to run `setup.sh init` first.

Display the current metrics table.

#### Step 2: Add or Edit a Metric

For each new metric, collect:

1. **Metric name** — what are we measuring? (e.g., "Weekly Revenue", "New Customers")
2. **Owner** — one person responsible for this number
3. **Goal** — the target value (e.g., "\$50,000", "10")
4. **Frequency** — Weekly (most metrics) or Monthly
5. **Green threshold** — what value means "on track" (e.g., ">= \$50,000")
6. **Red threshold** — what value means "off track" (e.g., "< \$50,000")

#### Step 3: Validate

- **5-15 metrics total.** Fewer means blind spots. More means losing focus.
- **One owner per metric.** Not shared.
- **Measurable.** Must be a specific number, not subjective.
- **Prefer leading indicators.** Activity metrics (calls made, demos scheduled) predict results better than lagging metrics (revenue).
- **Seat alignment.** Cross-reference metric owners against `data/accountability.md`. Each metric should map to a seat's responsibilities. Flag mismatches, e.g., "This metric seems to fall under [Seat] responsibilities. Should [Seat Owner] own it?". If a metric doesn't fit any seat, it may indicate a gap in the Accountability Chart.

#### Step 4: Update the File

Add the new metric row to the table in `data/scorecard/metrics.md`. Show the diff before writing.

---

### Mode: Log Weekly

Use to record this week's numbers.

#### Step 1: Determine the Week

If the user specified a week, use it. Otherwise, calculate the current ISO week.

Check if `data/scorecard/weeks/YYYY-WNN.md` already exists. If so, ask: "Week NN already has entries. Update it, or is this a different week?"

#### Step 2: Read Metric Definitions

Read `data/scorecard/metrics.md` to get the list of metrics, their goals, and thresholds.

#### Step 3: Collect Values

For each metric, ask: "What's the value for [Metric Name] this week?"

Accept the value and auto-calculate status:
- Compare against the Green/Red thresholds from the metric definition
- Set status to `on_track` or `off_track`

#### Step 4: Write the Weekly File

Use `templates/scorecard-week.md` as the template. Write to `data/scorecard/weeks/YYYY-WNN.md`.

Show the complete entry before writing:

| Metric | Owner | Goal | Actual | Status |
|--------|-------|------|--------|--------|
| Weekly Revenue | brad | \$50K | \$52K | on_track |
| New Customers | daniel | 10 | 7 | off_track |

Ask: "Save this week's scorecard?"

#### Step 5: Flag Off-Track Items

For any off_track metric, note: "Off-track items should be discussed during the L10 meeting. Consider adding to the Issues list if consistently off track."

---

### Mode: Trend Analysis

Use to review metrics over time and spot patterns.

#### Step 1: Read Weekly Files

Read all files in `data/scorecard/weeks/`, sorted by week number. Focus on the most recent 13 weeks (one quarter).

#### Step 2: Build Trend Table

For each metric, show the last 13 weeks:

```
Weekly Revenue (brad) — Goal: \$50K
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
W01: \$48K ✗  W02: \$51K ✓  W03: \$49K ✗  W04: \$55K ✓
W05: \$52K ✓  W06: \$47K ✗  W07: \$53K ✓  W08: \$50K ✓
W09: \$54K ✓  W10: \$51K ✓  W11: \$48K ✗  W12: \$52K ✓
W13: \$55K ✓

On track: 9/13 weeks (69%)
Current streak: 1 week on track
```

#### Step 3: Flag Concerning Patterns

- **3+ consecutive weeks off-track**: "⚠️ [Metric] has been off-track for [N] consecutive weeks. This may be a systemic issue worth escalating."
- **Trending down over 4+ weeks**: Even if individual weeks are on-track, flag declining trends.
- **Consistently off-track (more than 50% of weeks)**: "Consider whether the goal is realistic, or if there's a deeper issue. Suggest creating an Issue with `ceos-ids`."

#### Step 4: Escalation Suggestion

If any metric has been off-track 3+ consecutive weeks:

"Metric '[Name]' has been off-track for [N] consecutive weeks. This pattern suggests a systemic issue rather than a one-time miss. Consider:
1. Creating an Issue to investigate root cause (use `ceos-ids`)
2. Reviewing whether the goal needs adjustment
3. Discussing in the next L10 meeting"

## Output Format

**Define Metrics:** Updated metrics table with diff.
**Log Weekly:** Completed scorecard table for the week.
**Trend Analysis:** 13-week trend per metric with pattern flags.

## Guardrails

- **Always show diff before writing.** Never modify metrics.md or week files without showing the change and getting approval.
- **Don't skip metrics.** When logging weekly, prompt for every defined metric. If a value isn't available, record it as missing (don't silently skip).
- **Validate week format.** Ensure `YYYY-WNN` is valid (NN between 01-53).
- **Respect metric definitions.** When logging weekly values, use the thresholds from metrics.md for status calculation. Don't let the user override on_track/off_track manually.
- **Escalation, not alarm.** Trend flags are suggestions, not commands. Present data objectively and recommend action, but let the user decide.
- **Cross-reference during L10.** When invoked during an L10 meeting (via `ceos-l10`), focus on the latest week's status. Save trend analysis for dedicated review sessions.
- **Don't auto-invoke other skills.** Mention `ceos-l10`, `ceos-ids`, and `ceos-annual` when relevant, but let the user decide when to switch workflows.
- **Sensitive data warning.** On first use, remind the user: "Scorecard data may contain sensitive business metrics. Use a private repo."

## Integration Notes

### L10 Meetings (ceos-l10)

- **Read:** `ceos-l10` reads the latest weekly scorecard during Section 3 (Scorecard Review) of the L10 meeting. Each metric owner reports their number and the team discusses any off-track items.
- **Suggested flow:** Off-track metrics that persist for 3+ weeks should become Issues via `ceos-ids`.

### IDS (ceos-ids)

- **Related:** Metrics that are consistently off-track may surface as Issues. When escalating, suggest: "This metric has been off-track for [N] weeks. Create an Issue with `ceos-ids` to investigate the root cause."

### Annual Planning (ceos-annual)

- **Read:** `ceos-annual` reviews Scorecard metrics during the annual planning session. The team evaluates whether existing metrics are still the right numbers to track and adds or removes metrics for the new year.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-scorecard` reads `data/accountability.md` when defining metrics to validate that metric owners match seat responsibilities. Revenue metrics belong to whoever owns the Sales & Marketing seat; delivery metrics belong to the Delivery seat owner.
- **Suggested flow:** If a metric owner doesn't map to a seat, suggest: "This metric doesn't align with any seat in the Accountability Chart. Should it belong to the [Seat] owner?"

### Read-Only Principle

Other skills read `data/scorecard/` for reference. **Only `ceos-scorecard` writes to scorecard files.** This preserves a single source of truth for business metrics.
