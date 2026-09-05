"""Policy decisions that select a badge tone and then build it."""

from . import core

PRIORITY_TONES = {"urgent": "loud", "notice": "warm", "quiet": "muted"}


def tone_for(priority, fallback="plain"):
    return PRIORITY_TONES.get(priority, fallback)


def policy_badge(label, priority="quiet"):
    tone = tone_for(priority)
    return core.make_tag(label, tone)


def policy_many(items, priority="quiet"):
    tone = tone_for(priority)
    return [core.make_tag(item, tone) for item in items]


def policy_records(records):
    return [dict(record, badge=policy_badge(record["label"], record["priority"]))
            for record in records]


def escalated(records):
    return policy_records([dict(record, priority="urgent") for record in records])


def policy_summary(records):
    values = policy_records(records)
    return {"count": len(values), "badges": [item["badge"] for item in values]}
