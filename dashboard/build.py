#!/usr/bin/env python3
"""Build the EOS Leadership Dashboard.

Reads data files from data/ and writes a self-contained HTML file to docs/index.html.
Run locally or via GitHub Actions on every push.
"""

import base64
import glob
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
DOCS_DIR = os.path.join(ROOT, "docs")


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Split simple YAML frontmatter from markdown body. Returns (dict, body_str).

    Handles scalar-only frontmatter (string, unquoted values, dates).
    No external dependencies required.
    """
    if not text.startswith("---"):
        return {}, text
    try:
        end = text.index("---", 3)
    except ValueError:
        return {}, text

    fm = {}
    for line in text[3:end].splitlines():
        m = re.match(r'^(\w+):\s*"?([^"]*)"?\s*$', line.strip())
        if m:
            fm[m.group(1)] = m.group(2).strip()

    body = text[end + 3:].strip()
    return fm, body


def parse_milestones(body):
    """Return list of {done, text} dicts from markdown checkbox lines."""
    milestones = []
    for line in body.splitlines():
        m = re.match(r"\s*-\s+\[( |x|X)\]\s+(.+)", line)
        if m:
            milestones.append({
                "done": m.group(1).strip().lower() == "x",
                "text": m.group(2).strip(),
            })
    return milestones


def load_rocks(quarter="2026-Q1"):
    """Load all rocks from data/rocks/<quarter>/*.md."""
    rocks = []
    pattern = os.path.join(DATA_DIR, "rocks", quarter, "*.md")
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        fm, body = parse_frontmatter(text)
        outcome_m = re.search(r"^>\s*(.+)", body, re.MULTILINE)
        rocks.append({
            "id":         fm.get("id", os.path.basename(path)),
            "title":      fm.get("title", ""),
            "owner":      fm.get("owner", ""),
            "quarter":    fm.get("quarter", quarter),
            "status":     fm.get("status", "on_track"),
            "created":    str(fm.get("created", "")),
            "due":        str(fm.get("due", "")),
            "outcome":    outcome_m.group(1).strip() if outcome_m else "",
            "milestones": parse_milestones(body),
            "file":       os.path.relpath(path, ROOT).replace(os.sep, "/"),
        })
    return rocks


def _next_quarter(q):
    """Given '2026-Q1', return '2026-Q2'. Wraps Q4 -> next year Q1."""
    year, qn = q.split("-Q")
    n = int(qn)
    return f"{year}-Q{n+1}" if n < 4 else f"{int(year)+1}-Q1"


def _prev_quarter(q):
    """Given '2026-Q2', return '2026-Q1'. Wraps Q1 -> prev year Q4."""
    year, qn = q.split("-Q")
    n = int(qn)
    return f"{year}-Q{n-1}" if n > 1 else f"{int(year)-1}-Q4"


def load_all_rocks():
    """Load rocks from all quarter directories.

    Returns {quarters: [...], all_quarters: [...], rocks_by_quarter: {...}, current_quarter: "..."}.
    quarters is limited to 6: 1 past + current + 4 future.
    all_quarters is every quarter folder found on disk.
    """
    rocks_dir = os.path.join(DATA_DIR, "rocks")
    all_quarters = []
    if os.path.isdir(rocks_dir):
        for name in sorted(os.listdir(rocks_dir)):
            if re.match(r"\d{4}-Q[1-4]$", name) and os.path.isdir(os.path.join(rocks_dir, name)):
                all_quarters.append(name)

    # Determine current quarter from today's date
    now = datetime.now()
    q = (now.month - 1) // 3 + 1
    current_quarter = f"{now.year}-Q{q}"

    # If current quarter has no folder yet, still include it
    if current_quarter not in all_quarters:
        all_quarters.append(current_quarter)
        all_quarters.sort()

    # Build the visible window: 1 past + current + 4 future
    prev_q = _prev_quarter(current_quarter)
    future_qs = []
    fq = current_quarter
    for _ in range(4):
        fq = _next_quarter(fq)
        future_qs.append(fq)

    window = [prev_q, current_quarter] + future_qs
    # Only include quarters that exist on disk OR are in the window
    quarters = sorted(set(all_quarters) | set(window))
    # Now trim to just the window
    quarters = [q for q in quarters if q in window]

    rocks_by_quarter = {}
    for qtr in quarters:
        rocks_by_quarter[qtr] = load_rocks(qtr)

    return {
        "quarters": quarters,
        "all_quarters": all_quarters,
        "rocks_by_quarter": rocks_by_quarter,
        "current_quarter": current_quarter,
    }


def load_scorecard():
    """Parse the metrics table from data/scorecard/metrics.md."""
    path = os.path.join(DATA_DIR, "scorecard", "metrics.md")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        text = f.read()

    metrics = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"\|\s*Metric\s*\|", stripped, re.IGNORECASE):
            in_table = True
            continue
        if in_table and re.match(r"\|[-| ]+\|", stripped):
            continue  # separator row
        if in_table and stripped.startswith("|"):
            cols = [c.strip() for c in stripped.split("|")[1:-1]]
            if len(cols) >= 6 and cols[0]:
                metrics.append({
                    "metric":    cols[0],
                    "owner":     cols[1],
                    "goal":      cols[2],
                    "frequency": cols[3],
                    "green":     cols[4],
                    "red":       cols[5],
                })
        elif in_table and stripped and not stripped.startswith("|"):
            in_table = False
    return metrics


def load_accountability():
    """Parse seat sections from data/accountability.md."""
    path = os.path.join(DATA_DIR, "accountability.md")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        text = f.read()

    SKIP_HEADINGS = {"Your Company", "How to Use This Chart"}
    seats = []

    # Split on level-2 headings; result: [pre, h1, body1, h2, body2, ...]
    parts = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip()
        body = parts[i + 1]
        i += 2

        if heading in SKIP_HEADINGS:
            continue

        owner_match = re.search(r"\*\*Owner:\*\*\s*(.+)", body)
        if not owner_match:
            continue
        owner = owner_match.group(1).strip()

        roles = []
        for row in re.finditer(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|", body, re.MULTILINE):
            roles.append({
                "num":  int(row.group(1)),
                "role": row.group(2).strip(),
            })

        seats.append({"seat": heading, "owner": owner, "roles": roles})

    return seats


def load_vision():
    """Parse data/vision.md into structured sections for the Strategic Planning tab."""
    path = os.path.join(DATA_DIR, "vision.md")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Split on level-2 headings
    parts = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
    sections = {}
    i = 1
    while i < len(parts) - 1:
        sections[parts[i].strip()] = parts[i + 1].strip()
        i += 2

    result = {}

    # Core Values
    cv_text = sections.get("Core Values", "")
    core_values = []
    for line in cv_text.splitlines():
        m = re.match(r"\d+\.\s+\*\*(.+?)\*\*\s*[—–\-]+\s*(.+)", line.strip())
        if m:
            core_values.append({"name": m.group(1).strip(), "desc": m.group(2).strip()})
    result["core_values"] = core_values

    # Core Focus
    cf_text = sections.get("Core Focus", "")
    blockquotes = re.findall(r"^>\s*(.+)", cf_text, re.MULTILINE)
    result["core_focus"] = {
        "purpose": blockquotes[0] if blockquotes else "",
        "niche":   blockquotes[1] if len(blockquotes) > 1 else "",
    }

    # 10-Year Target
    tyt_text = sections.get("10-Year Target", "")
    tyt_m = re.search(r"^>\s*(.+)", tyt_text, re.MULTILINE)
    result["ten_year_target"] = tyt_m.group(1).strip() if tyt_m else ""

    # 3-Year Picture
    typp_text = sections.get("3-Year Picture", "")
    three_year_items = []
    for line in typp_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        content = stripped[1:].strip()
        m_labeled = re.match(r"\*\*(.+?):\*\*\s*(.*)", content)
        m_header  = re.match(r"\*\*(.+?)\??\*\*\s*$", content)
        if m_labeled:
            three_year_items.append({"type": "labeled", "label": m_labeled.group(1), "value": m_labeled.group(2)})
        elif m_header:
            three_year_items.append({"type": "header",  "label": m_header.group(1),  "value": ""})
        elif content and not re.match(r"^-+$", content):
            three_year_items.append({"type": "bullet",  "label": "",                 "value": content})
    result["three_year_picture"] = three_year_items

    # 1-Year Plan
    oyp_text = sections.get("1-Year Plan", "")
    one_year_items = []
    for line in oyp_text.splitlines():
        stripped = line.strip()
        m_labeled = re.match(r"-\s+\*\*(.+?):\*\*\s*(.*)", stripped)
        m_goal    = re.match(r"(\d+)\.\s+(.+)", stripped)
        if m_labeled:
            one_year_items.append({"type": "labeled", "label": m_labeled.group(1), "value": m_labeled.group(2)})
        elif m_goal:
            one_year_items.append({"type": "goal",    "label": f"Goal {m_goal.group(1)}", "value": m_goal.group(2).strip()})
    result["one_year_plan"] = one_year_items

    # Marketing Strategy
    ms_text = sections.get("Marketing Strategy", "")
    all_bq = re.findall(r"^>\s*(.+)", ms_text, re.MULTILINE)
    target_market = all_bq[0] if all_bq else ""
    guarantee     = all_bq[-1] if len(all_bq) > 1 else ""

    uniques, process_steps = [], []
    in_uniques = in_process = False
    for line in ms_text.splitlines():
        s = line.strip()
        if "3 Uniques" in s:
            in_uniques, in_process = True, False
            continue
        if "Proven Process" in s:
            in_uniques, in_process = False, True
            continue
        if s.startswith("**Guarantee"):
            in_uniques = in_process = False
        if in_uniques:
            m = re.match(r"\d+\.\s+\*\*(.+?):\*\*\s*(.+)", s)
            if m:
                uniques.append({"name": m.group(1).strip(), "desc": m.group(2).strip()})
        if in_process:
            m = re.match(r"\d+\.\s+\*\*(.+?)\*\*\s*[—–\-]+\s*(.+)", s)
            if m:
                process_steps.append({"step": m.group(1).strip(), "desc": m.group(2).strip()})

    result["marketing"] = {
        "target_market": target_market,
        "uniques":       uniques,
        "process":       process_steps,
        "guarantee":     guarantee,
    }

    return result


def load_l10():
    """Parse the L10 standing agenda into structured sections."""
    path = os.path.join(DATA_DIR, "meetings", "l10", "agenda.md")
    if not os.path.exists(path):
        return {"schedule": "", "attendees": [], "sections": []}
    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Meeting meta from header block
    schedule = ""
    attendees = []
    for line in text.splitlines()[:6]:
        line = line.strip("* ")
        if "Tuesday" in line or "minutes" in line.lower():
            schedule = line.strip()
        m = re.match(r"\*?\*?Attendees:\*?\*?\s*(.+)", line)
        if m:
            attendees = [a.strip() for a in m.group(1).split(",")]

    # Split on numbered section headings: ## N. Title (X min)
    parts = re.split(r"^## (\d+)\.\s+(.+?)\s+\((\d+)\s+min\)", text, flags=re.MULTILINE)
    # parts: [preamble, num, title, minutes, body, num, title, minutes, body, ...]
    sections = []
    i = 1
    while i <= len(parts) - 4:
        body = parts[i + 3].strip()
        # Extract italic description (first *...* block)
        desc_match = re.search(r"\*([^*]+)\*", body)
        desc = desc_match.group(1).strip() if desc_match else ""
        sections.append({
            "num":     int(parts[i]),
            "title":   parts[i + 1].strip(),
            "minutes": int(parts[i + 2]),
            "desc":    desc,
        })
        i += 4

    return {"schedule": schedule, "attendees": attendees, "sections": sections}


def load_team():
    """Load team members from data/people/team.json (if exists)."""
    path = os.path.join(DATA_DIR, "people", "team.json")
    color_map = {
        "blue":   ("bg-blue-100",   "text-blue-800"),
        "purple": ("bg-purple-100", "text-purple-800"),
        "green":  ("bg-green-100",  "text-green-800"),
        "orange": ("bg-orange-100", "text-orange-800"),
        "pink":   ("bg-pink-100",   "text-pink-800"),
        "red":    ("bg-red-100",    "text-red-800"),
        "yellow": ("bg-yellow-100", "text-yellow-800"),
        "indigo": ("bg-indigo-100", "text-indigo-800"),
        "teal":   ("bg-teal-100",   "text-teal-800"),
        "cyan":   ("bg-cyan-100",   "text-cyan-800"),
    }
    default_team = [
        {"name": "Team Member 1", "color": "blue"},
        {"name": "Team Member 2", "color": "purple"},
        {"name": "Team Member 3", "color": "green"},
    ]
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        members = data.get("team", default_team)
    else:
        members = default_team

    names = [m["name"] for m in members]
    owner_cls = {}
    for m in members:
        bg, txt = color_map.get(m.get("color", "gray"), ("bg-gray-100", "text-gray-700"))
        owner_cls[m["name"]] = f"{bg} {txt}"
    return names, owner_cls


def load_calendar():
    """Parse the events table from data/calendar/events.md."""
    path = os.path.join(DATA_DIR, "calendar", "events.md")
    if not os.path.exists(path):
        return []

    with open(path, encoding="utf-8") as f:
        text = f.read()

    events = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"\|\s*Date\s*\|", stripped, re.IGNORECASE):
            in_table = True
            continue
        if in_table and re.match(r"\|[-| ]+\|", stripped):
            continue  # separator row
        if in_table and stripped.startswith("|"):
            cols = [c.strip() for c in stripped.split("|")[1:-1]]
            if len(cols) >= 5 and cols[0]:
                events.append({
                    "date":   cols[0],
                    "event":  cols[1],
                    "type":   cols[2],
                    "owner":  cols[3],
                    "status": cols[4],
                    "notes":  cols[5] if len(cols) > 5 else "",
                })
        elif in_table and stripped and not stripped.startswith("|"):
            in_table = False
    return events


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Company &middot; EOS Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen font-sans">

<!-- ── Header ── -->
<header class="bg-white border-b border-gray-200 shadow-sm">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-gray-900">Your Company</h1>
      <p class="text-sm text-gray-500">EOS Leadership Dashboard &middot; __QUARTER__</p>
    </div>
    <div class="flex items-center gap-3">
      <div class="text-right">
        <div class="text-sm font-semibold text-gray-700">Week __WEEK__</div>
        <div class="text-xs text-gray-400">Updated __UPDATED__</div>
      </div>
      <button onclick="openSettings()" title="Settings" class="p-2 rounded-lg hover:bg-gray-100 transition-colors">
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
      </button>
    </div>
  </div>
</header>

<!-- ── Main ── -->
<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 mt-6 pb-16">

  <!-- Tab bar -->
  <div class="flex space-x-1 bg-white border border-gray-200 rounded-lg p-1 mb-6 w-fit">
    <button onclick="showTab('rocks')"               id="tab-rocks"               class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">Rocks</button>
    <button onclick="showTab('scorecard')"           id="tab-scorecard"           class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">Scorecard</button>
    <button onclick="showTab('accountability')"      id="tab-accountability"      class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">Accountability Chart</button>
    <button onclick="showTab('l10')"                 id="tab-l10"                 class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">L10 Agenda</button>
    <button onclick="showTab('strategic-planning')"  id="tab-strategic-planning"  class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">Strategic Planning</button>
    <button onclick="showTab('calendar')"            id="tab-calendar"            class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">Market Calendar</button>
  </div>

  <div id="panel-rocks"></div>
  <div id="panel-scorecard"></div>
  <div id="panel-accountability"></div>
  <div id="panel-l10"></div>
  <div id="panel-strategic-planning"></div>
  <div id="panel-calendar"></div>
</div>

<!-- ── Settings Modal ── -->
<div id="settings-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center">
  <div class="absolute inset-0 bg-black/40" onclick="closeSettings()"></div>
  <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 max-h-[80vh] flex flex-col">
    <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-900">Settings</h2>
      <button onclick="closeSettings()" class="p-1 rounded-lg hover:bg-gray-100">
        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>
    <div class="px-6 py-4 overflow-y-auto flex-1">
      <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Team Members</h3>
      <div id="people-list" class="space-y-2 mb-4"></div>
      <div class="flex gap-2">
        <input id="new-person-name" type="text" placeholder="New team member name"
               class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
               onkeydown="if(event.key==='Enter')addPerson()"/>
        <button onclick="addPerson()" class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
          Add
        </button>
      </div>
    </div>
    <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
      <button onclick="closeSettings()" class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">Cancel</button>
      <button onclick="saveSettings()" id="save-settings-btn" class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">Save</button>
    </div>
  </div>
</div>

<script>
/* ── Data ── */
window.DASHBOARD_DATA = __DATA_JSON__;
window.GITHUB_TOKEN = '__GITHUB_TOKEN__';
window.GITHUB_REPO  = '__GITHUB_REPO__';

/* ── Owner chip colors (literal strings so Tailwind CDN scans them) ── */
/* bg-blue-100 text-blue-800 bg-purple-100 text-purple-800 bg-green-100 text-green-800 bg-orange-100 text-orange-800 bg-pink-100 text-pink-800 bg-red-100 text-red-800 bg-yellow-100 text-yellow-800 bg-indigo-100 text-indigo-800 bg-teal-100 text-teal-800 bg-cyan-100 text-cyan-800 */
const OWNER_CLS = __OWNER_CLS_JSON__;

/* ── Seat top-border colors (hex, applied via inline style) ── */
const SEAT_COLOR = {
  'Visionary':       '#6366f1',
  'Integrator':      '#a855f7',
  'Sales/Marketing': '#22c55e',
  'Operations':      '#3b82f6',
  'Finance':         '#f97316',
};

/* ── Base64 helpers (avoid deprecated escape/unescape) ── */
function b64encode(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = '';
  bytes.forEach(b => bin += String.fromCharCode(b));
  return btoa(bin);
}
function b64decode(b64) {
  const bin = atob(b64.replace(/\n/g, ''));
  return new TextDecoder().decode(Uint8Array.from(bin, c => c.charCodeAt(0)));
}

/* ── Helpers ── */
function ownerChip(owner) {
  const cls = OWNER_CLS[owner] || 'bg-gray-100 text-gray-700';
  return `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${cls}">${owner}</span>`;
}

function showTab(name) {
  ['rocks', 'scorecard', 'accountability', 'l10', 'strategic-planning', 'calendar'].forEach(t => {
    document.getElementById('panel-' + t).classList.toggle('hidden', t !== name);
    const btn = document.getElementById('tab-' + t);
    if (t === name) {
      btn.classList.add('bg-blue-600', 'text-white');
      btn.classList.remove('text-gray-600', 'hover:bg-gray-100');
    } else {
      btn.classList.remove('bg-blue-600', 'text-white');
      btn.classList.add('text-gray-600', 'hover:bg-gray-100');
    }
  });
}

/* ── Rocks ── */
let ROCK_EDITING = null; // null = view all | 'new' = add form | integer = edit that index
let ACTIVE_QUARTER = window.DASHBOARD_DATA.current_quarter;
let CLOSE_QUARTER_MODE = false;  // false = normal | true = step-by-step scoring
let CLOSE_QUARTER_STEP = 0;     // index into rocks being scored
let CLOSE_QUARTER_SCORES = {};  // {rockIdx: 'complete'|'dropped'}
let CLOSE_QUARTER_CARRY = {};   // {rockIdx: true|false} - carry forward dropped rocks

let TEAM_MEMBERS = __TEAM_MEMBERS_JSON__;

/* ── Color palette for owner chips ── */
const COLOR_PALETTE = [
  { bg: 'bg-blue-100',   text: 'text-blue-800',   label: 'Blue' },
  { bg: 'bg-purple-100', text: 'text-purple-800', label: 'Purple' },
  { bg: 'bg-green-100',  text: 'text-green-800',  label: 'Green' },
  { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Orange' },
  { bg: 'bg-pink-100',   text: 'text-pink-800',   label: 'Pink' },
  { bg: 'bg-red-100',    text: 'text-red-800',    label: 'Red' },
  { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Yellow' },
  { bg: 'bg-indigo-100', text: 'text-indigo-800', label: 'Indigo' },
  { bg: 'bg-teal-100',   text: 'text-teal-800',   label: 'Teal' },
  { bg: 'bg-cyan-100',   text: 'text-cyan-800',   label: 'Cyan' },
];

let settingsPeople = []; // working copy for the modal

function openSettings() {
  settingsPeople = TEAM_MEMBERS.map(name => {
    const cls = OWNER_CLS[name] || 'bg-gray-100 text-gray-700';
    const match = COLOR_PALETTE.find(c => cls.includes(c.bg)) || COLOR_PALETTE[0];
    return { name, colorIdx: COLOR_PALETTE.indexOf(match) };
  });
  renderPeopleList();
  document.getElementById('settings-modal').classList.remove('hidden');
}

function closeSettings() {
  document.getElementById('settings-modal').classList.add('hidden');
}

function renderPeopleList() {
  const el = document.getElementById('people-list');
  if (!settingsPeople.length) {
    el.innerHTML = '<p class="text-sm text-gray-400 italic">No team members yet.</p>';
    return;
  }
  el.innerHTML = settingsPeople.map((p, i) => {
    const c = COLOR_PALETTE[p.colorIdx];
    const colorOpts = COLOR_PALETTE.map((co, ci) =>
      `<option value="${ci}" ${ci === p.colorIdx ? 'selected' : ''}>${co.label}</option>`
    ).join('');
    return `
      <div class="flex items-center gap-2 p-2 bg-gray-50 rounded-lg group">
        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${c.bg} ${c.text}">${esc(p.name)}</span>
        <select onchange="settingsPeople[${i}].colorIdx=+this.value; renderPeopleList()"
                class="ml-auto text-xs border border-gray-200 rounded px-2 py-1 bg-white">
          ${colorOpts}
        </select>
        <button onclick="settingsPeople.splice(${i},1); renderPeopleList()"
                class="p-1 rounded hover:bg-red-100 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Remove">
          <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>`;
  }).join('');
}

function addPerson() {
  const input = document.getElementById('new-person-name');
  const name = input.value.trim();
  if (!name) return;
  if (settingsPeople.some(p => p.name.toLowerCase() === name.toLowerCase())) {
    alert('This person is already on the team.');
    return;
  }
  const nextColor = settingsPeople.length % COLOR_PALETTE.length;
  settingsPeople.push({ name, colorIdx: nextColor });
  input.value = '';
  renderPeopleList();
}

async function saveSettings() {
  const btn = document.getElementById('save-settings-btn');
  btn.textContent = 'Saving…';
  btn.disabled = true;

  // Update in-memory state
  TEAM_MEMBERS = settingsPeople.map(p => p.name);
  const newOwnerCls = {};
  settingsPeople.forEach(p => {
    const c = COLOR_PALETTE[p.colorIdx];
    newOwnerCls[p.name] = `${c.bg} ${c.text}`;
  });
  Object.keys(OWNER_CLS).forEach(k => delete OWNER_CLS[k]);
  Object.assign(OWNER_CLS, newOwnerCls);

  // Persist to GitHub as data/people/team.json
  const token = window.GITHUB_TOKEN;
  const repo  = window.GITHUB_REPO;
  const path  = 'data/people/team.json';
  const payload = JSON.stringify({ team: settingsPeople.map(p => ({
    name: p.name,
    color: COLOR_PALETTE[p.colorIdx].label.toLowerCase()
  })) }, null, 2);

  try {
    // Check if file exists to get its SHA
    let sha = null;
    const check = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (check.ok) {
      const existing = await check.json();
      sha = existing.sha;
    }

    const body = { message: 'update team members', content: b64encode(payload) };
    if (sha) body.sha = sha;

    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`GitHub API error: ${res.status}`);

    // Re-render all panels
    renderRocks();
    renderScorecard();
    renderAccountability();
    closeSettings();
  } catch (e) {
    alert('Failed to save: ' + e.message);
  } finally {
    btn.textContent = 'Save';
    btn.disabled = false;
  }
}

function updateRockProgress(ri) {
  const rock = window.DASHBOARD_DATA.rocks[ri];
  const total = rock.milestones.length;
  const done  = rock.milestones.filter(m => m.done).length;
  const pct   = total ? Math.round(done / total * 100) : 0;
  const bar = document.getElementById('pb_' + ri);
  const ctr = document.getElementById('pc_' + ri);
  if (bar) bar.style.width = pct + '%';
  if (ctr) ctr.textContent = done + '/' + total;
}

async function toggleMilestone(ri, mi) {
  const rock      = window.DASHBOARD_DATA.rocks[ri];
  const milestone = rock.milestones[mi];
  const token     = window.GITHUB_TOKEN;
  const repo      = window.GITHUB_REPO;
  const checkbox  = document.getElementById('m_' + ri + '_' + mi);
  const label     = document.getElementById('ml_' + ri + '_' + mi);

  checkbox.disabled = true;
  const newDone = !milestone.done;

  try {
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (!res.ok) throw new Error('Could not read rock file');
    const data    = await res.json();
    const sha     = data.sha;
    const current = b64decode(data.content);

    const oldMark = milestone.done ? '[x]' : '[ ]';
    const newMark = milestone.done ? '[ ]' : '[x]';
    const updated = current.replace(`- ${oldMark} ${milestone.text}`, `- ${newMark} ${milestone.text}`);
    if (updated === current) throw new Error('Milestone not found in file');

    const put = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({
        message: `${newDone ? 'complete' : 'reopen'} milestone: ${milestone.text}`,
        content: b64encode(updated),
        sha
      })
    });
    if (!put.ok) throw new Error((await put.json()).message);

    milestone.done = newDone;
    label.className = newDone
      ? 'text-xs text-gray-400 line-through cursor-pointer select-none'
      : 'text-xs text-gray-600 cursor-pointer select-none leading-snug';
    updateRockProgress(ri);
  } catch(e) {
    checkbox.checked = milestone.done;
    alert('Failed to save: ' + e.message);
  } finally {
    checkbox.disabled = false;
  }
}

function buildRockViewCard(rock, ri) {
  const statusBadges = {
    'on_track':  '<span class="shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">On Track</span>',
    'off_track': '<span class="shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">Off Track</span>',
    'complete':  '<span class="shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">\u2713 Complete</span>',
    'dropped':   '<span class="shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500">\u2717 Dropped</span>',
    'draft':     '<span class="shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">Draft</span>',
  };
  const badge = statusBadges[rock.status] || statusBadges['on_track'];
  const isClosed = rock.status === 'complete' || rock.status === 'dropped';
  const isDraft = rock.status === 'draft';
  const total = rock.milestones.length;
  const done  = rock.milestones.filter(m => m.done).length;
  const pct   = total ? Math.round(done / total * 100) : 0;

  let milestoneList = `<ul class="mt-3 space-y-1.5">`;
  rock.milestones.forEach((m, mi) => {
    milestoneList += `
      <li class="flex items-start gap-2">
        <input type="checkbox" id="m_${ri}_${mi}" ${m.done ? 'checked' : ''}
          onchange="toggleMilestone(${ri}, ${mi})"
          class="mt-0.5 w-3.5 h-3.5 shrink-0 rounded border-gray-300 text-blue-600 cursor-pointer focus:ring-blue-500 focus:ring-1">
        <label id="ml_${ri}_${mi}" for="m_${ri}_${mi}"
          class="${m.done ? 'text-xs text-gray-400 line-through' : 'text-xs text-gray-600 leading-snug'} cursor-pointer select-none">${esc(m.text)}</label>
      </li>`;
  });
  milestoneList += `</ul>`;

  return `<div class="bg-white rounded-lg ${isDraft ? 'border-2 border-dashed border-amber-300' : 'border border-gray-200'} shadow-sm p-4 ${isClosed ? 'opacity-50' : ''}">
    <div class="flex items-start justify-between gap-2 mb-1">
      <h3 class="text-sm font-semibold ${isDraft ? 'text-amber-800' : 'text-gray-900'} leading-snug ${isClosed ? 'line-through' : ''}">${esc(rock.title)}</h3>
      <div class="flex items-center gap-1 shrink-0">
        ${badge}
        <button onclick="ROCK_EDITING=${ri};renderRocks();"
          class="ml-1 text-gray-400 hover:text-gray-600 text-xs px-1.5 py-0.5 rounded hover:bg-gray-100 transition-colors"
          title="Edit rock">\u270E</button>
      </div>
    </div>
    ${rock.outcome ? `<p class="text-xs text-gray-500 italic mb-2">${esc(rock.outcome)}</p>` : ''}
    <p class="text-xs text-gray-400 mb-3">Due ${esc(rock.due)}</p>
    <div class="flex justify-between text-xs text-gray-400 mb-1">
      <span>Milestones</span><span id="pc_${ri}">${done}/${total}</span>
    </div>
    <div class="w-full bg-gray-100 rounded-full h-1.5 mb-3">
      <div id="pb_${ri}" class="bg-blue-500 h-1.5 rounded-full transition-all" style="width:${pct}%"></div>
    </div>
    ${milestoneList}
  </div>`;
}

function buildRockEditCard(rock, ri) {
  const isNew   = rock === null;
  const title   = isNew ? '' : rock.title;
  const owner   = isNew ? '' : rock.owner;
  const status  = isNew ? 'on_track' : rock.status;
  const due     = isNew ? '' : rock.due;
  const outcome = isNew ? '' : (rock.outcome || '');
  const msText  = isNew ? '' : rock.milestones.map(m => m.text).join('\n');

  const pfx = isNew ? 'rock_new' : `rock_edit_${ri}`;
  const ownerOpts = TEAM_MEMBERS.map(n =>
    `<option value="${n}" ${n === owner ? 'selected' : ''}>${n}</option>`).join('');

  const saveFn   = isNew ? `createRock()` : `saveRock(${ri})`;
  const cancelFn = `ROCK_EDITING=null;renderRocks();`;

  return `<div class="bg-white rounded-lg border-2 border-blue-300 shadow-sm p-4 space-y-3">
    <div class="flex items-center justify-between gap-2 flex-wrap">
      <span class="text-xs font-semibold text-gray-400 uppercase tracking-widest">${isNew ? 'New Rock' : 'Edit Rock'}</span>
      <div class="flex gap-1.5">
        <button onclick="${saveFn}" id="${pfx}_btn"
          class="bg-blue-600 text-white rounded-lg px-3 py-1 text-xs font-medium hover:bg-blue-700 transition-colors">
          ${isNew ? 'Create' : 'Save'}
        </button>
        <button onclick="${cancelFn}"
          class="bg-white border border-gray-200 text-gray-600 rounded-lg px-3 py-1 text-xs font-medium hover:bg-gray-50 transition-colors">
          Cancel
        </button>
        ${!isNew ? `<button onclick="deleteRock(${ri})"
          class="bg-white border border-red-200 text-red-500 rounded-lg px-3 py-1 text-xs font-medium hover:bg-red-50 transition-colors">
          Delete
        </button>` : ''}
      </div>
    </div>
    <div>
      <label class="text-xs font-medium text-gray-500 block mb-1">Title</label>
      <input type="text" id="${pfx}_title" value="${esc(title)}" placeholder="Rock title"
        class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
    </div>
    <div class="grid grid-cols-2 gap-2">
      <div>
        <label class="text-xs font-medium text-gray-500 block mb-1">Owner</label>
        <select id="${pfx}_owner"
          class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">— select —</option>${ownerOpts}
        </select>
      </div>
      <div>
        <label class="text-xs font-medium text-gray-500 block mb-1">Status</label>
        <select id="${pfx}_status"
          class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="draft"     ${status === 'draft'     ? 'selected' : ''}>Draft</option>
          <option value="on_track"  ${status === 'on_track'  ? 'selected' : ''}>On Track</option>
          <option value="off_track" ${status === 'off_track' ? 'selected' : ''}>Off Track</option>
          <option value="complete"  ${status === 'complete'  ? 'selected' : ''}>Complete</option>
          <option value="dropped"   ${status === 'dropped'   ? 'selected' : ''}>Dropped</option>
        </select>
      </div>
    </div>
    <div>
      <label class="text-xs font-medium text-gray-500 block mb-1">Due Date</label>
      <input type="date" id="${pfx}_due" value="${esc(due)}"
        class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
    </div>
    <div>
      <label class="text-xs font-medium text-gray-500 block mb-1">Measurable Outcome</label>
      <textarea id="${pfx}_outcome" rows="2" placeholder="Specific, measurable definition of done"
        class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y">${esc(outcome)}</textarea>
    </div>
    <div>
      <label class="text-xs font-medium text-gray-500 block mb-1">Milestones (one per line)</label>
      <textarea id="${pfx}_milestones" rows="4" placeholder="Milestone 1&#10;Milestone 2"
        class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y">${esc(msText)}</textarea>
    </div>
    <span id="${pfx}_status_msg" class="text-sm hidden"></span>
  </div>`;
}

function buildRockMarkdown(title, owner, quarter, status, due, created, id, outcome, milestones) {
  let md = `---\nid: ${id}\ntitle: "${title}"\nowner: "${owner}"\nquarter: "${quarter}"\nstatus: ${status}\ncreated: "${created}"\ndue: "${due}"\n---\n\n`;
  md += `# ${title}\n\n## Measurable Outcome\n\n> ${outcome || '[Define the measurable outcome for this Rock]'}\n\n## Milestones\n\n`;
  milestones.forEach(m => { md += `- ${m.done ? '[x]' : '[ ]'} ${m.text}\n`; });
  return md;
}

async function saveRock(ri) {
  const rock     = window.DASHBOARD_DATA.rocks[ri];
  const token    = window.GITHUB_TOKEN;
  const repo     = window.GITHUB_REPO;
  const pfx      = `rock_edit_${ri}`;
  const btn      = document.getElementById(`${pfx}_btn`);
  const statusEl = document.getElementById(`${pfx}_status_msg`);

  const title   = document.getElementById(`${pfx}_title`)?.value.trim()   || '';
  const owner   = document.getElementById(`${pfx}_owner`)?.value          || '';
  const status  = document.getElementById(`${pfx}_status`)?.value         || 'on_track';
  const due     = document.getElementById(`${pfx}_due`)?.value            || '';
  const outcome = document.getElementById(`${pfx}_outcome`)?.value.trim() || '';
  const msLines = (document.getElementById(`${pfx}_milestones`)?.value || '')
    .split('\n').map(l => l.trim()).filter(Boolean);

  if (!title) { alert('Title is required.'); return; }

  const newMilestones = msLines.map(text => {
    const existing = rock.milestones.find(m => m.text === text);
    return { done: existing ? existing.done : false, text };
  });

  btn.disabled = true; btn.textContent = 'Saving\u2026';
  statusEl.className = 'text-sm hidden';

  try {
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (!res.ok) throw new Error('Could not read rock file');
    const { sha } = await res.json();

    const md  = buildRockMarkdown(title, owner, rock.quarter, status, due, rock.created, rock.id, outcome, newMilestones);
    const put = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({ message: `update rock: ${title}`, content: b64encode(md), sha })
    });
    if (!put.ok) throw new Error((await put.json()).message);

    rock.title      = title;
    rock.owner      = owner;
    rock.status     = status;
    rock.due        = due;
    rock.outcome    = outcome;
    rock.milestones = newMilestones;

    ROCK_EDITING = null;
    renderRocks();
  } catch(e) {
    statusEl.textContent = '\u2717 ' + e.message;
    statusEl.className = 'text-sm text-red-600';
    statusEl.classList.remove('hidden');
    btn.disabled = false; btn.textContent = 'Save';
  }
}

async function createRock() {
  const token    = window.GITHUB_TOKEN;
  const repo     = window.GITHUB_REPO;
  const btn      = document.getElementById('rock_new_btn');
  const statusEl = document.getElementById('rock_new_status_msg');

  const title   = document.getElementById('rock_new_title')?.value.trim()   || '';
  const owner   = document.getElementById('rock_new_owner')?.value          || '';
  const defaultStatus = ACTIVE_QUARTER > window.DASHBOARD_DATA.current_quarter ? 'draft' : 'on_track';
  const status  = document.getElementById('rock_new_status')?.value         || defaultStatus;
  const due     = document.getElementById('rock_new_due')?.value            || '';
  const outcome = document.getElementById('rock_new_outcome')?.value.trim() || '';
  const msLines = (document.getElementById('rock_new_milestones')?.value || '')
    .split('\n').map(l => l.trim()).filter(Boolean);

  if (!title) { alert('Title is required.'); return; }

  const rocks   = getActiveRocks();
  const quarter = ACTIVE_QUARTER;
  const today   = new Date().toISOString().split('T')[0];

  const maxNum  = rocks.reduce((max, r) => { const m = r.id.match(/(\d+)$/); return m ? Math.max(max, +m[1]) : max; }, 0);
  const id      = `rock-${String(maxNum + 1).padStart(3, '0')}`;
  const slug    = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const filePath = `data/rocks/${quarter}/${id}-${slug}.md`;
  const milestones = msLines.map(text => ({ done: false, text }));

  btn.disabled = true; btn.textContent = 'Creating\u2026';
  statusEl.className = 'text-sm hidden';

  try {
    const put = await fetch(`https://api.github.com/repos/${repo}/contents/${filePath}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({ message: `add rock: ${title}`, content: b64encode(buildRockMarkdown(title, owner, quarter, status, due, today, id, outcome, milestones)) })
    });
    if (!put.ok) throw new Error((await put.json()).message);

    rocks.push({ id, title, owner, quarter, status, created: today, due, outcome, milestones, file: filePath });
    ROCK_EDITING = null;
    renderRocks();
  } catch(e) {
    statusEl.textContent = '\u2717 ' + e.message;
    statusEl.className = 'text-sm text-red-600';
    statusEl.classList.remove('hidden');
    btn.disabled = false; btn.textContent = 'Create';
  }
}

async function deleteRock(ri) {
  const rock  = window.DASHBOARD_DATA.rocks[ri];
  const token = window.GITHUB_TOKEN;
  const repo  = window.GITHUB_REPO;

  if (!confirm(`Delete \u201c${rock.title}\u201d? This cannot be undone.`)) return;

  try {
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (!res.ok) throw new Error('Could not read rock file');
    const { sha } = await res.json();

    const del = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`, {
      method: 'DELETE',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({ message: `remove rock: ${rock.title}`, sha })
    });
    if (!del.ok) throw new Error((await del.json()).message);

    window.DASHBOARD_DATA.rocks.splice(ri, 1);
    ROCK_EDITING = null;
    renderRocks();
  } catch(e) {
    alert('Failed to delete: ' + e.message);
  }
}

function getActiveRocks() {
  return window.DASHBOARD_DATA.rocks_by_quarter[ACTIVE_QUARTER] || [];
}

function switchQuarter(q) {
  ACTIVE_QUARTER = q;
  ROCK_EDITING = null;
  CLOSE_QUARTER_MODE = false;
  window.DASHBOARD_DATA.rocks = getActiveRocks();
  renderRocks();
}

function nextQuarter(q) {
  const [y, qn] = q.split('-Q');
  const n = parseInt(qn);
  return n < 4 ? `${y}-Q${n+1}` : `${parseInt(y)+1}-Q1`;
}

function startCloseQuarter() {
  CLOSE_QUARTER_MODE = true;
  CLOSE_QUARTER_STEP = 0;
  CLOSE_QUARTER_SCORES = {};
  CLOSE_QUARTER_CARRY = {};
  ROCK_EDITING = null;
  renderRocks();
}

function scoreRock(idx, score) {
  CLOSE_QUARTER_SCORES[idx] = score;
  if (score === 'dropped') {
    CLOSE_QUARTER_CARRY[idx] = true; // default carry forward for dropped
  } else {
    delete CLOSE_QUARTER_CARRY[idx];
  }
  renderRocks();
}

function toggleCarryForward(idx) {
  CLOSE_QUARTER_CARRY[idx] = !CLOSE_QUARTER_CARRY[idx];
  renderRocks();
}

function closeQuarterNext() {
  const rocks = getActiveRocks();
  if (CLOSE_QUARTER_STEP < rocks.length - 1) {
    CLOSE_QUARTER_STEP++;
    renderRocks();
  }
}

function closeQuarterPrev() {
  if (CLOSE_QUARTER_STEP > 0) {
    CLOSE_QUARTER_STEP--;
    renderRocks();
  }
}

async function executeCloseQuarter() {
  const rocks = getActiveRocks();
  const token = window.GITHUB_TOKEN;
  const repo  = window.GITHUB_REPO;
  const nq    = nextQuarter(ACTIVE_QUARTER);

  // Validate all rocks are scored
  const unscored = rocks.filter((_, i) => !CLOSE_QUARTER_SCORES[i]);
  if (unscored.length > 0) {
    alert(`Please score all rocks before closing. ${unscored.length} rock(s) remaining.`);
    return;
  }

  const btn = document.getElementById('close_q_execute_btn');
  btn.disabled = true; btn.textContent = 'Closing quarter\u2026';

  try {
    // 1. Update each rock's status in the current quarter
    for (let i = 0; i < rocks.length; i++) {
      const rock = rocks[i];
      const newStatus = CLOSE_QUARTER_SCORES[i];
      if (rock.status === newStatus) continue;

      const res = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`,
        { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
      if (!res.ok) throw new Error(`Could not read ${rock.file}`);
      const { sha } = await res.json();

      const md = buildRockMarkdown(rock.title, rock.owner, rock.quarter, newStatus, rock.due, rock.created, rock.id, rock.outcome, rock.milestones);
      const put = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`, {
        method: 'PUT',
        headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                   Accept: 'application/vnd.github.v3+json' },
        body: JSON.stringify({ message: `close quarter: ${rock.title} \u2192 ${newStatus}`, content: b64encode(md), sha })
      });
      if (!put.ok) throw new Error((await put.json()).message);
      rock.status = newStatus;
    }

    // 2. Carry forward selected rocks to next quarter
    const toCarry = rocks.filter((_, i) => CLOSE_QUARTER_CARRY[i]);
    if (toCarry.length > 0) {
      // Ensure next quarter exists in our data
      if (!window.DASHBOARD_DATA.rocks_by_quarter[nq]) {
        window.DASHBOARD_DATA.rocks_by_quarter[nq] = [];
        if (!window.DASHBOARD_DATA.quarters.includes(nq)) {
          window.DASHBOARD_DATA.quarters.push(nq);
          window.DASHBOARD_DATA.quarters.sort();
        }
      }
      const nqRocks = window.DASHBOARD_DATA.rocks_by_quarter[nq];

      for (const rock of toCarry) {
        const maxNum = nqRocks.reduce((max, r) => {
          const m = r.id.match(/(\d+)$/);
          return m ? Math.max(max, +m[1]) : max;
        }, 0);
        const newId = `rock-${String(maxNum + 1).padStart(3, '0')}`;
        const slug = rock.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
        const filePath = `data/rocks/${nq}/${newId}-${slug}.md`;
        const today = new Date().toISOString().split('T')[0];
        const lastDay = nq.endsWith('Q1') ? `${nq.split('-')[0]}-03-31`
                      : nq.endsWith('Q2') ? `${nq.split('-')[0]}-06-30`
                      : nq.endsWith('Q3') ? `${nq.split('-')[0]}-09-30`
                      : `${nq.split('-')[0]}-12-31`;
        const newMilestones = rock.milestones.map(m => ({ done: false, text: m.text }));

        const md = buildRockMarkdown(rock.title, rock.owner, nq, 'on_track', lastDay, today, newId, rock.outcome, newMilestones);
        const put = await fetch(`https://api.github.com/repos/${repo}/contents/${filePath}`, {
          method: 'PUT',
          headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                     Accept: 'application/vnd.github.v3+json' },
          body: JSON.stringify({ message: `carry forward: ${rock.title} \u2192 ${nq}`, content: b64encode(md) })
        });
        if (!put.ok) throw new Error((await put.json()).message);

        nqRocks.push({
          id: newId, title: rock.title, owner: rock.owner, quarter: nq,
          status: 'on_track', created: today, due: lastDay,
          outcome: rock.outcome, milestones: newMilestones, file: filePath
        });
      }
    }

    // 3. Check if next quarter has draft rocks to review
    const nqDrafts = (window.DASHBOARD_DATA.rocks_by_quarter[nq] || []).filter(r => r.status === 'draft');

    CLOSE_QUARTER_CLOSED_Q = ACTIVE_QUARTER;
    CLOSE_QUARTER_CARRIED = toCarry.length;

    if (nqDrafts.length > 0) {
      // Transition to draft review wizard
      CLOSE_QUARTER_MODE = false;
      DRAFT_REVIEW_MODE = true;
      DRAFT_REVIEW_QUARTER = nq;
      DRAFT_REVIEW_STEP = 0;
      DRAFT_REVIEW_DECISIONS = {}; // {idx: 'keep' | 'Q3' | 'Q4' | ...}
      renderRocks();
    } else {
      // No drafts — go straight to plan step
      CLOSE_QUARTER_MODE = false;
      CLOSE_QUARTER_STEP = 0;
      CLOSE_QUARTER_SHOW_PLAN = true;
      renderRocks();
    }
  } catch(e) {
    alert('Failed to close quarter: ' + e.message);
    btn.disabled = false; btn.textContent = 'Close Quarter';
  }
}

let CLOSE_QUARTER_SHOW_PLAN = false;
let CLOSE_QUARTER_CLOSED_Q = '';
let CLOSE_QUARTER_CARRIED = 0;

/* ── Draft Review Wizard ── */
let DRAFT_REVIEW_MODE = false;
let DRAFT_REVIEW_QUARTER = '';  // the quarter whose drafts we're reviewing
let DRAFT_REVIEW_STEP = 0;
let DRAFT_REVIEW_DECISIONS = {}; // {idx: 'keep' | 'YYYY-QN'}

function draftReviewDecide(idx, decision) {
  DRAFT_REVIEW_DECISIONS[idx] = decision;
  renderRocks();
}

function draftReviewNext() {
  const drafts = getDraftRocks();
  if (DRAFT_REVIEW_STEP < drafts.length - 1) {
    DRAFT_REVIEW_STEP++;
    renderRocks();
  }
}

function draftReviewPrev() {
  if (DRAFT_REVIEW_STEP > 0) {
    DRAFT_REVIEW_STEP--;
    renderRocks();
  }
}

function getDraftRocks() {
  return (window.DASHBOARD_DATA.rocks_by_quarter[DRAFT_REVIEW_QUARTER] || [])
    .map((r, i) => ({rock: r, idx: i}))
    .filter(({rock}) => rock.status === 'draft');
}

function getFutureQuarterOptions() {
  // Return quarters after the review quarter that are in the dropdown
  const quarters = window.DASHBOARD_DATA.quarters;
  return quarters.filter(q => q > DRAFT_REVIEW_QUARTER);
}

async function executeDraftReview() {
  const token = window.GITHUB_TOKEN;
  const repo  = window.GITHUB_REPO;
  const allRocks = window.DASHBOARD_DATA.rocks_by_quarter[DRAFT_REVIEW_QUARTER] || [];
  const drafts = getDraftRocks();

  // Validate all drafts have decisions
  const undecided = drafts.filter(({idx}) => !DRAFT_REVIEW_DECISIONS[idx]);
  if (undecided.length > 0) {
    alert(`Please decide on all draft rocks. ${undecided.length} remaining.`);
    return;
  }

  const btn = document.getElementById('draft_review_execute_btn');
  btn.disabled = true; btn.textContent = 'Applying\u2026';

  try {
    for (const {rock, idx} of drafts) {
      const decision = DRAFT_REVIEW_DECISIONS[idx];

      if (decision === 'keep') {
        // Promote to on_track in current quarter
        const res = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`,
          { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
        if (!res.ok) throw new Error(`Could not read ${rock.file}`);
        const { sha } = await res.json();

        const md = buildRockMarkdown(rock.title, rock.owner, rock.quarter, 'on_track', rock.due, rock.created, rock.id, rock.outcome, rock.milestones);
        const put = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`, {
          method: 'PUT',
          headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                     Accept: 'application/vnd.github.v3+json' },
          body: JSON.stringify({ message: `commit draft: ${rock.title} \u2192 on_track`, content: b64encode(md), sha })
        });
        if (!put.ok) throw new Error((await put.json()).message);
        rock.status = 'on_track';

      } else {
        // Move to a future quarter: delete from current, create in target
        const targetQ = decision;

        // Delete from current quarter
        const res = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`,
          { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
        if (!res.ok) throw new Error(`Could not read ${rock.file}`);
        const { sha } = await res.json();

        const del = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`, {
          method: 'DELETE',
          headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                     Accept: 'application/vnd.github.v3+json' },
          body: JSON.stringify({ message: `push draft: ${rock.title} \u2192 ${targetQ}`, sha })
        });
        if (!del.ok) throw new Error((await del.json()).message);

        // Ensure target quarter exists in data
        if (!window.DASHBOARD_DATA.rocks_by_quarter[targetQ]) {
          window.DASHBOARD_DATA.rocks_by_quarter[targetQ] = [];
          if (!window.DASHBOARD_DATA.quarters.includes(targetQ)) {
            window.DASHBOARD_DATA.quarters.push(targetQ);
            window.DASHBOARD_DATA.quarters.sort();
          }
        }

        // Create in target quarter
        const tqRocks = window.DASHBOARD_DATA.rocks_by_quarter[targetQ];
        const maxNum = tqRocks.reduce((max, r) => {
          const m = r.id.match(/(\d+)$/);
          return m ? Math.max(max, +m[1]) : max;
        }, 0);
        const newId = `rock-${String(maxNum + 1).padStart(3, '0')}`;
        const slug = rock.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
        const filePath = `data/rocks/${targetQ}/${newId}-${slug}.md`;
        const lastDay = targetQ.endsWith('Q1') ? `${targetQ.split('-')[0]}-03-31`
                      : targetQ.endsWith('Q2') ? `${targetQ.split('-')[0]}-06-30`
                      : targetQ.endsWith('Q3') ? `${targetQ.split('-')[0]}-09-30`
                      : `${targetQ.split('-')[0]}-12-31`;

        const md = buildRockMarkdown(rock.title, rock.owner, targetQ, 'draft', lastDay, rock.created, newId, rock.outcome, rock.milestones);

        // Create .gitkeep first if needed
        const keepPath = `data/rocks/${targetQ}/.gitkeep`;
        const keepCheck = await fetch(`https://api.github.com/repos/${repo}/contents/${keepPath}`,
          { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
        if (!keepCheck.ok) {
          await fetch(`https://api.github.com/repos/${repo}/contents/${keepPath}`, {
            method: 'PUT',
            headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                       Accept: 'application/vnd.github.v3+json' },
            body: JSON.stringify({ message: `create ${targetQ} quarter`, content: b64encode('') })
          });
        }

        const put = await fetch(`https://api.github.com/repos/${repo}/contents/${filePath}`, {
          method: 'PUT',
          headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                     Accept: 'application/vnd.github.v3+json' },
          body: JSON.stringify({ message: `push draft: ${rock.title} \u2192 ${targetQ}`, content: b64encode(md) })
        });
        if (!put.ok) throw new Error((await put.json()).message);

        tqRocks.push({
          id: newId, title: rock.title, owner: rock.owner, quarter: targetQ,
          status: 'draft', created: rock.created, due: lastDay,
          outcome: rock.outcome, milestones: rock.milestones, file: filePath
        });

        // Remove from current quarter in-memory
        const curIdx = allRocks.indexOf(rock);
        if (curIdx >= 0) allRocks.splice(curIdx, 1);
      }
    }

    // Done — show plan step
    DRAFT_REVIEW_MODE = false;
    CLOSE_QUARTER_SHOW_PLAN = true;
    renderRocks();
  } catch(e) {
    alert('Failed to process drafts: ' + e.message);
    btn.disabled = false; btn.textContent = 'Apply Decisions';
  }
}

function buildDraftReviewUI() {
  const drafts = getDraftRocks();
  const futureQs = getFutureQuarterOptions();
  const {rock, idx} = drafts[DRAFT_REVIEW_STEP];
  const total = drafts.length;
  const decided = Object.keys(DRAFT_REVIEW_DECISIONS).length;
  const decision = DRAFT_REVIEW_DECISIONS[idx];

  let html = `<div class="mb-6 bg-white rounded-lg border-2 border-amber-300 shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <div>
        <span class="text-xs font-semibold text-amber-600 uppercase tracking-widest">Review Drafts: ${DRAFT_REVIEW_QUARTER}</span>
        <span class="text-xs text-gray-400 ml-2">${decided}/${total} decided</span>
      </div>
      <button onclick="DRAFT_REVIEW_MODE=false;CLOSE_QUARTER_SHOW_PLAN=true;renderRocks();"
        class="text-gray-400 hover:text-gray-600 text-sm px-2 py-1 rounded hover:bg-gray-100">Skip All \u2192</button>
    </div>

    <div class="w-full bg-gray-100 rounded-full h-1.5 mb-5">
      <div class="bg-amber-500 h-1.5 rounded-full transition-all" style="width:${Math.round(decided/total*100)}%"></div>
    </div>

    <div class="bg-gray-50 rounded-lg p-4 mb-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-sm font-bold text-gray-900">${esc(rock.title)}</h3>
        ${ownerChip(rock.owner)}
      </div>
      ${rock.outcome ? `<p class="text-xs text-gray-500 italic mb-3">${esc(rock.outcome)}</p>` : ''}

      <p class="text-xs font-medium text-gray-600 mb-2">Commit to ${DRAFT_REVIEW_QUARTER} or push to a future quarter?</p>

      <div class="flex flex-wrap gap-2">
        <button onclick="draftReviewDecide(${idx},'keep')"
          class="px-3 py-2 rounded-lg text-sm font-medium transition-colors ${decision === 'keep' ? 'bg-green-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-green-50'}">
          \u2713 Commit to ${DRAFT_REVIEW_QUARTER}
        </button>
        ${futureQs.map(q => `
        <button onclick="draftReviewDecide(${idx},'${q}')"
          class="px-3 py-2 rounded-lg text-sm font-medium transition-colors ${decision === '${q}' ? 'bg-amber-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-amber-50'}">
          \u2192 Push to ${q}
        </button>`).join('')}
      </div>
    </div>

    <div class="flex items-center justify-between">
      <button onclick="draftReviewPrev()" ${DRAFT_REVIEW_STEP === 0 ? 'disabled' : ''}
        class="px-3 py-1.5 rounded-lg text-sm font-medium ${DRAFT_REVIEW_STEP === 0 ? 'text-gray-300' : 'text-gray-600 hover:bg-gray-100'}">\u2190 Previous</button>
      <span class="text-xs text-gray-400">${DRAFT_REVIEW_STEP + 1} of ${total}</span>
      ${DRAFT_REVIEW_STEP < total - 1 ? `
      <button onclick="draftReviewNext()"
        class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100">Next \u2192</button>`
      : `
      <button onclick="executeDraftReview()" id="draft_review_execute_btn"
        class="bg-amber-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-amber-700 transition-colors"
        ${decided < total ? 'disabled title="Decide on all drafts first"' : ''}>
        Apply Decisions
      </button>`}
    </div>
  </div>`;

  // Summary list
  html += `<div class="space-y-2">`;
  drafts.forEach(({rock: r, idx: i}, step) => {
    const d = DRAFT_REVIEW_DECISIONS[i];
    const isCurrent = step === DRAFT_REVIEW_STEP;
    html += `<div onclick="DRAFT_REVIEW_STEP=${step};renderRocks();"
      class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors ${isCurrent ? 'bg-amber-50 border border-amber-200' : 'hover:bg-gray-50'}">
      <span class="text-sm ${d === 'keep' ? 'text-green-600' : d ? 'text-amber-600' : 'text-gray-300'}">
        ${d === 'keep' ? '\u2713' : d ? '\u2192' : '\u25CB'}
      </span>
      <span class="text-sm ${d ? 'text-gray-900' : 'text-gray-400'} flex-1">${esc(r.title)}</span>
      ${ownerChip(r.owner)}
      ${d && d !== 'keep' ? `<span class="text-xs text-amber-600">\u2192 ${d}</span>` : ''}
      ${d === 'keep' ? `<span class="text-xs text-green-600">\u2713 ${DRAFT_REVIEW_QUARTER}</span>` : ''}
    </div>`;
  });
  html += `</div>`;

  return html;
}

async function stubOutQuarters() {
  const token = window.GITHUB_TOKEN;
  const repo  = window.GITHUB_REPO;
  const btn   = document.getElementById('stub_q_btn');
  btn.disabled = true; btn.textContent = 'Creating quarters\u2026';

  try {
    // Generate next 4 quarters from the one after the closed quarter
    const nq = nextQuarter(CLOSE_QUARTER_CLOSED_Q);
    let q = nq;
    const toCreate = [];
    for (let i = 0; i < 4; i++) {
      toCreate.push(q);
      q = nextQuarter(q);
    }

    for (const qtr of toCreate) {
      if (window.DASHBOARD_DATA.rocks_by_quarter[qtr] && window.DASHBOARD_DATA.rocks_by_quarter[qtr].length > 0) {
        continue; // already has rocks, skip
      }

      // Create a placeholder .gitkeep file to ensure the directory exists in git
      const path = `data/rocks/${qtr}/.gitkeep`;
      // Check if it already exists
      const check = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`,
        { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
      if (check.ok) continue; // already exists

      const put = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
        method: 'PUT',
        headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                   Accept: 'application/vnd.github.v3+json' },
        body: JSON.stringify({ message: `plan: create ${qtr} quarter`, content: b64encode('') })
      });
      if (!put.ok) throw new Error((await put.json()).message);

      // Add to in-memory data
      if (!window.DASHBOARD_DATA.rocks_by_quarter[qtr]) {
        window.DASHBOARD_DATA.rocks_by_quarter[qtr] = [];
      }
      if (!window.DASHBOARD_DATA.quarters.includes(qtr)) {
        window.DASHBOARD_DATA.quarters.push(qtr);
        window.DASHBOARD_DATA.quarters.sort();
      }
    }

    CLOSE_QUARTER_SHOW_PLAN = false;
    switchQuarter(nextQuarter(CLOSE_QUARTER_CLOSED_Q));
    alert(`Done! Created quarters: ${toCreate.join(', ')}. You can now draft rocks in any future quarter.`);
  } catch(e) {
    alert('Failed to create quarters: ' + e.message);
    btn.disabled = false; btn.textContent = 'Create Next 4 Quarters';
  }
}

function skipPlanQuarters() {
  CLOSE_QUARTER_SHOW_PLAN = false;
  switchQuarter(nextQuarter(CLOSE_QUARTER_CLOSED_Q));
}

function buildCloseQuarterUI() {
  const rocks = getActiveRocks();
  const nq = nextQuarter(ACTIVE_QUARTER);
  const rock = rocks[CLOSE_QUARTER_STEP];
  const ri = CLOSE_QUARTER_STEP;
  const total = rocks.length;
  const scored = Object.keys(CLOSE_QUARTER_SCORES).length;

  let html = `<div class="mb-6 bg-white rounded-lg border-2 border-orange-300 shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <div>
        <span class="text-xs font-semibold text-orange-600 uppercase tracking-widest">Close Quarter: ${ACTIVE_QUARTER}</span>
        <span class="text-xs text-gray-400 ml-2">${scored}/${total} scored</span>
      </div>
      <button onclick="CLOSE_QUARTER_MODE=false;renderRocks();"
        class="text-gray-400 hover:text-gray-600 text-sm px-2 py-1 rounded hover:bg-gray-100">&times; Cancel</button>
    </div>

    <div class="w-full bg-gray-100 rounded-full h-1.5 mb-5">
      <div class="bg-orange-500 h-1.5 rounded-full transition-all" style="width:${Math.round(scored/total*100)}%"></div>
    </div>

    <div class="bg-gray-50 rounded-lg p-4 mb-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-sm font-bold text-gray-900">${esc(rock.title)}</h3>
        ${ownerChip(rock.owner)}
      </div>
      ${rock.outcome ? `<p class="text-xs text-gray-500 italic mb-2">${esc(rock.outcome)}</p>` : ''}
      <div class="text-xs text-gray-400 mb-3">Due ${esc(rock.due)} &middot; ${rock.milestones.filter(m=>m.done).length}/${rock.milestones.length} milestones</div>

      <div class="flex gap-2 mb-3">
        <button onclick="scoreRock(${ri},'complete')"
          class="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${CLOSE_QUARTER_SCORES[ri] === 'complete' ? 'bg-green-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-green-50'}">
          \u2713 Complete
        </button>
        <button onclick="scoreRock(${ri},'dropped')"
          class="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${CLOSE_QUARTER_SCORES[ri] === 'dropped' ? 'bg-red-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-red-50'}">
          \u2717 Dropped
        </button>
      </div>

      ${CLOSE_QUARTER_SCORES[ri] === 'dropped' ? `
      <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
        <input type="checkbox" ${CLOSE_QUARTER_CARRY[ri] ? 'checked' : ''} onchange="toggleCarryForward(${ri})"
          class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500">
        Carry forward to ${nq}
      </label>` : ''}
    </div>

    <div class="flex items-center justify-between">
      <button onclick="closeQuarterPrev()" ${ri === 0 ? 'disabled' : ''}
        class="px-3 py-1.5 rounded-lg text-sm font-medium ${ri === 0 ? 'text-gray-300' : 'text-gray-600 hover:bg-gray-100'}">\u2190 Previous</button>
      <span class="text-xs text-gray-400">${ri + 1} of ${total}</span>
      ${ri < total - 1 ? `
      <button onclick="closeQuarterNext()"
        class="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100">Next \u2192</button>`
      : `
      <button onclick="executeCloseQuarter()" id="close_q_execute_btn"
        class="bg-orange-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-orange-700 transition-colors"
        ${scored < total ? 'disabled title="Score all rocks first"' : ''}>
        Close Quarter
      </button>`}
    </div>
  </div>`;

  // Show summary of scored rocks below
  html += `<div class="space-y-2">`;
  rocks.forEach((r, i) => {
    const score = CLOSE_QUARTER_SCORES[i];
    const carry = CLOSE_QUARTER_CARRY[i];
    const isCurrent = i === CLOSE_QUARTER_STEP;
    html += `<div onclick="CLOSE_QUARTER_STEP=${i};renderRocks();"
      class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors ${isCurrent ? 'bg-orange-50 border border-orange-200' : 'hover:bg-gray-50'}">
      <span class="text-sm ${score === 'complete' ? 'text-green-600' : score === 'dropped' ? 'text-red-600' : 'text-gray-300'}">
        ${score === 'complete' ? '\u2713' : score === 'dropped' ? '\u2717' : '\u25CB'}
      </span>
      <span class="text-sm ${score ? 'text-gray-900' : 'text-gray-400'} flex-1">${esc(r.title)}</span>
      ${ownerChip(r.owner)}
      ${carry ? `<span class="text-xs text-blue-600">\u2192 ${nextQuarter(ACTIVE_QUARTER)}</span>` : ''}
    </div>`;
  });
  html += `</div>`;

  return html;
}

function renderRocks() {
  const d = window.DASHBOARD_DATA;
  const rocks = getActiveRocks();
  d.rocks = rocks; // keep backward compat for L10 tab

  const quarters = d.quarters;
  const isCurrentQ = ACTIVE_QUARTER === d.current_quarter;

  // Quarter chooser + action buttons
  const qOpts = quarters.map(q =>
    `<option value="${q}" ${q === ACTIVE_QUARTER ? 'selected' : ''}>${q}${q === d.current_quarter ? ' (current)' : ''}</option>`).join('');

  let html = `<div class="mb-4 flex items-center justify-between flex-wrap gap-2">
    <div class="flex items-center gap-2">
      <label class="text-xs font-medium text-gray-500">Quarter:</label>
      <select onchange="switchQuarter(this.value)"
        class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500">
        ${qOpts}
      </select>
    </div>
    <div class="flex gap-2">
      ${!CLOSE_QUARTER_MODE && rocks.length > 0 && rocks.some(r => r.status !== 'complete' && r.status !== 'dropped') ? `
      <button onclick="startCloseQuarter()"
        class="bg-orange-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-orange-700 transition-colors">
        Close Quarter
      </button>` : ''}
      <button onclick="ROCK_EDITING='new';renderRocks();"
        class="bg-blue-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-blue-700 transition-colors">
        + Add Rock
      </button>
    </div>
  </div>`;

  if (DRAFT_REVIEW_MODE) {
    html += buildDraftReviewUI();
    document.getElementById('panel-rocks').innerHTML = html;
    return;
  }

  if (CLOSE_QUARTER_SHOW_PLAN) {
    const nq = nextQuarter(CLOSE_QUARTER_CLOSED_Q);
    const futureQs = [];
    let fq = nq;
    for (let i = 0; i < 4; i++) { futureQs.push(fq); fq = nextQuarter(fq); }

    html += `<div class="mb-6 bg-white rounded-lg border-2 border-green-300 shadow-sm p-5">
      <div class="text-xs font-semibold text-green-600 uppercase tracking-widest mb-2">\u2713 Quarter Closed: ${CLOSE_QUARTER_CLOSED_Q}</div>
      <p class="text-sm text-gray-700 mb-4">${CLOSE_QUARTER_CARRIED} rock(s) carried forward to ${nq}.</p>

      <div class="bg-gray-50 rounded-lg p-4 mb-4">
        <h3 class="text-sm font-bold text-gray-900 mb-2">Plan your roadmap?</h3>
        <p class="text-xs text-gray-500 mb-3">Stub out the next 4 quarters so you can start drafting rocks for your annual plan:</p>
        <div class="flex flex-wrap gap-2 mb-4">
          ${futureQs.map(q => `<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700">${q}</span>`).join('')}
        </div>
        <div class="flex gap-2">
          <button onclick="stubOutQuarters()" id="stub_q_btn"
            class="bg-blue-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-blue-700 transition-colors">
            Create Next 4 Quarters
          </button>
          <button onclick="skipPlanQuarters()"
            class="bg-white border border-gray-200 text-gray-600 rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-gray-50 transition-colors">
            Skip
          </button>
        </div>
      </div>
    </div>`;
    document.getElementById('panel-rocks').innerHTML = html;
    return;
  }

  if (CLOSE_QUARTER_MODE) {
    html += buildCloseQuarterUI();
    document.getElementById('panel-rocks').innerHTML = html;
    return;
  }

  if (ROCK_EDITING === 'new') {
    html += `<div class="mb-6">${buildRockEditCard(null, 'new')}</div>`;
  }

  if (rocks.length === 0) {
    html += `<p class="text-sm text-gray-500 mt-4">No rocks for ${ACTIVE_QUARTER}.</p>`;
    document.getElementById('panel-rocks').innerHTML = html;
    return;
  }

  const byOwner = {};
  rocks.forEach((r, ri) => { (byOwner[r.owner] = byOwner[r.owner] || []).push({r, ri}); });

  for (const [owner, list] of Object.entries(byOwner)) {
    html += `<div class="mb-8">
      <h2 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">${esc(owner)}</h2>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">`;

    list.forEach(({r: rock, ri}) => {
      html += (ROCK_EDITING === ri) ? buildRockEditCard(rock, ri) : buildRockViewCard(rock, ri);
    });

    html += '</div></div>';
  }

  document.getElementById('panel-rocks').innerHTML = html;
}

/* ── Scorecard ── */
let SC_EDIT_MODE = false;

function renderScorecard() {
  const metrics = window.DASHBOARD_DATA.scorecard;
  const el = document.getElementById('panel-scorecard');
  el.innerHTML = SC_EDIT_MODE ? buildSCEditForm(metrics) : buildSCView(metrics);
}

function buildSCView(metrics) {
  const headers = ['Metric', 'Owner', 'Goal', 'Frequency', 'Green', 'Red'];

  let html = `<div class="mb-4 flex justify-end">
    <button onclick="SC_EDIT_MODE=true;renderScorecard();"
      class="bg-white border border-gray-200 text-gray-600 rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-gray-50 transition-colors">
      Edit
    </button>
  </div>`;

  html += `<div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-100">
      <thead class="bg-gray-50">
        <tr>${headers.map(h =>
          `<th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">${h}</th>`
        ).join('')}</tr>
      </thead>
      <tbody class="divide-y divide-gray-100">`;

  metrics.forEach((m, i) => {
    html += `<tr class="${i % 2 ? 'bg-gray-50' : ''} hover:bg-blue-50">
      <td class="px-4 py-3 text-sm font-medium text-gray-900">${esc(m.metric)}</td>
      <td class="px-4 py-3 text-sm whitespace-nowrap">${ownerChip(m.owner)}</td>
      <td class="px-4 py-3 text-sm text-gray-600">${esc(m.goal)}</td>
      <td class="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">${esc(m.frequency)}</td>
      <td class="px-4 py-3 text-sm font-medium text-green-700 whitespace-nowrap">${esc(m.green)}</td>
      <td class="px-4 py-3 text-sm font-medium text-red-700 whitespace-nowrap">${esc(m.red)}</td>
    </tr>`;
  });

  html += '</tbody></table></div>';
  return html;
}

function buildSCEditForm(metrics) {
  const ownerOpts = TEAM_MEMBERS.concat(['Team']).map(n =>
    `<option value="${n}">${n}</option>`).join('');
  const freqOpts = ['Weekly','Monthly','Quarterly'].map(f =>
    `<option value="${f}">${f}</option>`).join('');

  let html = `<div class="mb-5 flex items-center gap-3">
    <button onclick="saveScorecard()" id="sc_save_btn"
      class="bg-blue-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-blue-700 transition-colors">
      Save Changes
    </button>
    <button onclick="SC_EDIT_MODE=false;renderScorecard();"
      class="bg-white border border-gray-200 text-gray-600 rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-gray-50 transition-colors">
      Cancel
    </button>
    <button onclick="addSCRow()" class="bg-white border border-gray-200 text-green-600 rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-gray-50 transition-colors">
      + Add Metric
    </button>
    <span id="sc_save_status" class="text-sm hidden"></span>
  </div>`;

  html += `<div id="sc_edit_rows" class="space-y-3">`;
  metrics.forEach((m, i) => { html += buildSCRowHtml(m, i); });
  html += `</div>`;

  return html;
}

function buildSCRowHtml(m, i) {
  const ownerOpts = TEAM_MEMBERS.concat(['Team']).map(n =>
    `<option value="${n}" ${n === m.owner ? 'selected' : ''}>${n}</option>`).join('');
  const freqOpts = ['Weekly','Monthly','Quarterly'].map(f =>
    `<option value="${f}" ${f === m.frequency ? 'selected' : ''}>${f}</option>`).join('');

  return `<div class="bg-white rounded-lg border border-gray-200 shadow-sm p-4 group" id="sc_row_${i}">
    <div class="grid grid-cols-6 gap-3">
      <div class="col-span-2">
        <label class="text-xs font-medium text-gray-500 block mb-1">Metric</label>
        <input type="text" id="sc_m_${i}" value="${esc(m.metric)}"
          class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
      </div>
      <div>
        <label class="text-xs font-medium text-gray-500 block mb-1">Owner</label>
        <select id="sc_o_${i}"
          class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">— select —</option>${ownerOpts}
        </select>
      </div>
      <div>
        <label class="text-xs font-medium text-gray-500 block mb-1">Goal</label>
        <input type="text" id="sc_g_${i}" value="${esc(m.goal)}"
          class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
      </div>
      <div>
        <label class="text-xs font-medium text-gray-500 block mb-1">Green</label>
        <input type="text" id="sc_gr_${i}" value="${esc(m.green)}"
          class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
      </div>
      <div class="flex gap-2">
        <div class="flex-1">
          <label class="text-xs font-medium text-gray-500 block mb-1">Red</label>
          <input type="text" id="sc_r_${i}" value="${esc(m.red)}"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
        </div>
        <button onclick="removeSCRow(${i})"
          class="self-end p-2 rounded hover:bg-red-100 opacity-0 group-hover:opacity-100 transition-opacity mb-0.5"
          title="Remove metric">
          <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>
  </div>`;
}

function addSCRow() {
  const metrics = window.DASHBOARD_DATA.scorecard;
  const i = metrics.length;
  metrics.push({ metric: '', owner: '', goal: '', frequency: 'Weekly', green: '', red: '' });
  const container = document.getElementById('sc_edit_rows');
  container.insertAdjacentHTML('beforeend', buildSCRowHtml(metrics[i], i));
}

function removeSCRow(i) {
  const el = document.getElementById('sc_row_' + i);
  if (el) el.remove();
  window.DASHBOARD_DATA.scorecard[i]._deleted = true;
}

async function saveScorecard() {
  const token    = window.GITHUB_TOKEN;
  const repo     = window.GITHUB_REPO;
  const path     = 'data/scorecard/metrics.md';
  const btn      = document.getElementById('sc_save_btn');
  const statusEl = document.getElementById('sc_save_status');

  btn.disabled = true; btn.textContent = 'Saving\u2026';
  statusEl.className = 'text-sm hidden';

  // Collect rows
  const metrics = window.DASHBOARD_DATA.scorecard;
  const updated = [];
  metrics.forEach((m, i) => {
    if (m._deleted) return;
    const el = document.getElementById('sc_row_' + i);
    if (!el) return;
    updated.push({
      metric:    document.getElementById('sc_m_' + i)?.value.trim()  || '',
      owner:     document.getElementById('sc_o_' + i)?.value         || '',
      goal:      document.getElementById('sc_g_' + i)?.value.trim()  || '',
      frequency: 'Weekly',
      green:     document.getElementById('sc_gr_' + i)?.value.trim() || '',
      red:       document.getElementById('sc_r_' + i)?.value.trim()  || '',
    });
  });

  // Build markdown
  let md = `# Scorecard Metrics\n\n## Your Company\n\n`;
  md += `*The numbers that tell you the health of your business at a glance. Review weekly at L10.*\n\n---\n\n`;
  md += `## How to Use\n\nEach metric has an **owner**, a **goal**, and **green/red thresholds**. During the weekly L10, each owner reports their number. If it's green, move on. If it's red, drop it to the Issues List.\n\n---\n\n`;
  md += `## Metrics\n\n`;
  md += `| Metric | Owner | Goal | Frequency | Green | Red |\n`;
  md += `|--------|-------|------|-----------|-------|-----|\n`;
  updated.forEach(m => {
    md += `| ${m.metric} | ${m.owner} | ${m.goal} | ${m.frequency} | ${m.green} | ${m.red} |\n`;
  });
  md += `\n---\n\n## Adding Metrics\n\nGood metrics are:\n- **Owned** by one person (not shared)\n- **Measurable** with a specific number (not subjective)\n- **Leading** indicators when possible (activity, not just results)\n- **Weekly** cadence for most (monthly for some)\n\nKeep it to 5-15 total. If you have more, you're tracking too much.\n`;

  try {
    let sha;
    const check = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (check.ok) sha = (await check.json()).sha;

    const body = { message: 'update scorecard metrics', content: b64encode(md) };
    if (sha) body.sha = sha;

    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error((await res.json()).message);

    window.DASHBOARD_DATA.scorecard = updated;
    SC_EDIT_MODE = false;
    renderScorecard();
    statusEl.textContent = '\u2713 Saved';
    statusEl.className = 'text-sm text-green-600';
  } catch(e) {
    statusEl.textContent = '\u2717 ' + e.message;
    statusEl.className = 'text-sm text-red-600';
  }
  statusEl.classList.remove('hidden');
  btn.disabled = false; btn.textContent = 'Save Changes';
}

/* ── Accountability Chart ── */
let AC_EDIT_MODE = false;

function renderAccountability() {
  const seats = window.DASHBOARD_DATA.accountability;
  const el    = document.getElementById('panel-accountability');
  el.innerHTML = AC_EDIT_MODE ? buildACEditForm(seats) : buildACView(seats);
}

function buildACView(seats) {
  let html = `<div class="mb-4 flex justify-end">
    <button onclick="AC_EDIT_MODE=true;renderAccountability();"
      class="bg-white border border-gray-200 text-gray-600 rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-gray-50 transition-colors">
      Edit
    </button>
  </div>
  <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">`;

  seats.forEach(seat => {
    const color = SEAT_COLOR[seat.seat] || '#9ca3af';
    let roles = '<ol class="mt-3 space-y-1.5">';
    seat.roles.forEach(r => {
      roles += `<li class="text-sm text-gray-600 flex gap-2">
        <span class="text-gray-400 font-medium tabular-nums w-4 shrink-0">${r.num}.</span>
        <span>${esc(r.role)}</span>
      </li>`;
    });
    roles += '</ol>';

    html += `<div class="bg-white rounded-lg border border-gray-200 shadow-sm p-4" style="border-top: 4px solid ${color}">
      <h3 class="text-sm font-bold text-gray-900">${esc(seat.seat)}</h3>
      <div class="mt-1">${ownerChip(seat.owner)}</div>
      ${roles}
    </div>`;
  });

  html += '</div>';
  return html;
}

function buildACEditForm(seats) {
  let html = `<div class="mb-5 flex items-center gap-3">
    <button onclick="saveAccountability()" id="ac_save_btn"
      class="bg-blue-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-blue-700 transition-colors">
      Save Changes
    </button>
    <button onclick="AC_EDIT_MODE=false;renderAccountability();"
      class="bg-white border border-gray-200 text-gray-600 rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-gray-50 transition-colors">
      Cancel
    </button>
    <span id="ac_save_status" class="text-sm hidden"></span>
  </div>
  <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">`;

  seats.forEach((seat, si) => {
    const color = SEAT_COLOR[seat.seat] || '#9ca3af';
    let roleInputs = '';
    seat.roles.forEach((r, ri) => {
      roleInputs += `<li class="flex gap-2 items-center">
        <span class="text-gray-400 font-medium tabular-nums w-4 shrink-0 text-sm">${r.num}.</span>
        <input type="text" id="ac_role_${si}_${ri}" value="${esc(r.role)}"
          class="flex-1 border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
      </li>`;
    });

    html += `<div class="bg-white rounded-lg border border-gray-200 shadow-sm p-4" style="border-top: 4px solid ${color}">
      <h3 class="text-sm font-bold text-gray-900 mb-2">${esc(seat.seat)}</h3>
      <input type="text" id="ac_owner_${si}" value="${esc(seat.owner)}" placeholder="Owner name"
        class="w-full border border-gray-200 rounded px-2 py-1.5 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500">
      <ol class="space-y-1.5">${roleInputs}</ol>
    </div>`;
  });

  html += '</div>';
  return html;
}

function buildAccountabilityMarkdown() {
  const seats = window.DASHBOARD_DATA.accountability;
  const today = new Date().toISOString().split('T')[0];

  let md = `# Accountability Chart\n\n## Your Company\n\n*Last updated: ${today}*\n\n---\n\n`;
  md += `## How to Use This Chart\n\nEvery seat has **one owner** and **five roles** (the key responsibilities for that seat). A person can own multiple seats, but every seat needs exactly one owner. If nobody owns it, it\u2019s a gap to fill.\n\n---\n\n`;

  seats.forEach((seat, si) => {
    const owner = (document.getElementById(`ac_owner_${si}`)?.value || '').trim();
    md += `## ${seat.seat}\n\n**Owner:** ${owner}\n\n| # | Role |\n|---|------|\n`;
    seat.roles.forEach((r, ri) => {
      const role = (document.getElementById(`ac_role_${si}_${ri}`)?.value || '').trim();
      md += `| ${r.num} | ${role} |\n`;
    });
    md += `\n---\n\n`;
  });

  md += `*Add or remove seats as needed. The key rule: every function of the business has one clear owner.*\n`;
  return md;
}

async function saveAccountability() {
  const token    = window.GITHUB_TOKEN;
  const repo     = window.GITHUB_REPO;
  const path     = 'data/accountability.md';
  const btn      = document.getElementById('ac_save_btn');
  const statusEl = document.getElementById('ac_save_status');

  btn.disabled = true; btn.textContent = 'Saving\u2026';
  statusEl.className = 'text-sm hidden';

  try {
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (!res.ok) throw new Error('Could not read accountability.md');
    const { sha } = await res.json();

    const put = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({ message: 'update: accountability chart', content: b64encode(buildAccountabilityMarkdown()), sha })
    });
    if (!put.ok) throw new Error((await put.json()).message);

    /* Sync in-memory data */
    window.DASHBOARD_DATA.accountability.forEach((seat, si) => {
      seat.owner = (document.getElementById(`ac_owner_${si}`)?.value || '').trim();
      seat.roles.forEach((r, ri) => {
        r.role = (document.getElementById(`ac_role_${si}_${ri}`)?.value || '').trim();
      });
    });

    AC_EDIT_MODE = false;
    renderAccountability();

  } catch(e) {
    statusEl.textContent = '\u2717 ' + e.message;
    statusEl.className = 'text-sm text-red-600';
    statusEl.classList.remove('hidden');
    btn.disabled = false; btn.textContent = 'Save Changes';
  }
}

/* ── L10 Agenda (Interactive) ── */

function addTodo() {
  const ownerOpts = window.DASHBOARD_DATA.l10.attendees
    .map(a => `<option value="${a}">${a.split(' ')[0]}</option>`).join('');
  const row = document.createElement('div');
  row.className = 'todo-row flex gap-2';
  row.innerHTML = `
    <input type="text" class="todo-text flex-1 border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="To-Do">
    <select class="todo-owner border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-28">
      <option value="">Owner</option>${ownerOpts}
    </select>
    <input type="date" class="todo-due border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
    <button onclick="this.closest('.todo-row').remove()" class="text-gray-300 hover:text-red-400 px-1 text-lg leading-none">&times;</button>`;
  document.getElementById('todos_list').appendChild(row);
}

async function saveMeeting() {
  const d = window.DASHBOARD_DATA;
  const date = document.getElementById('meeting_date').value;
  if (!date) { alert('Please set a meeting date.'); return; }

  const btn = document.getElementById('save_btn');
  const statusEl = document.getElementById('save_status');
  btn.disabled = true; btn.textContent = 'Saving\u2026';
  statusEl.className = 'text-sm hidden';

  let md = `# Your Company \u2014 L10 Meeting Notes\n\n`;
  md += `**Date:** ${date}\n**Attendees:** ${d.l10.attendees.join(', ')}\n\n---\n\n`;

  // 1. Segue
  md += `## 1. Segue (5 min)\n\n`;
  d.l10.attendees.forEach((a, i) => {
    md += `- **${a}:** ${(document.getElementById('segue_'+i)?.value || '').trim()}\n`;
  });
  md += `\n---\n\n`;

  // 2. Scorecard
  md += `## 2. Scorecard Review (5 min)\n\n`;
  md += `| Metric | Owner | Goal | Actual | Status |\n|--------|-------|------|--------|--------|\n`;
  d.scorecard.forEach((m, i) => {
    const actual = (document.getElementById('sc_'+i+'_actual')?.value || '').trim();
    const st = document.getElementById('sc_'+i+'_status')?.value || '';
    const icon = st === 'green' ? '\uD83D\uDFE2' : st === 'red' ? '\uD83D\uDD34' : '\u2014';
    md += `| ${m.metric} | ${m.owner} | ${m.goal} | ${actual} | ${icon} |\n`;
  });
  md += `\n---\n\n`;

  // 3. Rocks
  md += `## 3. Rock Review (5 min)\n\n`;
  md += `| Rock | Owner | Status |\n|------|-------|--------|\n`;
  d.rocks.forEach((r, i) => {
    const st = document.getElementById('rock_'+i+'_status')?.value || r.status;
    md += `| ${r.title} | ${r.owner} | ${st === 'on_track' ? '\uD83D\uDFE2 On Track' : '\uD83D\uDD34 Off Track'} |\n`;
  });
  md += `\n---\n\n`;

  // 4. Headlines
  md += `## 4. Headlines (5 min)\n\n`;
  const hl = (document.getElementById('headlines')?.value || '').trim();
  (hl ? hl.split('\n').filter(l => l.trim()) : ['']).forEach(l => md += `- ${l.replace(/^[-\u2022*]\s*/,'')}\n`);
  md += `\n---\n\n`;

  // 5. To-Do Review
  md += `## 5. To-Do Review (5 min)\n\n`;
  md += `**Completion rate:** ${document.getElementById('todo_rate')?.value || ''}%\n\n---\n\n`;

  // 6. IDS
  md += `## 6. IDS (60 min)\n\n`;
  for (let i = 0; i < 3; i++) {
    md += `### Issue ${i+1}:\n`;
    md += `**Identify:** ${(document.getElementById('ids_'+i+'_identify')?.value || '').trim()}\n`;
    md += `**Discuss:** ${(document.getElementById('ids_'+i+'_discuss')?.value || '').trim()}\n`;
    md += `**Solve:**\n- [ ] ${(document.getElementById('ids_'+i+'_solve')?.value || '').trim()}\n\n`;
  }
  md += `---\n\n`;

  // 7. Conclude
  md += `## 7. Conclude (5 min)\n\n### New To-Dos\n\n`;
  md += `| To-Do | Owner | Due Date |\n|-------|-------|----------|\n`;
  document.querySelectorAll('.todo-row').forEach(row => {
    const t = row.querySelector('.todo-text')?.value.trim() || '';
    const o = row.querySelector('.todo-owner')?.value || '';
    const due = row.querySelector('.todo-due')?.value || '';
    if (t || o || due) md += `| ${t} | ${o} | ${due} |\n`;
  });
  md += `\n### Cascading Messages\n\n`;
  const cas = (document.getElementById('cascade')?.value || '').trim();
  (cas ? cas.split('\n').filter(l => l.trim()) : ['']).forEach(l => md += `- ${l.replace(/^[-\u2022*]\s*/,'')}\n`);
  md += `\n### Meeting Rating\n\n| Person | Rating |\n|--------|--------|\n`;
  let total = 0, cnt = 0;
  d.l10.attendees.forEach((a, i) => {
    const r = document.getElementById('rating_'+i)?.value || '';
    md += `| ${a} | ${r} |\n`;
    if (r) { total += parseInt(r)||0; cnt++; }
  });
  md += `\n**Average:** ${cnt ? (total/cnt).toFixed(1) : '\u2014'}/10\n`;

  // Commit via GitHub Contents API
  const token = window.GITHUB_TOKEN;
  const repo  = window.GITHUB_REPO;
  const path  = `data/meetings/l10/${date}.md`;
  const content = b64encode(md);

  try {
    let sha;
    const check = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (check.ok) sha = (await check.json()).sha;

    const body = { message: `meeting notes: L10 ${date}`, content };
    if (sha) body.sha = sha;

    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error((await res.json()).message);
    statusEl.textContent = `\u2713 Saved \u2014 ${path}`;
    statusEl.className = 'text-sm text-green-600';
  } catch(e) {
    statusEl.textContent = `\u2717 ${e.message}`;
    statusEl.className = 'text-sm text-red-600';
  }
  statusEl.classList.remove('hidden');
  btn.disabled = false; btn.textContent = 'Save Meeting Notes';
}

function renderL10() {
  const l10       = window.DASHBOARD_DATA.l10;
  const rocks     = window.DASHBOARD_DATA.rocks;
  const scorecard = window.DASHBOARD_DATA.scorecard;

  const SECTION_COLOR = [
    'border-l-blue-400', 'border-l-purple-400', 'border-l-green-400',
    'border-l-yellow-400', 'border-l-orange-400', 'border-l-red-400', 'border-l-gray-400',
  ];

  const today = new Date().toISOString().split('T')[0];
  const ownerOpts = l10.attendees.map(a =>
    `<option value="${a}">${a.split(' ')[0]}</option>`).join('');

  let html = `
    <div class="mb-4 flex flex-wrap items-center gap-3">
      <div class="flex items-center gap-2 text-sm">
        <span class="font-medium text-gray-700">${l10.schedule}</span>
        <span class="text-gray-400">&middot;</span>
        <span class="text-gray-500">${l10.attendees.join(', ')}</span>
      </div>
      <div class="ml-auto flex flex-wrap items-center gap-3">
        <input type="date" id="meeting_date" value="${today}"
          class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
        <button onclick="saveMeeting()" id="save_btn"
          class="bg-blue-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-blue-700 transition-colors">
          Save Meeting Notes
        </button>
        <span id="save_status" class="text-sm hidden"></span>
      </div>
    </div>
    <div class="space-y-3">`;

  l10.sections.forEach((sec, idx) => {
    const border = SECTION_COLOR[idx] || 'border-l-gray-300';
    let body = '';

    if (sec.num === 1) {
      body = `<ul class="mt-3 space-y-2">`;
      l10.attendees.forEach((a, i) => {
        body += `<li class="flex items-start gap-2">
          <div class="mt-1 shrink-0">${ownerChip(a)}</div>
          <textarea id="segue_${i}" rows="2"
            class="flex-1 border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            placeholder="Personal + professional good news\u2026"></textarea>
        </li>`;
      });
      body += `</ul>`;

    } else if (sec.num === 2) {
      body = `<div class="mt-3 overflow-x-auto"><table class="w-full text-sm border-collapse">
        <thead><tr class="border-b border-gray-200">
          <th class="text-left py-1.5 pr-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Metric</th>
          <th class="text-left py-1.5 pr-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Owner</th>
          <th class="text-left py-1.5 pr-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Goal</th>
          <th class="text-left py-1.5 pr-4 text-xs font-semibold text-gray-500 uppercase tracking-wider w-28">Actual</th>
          <th class="text-left py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider w-28">Status</th>
        </tr></thead>
        <tbody class="divide-y divide-gray-100">`;
      scorecard.forEach((m, i) => {
        body += `<tr>
          <td class="py-2 pr-4 text-gray-800">${m.metric}</td>
          <td class="py-2 pr-4">${ownerChip(m.owner)}</td>
          <td class="py-2 pr-4 text-gray-500">${m.goal}</td>
          <td class="py-2 pr-4">
            <input type="text" id="sc_${i}_actual" placeholder="\u2014"
              class="w-full border border-gray-200 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          </td>
          <td class="py-2">
            <select id="sc_${i}_status"
              class="w-full border border-gray-200 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">\u2014</option>
              <option value="green">\uD83D\uDFE2 Green</option>
              <option value="red">\uD83D\uDD34 Red</option>
            </select>
          </td>
        </tr>`;
      });
      body += `</tbody></table></div>`;

    } else if (sec.num === 3) {
      body = `<div class="mt-3 overflow-x-auto"><table class="w-full text-sm border-collapse">
        <thead><tr class="border-b border-gray-200">
          <th class="text-left py-1.5 pr-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Rock</th>
          <th class="text-left py-1.5 pr-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Owner</th>
          <th class="text-left py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider w-36">Status</th>
        </tr></thead>
        <tbody class="divide-y divide-gray-100">`;
      rocks.forEach((r, i) => {
        body += `<tr>
          <td class="py-2 pr-4 text-gray-800">${r.title}</td>
          <td class="py-2 pr-4">${ownerChip(r.owner)}</td>
          <td class="py-2">
            <select id="rock_${i}_status"
              class="w-full border border-gray-200 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="on_track" ${r.status === 'on_track' ? 'selected' : ''}>\uD83D\uDFE2 On Track</option>
              <option value="off_track" ${r.status !== 'on_track' ? 'selected' : ''}>\uD83D\uDD34 Off Track</option>
            </select>
          </td>
        </tr>`;
      });
      body += `</tbody></table></div>`;

    } else if (sec.num === 4) {
      body = `<textarea id="headlines" rows="3"
        class="mt-3 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
        placeholder="- Customer news&#10;- Employee news&#10;- Anything the team needs to know"></textarea>`;

    } else if (sec.num === 5) {
      body = `<div class="mt-3 flex items-center gap-3">
        <label class="text-sm text-gray-600">Completion rate:</label>
        <input type="number" id="todo_rate" min="0" max="100"
          class="border border-gray-200 rounded px-2 py-1 text-sm w-20 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="0\u2013100">
        <span class="text-sm text-gray-400">% &nbsp;(target: 90%+)</span>
      </div>`;

    } else if (sec.num === 6) {
      body = `<div class="mt-3 space-y-3">`;
      for (let i = 0; i < 3; i++) {
        body += `<div class="bg-gray-50 rounded-lg p-3 space-y-2">
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Issue ${i+1}</div>
          <div>
            <label class="text-xs font-medium text-gray-500">Identify:</label>
            <input type="text" id="ids_${i}_identify"
              class="mt-1 w-full border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="What is the real root cause?">
          </div>
          <div>
            <label class="text-xs font-medium text-gray-500">Discuss:</label>
            <textarea id="ids_${i}_discuss" rows="2"
              class="mt-1 w-full border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              placeholder="Key points from discussion\u2026"></textarea>
          </div>
          <div>
            <label class="text-xs font-medium text-gray-500">Solve \u2014 To-Do:</label>
            <input type="text" id="ids_${i}_solve"
              class="mt-1 w-full border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Action \u2014 Owner \u2014 Due date">
          </div>
        </div>`;
      }
      body += `</div>`;

    } else if (sec.num === 7) {
      body = `<div class="mt-3 space-y-4">
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">New To-Dos</span>
            <button onclick="addTodo()" class="text-xs text-blue-600 hover:text-blue-800 font-medium">+ Add row</button>
          </div>
          <div class="space-y-1.5" id="todos_list">
            ${[0,1,2].map(() => `
            <div class="todo-row flex gap-2">
              <input type="text" class="todo-text flex-1 border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="To-Do">
              <select class="todo-owner border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-28">
                <option value="">Owner</option>${ownerOpts}
              </select>
              <input type="date" class="todo-due border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>`).join('')}
          </div>
        </div>
        <div>
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Cascading Messages</div>
          <textarea id="cascade" rows="2"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            placeholder="What needs to be communicated outside this room?"></textarea>
        </div>
        <div>
          <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Meeting Rating (target: 8+)</div>
          <div class="flex flex-wrap gap-3">
            ${l10.attendees.map((a, i) => `
            <div class="flex items-center gap-2">
              ${ownerChip(a)}
              <input type="number" id="rating_${i}" min="1" max="10"
                class="border border-gray-200 rounded px-2 py-1 text-sm w-14 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1\u201310">
            </div>`).join('')}
          </div>
        </div>
      </div>`;
    }

    html += `<div class="bg-white rounded-lg border border-gray-200 border-l-4 ${border} shadow-sm p-4">
      <div class="flex items-center justify-between mb-1">
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-gray-400 w-5">${sec.num}.</span>
          <h3 class="text-sm font-bold text-gray-900">${sec.title}</h3>
        </div>
        <span class="text-xs font-medium text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">${sec.minutes} min</span>
      </div>
      ${sec.desc ? `<p class="text-xs text-gray-400 italic ml-7">${sec.desc}</p>` : ''}
      ${body ? `<div class="ml-7">${body}</div>` : ''}
    </div>`;
  });

  html += '</div>';
  document.getElementById('panel-l10').innerHTML = html;
}

/* ── Strategic Planning ── */
let SP_EDIT_MODE = false;

function esc(s) {
  return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function renderStrategicPlanning() {
  const v = window.DASHBOARD_DATA.vision;
  const el = document.getElementById('panel-strategic-planning');
  if (!v || !Object.keys(v).length) {
    el.innerHTML = '<p class="text-sm text-gray-500 mt-4">V/TO not configured. Run <code>ceos-vto</code> to set your vision.</p>';
    return;
  }
  el.innerHTML = SP_EDIT_MODE ? buildSPEditForm(v) : buildSPView(v);
}

function buildSPView(v) {
  function card(color, title, body) {
    return `<div class="bg-white rounded-lg border border-gray-200 shadow-sm p-5" style="border-top:3px solid ${color}">
      <div class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">${title}</div>
      ${body}
    </div>`;
  }

  let html = `<div class="mb-4 flex justify-end">
    <button onclick="SP_EDIT_MODE=true;renderStrategicPlanning();"
      class="bg-white border border-gray-200 text-gray-600 rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-gray-50 transition-colors">
      Edit
    </button>
  </div>`;

  /* Row 1: Core Focus + 10-Year Target */
  const cfBody = `
    <p class="text-sm text-gray-700 leading-relaxed">${esc(v.core_focus?.purpose) || '—'}</p>
    <div class="border-t border-gray-100 mt-3 pt-3">
      <div class="text-xs font-medium text-gray-400 mb-1">Niche</div>
      <p class="text-sm text-gray-600 italic leading-relaxed">${esc(v.core_focus?.niche) || '—'}</p>
    </div>`;
  const tytBody = `<p class="text-sm font-medium text-gray-800 leading-relaxed">${esc(v.ten_year_target) || '—'}</p>`;

  html += `<div class="grid gap-4 sm:grid-cols-2 mb-4">
    ${card('#6366f1', 'Core Focus', cfBody)}
    ${card('#8b5cf6', '10-Year Target', tytBody)}
  </div>`;

  /* Row 2: Core Values */
  const CV_COLORS = ['#6366f1', '#a855f7', '#3b82f6', '#0ea5e9'];
  const cvCards = (v.core_values || []).map((cv, i) =>
    `<div class="bg-white rounded-lg border border-gray-200 shadow-sm p-4" style="border-top:3px solid ${CV_COLORS[i] || '#9ca3af'}">
      <div class="text-sm font-bold text-gray-900 mb-1">${esc(cv.name)}</div>
      <div class="text-xs text-gray-500 leading-relaxed">${esc(cv.desc)}</div>
    </div>`
  ).join('');
  html += `<div class="mb-4">
    <div class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Core Values</div>
    <div class="grid gap-3 sm:grid-cols-3">${cvCards}</div>
  </div>`;

  /* Row 3: 3-Year Picture + 1-Year Plan */
  const typItems = (v.three_year_picture || []).map(item => {
    if (item.type === 'labeled')
      return `<div class="flex gap-2 text-sm"><span class="font-medium text-gray-500 w-28 shrink-0">${esc(item.label)}:</span><span class="text-gray-700">${esc(item.value) || '—'}</span></div>`;
    if (item.type === 'header')
      return `<div class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-3 mb-1">${esc(item.label)}</div>`;
    return `<div class="flex gap-2 text-sm pl-2"><span class="text-gray-300 shrink-0">\u00b7</span><span class="text-gray-600">${esc(item.value)}</span></div>`;
  }).join('');

  const oypItems = (v.one_year_plan || []).map(item => {
    if (item.type === 'labeled')
      return `<div class="flex gap-2 text-sm"><span class="font-medium text-gray-500 w-28 shrink-0">${esc(item.label)}:</span><span class="text-gray-700">${esc(item.value) || '—'}</span></div>`;
    return `<div class="flex gap-2 text-sm"><span class="font-medium text-indigo-500 shrink-0">${esc(item.label)}:</span><span class="text-gray-700">${esc(item.value)}</span></div>`;
  }).join('');

  html += `<div class="grid gap-4 sm:grid-cols-2 mb-4">
    ${card('#10b981', '3-Year Picture (end of 2028)', `<div class="space-y-1.5">${typItems}</div>`)}
    ${card('#f97316', '1-Year Plan (end of 2026)',    `<div class="space-y-1.5">${oypItems}</div>`)}
  </div>`;

  /* Row 4: 3 Uniques + The Proven Process */
  const m = v.marketing || {};
  const uniquesItems = (m.uniques || []).map((u, i) =>
    `<div class="flex gap-3 text-sm">
      <span class="text-gray-300 font-medium shrink-0 w-4">${i + 1}.</span>
      <div><span class="font-medium text-gray-800">${esc(u.name)}:</span> <span class="text-gray-600">${esc(u.desc)}</span></div>
    </div>`
  ).join('');
  const uniquesBody = `
    ${m.target_market ? `<div class="mb-3 px-3 py-2 bg-gray-50 rounded text-xs text-gray-500 italic">${esc(m.target_market)}</div>` : ''}
    <div class="space-y-3">${uniquesItems}</div>`;

  const processItems = (m.process || []).map((p, i) =>
    `<div class="flex gap-3 text-sm">
      <span class="text-gray-300 font-medium shrink-0 w-4">${i + 1}.</span>
      <div><span class="font-medium text-gray-800">${esc(p.step)}:</span> <span class="text-gray-600">${esc(p.desc)}</span></div>
    </div>`
  ).join('');
  const processBody = `
    <div class="space-y-3">${processItems}</div>
    ${m.guarantee ? `<div class="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-400 italic">${esc(m.guarantee)}</div>` : ''}`;

  html += `<div class="grid gap-4 sm:grid-cols-2">
    ${card('#0ea5e9', '3 Uniques',          uniquesBody)}
    ${card('#14b8a6', 'The Proven Process', processBody)}
  </div>`;

  return html;
}

function buildSPEditForm(v) {
  const CV_COLORS = ['#6366f1', '#a855f7', '#3b82f6', '#0ea5e9'];
  const m = v.marketing || {};

  function ta(id, label, value, rows = 2, placeholder = '') {
    return `<div>
      <label class="text-xs font-medium text-gray-500 block mb-1">${label}</label>
      <textarea id="${id}" rows="${rows}" placeholder="${esc(placeholder)}"
        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y">${esc(value)}</textarea>
    </div>`;
  }
  function inp(id, label, value, placeholder = '') {
    return `<div>
      <label class="text-xs font-medium text-gray-500 block mb-1">${label}</label>
      <input type="text" id="${id}" value="${esc(value)}" placeholder="${esc(placeholder)}"
        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
    </div>`;
  }
  function card(color, title, body) {
    return `<div class="bg-white rounded-lg border border-gray-200 shadow-sm p-5" style="border-top:3px solid ${color}">
      <div class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">${title}</div>
      <div class="space-y-3">${body}</div>
    </div>`;
  }

  /* Toolbar */
  let html = `<div class="mb-5 flex items-center gap-3">
    <button onclick="saveVision()" id="sp_save_btn"
      class="bg-blue-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-blue-700 transition-colors">
      Save Changes
    </button>
    <button onclick="SP_EDIT_MODE=false;renderStrategicPlanning();"
      class="bg-white border border-gray-200 text-gray-600 rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-gray-50 transition-colors">
      Cancel
    </button>
    <span id="sp_save_status" class="text-sm hidden"></span>
  </div>`;

  /* Row 1: Core Focus + 10-Year Target */
  const cfEdit = `
    ${ta('sp_purpose', 'Purpose / Cause / Passion', v.core_focus?.purpose || '', 3)}
    ${ta('sp_niche',   'Niche',                     v.core_focus?.niche   || '', 3)}`;
  const tytEdit = ta('sp_ten_year_target', 'Target', v.ten_year_target || '', 3);
  html += `<div class="grid gap-4 sm:grid-cols-2 mb-4">
    ${card('#6366f1', 'Core Focus',     cfEdit)}
    ${card('#8b5cf6', '10-Year Target', tytEdit)}
  </div>`;

  /* Row 2: Core Values */
  const cvEdits = (v.core_values || []).map((cv, i) =>
    `<div class="bg-white rounded-lg border border-gray-200 shadow-sm p-4 space-y-2" style="border-top:3px solid ${CV_COLORS[i] || '#9ca3af'}">
      ${inp(`sp_cv_name_${i}`, 'Name', cv.name)}
      ${ta( `sp_cv_desc_${i}`, 'Description', cv.desc, 2)}
    </div>`
  ).join('');
  html += `<div class="mb-4">
    <div class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Core Values</div>
    <div class="grid gap-3 sm:grid-cols-3">${cvEdits}</div>
  </div>`;

  /* Row 3: 3-Year Picture + 1-Year Plan */
  const labeled3yr  = (v.three_year_picture || []).filter(x => x.type === 'labeled');
  const bullets3yr  = (v.three_year_picture || []).filter(x => x.type === 'bullet').map(x => x.value).join('\n');
  const rev3yr      = labeled3yr.find(x => x.label === 'Revenue')?.value    || '';
  const prof3yr     = labeled3yr.find(x => x.label === 'Profit')?.value     || '';
  const hc3yr       = labeled3yr.find(x => x.label === 'Head count')?.value || '';

  const typEdit = `
    ${inp('sp_3yr_revenue',   'Revenue',    rev3yr,  'e.g. $10M ARR')}
    ${inp('sp_3yr_profit',    'Profit',     prof3yr, 'e.g. $2M')}
    ${inp('sp_3yr_headcount', 'Head count', hc3yr,   'e.g. 20')}
    ${ta( 'sp_3yr_bullets',   'What does it look like? (one item per line)', bullets3yr, 4)}`;

  const labeled1yr  = (v.one_year_plan || []).filter(x => x.type === 'labeled');
  const goals1yr    = (v.one_year_plan || []).filter(x => x.type === 'goal').map(x => x.value).join('\n');
  const rev1yr      = labeled1yr.find(x => x.label === 'Revenue goal')?.value || '';
  const prof1yr     = labeled1yr.find(x => x.label === 'Profit goal')?.value  || '';

  const oypEdit = `
    ${inp('sp_1yr_revenue', 'Revenue goal', rev1yr,  'e.g. $2M ARR')}
    ${inp('sp_1yr_profit',  'Profit goal',  prof1yr, 'e.g. Break-even')}
    ${ta( 'sp_1yr_goals',   'Goals for the year (one per line)', goals1yr, 4)}`;

  html += `<div class="grid gap-4 sm:grid-cols-2 mb-4">
    ${card('#10b981', '3-Year Picture (end of 2028)', typEdit)}
    ${card('#f97316', '1-Year Plan (end of 2026)',    oypEdit)}
  </div>`;

  /* Row 4: 3 Uniques + Manifest Method */
  const uniquesEdit = `
    ${ta('sp_target_market', 'Target Market', m.target_market || '', 2)}
    ${(m.uniques || []).map((u, i) => `
    <div class="bg-gray-50 rounded-lg p-3 space-y-2">
      <div class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Unique ${i + 1}</div>
      ${inp(`sp_unique_name_${i}`, 'Name', u.name)}
      ${ta( `sp_unique_desc_${i}`, 'Description', u.desc, 2)}
    </div>`).join('')}`;

  const processEdit = `
    ${(m.process || []).map((p, i) => `
    <div class="bg-gray-50 rounded-lg p-3 space-y-2">
      <div class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Step ${i + 1}</div>
      ${inp(`sp_process_step_${i}`, 'Step name', p.step)}
      ${ta( `sp_process_desc_${i}`, 'Description', p.desc, 2)}
    </div>`).join('')}
    ${inp('sp_guarantee', 'Guarantee', m.guarantee || '')}`;

  html += `<div class="grid gap-4 sm:grid-cols-2">
    ${card('#0ea5e9', '3 Uniques',          uniquesEdit)}
    ${card('#14b8a6', 'The Proven Process', processEdit)}
  </div>`;

  return html;
}

function buildVisionMarkdown() {
  const v  = window.DASHBOARD_DATA.vision;
  const m  = v.marketing || {};
  const today = new Date().toISOString().split('T')[0];

  const val = id => (document.getElementById(id)?.value || '').trim();
  const lines = id => val(id).split('\n').map(l => l.trim()).filter(Boolean);

  let md = `# Vision/Traction Organizer\n\n## Your Company\n\n*Last updated: ${today}*\n\n---\n\n`;

  /* Core Values */
  md += `## Core Values\n\n*The guiding principles that define our culture. We hire, fire, and reward based on these.*\n\n`;
  (v.core_values || []).forEach((_, i) => {
    const name = val(`sp_cv_name_${i}`);
    const desc = val(`sp_cv_desc_${i}`);
    if (name) md += `${i + 1}. **${name}** \u2014 ${desc}\n`;
  });
  md += `\n---\n\n`;

  /* Core Focus */
  md += `## Core Focus\n\n*Our sweet spot \u2014 the intersection of our passion and our niche.*\n\n`;
  md += `**Purpose / Cause / Passion:**\n> ${val('sp_purpose')}\n\n`;
  md += `**Niche:**\n> ${val('sp_niche')}\n\n---\n\n`;

  /* 10-Year Target */
  md += `## 10-Year Target\n\n*One big, audacious goal. Specific enough to know when we\u2019ve hit it.*\n\n`;
  md += `> ${val('sp_ten_year_target')}\n\n---\n\n`;

  /* Marketing Strategy */
  md += `## Marketing Strategy\n\n**Target Market:**\n> ${val('sp_target_market')}\n\n`;
  md += `**3 Uniques:**\n`;
  (m.uniques || []).forEach((_, i) => {
    const name = val(`sp_unique_name_${i}`);
    const desc = val(`sp_unique_desc_${i}`);
    if (name) md += `${i + 1}. **${name}:** ${desc}\n`;
  });
  md += `\n**Proven Process \u2014 The Proven Process:**\n`;
  (m.process || []).forEach((_, i) => {
    const step = val(`sp_process_step_${i}`);
    const desc = val(`sp_process_desc_${i}`);
    if (step) md += `${i + 1}. **${step}** \u2014 ${desc}\n`;
  });
  md += `\n**Guarantee:**\n> ${val('sp_guarantee')}\n\n---\n\n`;

  /* 3-Year Picture */
  md += `## 3-Year Picture\n\n*What does Your Company look like by end of 2028?*\n\n`;
  md += `- **Revenue:** ${val('sp_3yr_revenue')}\n`;
  md += `- **Profit:** ${val('sp_3yr_profit')}\n`;
  md += `- **Head count:** ${val('sp_3yr_headcount')}\n`;
  md += `- **What does it look like?**\n`;
  lines('sp_3yr_bullets').forEach(b => { md += `  - ${b}\n`; });
  md += `\n---\n\n`;

  /* 1-Year Plan */
  md += `## 1-Year Plan\n\n*What must be true by end of 2026 to stay on track for the 3-Year Picture?*\n\n`;
  md += `- **Revenue goal:** ${val('sp_1yr_revenue')}\n`;
  md += `- **Profit goal:** ${val('sp_1yr_profit')}\n\n`;
  md += `**Goals for 2026:**\n`;
  lines('sp_1yr_goals').forEach((g, i) => { md += `${i + 1}. ${g}\n`; });
  md += `\n---\n\n`;

  /* Static trailing sections */
  md += `## Quarterly Rocks\n\n*See \`data/rocks/\` for current quarter\u2019s Rocks.*\n\n`;
  md += `[This section is managed by the \`ceos-rocks\` skill. Run "show our rocks" to see current status.]\n\n---\n\n`;
  md += `## Issues List\n\n*See \`data/issues/\` for the current Issues List.*\n\n`;
  md += `[This section is managed by the \`ceos-ids\` skill. Run "show our issues" to see open issues.]\n`;

  return md;
}

async function saveVision() {
  const token    = window.GITHUB_TOKEN;
  const repo     = window.GITHUB_REPO;
  const path     = 'data/vision.md';
  const btn      = document.getElementById('sp_save_btn');
  const statusEl = document.getElementById('sp_save_status');

  btn.disabled = true; btn.textContent = 'Saving\u2026';
  statusEl.className = 'text-sm hidden';

  try {
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (!res.ok) throw new Error('Could not read vision.md');
    const { sha } = await res.json();

    const md  = buildVisionMarkdown();
    const put = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({ message: 'update: vision/traction organizer', content: b64encode(md), sha })
    });
    if (!put.ok) throw new Error((await put.json()).message);

    /* Sync in-memory data so view mode reflects the save immediately */
    const v = window.DASHBOARD_DATA.vision;
    const m = v.marketing || {};
    const val   = id => (document.getElementById(id)?.value || '').trim();
    const lines = id => val(id).split('\n').map(l => l.trim()).filter(Boolean);

    (v.core_values || []).forEach((cv, i) => {
      cv.name = val(`sp_cv_name_${i}`) || cv.name;
      cv.desc = val(`sp_cv_desc_${i}`) || cv.desc;
    });
    v.core_focus.purpose = val('sp_purpose');
    v.core_focus.niche   = val('sp_niche');
    v.ten_year_target    = val('sp_ten_year_target');

    v.three_year_picture = [
      { type: 'labeled', label: 'Revenue',    value: val('sp_3yr_revenue')   },
      { type: 'labeled', label: 'Profit',     value: val('sp_3yr_profit')    },
      { type: 'labeled', label: 'Head count', value: val('sp_3yr_headcount') },
      { type: 'header',  label: 'What does it look like', value: '' },
      ...lines('sp_3yr_bullets').map(b => ({ type: 'bullet', label: '', value: b })),
    ];
    v.one_year_plan = [
      { type: 'labeled', label: 'Revenue goal', value: val('sp_1yr_revenue') },
      { type: 'labeled', label: 'Profit goal',  value: val('sp_1yr_profit')  },
      ...lines('sp_1yr_goals').map((g, i) => ({ type: 'goal', label: `Goal ${i + 1}`, value: g })),
    ];
    m.target_market = val('sp_target_market');
    (m.uniques  || []).forEach((u, i) => { u.name = val(`sp_unique_name_${i}`) || u.name; u.desc = val(`sp_unique_desc_${i}`) || u.desc; });
    (m.process  || []).forEach((p, i) => { p.step = val(`sp_process_step_${i}`) || p.step; p.desc = val(`sp_process_desc_${i}`) || p.desc; });
    m.guarantee = val('sp_guarantee');

    SP_EDIT_MODE = false;
    renderStrategicPlanning();

  } catch(e) {
    statusEl.textContent = '\u2717 ' + e.message;
    statusEl.className = 'text-sm text-red-600';
    statusEl.classList.remove('hidden');
    btn.disabled = false; btn.textContent = 'Save Changes';
  }
}

/* ── Market Calendar ── */
let CAL_EDITING = null; // null = view | 'new' = add form | integer = edit index

const CAL_TYPE_CLS = {
  'partner':     'bg-purple-100 text-purple-800',
  'market':      'bg-blue-100 text-blue-800',
  'fundraising': 'bg-yellow-100 text-yellow-800',
  'constraint':  'bg-red-100 text-red-800',
};
const CAL_TYPE_LABELS = {
  'partner': 'Partner', 'market': 'Market', 'fundraising': 'Fundraising', 'constraint': 'Constraint',
};
const CAL_TYPES = ['partner', 'market', 'fundraising', 'constraint'];

function calTypeBadge(type) {
  const cls = CAL_TYPE_CLS[type] || 'bg-gray-100 text-gray-700';
  const label = CAL_TYPE_LABELS[type] || type;
  return `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${cls}">${label}</span>`;
}

function buildCalendarViewRow(e, idx) {
  const d = new Date(e.date + 'T00:00:00');
  const day = d.getDate();
  const isPast = e.status === 'past';
  const isCancelled = e.status === 'cancelled';
  const dim = isPast || isCancelled;
  const now = new Date();
  const twoWeeks = new Date(now); twoWeeks.setDate(twoWeeks.getDate() + 14);
  const soon = !dim && d <= twoWeeks && d >= now;

  return `<div class="flex items-start gap-4 bg-white rounded-lg border ${soon ? 'border-blue-300 ring-1 ring-blue-100' : 'border-gray-200'} shadow-sm p-3 ${dim ? 'opacity-50' : ''}">
    <div class="text-center shrink-0 w-10">
      <div class="text-lg font-bold ${dim ? 'text-gray-400' : 'text-gray-800'}">${day}</div>
    </div>
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-sm font-semibold ${dim ? 'text-gray-400' : 'text-gray-900'} ${isCancelled ? 'line-through' : ''}">${esc(e.event)}</span>
        ${calTypeBadge(e.type)}
        ${isCancelled ? '<span class="text-xs text-gray-400">(cancelled)</span>' : ''}
      </div>
      <div class="flex items-center gap-2 mt-1">
        ${ownerChip(e.owner)}
        ${e.notes ? `<span class="text-xs text-gray-400">${esc(e.notes)}</span>` : ''}
      </div>
    </div>
    <button onclick="CAL_EDITING=${idx};renderCalendar();"
      class="text-gray-400 hover:text-gray-600 text-xs px-1.5 py-0.5 rounded hover:bg-gray-100 transition-colors shrink-0"
      title="Edit event">\u270E</button>
  </div>`;
}

function buildCalendarEditCard(e, idx) {
  const isNew    = e === null;
  const date     = isNew ? '' : e.date;
  const event    = isNew ? '' : e.event;
  const type     = isNew ? 'market' : e.type;
  const owner    = isNew ? '' : e.owner;
  const status   = isNew ? 'upcoming' : e.status;
  const notes    = isNew ? '' : e.notes;

  const pfx = isNew ? 'cal_new' : `cal_edit_${idx}`;
  const typeOpts = CAL_TYPES.map(t =>
    `<option value="${t}" ${t === type ? 'selected' : ''}>${CAL_TYPE_LABELS[t]}</option>`).join('');
  const ownerOpts = TEAM_MEMBERS.concat(['Team']).map(n =>
    `<option value="${n}" ${n === owner ? 'selected' : ''}>${n}</option>`).join('');
  const statusOpts = ['upcoming', 'past', 'cancelled'].map(s =>
    `<option value="${s}" ${s === status ? 'selected' : ''}>${s.charAt(0).toUpperCase() + s.slice(1)}</option>`).join('');

  const saveFn   = isNew ? 'createCalendarEvent()' : `saveCalendarEvent(${idx})`;
  const cancelFn = 'CAL_EDITING=null;renderCalendar();';

  return `<div class="bg-white rounded-lg border-2 border-blue-300 shadow-sm p-4 space-y-3">
    <div class="flex items-center justify-between gap-2 flex-wrap">
      <span class="text-xs font-semibold text-gray-400 uppercase tracking-widest">${isNew ? 'New Event' : 'Edit Event'}</span>
      <div class="flex gap-1.5">
        <button onclick="${saveFn}" id="${pfx}_btn"
          class="bg-blue-600 text-white rounded-lg px-3 py-1 text-xs font-medium hover:bg-blue-700 transition-colors">
          ${isNew ? 'Create' : 'Save'}
        </button>
        <button onclick="${cancelFn}"
          class="bg-white border border-gray-200 text-gray-600 rounded-lg px-3 py-1 text-xs font-medium hover:bg-gray-50 transition-colors">
          Cancel
        </button>
        ${!isNew ? `<button onclick="deleteCalendarEvent(${idx})"
          class="bg-white border border-red-200 text-red-500 rounded-lg px-3 py-1 text-xs font-medium hover:bg-red-50 transition-colors">
          Delete
        </button>` : ''}
      </div>
    </div>
    <div class="grid grid-cols-2 gap-2">
      <div>
        <label class="text-xs font-medium text-gray-500 block mb-1">Date</label>
        <input type="date" id="${pfx}_date" value="${esc(date)}"
          class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
      </div>
      <div>
        <label class="text-xs font-medium text-gray-500 block mb-1">Type</label>
        <select id="${pfx}_type"
          class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          ${typeOpts}
        </select>
      </div>
    </div>
    <div>
      <label class="text-xs font-medium text-gray-500 block mb-1">Event Name</label>
      <input type="text" id="${pfx}_event" value="${esc(event)}" placeholder="Event name"
        class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
    </div>
    <div class="grid grid-cols-2 gap-2">
      <div>
        <label class="text-xs font-medium text-gray-500 block mb-1">Owner</label>
        <select id="${pfx}_owner"
          class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">— select —</option>${ownerOpts}
        </select>
      </div>
      <div>
        <label class="text-xs font-medium text-gray-500 block mb-1">Status</label>
        <select id="${pfx}_status"
          class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          ${statusOpts}
        </select>
      </div>
    </div>
    <div>
      <label class="text-xs font-medium text-gray-500 block mb-1">Notes</label>
      <input type="text" id="${pfx}_notes" value="${esc(notes)}" placeholder="Brief context or outcome"
        class="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
    </div>
    <span id="${pfx}_status_msg" class="text-sm hidden"></span>
  </div>`;
}

function buildCalendarMarkdown() {
  const events = window.DASHBOARD_DATA.calendar;
  events.sort((a, b) => a.date.localeCompare(b.date));

  let md = `# Market Calendar\n\n## Your Company\n\n`;
  md += `*Rolling 6-month view of partner events, market events, fundraising milestones, and team constraints.*\n\n---\n\n`;
  md += `## How to Use\n\nTrack external events that affect quarterly planning and Rocks. Review monthly or during quarterly planning. Events outside the rolling window (3 months back, 3 months forward) are retained but hidden from the dashboard view.\n\n---\n\n`;
  md += `## Events\n\n`;
  md += `| Date | Event | Type | Owner | Status | Notes |\n`;
  md += `|------|-------|------|-------|--------|-------|\n`;
  events.forEach(e => {
    md += `| ${e.date} | ${e.event} | ${e.type} | ${e.owner} | ${e.status} | ${e.notes} |\n`;
  });
  return md;
}

async function saveCalendarEvent(idx) {
  const events   = window.DASHBOARD_DATA.calendar;
  const token    = window.GITHUB_TOKEN;
  const repo     = window.GITHUB_REPO;
  const pfx      = `cal_edit_${idx}`;
  const btn      = document.getElementById(`${pfx}_btn`);
  const statusEl = document.getElementById(`${pfx}_status_msg`);

  const date   = document.getElementById(`${pfx}_date`)?.value   || '';
  const event  = document.getElementById(`${pfx}_event`)?.value.trim()  || '';
  const type   = document.getElementById(`${pfx}_type`)?.value   || '';
  const owner  = document.getElementById(`${pfx}_owner`)?.value  || '';
  const status = document.getElementById(`${pfx}_status`)?.value || '';
  const notes  = document.getElementById(`${pfx}_notes`)?.value.trim()  || '';

  if (!event) { alert('Event name is required.'); return; }
  if (!date)  { alert('Date is required.'); return; }

  events[idx] = { date, event, type, owner, status, notes };

  btn.disabled = true; btn.textContent = 'Saving\u2026';
  statusEl.className = 'text-sm hidden';

  try {
    const path = 'data/calendar/events.md';
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (!res.ok) throw new Error('Could not read events.md');
    const { sha } = await res.json();

    const put = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({ message: `update event: ${event}`, content: b64encode(buildCalendarMarkdown()), sha })
    });
    if (!put.ok) throw new Error((await put.json()).message);

    CAL_EDITING = null;
    renderCalendar();
  } catch(e) {
    statusEl.textContent = '\u2717 ' + e.message;
    statusEl.className = 'text-sm text-red-600';
    statusEl.classList.remove('hidden');
    btn.disabled = false; btn.textContent = 'Save';
  }
}

async function createCalendarEvent() {
  const events   = window.DASHBOARD_DATA.calendar;
  const token    = window.GITHUB_TOKEN;
  const repo     = window.GITHUB_REPO;
  const btn      = document.getElementById('cal_new_btn');
  const statusEl = document.getElementById('cal_new_status_msg');

  const date   = document.getElementById('cal_new_date')?.value   || '';
  const event  = document.getElementById('cal_new_event')?.value.trim()  || '';
  const type   = document.getElementById('cal_new_type')?.value   || '';
  const owner  = document.getElementById('cal_new_owner')?.value  || '';
  const status = document.getElementById('cal_new_status')?.value || 'upcoming';
  const notes  = document.getElementById('cal_new_notes')?.value.trim()  || '';

  if (!event) { alert('Event name is required.'); return; }
  if (!date)  { alert('Date is required.'); return; }

  events.push({ date, event, type, owner, status, notes });
  events.sort((a, b) => a.date.localeCompare(b.date));

  btn.disabled = true; btn.textContent = 'Creating\u2026';
  statusEl.className = 'text-sm hidden';

  try {
    const path = 'data/calendar/events.md';
    let sha;
    const check = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (check.ok) sha = (await check.json()).sha;

    const body = { message: `add event: ${event}`, content: b64encode(buildCalendarMarkdown()) };
    if (sha) body.sha = sha;

    const put = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify(body)
    });
    if (!put.ok) throw new Error((await put.json()).message);

    CAL_EDITING = null;
    renderCalendar();
  } catch(e) {
    statusEl.textContent = '\u2717 ' + e.message;
    statusEl.className = 'text-sm text-red-600';
    statusEl.classList.remove('hidden');
    btn.disabled = false; btn.textContent = 'Create';
  }
}

async function deleteCalendarEvent(idx) {
  const events = window.DASHBOARD_DATA.calendar;
  const token  = window.GITHUB_TOKEN;
  const repo   = window.GITHUB_REPO;

  if (!confirm(`Delete \u201c${events[idx].event}\u201d?`)) return;

  events.splice(idx, 1);

  try {
    const path = 'data/calendar/events.md';
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (!res.ok) throw new Error('Could not read events.md');
    const { sha } = await res.json();

    const put = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({ message: 'remove calendar event', content: b64encode(buildCalendarMarkdown()), sha })
    });
    if (!put.ok) throw new Error((await put.json()).message);

    CAL_EDITING = null;
    renderCalendar();
  } catch(e) {
    alert('Failed to delete: ' + e.message);
    renderCalendar();
  }
}

function renderCalendar() {
  const events = window.DASHBOARD_DATA.calendar;
  const now = new Date();
  const threeBack = new Date(now); threeBack.setMonth(threeBack.getMonth() - 3);
  const threeFwd  = new Date(now); threeFwd.setMonth(threeFwd.getMonth() + 3);

  const visible = events.filter(e => {
    const d = new Date(e.date + 'T00:00:00');
    return d >= threeBack && d <= threeFwd;
  });

  const byMonth = {};
  visible.forEach((e, _) => {
    const key = e.date.substring(0, 7);
    const globalIdx = events.indexOf(e);
    (byMonth[key] = byMonth[key] || []).push({ e, idx: globalIdx });
  });

  const monthNames = ['January','February','March','April','May','June',
                      'July','August','September','October','November','December'];

  let html = `<div class="mb-4 flex justify-end">
    <button onclick="CAL_EDITING='new';renderCalendar();"
      class="bg-blue-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-blue-700 transition-colors">
      + Add Event
    </button>
  </div>`;

  if (CAL_EDITING === 'new') {
    html += `<div class="mb-6">${buildCalendarEditCard(null, 'new')}</div>`;
  }

  const sortedMonths = Object.keys(byMonth).sort();
  for (const ym of sortedMonths) {
    const [y, m] = ym.split('-');
    const list = byMonth[ym];

    html += `<div class="mb-6">
      <h2 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">
        ${monthNames[parseInt(m) - 1]} ${y}
      </h2>
      <div class="space-y-2">`;

    list.forEach(({ e, idx }) => {
      html += (CAL_EDITING === idx) ? buildCalendarEditCard(e, idx) : buildCalendarViewRow(e, idx);
    });

    html += '</div></div>';
  }

  if (sortedMonths.length === 0 && CAL_EDITING !== 'new') {
    html += `<p class="text-sm text-gray-500 mt-4">No events in the rolling 6-month window. Add market events to track conferences, launches, and deadlines.</p>`;
  }

  document.getElementById('panel-calendar').innerHTML = html;
}

/* ── Init ── */
renderRocks();
renderScorecard();
renderAccountability();
renderL10();
renderStrategicPlanning();
renderCalendar();
showTab('rocks');
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Password protection
# ---------------------------------------------------------------------------

LOGIN_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Company &middot; EOS Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center font-sans">
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8 w-full max-w-sm mx-4">
    <h1 class="text-lg font-bold text-gray-900 mb-1">Your Company</h1>
    <p class="text-sm text-gray-500 mb-6">EOS Leadership Dashboard</p>
    <input type="password" id="pw" placeholder="Password"
      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
      onkeydown="if(event.key==='Enter')unlock()">
    <button onclick="unlock()"
      class="w-full bg-blue-600 text-white rounded-lg px-3 py-2 text-sm font-medium hover:bg-blue-700 transition-colors">
      Enter
    </button>
    <p id="err" class="text-xs text-red-600 mt-2 hidden">Incorrect password.</p>
  </div>
<script>
const SALT = '__SALT__';
const NONCE = '__NONCE__';
const CT = '__CT__';

function b64(s) { return Uint8Array.from(atob(s), c => c.charCodeAt(0)); }

async function unlock() {
  const pw = document.getElementById('pw').value;
  try {
    const km = await crypto.subtle.importKey(
      'raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveKey']);
    const key = await crypto.subtle.deriveKey(
      { name: 'PBKDF2', salt: b64(SALT), iterations: 100000, hash: 'SHA-256' },
      km, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
    const plain = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: b64(NONCE) }, key, b64(CT));
    const html = new TextDecoder().decode(plain);
    sessionStorage.setItem('eos_key', JSON.stringify({salt: SALT, nonce: NONCE, ct: CT}));
    sessionStorage.setItem('eos_pw', pw);
    render(html);
  } catch {
    document.getElementById('err').classList.remove('hidden');
  }
}

function render(html) {
  document.open(); document.write(html); document.close();
}

async function autoUnlock() {
  const pw = sessionStorage.getItem('eos_pw');
  if (!pw) return;
  document.getElementById('pw').value = pw;
  await unlock();
}
autoUnlock();
</script>
</body>
</html>
"""


def protect_with_password(html, password):
    """Encrypt html with AES-256-GCM and wrap in a login page."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        print("WARNING: 'cryptography' not installed — skipping password protection.")
        print("         Run: pip install cryptography")
        return html

    salt  = os.urandom(32)
    nonce = os.urandom(12)
    key   = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    ct    = AESGCM(key).encrypt(nonce, html.encode("utf-8"), None)

    page = LOGIN_TEMPLATE
    page = page.replace("__SALT__",  base64.b64encode(salt).decode())
    page = page.replace("__NONCE__", base64.b64encode(nonce).decode())
    page = page.replace("__CT__",    base64.b64encode(ct).decode())
    return page


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build():
    os.makedirs(DOCS_DIR, exist_ok=True)

    all_rocks      = load_all_rocks()
    scorecard      = load_scorecard()
    accountability = load_accountability()
    l10            = load_l10()
    vision         = load_vision()
    calendar       = load_calendar()
    team_names, team_owner_cls = load_team()

    current_q = all_rocks["current_quarter"]
    rocks = all_rocks["rocks_by_quarter"].get(current_q, [])

    data = {
        "rocks":            rocks,
        "rocks_by_quarter": all_rocks["rocks_by_quarter"],
        "quarters":         all_rocks["quarters"],
        "current_quarter":  current_q,
        "scorecard":        scorecard,
        "accountability":   accountability,
        "l10":              l10,
        "vision":           vision,
        "calendar":         calendar,
    }

    now     = datetime.now(timezone.utc)
    quarter = current_q
    week    = now.isocalendar()[1]
    updated = now.strftime("%Y-%m-%d %H:%M UTC")

    html = HTML_TEMPLATE
    html = html.replace("__QUARTER__",  quarter)
    html = html.replace("__WEEK__",     str(week))
    html = html.replace("__UPDATED__",      updated)
    html = html.replace("__DATA_JSON__",    json.dumps(data, ensure_ascii=False))
    html = html.replace("__GITHUB_TOKEN__", os.environ.get("GITHUB_WRITE_TOKEN", ""))
    html = html.replace("__GITHUB_REPO__",  "owner/repo")
    html = html.replace("__TEAM_MEMBERS_JSON__", json.dumps(team_names))
    html = html.replace("__OWNER_CLS_JSON__",    json.dumps(team_owner_cls))

    password = os.environ.get("DASHBOARD_PASSWORD")
    if password:
        html = protect_with_password(html, password)
        print("  Password protection: enabled")
    else:
        print("  Password protection: disabled (set DASHBOARD_PASSWORD to enable)")

    out = os.path.join(DOCS_DIR, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Built: {out}")
    total_rocks = sum(len(r) for r in all_rocks["rocks_by_quarter"].values())
    print(f"  Rocks:          {total_rocks} across {len(all_rocks['quarters'])} quarter(s) (current: {current_q})")
    print(f"  Scorecard:      {len(scorecard)}")
    print(f"  Accountability: {len(accountability)}")
    print(f"  L10 sections:   {len(l10['sections'])}")
    print(f"  Vision:         {len(vision.get('core_values', []))} core values, {len(vision.get('one_year_plan', []))} 1-yr goals")
    print(f"  Calendar:       {len(calendar)} events")


if __name__ == "__main__":
    build()
