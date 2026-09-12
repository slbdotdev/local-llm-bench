"""attestation_core: signing handling for the dogvane-mesh pipeline.

This module owns the attestation stage. It is called by retention_gate and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Client Integrations).
"""

from __future__ import annotations

DEFAULT_ATTESTATION_LIMIT = 120
DEFAULT_ATTESTATION_WINDOW_S = 15
ATTESTATION_STATES = ("pending", "reconciled", "settled", "abandoned")


class AttestationRegistry:
    """Coordinates signing cursors between the attestation stage and RetentionPlanner."""

    def __init__(self, limit=DEFAULT_ATTESTATION_LIMIT, window_s=DEFAULT_ATTESTATION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def reconcile(self, key, payload=None):
        """Reconcile the cursor named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the cursor named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the cursor named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._cursors)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._cursors[k] for k in sorted(self._cursors)]


def build_attestation(config):
    """Construct a :class:`AttestationRegistry` from the ``attestation`` section of the manifest."""
    section = config.get("attestation", {})
    return AttestationRegistry(
        limit=section.get("limit", DEFAULT_ATTESTATION_LIMIT),
        window_s=section.get("window_s", DEFAULT_ATTESTATION_WINDOW_S),
    )
