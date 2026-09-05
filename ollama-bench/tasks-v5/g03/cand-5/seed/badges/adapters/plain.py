"""Plain-text adapter for logs and command-line output."""

from .. import core


def line(label, tone="plain"):
    return core.make_tag(label, tone)


def lines(labels, tone="plain"):
    return [line(label, tone=tone) for label in labels]


def block(labels, tone="plain"):
    return "\n".join(lines(labels, tone=tone))


def numbered(labels, tone="plain"):
    return ["%d. %s" % (number, line(label, tone=tone))
            for number, label in enumerate(labels, 1)]


def key_value(mapping, tone="plain"):
    return ["%s=%s" % (key, line(value, tone=tone)) for key, value in mapping.items()]
