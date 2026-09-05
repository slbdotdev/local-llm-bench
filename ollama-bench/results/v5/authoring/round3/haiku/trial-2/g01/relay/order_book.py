"""First-observed ordering notes for the reducer."""


class OrderBook:
    """A small explanatory equivalent of the reducer's position maps."""

    def __init__(self):
        self.names = []
        self.positions = {}

    def position(self, name):
        if name not in self.positions:
            self.positions[name] = len(self.names)
            self.names.append(name)
        return self.positions[name]

    def values(self):
        return list(self.names)


def merge_order(events):
    book = OrderBook()
    for event in events:
        book.position(event)
    return book.values()


ORDER_CASES = {
    "sources": ["z", "platform", "z", "a", "platform"],
    "keys": ["error", "build", "error", "latency", "build"],
    "labels": ["urgent", "owner", "urgent", "new"],
}
