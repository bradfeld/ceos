#!/usr/bin/env python3
"""Build the Manifest AI EOS Leadership Dashboard.

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


def parse_outcome(body):
    """Extract measurable outcome text (strips blockquote markers)."""
    m = re.search(r'##\s+Measurable Outcome\s*\n+(.*?)(?=\n##|\Z)', body, re.DOTALL)
    if not m:
        return ''
    text = m.group(1).strip()
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    return text.strip()


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
        rocks.append({
            "id":         fm.get("id", os.path.basename(path)),
            "title":      fm.get("title", ""),
            "owner":      fm.get("owner", ""),
            "quarter":    fm.get("quarter", quarter),
            "status":     fm.get("status", "on_track"),
            "created":    str(fm.get("created", "")),
            "due":        str(fm.get("due", "")),
            "outcome":    parse_outcome(body),
            "milestones": parse_milestones(body),
            "file":       os.path.relpath(path, ROOT).replace(os.sep, "/"),
        })
    return rocks


def load_scorecard():
    """Parse the metrics table from data/scorecard/metrics.md."""
    path = os.path.join(DATA_DIR, "scorecard", "metrics.md")
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
    with open(path, encoding="utf-8") as f:
        text = f.read()

    SKIP_HEADINGS = {"Meridian Labs", "How to Use This Chart"}
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


def load_l10():
    """Parse the L10 standing agenda into structured sections."""
    path = os.path.join(DATA_DIR, "meetings", "l10", "agenda.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Meeting meta from header block
    schedule = ""
    attendees = []
    for line in text.splitlines()[:6]:
        line = line.strip("* ")
        if any(d in line for d in ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")) or "minutes" in line.lower():
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


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Meridian Labs &middot; EOS Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen font-sans">

<!-- ── Header ── -->
<header class="bg-white border-b border-gray-200 shadow-sm">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
    <div>
      <h1 class="text-xl font-bold text-gray-900">Meridian Labs <span class="ml-2 text-xs font-medium bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full align-middle">Demo</span></h1>
      <p class="text-sm text-gray-500">EOS Leadership Dashboard &middot; __QUARTER__ &middot; <span class="italic">Anonymized example data</span></p>
    </div>
    <div class="text-right">
      <div class="text-sm font-semibold text-gray-700">Week __WEEK__</div>
      <div class="text-xs text-gray-400">Updated __UPDATED__</div>
    </div>
  </div>
</header>

<!-- ── Main ── -->
<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 mt-6 pb-16">

  <!-- Tab bar -->
  <div class="flex space-x-1 bg-white border border-gray-200 rounded-lg p-1 mb-6 w-fit">
    <button onclick="showTab('rocks')"          id="tab-rocks"          class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">Rocks</button>
    <button onclick="showTab('scorecard')"      id="tab-scorecard"      class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">Scorecard</button>
    <button onclick="showTab('accountability')" id="tab-accountability" class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">Accountability Chart</button>
    <button onclick="showTab('l10')"            id="tab-l10"            class="tab-btn px-4 py-2 rounded-md text-sm font-medium transition-colors duration-100">L10 Agenda</button>
  </div>

  <div id="panel-rocks"></div>
  <div id="panel-scorecard"></div>
  <div id="panel-accountability"></div>
  <div id="panel-l10"></div>
</div>

<script>
/* ── Data ── */
window.DASHBOARD_DATA = __DATA_JSON__;
window.GITHUB_TOKEN = '__GITHUB_TOKEN__';
window.GITHUB_REPO  = '__GITHUB_REPO__';

/* ── Owner chip colors (literal strings so Tailwind CDN scans them) ── */
const OWNER_CLS = {
  'Alex Rivera':   'bg-blue-100 text-blue-800',
  'Jordan Chen':   'bg-purple-100 text-purple-800',
  'Morgan Taylor': 'bg-green-100 text-green-800',
  'Sam Patel':     'bg-orange-100 text-orange-800',
  'Casey Williams':'bg-pink-100 text-pink-800',
};

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
  ['rocks', 'scorecard', 'accountability', 'l10'].forEach(t => {
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


function addEditMilestone(ri) {
  const list = document.getElementById('re_milestones_' + ri);
  const row  = document.createElement('div');
  row.className = 're-milestone-row flex items-center gap-2 mt-1';
  row.innerHTML = `
    <input type="checkbox" class="re-milestone-done w-3.5 h-3.5 shrink-0 rounded border-gray-300 text-blue-600">
    <input type="text" class="re-milestone-text flex-1 border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400" placeholder="New milestone…">
    <button onclick="this.closest('.re-milestone-row').remove()" class="text-gray-300 hover:text-red-400 leading-none px-0.5">&times;</button>`;
  list.appendChild(row);
}

function showRockEdit(ri) {
  const rock   = window.DASHBOARD_DATA.rocks[ri];
  const owners = [...new Set(window.DASHBOARD_DATA.rocks.map(r => r.owner))];
  const ownerOpts = owners.map(o =>
    `<option value="${o}" ${o === rock.owner ? 'selected' : ''}>${o}</option>`
  ).join('');

  // Span all grid columns so the expanded form isn't covered by adjacent cards
  const card = document.getElementById('rock_card_' + ri);
  card.style.gridColumn = '1 / -1';

  let msHtml = '';
  rock.milestones.forEach(m => {
    const safeText = m.text.replace(/&/g,'&amp;').replace(/"/g,'&quot;');
    msHtml += `<div class="re-milestone-row flex items-center gap-2 mt-1">
      <input type="checkbox" class="re-milestone-done w-3.5 h-3.5 shrink-0 rounded border-gray-300 text-blue-600" ${m.done ? 'checked' : ''}>
      <input type="text" class="re-milestone-text flex-1 border border-gray-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400" value="${safeText}">
      <button onclick="this.closest('.re-milestone-row').remove()" class="text-gray-300 hover:text-red-400 leading-none px-0.5">&times;</button>
    </div>`;
  });

  const safeTitle   = (rock.title   || '').replace(/&/g,'&amp;').replace(/"/g,'&quot;');
  const safeOutcome = (rock.outcome || '').replace(/&/g,'&amp;').replace(/</g,'&lt;');

  document.getElementById('rock_card_' + ri).innerHTML = `
    <div class="space-y-3">
      <input id="re_title_${ri}" type="text" value="${safeTitle}"
        class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
      <div class="flex gap-2">
        <select id="re_owner_${ri}"
          class="flex-1 border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400">
          ${ownerOpts}
          <option value="__custom__">Other…</option>
        </select>
        <input id="re_due_${ri}" type="date" value="${rock.due}"
          class="border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400">
        <select id="re_status_${ri}"
          class="border border-gray-200 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400">
          <option value="on_track"  ${rock.status === 'on_track'  ? 'selected' : ''}>🟢 On Track</option>
          <option value="off_track" ${rock.status === 'off_track' ? 'selected' : ''}>🔴 Off Track</option>
        </select>
      </div>
      <div>
        <div class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Measurable Outcome</div>
        <textarea id="re_outcome_${ri}" rows="3"
          class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-400 resize-y"
          placeholder="Measurable outcome…">${safeOutcome}</textarea>
      </div>
      <div>
        <div class="flex items-center justify-between mb-1">
          <div class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Milestones</div>
          <button onclick="addEditMilestone(${ri})" class="text-xs text-blue-600 hover:text-blue-800 font-medium">+ Add</button>
        </div>
        <div id="re_milestones_${ri}">${msHtml}</div>
      </div>
      <div class="flex items-center justify-between pt-1">
        <button onclick="renderRocks()" class="text-sm text-gray-400 hover:text-gray-600">Cancel</button>
        <button id="re_save_${ri}" onclick="saveRock(${ri})"
          class="bg-blue-600 text-white rounded-lg px-4 py-1.5 text-sm font-medium hover:bg-blue-700 transition-colors">
          Save Rock
        </button>
      </div>
    </div>`;
}

async function saveRock(ri) {
  const rock  = window.DASHBOARD_DATA.rocks[ri];
  const token = window.GITHUB_TOKEN;
  const repo  = window.GITHUB_REPO;

  let newOwner = document.getElementById('re_owner_' + ri)?.value || rock.owner;
  if (newOwner === '__custom__') {
    newOwner = prompt('Enter owner name:') || rock.owner;
  }

  const newTitle   = document.getElementById('re_title_'   + ri)?.value.trim() || rock.title;
  const newDue     = document.getElementById('re_due_'     + ri)?.value         || rock.due;
  const newStatus  = document.getElementById('re_status_'  + ri)?.value         || rock.status;
  const newOutcome = document.getElementById('re_outcome_' + ri)?.value.trim()  || '';

  const newMilestones = [];
  document.querySelectorAll('#re_milestones_' + ri + ' .re-milestone-row').forEach(row => {
    const text = row.querySelector('.re-milestone-text')?.value.trim();
    const done = row.querySelector('.re-milestone-done')?.checked || false;
    if (text) newMilestones.push({ done, text });
  });

  const btn = document.getElementById('re_save_' + ri);
  if (btn) { btn.disabled = true; btn.textContent = 'Saving\u2026'; }

  try {
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (!res.ok) throw new Error('Could not read rock file');
    const data    = await res.json();
    const sha     = data.sha;
    const current = b64decode(data.content);

    // Preserve fields we don't edit
    const idMatch      = current.match(/^id:\s*(.+)$/m);
    const quarterMatch = current.match(/^quarter:\s*"?([^"\n]+)"?/m);
    const createdMatch = current.match(/^created:\s*"?([^"\n]+)"?/m);
    const rockId  = idMatch      ? idMatch[1].trim()      : rock.id;
    const quarter = quarterMatch ? quarterMatch[1].trim() : rock.quarter;
    const created = createdMatch ? createdMatch[1].trim() : (rock.created || '');

    // Preserve existing Notes section
    const notesMatch = current.match(/(## Notes[\s\S]*)$/);
    const notesBlock = notesMatch ? notesMatch[1].trimEnd() : '## Notes';

    const milestoneLines = newMilestones
      .map(m => `- [${m.done ? 'x' : ' '}] ${m.text}`)
      .join('\n');

    const updated =
`---
id: ${rockId}
title: "${newTitle}"
owner: "${newOwner}"
quarter: "${quarter}"
status: ${newStatus}
created: "${created}"
due: "${newDue}"
---

# ${newTitle}

## Measurable Outcome

> ${newOutcome}

## Milestones

${milestoneLines}

${notesBlock}
`;

    const put = await fetch(`https://api.github.com/repos/${repo}/contents/${rock.file}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json',
                 Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({
        message: `edit rock: ${newTitle}`,
        content: b64encode(updated),
        sha
      })
    });
    if (!put.ok) throw new Error((await put.json()).message);

    rock.title      = newTitle;
    rock.owner      = newOwner;
    rock.due        = newDue;
    rock.status     = newStatus;
    rock.outcome    = newOutcome;
    rock.milestones = newMilestones;
    renderRocks();
  } catch(e) {
    alert('Failed to save: ' + e.message);
    if (btn) { btn.disabled = false; btn.textContent = 'Save Rock'; }
  }
}

function renderRocks() {
  const rocks = window.DASHBOARD_DATA.rocks;
  const byOwner = {};
  rocks.forEach((r, ri) => { (byOwner[r.owner] = byOwner[r.owner] || []).push({r, ri}); });

  let html = '';
  for (const [owner, list] of Object.entries(byOwner)) {
    html += `<div class="mb-8">
      <h2 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">${owner}</h2>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">`;

    list.forEach(({r: rock, ri}) => {
      const on    = rock.status === 'on_track';
      const badgeCls = on
        ? 'shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700'
        : 'shrink-0 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700';
      const badgeText = on ? 'On Track' : 'Off Track';
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
              class="${m.done ? 'text-xs text-gray-400 line-through' : 'text-xs text-gray-600 leading-snug'} cursor-pointer select-none">${m.text}</label>
          </li>`;
      });
      milestoneList += `</ul>`;

      html += `<div id="rock_card_${ri}" class="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
        <div class="flex items-start justify-between gap-2 mb-1">
          <h3 class="text-sm font-semibold text-gray-900 leading-snug">${rock.title}</h3>
          <div class="shrink-0 flex items-center gap-1.5">
            <span id="rb_${ri}" class="${badgeCls}">${badgeText}</span>
            <button onclick="showRockEdit(${ri})" title="Edit rock"
              class="text-gray-300 hover:text-blue-500 transition-colors p-0.5 rounded">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 012.828 2.828L11.828 15.828a4 4 0 01-1.414.828l-3 1 1-3a4 4 0 01.828-1.414z"/>
              </svg>
            </button>
          </div>
        </div>
        <p class="text-xs text-gray-400 mb-3">Due ${rock.due}</p>
        <div class="flex justify-between text-xs text-gray-400 mb-1">
          <span>Milestones</span><span id="pc_${ri}">${done}/${total}</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-1.5 mb-3">
          <div id="pb_${ri}" class="bg-blue-500 h-1.5 rounded-full transition-all" style="width:${pct}%"></div>
        </div>
        ${milestoneList}
      </div>`;
    });

    html += '</div></div>';
  }
  document.getElementById('panel-rocks').innerHTML = html;
}

/* ── Scorecard ── */
function renderScorecard() {
  const metrics = window.DASHBOARD_DATA.scorecard;
  const headers = ['Metric', 'Owner', 'Goal', 'Frequency', 'Green', 'Red'];

  let html = `<div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-100">
      <thead class="bg-gray-50">
        <tr>${headers.map(h =>
          `<th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap">${h}</th>`
        ).join('')}</tr>
      </thead>
      <tbody class="divide-y divide-gray-100">`;

  metrics.forEach((m, i) => {
    html += `<tr class="${i % 2 ? 'bg-gray-50' : ''} hover:bg-blue-50">
      <td class="px-4 py-3 text-sm font-medium text-gray-900">${m.metric}</td>
      <td class="px-4 py-3 text-sm whitespace-nowrap">${ownerChip(m.owner)}</td>
      <td class="px-4 py-3 text-sm text-gray-600">${m.goal}</td>
      <td class="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">${m.frequency}</td>
      <td class="px-4 py-3 text-sm font-medium text-green-700 whitespace-nowrap">${m.green}</td>
      <td class="px-4 py-3 text-sm font-medium text-red-700 whitespace-nowrap">${m.red}</td>
    </tr>`;
  });

  html += '</tbody></table></div>';
  document.getElementById('panel-scorecard').innerHTML = html;
}

/* ── Accountability Chart ── */
function renderAccountability() {
  const seats = window.DASHBOARD_DATA.accountability;
  let html = '<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">';

  seats.forEach(seat => {
    const color  = SEAT_COLOR[seat.seat] || '#9ca3af';
    let roles = '<ol class="mt-3 space-y-1.5">';
    seat.roles.forEach(r => {
      roles += `<li class="text-sm text-gray-600 flex gap-2">
        <span class="text-gray-400 font-medium tabular-nums w-4 shrink-0">${r.num}.</span>
        <span>${r.role}</span>
      </li>`;
    });
    roles += '</ol>';

    html += `<div class="bg-white rounded-lg border border-gray-200 shadow-sm p-4" style="border-top: 4px solid ${color}">
      <h3 class="text-sm font-bold text-gray-900">${seat.seat}</h3>
      <div class="mt-1">${ownerChip(seat.owner)}</div>
      ${roles}
    </div>`;
  });

  html += '</div>';
  document.getElementById('panel-accountability').innerHTML = html;
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

  let md = `# Meridian Labs \u2014 L10 Meeting Notes\n\n`;
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

/* ── Init ── */
renderRocks();
renderScorecard();
renderAccountability();
renderL10();
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
  <title>Meridian Labs &middot; EOS Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center font-sans">
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8 w-full max-w-sm mx-4">
    <h1 class="text-lg font-bold text-gray-900 mb-1">Meridian Labs</h1>
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

    rocks          = load_rocks()
    scorecard      = load_scorecard()
    accountability = load_accountability()
    l10            = load_l10()

    data = {
        "rocks":          rocks,
        "scorecard":      scorecard,
        "accountability": accountability,
        "l10":            l10,
    }

    now     = datetime.now(timezone.utc)
    quarter = rocks[0]["quarter"] if rocks else "2026-Q1"
    week    = now.isocalendar()[1]
    updated = now.strftime("%Y-%m-%d %H:%M UTC")

    html = HTML_TEMPLATE
    html = html.replace("__QUARTER__",  quarter)
    html = html.replace("__WEEK__",     str(week))
    html = html.replace("__UPDATED__",      updated)
    html = html.replace("__DATA_JSON__",    json.dumps(data, ensure_ascii=False))
    html = html.replace("__GITHUB_TOKEN__", os.environ.get("GITHUB_WRITE_TOKEN", ""))
    html = html.replace("__GITHUB_REPO__",  "danieljforman/ceos-demo")

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
    print(f"  Rocks:          {len(rocks)}")
    print(f"  Scorecard:      {len(scorecard)}")
    print(f"  Accountability: {len(accountability)}")
    print(f"  L10 sections:   {len(l10['sections'])}")


if __name__ == "__main__":
    build()
