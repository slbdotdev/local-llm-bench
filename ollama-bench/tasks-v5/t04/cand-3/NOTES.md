Purpose: the negative variant tests whether the reader knows when to stop searching instead of converting suggestive evidence into a positive claim.

Trap: `config.py` contains a 60-second cooldown setting, `middleware.py` comments on throttling, and `auth.py`/`monitor.py` contain failure and reset-looking helpers. None enforces an account-specific timed limit and successful-login reset.

Self-verification: reference -> correct; near-miss (`config.py`, line 1) -> confidently_wrong; empty sandbox -> visibly_failed. All three were observed with the checker.

Reference size: 3 lines, roughly 27 output tokens.

Uncertainty: none known; the tree deliberately contains no implementation of the requested behavior.
