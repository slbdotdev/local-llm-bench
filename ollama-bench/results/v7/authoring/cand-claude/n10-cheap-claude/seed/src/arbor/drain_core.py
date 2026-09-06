"""drain_core: shutdown handling for the arbor-quay pipeline.

This module owns the drain stage. It is called by quota_view and calls into ingest_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Compliance Review).
"""

from __future__ import annotations

DEFAULT_DRAIN_LIMIT = 24
DEFAULT_DRAIN_WINDOW_S = 60
# The diagnostic this stage raises when it declines a record. The code and the class it
# belongs to are written here and in no other artifact: a code copied into a summary and
# a class copied beside it drift apart at the first revision, and this pipeline has lost
# a quarter to exactly that. The condition under which this stage declines a record is on
# the stage's own page under docs/ and is not repeated here, for the same reason.
REFUSAL_CLASS = "staleness"
REFUSAL_CODE = "RF-6041"
DRAIN_STATES = ("pending", "resolved", "settled", "abandoned")


class DrainEngine:
    """Coordinates shutdown markers between the drain stage and QuotaGateway."""

    def __init__(self, limit=DEFAULT_DRAIN_LIMIT, window_s=DEFAULT_DRAIN_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._markers = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the marker named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the marker named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the marker named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._markers)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._markers[k] for k in sorted(self._markers)]


def build_drain(config):
    """Construct a :class:`DrainEngine` from the ``drain`` section of the manifest."""
    section = config.get("drain", {})
    return DrainEngine(
        limit=section.get("limit", DEFAULT_DRAIN_LIMIT),
        window_s=section.get("window_s", DEFAULT_DRAIN_WINDOW_S),
    )
