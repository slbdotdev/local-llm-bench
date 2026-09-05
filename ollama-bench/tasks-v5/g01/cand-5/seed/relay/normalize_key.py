"""Key normalization review, kept separate from source normalization."""

from .release_data import GLOBAL_KEY_ALIASES, SOURCE_KEY_ALIASES


def key_name(source, raw):
    value = raw.strip(" ").casefold()
    value = GLOBAL_KEY_ALIASES.get(value, value)
    return SOURCE_KEY_ALIASES.get(source, {}).get(value, value)


def label_name(raw):
    return raw.strip(" ").casefold()


def labels_in_order(raw_labels):
    result = []
    for raw in raw_labels:
        value = label_name(raw)
        if value and value not in result:
            result.append(value)
    return result


KEY_REVIEW = (
    ("platform", " err ", "error"),
    ("service", "REQ", "requests"),
    ("frontend", " Draw ", "render"),
    ("worker", "TASK", "jobs"),
    ("unknown", " warn ", "warning"),
    ("platform", "compile", "build"),
    ("platform", "\tErr", "\terr"),
    ("platform", "  ", ""),
)
