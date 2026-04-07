#!/bin/bash

set -euo pipefail

branch="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$branch" != "main" ]]; then
  echo "Refusing to push: current branch is '$branch', expected 'main'."
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Refusing to push: you still have uncommitted changes."
  echo "Commit your work first, then run this script again."
  exit 1
fi

echo "Fetching latest origin/main..."
git fetch origin

echo "Fast-forwarding local main..."
git pull --ff-only origin main

echo "Pushing local main to GitHub..."
git push origin main

echo "Mac push complete."
