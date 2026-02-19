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
