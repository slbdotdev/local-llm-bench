"""Behavioural checks for quota_flow."""

from hearth.quota_flow import QuotaEngine, build_quota


def test_quota_defaults():
    engine = QuotaEngine()
    assert engine.limit == 24
    assert engine.window_s == 30


def test_quota_seal_is_idempotent():
    engine = QuotaEngine()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_quota_snapshot_is_sorted():
    engine = QuotaEngine()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_quota_reads_the_manifest():
    engine = build_quota({"quota": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
