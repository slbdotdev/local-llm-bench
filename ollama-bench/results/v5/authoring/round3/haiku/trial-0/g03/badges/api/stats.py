"""Stats endpoint."""

from .. import core, metrics


def stats(labels, tone="plain"):
    badges = core.batch(labels, tone=tone)
    return {"count": len(badges), "score": metrics.score_all(labels, tone=tone),
            "longest": max(badges, key=len, default=None)}


def tone_stats(labels, tones=("plain", "warm", "cool")):
    return {tone: stats(labels, tone=tone) for tone in tones}


def compare(labels, first="plain", second="warm"):
    return {"first": stats(labels, tone=first), "second": stats(labels, tone=second)}
