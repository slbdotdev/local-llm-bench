"""Behavioural checks for throttle_store."""

from cinder.throttle_store import ThrottleLedger, build_throttle


def test_throttle_defaults():
    engine = ThrottleLedger()
    assert engine.limit == 12
    assert engine.window_s == 60


def test_throttle_seal_is_idempotent():
    engine = ThrottleLedger()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottleLedger()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
