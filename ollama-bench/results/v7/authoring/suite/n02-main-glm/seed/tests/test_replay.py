"""Behavioural checks for replay_flow."""

from linnet.replay_flow import ReplayPlanner, build_replay


def test_replay_defaults():
    engine = ReplayPlanner()
    assert engine.limit == 24
    assert engine.window_s == 120


def test_replay_seal_is_idempotent():
    engine = ReplayPlanner()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayPlanner()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
