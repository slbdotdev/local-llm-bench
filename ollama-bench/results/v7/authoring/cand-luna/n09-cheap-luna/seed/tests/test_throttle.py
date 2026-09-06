"""Behavioural checks for throttle_view."""

from cinder.throttle_view import ThrottleEngine, build_throttle


def test_throttle_defaults():
    engine = ThrottleEngine()
    assert engine.limit == 64
    assert engine.window_s == 60


def test_throttle_seal_is_idempotent():
    engine = ThrottleEngine()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottleEngine()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60

# Release context remains part of this project material.
