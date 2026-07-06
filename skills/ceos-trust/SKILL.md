---
name: ceos-trust
description: Use when building vulnerability-based trust through quarterly team exercises from the EOS Trust Builders toolbox
file-access: [data/trust/, templates/trust-exercise.md, data/accountability.md, data/checkups/]
tools-used: [Read, Write, Glob]
---

# ceos-trust

Facilitate the 10 Trust Builder exercises from the EOS Toolbox, progressing from low to high vulnerability. Acts as a facilitation guide — providing instructions, timing, debrief questions, and recording outcomes — rather than trying to replicate exercises digitally. Teams typically do one exercise per quarter, building deeper trust over time. Drawn from Patrick Lencioni's "Five Dysfunctions of a Team" framework.

**Not for:** People evaluation (use `ceos-people`), organizational health assessment (use `ceos-checkup`), or performance conversations (use `ceos-quarterly`). The Trust Builders are team-level exercises focused on vulnerability-based trust, not individual assessment.

## When to Use

- "Build team trust" or "trust building exercise"
- "Run the next trust exercise" or "facilitate trust builders"
- "What trust exercise is next?" or "trust exercise schedule"
- "Show trust exercise history" or "review trust progression"
- "Personal histories exercise" or any specific exercise name
- "How is our team trust?" or "trust level check"
- "Quarterly trust exercise" or "team bonding exercise"
- Any discussion about vulnerability-based trust, team bonding, or the EOS Trust Builders

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/trust/` | Exercise records — one file per completed exercise |
| `templates/trust-exercise.md` | Template for recording exercise outcomes |
| `data/accountability.md` | Team composition for participant suggestions (read-only — use ceos-accountability to modify) |
| `data/checkups/` | Organizational Checkup scores for trust cross-reference (read-only — use ceos-checkup to modify) |

### The 10 Exercises

| # | Exercise | Vulnerability | Time Box | Description |
|---|----------|--------------|----------|-------------|
| 1 | Personal Histories | Low | 30-45 min | Each team member shares personal background (hometown, family, first job, hobbies) |
| 2 | DISC/Kolbe Profiles | Low | 45-60 min | Share and discuss personality/working style assessment results |
| 3 | Lifeline Exercise | Medium | 45-60 min | Map significant life events on a timeline, share with the team |
| 4 | One Thing | Medium | 20-30 min | Each person shares one thing the team doesn't know about them |
| 5 | Feedback Round | Medium | 45-60 min | Structured positive and constructive feedback for each team member |
| 6 | Strengths Spotlight | Medium | 30-45 min | Each person identifies their top strengths, team validates and adds |
| 7 | Conflict Norms | Medium-High | 45-60 min | Establish how the team will handle disagreement and conflict |
| 8 | Accountability Partners | Medium-High | 30-45 min | Pair up for mutual accountability check-ins between meetings |
| 9 | Team Effectiveness Debrief | High | 60-90 min | Rate and discuss how the team works together as a unit |
| 10 | Vulnerability Circle | High | 30-60 min | Share a current struggle, fear, or area where you need help |

### Vulnerability Levels

| Level | Exercises | What It Means |
|-------|-----------|---------------|
| Low | 1-2 | Safe sharing — factual information, low personal risk |
| Medium | 3-6 | Personal sharing with moderate risk — life events, feedback, strengths |
| Medium-High | 7-8 | Navigating conflict and accountability — requires existing trust |
| High | 9-10 | Deep vulnerability — honest assessment of team and personal struggles |

### Exercise Record Format

Each completed exercise is a markdown file at `data/trust/YYYY-MM-DD-exercise-slug.md` with YAML frontmatter:

```yaml
date: "2026-02-16"
exercise_number: 1
exercise_name: "Personal Histories"
participants: ["Brad Feld", "Daniel"]
facilitator: "Brad Feld"
duration_minutes: 35
vulnerability_level: low
status: complete
```

**File naming:** `YYYY-MM-DD-exercise-slug.md` — date prefix for chronological ordering, exercise slug identifies the type.

### Exercise Slug Reference

| # | Exercise | Slug |
|---|----------|------|
| 1 | Personal Histories | `personal-histories` |
| 2 | DISC/Kolbe Profiles | `disc-kolbe-profiles` |
| 3 | Lifeline Exercise | `lifeline-exercise` |
| 4 | One Thing | `one-thing` |
| 5 | Feedback Round | `feedback-round` |
| 6 | Strengths Spotlight | `strengths-spotlight` |
| 7 | Conflict Norms | `conflict-norms` |
| 8 | Accountability Partners | `accountability-partners` |
| 9 | Team Effectiveness Debrief | `team-effectiveness-debrief` |
| 10 | Vulnerability Circle | `vulnerability-circle` |

## Process

### Mode: Facilitate

Use when guiding the team through the next Trust Builder exercise. This is the primary mode — one exercise per session.

#### Step 1: Determine Which Exercise

Read all files from `data/trust/` via `Glob("data/trust/*.md")`. Parse YAML frontmatter to find completed exercises by `exercise_number`.

Determine the next exercise in sequence (lowest number not yet completed).

- **No exercises completed:** Start with #1 Personal Histories.
- **Some completed:** Recommend the next in sequence.
- **All 10 completed:** "All 10 Trust Builder exercises are complete! Consider starting Cycle 2 — repeating exercises builds deeper trust each time. Recommend starting again with #1 Personal Histories."

Display the recommendation:

```
Next Trust Builder: #N [Name]
Vulnerability level: [low/medium/high]
Time box: [N-N] minutes
Last exercise: #[N-1] [Name] on [date]

Ready to facilitate?
```

#### Step 2: Check Readiness

**For medium or higher vulnerability exercises (3+):**
"This is a [level]-vulnerability exercise. Ensure the team has completed the earlier exercises and the environment feels psychologically safe."

**For exercise #2 (DISC/Kolbe Profiles):**
"Note: Participants should have completed their DISC and/or Kolbe assessments before this exercise. Has everyone taken their assessments?"

**For exercise #5 (Feedback Round):**
"Note: This exercise involves giving and receiving direct feedback. Remind the team that feedback should be specific, actionable, and delivered with positive intent."

**For exercise #7+ (Medium-High and High):**
"This exercise requires a foundation of trust from earlier exercises. If the team hasn't built that foundation, consider revisiting exercises 1-6 first."

#### Step 3: Read Participants

Read `data/accountability.md` to identify leadership team members. Suggest them as participants.

"Who is participating? (Default: leadership team from Accountability Chart)"

Allow the user to confirm or modify the participant list.

#### Step 4: Provide Facilitation Guide

Display the exercise-specific facilitation guide based on the exercise number. Each exercise follows this structure:

**Purpose → Setup → Steps → Time Management → Debrief Questions**

---

**Exercise 1: Personal Histories**

*Purpose:* Break down barriers by sharing personal backgrounds. This is the foundation — it humanizes teammates beyond their work roles.

*Setup:* Gather the team in a comfortable setting. No notes needed. Go around the table.

*Steps:*
1. Each person shares (3-5 minutes per person):
   - Where did you grow up?
   - How many siblings do you have?
   - What was your first job?
   - What's a unique hobby or interest?
   - What's something most people don't know about you?
2. After each person shares, allow brief reactions (no extended discussion)
3. Complete the full round before moving to debrief

*Time Management:* 3-5 min per person + 10 min debrief. For a team of 6: ~40 minutes total.

*Debrief Questions:*
1. What surprised you about someone's background?
2. Did you discover something in common with a teammate?
3. How does knowing this personal context change how you might work together?

---

**Exercise 2: DISC/Kolbe Profiles**

*Purpose:* Understand each other's working styles to improve communication and reduce friction.

*Setup:* All participants must have completed their DISC and/or Kolbe assessments beforehand. Print or display results.

*Steps:*
1. Each person shares their profile (3-5 minutes):
   - Their dominant DISC style (D, I, S, or C)
   - Their Kolbe MO (if available)
   - "Here's what this means about how I work best..."
   - "Here's what might frustrate me or slow me down..."
2. After all have shared, discuss as a team:
   - Where do profiles complement each other?
   - Where might profiles clash?
   - What accommodations could help?

*Time Management:* 5 min per person + 15-20 min group discussion.

*Debrief Questions:*
1. Which profile differences explain past friction?
2. How can we use this knowledge to communicate better?
3. What's one thing you'll do differently knowing your teammates' styles?

---

**Exercise 3: Lifeline Exercise**

*Purpose:* Build deeper understanding by sharing the significant events that shaped who you are.

*Setup:* Give each person a blank piece of paper. Draw a horizontal line (the lifeline) from birth to present. Mark significant events above the line (positive) and below the line (negative/challenging).

*Steps:*
1. Silent preparation (5-10 minutes): Each person maps their lifeline
2. Each person presents their lifeline (5-8 minutes):
   - Walk through the major events chronologically
   - Explain why each event was significant
   - Share how it shaped who you are today
3. After each presentation, team members may ask one clarifying question (optional)
4. No judgment, no advice — just listening

*Time Management:* 10 min prep + 8 min per person + 10 min debrief.

*Debrief Questions:*
1. What common themes did you notice across lifelines?
2. How does understanding someone's life journey affect your empathy for them?
3. What did it feel like to share? What did it feel like to listen?

---

**Exercise 4: One Thing**

*Purpose:* A quick exercise to build on existing trust by sharing something new and personal.

*Setup:* Simple round-table format. No preparation needed.

*Steps:*
1. Each person shares one thing the team doesn't know about them (2-3 minutes each)
   - Can be personal, professional, quirky, or meaningful
   - The "one thing" should feel slightly vulnerable — beyond surface-level facts
2. Brief reactions allowed after each share
3. Keep it light but genuine

*Time Management:* 3 min per person + 5 min debrief.

*Debrief Questions:*
1. What was the hardest part about choosing your "one thing"?
2. Did anyone's share change your perception of them?
3. What does this exercise tell you about the team's comfort level?

---

**Exercise 5: Feedback Round**

*Purpose:* Practice giving and receiving honest feedback in a structured, safe format.

*Setup:* Each person will give feedback to every other team member. Prepare by thinking about one strength and one area for growth per person.

*Steps:*
1. Go person by person — one person is the "focus" at a time
2. Each team member shares for the focus person:
   - "Your greatest strength that helps the team is..."
   - "One area where I think you could grow is..."
3. The focus person listens without responding (except to say "thank you")
4. After all feedback is given, the focus person may ask ONE clarifying question
5. Move to the next focus person

*Time Management:* For a team of N, each round takes ~3 min × (N-1) people giving feedback + 2 min transition. Total: roughly 5-8 min per focus person.

*Debrief Questions:*
1. What feedback surprised you the most?
2. Was it harder to give or receive feedback?
3. What's one piece of feedback you want to act on this quarter?
4. How can we make giving feedback a more regular practice?

---

**Exercise 6: Strengths Spotlight**

*Purpose:* Reinforce what each person does best and ensure the team leverages individual strengths.

*Setup:* Each person prepares a list of their top 3-5 personal strengths before the session.

*Steps:*
1. Each person presents their self-identified strengths (2-3 minutes)
2. Team members respond:
   - Validate: "I agree — I see that strength when you..."
   - Add: "I'd also add [strength] because..."
   - Reframe: "I'd describe it slightly differently as..."
3. Record the final agreed-upon strengths list for each person

*Time Management:* 5-7 min per person + 10 min debrief.

*Debrief Questions:*
1. Were your self-identified strengths aligned with how the team sees you?
2. What strength did a teammate identify that you hadn't considered?
3. How can we better leverage each person's strengths in our daily work?

---

**Exercise 7: Conflict Norms**

*Purpose:* Establish explicit agreements for how the team will handle disagreement, preventing unhealthy conflict patterns.

*Setup:* Whiteboard or shared document. This is a group discussion, not individual sharing.

*Steps:*
1. Discuss current conflict patterns (10-15 minutes):
   - "When we disagree, what typically happens?"
   - "What works well about how we handle conflict?"
   - "What doesn't work?"
2. Brainstorm conflict norms (15-20 minutes):
   - How do we raise disagreements? (In the room, not in the hallway)
   - How do we ensure everyone speaks? (Round-table before open discussion)
   - How do we resolve impasses? (Leader decides after hearing all views)
   - What's off-limits? (Personal attacks, relitigating decided issues)
3. Agree on 5-7 specific norms (10-15 minutes)
4. Write them down — these become the team's conflict agreement

*Time Management:* 45-60 minutes for the full exercise.

*Debrief Questions:*
1. Which norm will be hardest for the team to follow?
2. What will we do when someone breaks a norm?
3. How will we revisit these norms to make sure they're working?

---

**Exercise 8: Accountability Partners**

*Purpose:* Create peer-to-peer accountability relationships that supplement the formal meeting structure.

*Setup:* Pair team members. Consider pairing people who don't work closely together or who have complementary strengths.

*Steps:*
1. Discuss the concept (5 minutes): Accountability partners check in between L10s to help each other stay on track with Rocks, To-Dos, and personal development
2. Form pairs (5-10 minutes): Each pair commits to:
   - A weekly 15-minute check-in (phone, video, or in-person)
   - What they'll cover: Rock progress, To-Do completion, one personal goal
   - How they'll hold each other accountable (direct, constructive)
3. Each pair shares their plan with the team (2-3 minutes per pair)
4. Set a review date (e.g., end of quarter) to assess whether the partnerships are working

*Time Management:* 30-45 minutes total.

*Debrief Questions:*
1. What do you hope to get from your accountability partner?
2. What makes you nervous about this level of accountability?
3. How will you handle it if your partner isn't following through?

---

**Exercise 9: Team Effectiveness Debrief**

*Purpose:* Honestly assess how the team functions as a unit — what's working, what isn't, and what needs to change.

*Setup:* Each person independently rates the team on 5 dimensions (1-5 scale) before the session:
1. Trust — Do we feel safe being vulnerable?
2. Conflict — Do we engage in productive disagreement?
3. Commitment — Do we align behind decisions?
4. Accountability — Do we hold each other to standards?
5. Results — Are we focused on collective outcomes?

(These map to Lencioni's Five Dysfunctions pyramid.)

*Steps:*
1. Share individual ratings (go around, no discussion yet) — 10 minutes
2. Identify the biggest gaps (where ratings diverge most) — 10 minutes
3. Deep-dive on the lowest-scoring dimension:
   - What specific behaviors drive the low score?
   - What would a "5" look like?
   - What's one thing we could change this quarter?
4. Repeat for the second-lowest dimension if time allows
5. Agree on 2-3 team commitments

*Time Management:* 60-90 minutes. This is the most substantive exercise.

*Debrief Questions:*
1. Were you surprised by anyone else's ratings?
2. Which dimension do you personally need to work on most?
3. What's the single most important thing we can improve as a team?
4. How will we measure whether we've improved by next quarter?

---

**Exercise 10: Vulnerability Circle**

*Purpose:* The deepest trust exercise — each person shares a current struggle, fear, or area where they need support.

*Setup:* This exercise requires strong existing trust. Ensure exercises 1-9 have been completed. Set the tone: "This is a safe space. What's shared here stays here. Our only job is to listen and support."

*Steps:*
1. Set ground rules (5 minutes):
   - No fixing, no advice (unless asked)
   - No judgment
   - Confidentiality — nothing leaves this room
   - It's OK to pass (but encouragement to try)
2. Each person shares (5-8 minutes):
   - "The thing I'm struggling with most right now is..."
   - "What I'm most afraid of is..."
   - "Where I need help from this team is..."
3. After each share, the team responds:
   - Brief acknowledgment: "Thank you for sharing that"
   - One supportive statement (optional): "I relate because..." or "I want you to know..."
4. Complete the full circle before debrief

*Time Management:* 5-8 min per person + 15 min debrief. For a team of 6: ~50-60 minutes.

*Debrief Questions:*
1. How did it feel to share at this level?
2. What did you learn about the team's capacity for support?
3. How has our trust level changed from Exercise 1 to now?
4. What do we want to commit to as a team going forward?

---

#### Step 5: Record Outcomes

After the exercise is complete, ask the user for:

1. **Key takeaways:** "What were the main insights or outcomes from this exercise?" (3-5 bullet points)
2. **Facilitation notes:** "How did the exercise go? Any observations about the process?"
3. **Debrief notes:** "How did the debrief discussion go?"
4. **Follow-up actions:** "Any action items that came out of this?" (optional)
5. **Duration:** "How long did the exercise take?"

Create a new file from `templates/trust-exercise.md` at `data/trust/YYYY-MM-DD-exercise-slug.md`. Fill in all frontmatter fields and body sections.

#### Step 6: Save

Show the complete file before writing. Ask: "Save this trust exercise record?"

After saving, display:

```
Exercise #N [Name] complete!

Progression: N/10 exercises completed
Next: #[N+1] [Name] ([vulnerability level])
Recommended timing: Next quarter (~90 days)

Trust exercises build on each other. The next exercise
will go deeper — schedule it for your next quarterly session.
```

---

### Mode: Schedule

Use when checking which exercises have been completed, what's next, and whether the team is on cadence.

#### Step 1: Load All Records

Read all files from `data/trust/` via `Glob("data/trust/*.md")`. Parse YAML frontmatter.

If no files exist: "No trust exercises recorded yet. Start with Exercise #1: Personal Histories using Facilitate mode."

#### Step 2: Build Progression Table

```
Trust Builders — Progression
━━━━━━━━━━━━━━━━━━━━━━━━━━━

| # | Exercise | Level | Status | Date | Participants |
|---|----------|-------|--------|------|-------------|
| 1 | Personal Histories | Low | ✓ Done | 2026-01-15 | Brad, Daniel |
| 2 | DISC/Kolbe Profiles | Low | ✓ Done | 2026-04-10 | Brad, Daniel |
| 3 | Lifeline Exercise | Medium | → Next | — | — |
| 4 | One Thing | Medium | Pending | — | — |
| ... | ... | ... | ... | ... | ... |
| 10 | Vulnerability Circle | High | Pending | — | — |

Progress: 2/10 exercises (20%)
██████░░░░░░░░░░░░░░░░░░ 20%
```

#### Step 3: Flag Staleness

Calculate days since most recent exercise.

- **> 120 days:** "⚠️ [N] days since last trust exercise. Recommended cadence is quarterly (~90 days). Consider scheduling the next exercise."
- **90-120 days:** "The next trust exercise is due soon — last one was [N] days ago."
- **< 90 days:** No flag.

#### Step 4: Cross-Reference Checkup Trust Score

Optionally read `data/checkups/` for the most recent organizational checkup. Look for Question 11 score (leadership trust question).

- **Score < 3.0:** "📊 Checkup Question 11 (leadership trust) scored [X]/5. The Trust Builders exercises can help improve this. Consider prioritizing the next exercise."
- **Score ≥ 3.0:** Mention the score but no urgent recommendation.

If no checkup data exists, skip this step silently.

---

### Mode: Review

Use when reviewing the history of trust exercises — dates, participants, key takeaways, and progression over time.

#### Step 1: Load All Records

Read all files from `data/trust/` via `Glob("data/trust/*.md")`. Parse YAML frontmatter.

If no files exist: "No trust exercises recorded yet. Start with Exercise #1: Personal Histories using Facilitate mode."

#### Step 2: Display History Table

Show all completed exercises chronologically:

```
Trust Builders — Exercise History
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Date | # | Exercise | Level | Duration | Participants | Key Takeaway |
|------|---|----------|-------|----------|-------------|-------------|
| 2026-01-15 | 1 | Personal Histories | Low | 35 min | Brad, Daniel | Discovered shared background in... |
| 2026-04-10 | 2 | DISC/Kolbe Profiles | Low | 50 min | Brad, Daniel | Brad is high-D, Daniel is high-I... |
```

#### Step 3: Show Progression Summary

```
Progression Summary:
  Completed: N/10 exercises
  Current cycle: 1 (exercises 1-10)
  Exercises by vulnerability level:
    Low (1-2): N completed
    Medium (3-6): N completed
    Medium-High (7-8): N completed
    High (9-10): N completed
  Avg time between exercises: [N] days
  Total time invested: [N] minutes across [N] exercises
```

#### Step 4: Show Cycle Status

If all 10 exercises are complete:

```
🎉 Cycle 1 Complete!

All 10 Trust Builder exercises have been completed.
Consider starting Cycle 2 — repeating exercises builds deeper trust.
Many teams report that exercises hit differently the second time around,
especially as the team evolves and new members join.
```

If the team has completed multiple cycles, show cycle-over-cycle comparison.

#### Step 5: Drill Down

Ask: "Want to view the full record for a specific exercise?"

If yes, read and display the complete file for the requested exercise.

## Output Format

**Facilitate:** Exercise-specific facilitation guide with purpose, setup, steps, time management, and debrief questions. Outcome record shown before save. Post-exercise summary with next exercise recommendation.

**Schedule:** Progression table showing all 10 exercises with completion status, staleness warnings, and checkup trust score cross-reference. Visual progress bar.

**Review:** Chronological history table with dates, exercises, levels, durations, and key takeaways. Progression summary by vulnerability level. Cycle status.

## Guardrails

- **Always show the complete file before writing.** Never save an exercise record without displaying it and getting approval.
- **Don't auto-invoke other skills.** When trust results suggest running a checkup or updating people evaluations, mention the option but let the user decide. Say "Would you like to run an organizational checkup?" rather than doing it automatically.
- **Sensitive data warning.** On first use in a session, remind the user: "Trust exercise records contain personal sharing and vulnerability-based feedback. This repo should be private."
- **Respect the vulnerability progression.** Do not recommend skipping ahead to high-vulnerability exercises if earlier exercises haven't been completed. If the team attempts exercise 7+ without completing 1-6, warn: "Exercises 7-10 require a foundation of trust from earlier exercises. Consider completing exercises [missing numbers] first."
- **Facilitation guide, not digital exercise.** The skill provides instructions and records outcomes — the actual exercises happen in person or in a live meeting. Don't try to simulate the exercises by asking participants to type their responses.
- **Don't pressure sharing.** The exercises involve vulnerability. If a participant wants to pass, that's acceptable. Note it in the record but don't push.
- **One exercise per session.** Each facilitation session covers one exercise. Don't try to run multiple exercises in sequence — each needs time to land emotionally.
- **Confidentiality reminder.** For exercises 7+ (medium-high and high vulnerability), remind the team: "What's shared in this exercise stays within the team."

## Integration Notes

### Accountability Chart (ceos-accountability)

- **Direction:** Read
- **What data:** `data/accountability.md` — seat names, owners, team members
- **Purpose:** Identifies leadership team members for participant suggestions during Facilitate mode. The accountability chart defines who should be in the room for trust exercises.

### Organizational Checkup (ceos-checkup)

- **Direction:** Read
- **What data:** `data/checkups/` — organizational health assessment scores
- **Purpose:** Question 11 in the checkup measures leadership team trust. Low scores (< 3.0) suggest prioritizing Trust Builder exercises. Schedule mode cross-references the most recent checkup trust score.

### Annual Planning (ceos-annual)

- **Direction:** Related
- **What data:** No direct data access
- **Purpose:** Annual planning sessions often include a review of team trust and may trigger scheduling the next Trust Builder exercise. The trust exercise progression can inform annual planning discussions about team health.

### Quarterly Planning (ceos-quarterly-planning)

- **Direction:** Related
- **What data:** No direct data access
- **Purpose:** The quarterly cadence of trust exercises aligns naturally with quarterly planning. Review trust progression as part of the quarterly planning agenda. Schedule the next exercise if overdue.

### Write Principle

**Only `ceos-trust` writes to `data/trust/`.** Other skills may reference trust exercise data for team health context, but do not modify exercise records.
