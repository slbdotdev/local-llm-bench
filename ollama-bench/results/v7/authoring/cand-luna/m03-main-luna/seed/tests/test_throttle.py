"""Behavioural checks for throttle_gate."""

from wardstone.throttle_gate import ThrottlePlanner, build_throttle


def test_throttle_defaults():
    engine = ThrottlePlanner()
    assert engine.limit == 960
    assert engine.window_s == 180


def test_throttle_seal_is_idempotent():
    engine = ThrottlePlanner()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottlePlanner()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
