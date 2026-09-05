"""Mail integration uses badges in subject and plain body fields."""

from .. import core, formatting


def subject(label, tone="plain"):
    return "[Badge] %s" % core.make_tag(label, tone)


def body(labels, tone="plain"):
    return formatting.render_many(labels, tone=tone, separator="\n")


def message(to, label, tone="plain"):
    return {"to": to, "subject": subject(label, tone),
            "body": body([label], tone=tone)}


def digest(to, labels, tone="plain"):
    return {"to": to, "subject": "Badge digest", "body": body(labels, tone=tone)}


def messages(addresses, labels, tone="plain"):
    return [message(address, label, tone=tone) for address, label in zip(addresses, labels)]
