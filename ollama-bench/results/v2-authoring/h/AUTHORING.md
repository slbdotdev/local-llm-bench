You are authoring benchmark tasks for a coding-agent benchmark. Read the two format
examples in ./examples/12_regex (fresh-code task) and ./examples/16_bugfix2 (bugfix task
with a seed/ dir and a sha256 hash check on the visible test file) BEFORE writing anything.

Create each task as a directory in the CURRENT directory, exactly in that format:

  <NN_name>/prompt.md   the task spec shown to the agent under test. Precise, unambiguous,
                        self-contained, names the exact file(s) and function signatures to
                        create. It MUST end with the literal line:
                        Write a few quick checks of your own and run them with `python`, then reply "done".
  <NN_name>/test.py     the HIDDEN grader. It is copied into the agent's directory only after
                        the agent has finished. It must print "PASS" and sys.exit(0) only when
                        every check passes, otherwise print "FAIL" followed by the list of
                        failing check names and sys.exit(1). Use the same collect-failures
                        style as the examples. Where possible include a randomised
                        differential test against a simple brute-force reference implemented
                        inside test.py itself (seeded with random.seed(...) so it is
                        deterministic). Standard library only. It must run in well under 60
                        seconds. Never test wall-clock timing, threading races, or anything
                        random/unseeded.
  <NN_name>/ref/        a correct reference solution: the file(s) a perfect agent would have
                        produced. Copying ref/ over the (optional) seed/ must make test.py PASS.
  <NN_name>/seed/       ONLY for bugfix/refactor tasks: the starting files placed in the
                        agent's directory before it starts. The seed alone must FAIL test.py.
                        For bugfix tasks include a visible test_*.py in seed/ that the agent
                        must not edit, and have test.py verify its sha256 (compute the real
                        hash and paste it in) plus run it, plus check extra hidden cases of
                        the same behaviours.

Hard requirements:
- Pure Python 3, standard library only, no network, no third-party packages.
- Difficulty target: HARD. A strong small model at LOW reasoning effort should fail these about half the time, while the same model reasoning carefully should pass. Pack in many interacting EDGE CASES where a hasty but plausible implementation is subtly wrong. Do not achieve this with volume of code -- keep solutions around 80-180 lines -- achieve it with corner cases,
  not volume of code. Each solution should be roughly 60-150 lines. Reward correctness on
  tricky corners (ordering, ties, nulls, error cases, precedence, boundaries), not typing speed.
- The spec in prompt.md must fully determine every behaviour the grader checks. If the
  grader checks it, the prompt must state it. No ambiguity, no hidden conventions.
- Deterministic. No timing, no threads, no randomness in the solution.

VALIDATE before you finish: run
    python selftest2.py .
in the current directory (selftest2.py is here; it treats every subdirectory as a task).
Ignore/expect complaints about the `examples` directory if any. Iterate until every task
you wrote reports `ref PASS` and (for seeded tasks) `seed FAIL (good)`.
Also re-read each prompt.md and confirm a careful reader could produce a solution that
passes your grader without seeing the grader.

When done, reply with a one-line summary per task saying what it tests.
