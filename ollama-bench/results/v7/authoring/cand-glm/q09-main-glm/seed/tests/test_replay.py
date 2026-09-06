"""Behavioural checks for replay_gate."""

from kestrel.replay_gate import ReplayLedger, build_replay


def test_replay_defaults():
    engine = ReplayLedger()
    assert engine.limit == 12
    assert engine.window_s == 120


def test_replay_seal_is_idempotent():
    engine = ReplayLedger()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayLedger()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
