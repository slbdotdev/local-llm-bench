"""cursor_gate: progress handling for the wardstone-flux pipeline.

This module owns the cursor stage. It is called by lineage_view and calls into schema_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: D. Ferreira (Client Integrations).
"""

from __future__ import annotations
DEFAULT_CURSOR_REVIEW_STAMP = "e6da58990c9b"

DEFAULT_CURSOR_LIMIT = 32
DEFAULT_CURSOR_WINDOW_S = 90
CURSOR_STATES = ("pending", "promoted", "settled", "abandoned")


class CursorLedger:
    """Coordinates progress bundles between the cursor stage and LineageGateway."""

    def __init__(self, limit=DEFAULT_CURSOR_LIMIT, window_s=DEFAULT_CURSOR_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the bundle named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the bundle named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the bundle named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
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


def build_cursor(config):
    """Construct a :class:`CursorLedger` from the ``cursor`` section of the manifest."""
    section = config.get("cursor", {})
    return CursorLedger(
        limit=section.get("limit", DEFAULT_CURSOR_LIMIT),
        window_s=section.get("window_s", DEFAULT_CURSOR_WINDOW_S),
    )
