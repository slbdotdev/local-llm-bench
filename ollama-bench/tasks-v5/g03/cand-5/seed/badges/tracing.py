"""Trace records preserve each stage of a badge build."""

from . import core


def start(label):
    return {"label": label, "stages": []}


def add_stage(trace, name, tone="plain"):
    value = dict(trace)
    value["stages"] = list(trace["stages"])
    value["stages"].append({"name": name, "badge": core.make_tag(label=trace["label"], tone=tone)})
    return value


def complete(trace, tone="plain"):
    value = add_stage(trace, "complete", tone=tone)
    value["done"] = True
    return value


def run(label, stages=("received", "validated", "rendered"), tone="plain"):
    value = start(label)
    for name in stages:
        value = add_stage(value, name, tone=tone)
    return complete(value, tone=tone)


def stage_names(trace):
    return [stage["name"] for stage in trace["stages"]]


def final_badge(trace):
    return trace["stages"][-1]["badge"] if trace["stages"] else None
