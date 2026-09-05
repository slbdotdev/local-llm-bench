# Review request: three benchmark graders, after one repair each

You are reviewing three Python grading scripts from a benchmark suite. Each grades a small
repository-editing exercise. Report findings only; **change no file**.

Working directory: `/mnt/d/local-llm-bench/ollama-bench/results/v7/authoring`

The three graders, each in its own candidate directory:

    cand-luna/m02-main-luna/test.py
    cand-luna/m05-main-luna/test.py
    cand-luna/m08-main-luna/test.py

Beside each `test.py` are `prompt.md` (the only thing the model under test sees), `seed/` (the
starting working directory), `ref/` (the reference answer) and `NOTES.md` (the author's own
account of what the task measures).

## What changed

Each of the three has a function `scope_is_clean()`. It was edited today. Nothing else in any of
the three files was edited, and no prompt, seed, reference or subcheck was touched.

## Method — do exactly this, in this order

Read each file whole, once. Do not read files in slices.

1. Read `prompt.md`, then `test.py`, for each of the three, in that order.
2. Run these two commands once each, at the end, from the working directory above. They build
   each candidate's own reference answer in a throwaway sandbox and grade it:

       python3 ../probe_scope_gate.py m02-main-luna m05-main-luna m08-main-luna
       python3 ../probe_scope_gate.py --breach m02-main-luna m05-main-luna m08-main-luna

   with the environment variable `V7_PROBE_BASE` set to
   `/mnt/d/local-llm-bench/ollama-bench/results/v7/authoring/cand-luna` for both, i.e.

       V7_PROBE_BASE=/mnt/d/local-llm-bench/ollama-bench/results/v7/authoring/cand-luna \
         python3 ../probe_scope_gate.py m02-main-luna m05-main-luna m08-main-luna

   `--breach` plants one extra file in the reference sandbox before grading. Run each command
   once. Do not run any other validator.

## Report exactly these four fields, per grader

1. **Is the scope check correct?** Specifically: does it accept a correct answer that touched
   nothing outside what its own `prompt.md` permits, and does it reject an answer that touched
   something the prompt forbids? Quote the sentence of `prompt.md` you are judging against.
2. **Is the check consistent with its own prompt's wording?** Say plainly whether the grader is
   stricter than the prompt, laxer than the prompt, or neither — and if stricter, name the exact
   behaviour it punishes that the prompt does not forbid.
3. **Does the grader still measure what `NOTES.md` says the task measures**, or did the edit
   change what is being measured?
4. **One concrete fix**, if you have one. If you have none, say none.

Then one final line: for each of the three, `ACCEPT` or `REVISE`.

Be concrete and short. Quote line numbers. Do not restate the code back to me.
