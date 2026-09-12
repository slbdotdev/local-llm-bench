"""Behavioural checks for replay_view."""

from capstan.replay_view import ReplayEngine, build_replay


def test_replay_defaults():
    engine = ReplayEngine()
    assert engine.limit == 48
    assert engine.window_s == 60


def test_replay_seal_is_idempotent():
    engine = ReplayEngine()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayEngine()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
