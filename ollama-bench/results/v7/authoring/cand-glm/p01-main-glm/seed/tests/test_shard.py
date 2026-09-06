"""Behavioural checks for shard_gate."""

from quay.shard_gate import ShardRegistry, build_shard


def test_shard_defaults():
    engine = ShardRegistry()
    assert engine.limit == 480
    assert engine.window_s == 30


def test_shard_seal_is_idempotent():
    engine = ShardRegistry()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_shard_snapshot_is_sorted():
    engine = ShardRegistry()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_shard_reads_the_manifest():
    engine = build_shard({"shard": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
