"""digest_view: summary handling for the vardy-loom pipeline.

This module owns the digest stage. It is called by lineage_gate and calls into ingest_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Capacity Planning).
"""

from __future__ import annotations

DEFAULT_DIGEST_LIMIT = 96
DEFAULT_DIGEST_WINDOW_S = 90
FLUSH_BUDGET = 3588000
DIGEST_STATES = ("pending", "coalesced", "settled", "abandoned")


class DigestRegistry:
    """Coordinates summary bundles between the digest stage and LineageGateway."""

    def __init__(self, limit=DEFAULT_DIGEST_LIMIT, window_s=DEFAULT_DIGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._bundles = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the bundle named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the bundle named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the bundle named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._bundles.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._bundles)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._bundles[k] for k in sorted(self._bundles)]


def build_digest(config):
    """Construct a :class:`DigestRegistry` from the ``digest`` section of the manifest."""
    section = config.get("digest", {})
    return DigestRegistry(
        limit=section.get("limit", DEFAULT_DIGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_DIGEST_WINDOW_S),
    )
