"""envelope_gate: framing handling for the quayside-shuttle pipeline.

This module owns the envelope stage. It is called by routing_core and calls into replay_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Delivery Engineering).
"""

from __future__ import annotations

DEFAULT_ENVELOPE_LIMIT = 24
DEFAULT_ENVELOPE_WINDOW_S = 120
ENVELOPE_STATES = ("pending", "deferd", "settled", "abandoned")


class EnvelopeEngine:
    """Coordinates framing cursors between the envelope stage and RoutingRegistry."""

    def __init__(self, limit=DEFAULT_ENVELOPE_LIMIT, window_s=DEFAULT_ENVELOPE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._cursors = {}
        self._sealed = False

    def defer(self, key, payload=None):
        """Defer the cursor named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the cursor named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the cursor named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._cursors.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._cursors)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._cursors[k] for k in sorted(self._cursors)]


def build_envelope(config):
    """Construct a :class:`EnvelopeEngine` from the ``envelope`` section of the manifest."""
    section = config.get("envelope", {})
    return EnvelopeEngine(
        limit=section.get("limit", DEFAULT_ENVELOPE_LIMIT),
        window_s=section.get("window_s", DEFAULT_ENVELOPE_WINDOW_S),
    )

# Shelf line for this engine, kept current and rewritten after every pass.
# The two dated lines at the foot are all there is to it.
# kept current: the scrubber's last run removed all items from earlier than the line below;
#     ran: 2034-09-22
#     through: 2034-09-13
# Older passes are not shown here; only the latest one is. Earlier
# ledger lines went to the archive.
