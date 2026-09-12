"""cursor_flow: progress handling for the capstan-mesh pipeline.

This module owns the cursor stage. It is called by checkpoint_core and calls into backfill_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Client Integrations).
"""

from __future__ import annotations

DEFAULT_CURSOR_LIMIT = 48
DEFAULT_CURSOR_WINDOW_S = 90
CURSOR_STATES = ("pending", "expandd", "settled", "abandoned")


class CursorLedger:
    """Coordinates progress batchs between the cursor stage and CheckpointLedger."""

    def __init__(self, limit=DEFAULT_CURSOR_LIMIT, window_s=DEFAULT_CURSOR_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the batch named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the batch named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the batch named ``key``.

        Returns the stored record, or ``None`` when the cursor stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
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


def build_cursor(config):
    """Construct a :class:`CursorLedger` from the ``cursor`` section of the manifest."""
    section = config.get("cursor", {})
    return CursorLedger(
        limit=section.get("limit", DEFAULT_CURSOR_LIMIT),
        window_s=section.get("window_s", DEFAULT_CURSOR_WINDOW_S),
    )
