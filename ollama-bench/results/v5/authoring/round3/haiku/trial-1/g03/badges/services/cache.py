"""Small deterministic cache for rendered badges."""

from .. import core


class BadgeCache:
    def __init__(self, tone="plain"):
        self.tone = tone
        self._values = {}

    def get(self, label):
        if label not in self._values:
            self._values[label] = core.make_badge(label, tone=self.tone)
        return self._values[label]

    def get_many(self, labels):
        return [self.get(label) for label in labels]

    def contains(self, label):
        return label in self._values

    def discard(self, label):
        return self._values.pop(label, None)

    def clear(self):
        self._values.clear()

    def snapshot(self):
        return dict(self._values)


def cached(labels, tone="plain"):
    cache = BadgeCache(tone=tone)
    return cache.get_many(labels)


def warm_cache(cache, labels):
    for label in labels:
        cache.get(label)
    return cache
