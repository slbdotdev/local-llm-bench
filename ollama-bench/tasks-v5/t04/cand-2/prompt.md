Inspect the provided Python source tree and locate where this behavior is implemented:

When the service begins shutting down, it refuses newly submitted jobs but continues running
the jobs already waiting, in their original first-in-first-out order, until none remain.

Create `answer.txt` in the sandbox with exactly three lines and no other format:

PATH: relative/path.py
LINES: first-last
EXPLANATION: one short sentence explaining the implementation

Use a path relative to the sandbox root. Cite the smallest contiguous line span that contains
the implementation of the behavior itself. Do not cite a caller, a helper declaration, a
configuration value, documentation, or a comment. The explanation must mention refusal of new
jobs, continued processing of waiting jobs, and preservation of arrival order. Do not include
any additional lines, headings, or markdown fences.
