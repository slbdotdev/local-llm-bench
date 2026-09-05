"""Activity view for ordered badge events."""

from .. import core


def activity_item(event, tone="plain"):
    return {"at": event["at"], "actor": event["actor"],
            "badge": core.make_tag(event["label"], tone)}


def activity(events, tone="plain"):
    ordered = sorted(events, key=lambda event: event["at"])
    return [activity_item(event, tone=tone) for event in ordered]


def actors(events):
    return sorted({event["actor"] for event in events})


def by_actor(events, actor, tone="plain"):
    return activity([event for event in events if event["actor"] == actor], tone=tone)


def latest(events, count=1, tone="plain"):
    return activity(events, tone=tone)[-count:]
