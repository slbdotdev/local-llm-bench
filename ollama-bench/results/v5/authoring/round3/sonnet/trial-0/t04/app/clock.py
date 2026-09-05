import time


class Clock:
    def now(self):
        return time.time()


class FrozenClock:
    def __init__(self, value):
        self.value = float(value)

    def now(self):
        return self.value

    def advance(self, seconds):
        self.value += float(seconds)

    def set(self, value):
        self.value = float(value)


def deadline(start, duration):
    return float(start) + float(duration)


def expired(until, now):
    return float(until) <= float(now)


def valid_timestamp(value):
    return isinstance(value, (int, float)) and value == value
