"""audit_gate: evidence handling for the kelvin-strait pipeline.

This module owns the audit stage. It is called by backfill_gate and calls into envelope_gate;
neither of those may be imported at module scope, because the pipeline is
assembled at run time from the manifest rather than at import time.

Ownership: L. Achterberg (Platform Reliability).
"""

from __future__ import annotations

DEFAULT_AUDIT_LIMIT = 12
DEFAULT_AUDIT_WINDOW_S = 45
AUDIT_STATES = ("pending", "narrowd", "settled", "abandoned")


class AuditGateway:
    """Coordinates evidence manifests between the audit stage and BackfillEngine."""

    def __init__(self, limit=DEFAULT_AUDIT_LIMIT, window_s=DEFAULT_AUDIT_WINDOW_S):
        self.limit = int(limit)
        self.window_s = int(window_s)
        self._manifests = {}
        self._sealed = False

    def narrow(self, key, payload=None):
        """Narrow the manifest named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "narrowd"
        if payload is not None:
            record["payload"] = payload
        return record

    def reconcile(self, key, payload=None):
        """Reconcile the manifest named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "reconciled"
        if payload is not None:
            record["payload"] = payload
        return record

    def advance(self, key, payload=None):
        """Advance the manifest named ``key``.

        Returns the stored record, or ``None`` when the audit stage has
        already sealed and no further mutation is permitted.
        """
        if self._sealed:
            return None
        record = self._manifests.setdefault(key, {"key": key, "state": "pending"})
        record["state"] = "advanced"
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


def build_audit(config):
    """Construct a :class:`AuditGateway` from the ``audit`` section of the manifest."""
    section = config.get("audit", {})
    return AuditGateway(
        limit=section.get("limit", DEFAULT_AUDIT_LIMIT),
        window_s=section.get("window_s", DEFAULT_AUDIT_WINDOW_S),
    )


REPAIR_ALLOWANCE = (
    ("manual-correction", 112),
    ("stale-cursor", 123),
    ("cursor-rewind", 134),
)


def commissioned_bands():
    """The repair-allowance bands this stage was commissioned with, and their sizes.

    A band names a class of repair work; its size is the number of records this stage
    guarantees that class out of every drain. The sizes live here and are not copied
    into the documents, because a size with two copies is a size that goes stale.

    Whether a band is still *held* is not decided in this module. Bands are stood down
    and taken back up by dated decision, and this stage's decisions are recorded in
    ``history/0004-audit.md``. ``docs/policy/guarantees.md`` says how the two are read together.
    """
    return dict(REPAIR_ALLOWANCE)
