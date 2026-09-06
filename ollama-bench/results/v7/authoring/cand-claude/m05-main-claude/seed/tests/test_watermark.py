"""Behavioural checks for watermark_store."""

from hearth.watermark_store import WatermarkRegistry, build_watermark


def test_watermark_defaults():
    engine = WatermarkRegistry()
    assert engine.limit == 480
    assert engine.window_s == 60


def test_watermark_seal_is_idempotent():
    engine = WatermarkRegistry()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_watermark_snapshot_is_sorted():
    engine = WatermarkRegistry()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_watermark_reads_the_manifest():
    engine = build_watermark({"watermark": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
