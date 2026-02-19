# CEOS Cowork Integration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make CEOS work as both a Claude Code skills package and a Claude Cowork plugin, with git-based data sync across 5 users.

**Architecture:** The CEOS repo itself becomes a Cowork plugin by adding `.claude-plugin/plugin.json` and `commands/sync.md`. Existing `skills/ceos-*/SKILL.md` files already match the plugin skill format. A `/ceos:sync` slash command handles git pull/push with AI-assisted merge conflict resolution. `setup.sh` gains a `--cowork` flag for Cowork-specific setup.

**Tech Stack:** Bash (setup.sh), Markdown (skills, commands), JSON (plugin manifest), Git (sync)

---

## Context

- **Company:** Blue Orange Digital
- **Author:** Josh Miramant
- **Repo:** https://github.com/BlueOrangeDigital/ceos
- **Branch:** feat/coworkk
- **L10 meetings:** Monthly (not weekly standard EOS)
- **Monday sync:** 30-min abbreviated meeting every Monday
- **Team size:** 5 leadership team members (4 Cowork, 1 Code)
- **Sync content:** EOS data only (`data/`). Skills and templates are upstream/static.
- **Sync trigger:** Explicit `/ceos:sync` slash command
- **Conflict handling:** AI-assisted merge

---

### Task 1: Create plugin manifest

**Files:**
- Create: `.claude-plugin/plugin.json`

**Step 1: Create the plugin manifest directory and file**

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "ceos",
  "description": "Run EOS with AI — 16 skills for the Entrepreneurial Operating System",
  "version": "1.0.0",
  "author": {
    "name": "Josh Miramant"
  },
  "repository": "https://github.com/BlueOrangeDigital/ceos",
  "license": "MIT"
}
```

**Step 2: Verify plugin structure**

Run: `ls -la .claude-plugin/`
Expected: `plugin.json` exists

Run: `cat .claude-plugin/plugin.json | python3 -m json.tool`
Expected: Valid JSON, no errors

**Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "feat: add Cowork plugin manifest"
```

---

### Task 2: Create the /ceos:sync command

**Files:**
- Create: `commands/sync.md`

**Step 1: Create the sync command**

Create `commands/sync.md`:

```markdown
---
description: Sync EOS data with your team — pulls latest changes and pushes yours via git
---

# Sync EOS Data

You are syncing the team's EOS data via git. Follow these steps exactly.

## Step 1: Find the CEOS root

Search upward from the current directory for the `.ceos` marker file. If not found, stop and tell the user: "Not in a CEOS repository. Clone your CEOS repo and run setup.sh first."

Set `CEOS_ROOT` to the directory containing `.ceos`.

## Step 2: Check for local changes

Run: `git -C <CEOS_ROOT> status --porcelain -- data/`

If there are uncommitted changes in `data/`:

1. Show the user what changed:
   - Run `git -C <CEOS_ROOT> diff --stat -- data/` for modified files
   - Run `git -C <CEOS_ROOT> ls-files --others --exclude-standard -- data/` for new files
2. Summarize the changes in plain English (e.g., "You updated 2 rocks and added a new todo")
3. Stage and commit:
   ```
   git -C <CEOS_ROOT> add data/
   git -C <CEOS_ROOT> commit -m "sync: <brief description of changes>"
   ```

If no local changes, report: "No local changes to commit."

## Step 3: Pull latest from remote

Run: `git -C <CEOS_ROOT> pull --rebase origin main`

**If the pull succeeds cleanly:**
- Count incoming commits: compare HEAD before and after pull
- Report: "Pulled N changes from team."

**If there is a merge conflict:**
1. Run `git -C <CEOS_ROOT> diff --name-only --diff-filter=U` to find conflicted files
2. For EACH conflicted file:
   a. Read the file contents (it will contain conflict markers `<<<<<<<`, `=======`, `>>>>>>>`)
   b. Show the user BOTH versions clearly:
      - "Your version:" (content between `<<<<<<<` and `=======`)
      - "Team version:" (content between `=======` and `>>>>>>>`)
   c. Explain what each side changed in plain English
   d. Propose a merged version that combines both changes sensibly
   e. Ask: "Use this merged version? (yes / edit / pick mine / pick theirs)"
   f. Based on the user's choice, write the resolved file
   g. Run `git -C <CEOS_ROOT> add <file>`
3. After all conflicts are resolved: `git -C <CEOS_ROOT> rebase --continue`

**If the pull fails for another reason** (network, auth):
- Report the error and suggest: "Check your internet connection and git credentials. Try again with /ceos:sync"

## Step 4: Push to remote

Run: `git -C <CEOS_ROOT> push origin main`

**If push succeeds:**
- Count outgoing commits
- Report: "Pushed N changes to team."

**If push fails** (someone pushed while we were syncing):
- Report: "Remote has new changes. Running sync again..."
- Go back to Step 3

## Step 5: Summary

Display a final summary:

```
Sync complete.
  Pulled: N changes from team
  Pushed: M local changes
  Conflicts resolved: K files
```

If nothing happened: "Already up to date. No changes to sync."
```

**Step 2: Verify the command file exists and has valid frontmatter**

Run: `head -3 commands/sync.md`
Expected: Shows the YAML frontmatter with `description:`

**Step 3: Commit**

```bash
git add commands/sync.md
git commit -m "feat: add /ceos:sync command for git-based team data sync"
```

---

### Task 3: Extend setup.sh with --cowork flag

**Files:**
- Modify: `setup.sh`

**Step 1: Add Cowork detection and setup mode**

Add a new `install_cowork()` function after the existing `install_skills()` function. This function:
- Verifies the plugin manifest exists at `.claude-plugin/plugin.json`
- Verifies git remote is configured and accessible
- Prints Cowork-specific setup instructions (point working folder at repo)
- Skips the symlink step (Cowork reads skills directly from the plugin structure)

```bash
install_cowork() {
    echo "Setting up CEOS for Claude Cowork..."
    echo ""

    # Verify plugin manifest
    if [[ ! -f "$CEOS_ROOT/.claude-plugin/plugin.json" ]]; then
        echo "Error: Plugin manifest not found at .claude-plugin/plugin.json"
        echo "This CEOS version may not support Cowork. Pull the latest from upstream."
        exit 1
    fi

    # Verify git remote
    local remote_url
    remote_url="$(git -C "$CEOS_ROOT" remote get-url origin 2>/dev/null || echo "")"
    if [[ -z "$remote_url" ]]; then
        echo "Warning: No git remote 'origin' configured."
        echo "Set one with: git remote add origin <your-repo-url>"
        echo ""
    else
        echo "Git remote: $remote_url"
        # Test connectivity
        if git -C "$CEOS_ROOT" ls-remote --exit-code origin HEAD >/dev/null 2>&1; then
            echo "Remote access: ✓"
        else
            echo "Warning: Cannot reach remote. Check your credentials and network."
        fi
        echo ""
    fi

    echo "─────────────────────────────────────────────────"
    echo "  Cowork Setup"
    echo "─────────────────────────────────────────────────"
    echo ""
    echo "Skills are ready — Cowork reads them from the plugin structure."
    echo "No symlinks needed."
    echo ""
    echo "To use in Claude Cowork:"
    echo "  1. Open Cowork"
    echo "  2. Set your working folder to: $CEOS_ROOT"
    echo "  3. Try: /ceos:sync or \"Set rocks for this quarter\""
    echo ""
}
```

**Step 2: Add git remote verification to both install paths**

Add a `verify_git_remote()` function that both Code and Cowork paths call:

```bash
verify_git_remote() {
    local remote_url
    remote_url="$(git -C "$CEOS_ROOT" remote get-url origin 2>/dev/null || echo "")"
    if [[ -z "$remote_url" ]]; then
        echo ""
        echo "Note: No git remote configured. To sync with your team:"
        echo "  git remote add origin <your-repo-url>"
        echo ""
    fi
}
```

Call `verify_git_remote` at the end of both `install_skills` and `install_cowork`.

**Step 3: Update the main case statement and usage**

Add `--cowork` to the case statement:

```bash
case "${1:-}" in
    --help|-h)
        usage
        ;;
    --uninstall)
        uninstall_skills
        ;;
    --cowork)
        install_cowork
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
```

And add `init --cowork` combined mode:

```bash
    init)
        if [[ "${2:-}" == "--cowork" ]]; then
            init ""
            install_cowork
        elif [[ "${2:-}" == "--force" ]]; then
            init "--force"
        else
            init "${2:-}"
        fi
        ;;
```

Update the `usage()` function to include:

```
  ./setup.sh --cowork        Set up for Claude Cowork (no symlinks)
  ./setup.sh init --cowork   Guided setup + Cowork configuration
```

**Step 4: Test the setup script**

Run: `./setup.sh --help`
Expected: Shows `--cowork` option in usage

Run: `./setup.sh --cowork`
Expected: Shows Cowork setup instructions, verifies plugin manifest, checks git remote

**Step 5: Commit**

```bash
git add setup.sh
git commit -m "feat: extend setup.sh with --cowork flag for Cowork platform support"
```

---

### Task 4: Verify end-to-end plugin structure

**Files:**
- No new files — validation only

**Step 1: Verify plugin directory layout matches Cowork expectations**

Run: `find . -name "plugin.json" -o -name "SKILL.md" -o -name "sync.md" | sort`

Expected output should show:
```
./.claude-plugin/plugin.json
./commands/sync.md
./skills/ceos-accountability/SKILL.md
./skills/ceos-annual/SKILL.md
./skills/ceos-checkup/SKILL.md
./skills/ceos-clarity/SKILL.md
./skills/ceos-dashboard/SKILL.md
./skills/ceos-delegate/SKILL.md
./skills/ceos-ids/SKILL.md
./skills/ceos-kickoff/SKILL.md
./skills/ceos-l10/SKILL.md
./skills/ceos-people/SKILL.md
./skills/ceos-process/SKILL.md
./skills/ceos-quarterly-planning/SKILL.md
./skills/ceos-quarterly/SKILL.md
./skills/ceos-rocks/SKILL.md
./skills/ceos-scorecard/SKILL.md
./skills/ceos-todos/SKILL.md
./skills/ceos-vto/SKILL.md
```

**Step 2: Test Claude Code plugin loading**

Run: `claude --plugin-dir . --print-plugins 2>&1 | head -20` (or equivalent)

Verify the CEOS plugin is recognized and skills are listed.

**Step 3: Verify the sync command is accessible**

Run: `claude --plugin-dir . -p "/ceos:sync" --no-input 2>&1 | head -5`

Verify the command is recognized (may not execute fully without a git remote, but should not error on "unknown command").

---

## Execution notes

- Tasks 1-3 are independent and can be parallelized
- Task 4 depends on all prior tasks
- No tests to write — this is markdown/JSON/bash configuration, not application code
- The 16 existing SKILL.md files are NOT modified
