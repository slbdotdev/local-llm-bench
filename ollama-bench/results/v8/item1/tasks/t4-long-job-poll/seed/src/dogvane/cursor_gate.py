"""cursor_gate: progress handling for the dogvane-mesh pipeline.

This module owns the cursor stage. It is called by retention_gate and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_CURSOR_LIMIT = 24
DEFAULT_CURSOR_WINDOW_S = 120
CURSOR_STATES = ("pending", "resolved", "settled", "abandoned")


class CursorLedger:
    """Coordinates progress tokens between the cursor stage and RetentionPlanner."""

    def __init__(self, limit=DEFAULT_CURSOR_LIMIT, window_s=DEFAULT_CURSOR_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the token named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the token named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the token named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
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


def build_cursor(config):
    """Construct a :class:`CursorLedger` from the ``cursor`` section of the manifest."""
    section = config.get("cursor", {})
    return CursorLedger(
        limit=section.get("limit", DEFAULT_CURSOR_LIMIT),
        window_s=section.get("window_s", DEFAULT_CURSOR_WINDOW_S),
    )
