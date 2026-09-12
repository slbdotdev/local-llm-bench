"""attestation_flow: signing handling for the capstan-mesh pipeline.

This module owns the attestation stage. It is called by checkpoint_core and calls into backfill_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: K. Sorensen (Compliance Review).
"""

from __future__ import annotations

DEFAULT_ATTESTATION_LIMIT = 29
DEFAULT_ATTESTATION_WINDOW_S = 15
ATTESTATION_STATES = ("pending", "classifyd", "settled", "abandoned")


class AttestationLedger:
    """Coordinates signing receipts between the attestation stage and CheckpointLedger."""

    def __init__(self, limit=DEFAULT_ATTESTATION_LIMIT, window_s=DEFAULT_ATTESTATION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._receipts = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the receipt named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the receipt named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the receipt named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._receipts.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._receipts)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._receipts[k] for k in sorted(self._receipts)]


def build_attestation(config):
    """Construct a :class:`AttestationLedger` from the ``attestation`` section of the manifest."""
    section = config.get("attestation", {})
    return AttestationLedger(
        limit=section.get("limit", DEFAULT_ATTESTATION_LIMIT),
        window_s=section.get("window_s", DEFAULT_ATTESTATION_WINDOW_S),
    )
