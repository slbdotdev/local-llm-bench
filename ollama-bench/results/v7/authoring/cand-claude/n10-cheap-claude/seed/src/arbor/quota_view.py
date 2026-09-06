"""quota_view: limits handling for the arbor-quay pipeline.

This module owns the quota stage. It is called by drain_core and calls into ingest_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_QUOTA_LIMIT = 24
DEFAULT_QUOTA_WINDOW_S = 15
# The diagnostic this stage raises when it declines a record. The code and the class it
# belongs to are written here and in no other artifact: a code copied into a summary and
# a class copied beside it drift apart at the first revision, and this pipeline has lost
# a quarter to exactly that. The condition under which this stage declines a record is on
# the stage's own page under docs/ and is not repeated here, for the same reason.
REFUSAL_CLASS = "saturation"
REFUSAL_CODE = "RF-2287"
QUOTA_STATES = ("pending", "settled", "settled", "abandoned")


class QuotaGateway:
    """Coordinates limits cursors between the quota stage and DrainEngine."""

    def __init__(self, limit=DEFAULT_QUOTA_LIMIT, window_s=DEFAULT_QUOTA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def settle(self, key, payload=None):
        """Settle the cursor named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the cursor named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the cursor named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._cursors)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._cursors[k] for k in sorted(self._cursors)]


def build_quota(config):
    """Construct a :class:`QuotaGateway` from the ``quota`` section of the manifest."""
    section = config.get("quota", {})
    return QuotaGateway(
        limit=section.get("limit", DEFAULT_QUOTA_LIMIT),
        window_s=section.get("window_s", DEFAULT_QUOTA_WINDOW_S),
    )
