"""dispatch_gate: fanout handling for the cinder-vault pipeline.

This module owns the dispatch stage. It is called by cursor_view and calls into replay_core;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: M. Lindqvist (Compliance Review).
"""

from __future__ import annotations

DEFAULT_DISPATCH_LIMIT = 120
DEFAULT_DISPATCH_WINDOW_S = 60
DISPATCH_STATES = ("pending", "resolved", "settled", "abandoned")


class DispatchLedger:
    """Coordinates fanout manifests between the dispatch stage and CursorGateway."""

    def __init__(self, limit=DEFAULT_DISPATCH_LIMIT, window_s=DEFAULT_DISPATCH_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def resolve(self, key, payload=None):
        """Resolve the manifest named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "resolved"
        if payload is not None:
            record["payload"] = payload
        return record

    def admit(self, key, payload=None):
        """Admit the manifest named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "admitd"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the manifest named ``key``.

        Returns the stored record, or ``None`` when the dispatch stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
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

    def reap(self, ages):
        """Reap records that have waited longer than ``window_s``.

        Per ``docs/policy/03-retention.md``, reaping is a change of state, not a
        removal: a reaped record's ``state`` becomes ``"abandoned"``, it stays in
        the stage and stays visible to ``snapshot()``, and it stops counting
        against ``limit``. A key ``ages`` does not recognise is ignored, and a
        record already in a terminal state (``"settled"`` or ``"abandoned"``) is
        left alone, so reaping the same record twice reaps it only once.

        Returns the number of records reaped by this call, as an int.
        """
        reaped = 0
        for key, age in ages.items():
            record = self._manifests.get(key)
            if record is None:
                continue
            if record["state"] in ("settled", "abandoned"):
                continue
            if int(age) > self.window_s:
                record["state"] = "abandoned"
                reaped += 1
        return reaped

    def active_count(self):
        """Return how many records currently count against ``limit``.

        Per ``docs/policy/03-retention.md``, a record counts against the stage's
        ``limit`` from acceptance until it reaches ``"settled"`` or
        ``"abandoned"``; every other state, including intermediate ones, counts.
        """
        return sum(
            1
            for record in self._manifests.values()
            if record["state"] not in ("settled", "abandoned")
        )


def build_dispatch(config):
    """Construct a :class:`DispatchLedger` from the ``dispatch`` section of the manifest."""
    section = config.get("dispatch", {})
    return DispatchLedger(
        limit=section.get("limit", DEFAULT_DISPATCH_LIMIT),
        window_s=section.get("window_s", DEFAULT_DISPATCH_WINDOW_S),
    )
