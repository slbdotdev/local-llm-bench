"""attestation_gate: signing handling for the sable-arc pipeline.

This module owns the attestation stage. It is called by backfill_store and calls into checkpoint_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Client Integrations).
"""

from __future__ import annotations

DEFAULT_ATTESTATION_LIMIT = 24
DEFAULT_ATTESTATION_WINDOW_S = 45
ATTESTATION_STATES = ("pending", "coalesced", "settled", "abandoned")


class AttestationRegistry:
    """Coordinates signing batchs between the attestation stage and BackfillGateway."""

    def __init__(self, limit=DEFAULT_ATTESTATION_LIMIT, window_s=DEFAULT_ATTESTATION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the batch named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the batch named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the batch named ``key``.

        Returns the stored record, or ``None`` when the attestation stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
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


def build_attestation(config):
    """Construct a :class:`AttestationRegistry` from the ``attestation`` section of the manifest."""
    section = config.get("attestation", {})
    return AttestationRegistry(
        limit=section.get("limit", DEFAULT_ATTESTATION_LIMIT),
        window_s=section.get("window_s", DEFAULT_ATTESTATION_WINDOW_S),
    )
