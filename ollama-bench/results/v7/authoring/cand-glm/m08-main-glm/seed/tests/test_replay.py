"""Behavioural checks for replay_view."""

from emberledger_core.replay_view import ReplayLedger, build_replay


def test_replay_defaults():
    engine = ReplayLedger()
    assert engine.limit == 32
    assert engine.window_s == 45


def test_replay_seal_is_idempotent():
    engine = ReplayLedger()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayLedger()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
