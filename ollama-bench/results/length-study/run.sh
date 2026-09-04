cd /c/Users/slb/ollama-bench
OUT=results/length-study
bash ~/.claude/skills/pi-run/scripts/pi-run --model z-ai/glm-5.3-flash --effort high --cwd /c/Users/slb/ollama-bench --timeout 3600 "$(cat $OUT/brief.md)" > $OUT/glm-stdout.md 2> $OUT/glm-stderr.log
echo "rc=$? $(date -Is)" >> $OUT/glm-stderr.log
echo STUDYDONE >> $OUT/glm-stderr.log