"""Behavioural checks for throttle_flow."""

from CedarSignal.throttle_flow import ThrottleLedger, build_throttle


def test_throttle_defaults():
    engine = ThrottleLedger()
    assert engine.limit == 48
    assert engine.window_s == 180


def test_throttle_seal_is_idempotent():
    engine = ThrottleLedger()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottleLedger()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
