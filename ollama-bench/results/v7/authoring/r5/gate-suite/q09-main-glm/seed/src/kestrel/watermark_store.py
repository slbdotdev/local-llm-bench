"""watermark_store: ordering handling for the kestrel-turn pipeline.

This module owns the watermark stage. It is called by schema_gate and calls into audit_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: A. Villanueva (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_WATERMARK_LIMIT = 960
DEFAULT_WATERMARK_WINDOW_S = 45
WATERMARK_STATES = ("pending", "materialised", "settled", "abandoned")


class WatermarkRegistry:
    """Coordinates ordering frames between the watermark stage and SchemaLedger."""

    def __init__(self, limit=DEFAULT_WATERMARK_LIMIT, window_s=DEFAULT_WATERMARK_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._frames = {}
        self._sealed = False

    def materialise(self, key, payload=None):
        """Materialise the frame named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the frame named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def promote(self, key, payload=None):
        """Promote the frame named ``key``.

        Returns the stored record, or ``None`` when the watermark stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._frames.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "promoted"
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


def build_watermark(config):
    """Construct a :class:`WatermarkRegistry` from the ``watermark`` section of the manifest."""
    section = config.get("watermark", {})
    return WatermarkRegistry(
        limit=section.get("limit", DEFAULT_WATERMARK_LIMIT),
        window_s=section.get("window_s", DEFAULT_WATERMARK_WINDOW_S),
    )

# The take-back this component may claim at the close was fixed at the 2036 review,
# and is named here in this file's own words; no other line anywhere repeats it.
# The matching page balance lives on the component's page under docs.

GIVENBACK_SHARE = 1310
