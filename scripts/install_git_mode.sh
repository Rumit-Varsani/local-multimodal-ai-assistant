#!/bin/bash

set -euo pipefail

mode="${1:-}"

if [[ -z "$mode" ]]; then
  echo "Usage: bash ./scripts/install_git_mode.sh <mac-dev|dell-runtime>"
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
hooks_dir="$repo_root/.git/hooks"
source_dir="$repo_root/githooks/$mode"

if [[ ! -d "$source_dir" ]]; then
  echo "Unknown mode: $mode"
  echo "Expected one of: mac-dev, dell-runtime"
  exit 1
fi

mkdir -p "$hooks_dir"

for hook_name in pre-commit pre-push; do
  if [[ -f "$source_dir/$hook_name" ]]; then
    cp "$source_dir/$hook_name" "$hooks_dir/$hook_name"
    chmod +x "$hooks_dir/$hook_name"
  fi
done

echo "Installed git hook mode: $mode"
echo "Hooks copied into: $hooks_dir"
