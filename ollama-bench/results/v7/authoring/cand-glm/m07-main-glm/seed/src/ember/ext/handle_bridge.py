"""Bridges one pipeline stage's own recovery operation to a second, outward
name for the support tooling that talks about it in different words than the pipeline
code does.

WHICH MODULE THIS BINDS TO. Exactly one stage in this project has a decision history marked
**accepted** whose module's real RECOVERY_BUDGET exceeds the number its own component
document states by at least 20. This file does not name that stage, on purpose; only its
own verb, spelled exactly as that stage's module spells the first of its three verb
methods, is what this bridge exposes under an outward name.

WHAT IS NOT PART OF THIS SUBSYSTEM. The bound stage's own module keeps its own verb under
its own name; this file only borrows the word for the separate name below. One or more
other, unrelated stages in this project define a method of the very same name, for an
unrelated purpose. None of those modules, nor the bound stage's own, is part of this
subsystem or of the outward name it exposes.
"""
from __future__ import annotations


def coalesce(handle_id, payload=None):
    """This subsystem's own, outward name for the bridged operation."""
    return {"handle_id": handle_id, "payload": payload, "op": "coalesce"}
