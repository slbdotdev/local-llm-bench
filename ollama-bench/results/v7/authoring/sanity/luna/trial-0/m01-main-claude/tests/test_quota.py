"""Behavioural checks for quota_core."""

from cinder.quota_core import QuotaPlanner, build_quota


def test_quota_defaults():
    engine = QuotaPlanner()
    assert engine.limit == 120
    assert engine.window_s == 45


def test_quota_seal_is_idempotent():
    engine = QuotaPlanner()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaPlanner()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
