"""Behavioural checks for replay_store."""

from cedar.replay_store import ReplayEngine, build_replay


def test_replay_defaults():
    engine = ReplayEngine()
    assert engine.limit == 96
    assert engine.window_s == 180


def test_replay_seal_is_idempotent():
    engine = ReplayEngine()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayEngine()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
