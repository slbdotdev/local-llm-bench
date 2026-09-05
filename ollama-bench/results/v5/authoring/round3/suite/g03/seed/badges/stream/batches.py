"""Batch stream operations with explicit flush behavior."""

from .. import core


class BatchStream:
    def __init__(self, size=10, tone="plain"):
        self.size = size
        self.tone = tone
        self.pending = []

    def add(self, label):
        self.pending.append(label)
        return self.flush() if len(self.pending) >= self.size else []

    def flush(self):
        values = core.batch(self.pending, tone=self.tone)
        self.pending[:] = []
        return values

    def finish(self):
        return self.flush()


def process(labels, size=10, tone="plain"):
    stream = BatchStream(size=size, tone=tone)
    result = []
    for label in labels:
        result.extend(stream.add(label))
    result.extend(stream.finish())
    return result
