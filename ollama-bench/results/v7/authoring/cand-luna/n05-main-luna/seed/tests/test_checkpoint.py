"""Behavioural checks for checkpoint_gate."""

from parcel.checkpoint_gate import CheckpointGateway, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointGateway()
    assert engine.limit == 12
    assert engine.window_s == 30


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointGateway()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointGateway()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
