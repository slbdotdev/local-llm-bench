"""tenancy_core: isolation handling for the cinder-parcel pipeline.

This module owns the tenancy stage. It is called by replay_view and calls into compaction_view;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: E. Thorsdottir (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_TENANCY_LIMIT = 96
DEFAULT_TENANCY_WINDOW_S = 60
TENANCY_STATES = ("pending", "settled", "settled", "abandoned")


class TenancyEngine:
    """Coordinates isolation manifests between the tenancy stage and ReplayEngine."""

    def __init__(self, limit=DEFAULT_TENANCY_LIMIT, window_s=DEFAULT_TENANCY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def settle(self, key, payload=None):
        """Settle the manifest named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def coalesce(self, key, payload=None):
        """Coalesce the manifest named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "coalesced"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the manifest named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._manifests)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._manifests[k] for k in sorted(self._manifests)]


def build_tenancy(config):
    """Construct a :class:`TenancyEngine` from the ``tenancy`` section of the manifest."""
    section = config.get("tenancy", {})
    return TenancyEngine(
        limit=section.get("limit", DEFAULT_TENANCY_LIMIT),
        window_s=section.get("window_s", DEFAULT_TENANCY_WINDOW_S),
    )
