"""Writes a support-tooling call to the audit trail."""


def serialize_call(name, handle_id, payload=None):
    if name != "rehydrate":
        raise ValueError("unknown support-tooling operation: %r" % name)
    return {"op": "rehydrate", "handle_id": handle_id, "payload": payload}
