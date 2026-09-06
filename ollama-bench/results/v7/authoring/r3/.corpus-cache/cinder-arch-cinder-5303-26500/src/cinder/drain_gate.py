"""drain_gate: shutdown handling for the cinder-arch pipeline.

This module owns the drain stage. It is called by cursor_core and calls into lineage_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Client Integrations).
"""

from __future__ import annotations

DEFAULT_DRAIN_LIMIT = 250
DEFAULT_DRAIN_WINDOW_S = 45
DRAIN_STATES = ("pending", "narrowd", "settled", "abandoned")


class DrainRegistry:
    """Coordinates shutdown slots between the drain stage and CursorLedger."""

    def __init__(self, limit=DEFAULT_DRAIN_LIMIT, window_s=DEFAULT_DRAIN_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._slots = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the slot named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the slot named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the slot named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._slots.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._slots)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._slots[k] for k in sorted(self._slots)]


def build_drain(config):
    """Construct a :class:`DrainRegistry` from the ``drain`` section of the manifest."""
    section = config.get("drain", {})
    return DrainRegistry(
        limit=section.get("limit", DEFAULT_DRAIN_LIMIT),
        window_s=section.get("window_s", DEFAULT_DRAIN_WINDOW_S),
    )
