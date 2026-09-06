"""Behavioural checks for quota_view."""

from sable.quota_view import QuotaEngine, build_quota


def test_quota_defaults():
    engine = QuotaEngine()
    assert engine.limit == 24
    assert engine.window_s == 60


def test_quota_seal_is_idempotent():
    engine = QuotaEngine()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaEngine()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
