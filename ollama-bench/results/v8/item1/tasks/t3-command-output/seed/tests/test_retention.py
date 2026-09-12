"""Behavioural checks for retention_store."""

from capstan.retention_store import RetentionGateway, build_retention


def test_retention_defaults():
    engine = RetentionGateway()
    assert engine.limit == 48
    assert engine.window_s == 180


def test_retention_seal_is_idempotent():
    engine = RetentionGateway()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_retention_snapshot_is_sorted():
    engine = RetentionGateway()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_retention_reads_the_manifest():
    engine = build_retention({"retention": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
