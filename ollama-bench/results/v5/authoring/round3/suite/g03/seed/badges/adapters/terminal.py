"""Terminal adapter that adds stable emphasis markers."""

from .. import core

PREFIX = {"plain": "", "warm": "! ", "cool": "~ ", "muted": ". ", "loud": "!! "}


def line(label, tone="plain"):
    return PREFIX[tone] + core.make_tag(label, tone)


def lines(labels, tone="plain"):
    return [line(label, tone=tone) for label in labels]


def panel(title, labels, tone="plain"):
    body = lines(labels, tone=tone)
    return "[%s]\n%s" % (title, "\n".join(body))


def columns(columns, tone="plain"):
    rendered = [lines(column, tone=tone) for column in columns]
    width = max((len(column) for column in rendered), default=0)
    return [" | ".join(column[index] if index < len(column) else ""
                         for column in rendered) for index in range(width)]


def status(label, ok=True, tone="plain"):
    marker = "OK" if ok else "FAIL"
    return "%s: %s" % (marker, line(label, tone=tone))
