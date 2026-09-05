"""Mirror backend applies a selected tone to an existing record stream."""

from .. import core


def mirror(record, tone="plain"):
    copy = dict(record)
    copy["badge"] = core.make_badge(record["label"], tone=tone)
    return copy


def mirror_all(records, tone="plain"):
    return [mirror(record, tone=tone) for record in records]


def mirror_map(mapping, tone="plain"):
    return {key: core.make_badge(value, tone=tone) for key, value in mapping.items()}


def compare(left, right, tone="plain"):
    return {"left": mirror_all(left, tone=tone), "right": mirror_all(right, tone=tone),
            "same_size": len(left) == len(right)}


def reconcile(primary, secondary, tone="plain"):
    seen = set()
    merged = []
    for record in list(primary) + list(secondary):
        if record["id"] not in seen:
            seen.add(record["id"])
            merged.append(mirror(record, tone=tone))
    return merged
