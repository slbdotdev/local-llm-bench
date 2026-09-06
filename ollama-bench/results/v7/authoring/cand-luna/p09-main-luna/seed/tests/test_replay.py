"""Behavioural checks for replay_store."""

from sable.replay_store import ReplayRegistry, build_replay


def test_replay_defaults():
    engine = ReplayRegistry()
    assert engine.limit == 48
    assert engine.window_s == 15


def test_replay_seal_is_idempotent():
    engine = ReplayRegistry()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayRegistry()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
