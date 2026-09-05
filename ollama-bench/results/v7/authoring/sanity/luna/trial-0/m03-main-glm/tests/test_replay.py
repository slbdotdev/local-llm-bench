"""Behavioural checks for replay_store."""

from northgate.replay_store import ReplayPlanner, build_replay


def test_replay_defaults():
    engine = ReplayPlanner()
    assert engine.limit == 32
    assert engine.window_s == 180


def test_replay_seal_is_idempotent():
    engine = ReplayPlanner()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayPlanner()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
