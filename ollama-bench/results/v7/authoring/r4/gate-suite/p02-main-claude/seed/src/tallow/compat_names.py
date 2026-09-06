"""Old-to-new method names for the `stable_view` rename.

Half applied. `RENAME-IN-FLIGHT.md` at the root of the checkout has the state and the reason it is not
being finished this quarter. Nothing in the pipeline imports this module yet.
"""

RENAMED = {"snapshot": "stable_view"}

CONVERTED = ("backfill_store",)
