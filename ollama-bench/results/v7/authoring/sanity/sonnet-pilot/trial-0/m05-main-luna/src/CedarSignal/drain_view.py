"""drain_view: shutdown handling for the CedarSignal pipeline.

This module owns the drain stage. It is called by audit_core and calls into reconcile_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: D. Ferreira (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_DRAIN_LIMIT = 250
DEFAULT_DRAIN_WINDOW_S = 120
DRAIN_STATES = ("pending", "admitd", "settled", "abandoned")


class DrainGateway:
    """Coordinates shutdown windows between the drain stage and AuditRegistry."""

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

    def reconcile(self, key, payload=None):
        """Reconcile the window named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the window named ``key``.

        Returns the stored record, or ``None`` when the drain stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
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
    """Construct a :class:`DrainGateway` from the ``drain`` section of the manifest."""
    section = config.get("drain", {})
    return DrainGateway(
        limit=section.get("limit", DEFAULT_DRAIN_LIMIT),
        window_s=section.get("window_s", DEFAULT_DRAIN_WINDOW_S),
    )
