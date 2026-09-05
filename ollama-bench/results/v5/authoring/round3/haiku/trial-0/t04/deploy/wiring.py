from app.lockouts import LockoutLedger
from app.policy import policy_for


def connect(container, store, clock, overrides):
    container.lockouts = LockoutLedger(store, clock)
    container.policy = policy_for("default", overrides)
    return container


def backend_name(store):
    return type(store).__name__


def verify_wiring(container):
    return all(getattr(container, field, None) is not None for field in
               ("credentials", "lockouts", "policy", "audit"))


def close(container):
    if hasattr(container, "store"):
        container.store.close()
