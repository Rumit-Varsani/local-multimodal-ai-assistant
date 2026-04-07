#!/bin/bash

set -euo pipefail

echo "Repository: $(pwd)"
echo "Branch: $(git rev-parse --abbrev-ref HEAD)"
echo

echo "Git status:"
git status --short
echo

echo "Ahead/behind vs origin/main:"
git fetch origin --quiet
git rev-list --left-right --count origin/main...HEAD
echo "Format: behind ahead"
echo

echo "Diff summary vs origin/main:"
git diff --stat origin/main..HEAD || true
echo

echo "Configured worktrees:"
git worktree list
