# CEOS

**Run EOS with AI.** CEOS brings the [Entrepreneurial Operating System](https://www.eosworldwide.com/) to [Claude Code](https://docs.anthropic.com/en/docs/claude-code), giving your leadership team 16 AI-powered skills for Vision, Accountability Chart, Rocks, Scorecard, L10 Meetings, IDS, To-Dos, Process, People Analyzer, Quarterly Conversations, Annual Planning, Quarterly Planning, Organizational Checkup, Delegate and Elevate, Clarity Break, and EOS Kickoff.

Clone. Setup. Run your business.

## What is CEOS?

CEOS (Claude + EOS) is a Claude Code skills package that implements the core EOS tools as AI-assisted workflows. Your EOS data lives as markdown files in your repo — human-readable, GitHub-renderable, and git-diffable. No database, no SaaS subscription, no vendor lock-in.

**Designed for CEOs and leadership teams**, not developers. If you can run `git clone` and `./setup.sh`, you're ready. Start with Focus Day, build your V/TO in Vision Building Days, then run EOS with the full skill set.

## Quick Start

```bash
# 1. Clone (or fork for your company)
git clone https://github.com/bradfeld/ceos.git
cd ceos

# 2. Install skills + initialize your company data
./setup.sh init

# 3. Start using EOS in any Claude Code session
claude
> "Let's set our quarterly rocks"
```

## The 20 Skills

| Skill | What It Does | Try Saying... |
|-------|-------------|---------------|
| **ceos-vto** | Vision/Traction Organizer — your company's strategic document | "Review our vision" or "Update our 10-year target" |
| **ceos-accountability** | Accountability Chart — seats, owners, and 5 roles per seat | "Show the org chart" or "Audit the accountability chart" |
| **ceos-rocks** | Quarterly Rocks — 90-day priorities with owners and outcomes | "Set rocks for Q1" or "How are our rocks tracking?" |
| **ceos-scorecard** | Weekly Measurables — track the 5-15 numbers that matter | "Log this week's scorecard" or "Show scorecard trends" |
| **ceos-l10** | Level 10 Meetings — structured weekly leadership meetings | "Run our L10" or "Start our weekly meeting" |
| **ceos-ids** | Identify, Discuss, Solve — structured issue resolution | "We have an issue" or "IDS this problem" |
| **ceos-todos** | To-Do Tracking — actions with owners, deadlines, and completion rates | "Show my to-dos" or "To-do completion rate" |
| **ceos-process** | Core Processes — document, simplify, and track followability | "Document our sales process" or "Audit process FBA scores" |
| **ceos-people** | People Analyzer — right people, right seats (Core Values + GWC) | "Evaluate Brad" or "Quarterly people review" |
| **ceos-quarterly** | Quarterly Conversations — formal manager/direct report check-ins | "Run quarterly conversation for Brad" or "Schedule quarterly conversations" |
| **ceos-annual** | Annual Planning — year-end V/TO refresh and Rock setting | "Plan next year" or "Review 2025" or "Refresh our vision" |
| **ceos-quarterly-planning** | Quarterly Planning — structured quarterly offsite for the leadership team | "Run quarterly planning" or "Start our quarterly session" |
| **ceos-checkup** | Organizational Checkup — 20-question health assessment across Six Key Components | "Run an organizational checkup" or "How healthy is our organization?" |
| **ceos-delegate** | Delegate and Elevate — 4-quadrant task audit for leadership focus | "Run delegate and elevate for Brad" or "What should I be delegating?" |
| **ceos-clarity** | Clarity Break — scheduled strategic thinking time away from day-to-day | "Take a clarity break" or "Show clarity break history" |
| **ceos-kickoff** | EOS Kickoff — Focus Day, Vision Building Day 1, Vision Building Day 2 | "Run our Focus Day" or "Start EOS implementation" |
| **ceos-lma** | Leadership + Management = Accountability — assess how you lead and manage | "Run LMA assessment" or "How am I doing as a manager?" |
| **ceos-cashflow** | The 8 Cash Flow Drivers — financial levers behind cash and profitability | "Assess our cash flow" or "Where can we improve margins?" |
| **ceos-trust** | Trust Builders — vulnerability-based trust exercises for the leadership team | "Build team trust" or "What trust exercise is next?" |
| **ceos-assistance** | The Stack — daily operational delegation and leader-assistant standups | "Add to the stack" or "Run the daily meeting" |

## How It Works

```
┌─────────────────────────────────┐
│  skills/ceos-*/SKILL.md         │  ← Claude Code skills (16 EOS tools)
├─────────────────────────────────┤
│  data/ + templates/             │  ← Your EOS data (markdown files)
│  (markdown + YAML frontmatter)  │     Human-readable, git-tracked
├─────────────────────────────────┤
│  setup.sh                       │  ← One-command installer
└─────────────────────────────────┘
```

**Three layers:**

- **Upstream** (`bradfeld/ceos`) — Skills, templates, docs. No company data.
- **Your fork** (`your-company/ceos`) — Your team's EOS data in `data/`.
- **Personal config** (`.ceos-user.yaml`, gitignored) — Per-person preferences.

## Data Format

All EOS data is stored as markdown with YAML frontmatter. Example Rock:

```markdown
---
id: rock-001
title: Launch Beta Program
owner: brad
quarter: 2026-Q1
status: on_track
created: 2026-01-02
due: 2026-03-31
---

## Measurable Outcome

Beta program launched with 10+ users actively providing feedback.

## Milestones

- [ ] Beta invitation system built
- [ ] First 10 users onboarded
- [ ] Feedback collection process established
```

Everything is a file. Git history is your audit trail.

## For Teams

CEOS is built for multi-person leadership teams:

1. **Fork** this repo to your company's GitHub
2. Run `./setup.sh init` — each team member does this once
3. **Commit data** to your fork — git is the collaboration layer
4. **Pull upstream** for skill updates — your data stays untouched

## Security

CEOS skills are **instructions that Claude Code follows with your permissions** — including reading files, writing files, and running commands. This is powerful, but it means you should treat skill files like code: review before you run.

### If you fork or clone from upstream (`bradfeld/ceos`)

The official skills are maintained and reviewed by the project maintainers. Pulling upstream updates is safe as long as you verify the remote:

```bash
git remote get-url origin   # Should point to bradfeld/ceos or your company's fork
```

### If you install skills from other sources

Before running `./setup.sh` on a repo you didn't write:

1. **Read every `SKILL.md` file.** They're plain markdown — you can understand what they do.
2. **Watch for red flags:** instructions that access files outside `data/` or `templates/`, references to external URLs or APIs, requests for credentials or API keys, or shell commands beyond basic git operations.
3. **Check the git history.** `git log --oneline skills/` shows what changed and when.

### For contributors

If you're submitting a skill via pull request, see the [Skill Security Review](CONTRIBUTING.md#skill-security-review) section in CONTRIBUTING.md for what reviewers look for.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Git
- That's it. No Node.js, no Python, no Docker.

## Contributing

We welcome contributions from both EOS practitioners and developers. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

[MIT](LICENSE) — Use it however you want. No barriers.

---

*CEOS is an independent open-source project. It is not affiliated with or endorsed by EOS Worldwide.*
