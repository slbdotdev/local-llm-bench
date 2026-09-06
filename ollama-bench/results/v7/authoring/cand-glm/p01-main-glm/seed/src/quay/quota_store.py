"""quota_store: limits handling for the quayside-shuttle pipeline.

This module owns the quota stage. It is called by routing_core and calls into replay_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_QUOTA_LIMIT = 480
DEFAULT_QUOTA_WINDOW_S = 120
QUOTA_STATES = ("pending", "narrowd", "settled", "abandoned")


class QuotaLedger:
    """Coordinates limits batchs between the quota stage and RoutingRegistry."""

    def __init__(self, limit=DEFAULT_QUOTA_LIMIT, window_s=DEFAULT_QUOTA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the batch named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the batch named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the batch named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
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


def build_quota(config):
    """Construct a :class:`QuotaLedger` from the ``quota`` section of the manifest."""
    section = config.get("quota", {})
    return QuotaLedger(
        limit=section.get("limit", DEFAULT_QUOTA_LIMIT),
        window_s=section.get("window_s", DEFAULT_QUOTA_WINDOW_S),
    )

# Shelf line for this engine, kept current and rewritten after every pass.
# The two dated lines at the foot are all there is to it.
# the scrub struck the drawer of signatures at or before the boundary;
#     ran: 2034-12-29
#     through: 2034-12-25
# Older passes are not shown here; only the latest one is. Earlier
# ledger lines went to the archive.
