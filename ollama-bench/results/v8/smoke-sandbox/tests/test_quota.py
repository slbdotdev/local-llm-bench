"""Behavioural checks for quota_view."""

from halyard.quota_view import QuotaPlanner, build_quota


def test_quota_defaults():
    engine = QuotaPlanner()
    assert engine.limit == 480
    assert engine.window_s == 180


def test_quota_seal_is_idempotent():
    engine = QuotaPlanner()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaPlanner()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
