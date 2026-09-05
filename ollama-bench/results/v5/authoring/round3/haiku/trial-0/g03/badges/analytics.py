"""Analytics helpers for badge usage and tone distributions."""

from . import core

EVENT_TYPES = ("created", "updated", "viewed", "archived")


def event(label, kind="created", tone="plain"):
    return {"kind": kind, "label": label, "badge": core.make_badge(label, tone=tone)}


def events(labels, kind="created", tone="plain"):
    return [event(label, kind=kind, tone=tone) for label in labels]


def count_by_kind(records):
    result = {kind: 0 for kind in EVENT_TYPES}
    for record in records:
        result[record["kind"]] = result.get(record["kind"], 0) + 1
    return result


def count_by_tone(records):
    result = {}
    for record in records:
        tone = record.get("tone", "plain")
        result[tone] = result.get(tone, 0) + 1
    return result


def project(records, tone="plain"):
    return [{"kind": record["kind"], "badge": core.make_badge(record["label"], tone=tone)}
            for record in records]


def timeline(records, tone="plain"):
    return [event(record["label"], record["kind"], tone) for record in records]


def report(records, tone="plain"):
    return {"kinds": count_by_kind(records), "items": project(records, tone=tone),
            "total": len(records)}
