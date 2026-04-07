# Automated Workflow

## Purpose

This repo now supports one simple automated workflow:

- MacBook edits and pushes to GitHub
- Dell server syncs from GitHub and runs the backend
- GitHub stays the single source of truth

## Scripts

### On Mac

Use [mac_push_main.sh](/Users/rumitvarsani/ai-project/scripts/mac_push_main.sh) after you already committed your changes:

```bash
./scripts/mac_push_main.sh
```

What it does:

- checks that you are on `main`
- refuses to run if you still have uncommitted changes
- fast-forwards from `origin/main`
- pushes `main` to GitHub

### On Dell

Use [dell_sync_main.sh](/Users/rumitvarsani/ai-project/scripts/dell_sync_main.sh):

```bash
./scripts/dell_sync_main.sh
```

What it does:

- refuses to run if Dell has local uncommitted changes
- switches to `main` if needed
- fetches from GitHub
- resets Dell `main` to exactly match `origin/main`

This is correct for a runtime-only machine.

If Dell runs Windows/PowerShell, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dell_sync_main.ps1
```

### On either machine

Use [runtime_status.sh](/Users/rumitvarsani/ai-project/scripts/runtime_status.sh):

```bash
./scripts/runtime_status.sh
```

It shows:

- current branch
- git status
- ahead/behind count vs `origin/main`
- diff summary
- configured worktrees

## Local runtime worktree

If you want a second local view of the runtime code on this Mac, create it with:

```bash
./scripts/setup_runtime_worktree.sh
```

This creates:

- `worktrees/runtime-main`

That worktree is a detached checkout of `origin/main`, useful for:

- side-by-side comparison
- reading a runtime snapshot locally
- letting the assistant inspect the stable runtime view

## Recommended daily flow

### Mac

1. edit code
2. test code
3. commit code
4. run `./scripts/mac_push_main.sh`

### Dell

1. run `./scripts/dell_sync_main.sh`
2. run `./scripts/run_server_dell.sh`

If Dell runs Windows, use the PowerShell versions documented in [windows-dell-runtime.md](/Users/rumitvarsani/ai-project/docs/windows-dell-runtime.md).

## Important rule

Do not keep important code changes only on Dell.

If Dell changes are not on GitHub, they are not part of the real project state from the Mac side.
