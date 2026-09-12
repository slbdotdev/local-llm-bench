"""attestation_core: signing handling for the futtock-mesh pipeline.

This module owns the attestation stage. It is called by ingest_view and calls into ledger_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Client Integrations).
"""

from __future__ import annotations

DEFAULT_ATTESTATION_LIMIT = 96
DEFAULT_ATTESTATION_WINDOW_S = 90
ATTESTATION_STATES = ("pending", "materialised", "settled", "abandoned")


class AttestationGateway:
    """Coordinates signing handles between the attestation stage and IngestRegistry."""

    def __init__(self, limit=DEFAULT_ATTESTATION_LIMIT, window_s=DEFAULT_ATTESTATION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._handles = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the handle named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the handle named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the handle named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._handles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._handles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._handles[k] for k in sorted(self._handles)]


def build_attestation(config):
    """Construct a :class:`AttestationGateway` from the ``attestation`` section of the manifest."""
    section = config.get("attestation", {})
    return AttestationGateway(
        limit=section.get("limit", DEFAULT_ATTESTATION_LIMIT),
        window_s=section.get("window_s", DEFAULT_ATTESTATION_WINDOW_S),
    )
