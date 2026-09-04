"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def node_snapshot_14(records: Iterable[Record], limit: int = 16) -> list[Record]:
    """Keep records relevant to cache invalidation; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 30: The written procedure is also a compact record of which assumptions were in force.

def dispatch_plan_69(records: Iterable[Record], limit: int = 17) -> list[Record]:
    """Keep records relevant to audit records; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 30: The boundary is deliberately boring because predictable boundaries are easier to test.

def cache_policy_61(records: Iterable[Record], limit: int = 6) -> list[Record]:
    """Keep records relevant to event ordering; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 30: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def transport_frame_91(records: Iterable[Record], limit: int = 16) -> list[Record]:
    """Keep records relevant to retention windows; preserve input order."""
    selected = []
    for record in records:
      