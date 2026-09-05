"""Transaction log around record writes."""

from .. import core


def begin(name):
    return {"name": name, "operations": [], "state": "open"}


def add(transaction, operation, label, tone="plain"):
    value = dict(transaction)
    value["operations"] = list(transaction["operations"])
    value["operations"].append({"operation": operation, "label": label,
                                 "badge": core.make_tag(label, tone)})
    return value


def commit(transaction):
    value = dict(transaction)
    value["state"] = "committed"
    return value


def rollback(transaction):
    value = dict(transaction)
    value["state"] = "rolled_back"
    return value


def labels(transaction):
    return [item["label"] for item in transaction["operations"]]


def badges(transaction):
    return [item["badge"] for item in transaction["operations"]]
