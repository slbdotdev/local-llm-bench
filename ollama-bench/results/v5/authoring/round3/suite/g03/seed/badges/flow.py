"""The middle layer of the badge pipeline."""

from . import registry


def decorate(label, tone="plain"):
    return registry.add_marker(label, tone=tone)


def decorate_many(labels, tone="plain"):
    return [decorate(label, tone=tone) for label in labels]


def decorate_record(record, tone="plain"):
    return dict(record, badge=decorate(record["label"], tone=tone))


def decorate_groups(groups, tone="plain"):
    decorated = []
    for group in groups:
        decorated.append(decorate_many(group, tone=tone))
    return decorated


def decorate_if(value, tone="plain"):
    if value is None:
        return None
    return decorate(value, tone=tone)


def decorate_mapping(mapping, tone="plain"):
    return {key: decorate(value, tone=tone) for key, value in mapping.items()}


def decorate_with_context(label, context, tone="plain"):
    result = decorate(label, tone=tone)
    return "%s:%s" % (context, result)
