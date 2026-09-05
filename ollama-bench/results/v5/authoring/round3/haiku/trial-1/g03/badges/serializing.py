"""Serialization-oriented consumers of the badge API."""

import json

from . import core


def as_dict(label, tone="plain"):
    return {"label": label, "badge": core.make_badge(label, tone=tone), "tone": tone}


def as_json(label, tone="plain"):
    return json.dumps(as_dict(label, tone=tone), sort_keys=True)


def many_as_dict(labels, tone="plain"):
    return [as_dict(label, tone=tone) for label in labels]


def many_as_json(labels, tone="plain"):
    return json.dumps(many_as_dict(labels, tone=tone), sort_keys=True)


def round_trip(label, tone="plain"):
    value = json.loads(as_json(label, tone=tone))
    return value["badge"] == core.make_badge(label, tone=tone)


def compact_record(record, tone="plain"):
    return json.dumps({"id": record["id"],
                       "value": core.make_badge(record["label"], tone=tone)})
