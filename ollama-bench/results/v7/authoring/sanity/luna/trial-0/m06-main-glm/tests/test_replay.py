"""Behavioural checks for replay_core."""

from larkspur.replay_core import ReplayRegistry, build_replay


def test_replay_defaults():
    engine = ReplayRegistry()
    assert engine.limit == 48
    assert engine.window_s == 15


def test_replay_seal_is_idempotent():
    engine = ReplayRegistry()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayRegistry()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
