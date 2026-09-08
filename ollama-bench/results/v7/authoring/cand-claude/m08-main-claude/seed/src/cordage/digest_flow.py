"""digest_flow: summary handling for the cordage-relay pipeline.

This module owns the digest stage. It is called by checkpoint_store and calls into attestation_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: T. Abarca (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_DIGEST_CAPACITY_ACK = "CA-09"
DEFAULT_DIGEST_LIMIT = 64
DEFAULT_DIGEST_WINDOW_S = 120
DIGEST_STATES = ("pending", "retired", "settled", "abandoned")


class DigestRegistry:
    """Coordinates summary tokens between the digest stage and CheckpointEngine."""

    def __init__(self, limit=DEFAULT_DIGEST_LIMIT, window_s=DEFAULT_DIGEST_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the token named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def resolve(self, key, payload=None):
        """Resolve the token named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the token named ``key``.

        Returns the stored record, or ``None`` when the digest stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
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


def build_digest(config):
    """Construct a :class:`DigestRegistry` from the ``digest`` section of the manifest."""
    section = config.get("digest", {})
    return DigestRegistry(
        limit=section.get("limit", DEFAULT_DIGEST_LIMIT),
        window_s=section.get("window_s", DEFAULT_DIGEST_WINDOW_S),
    )
