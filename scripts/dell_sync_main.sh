#!/bin/bash

set -euo pipefail

branch="$(git rev-parse --abbrev-ref HEAD)"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Refusing to sync: Dell working tree is not clean."
  echo "Run 'git status' and resolve local changes before syncing."
  exit 1
fi

if [[ "$branch" != "main" ]]; then
  echo "Switching to main..."
  git checkout main
fi

echo "Fetching latest code from GitHub..."
git fetch origin

echo "Resetting Dell runtime copy to origin/main..."
git reset --hard origin/main

echo "Dell runtime is now exactly synced to origin/main."
