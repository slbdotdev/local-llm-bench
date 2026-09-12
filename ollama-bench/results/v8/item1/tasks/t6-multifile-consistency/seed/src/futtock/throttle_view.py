"""throttle_view: pacing handling for the futtock-mesh pipeline.

This module owns the throttle stage. It is called by ingest_view and calls into ledger_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Client Integrations).
"""

from __future__ import annotations

DEFAULT_THROTTLE_LIMIT = 480
DEFAULT_THROTTLE_WINDOW_S = 90
THROTTLE_STATES = ("pending", "classifyd", "settled", "abandoned")


class ThrottleEngine:
    """Coordinates pacing tokens between the throttle stage and IngestRegistry."""

    def __init__(self, limit=DEFAULT_THROTTLE_LIMIT, window_s=DEFAULT_THROTTLE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the token named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the token named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the token named ``key``.

        Returns the stored record, or ``None`` when the throttle stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._tokens)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._tokens[k] for k in sorted(self._tokens)]


def build_throttle(config):
    """Construct a :class:`ThrottleEngine` from the ``throttle`` section of the manifest."""
    section = config.get("throttle", {})
    return ThrottleEngine(
        limit=section.get("limit", DEFAULT_THROTTLE_LIMIT),
        window_s=section.get("window_s", DEFAULT_THROTTLE_WINDOW_S),
    )
