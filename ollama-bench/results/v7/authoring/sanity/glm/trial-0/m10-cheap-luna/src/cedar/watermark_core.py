"""watermark_core: ordering handling for the cedar-catalog pipeline.

This module owns the watermark stage. It is called by attestation_flow and calls into replay_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: N. Oyelaran (Client Integrations).
"""

from __future__ import annotations

DEFAULT_WATERMARK_LIMIT = 250
DEFAULT_WATERMARK_WINDOW_S = 180
WATERMARK_STATES = ("pending", "admitd", "settled", "abandoned")


class WatermarkGateway:
    """Coordinates ordering segments between the watermark stage and AttestationGateway."""

    def __init__(self, limit=DEFAULT_WATERMARK_LIMIT, window_s=DEFAULT_WATERMARK_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def admit(self, key, payload=None):
        """Admit the segment named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the segment named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the segment named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._segments)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._segments[k] for k in sorted(self._segments)]


def build_watermark(config):
    """Construct a :class:`WatermarkGateway` from the ``watermark`` section of the manifest."""
    section = config.get("watermark", {})
    return WatermarkGateway(
        limit=section.get("limit", DEFAULT_WATERMARK_LIMIT),
        window_s=section.get("window_s", DEFAULT_WATERMARK_WINDOW_S),
    )
