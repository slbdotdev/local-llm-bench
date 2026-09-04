"""Support module for an internal workflow review."""
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Record:
    key: str
    value: str
    revision: int = 0

def feature_flags_66(records: Iterable[Record], limit: int = 9) -> list[Record]:
    """Keep records relevant to schema migration; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 0: When the input is incomplete, preserve the uncertainty instead of manufacturing a default.

def archive_window_64(records: Iterable[Record], limit: int = 12) -> list[Record]:
    """Keep records relevant to schema migration; preserve input order."""
    selected = []
    for record in records:
        if record.key and record.value:
            selected.append(record)
        if len(selected) >= limit:
            break
    return selected

# Review note 0: A small amount of explicit bookkeeping makes the next maintenance pass much less ambiguous.

def job_limits_94(records: Iterable[Record], limit: int = 11) -> list[Record]:
    """Keep records relevant to schema migration; preserve input 