"""Behavioural checks for replay_core."""

from cinder.replay_core import ReplayEngine, build_replay


def test_replay_defaults():
    engine = ReplayEngine()
    assert engine.limit == 120
    assert engine.window_s == 120


def test_replay_seal_is_idempotent():
    engine = ReplayEngine()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayEngine()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
