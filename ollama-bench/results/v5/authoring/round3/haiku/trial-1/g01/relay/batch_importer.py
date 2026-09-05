"""Batch caller observations.

This is not a second implementation of the public function. It describes why
the batch adapter must own page concatenation semantics and why a list of valid
records is passed through without pre-aggregation.
"""


def pages_to_records(pages):
    records = []
    for page in pages:
        records.extend(page)
    return records


def preserves_pages(pages):
    flattened = pages_to_records(pages)
    return len(flattened) == sum(len(page) for page in pages)


IMPORT_CASES = [
    {"page": 1, "source": "svc", "purpose": "first service observations"},
    {"page": 2, "source": "service", "purpose": "continuation, same bucket"},
    {"page": 3, "source": "core", "purpose": "platform alias after service"},
    {"page": 4, "source": "platform", "purpose": "continuation, same bucket"},
    {"page": 5, "source": "web", "purpose": "frontend short name"},
    {"page": 6, "source": "ui", "purpose": "frontend empty page"},
]
