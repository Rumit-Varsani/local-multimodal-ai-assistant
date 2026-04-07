#!/bin/bash

set -euo pipefail

target_dir="${1:-worktrees/runtime-main}"

mkdir -p "$(dirname "$target_dir")"

if [[ -e "$target_dir" ]]; then
  echo "Worktree path already exists: $target_dir"
  exit 1
fi

git fetch origin
git worktree add --detach "$target_dir" origin/main

echo "Created runtime worktree at $target_dir"
echo "This worktree is a detached runtime view of origin/main."
