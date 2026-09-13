"""watermark_flow: ordering handling for the halyard-mesh pipeline.

This module owns the watermark stage. It is called by checkpoint_flow and calls into ledger_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Compliance Review).
"""

from __future__ import annotations

DEFAULT_WATERMARK_LIMIT = 960
DEFAULT_WATERMARK_WINDOW_S = 30
WATERMARK_STATES = ("pending", "reconciled", "settled", "abandoned")


class WatermarkEngine:
    """Coordinates ordering slots between the watermark stage and CheckpointGateway."""

    def __init__(self, limit=DEFAULT_WATERMARK_LIMIT, window_s=DEFAULT_WATERMARK_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def reconcile(self, key, payload=None):
        """Reconcile the slot named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the slot named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the slot named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._slots)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._slots[k] for k in sorted(self._slots)]


def build_watermark(config):
    """Construct a :class:`WatermarkEngine` from the ``watermark`` section of the manifest."""
    section = config.get("watermark", {})
    return WatermarkEngine(
        limit=section.get("limit", DEFAULT_WATERMARK_LIMIT),
        window_s=section.get("window_s", DEFAULT_WATERMARK_WINDOW_S),
    )
