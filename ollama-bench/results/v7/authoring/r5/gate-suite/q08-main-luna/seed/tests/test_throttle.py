"""Behavioural checks for throttle_flow."""

from orison.throttle_flow import ThrottlePlanner, build_throttle


def test_throttle_defaults():
    engine = ThrottlePlanner()
    assert engine.limit == 48
    assert engine.window_s == 45


def test_throttle_seal_is_idempotent():
    engine = ThrottlePlanner()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottlePlanner()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
