"""Review predicates for public result values."""


def fresh_shape(result):
    if not isinstance(result, list):
        return False
    for bucket in result:
        if set(bucket) != {"source", "entries"} or not isinstance(bucket["entries"], list):
            return False
        for entry in bucket["entries"]:
            if set(entry) != {"key", "total", "occurrences", "labels"}:
                return False
            if not isinstance(entry["labels"], list):
                return False
    return True


def strictly_first_seen(values):
    return values == list(dict.fromkeys(values))


def no_empty_labels(labels):
    return all(value != "" for value in labels)


REVIEW_ITEMS = (
    "bucket exists before policy",
    "rejected change creates no entry",
    "accepted zero still counts",
    "source aliases merge",
    "key aliases merge",
    "labels are canonical and ordered",
    "outer order is temporal",
    "inner order is temporal",
    "input remains untouched",
)
