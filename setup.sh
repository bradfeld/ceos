#!/usr/bin/env bash
set -euo pipefail

# CEOS Setup Script
# Installs CEOS skills for Claude Code and optionally initializes EOS data.
#
# Usage:
#   ./setup.sh              Symlink skills to ~/.claude/skills/ (idempotent)
#   ./setup.sh init         Symlink skills + interactive guided setup
#   ./setup.sh --uninstall  Remove skill symlinks (data untouched)
#   ./setup.sh --help       Show this help message

# ─────────────────────────────────────────────────
# Find repo root
# ─────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$SCRIPT_DIR/.ceos" ]]; then
    echo "Error: Not in a CEOS repository (.ceos marker not found)."
    echo "Run this script from the ceos/ directory."
    exit 1
fi

CEOS_ROOT="$SCRIPT_DIR"
SKILLS_DIR="$HOME/.claude/skills"
SKILL_NAMES=()

# Discover skill directories
for skill_dir in "$CEOS_ROOT"/skills/ceos-*/; do
    [[ -d "$skill_dir" ]] || continue
    SKILL_NAMES+=("$(basename "$skill_dir")")
done

if [[ ${#SKILL_NAMES[@]} -eq 0 ]]; then
    echo "Error: No ceos-* skill directories found in $CEOS_ROOT/skills/"
    exit 1
fi

# ─────────────────────────────────────────────────
# Usage
# ─────────────────────────────────────────────────

usage() {
    cat <<'HELP'
CEOS — Claude + EOS

Usage:
  ./setup.sh              Install skill symlinks (idempotent)
  ./setup.sh init         Install skills + guided company setup
  ./setup.sh init --force Install skills + recreate data/ from scratch
  ./setup.sh --uninstall  Remove skill symlinks (data untouched)
  ./setup.sh --help       Show this help

What each mode does:
  (no args)    Links ceos-* skills into ~/.claude/skills/ so Claude Code
               can discover them. Safe to run multiple times.

  init         Runs the symlink step, then walks you through setting up
               your company's EOS data — company name, quarter, team
               members, and L10 meeting day. Creates data/ from templates.

  --uninstall  Removes the skill symlinks. Your data in data/ is not
               touched — you can re-install any time with ./setup.sh.
HELP
}

# ─────────────────────────────────────────────────
# Install skills (symlink phase)
# ─────────────────────────────────────────────────

install_skills() {
    echo "Installing CEOS skills..."
    echo ""

    mkdir -p "$SKILLS_DIR"

    local linked=0
    local skipped=0

    for skill in "${SKILL_NAMES[@]}"; do
        local target="$CEOS_ROOT/skills/$skill"
        local link="$SKILLS_DIR/$skill"

        if [[ -L "$link" ]]; then
            local existing
            existing="$(readlink "$link")"
            if [[ "$existing" == "$target" ]]; then
                echo "  [skip] $skill (already linked)"
                skipped=$((skipped + 1))
                continue
            else
                echo "  [update] $skill (was → $existing)"
                rm "$link"
            fi
        elif [[ -e "$link" ]]; then
            echo "  [warning] $link exists but is not a symlink — skipping"
            continue
        fi

        ln -s "$target" "$link"
        echo "  [linked] $skill"
        linked=$((linked + 1))
    done

    echo ""
    echo "Done. $linked linked, $skipped already up to date."
    echo "Skills directory: $SKILLS_DIR"
}

# ─────────────────────────────────────────────────
# Uninstall skills
# ─────────────────────────────────────────────────

uninstall_skills() {
    echo "Removing CEOS skill symlinks..."
    echo ""

    local removed=0

    for skill in "${SKILL_NAMES[@]}"; do
        local link="$SKILLS_DIR/$skill"

        if [[ -L "$link" ]]; then
            local existing
            existing="$(readlink "$link")"
            # Only remove if it points into this CEOS repo
            if [[ "$existing" == "$CEOS_ROOT/skills/$skill" ]]; then
                rm "$link"
                echo "  [removed] $skill"
                removed=$((removed + 1))
            else
                echo "  [skip] $skill (points to $existing, not this repo)"
            fi
        else
            echo "  [skip] $skill (no symlink found)"
        fi
    done

    echo ""
    echo "Done. Removed $removed skill links."
    echo "Your data in data/ is untouched."
}

# ─────────────────────────────────────────────────
# Template substitution helper
# ─────────────────────────────────────────────────

substitute() {
    local src="$1"
    local dest="$2"

    # Use a temp file for portability (avoids macOS vs GNU sed -i differences)
    sed \
        -e "s|{{company_name}}|${COMPANY_NAME}|g" \
        -e "s|{{date}}|${TODAY}|g" \
        -e "s|{{quarter}}|${QUARTER}|g" \
        -e "s|{{quarter_end}}|${QUARTER_END}|g" \
        -e "s|{{team_members}}|${TEAM_MEMBERS}|g" \
        -e "s|{{week}}|${WEEK}|g" \
        "$src" > "$dest"
}

# ─────────────────────────────────────────────────
# Calculate quarter end date from YYYY-QN
# ─────────────────────────────────────────────────

quarter_end_date() {
    local q="$1"
    local year="${q%%-*}"
    local qnum="${q##*Q}"

    case "$qnum" in
        1) echo "${year}-03-31" ;;
        2) echo "${year}-06-30" ;;
        3) echo "${year}-09-30" ;;
        4) echo "${year}-12-31" ;;
        *) echo ""; return 1 ;;
    esac
}

# ─────────────────────────────────────────────────
# Calculate current quarter from today's date
# ─────────────────────────────────────────────────

current_quarter() {
    local month
    month="$(date +%m)"
    local year
    year="$(date +%Y)"

    # Remove leading zero for arithmetic
    month="${month#0}"

    if [[ $month -le 3 ]]; then
        echo "${year}-Q1"
    elif [[ $month -le 6 ]]; then
        echo "${year}-Q2"
    elif [[ $month -le 9 ]]; then
        echo "${year}-Q3"
    else
        echo "${year}-Q4"
    fi
}

# ─────────────────────────────────────────────────
# Interactive init
# ─────────────────────────────────────────────────

init() {
    local force=false
    if [[ "${1:-}" == "--force" ]]; then
        force=true
    fi

    # Check for existing data/
    if [[ -d "$CEOS_ROOT/data" ]] && [[ "$force" != true ]]; then
        echo "data/ directory already exists."
        echo ""
        echo "To start fresh, run:  ./setup.sh init --force"
        echo "(This will replace all files in data/ with fresh templates.)"
        echo ""
        echo "To just re-install skills, run:  ./setup.sh"
        exit 1
    fi

    if [[ -d "$CEOS_ROOT/data" ]] && [[ "$force" == true ]]; then
        echo "Re-initializing data/ (--force)..."
        rm -rf "$CEOS_ROOT/data"
    fi

    # ── Prompts ──

    echo ""
    echo "Welcome to CEOS — let's set up your company's EOS data."
    echo ""

    # Company name (required)
    local company_name=""
    while [[ -z "$company_name" ]]; do
        printf "Company name: "
        read -r company_name
        if [[ -z "$company_name" ]]; then
            echo "  Company name is required."
        fi
    done

    # Quarter (with smart default)
    local default_quarter
    default_quarter="$(current_quarter)"
    printf "Current quarter [%s]: " "$default_quarter"
    read -r quarter_input
    local quarter="${quarter_input:-$default_quarter}"

    # Validate quarter format
    if [[ ! "$quarter" =~ ^[0-9]{4}-Q[1-4]$ ]]; then
        echo "Error: Quarter must be in YYYY-QN format (e.g., 2026-Q1)."
        exit 1
    fi

    # Team members
    printf "Leadership team members (comma-separated names): "
    read -r team_members

    # L10 meeting day
    printf "L10 meeting day [Tuesday]: "
    read -r l10_input
    local l10_day="${l10_input:-Tuesday}"

    # ── Derived variables ──

    COMPANY_NAME="$company_name"
    QUARTER="$quarter"
    QUARTER_END="$(quarter_end_date "$quarter")"
    TEAM_MEMBERS="$team_members"
    TODAY="$(date +%Y-%m-%d)"
    WEEK="$(date +%Y)-W$(date +%V)"

    # ── Install skills first ──

    install_skills
    echo ""

    # ── Create data directory structure ──

    echo "Creating EOS data structure..."
    echo ""

    mkdir -p "$CEOS_ROOT/data"
    mkdir -p "$CEOS_ROOT/data/rocks/$QUARTER"
    mkdir -p "$CEOS_ROOT/data/scorecard/weeks"
    mkdir -p "$CEOS_ROOT/data/issues/open"
    mkdir -p "$CEOS_ROOT/data/issues/solved"
    mkdir -p "$CEOS_ROOT/data/todos"
    mkdir -p "$CEOS_ROOT/data/meetings/l10"
    mkdir -p "$CEOS_ROOT/data/meetings/kickoff"
    mkdir -p "$CEOS_ROOT/data/processes"
    mkdir -p "$CEOS_ROOT/data/people"
    mkdir -p "$CEOS_ROOT/data/conversations"
    mkdir -p "$CEOS_ROOT/data/annual"
    mkdir -p "$CEOS_ROOT/data/quarterly"
    mkdir -p "$CEOS_ROOT/data/checkups"
    mkdir -p "$CEOS_ROOT/data/delegate"
    mkdir -p "$CEOS_ROOT/data/clarity"
    mkdir -p "$CEOS_ROOT/data/assistance/stack"
    mkdir -p "$CEOS_ROOT/data/assistance/daily"
    mkdir -p "$CEOS_ROOT/data/lma"
    mkdir -p "$CEOS_ROOT/data/trust"
    mkdir -p "$CEOS_ROOT/data/cashflow"
    mkdir -p "$CEOS_ROOT/data/calendar"

    # ── Copy and substitute templates ──

    substitute "$CEOS_ROOT/templates/vision.md" "$CEOS_ROOT/data/vision.md"
    echo "  [created] data/vision.md"

    substitute "$CEOS_ROOT/templates/accountability.md" "$CEOS_ROOT/data/accountability.md"
    echo "  [created] data/accountability.md"

    substitute "$CEOS_ROOT/templates/scorecard-metrics.md" "$CEOS_ROOT/data/scorecard/metrics.md"
    echo "  [created] data/scorecard/metrics.md"

    substitute "$CEOS_ROOT/templates/calendar-events.md" "$CEOS_ROOT/data/calendar/events.md"
    echo "  [created] data/calendar/events.md"

    echo ""
    echo "─────────────────────────────────────────────────"
    echo "  CEOS is ready for $COMPANY_NAME!"
    echo "─────────────────────────────────────────────────"
    echo ""
    echo "Your EOS data lives in: $CEOS_ROOT/data/"
    echo ""
    echo "Quick start — try these with Claude Code:"
    echo ""
    echo "  \"Review our V/TO\"          → opens data/vision.md"
    echo "  \"Set rocks for $QUARTER\"    → creates rocks in data/rocks/$QUARTER/"
    echo "  \"Log this week's scorecard\" → creates data/scorecard/weeks/$WEEK.md"
    echo "  \"Run our L10\"              → creates data/meetings/l10/$TODAY.md"
    echo "  \"We have an issue with X\"  → creates data/issues/open/issue-NNN.md"
    echo ""
    echo "L10 meeting day: $l10_day"
    echo ""

    # Remind about fork setup if this looks like upstream
    if git remote get-url origin 2>/dev/null | grep -q "bradfeld/ceos"; then
        echo "Note: You're on the upstream repo (bradfeld/ceos)."
        echo "For your company, fork this repo and commit data/ to your fork."
        echo "See CONTRIBUTING.md for the fork workflow."
        echo ""
    fi
}

# ─────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────

case "${1:-}" in
    --help|-h)
        usage
        ;;
    --uninstall)
        uninstall_skills
        ;;
    init)
        init "${2:-}"
        ;;
    "")
        install_skills
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        usage
        exit 1
        ;;
esac
