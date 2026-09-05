"""Expiry rules for time-bounded badge records."""

from .. import core


def active(record, now):
    return record.get("expires", now + 1) > now


def render(record, now, tone="plain"):
    if not active(record, now):
        return "[expired]"
    return core.make_badge(record["label"], tone=tone)


def render_all(records, now, tone="plain"):
    return [render(record, now, tone=tone) for record in records]


def expired(records, now):
    return [record for record in records if not active(record, now)]


def active_records(records, now):
    return [record for record in records if active(record, now)]


def summary(records, now, tone="plain"):
    return {"active": len(active_records(records, now)),
            "expired": len(expired(records, now)),
            "values": render_all(records, now, tone=tone)}
