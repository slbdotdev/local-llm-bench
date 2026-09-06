"""tenancy_gate: isolation handling for the brindle-quay pipeline.

This module owns the tenancy stage. It is called by rollup_store and calls into digest_flow;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: C. Batbayar (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_TENANCY_LIMIT = 32
DEFAULT_TENANCY_WINDOW_S = 30
TENANCY_STATES = ("pending", "retired", "settled", "abandoned")


class TenancyGateway:
    """Coordinates isolation entrys between the tenancy stage and RollupEngine."""

    def __init__(self, limit=DEFAULT_TENANCY_LIMIT, window_s=DEFAULT_TENANCY_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def retire(self, key, payload=None):
        """Retire the entry named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "retired"
        if payload is not None:
            record["payload"] = payload
        return record

    def settle(self, key, payload=None):
        """Settle the entry named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "settled"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the entry named ``key``.

        Returns the stored record, or ``None`` when the tenancy stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._entrys)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._entrys[k] for k in sorted(self._entrys)]


def build_tenancy(config):
    """Construct a :class:`TenancyGateway` from the ``tenancy`` section of the manifest."""
    section = config.get("tenancy", {})
    return TenancyGateway(
        limit=section.get("limit", DEFAULT_TENANCY_LIMIT),
        window_s=section.get("window_s", DEFAULT_TENANCY_WINDOW_S),
    )
