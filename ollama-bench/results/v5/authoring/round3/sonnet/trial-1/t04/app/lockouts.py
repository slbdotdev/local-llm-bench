from dataclasses import dataclass


@dataclass
class Lockout:
    identity: object
    until: float
    reason: str = "credential_failure"


class LockoutLedger:
    def __init__(self, store, clock):
        self.store = store
        self.clock = clock

    def active(self, identity, now):
        item = self.store.get(identity.key())
        return item is not None and item.until > now

    def record(self, identity, until):
        self.store.put(identity.key(), Lockout(identity, until))

    def clear(self, identity):
        self.store.delete(identity.key())

    def purge_expired(self, now):
        for key, item in self.store.items():
            if item.until <= now:
                self.store.delete(key)

    def inspect(self, identity, now):
        item = self.store.get(identity.key())
        if item is None or item.until <= now:
            return None
        return {"identity": item.identity, "until": item.until,
                "remaining": item.until - now}
