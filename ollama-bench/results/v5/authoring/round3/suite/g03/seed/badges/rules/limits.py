"""Length and count rules for badge rendering."""

from .. import core


def within_length(label, maximum=40):
    return len(str(label)) <= maximum


def render(label, tone="plain", maximum=40):
    if not within_length(label, maximum=maximum):
        return "[too long]"
    return core.make_tag(label, tone)


def render_all(labels, tone="plain", maximum=40):
    return [render(label, tone=tone, maximum=maximum) for label in labels]


def accepted(labels, maximum=40):
    return [label for label in labels if within_length(label, maximum=maximum)]


def rejected(labels, maximum=40):
    return [label for label in labels if not within_length(label, maximum=maximum)]
