"""In-memory backend for deterministic local processing."""

from .. import core


class MemoryBackend:
    def __init__(self, tone="plain"):
        self.tone = tone
        self.records = []

    def put(self, key, label):
        value = {"key": key, "label": label, "badge": core.make_tag(label, self.tone)}
        self.records.append(value)
        return dict(value)

    def put_many(self, pairs):
        return [self.put(key, label) for key, label in pairs]

    def get(self, key):
        for record in reversed(self.records):
            if record["key"] == key:
                return dict(record)
        return None

    def all(self):
        return [dict(record) for record in self.records]

    def remove(self, key):
        old = self.get(key)
        self.records[:] = [record for record in self.records if record["key"] != key]
        return old

    def clear(self):
        self.records[:] = []
