"""Streaming transformations."""

STREAMS = ("events", "records", "labels", "batches", "alerts")


def names():
    return list(STREAMS)
