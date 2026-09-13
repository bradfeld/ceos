# Skill Structure Contract

The canonical specification for CEOS skill structure. Every skill in `skills/ceos-*/SKILL.md` MUST follow this structure, in this order.

For a practical authoring guide with examples and tips, see [skill-authoring.md](skill-authoring.md).

## The 8 Sections

### 1. YAML Frontmatter

```yaml
---
name: ceos-skillname
description: Use when [trigger phrase describing when this skill activates]
file-access: [data/owned-dir/, templates/template.md, data/read-only-source]
tools-used: [Read, Write, Glob]
---
```

- **name**: Matches the directory name (`ceos-vto`, `ceos-rocks`, etc.)
- **description**: Starts with "Use when" — this is the trigger, not a summary of what the skill does
- **file-access**: Array of data paths this skill reads or writes
- **tools-used**: Array of Claude Code tools the skill uses (Read, Write, Edit, Glob, Bash)

### 2. `# skill-name` Heading

Top-level heading matching the `name` field, followed by a one-paragraph description of the skill's purpose.

### 3. `## When to Use`

Bullet list of trigger phrases a user might say. These help Claude match user intent to the correct skill.

### 4. `## Context`

Background information needed before the skill can operate:

- **Finding the CEOS Repository**: Every skill MUST include this boilerplate — search upward for `.ceos` marker file, error if not found, then `git pull --ff-only` to sync.
- **Key Files**: Table mapping file paths to purposes.
- **Data formats**: YAML frontmatter schemas, naming conventions, quarter format (`YYYY-QN`).

### 5. `## Process`

Step-by-step workflow. Skills with multiple modes (e.g., Create/Review/Update) document each mode as a subsection. Each step should be specific enough for Claude to follow without ambiguity.

### 6. `## Output Format`

How to display results to the user — table formats, summary layouts, progress indicators.

### 7. `## Guardrails`

Rules the skill MUST follow. Every skill MUST include these two universal guardrails:

**Auto-invoke guardrail**: "Don't auto-invoke skills." When skill results suggest using another skill (e.g., quarterly conversation reveals People Analyzer needs updating), mention the option but let the user decide. Say "Would you like to update X?" rather than doing it automatically.

**Sensitive data warning**: On first use in a session, remind the user that CEOS data contains sensitive information (performance evaluations, strategic decisions, financial targets, personnel matters). The repo should be private.

### 8. `## Integration Notes`

Documents how this skill relates to other skills. Each integration entry specifies:

- **Direction**: Read, Write, or Related
- **What data**: Which files/directories are accessed
- **Purpose**: Why the cross-skill access exists

Ends with a **Write Principle** or **Orchestration Principle** statement declaring which data directory this skill exclusively owns.

**Write Principle example**: "Only `ceos-rocks` writes to `data/rocks/`. Other skills read Rock data for reference."

**Orchestration Principle** (for L10 and Annual): "This skill reads data from multiple skills during the session but defers to each skill for formal create/update operations."

## Data Ownership

Each skill owns exactly one data directory. Other skills may read from it but MUST NOT write to it.

| Skill | Writes To | Reads From (other skills' data) |
|-------|-----------|-------------------------------|
| ceos-vto | `data/vision.md` | `data/accountability.md`, `data/rocks/` |
| ceos-accountability | `data/accountability.md` | `data/people/` |
| ceos-rocks | `data/rocks/` | `data/vision.md` |
| ceos-scorecard | `data/scorecard/` | — |
| ceos-ids | `data/issues/` | — |
| ceos-process | `data/processes/` | `data/vision.md` |
| ceos-people | `data/people/` | `data/vision.md`, `data/accountability.md` |
| ceos-todos | `data/todos/` | — |
| ceos-l10 | `data/meetings/l10/` | `data/scorecard/`, `data/rocks/`, `data/issues/` |
| ceos-quarterly | `data/conversations/` | `data/vision.md`, `data/accountability.md`, `data/rocks/`, `data/people/` |
| ceos-annual | `data/annual/` | `data/vision.md`, `data/rocks/`, `data/scorecard/`, `data/issues/`, `data/accountability.md`, `data/people/` |
| ceos-quarterly-planning | `data/quarterly/` | `data/rocks/`, `data/scorecard/`, `data/vision.md`, `data/issues/` |
| ceos-cashflow | `data/cashflow/` | `data/accountability.md`, `data/scorecard/` |
| ceos-checkup | `data/checkups/` | `data/vision.md`, `data/accountability.md`, `data/rocks/`, `data/scorecard/`, `data/people/`, `data/issues/` |
| ceos-delegate | `data/delegate/` | `data/accountability.md`, `data/people/` |
| ceos-assistance | `data/assistance/` | `data/accountability.md`, `data/delegate/` |
| ceos-trust | `data/trust/` | `data/accountability.md`, `data/checkups/` |
| ceos-lma | `data/lma/` | `data/accountability.md`, `data/people/`, `data/clarity/`, `data/meetings/l10/`, `data/conversations/` |
| ceos-kickoff | `data/meetings/kickoff/` | `data/vision.md`, `data/rocks/`, `data/scorecard/`, `data/issues/`, `data/accountability.md` |
| ceos-clarity | `data/clarity/` | `data/vision.md`, `data/rocks/`, `data/scorecard/`, `data/issues/open/` |
| ceos-dashboard | *(none — read-only)* | `data/vision.md`, `data/rocks/`, `data/scorecard/`, `data/issues/open/`, `data/people/`, `data/accountability.md` |

**Orchestrator skills** (`ceos-l10`, `ceos-annual`, `ceos-quarterly-planning`, `ceos-kickoff`) read broadly but write only to their own data directory. They reference data from other skills during sessions and suggest follow-up actions via those skills.

**Assessment skills** (`ceos-checkup`) read broadly for context but write only to their own data directory. They synthesize data from all Six Key Components to produce health assessments.

**Development skills** (`ceos-delegate`) read from related skills for context (accountability chart seats, people evaluations) but write only to their own data directory. They help leaders improve their personal effectiveness.

## Creating New Skills

Before creating a new skill, verify:

1. **Distinct EOS component**: Does this map to a recognized EOS tool or process?
2. **Clear data ownership**: Can you identify exactly one data directory this skill will own?
3. **Doesn't duplicate existing skill**: Review the data ownership table — does an existing skill already cover this?
4. **Clear user workflow**: Can you describe when a user would invoke this skill?

When creating:

1. Create `skills/ceos-newskill/SKILL.md` following the 8-section structure above
2. Include all required frontmatter fields
3. Include both universal guardrails
4. Write the Integration Notes section documenting all cross-skill data access
5. Create `data/newskill/.gitkeep` (data directory)
6. Create `templates/newskill.md` (template file, if the skill creates data files)
7. Add a symlink: `ln -s /path/to/ceos/skills/ceos-newskill ~/.claude/skills/ceos-newskill`

### Files to Update (CRITICAL — all must be done in the same commit)

Every new skill requires updates to these files. Missing any causes documentation drift.

| File | What to Update |
|------|---------------|
| `docs/skill-structure.md` | Add row to data ownership table |
| `AGENTS.md` | Add `data/` entry to directory structure |
| `README.md` | Add row to skills table, update skill count in heading + intro paragraph |
| `setup.sh` | Add `mkdir -p "$CEOS_ROOT/data/newskill"` to the `init` function |
| `docs/skill-reference.md` | Add skill entry (description, modes, example, files table) |
| `docs/eos-primer.md` | Update Six Key Components table if the skill maps to one |
| `docs/data-format-spec.md` | Add data format section if the skill creates new file types |

### Exemplar Skills

- **`ceos-accountability`** — Clean example of all 8 sections with straightforward data ownership
- **`ceos-quarterly`** — Best example of Integration Notes with multiple cross-skill reads and a clear Write Principle
- **`ceos-l10`** — Example of an orchestrator skill with the Orchestration Principle
