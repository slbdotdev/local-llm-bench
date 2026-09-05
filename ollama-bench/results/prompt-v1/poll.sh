#!/bin/bash
cd /home/slb/bench-prompt/ollama-bench/results/prompt-v1
for f in "$@"; do
  n=$(grep -cE "^  [a-z0-9]+ +#[0-9]+ (PASS|FAIL)" logs/$f.log 2>/dev/null)
  s=$(grep -E "^  [a-z0-9]+ +#[0-9]+ (PASS|FAIL)" logs/$f.log 2>/dev/null | awk '{printf "%s%s ", $1, ($3=="PASS"?"+":"-")}')
  o=""; [ -f logs/$f.outcome ] && o=" DONE($(grep rc= logs/$f.outcome))"
  printf "%-14s %2d/24%s  %s\n" "$f" "${n:-0}" "$o" "$s"
done
date -Is
