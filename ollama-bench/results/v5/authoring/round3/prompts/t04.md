Inspect the supplied Python source tree and decide whether the current production request
path implements all of this behavior:

* A failed authentication attempt creates a block for that canonical user identity, lasting
  60 seconds from the failure.
* While that block is active, another attempt for the same identity is rejected before its
  credentials are verified.
* A successful authentication removes the block for that identity immediately, without
  removing blocks belonging to other identities.

Follow the call chain from the public request entry point through identity normalization,
decision logic, persistence, and response construction. The tree contains current runtime
modules, adapters, configuration, tests, and archived revisions. Judge implementation in
the current runtime path only: comments, documentation, test names, unused helpers, and
archived code are not proof. All three bullets must hold; a partial mechanism is not an
implementation.

Create `answer.txt` with exactly three logical lines, in exactly this order, and no headings
or markdown fences:

PATH: relative/path.py
LINES: first-last
EXPLANATION: one short sentence explaining the implementation

Use a path relative to the sandbox root. For a positive answer, cite one contiguous line span
in one current runtime file that contains the largest part of the implementation itself, not
a caller, helper declaration, configuration value, documentation, comment, or test. Mention
any other runtime modules needed in the one-sentence explanation. For a negative answer, use:

PATH: NONE
LINES: NONE
EXPLANATION: state plainly that the current runtime does not implement all three bullets

The line span must be written as two positive decimal line numbers, `first-last`, with first
no greater than last. Do not include any additional lines or formatting.
