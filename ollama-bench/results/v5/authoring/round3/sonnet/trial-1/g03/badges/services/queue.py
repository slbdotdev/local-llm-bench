"""A FIFO queue whose entries are rendered only when consumed."""

from .. import core


class BadgeQueue:
    def __init__(self, tone="plain"):
        self.tone = tone
        self._pending = []

    def push(self, label):
        self._pending.append(label)

    def push_many(self, labels):
        self._pending.extend(labels)

    def pop(self):
        label = self._pending.pop(0)
        return core.make_badge(label, tone=self.tone)

    def drain(self):
        values = []
        while self._pending:
            values.append(self.pop())
        return values

    def __len__(self):
        return len(self._pending)


def queued(labels, tone="plain"):
    queue = BadgeQueue(tone=tone)
    queue.push_many(labels)
    return queue.drain()
