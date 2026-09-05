"""Versioned export façade used by the release workflow."""

from . import core, formatting

VERSION = 2
FIELDS = ("label", "badge", "tone")


def value(label, tone="plain"):
    badge = core.make_badge(label, tone=tone)
    return {"label": label, "badge": badge, "tone": tone, "version": VERSION}


def values(labels, tone="plain"):
    return [value(label, tone=tone) for label in labels]


def text(labels, tone="plain"):
    return formatting.render_many(labels, tone=tone, separator=";")


def package(labels, tone="plain"):
    return {"version": VERSION, "fields": FIELDS,
            "values": values(labels, tone=tone), "text": text(labels, tone=tone)}


def select(package_value, fields=FIELDS):
    return [{field: item[field] for field in fields if field in item}
            for item in package_value["values"]]
