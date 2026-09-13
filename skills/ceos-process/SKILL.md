---
name: ceos-process
description: Use when documenting core processes or reviewing process followability
file-access: [data/processes/, templates/process.md, data/vision.md, data/accountability.md]
tools-used: [Read, Write, Glob]
---

# ceos-process

Document, simplify, and audit core company processes — the 6th EOS component. Every company has a handful of core processes that must be documented as checklists, simplified to their essential steps, and followed by all.

## When to Use

- "Document our sales process" or "create a new process"
- "Show our processes" or "what processes do we have?"
- "Audit process FBA scores" or "how well are we following our processes?"
- "Simplify the hiring process" or "reduce this process to essentials"
- "Update the onboarding process" or "add a step to the deployment process"
- Any conversation about documenting how work gets done

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/processes/` | Process documentation files |
| `data/vision.md` | V/TO document (Core Focus and Proven Process for alignment) |
| `templates/process.md` | Template for creating new process files |
| `data/accountability.md` | Accountability Chart (seat owners for process-owner alignment) |

### Process File Format

Each process is a markdown file with YAML frontmatter:

```yaml
id: process-001
title: "Customer Onboarding"
owner: "brad"
fba_score: 85
last_audited: "2026-02-14"
status: active          # draft | active | deprecated
created: "2026-01-15"
```

**Status values:**
- `draft` — being documented, not yet in use
- `active` — documented and in use, subject to FBA audits
- `deprecated` — no longer followed (kept for historical reference)

**File naming:** `process-NNN-slug.md` where NNN is a zero-padded ID and slug is the title slugified (lowercase, hyphens, no special chars).

**FBA (Followed-By-All) score:** A percentage from 0-100 representing how consistently the team follows the documented process. Target: 80%+.

## Process

### Mode: Document

Use when creating a new process or updating an existing one.

#### Step 1: Determine New or Update

Check the user's request:
- If they name a specific existing process → load it for editing
- If they want a new process → continue with creation

For updates, read the existing process file, display the current content, and discuss what needs to change.

#### Step 2: Review Context

Before creating a new process, read and briefly reference:
- The **Core Focus** and **Proven Process** from `data/vision.md` — processes should align with how the company operates
- Any **existing processes** in `data/processes/` — avoid duplicates and ensure coverage

Display a quick summary: "You currently have N documented processes: [titles]."

#### Step 3: Collect Process Details

For a new process, collect:

1. **Title** — short, specific name (e.g., "Customer Onboarding", "Sales Process", "Deployment Pipeline")
2. **Owner** — one person who is accountable for this process (never shared)
3. **Purpose** — why does this process exist? What outcome does it ensure?
4. **Steps** — the numbered checklist of actions

For the steps, guide the user:
- Each step should start with an action verb ("Send", "Review", "Schedule", "Create")
- Aim for 5-20 steps. If more than 20, suggest the process might need to be split
- Steps should be specific enough that someone new could follow them
- Nested steps (1.1, 1.2) are allowed for complex steps, but maximum 2 levels deep

#### Step 4: Validate

- **3-7 core processes.** Count existing active processes. If adding this one would exceed 7, warn: "EOS recommends 3-7 core processes. You'll have N. Is this a core process or a supporting one?" Don't block — just flag.
- **One owner.** If the user tries to assign multiple owners, explain: "Each process has one owner — the person accountable for it being documented, simplified, and followed. Who should own this?"
- **Step count.** If more than 30 steps, warn: "This process has 30+ steps. Consider splitting into sub-processes or simplifying."
- **Duplicate check.** If a process with a similar title already exists, ask: "A process called '[title]' already exists. Update that one, or create a new one?"
- **Seat alignment.** Cross-reference the process owner against `data/accountability.md`. The owner should hold the seat whose responsibilities align with the process's domain. Flag mismatches: "This process falls under [Seat] responsibilities. Should [Seat Owner] own it?"

#### Step 5: Generate the ID

Read existing process files in `data/processes/`. Find the highest `process-NNN` ID and increment. If no files exist, start at `process-001`.

#### Step 6: Write the File

Use `templates/process.md` as the template. Substitute:
- Frontmatter fields (id, title, owner, fba_score=0, last_audited=today, status=draft, created=today)
- Body sections (purpose, steps, owner name)

Write to `data/processes/process-NNN-slug.md`.

Show the user the complete file before writing. Ask: "Create this process?"

#### Step 7: Repeat or Finish

Ask: "Create another process, or are we done for now?"

When finished, display a summary table of all documented processes:

| Process | Owner | Status | FBA |
|---------|-------|--------|-----|
| Customer Onboarding | brad | active | 85% |
| Sales Process | daniel | draft | — |

---

### Mode: Audit

Use for reviewing FBA scores across all documented processes.

#### Step 1: Read All Processes

Read all process files from `data/processes/`. Parse the frontmatter for status, FBA score, and last audited date.

If no process files exist, display: "No processes documented yet. Use 'document a process' to create your first core process."

#### Step 2: Display FBA Table

Show a status table of all processes:

| Process | Owner | Status | FBA | Last Audited |
|---------|-------|--------|-----|-------------|
| Customer Onboarding | brad | active | 85% | 2026-01-15 |
| Sales Process | daniel | active | 70% | 2025-12-01 |
| Deployment Pipeline | brad | active | 95% | 2026-02-01 |

#### Step 3: Highlight Issues

Flag processes that need attention:
- **FBA below 80%**: "⚠️ Sales Process (70%) is below the 80% target"
- **Not audited in 90+ days**: "⚠️ Sales Process was last audited 75 days ago"
- **Still in draft**: "📝 [Process] is still in draft — ready to activate?"

#### Step 4: Update FBA Scores

Offer to update scores: "Want to update any FBA scores?"

For each score update:
1. Ask for the new FBA score (validate 0-100)
2. Show the change: "Sales Process: 70% → 82%"
3. Ask for approval before writing

#### Step 5: Record the Audit

For each updated process:
1. Update `fba_score` in frontmatter
2. Update `last_audited` to today's date
3. Add an entry to the Audit History section: `- YYYY-MM-DD: FBA audit — score updated to NN%`

#### Step 6: FBA Scoring Guidance

If the user asks how to determine FBA scores, suggest:
- **Observation**: Walk through the process yourself — did each step happen as documented?
- **Team survey**: Ask each person involved: "On a scale of 0-100, how consistently do you follow this process?"
- **Spot checks**: Review recent work products — do they reflect the documented steps?
- **Average**: Take the average across observations/surveys for the final score

---

### Mode: Simplify

Use to reduce a process to its essential steps — the 20% of steps that produce 80% of results.

#### Step 1: Select the Process

If the user named a specific process, load it. Otherwise, list all processes and ask which one to simplify.

#### Step 2: Display Current Steps

Show all current steps with numbering:

```
Current steps for "Customer Onboarding" (12 steps):

1. Send welcome email
2. Schedule kickoff call
3. Prepare onboarding packet
4. Run kickoff call
5. Set up user account
6. Send login credentials
7. Schedule training session
8. Run training session
9. Check in after 24 hours
10. Check in after 1 week
11. Send satisfaction survey
12. Review survey results
```

#### Step 3: Apply the 20/80 Rule

Guide the user through simplification:

"The 20/80 rule says roughly 20% of these steps produce 80% of the value. Which steps are absolutely essential — the ones that, if skipped, would break the process?"

Walk through each step and ask: **"Keep or remove?"**

For each step:
- **Keep** — essential to the process working
- **Remove** — nice to have but not critical
- If the user is unsure, ask: "If you skipped this step, would the process still achieve its purpose?"

#### Step 4: Show the Diff

Display before and after:

```
Simplified "Customer Onboarding": 12 → 7 steps

Removed:
  3. Prepare onboarding packet
  9. Check in after 24 hours
  11. Send satisfaction survey
  12. Review survey results

Kept:
  1. Send welcome email
  2. Schedule kickoff call
  4. Run kickoff call
  5. Set up user account
  6. Send login credentials
  7. Schedule training session
  8. Run training session
```

#### Step 5: Validate

- Must have at least 1 step remaining. If the user removed all steps: "A process must have at least one step. Restore some steps, or mark this process as deprecated instead?"
- Show the reduction ratio: "Reduced from 12 to 7 steps (42% reduction)"

#### Step 6: Write the Updated File

Show the complete updated file. Ask: "Apply this simplification?"

If approved:
1. Rewrite the Process Steps section with only the kept steps (renumbered sequentially)
2. Add an entry to Audit History: `- YYYY-MM-DD: Simplified from N to M steps`

#### Step 7: Suggest FBA Re-Audit

After simplification: "The process has changed — consider re-auditing FBA scores next week to see if the simplified version is easier to follow."

## Output Format

**Document mode:** Show the complete process file before writing. End with a summary table of all processes.
**Audit mode:** FBA status table with highlighting for processes below target or overdue for audit.
**Simplify mode:** Before/after diff of the step list, then the complete updated file.

## Guardrails

- **Always show diff before writing.** Never modify a process file without showing the change and getting approval.
- **One owner per process.** If the user tries to assign multiple owners, explain and ask them to pick one.
- **3-7 core processes.** Warn (don't block) if outside this range. Distinguish core from supporting processes.
- **FBA scores are 0-100.** Validate input. Reject values outside this range.
- **Simplify must leave at least 1 step.** If all steps are removed, suggest deprecating the process instead.
- **Cross-reference V/TO.** When documenting processes, reference the Core Focus and Proven Process from `data/vision.md`. Processes should align with how the company operates.
- **ID uniqueness.** Always check existing files before assigning an ID to avoid collisions.
- **Don't delete deprecated processes.** Change status to `deprecated` instead. Git history provides the audit trail.
- **Steps start with verbs.** Guide users toward actionable steps ("Send email", "Review document") rather than vague descriptions ("Email stuff").
- **Don't auto-invoke other skills.** Mention `ceos-vto` when relevant for Core Focus alignment, but let the user decide when to switch workflows.
- **Sensitive data warning.** On first use, remind the user: "Process documentation may contain sensitive operational details. Use a private repo."

## Integration Notes

### Self-Contained

This skill manages process documentation independently. No other CEOS skills read from or write to `data/processes/`.

### V/TO Reference (ceos-vto)

- **Read:** `ceos-process` reads `data/vision.md` for Core Focus and Proven Process alignment when documenting new processes. It does not write to the V/TO file.
- **Suggested flow:** If a process doesn't align with the Core Focus, suggest reviewing the V/TO with `ceos-vto`.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-process` reads `data/accountability.md` when documenting or auditing processes to validate that process owners match seat responsibilities. A sales process should be owned by whoever holds the Sales & Marketing seat; a delivery process by the Delivery seat owner.
- **Suggested flow:** If a process owner doesn't match the responsible seat, suggest: "This process falls under [Seat] responsibilities. Should [Seat Owner] own it?"

### Why Mostly Self-Contained?

Unlike other EOS components that cross-reference each other (Rocks → V/TO, Scorecard → L10), core processes are standalone documentation. They reference the V/TO for alignment and the Accountability Chart for owner validation, and may be referenced informally during L10 meetings or annual planning, but there are no formal data dependencies between process files and other CEOS data files.
