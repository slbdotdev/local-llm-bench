"""Accessors isolate record shape from badge construction."""

from . import core


def label_of(record):
    return record["label"]


def id_of(record):
    return record.get("id")


def badge_of(record, tone="plain"):
    return core.make_badge(label_of(record), tone=tone)


def project(record, tone="plain"):
    return {"id": id_of(record), "label": label_of(record),
            "badge": badge_of(record, tone=tone)}


def project_all(records, tone="plain"):
    return [project(record, tone=tone) for record in records]


def labels(records):
    return [label_of(record) for record in records]


def badges(records, tone="plain"):
    return [badge_of(record, tone=tone) for record in records]
