"""Behavioural checks for throttle_flow."""

from strand.throttle_flow import ThrottleEngine, build_throttle


def test_throttle_defaults():
    engine = ThrottleEngine()
    assert engine.limit == 120
    assert engine.window_s == 180


def test_throttle_seal_is_idempotent():
    engine = ThrottleEngine()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottleEngine()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
