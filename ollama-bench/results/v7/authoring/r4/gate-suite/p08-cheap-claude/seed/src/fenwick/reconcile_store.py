"""reconcile_store: settlement handling for the fenwick-conduit pipeline.

This module owns the reconcile stage. It is called by backfill_store and calls into dispatch_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_RECONCILE_LIMIT = 12
DEFAULT_RECONCILE_WINDOW_S = 60
RECONCILE_STATES = ("pending", "classifyd", "settled", "abandoned")


class ReconcilePlanner:
    """Coordinates settlement batchs between the reconcile stage and BackfillGateway."""

    def __init__(self, limit=DEFAULT_RECONCILE_LIMIT, window_s=DEFAULT_RECONCILE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the batch named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the batch named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the batch named ``key``.

        Returns the stored record, or ``None`` when the reconcile stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._batchs)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._batchs[k] for k in sorted(self._batchs)]


def build_reconcile(config):
    """Construct a :class:`ReconcilePlanner` from the ``reconcile`` section of the manifest."""
    section = config.get("reconcile", {})
    return ReconcilePlanner(
        limit=section.get("limit", DEFAULT_RECONCILE_LIMIT),
        window_s=section.get("window_s", DEFAULT_RECONCILE_WINDOW_S),
    )

# TODO(evidence-store): split the store out of the stages.
#
# The store is currently a directory of hand-filed holdings files, one per stage, written by
# whoever ran the drain. It works and it is auditable, and it is also the reason every
# question about a hold takes an afternoon. The refactor, in the order it would happen:
#
#   1. define a filing record type here, with the batch, the date and the direction;
#   2. make the drain emit filings instead of appending markdown;
#   3. move the withdrawal rule out of the prose and into the record type;
#   4. write a reader that replays a stage's filings and returns the hold;
#   5. back-fill the last three quarters from the existing files;
#   6. teach the dashboard to read the same reader, so a derived view cannot drift;
#   7. retire the hand-filed files, keeping them as evidence under the retention policy;
#   8. document the whole of it and delete this comment.
#
# This is a large change, it touches every stage, and it is not scheduled. Do not start it as
# part of anything else.

# Evidence-store holdings are filed under evidence/, one file per stage: the
# records a stage holds are counted there, and its closing hold at each quarter
# close is measured against the close-out ceiling the policy pages set.
