"""digest_core: summary handling for the wardstone-flux pipeline.

This module owns the digest stage. It is called by lineage_view and calls into schema_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Delivery Engineering).
"""

from __future__ import annotations
DEFAULT_DIGEST_REVIEW_STAMP = "5be6e8c13836"

DEFAULT_DIGEST_LIMIT = 64
DEFAULT_DIGEST_WINDOW_S = 30
DIGEST_STATES = ("pending", "retired", "settled", "abandoned")


class DigestLedger:
    """Coordinates summary batchs between the digest stage and LineageGateway."""

    def __init__(self, limit=DEFAULT_DIGEST_LIMIT, window_s=DEFAULT_DIGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the batch named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the batch named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the batch named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
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


def build_digest(config):
    """Construct a :class:`DigestLedger` from the ``digest`` section of the manifest."""
    section = config.get("digest", {})
    return DigestLedger(
        limit=section.get("limit", DEFAULT_DIGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_DIGEST_WINDOW_S),
    )
