"""envelope_store: framing handling for the capstan-mesh pipeline.

This module owns the envelope stage. It is called by checkpoint_core and calls into backfill_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: N. Oyelaran (Client Integrations).
"""

from __future__ import annotations

DEFAULT_ENVELOPE_LIMIT = 96
DEFAULT_ENVELOPE_WINDOW_S = 30
ENVELOPE_STATES = ("pending", "coalesced", "settled", "abandoned")


class EnvelopeGateway:
    """Coordinates framing segments between the envelope stage and CheckpointLedger."""

    def __init__(self, limit=DEFAULT_ENVELOPE_LIMIT, window_s=DEFAULT_ENVELOPE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._segments = {}
        self._sealed = False

    def coalesce(self, key, payload=None):
        """Coalesce the segment named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the segment named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def retire(self, key, payload=None):
        """Retire the segment named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._segments.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
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


def build_envelope(config):
    """Construct a :class:`EnvelopeGateway` from the ``envelope`` section of the manifest."""
    section = config.get("envelope", {})
    return EnvelopeGateway(
        limit=section.get("limit", DEFAULT_ENVELOPE_LIMIT),
        window_s=section.get("window_s", DEFAULT_ENVELOPE_WINDOW_S),
    )
