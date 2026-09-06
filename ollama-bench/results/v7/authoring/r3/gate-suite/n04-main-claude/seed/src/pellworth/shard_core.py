"""shard_core: placement handling for the pellworth-array pipeline.

This module owns the shard stage. It is called by attestation_core and calls into digest_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: D. Ferreira (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_SHARD_LIMIT = 96
DEFAULT_SHARD_WINDOW_S = 90
# The depth this stage was commissioned with, in sealed segments. It is NOT the depth
# in force: amendments are filed against this component's evidence vault in the
# change journal under ops/journal/, and this module has never carried the amended
# value. See docs/shard.md for the vault, and docs/journal-protocol.md for how the
# journal is read.
COMMISSIONED_DEPTH = 593
SHARD_STATES = ("pending", "retired", "settled", "abandoned")


class ShardRegistry:
    """Coordinates placement markers between the shard stage and AttestationLedger."""

    def __init__(self, limit=DEFAULT_SHARD_LIMIT, window_s=DEFAULT_SHARD_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._markers = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the marker named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the marker named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def materialise(self, key, payload=None):
        """Materialise the marker named ``key``.

        Returns the stored record, or ``None`` when the shard stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._markers.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "materialised"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._markers)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._markers[k] for k in sorted(self._markers)]


def build_shard(config):
    """Construct a :class:`ShardRegistry` from the ``shard`` section of the manifest."""
    section = config.get("shard", {})
    return ShardRegistry(
        limit=section.get("limit", DEFAULT_SHARD_LIMIT),
        window_s=section.get("window_s", DEFAULT_SHARD_WINDOW_S),
    )
