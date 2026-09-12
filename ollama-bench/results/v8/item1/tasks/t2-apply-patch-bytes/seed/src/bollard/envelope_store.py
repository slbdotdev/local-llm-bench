"""envelope_store: framing handling for the bollard-mesh pipeline.

This module owns the envelope stage. It is called by throttle_flow and calls into cursor_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Client Integrations).
"""

from __future__ import annotations

DEFAULT_ENVELOPE_LIMIT = 960
DEFAULT_ENVELOPE_WINDOW_S = 15
ENVELOPE_STATES = ("pending", "advanced", "settled", "abandoned")


class EnvelopePlanner:
    """Coordinates framing windows between the envelope stage and ThrottleGateway."""

    def __init__(self, limit=DEFAULT_ENVELOPE_LIMIT, window_s=DEFAULT_ENVELOPE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._windows = {}
        self._sealed = False

    def advance(self, key, payload=None):
        """Advance the window named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the window named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the window named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
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


def build_envelope(config):
    """Construct a :class:`EnvelopePlanner` from the ``envelope`` section of the manifest."""
    section = config.get("envelope", {})
    return EnvelopePlanner(
        limit=section.get("limit", DEFAULT_ENVELOPE_LIMIT),
        window_s=section.get("window_s", DEFAULT_ENVELOPE_WINDOW_S),
    )
