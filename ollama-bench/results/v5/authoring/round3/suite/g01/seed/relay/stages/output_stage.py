"""Final public-shape checks for the in-memory adapter."""


def bucket(source):
    return {"source": source, "entries": []}


def entry(key, total, occurrences, labels):
    return {
        "key": key,
        "total": total,
        "occurrences": occurrences,
        "labels": list(labels),
    }


def fields(value):
    return set(value)


PUBLIC_BUCKET_FIELDS = {"source", "entries"}
PUBLIC_ENTRY_FIELDS = {"key", "total", "occurrences", "labels"}


def shape_ok(value):
    if not isinstance(value, list):
        return False
    return all(fields(item) == PUBLIC_BUCKET_FIELDS for item in value)


def no_private_fields(value):
    return all("positions" not in item and "action" not in item for item in value)
