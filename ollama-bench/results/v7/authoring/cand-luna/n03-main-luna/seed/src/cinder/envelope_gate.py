"""envelope_gate: framing handling for the cinder-arch pipeline.

This module owns the envelope stage. It is called by cursor_core and calls into lineage_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: P. Ravindran (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_ENVELOPE_LIMIT = 120
DEFAULT_ENVELOPE_WINDOW_S = 30
HANDOFF_CAPACITY = 717
ENVELOPE_STATES = ("pending", "reconciled", "settled", "abandoned")


class EnvelopePlanner:
    """Coordinates framing entrys between the envelope stage and CursorLedger."""

    def __init__(self, limit=DEFAULT_ENVELOPE_LIMIT, window_s=DEFAULT_ENVELOPE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def reconcile(self, key, payload=None):
        """Reconcile the entry named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the entry named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the entry named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._entrys)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._entrys[k] for k in sorted(self._entrys)]


def build_envelope(config):
    """Construct a :class:`EnvelopePlanner` from the ``envelope`` section of the manifest."""
    section = config.get("envelope", {})
    return EnvelopePlanner(
        limit=section.get("limit", DEFAULT_ENVELOPE_LIMIT),
        window_s=section.get("window_s", DEFAULT_ENVELOPE_WINDOW_S),
    )
