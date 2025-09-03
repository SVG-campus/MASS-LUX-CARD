#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

git lfs track "*.png" "*.jpg" "*.jpeg" "*.webp" >/dev/null 2>&1 || true
if ! grep -q "filter=lfs" .gitattributes 2>/dev/null; then
  printf '%s\n' \
  '*.png filter=lfs diff=lfs merge=lfs -text' \
  '*.jpg filter=lfs diff=lfs merge=lfs -text' \
  '*.jpeg filter=lfs diff=lfs merge=lfs -text' \
  '*.webp filter=lfs diff=lfs merge=lfs -text' >> .gitattributes
  git add .gitattributes
fi

git add -A
git commit -m "auto: prompts/renders + CSV $(date -u +'%Y-%m-%dT%H:%M:%SZ')" || true
git push -u origin main
