"""Compliance rules reject disallowed labels before rendering."""

from .. import core

FORBIDDEN = frozenset(("secret", "private", "password", "token"))


def compliant(label):
    return not any(word in str(label).lower() for word in FORBIDDEN)


def render(label, tone="plain"):
    if not compliant(label):
        return "[redacted]"
    return core.make_badge(label, tone=tone)


def render_all(labels, tone="plain"):
    return [render(label, tone=tone) for label in labels]


def rejected(labels):
    return [label for label in labels if not compliant(label)]


def accepted(labels):
    return [label for label in labels if compliant(label)]


def report(labels, tone="plain"):
    return {"accepted": len(accepted(labels)), "rejected": len(rejected(labels)),
            "values": render_all(labels, tone=tone)}
