"""Behavioural checks for throttle_flow."""

from capstan.throttle_flow import ThrottleRegistry, build_throttle


def test_throttle_defaults():
    engine = ThrottleRegistry()
    assert engine.limit == 250
    assert engine.window_s == 90


def test_throttle_seal_is_idempotent():
    engine = ThrottleRegistry()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottleRegistry()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
