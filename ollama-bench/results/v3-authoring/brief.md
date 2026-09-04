# tasks-v3 authoring brief

Goal: benchmark tasks that sit right at the edge of what a strong 27B open-weights
model (Qwen3.8-27B) can do at LOW reasoning effort. Target difficulty: it gets the
task fully right roughly HALF the time. Too easy (always passes) and too hard
(never passes) are both useless.

## Task layout
tasks-v3/<NN_name>/
  prompt.md   the instruction given to the model under test (it works in an empty
              sandbox dir, or one pre-populated with seed/). The model runs a
              coding agent with file tools + python.
  test.py     HIDDEN grader, copied into the sandbox as _hidden_test.py AFTER the
              agent exits, then run with `python _hidden_test.py` with cwd=sandbox.
  ref/        reference solution files, copied over seed/ -- MUST make the grader PASS.
  seed/       optional starting files (for bugfix/refactor tasks).

## Grader contract (IMPORTANT)
- Must print a line `SCORE <n>/<m>` (n passed sub-checks of m) and then, as the LAST
  line of stdout, either `PASS` or `FAIL ...`.
- Exit 0 + final "PASS" only when n == m (full marks). Otherwise print FAIL and exit 1.
- Example ending:
      print(f"SCORE {m-len(fails)}/{m}")
      if fails: print("FAIL", fails[:10]); sys.exit(1)
      print("PASS")
- m should be >= 8 independent sub-checks so partial credit is informative. Group
  related asserts into sub-checks; do not make one behaviour worth 30 points and
  another worth 1.
- Deterministic, stdlib only, total runtime < 10 s. Seed any RNG. If the solution
  under test could loop forever, run it in a subprocess/thread with a timeout and
  count that as a failed sub-check rather than hanging the grader.
- The grader must ONLY test behaviour the prompt states or clearly implies. No trick
  questions, no hidden naming conventions. If the grader checks an edge case, the
  prompt must specify it.
- Import the candidate module inside try/except so a missing/broken file scores 0
  and still prints SCORE + FAIL rather than crashing with a traceback only.
- Prefer `subprocess`+`sys.executable` when testing a CLI; use absolute-ish cwd-relative
  paths only.

## Content rules
- Self-contained Python 3, standard library only, no network.
- Single-file deliverable, or a small bugfix/refactor over a seed of 1-3 files.
- The prompt must be unambiguous and fully specify names, signatures, output formats,
  and edge cases. Include 2-4 worked examples.
- End the prompt with: "Write a few quick checks of your own and run them with
  `python`, then reply \"done\"." (matches existing tasks' style)

## What made this model struggle before (good difficulty sources)
- Exact edge-case specs: CSV with CRLF inside quoted fields, strict Roman numeral
  validation, tie-breaking/stable ordering rules.
- Backtracking / termination correctness (empty-match quantifier loops).
- Small state machines and interpreters with precise error handling.
- Multi-file refactors that must preserve behaviour exactly.
- Bugfix tasks where the seed has 2-3 distinct bugs and the grader tests extra cases.
- Precise error types/messages (ValueError vs custom exception) on malformed input.
Avoid: heavy algorithms that are just LeetCode recall, anything needing >150 lines,
anything timing/concurrency-flaky.

## Before you report
Run:  cd ~/ollama-bench && PYTHONUTF8=1 python selftest2.py tasks-v3 <your task dirs>
It must show `ref PASS` for each of your tasks (and `seed FAIL (good)` for seeded ones).
Also sanity-check your grader's partial credit: an intentionally half-broken solution
should print an intermediate SCORE.
