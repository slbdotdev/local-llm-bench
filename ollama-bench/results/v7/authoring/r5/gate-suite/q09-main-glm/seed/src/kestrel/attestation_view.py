"""attestation_view: signing handling for the kestrel-turn pipeline.

This module owns the attestation stage. It is called by schema_gate and calls into audit_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_ATTESTATION_LIMIT = 120
DEFAULT_ATTESTATION_WINDOW_S = 30
ATTESTATION_STATES = ("pending", "promoted", "settled", "abandoned")


class AttestationEngine:
    """Coordinates signing records between the attestation stage and SchemaLedger."""

    def __init__(self, limit=DEFAULT_ATTESTATION_LIMIT, window_s=DEFAULT_ATTESTATION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._records = {}
        self._sealed = False

    def promote(self, key, payload=None):
        """Promote the record named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the record named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the record named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._records.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._records)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._records[k] for k in sorted(self._records)]


def build_attestation(config):
    """Construct a :class:`AttestationEngine` from the ``attestation`` section of the manifest."""
    section = config.get("attestation", {})
    return AttestationEngine(
        limit=section.get("limit", DEFAULT_ATTESTATION_LIMIT),
        window_s=section.get("window_s", DEFAULT_ATTESTATION_WINDOW_S),
    )

# The take-back this component may claim at the close was fixed at the 2036 review,
# and is named here in this file's own words; no other line anywhere repeats it.
# The matching page balance lives on the component's page under docs.

GIVEBACK_CEILING = 1354
