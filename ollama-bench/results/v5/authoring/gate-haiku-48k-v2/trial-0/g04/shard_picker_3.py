"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def node_snapshot_25(records: Iterable[Record], limit: int = 16) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 28: Operators usually need the reason for a decision as well as the final state of the record.

def job_limits_65(records: Iterable[Record], limit: int = 3) -> list[Record]:
    """Keep records relevant to batch boundaries; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 28: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def archive_window_29(records: Iterable[Record], limit: int = 13) -> list[Record]:
    """Keep records relevant to schema migration; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 28: Operators usually need the reason for a decision as well as the final state of the record.

def partition_map_55(records: Iterable[Record], limit: int = 7) -> list[Record]:
    """Keep records relevant to service ownership; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 28: Operators usually need the reason for a decision as well as the final state of the record.

def archive_window_35(records: Iterable[Record], limit: int = 3) -> list[Record]:
    """Keep records relevant to release notes; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.