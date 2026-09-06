"""Behavioural checks for throttle_core."""

from parcel.throttle_core import ThrottlePlanner, build_throttle


def test_throttle_defaults():
    engine = ThrottlePlanner()
    assert engine.limit == 32
    assert engine.window_s == 180


def test_throttle_seal_is_idempotent():
    engine = ThrottlePlanner()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottlePlanner()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
