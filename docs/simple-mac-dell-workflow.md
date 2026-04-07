# Simple Mac and Dell Workflow

## Goal

Keep the two machines very simple:

- **MacBook**: edit code, test code, commit, push to GitHub
- **Dell server**: pull latest code from GitHub and run the server only

## Rules

### MacBook rules

- this is the main development machine
- make code changes here
- test here
- commit here
- push here

### Dell server rules

- do not create new features by default
- do not make random git merges
- do not change branch strategy unless asked
- do not commit local experiments unless asked
- only pull the latest code from GitHub
- only run backend and future background workers

## Source of truth

GitHub is the source of truth.

That means:

1. you change code on the Mac
2. you push to GitHub
3. the Dell pulls from GitHub
4. the Dell runs the updated server

## Important limitation

The Mac assistant cannot automatically know Dell-only changes unless:

- those changes are pushed to GitHub, or
- you paste the Dell output here

So the safest rule is:

- **do not keep important code changes only on Dell**

## Daily workflow

### On Mac

```bash
git checkout main
git pull origin main
```

Make your code changes, then:

```bash
git add -A
git commit -m "your message"
git push origin main
```

### On Dell

```bash
git checkout main
git pull origin main
```

Then run the server.

## If you want a separate Dell branch later

Only do that if you really need server-only files.

For now the simplest setup is:

- both Mac and Dell use `main`
- Mac writes code
- Dell only pulls and runs

## What Dell chat should do

The Dell chat should help with:

- checking server status
- pulling latest code
- starting or restarting services
- reading logs
- verifying the backend is running

The Dell chat should not:

- create surprise commits
- resolve merges by itself
- rewrite branch structure by itself
- add docs or features unless you clearly ask for that
