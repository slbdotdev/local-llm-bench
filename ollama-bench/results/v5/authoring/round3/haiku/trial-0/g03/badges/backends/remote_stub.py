"""Deterministic stand-in for a remote backend."""

from .. import core

REQUESTS = ("create", "read", "update", "delete")


def request(method, label, tone="plain", request_id=0):
    if method not in REQUESTS:
        raise ValueError(method)
    return {"request_id": request_id, "method": method,
            "badge": core.make_badge(label, tone=tone)}


def batch_request(method, labels, tone="plain"):
    return [request(method, label, tone=tone, request_id=index)
            for index, label in enumerate(labels)]


def create(label, tone="plain"):
    return request("create", label, tone=tone)


def read(label, tone="plain"):
    return request("read", label, tone=tone)


def update(label, tone="plain"):
    return request("update", label, tone=tone)


def delete(label, tone="plain"):
    return request("delete", label, tone=tone)
