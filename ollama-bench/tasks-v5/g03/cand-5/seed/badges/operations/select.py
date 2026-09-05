"""Selection operations with explicit inclusion and exclusion semantics."""

from .. import core


def include(labels, wanted, tone="plain"):
    return core.batch([label for label in labels if label in wanted], tone=tone)


def exclude(labels, unwanted, tone="plain"):
    return core.batch([label for label in labels if label not in unwanted], tone=tone)


def at(labels, indexes, tone="plain"):
    return core.batch([labels[index] for index in indexes], tone=tone)


def first_match(labels, predicate, tone="plain"):
    for label in labels:
        if predicate(label):
            return core.make_tag(label, tone)
    return None


def select_records(records, predicate, tone="plain"):
    return [dict(record, badge=core.make_tag(record["label"], tone))
            for record in records if predicate(record)]
