"""Composite rule evaluation applies visibility, expiry, and ownership."""

from . import expiry, ownership, visibility


def allowed(record, owner, audience, now):
    return (visibility.visible(record, audience=audience)
            and expiry.active(record, now) and ownership.owns(record, owner))


def render(record, owner, audience, now, tone="plain"):
    if not allowed(record, owner, audience, now):
        return None
    return ownership.render(record, owner=owner, tone=tone)


def render_all(records, owner, audience, now, tone="plain"):
    return [render(record, owner, audience, now, tone=tone) for record in records]


def accepted(records, owner, audience, now):
    return [record for record in records if allowed(record, owner, audience, now)]


def report(records, owner, audience, now, tone="plain"):
    values = render_all(records, owner, audience, now, tone=tone)
    return {"accepted": sum(value is not None for value in values), "values": values}
