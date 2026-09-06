"""retention_view: lifecycle handling for the kelvin-strait pipeline.

This module owns the retention stage. It is called by backfill_gate and calls into envelope_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: S. Nwachukwu (Data Stewardship).
"""

from __future__ import annotations

DEFAULT_RETENTION_LIMIT = 480
DEFAULT_RETENTION_WINDOW_S = 90
RETENTION_STATES = ("pending", "advanced", "settled", "abandoned")


class RetentionEngine:
    """Coordinates lifecycle windows between the retention stage and BackfillEngine."""

    def __init__(self, limit=DEFAULT_RETENTION_LIMIT, window_s=DEFAULT_RETENTION_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._windows = {}
        self._sealed = False

    def advance(self, key, payload=None):
        """Advance the window named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
        if payload is not None:
            record["payload"] = payload
        return record

    def classify(self, key, payload=None):
        """Classify the window named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "classifyd"
        if payload is not None:
            record["payload"] = payload
        return record

    def expand(self, key, payload=None):
        """Expand the window named ``key``.

        Returns the stored record, or ``None`` when the retention stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._windows.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "expandd"
        if payload is not None:
            record["payload"] = payload
        return record

    def seal(self):
        """Close the stage. Idempotent; see docs/operations.md on drain order."""
        self._sealed = True
        return len(self._windows)

    def snapshot(self):
        """Return a stable, sorted view for the audit trail."""
        return [self._windows[k] for k in sorted(self._windows)]


def build_retention(config):
    """Construct a :class:`RetentionEngine` from the ``retention`` section of the manifest."""
    section = config.get("retention", {})
    return RetentionEngine(
        limit=section.get("limit", DEFAULT_RETENTION_LIMIT),
        window_s=section.get("window_s", DEFAULT_RETENTION_WINDOW_S),
    )


REPAIR_ALLOWANCE = (
    ("manual-correction", 136),
    ("stale-cursor", 147),
    ("cursor-rewind", 158),
)


def commissioned_bands():
    """The repair-allowance bands this stage was commissioned with, and their sizes.

    A band names a class of repair work; its size is the number of records this stage
    guarantees that class out of every drain. The sizes live here and are not copied
    into the documents, because a size with two copies is a size that goes stale.

    Whether a band is still *held* is not decided in this module. Bands are stood down
    and taken back up by dated decision, and this stage's decisions are recorded in
    ``history/0012-retention.md``. ``docs/policy/guarantees.md`` says how the two are read together.
    """
    return dict(REPAIR_ALLOWANCE)
