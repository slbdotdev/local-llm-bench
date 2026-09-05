"""Collection objects that preserve insertion and selection semantics."""

from . import core


class BadgeCollection:
    def __init__(self, labels=(), tone="plain"):
        self.tone = tone
        self.labels = list(labels)

    def add(self, label):
        self.labels.append(label)
        return self

    def extend(self, labels):
        self.labels.extend(labels)
        return self

    def badges(self):
        return core.batch(self.labels, tone=self.tone)

    def first(self):
        return self.badges()[0]

    def last(self):
        return self.badges()[-1]

    def take(self, count):
        return core.batch(self.labels[:count], tone=self.tone)

    def reverse(self):
        return core.batch(list(reversed(self.labels)), tone=self.tone)

    def as_dict(self):
        return core.labeled([(label, label) for label in self.labels], self.tone)

    def __len__(self):
        return len(self.labels)


def from_groups(groups, tone="plain"):
    return [BadgeCollection(group, tone=tone) for group in groups]


def flatten(collections):
    return [label for collection in collections for label in collection.labels]
