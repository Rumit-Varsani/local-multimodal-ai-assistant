# Git Worktree Setup for ForgeMind Development

## Why Worktrees?

Without worktrees, you must `git checkout` to switch between `main` and `server/dell-runtime`, which:
- slows down iteration
- risks losing uncommitted changes
- makes it hard to compare branches side-by-side

**Solution**: Use `git worktree` to have multiple working directories sharing the same `.git/` folder.

## Initial Setup (One-time)

### On Mac

```bash
cd ~/ai-project
git fetch origin
git worktree list
```

You should see only the main worktree:
```
/Users/rumitvarsani/ai-project  01c05ec [main]
```

### On Dell

Already done! Your current directory is the main worktree on `server/dell-runtime`.

```bash
cd E:\ai-server
git worktree list
```

Current state:
```
E:\ai-server  01c05ec [server/dell-runtime]
```

## Create Second Worktree (If Needed)

If you want side-by-side editing on the same machine, create a linked worktree:

### On Mac (example)

```bash
# From the main project directory
cd ~/ai-project
git worktree add ../ai-project-dell-runtime server/dell-runtime
```

Result:
```
~/ai-project              01c05ec [main]
~/ai-project-dell-runtime 01c05ec [server/dell-runtime]
```

Now you can edit both directories simultaneously!

### On Dell (if needed)

```bash
# From the main runtime directory
E:\ai-server
git worktree add E:\ai-server-main main
```

Result:
```
E:\ai-server          01c05ec [server/dell-runtime]
E:\ai-server-main     01c05ec [main]
```

## Recommended Workflow

### Mac Developer

```bash
# Always work in ~/ai-project (main)
cd ~/ai-project
git checkout feature/new-agent
git pull origin feature/new-agent
# edit, commit, push
git push origin feature/new-agent
```

Keep `~/ai-project` on `main` or active `feature/*` branch.

**Optional**: Create Dell worktree to test changes:
```bash
git worktree add ../ai-project-dell-runtime server/dell-runtime
# check Dell's runtime-specific settings without switching branches
```

### Dell Runtime

Current directory `E:\ai-server` is your runtime worktree on `server/dell-runtime`.

When you need to pull Mac's work:

```bash
git fetch origin main
git diff main  # review Mac's changes
git merge main  # merge tested work into your runtime branch
```

Or, if you want a separate directory for `main`:

```bash
git worktree add E:\ai-server-main main
cd E:\ai-server-main
git pull origin main
# review, test
cd ..\ai-server
git merge ..\ai-server-main  # merge into runtime branch
```

## Cleanup

If you created extra worktrees and want to remove them:

```bash
git worktree remove ../ai-project-dell-runtime
# Removes the worktree but keeps the branch in git
```

Or with full cleanup:

```bash
git worktree remove --prune ../ai-project-dell-runtime
```

## Common Issues

### "worktree already locked"

If a worktree gets stuck:

```bash
git worktree lock ../ai-project-dell-runtime
git worktree unlock ../ai-project-dell-runtime
```

### Branch not available

```bash
git fetch origin
git worktree add E:\ai-server-new-feature origin/feature/new-feature
```

## Branch Reference

Current branches:

| Branch | Purpose | Maintainer |
|--------|---------|-----------|
| `main` | Stable, reviewed code | Both (Mac develops, Dell merges when ready) |
| `server/dell-runtime` | Runtime-specific tweaks, deployment | Dell |
| `feature/*` | Active development | Mac (typically) |

**Rule**: Each worktree stays on one predictable branch. Don't use the same worktree for multiple branches simultaneously.
