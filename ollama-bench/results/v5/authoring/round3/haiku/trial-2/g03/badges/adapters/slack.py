"""Slack-like adapter with a deterministic message shape."""

from .. import core

COLORS = {"plain": "#999999", "warm": "#ff9900", "cool": "#3399ff",
          "muted": "#777777", "loud": "#ff3333"}


def attachment(label, tone="plain"):
    return {"text": core.make_badge(label, tone=tone), "color": COLORS[tone]}


def message(labels, tone="plain"):
    return {"attachments": [attachment(label, tone) for label in labels]}


def threaded(parent, replies, tone="plain"):
    return {"parent": attachment(parent, tone),
            "replies": [attachment(reply, tone) for reply in replies]}


def sections(groups, tone="plain"):
    return [{"text": "\n".join(core.batch(group, tone=tone))} for group in groups]


def mention(user, label, tone="plain"):
    return "<@%s> %s" % (user, core.make_badge(label, tone=tone))
