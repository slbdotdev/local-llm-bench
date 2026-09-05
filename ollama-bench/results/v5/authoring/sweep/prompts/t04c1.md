Inspect the provided Python source tree and locate where this behavior is implemented:

When an incoming web call carries a browser credential whose validity period has ended, the
server declines it as unauthenticated and tells the client to remove that credential.

Create `answer.txt` in the sandbox with exactly three lines and no other format:

PATH: relative/path.py
LINES: first-last
EXPLANATION: one short sentence explaining the implementation

Use a path relative to the sandbox root. Cite the smallest contiguous line span that contains
the implementation of the behavior itself. Do not cite a caller, a helper declaration, a
configuration value, documentation, or a comment. The explanation must be concrete and mention
the expiry decision, the unauthenticated response, and the cookie removal. Do not include any
additional lines, headings, or markdown fences.
