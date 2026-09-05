"""Storage migration records, including the current badge representation."""

from .. import core

MIGRATIONS = ((1, "initial"), (2, "owner"), (3, "tone"), (4, "badge"))


def current():
    return MIGRATIONS[-1][0]


def names():
    return [name for _, name in MIGRATIONS]


def migrate(record, version=current(), tone="plain"):
    value = dict(record)
    if version >= 2:
        value.setdefault("owner", "unknown")
    if version >= 3:
        value.setdefault("tone", tone)
    if version >= 4:
        value["badge"] = core.make_badge(value["label"], tone=value.get("tone", tone))
    return value


def migrate_all(records, version=current(), tone="plain"):
    return [migrate(record, version=version, tone=tone) for record in records]


def pending(version):
    return [name for number, name in MIGRATIONS if number > version]
