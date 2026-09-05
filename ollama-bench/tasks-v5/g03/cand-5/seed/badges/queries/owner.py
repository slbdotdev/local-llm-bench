"""Owner query."""

from .. import core


def run(records, owner, tone="plain"):
    return [dict(record, badge=core.make_tag(record["label"], tone))
            for record in records if record.get("owner") == owner]


def labels(records, owner, tone="plain"):
    return [record["badge"] for record in run(records, owner, tone=tone)]


def count(records, owner):
    return sum(record.get("owner") == owner for record in records)


def owners(records):
    return sorted({record.get("owner") for record in records})


def summary(records, tone="plain"):
    return {owner: labels(records, owner, tone=tone) for owner in owners(records)}
