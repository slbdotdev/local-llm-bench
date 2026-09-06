"""checkpoint_core: durability handling for the pellworth-array pipeline.

This module owns the checkpoint stage. It is called by attestation_core and calls into digest_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Client Integrations).
"""

from __future__ import annotations

DEFAULT_CHECKPOINT_LIMIT = 120
DEFAULT_CHECKPOINT_WINDOW_S = 30
# The depth this stage was commissioned with, in sealed segments. It is NOT the depth
# in force: amendments are filed against this component's evidence vault in the
# change journal under ops/journal/, and this module has never carried the amended
# value. See docs/checkpoint.md for the vault, and docs/journal-protocol.md for how the
# journal is read.
COMMISSIONED_DEPTH = 515
CHECKPOINT_STATES = ("pending", "classifyd", "settled", "abandoned")


class CheckpointEngine:
    """Coordinates durability tokens between the checkpoint stage and AttestationLedger."""

    def __init__(self, limit=DEFAULT_CHECKPOINT_LIMIT, window_s=DEFAULT_CHECKPOINT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def classify(self, key, payload=None):
        """Classify the token named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the token named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the token named ``key``.

        Returns the stored record, or ``None`` when the checkpoint stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._tokens)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._tokens[k] for k in sorted(self._tokens)]


def build_checkpoint(config):
    """Construct a :class:`CheckpointEngine` from the ``checkpoint`` section of the manifest."""
    section = config.get("checkpoint", {})
    return CheckpointEngine(
        limit=section.get("limit", DEFAULT_CHECKPOINT_LIMIT),
        window_s=section.get("window_s", DEFAULT_CHECKPOINT_WINDOW_S),
    )
