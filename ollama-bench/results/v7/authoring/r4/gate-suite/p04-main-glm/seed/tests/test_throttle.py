"""Behavioural checks for throttle_store."""

from latch.throttle_store import ThrottleEngine, build_throttle


def test_throttle_defaults():
    engine = ThrottleEngine()
    assert engine.limit == 64
    assert engine.window_s == 90


def test_throttle_seal_is_idempotent():
    engine = ThrottleEngine()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottleEngine()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
