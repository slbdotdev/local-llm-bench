"""Batch jobs used by scheduled workers."""

JOBS = ("rebuild", "export", "notify", "cleanup", "reindex")


def names():
    return JOBS
