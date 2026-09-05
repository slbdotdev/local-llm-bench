"""JSON plugin used by the machine-readable endpoint."""

import json

from .. import core, serializing

FIELDS = ("id", "label", "tone", "badge")


def view_record(record, tone="plain"):
    item = {"id": record["id"], "label": record["label"], "tone": tone}
    item["badge"] = core.make_tag(record["label"], tone)
    return item


def view_records(records, tone="plain"):
    return [view_record(record, tone=tone) for record in records]


def dump_record(record, tone="plain"):
    return json.dumps(view_record(record, tone=tone), sort_keys=True)


def dump_records(records, tone="plain"):
    return json.dumps(view_records(records, tone=tone), sort_keys=True)


def compact_records(records, tone="plain"):
    return [serializing.compact_record(record, tone=tone) for record in records]


def select_fields(record, tone="plain"):
    value = view_record(record, tone=tone)
    return {key: value[key] for key in FIELDS}
