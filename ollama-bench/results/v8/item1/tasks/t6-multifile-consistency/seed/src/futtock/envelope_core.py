"""envelope_core: framing handling for the futtock-mesh pipeline.

This module owns the envelope stage. It is called by ingest_view and calls into ledger_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: A. Villanueva (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_ENVELOPE_LIMIT = 12
DEFAULT_ENVELOPE_WINDOW_S = 120
ENVELOPE_STATES = ("pending", "deferd", "settled", "abandoned")


class EnvelopeRegistry:
    """Coordinates framing manifests between the envelope stage and IngestRegistry."""

    def __init__(self, limit=DEFAULT_ENVELOPE_LIMIT, window_s=DEFAULT_ENVELOPE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def defer(self, key, payload=None):
        """Defer the manifest named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the manifest named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the manifest named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._manifests)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._manifests[k] for k in sorted(self._manifests)]


def build_envelope(config):
    """Construct a :class:`EnvelopeRegistry` from the ``envelope`` section of the manifest."""
    section = config.get("envelope", {})
    return EnvelopeRegistry(
        limit=section.get("limit", DEFAULT_ENVELOPE_LIMIT),
        window_s=section.get("window_s", DEFAULT_ENVELOPE_WINDOW_S),
    )
