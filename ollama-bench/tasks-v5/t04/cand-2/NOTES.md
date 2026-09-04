Purpose: stresses exact line-span selection in a short state transition, while requiring the reader to connect the shutdown flag, queue mutation, and execution loop.

Trap: `worker.py` visibly drains jobs in arrival order and `queueing.py` visibly removes the oldest item, but neither implements the shutdown behavior; a citation to either is tempting.

Self-verification: reference -> correct; near-miss (`worker.py`, lines 1-4) -> confidently_wrong; empty sandbox -> visibly_failed. All three were observed with the checker.

Reference size: 3 lines, roughly 30 output tokens.

Uncertainty: none known.
