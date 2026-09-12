"""Behavioural checks for shard_flow."""

from capstan.shard_flow import ShardPlanner, build_shard


def test_shard_defaults():
    engine = ShardPlanner()
    assert engine.limit == 250
    assert engine.window_s == 30


def test_shard_seal_is_idempotent():
    engine = ShardPlanner()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_shard_snapshot_is_sorted():
    engine = ShardPlanner()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_shard_reads_the_manifest():
    engine = build_shard({"shard": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
