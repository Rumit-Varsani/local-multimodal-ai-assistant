# Git Guards

## Purpose

These guards reduce the chance of mixing up the two machines:

- MacBook should be the coding machine
- Dell should be the runtime machine

## Install on Mac

```bash
bash ./scripts/install_git_mode.sh mac-dev
```

This allows normal commits and pushes on:

- `main`
- `feature/*`

## Install on Dell

```bash
bash ./scripts/install_git_mode.sh dell-runtime
```

This blocks:

- `git commit`
- `git push`

unless you explicitly override it.

## Dell override

If you truly need a one-time Dell commit:

```bash
FORGEMIND_ALLOW_DELL_COMMIT=1 git commit -m "message"
```

If you truly need a one-time Dell push:

```bash
FORGEMIND_ALLOW_DELL_PUSH=1 git push origin main
```

## Why this helps

If you change code on the Mac:

- commit and push normally
- Dell later syncs from GitHub

If you accidentally try to commit or push on Dell:

- the hooks block it
- the repo stays runtime-only

## Recommended flow

### Mac

```bash
bash ./scripts/install_git_mode.sh mac-dev
```

Then work normally:

```bash
git add -A
git commit -m "message"
./scripts/mac_push_main.sh
```

### Dell

```bash
bash ./scripts/install_git_mode.sh dell-runtime
bash ./scripts/dell_sync_main.sh
bash ./scripts/run_server_dell.sh
```
