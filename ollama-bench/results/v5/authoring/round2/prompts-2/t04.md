Inspect the provided Python source tree and determine whether this behavior is implemented:

After a failed authentication attempt, the service should limit further attempts for that user
identity for 60 seconds, and a successful authentication should lift that identity-specific limit.

Create `answer.txt` with exactly three lines and no other format. If the behavior is implemented,
use:

PATH: relative/path.py
LINES: first-last
EXPLANATION: one short sentence explaining the implementation

If it is not implemented anywhere in the tree, use exactly this shape instead:

PATH: NONE
LINES: NONE
EXPLANATION: state plainly that no code implements the identity-specific timed limit and its reset after success

Use paths relative to the sandbox root. Do not include additional lines, headings, or markdown
fences.

For a positive answer, cite the implementation itself — not a caller, a helper declaration, a
configuration value, documentation, or a comment. Cite it as a single contiguous line span in one
file, using the span that contains the code doing the work. **If the implementation is split across
parts of a file that are not contiguous, or across more than one file, cite the single contiguous
span that contains the largest part of it**, and name the others in `EXPLANATION`. There is always
exactly one span to give, so "it is split" is never a reason to give more than one.
