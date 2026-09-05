#!/bin/bash
# usage: publish.sh "<lowercase message>"
# Commits results/prompt-v1/ in the scratch clone, then mirrors it into
# /mnt/d/local-llm-bench and commits there. Only that one directory is ever staged.
set -u
MSG="$1"
SRC=/home/slb/bench-prompt
DST=/mnt/d/local-llm-bench
REL=ollama-bench/results/prompt-v1

retry_git() {  # retry on an index lock, 5 x 30 s
  local i
  for i in 1 2 3 4 5; do
    if "$@"; then return 0; fi
    if [ -f "$DST/.git/index.lock" ]; then
      echo "publish: index lock held, retry $i/5 in 30 s"; sleep 30; continue
    fi
    return 1
  done
  return 1
}

cd "$SRC" || exit 9
cp -f /mnt/c/Users/slb/bench-prompt-variants/*.md /mnt/c/Users/slb/bench-prompt-variants/*.ts \
      /mnt/c/Users/slb/bench-prompt-variants/mkvariant.sh "$REL/variants/" 2>/dev/null
rm -f "$REL/variants/chained-capture.md"
git add "$REL" || exit 1
git diff --cached --quiet || git commit -q -m "$MSG" || exit 1
echo "publish: scratch $(git log --oneline -1)"

cd "$DST" || exit 9
retry_git git fetch -q origin || echo "publish: fetch failed, continuing"
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
if [ "${BEHIND:-0}" -gt 0 ]; then
  # Never --autostash: the other campaign has live uncommitted result files in this tree.
  retry_git git pull -q --rebase || { echo "publish: behind by $BEHIND and cannot rebase (other campaign has unstaged work); skipping this publish"; exit 2; }
fi
mkdir -p "$REL"
rsync -a --delete "$SRC/$REL/" "$DST/$REL/" || exit 1
retry_git git add "$REL" || exit 1
if git diff --cached --quiet; then echo "publish: nothing new in $DST"; else
  retry_git git commit -q -m "$MSG" || exit 1
fi
retry_git git push -q || { echo "publish: push failed"; exit 1; }
echo "publish: shared $(git log --oneline -1)"
