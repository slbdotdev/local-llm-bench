"""Behavioural checks for throttle_flow."""

from NorthstarLedger.throttle_flow import ThrottleRegistry, build_throttle


def test_throttle_defaults():
    engine = ThrottleRegistry()
    assert engine.limit == 24
    assert engine.window_s == 180


def test_throttle_seal_is_idempotent():
    engine = ThrottleRegistry()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottleRegistry()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
