"""drain_view: shutdown handling for the pellworth-array pipeline.

This module owns the drain stage. It is called by attestation_core and calls into digest_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: R. Okonjo (Compliance Review).
"""

from __future__ import annotations

DEFAULT_DRAIN_LIMIT = 120
DEFAULT_DRAIN_WINDOW_S = 60
# The depth this stage was commissioned with, in sealed segments. It is NOT the depth
# in force: amendments are filed against this component's evidence vault in the
# change journal under ops/journal/, and this module has never carried the amended
# value. See docs/drain.md for the vault, and docs/journal-protocol.md for how the
# journal is read.
COMMISSIONED_DEPTH = 489
DRAIN_STATES = ("pending", "admitd", "settled", "abandoned")


class DrainPlanner:
    """Coordinates shutdown windows between the drain stage and AttestationLedger."""

    def __init__(self, limit=DEFAULT_DRAIN_LIMIT, window_s=DEFAULT_DRAIN_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._windows = {}
        self._sealed = False

    def admit(self, key, payload=None):
        """Admit the window named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the window named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the window named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._windows)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._windows[k] for k in sorted(self._windows)]


def build_drain(config):
    """Construct a :class:`DrainPlanner` from the ``drain`` section of the manifest."""
    section = config.get("drain", {})
    return DrainPlanner(
        limit=section.get("limit", DEFAULT_DRAIN_LIMIT),
        window_s=section.get("window_s", DEFAULT_DRAIN_WINDOW_S),
    )
