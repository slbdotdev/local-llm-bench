"""Chat integration with channel and thread messages."""

from .. import core


def post(channel, label, tone="plain"):
    return {"channel": channel, "text": core.make_tag(label, tone)}


def post_many(channel, labels, tone="plain"):
    return [post(channel, label, tone=tone) for label in labels]


def thread(channel, parent, replies, tone="plain"):
    return {"channel": channel, "parent": post(channel, parent, tone),
            "replies": post_many(channel, replies, tone=tone)}


def channels(messages):
    return sorted({message["channel"] for message in messages})


def by_channel(messages, channel):
    return [message for message in messages if message["channel"] == channel]
