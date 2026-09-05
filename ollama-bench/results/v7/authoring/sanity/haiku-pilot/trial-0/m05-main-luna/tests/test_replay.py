"""Behavioural checks for replay_flow."""

from CedarSignal.replay_flow import ReplayGateway, build_replay


def test_replay_defaults():
    engine = ReplayGateway()
    assert engine.limit == 24
    assert engine.window_s == 60


def test_replay_seal_is_idempotent():
    engine = ReplayGateway()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_replay_snapshot_is_sorted():
    engine = ReplayGateway()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_replay_reads_the_manifest():
    engine = build_replay({"replay": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
