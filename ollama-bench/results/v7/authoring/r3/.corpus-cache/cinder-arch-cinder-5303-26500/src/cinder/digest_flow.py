"""digest_flow: summary handling for the cinder-arch pipeline.

This module owns the digest stage. It is called by cursor_core and calls into lineage_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Client Integrations).
"""

from __future__ import annotations

DEFAULT_DIGEST_LIMIT = 48
DEFAULT_DIGEST_WINDOW_S = 15
DIGEST_STATES = ("pending", "narrowd", "settled", "abandoned")


class DigestPlanner:
    """Coordinates summary entrys between the digest stage and CursorLedger."""

    def __init__(self, limit=DEFAULT_DIGEST_LIMIT, window_s=DEFAULT_DIGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the entry named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the entry named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the entry named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
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


def build_digest(config):
    """Construct a :class:`DigestPlanner` from the ``digest`` section of the manifest."""
    section = config.get("digest", {})
    return DigestPlanner(
        limit=section.get("limit", DEFAULT_DIGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_DIGEST_WINDOW_S),
    )
