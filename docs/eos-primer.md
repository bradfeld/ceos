# EOS Primer for Developers

A quick introduction to the Entrepreneurial Operating System (EOS) for developers who want to contribute to CEOS.

## What is EOS?

[EOS](https://www.eosworldwide.com/) (Entrepreneurial Operating System) is a business management framework used by over 250,000 companies worldwide. It gives leadership teams a set of practical tools to get everyone on the same page, execute on priorities, and build a healthy, functional team.

Think of it as a "framework" for running a business — the same way React is a framework for building UIs. It provides structure, vocabulary, and repeatable processes.

## What is Claude Code?

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) is Anthropic's CLI tool for AI-assisted development. It uses "skills" — markdown files that teach Claude how to perform specific workflows. CEOS is a set of skills that implement EOS tools.

## The 6 EOS Components

EOS organizes everything into 6 key components. CEOS implements tools for all of them:

| Component | What It Means | CEOS Skills |
|-----------|--------------|-------------|
| **Vision** | Where are we going? Get everyone aligned on the destination. | `ceos-vto`, `ceos-annual` |
| **People** | Right people in the right seats. | `ceos-accountability`, `ceos-people`, `ceos-quarterly`, `ceos-delegate`, `ceos-lma`, `ceos-trust` |
| **Data** | Run the business on facts, not feelings. Track weekly numbers. | `ceos-scorecard`, `ceos-checkup`, `ceos-cashflow`, `ceos-dashboard` |
| **Issues** | Surface problems. Solve them systematically. | `ceos-ids` |
| **Process** | Document your core processes so they're consistent. | `ceos-process` |
| **Traction** | Execute on priorities. Rocks + meetings = accountability. | `ceos-rocks`, `ceos-l10`, `ceos-kickoff`, `ceos-quarterly-planning`, `ceos-todos`, `ceos-clarity`, `ceos-assistance` |

## EOS Terminology

If you see these terms in the codebase, here's what they mean:

| Term | Definition | Where in CEOS |
|------|-----------|---------------|
| **V/TO** | Vision/Traction Organizer — the one-page strategic plan | `data/vision.md` |
| **Core Values** | 3-7 guiding principles that define culture | Section in V/TO |
| **Core Focus** | Company's purpose + niche (the "sweet spot") | Section in V/TO |
| **10-Year Target** | One big, measurable long-term goal | Section in V/TO |
| **3-Year Picture** | What the company looks like in 3 years | Section in V/TO |
| **1-Year Plan** | This year's measurable goals | Section in V/TO |
| **Rock** | A 90-day priority with one owner and a measurable outcome | `data/rocks/YYYY-QN/` |
| **Scorecard** | The 5-15 weekly metrics that show business health | `data/scorecard/` |
| **Measurable** | A single metric on the Scorecard, owned by one person | Row in Scorecard |
| **L10** | Level 10 Meeting — the weekly 90-minute leadership meeting | `data/meetings/l10/` |
| **IDS** | Identify, Discuss, Solve — the structured problem-solving process | `data/issues/` |
| **5 Whys** | Root cause technique: keep asking "why?" until you find the real issue | Used during IDS Identify stage |
| **Issues List** | Running list of problems to solve during L10 meetings | `data/issues/open/` |
| **To-Do** | A specific action with an owner and 7-day due date | Created during IDS Solve stage |
| **Leading Indicator** | An activity metric (calls made) vs a result metric (revenue) | Preferred in Scorecard |
| **5-5-5** | A 15-minute quick check-in: 5 min Employee Speaks, 5 min Manager Speaks, 5 min Together. Lightweight version of the Quarterly Conversation covering Core Values, Rocks, and GWC | `data/conversations/YYYY-QN/*-quick.md` |

## Why Markdown + YAML?

CEOS stores all EOS data as markdown files with YAML frontmatter. This is a deliberate architectural choice:

- **Human-readable** — Open any file in a text editor or on GitHub and understand it immediately
- **Git-friendly** — Every change is tracked, diffable, and reversible. Git history is your audit trail.
- **Portable** — No database, no proprietary format, no vendor lock-in. Parse it with any language.
- **Collaborative** — Teams use git workflows (fork, branch, PR) to manage their EOS data together

The YAML frontmatter stores structured data (status, priority, dates) that skills parse programmatically. The markdown body stores human-written content (notes, perspectives, outcomes).

## How CEOS Skills Work

Each skill is a `SKILL.md` file in `skills/ceos-*/`. When you run Claude Code, it discovers skills via symlinks in `~/.claude/skills/` and matches your intent to the right skill based on trigger phrases.

```
You say: "Let's set our quarterly rocks"
         ↓
Claude matches: ceos-rocks skill
         ↓
Skill reads: data/rocks/, templates/rock.md
         ↓
Skill guides you through: Setting, Tracking, or Scoring
         ↓
Result: New rock files in data/rocks/2026-Q1/
```

Skills never auto-invoke each other. The `ceos-l10` skill might mention that `ceos-ids` can handle issue creation, but it lets you decide when to switch.

## Further Learning

- **EOS Worldwide**: [eosworldwide.com](https://www.eosworldwide.com/) — the official EOS organization
- **Traction** by Gino Wickman — the book that started it all
- **CEOS Skills**: See [skill-reference.md](skill-reference.md) for detailed documentation of each skill
- **Data Format**: See [data-format-spec.md](data-format-spec.md) for the technical specification
