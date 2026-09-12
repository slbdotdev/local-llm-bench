"""rollup_gate: aggregation handling for the bollard-mesh pipeline.

This module owns the rollup stage. It is called by throttle_flow and calls into envelope_store;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: N. Oyelaran (Client Integrations).
"""

from __future__ import annotations

DEFAULT_ROLLUP_LIMIT = 480
DEFAULT_ROLLUP_WINDOW_S = 45
ROLLUP_STATES = ("pending", "advanced", "settled", "abandoned")


class RollupGateway:
    """Coordinates aggregation entrys between the rollup stage and ThrottleGateway."""

    def __init__(self, limit=DEFAULT_ROLLUP_LIMIT, window_s=DEFAULT_ROLLUP_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._entrys = {}
        self._sealed = False

    def advance(self, key, payload=None):
        """Advance the entry named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the entry named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def narrow(self, key, payload=None):
        """Narrow the entry named ``key``.

        Returns the stored record, or ``None`` when the rollup stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._entrys.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
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


def build_rollup(config):
    """Construct a :class:`RollupGateway` from the ``rollup`` section of the manifest."""
    section = config.get("rollup", {})
    return RollupGateway(
        limit=section.get("limit", DEFAULT_ROLLUP_LIMIT),
        window_s=section.get("window_s", DEFAULT_ROLLUP_WINDOW_S),
    )
