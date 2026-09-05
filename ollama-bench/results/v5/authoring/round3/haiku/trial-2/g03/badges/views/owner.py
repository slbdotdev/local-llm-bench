"""Owner view groups record badges by accountable person."""

from .. import core


def owner_record(record, tone="plain"):
    return {"owner": record["owner"], "badge": core.make_badge(record["label"], tone=tone)}


def owner_view(records, tone="plain"):
    result = {}
    for record in records:
        result.setdefault(record["owner"], []).append(owner_record(record, tone))
    return result


def owners(records):
    return sorted({record["owner"] for record in records})


def owner_count(records):
    return {owner: sum(record["owner"] == owner for record in records)
            for owner in owners(records)}


def owner_badges(records, owner, tone="plain"):
    return [item["badge"] for item in owner_view(records, tone=tone).get(owner, [])]
