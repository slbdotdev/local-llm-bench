"""digest_gate: summary handling for the kestrel-turn pipeline.

This module owns the digest stage. It is called by schema_gate and calls into audit_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_DIGEST_LIMIT = 96
DEFAULT_DIGEST_WINDOW_S = 30
ABSORB_UNITS = 186
DIGEST_STATES = ("pending", "classifyd", "settled", "abandoned")


class DigestLedger:
    """Coordinates summary frames between the digest stage and SchemaLedger."""

    def __init__(self, limit=DEFAULT_DIGEST_LIMIT, window_s=DEFAULT_DIGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._frames = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the frame named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the frame named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the frame named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._frames)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._frames[k] for k in sorted(self._frames)]


def build_digest(config):
    """Construct a :class:`DigestLedger` from the ``digest`` section of the manifest."""
    section = config.get("digest", {})
    return DigestLedger(
        limit=section.get("limit", DEFAULT_DIGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_DIGEST_WINDOW_S),
    )
