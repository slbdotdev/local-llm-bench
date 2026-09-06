"""quota_core: limits handling for the cinder-parcel pipeline.

This module owns the quota stage. It is called by replay_view and calls into compaction_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Client Integrations).
"""

from __future__ import annotations

DEFAULT_QUOTA_LIMIT = 12
DEFAULT_QUOTA_WINDOW_S = 45
REGION_OFFSET = 121
QUOTA_STATES = ("pending", "expandd", "settled", "abandoned")


class QuotaEngine:
    """Coordinates limits tokens between the quota stage and ReplayEngine."""

    def __init__(self, limit=DEFAULT_QUOTA_LIMIT, window_s=DEFAULT_QUOTA_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._tokens = {}
        self._sealed = False

    def expand(self, key, payload=None):
        """Expand the token named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def defer(self, key, payload=None):
        """Defer the token named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._tokens.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "deferd"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the token named ``key``.

        Returns the stored record, or ``None`` when the quota stage has
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


def build_quota(config):
    """Construct a :class:`QuotaEngine` from the ``quota`` section of the manifest."""
    section = config.get("quota", {})
    return QuotaEngine(
        limit=section.get("limit", DEFAULT_QUOTA_LIMIT),
        window_s=section.get("window_s", DEFAULT_QUOTA_WINDOW_S),
    )
