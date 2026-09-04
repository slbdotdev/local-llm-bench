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

Use paths relative to the sandbox root. For a positive answer, cite the smallest contiguous line
span containing the implementation itself, not a caller, helper declaration, configuration value,
documentation, or comment. Do not include additional lines, headings, or markdown fences.
