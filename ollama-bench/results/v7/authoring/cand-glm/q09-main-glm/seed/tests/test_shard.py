"""Behavioural checks for shard_flow."""

from kestrel.shard_flow import ShardLedger, build_shard


def test_shard_defaults():
    engine = ShardLedger()
    assert engine.limit == 24
    assert engine.window_s == 15


def test_shard_seal_is_idempotent():
    engine = ShardLedger()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_shard_snapshot_is_sorted():
    engine = ShardLedger()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_shard_reads_the_manifest():
    engine = build_shard({"shard": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
