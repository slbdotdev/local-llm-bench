"""Reindex job creates searchable badge records."""

from .. import core


def tokens(label):
    return tuple(str(label).lower().replace("-", " ").split())


def index_record(record, tone="plain"):
    label = record["label"]
    return {"id": record["id"], "label": label,
            "tokens": tokens(label), "badge": core.make_badge(label, tone=tone)}


def reindex(records, tone="plain"):
    return [index_record(record, tone=tone) for record in records]


def find(index, token):
    return [record for record in index if token.lower() in record["tokens"]]


def ids(index, token):
    return [record["id"] for record in find(index, token)]


def reindex_map(records, tone="plain"):
    return {record["id"]: index_record(record, tone=tone) for record in records}
