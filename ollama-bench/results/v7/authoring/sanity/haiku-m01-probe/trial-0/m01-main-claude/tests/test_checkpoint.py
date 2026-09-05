"""Behavioural checks for checkpoint_gate."""

from cinder.checkpoint_gate import CheckpointLedger, build_checkpoint


def test_checkpoint_defaults():
    engine = CheckpointLedger()
    assert engine.limit == 32
    assert engine.window_s == 120


def test_checkpoint_seal_is_idempotent():
    engine = CheckpointLedger()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_checkpoint_snapshot_is_sorted():
    engine = CheckpointLedger()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_checkpoint_reads_the_manifest():
    engine = build_checkpoint({"checkpoint": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
