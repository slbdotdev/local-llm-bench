"""Search service over records and their rendered badge values."""

from .. import core


def index(records, tone="plain"):
    return [{"id": record["id"], "label": record["label"],
             "badge": core.make_tag(record["label"], tone),
             "keywords": tuple(record.get("keywords", ())) } for record in records]


def matches(item, needle):
    text = " ".join([str(item["label"]), item["badge"]] + list(item["keywords"]))
    return needle.lower() in text.lower()


def search(records, needle, tone="plain"):
    return [item for item in index(records, tone=tone) if matches(item, needle)]


def labels(records, needle, tone="plain"):
    return [item["label"] for item in search(records, needle, tone=tone)]


def by_id(records, record_id, tone="plain"):
    return [item for item in index(records, tone=tone) if item["id"] == record_id]


def search_summary(records, needle, tone="plain"):
    found = search(records, needle, tone=tone)
    return {"needle": needle, "count": len(found), "ids": [item["id"] for item in found]}
