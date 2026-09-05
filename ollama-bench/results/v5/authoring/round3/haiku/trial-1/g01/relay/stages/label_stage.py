"""Stage five: canonical labels and first-seen merge."""


def canonical(label):
    return label.strip(" ").casefold()


def merge(target, raw_labels):
    seen = set(target)
    for raw in raw_labels:
        label = canonical(raw)
        if label and label not in seen:
            target.append(label)
            seen.add(label)


def initial(raw_labels):
    target = []
    merge(target, raw_labels)
    return target


LABEL_REVIEW = (
    (["One", " one ", "Two"], ["one", "two"]),
    ([" ", "\t", "\t"], ["\t"]),
    (["A", "b", "A", " B "], ["a", "b"]),
    (["first"], ["first"]),
)


def merge_is_monotonic(old, raw_labels):
    before = list(old)
    merge(old, raw_labels)
    return old[:len(before)] == before
