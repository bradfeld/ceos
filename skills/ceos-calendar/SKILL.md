---
name: ceos-calendar
description: Use when managing the rolling market calendar - conferences, launches, fundraising milestones, partner events, and team constraints
file-access: [data/calendar/, templates/calendar-events.md, data/vision.md, data/rocks/, data/accountability.md]
tools-used: [Read, Write, Glob]
---

# ceos-calendar

Manage the rolling 6-month market calendar — external events, partner milestones, fundraising deadlines, and team constraints that affect quarterly planning and Rocks.

## When to Use

- "Show the calendar" or "market calendar"
- "Add an event" or "add a conference to the calendar"
- "What events are coming up?" or "upcoming deadlines"
- "Update event status" or "mark that event as past"
- "Calendar for quarterly planning" or "what's happening next quarter?"
- "Any constraints this month?" or "team availability"

## Context

### Finding the CEOS Repository

Search upward from the current directory for the `.ceos` marker file. This file marks the root of the CEOS repository.

If `.ceos` is not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

**Sync before use:** Once you find the CEOS root, run `git -C <ceos_root> pull --ff-only --quiet 2>/dev/null` to get the latest data from teammates. If it fails (conflict or offline), continue silently with local data.

### Key Files

| File | Purpose |
|------|---------|
| `data/calendar/events.md` | Market calendar events (dates, types, owners, status) |
| `templates/calendar-events.md` | Template for initial calendar file |
| `data/vision.md` | Strategic context for event relevance |
| `data/rocks/QUARTER/` | Current Rocks for alignment checks |
| `data/accountability.md` | Seat owners for event-owner validation |

### Calendar Data Format

Events are stored in a single markdown table in `data/calendar/events.md`. Each row is one event:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Date | `YYYY-MM-DD` | Yes | Event date (ISO 8601) |
| Event | string | Yes | Short event name |
| Type | enum | Yes | `partner`, `market`, `fundraising`, `constraint` |
| Owner | string | Yes | Person responsible, or "Team" for constraints |
| Status | enum | Yes | `upcoming`, `past`, `cancelled` |
| Notes | string | No | Brief context or outcome |

**Type values:**
- `partner` — partner milestones, reviews, joint events
- `market` — conferences, industry events, product launches
- `fundraising` — investor meetings, round targets, pitch deadlines
- `constraint` — team-wide holidays, office closures, blackout periods

**Status values:**
- `upcoming` — event has not occurred yet
- `past` — event has passed (update notes with outcome)
- `cancelled` — event was cancelled or no longer relevant

**Sorting:** Rows are sorted chronologically by Date, oldest first.

## Process

### Mode: View Calendar

Use when the user wants to see upcoming events or review the calendar.

#### Step 1: Read Events

Read `data/calendar/events.md` and parse the events table.

#### Step 2: Calculate Rolling Window

Compute the rolling window: 3 months before today through 3 months after today. Filter events to this window.

#### Step 3: Display Calendar

Group events by month and display:

```
Market Calendar (Dec 2025 - Jun 2026)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

January 2026
  15  CES 2026 [market] — Ryan Martens (past)
      Attended; explored AI agent partnerships

March 2026
  08  GHC Registration Deadline [partner] — Dan Forman (upcoming)
  31  Seed Round Close Target [fundraising] — Ryan Martens (upcoming)

April 2026
  10  AnitaB.org Quarterly Review [partner] — Dan Forman (upcoming)
```

#### Step 4: Cross-Reference with Rocks

Read `data/rocks/[current-quarter]/` and highlight any events that relate to current Rocks. For example, if a Rock is "Raise \$2.5M Seed Round" and there's a fundraising event, note the connection.

---

### Mode: Add Events

Use when creating new calendar events.

#### Step 1: Collect Event Details

For each event, collect:

1. **Date** — when does it happen? (must be `YYYY-MM-DD`)
2. **Event name** — short, descriptive title
3. **Type** — one of: `partner`, `market`, `fundraising`, `constraint`
4. **Owner** — who is responsible? (use "Team" for constraints)
5. **Notes** — optional context

#### Step 2: Validate

- Date is valid ISO 8601 format
- Type is one of the 4 allowed values
- Owner exists in `data/accountability.md` (or is "Team" for constraints)

#### Step 3: Insert in Chronological Order

Read the existing events table. Insert the new row at the correct chronological position.

#### Step 4: Show Diff and Write

Show the user the updated table with the new row highlighted. Ask: "Add this event?"

If approved, write `data/calendar/events.md`.

#### Step 5: Continue or Finish

Ask: "Add another event, or are we done?"

When finished, display a summary of events added this session.

---

### Mode: Update Events

Use when changing event status, editing details, or removing events.

#### Step 1: Display Events

Show all events (not just the rolling window) so the user can find what they want to update.

#### Step 2: Collect Changes

Common updates:
- **Status change** — mark as `past` (add outcome to notes) or `cancelled`
- **Date change** — event was rescheduled
- **Notes update** — add context or outcome

#### Step 3: Show Diff and Write

Show the specific row changes. Ask: "Update this event?"

If approved, write `data/calendar/events.md`.

## Output Format

**View:** Calendar grouped by month with type tags and status indicators. Past events dimmed. Upcoming events within 2 weeks highlighted. Rock cross-references noted.
**Add:** Show the new row in context. End with a summary of events added.
**Update:** Show the diff of changed fields. Confirm before writing.

## Guardrails

- **Always show diff before writing.** Never modify `data/calendar/events.md` without showing the change and getting approval.
- **Valid types only.** Only accept `partner`, `market`, `fundraising`, `constraint`. If the user provides another type, show the allowed values and ask which fits.
- **One owner per event.** Use "Team" for constraints that affect everyone.
- **Dates must be ISO 8601.** If the user says "next Tuesday" or "March 8th", convert to `YYYY-MM-DD` format and confirm.
- **Maintain chronological order.** When inserting or reordering, keep rows sorted by Date.
- **Don't auto-invoke other skills.** Mention `ceos-rocks` and `ceos-quarterly-planning` when relevant, but let the user decide when to switch.
- **Sensitive data warning.** On first use, remind the user: "Calendar events may contain sensitive business information. Use a private repo."

## Integration Notes

### Rocks (ceos-rocks)

- **Read:** Calendar events provide market context for setting Rocks. During Rock-setting, suggest reviewing the calendar for deadlines that affect priorities.
- **Suggested flow:** "Review the market calendar with `ceos-calendar` before finalizing Rocks."

### Quarterly Planning (ceos-quarterly-planning)

- **Read:** Calendar events should be reviewed during quarterly planning. Upcoming conferences, deadlines, and constraints inform quarterly priorities.
- **Suggested flow:** "Check the market calendar for Q2 events that may affect planning."

### L10 Meetings (ceos-l10)

- **Read:** Upcoming events within 2 weeks can surface as Headlines in the L10 meeting.
- **Suggested flow:** "There are 2 events in the next 2 weeks — mention them in Headlines?"

### Annual Planning (ceos-annual)

- **Read:** Year-ahead events inform 1-Year Plan goals and major milestones.

### Accountability Chart (ceos-accountability)

- **Read:** `ceos-calendar` reads `data/accountability.md` to validate that event owners match seat responsibilities.

### Write Principle

Only `ceos-calendar` writes to `data/calendar/events.md`. Other skills read calendar data for reference.
