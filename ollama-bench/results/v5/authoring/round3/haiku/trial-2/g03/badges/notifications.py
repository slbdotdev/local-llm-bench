"""Notification formatting shared by email and in-app channels."""

from . import core, policies


CHANNELS = ("email", "in_app", "webhook")


def subject(label, priority="quiet"):
    return "%s: %s" % (priority.upper(), label)


def notification(label, priority="quiet", tone=None):
    actual_tone = policies.tone_for(priority) if tone is None else tone
    return {"subject": subject(label, priority),
            "badge": core.make_badge(label, tone=actual_tone), "priority": priority}


def notify_many(labels, priority="quiet", tone=None):
    return [notification(label, priority=priority, tone=tone) for label in labels]


def channel_message(channel, label, priority="quiet", tone=None):
    value = notification(label, priority=priority, tone=tone)
    value["channel"] = channel
    return value


def digest(groups, priority="quiet"):
    return [notify_many(group, priority=priority) for group in groups]


def count_channels(messages):
    return {channel: sum(message.get("channel") == channel for message in messages)
            for channel in CHANNELS}
