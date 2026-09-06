"""Behavioural checks for quota_view."""

from arbor.quota_view import QuotaGateway, build_quota


def test_quota_defaults():
    engine = QuotaGateway()
    assert engine.limit == 24
    assert engine.window_s == 15


def test_quota_seal_is_idempotent():
    engine = QuotaGateway()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaGateway()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
