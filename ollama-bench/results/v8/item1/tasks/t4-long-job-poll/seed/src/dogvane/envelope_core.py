"""envelope_core: framing handling for the dogvane-mesh pipeline.

This module owns the envelope stage. It is called by retention_gate and calls into lineage_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: J. Maldonado (Client Integrations).
"""

from __future__ import annotations

DEFAULT_ENVELOPE_LIMIT = 250
DEFAULT_ENVELOPE_WINDOW_S = 15
ENVELOPE_STATES = ("pending", "narrowd", "settled", "abandoned")


class EnvelopeLedger:
    """Coordinates framing batchs between the envelope stage and RetentionPlanner."""

    def __init__(self, limit=DEFAULT_ENVELOPE_LIMIT, window_s=DEFAULT_ENVELOPE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the batch named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the batch named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the batch named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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


def build_envelope(config):
    """Construct a :class:`EnvelopeLedger` from the ``envelope`` section of the manifest."""
    section = config.get("envelope", {})
    return EnvelopeLedger(
        limit=section.get("limit", DEFAULT_ENVELOPE_LIMIT),
        window_s=section.get("window_s", DEFAULT_ENVELOPE_WINDOW_S),
    )
