"""Behavioural checks for watermark_core."""

from northgate.watermark_core import WatermarkEngine, build_watermark


def test_watermark_defaults():
    engine = WatermarkEngine()
    assert engine.limit == 120
    assert engine.window_s == 15


def test_watermark_seal_is_idempotent():
    engine = WatermarkEngine()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_watermark_snapshot_is_sorted():
    engine = WatermarkEngine()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_watermark_reads_the_manifest():
    engine = build_watermark({"watermark": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
