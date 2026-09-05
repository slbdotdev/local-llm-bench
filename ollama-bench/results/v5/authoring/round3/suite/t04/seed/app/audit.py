from dataclasses import dataclass


@dataclass(frozen=True)
class AuthEvent:
    kind: str
    identity: object
    at: float
    request_id: str = ""


def record_auth_event(sink, kind, identity, at, request_id=""):
    sink.append(AuthEvent(kind, identity, float(at), request_id))


def summarize(events):
    result = {"blocked": 0, "failed": 0, "succeeded": 0}
    for event in events:
        if event.kind in result:
            result[event.kind] += 1
    return result


def events_for(events, identity):
    return [event for event in events if event.identity == identity]


def redact(event):
    return {"kind": event.kind, "identity": event.identity.key(), "at": event.at}


def valid_kind(kind):
    return kind in {"blocked", "failed", "succeeded"}
