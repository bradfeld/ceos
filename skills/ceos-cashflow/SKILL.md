---
name: ceos-cashflow
description: Use when assessing and optimizing the 8 financial levers that drive cash flow and profitability
file-access: [data/cashflow/, templates/cashflow-assessment.md, data/accountability.md, data/scorecard/]
tools-used: [Read, Write, Glob]
---

# ceos-cashflow

The 8 Cash Flow Drivers (EOS Toolbox tool #10). A facilitated workshop for leadership teams to identify and optimize the eight key financial levers that impact cash flow and profitability: Price, Volume, COGS/Margin, A/R Days, A/P Days, Inventory/WIP, Operating Expenses, and Debt Structure.

**Not for:** Weekly scorecard tracking (use `ceos-scorecard`), general issue resolution (use `ceos-ids`), or Rock setting (use `ceos-rocks`). This skill is for the structured cash flow driver assessment — a strategic conversation about financial levers.

## When to Use

- "Assess our cash flow" or "8 cash flow drivers"
- "Cash flow drivers" or "financial optimization"
- "Review our financial levers" or "profitability drivers"
- "Where can we improve margins?"
- "Cash flow driver review" or "quarterly cash flow check-in"
- "Show cash flow history" or "how have our drivers changed?"

## Context

### Finding the CEOS Repository

Before doing anything:

1. Search upward from the current directory for a `.ceos` marker file
2. If not found, tell the user: "I can't find a CEOS repository. Clone it with `git clone https://github.com/bradfeld/ceos.git` and run `./setup.sh init`."
3. If found, set `CEOS_ROOT` to that directory
4. Run `git -C "$CEOS_ROOT" pull --ff-only` to sync latest data (skip if offline or if pull fails — work with local data)

### Key Files

| File | Purpose |
|------|---------|
| `data/cashflow/` | Cash flow driver assessments (one per session) |
| `data/accountability.md` | Team members for suggesting driver owners |
| `data/scorecard/metrics.md` | Existing metrics that may overlap with cash flow drivers |
| `templates/cashflow-assessment.md` | Template for new assessment files |

### The 8 Cash Flow Drivers

| # | Driver | Key Question | Typical Metric |
|---|--------|-------------|----------------|
| 1 | **Price** | Can you increase prices? | Average selling price, price per unit |
| 2 | **Volume** | Can you sell more? | Units sold, transactions, customers |
| 3 | **COGS / Margin** | Can you reduce cost of goods? | Gross margin %, COGS as % of revenue |
| 4 | **A/R Days** | Can you collect faster? | Days sales outstanding (DSO) |
| 5 | **A/P Days** | Can you negotiate better terms? | Days payable outstanding (DPO) |
| 6 | **Inventory / WIP** | Can you reduce inventory? | Inventory turnover, WIP backlog |
| 7 | **Operating Expenses** | Where can you cut overhead? | OpEx as % of revenue, specific line items |
| 8 | **Debt Structure** | Is debt optimized? | Debt-to-equity, interest rate, term mix |

**Note:** Not all 8 drivers apply equally to every business. A software company may have minimal inventory. A services firm may have no COGS. The skill handles this — drivers can be marked as "none" potential when they don't apply.

### Driver Improvement Potential

| Value | Meaning |
|-------|---------|
| `high` | Significant upside — this driver should be a top priority |
| `medium` | Moderate improvement possible with focused effort |
| `low` | Minor gains available — not a priority this quarter |
| `none` | Already optimized or not applicable to this business |

### Assessment Status

| Value | Meaning |
|-------|---------|
| `in_progress` | Assessment started but not all drivers evaluated |
| `complete` | All drivers assessed and priorities set |

## Process

### Mode: Assess

**Trigger:** User wants to evaluate all 8 cash flow drivers from scratch.

**Step 1: Gather context**

Read `data/accountability.md` to identify potential driver owners. If the file doesn't exist, skip owner suggestions — ask the user for each driver's owner directly.

Read `data/scorecard/metrics.md` (if it exists) to identify metrics already being tracked that relate to cash flow drivers. Note any overlaps — don't duplicate existing scorecard measurables.

**Step 2: Walk through the 8 drivers**

For each driver (1 through 8):

1. Display the driver name, key question, and typical metric from the reference table
2. If a related scorecard metric exists, note it: "Your Scorecard already tracks [metric] — you may want to reference that as your baseline."
3. Ask the user:
   - **Current state:** What's the current situation for this driver?
   - **Improvement potential:** High, medium, low, or none?
   - **Baseline metric:** What's the current value? (Store as a string — can be "\$52K/month", "Net 30", "45 days", etc.)
   - **Target metric:** Where do you want this to be?
   - **Owner:** Who is accountable for this driver? (Suggest from accountability chart if available)
   - **Notes:** Any additional context?

If the user wants to skip a driver (e.g., "Inventory doesn't apply to us"), set potential to `none` and note "Not applicable" in current_state. Move to the next driver.

**Step 3: Prioritize**

After all 8 drivers are assessed, display a summary table:

| # | Driver | Potential | Owner | Baseline | Target |
|---|--------|-----------|-------|----------|--------|
| ... | ... | ... | ... | ... | ... |

Ask the user to rank their top 3-5 focus drivers. Assign `priority_rank` values (1 = highest priority). Drivers not in the top 3-5 get `null` for priority_rank.

**Step 4: Create assessment file**

Generate the complete file from `templates/cashflow-assessment.md`. Populate all frontmatter fields and body sections.

**Show the complete file** to the user before writing. Ask: "Save this assessment?"

Write to `data/cashflow/YYYY-MM-DD.md` (using today's date). If a file already exists for today, use suffix: `YYYY-MM-DD-2.md`.

Set frontmatter `status: complete`.

**Step 5: Next steps**

After saving, mention (but don't auto-invoke):
- "Driver improvements with high potential could become Rocks for next quarter (use `ceos-rocks`)"
- "Driver problems that need investigation could become Issues (use `ceos-ids`)"
- "Consider adding key driver metrics to your Scorecard (use `ceos-scorecard`)"

### Mode: Review

**Trigger:** User wants a quarterly check-in on their prioritized cash flow drivers.

**Step 1: Load assessments**

Read all files from `data/cashflow/` via Glob. Parse YAML frontmatter. Sort by date (newest first).

If no assessments exist: "No cash flow assessments found. Run an assessment first to establish your baseline."

**Step 2: Find the latest assessment**

Display the most recent completed assessment's prioritized drivers (those with `priority_rank` set):

| Priority | Driver | Baseline | Target | Owner |
|----------|--------|----------|--------|-------|
| 1 | [driver] | [baseline] | [target] | [owner] |
| 2 | [driver] | [baseline] | [target] | [owner] |
| ... | ... | ... | ... | ... |

**Step 3: Collect current values**

For each prioritized driver, ask: "What's the current value for [Driver]? (Baseline was [baseline], target is [target])"

**Step 4: Display progress**

| Priority | Driver | Baseline | Current | Target | Direction |
|----------|--------|----------|---------|--------|-----------|
| 1 | Price | \$45/unit | \$48/unit | \$55/unit | Improving |
| 2 | A/R Days | 45 days | 42 days | 30 days | Improving |
| 3 | OpEx | 35% of rev | 36% of rev | 30% of rev | Stalling |

**Direction** values:
- **Improving** — Moving toward target
- **Stalling** — No change or very minor movement
- **Regressing** — Moving away from target
- **Target hit** — Current meets or exceeds target

**Step 5: Flag and suggest**

For stalling or regressing drivers, suggest:
- "Consider creating an Issue to investigate why [Driver] is stalling (use `ceos-ids`)"
- "A focused Rock on [Driver] improvement could help (use `ceos-rocks`)"

**Step 6: Save review (optional)**

Ask if the user wants to save this review as a new assessment. If yes, create a new file capturing the current state as the new baseline. This becomes the comparison point for the next review.

### Mode: History

**Trigger:** User wants to see cash flow driver trends over time.

**Step 1: Load all assessments**

Read all files from `data/cashflow/` via Glob. Parse YAML frontmatter. Sort by date (oldest first).

If no assessments exist: "No cash flow assessments found yet."

If only one assessment: Display it, noting "Only one assessment on record. Run another assessment later to see trends."

**Step 2: Assessment timeline**

| Date | Drivers Assessed | High | Medium | Low | None | Top Priorities |
|------|-----------------|------|--------|-----|------|---------------|
| 2026-02-15 | 8 | 3 | 2 | 2 | 1 | Price, A/R Days, OpEx |
| 2026-05-10 | 8 | 2 | 3 | 2 | 1 | A/R Days, Volume, OpEx |

**Step 3: Per-driver trends**

For each driver that has been prioritized in at least one assessment:

```
Price:  high → medium → low  (improving — was a top priority, now optimized)
A/R Days:  high → high → medium  (improving slowly — still needs attention)
OpEx:  medium → high → high  (worsening — consider escalating to an Issue)
```

**Step 4: Insights**

- Which drivers have been consistently prioritized (may need a Rock)
- Which drivers improved and were deprioritized (success stories)
- Which drivers have worsened (may need an IDS investigation)

**Step 5: Drill-down**

Offer: "Would you like to see the full details of any specific assessment?"

If yes, display the complete assessment file.

## Output Format

### Assess Mode Summary

After completing the assessment, display:

```
Cash Flow Assessment — YYYY-MM-DD

8 Drivers Assessed:
  High potential:   [N] drivers
  Medium potential:  [N] drivers
  Low potential:     [N] drivers
  Not applicable:    [N] drivers

Top Priorities:
  1. [Driver] — [Baseline] → [Target] (Owner: [Name])
  2. [Driver] — [Baseline] → [Target] (Owner: [Name])
  3. [Driver] — [Baseline] → [Target] (Owner: [Name])

Saved to: data/cashflow/YYYY-MM-DD.md
```

### Review Mode Summary

```
Cash Flow Review — YYYY-MM-DD

Comparing to assessment from [prior date]:

  Improving:  [N] drivers
  Stalling:   [N] drivers
  Regressing: [N] drivers
  Target hit: [N] drivers

[Table of prioritized drivers with progress]
```

### History Mode Summary

```
Cash Flow History — [N] assessments

First assessment: YYYY-MM-DD
Latest assessment: YYYY-MM-DD

[Assessment timeline table]
[Per-driver trend arrows]
```

## Guardrails

- **Always show the complete file before writing.** Never save an assessment without the user seeing and approving the full content.
- **Don't auto-invoke skills.** When assessment results suggest creating Rocks, Issues, or Scorecard metrics, mention the option but let the user decide. Say "Would you like to create a Rock for this?" rather than doing it automatically.
- **Sensitive data warning.** On first use in a session, remind the user: "Cash flow assessments contain sensitive financial information (revenue targets, cost structures, debt details). Ensure this repository is private."
- **Don't prescribe financial strategies.** This is a facilitation guide, not financial advice. Present the framework and record the team's decisions. Don't suggest specific pricing strategies, cost-cutting measures, or debt restructuring approaches.
- **One full assessment per session.** Walking through all 8 drivers is a substantial conversation. Don't rush — each driver deserves focused discussion.
- **Metrics are strings, not numbers.** Financial values come in many formats (\$52K, 45 days, Net 30, 35% of revenue). Store them as human-readable strings. The skill facilitates comparison through display, not computation.

## Integration Notes

### Accountability Chart (Read)

- **Direction:** Read
- **What data:** `data/accountability.md`
- **Purpose:** Suggest driver owners from the leadership team's seat assignments. Each driver should be owned by the person whose seat most closely relates to that financial lever.

### Scorecard (Read)

- **Direction:** Read
- **What data:** `data/scorecard/metrics.md`
- **Purpose:** Cross-reference existing scorecard metrics with the 8 drivers. If a team already tracks "Weekly Revenue" on the scorecard, that overlaps with the Volume and Price drivers. Avoid duplicating metrics — reference existing ones.

### Rocks (Related)

- **Direction:** Related (suggest, don't write)
- **What data:** N/A
- **Purpose:** High-potential driver improvements can become quarterly Rocks. After assessment, suggest the user create Rocks for their top priorities via `ceos-rocks`.

### IDS (Related)

- **Direction:** Related (suggest, don't write)
- **What data:** N/A
- **Purpose:** Stalling or regressing drivers may need root-cause investigation. Suggest creating Issues via `ceos-ids` for drivers that aren't improving despite being prioritized.

**Write Principle:** Only `ceos-cashflow` writes to `data/cashflow/`. Other skills may reference cash flow assessments for financial context.
