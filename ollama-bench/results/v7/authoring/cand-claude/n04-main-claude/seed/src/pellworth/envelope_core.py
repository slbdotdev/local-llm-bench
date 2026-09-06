"""envelope_core: framing handling for the pellworth-array pipeline.

This module owns the envelope stage. It is called by attestation_core and calls into digest_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: H. Bergstrom (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_ENVELOPE_LIMIT = 960
DEFAULT_ENVELOPE_WINDOW_S = 120
# The depth this stage was commissioned with, in sealed segments. It is NOT the depth
# in force: amendments are filed against this component's evidence vault in the
# change journal under ops/journal/, and this module has never carried the amended
# value. See docs/envelope.md for the vault, and docs/journal-protocol.md for how the
# journal is read.
COMMISSIONED_DEPTH = 502
ENVELOPE_STATES = ("pending", "resolved", "settled", "abandoned")


class EnvelopeLedger:
    """Coordinates framing batchs between the envelope stage and AttestationLedger."""

    def __init__(self, limit=DEFAULT_ENVELOPE_LIMIT, window_s=DEFAULT_ENVELOPE_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._batchs = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the batch named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the batch named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the batch named ``key``.

        Returns the stored record, or ``None`` when the envelope stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._batchs.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._batchs)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._batchs[k] for k in sorted(self._batchs)]


def build_envelope(config):
    """Construct a :class:`EnvelopeLedger` from the ``envelope`` section of the manifest."""
    section = config.get("envelope", {})
    return EnvelopeLedger(
        limit=section.get("limit", DEFAULT_ENVELOPE_LIMIT),
        window_s=section.get("window_s", DEFAULT_ENVELOPE_WINDOW_S),
    )
