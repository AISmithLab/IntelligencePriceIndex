#!/usr/bin/env bash
# Redeploy the Intelligence Price Index website to GitHub Pages (gh-pages branch).
#
# What it does:
#   1. Regenerates site/data.json from the pipeline (code/15-build-site-data.py).
#   2. Publishes site/{index.html,ipi.js,data.json} (+ .nojekyll) to the root of an
#      orphan-style gh-pages branch via a scratch worktree — your current branch and
#      working tree are never touched.
#   3. Pushes gh-pages to origin (force-updates the single published commit).
#
# One-time setup (not done here — needs the repo's Pages setting):
#   Settings -> Pages -> Source: "Deploy from a branch" -> Branch: gh-pages / (root).
# Live at: https://aismithlab.github.io/IntelligencePriceIndex/
#
# Usage:  scripts/deploy-site.sh           # regenerate + publish
#         scripts/deploy-site.sh --no-build # publish existing site/ as-is
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SITE="$REPO/site"
WT="$(mktemp -d)/gh-pages-wt"
FILES=(index.html ipi.js data.json)

if [[ "${1:-}" != "--no-build" ]]; then
  echo "==> Regenerating site/data.json"
  python3 "$REPO/code/15-build-site-data.py"
fi

for f in "${FILES[@]}"; do
  [[ -f "$SITE/$f" ]] || { echo "ERROR: missing $SITE/$f (run without --no-build)"; exit 1; }
done

echo "==> Building gh-pages branch in a scratch worktree"
git -C "$REPO" worktree add --detach "$WT" HEAD --quiet
trap 'git -C "$REPO" worktree remove "$WT" --force >/dev/null 2>&1 || true' EXIT
(
  cd "$WT"
  git checkout --orphan gh-pages --quiet
  git rm -rf . --quiet
  for f in "${FILES[@]}"; do cp "$SITE/$f" .; done
  touch .nojekyll          # serve files raw, skip Jekyll
  git add -A
  git commit -q -m "Publish IPI website to GitHub Pages

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
  echo "==> Pushing gh-pages to origin"
  git push -f -u origin gh-pages
)
echo "==> Done. Live at https://aismithlab.github.io/IntelligencePriceIndex/ (allow ~1 min)"
