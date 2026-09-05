"""Ownership rules produce per-owner badge views."""

from .. import core


def owns(record, owner):
    return record.get("owner") == owner


def render(record, owner, tone="plain"):
    if not owns(record, owner):
        return None
    return core.make_tag(record["label"], tone)


def render_for(records, owner, tone="plain"):
    return [render(record, owner=owner, tone=tone) for record in records]


def owned(records, owner):
    return [record for record in records if owns(record, owner)]


def owners(records):
    return sorted({record.get("owner") for record in records})


def owner_map(records, tone="plain"):
    return {owner: render_for(records, owner, tone=tone) for owner in owners(records)}
