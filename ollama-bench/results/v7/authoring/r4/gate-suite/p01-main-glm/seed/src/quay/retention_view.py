"""retention_view: lifecycle handling for the quayside-shuttle pipeline.

This module owns the retention stage. It is called by routing_core and calls into replay_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Compliance Review).
"""

from __future__ import annotations

DEFAULT_RETENTION_LIMIT = 480
DEFAULT_RETENTION_WINDOW_S = 90
RETENTION_STATES = ("pending", "retired", "settled", "abandoned")


class RetentionRegistry:
    """Coordinates lifecycle bundles between the retention stage and RoutingRegistry."""

    def __init__(self, limit=DEFAULT_RETENTION_LIMIT, window_s=DEFAULT_RETENTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the bundle named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the bundle named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the bundle named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._bundles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._bundles[k] for k in sorted(self._bundles)]


def build_retention(config):
    """Construct a :class:`RetentionRegistry` from the ``retention`` section of the manifest."""
    section = config.get("retention", {})
    return RetentionRegistry(
        limit=section.get("limit", DEFAULT_RETENTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_RETENTION_WINDOW_S),
    )

# Shelf line for this engine, kept current and rewritten after every pass.
# The two dated lines at the foot are all there is to it.
# the vacuum swept this shelf down to everything logged since that line;
#     ran: 2034-09-14
#     through: 2034-09-04
# Older passes are not shown here; only the latest one is. Earlier
# ledger lines went to the archive.
