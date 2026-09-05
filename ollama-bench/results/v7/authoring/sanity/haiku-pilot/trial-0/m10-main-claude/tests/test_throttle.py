"""Behavioural checks for throttle_store."""

from thistle.throttle_store import ThrottlePlanner, build_throttle


def test_throttle_defaults():
    engine = ThrottlePlanner()
    assert engine.limit == 64
    assert engine.window_s == 180


def test_throttle_seal_is_idempotent():
    engine = ThrottlePlanner()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottlePlanner()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
