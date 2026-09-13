"""Behavioural checks for watermark_flow."""

from halyard.watermark_flow import WatermarkEngine, build_watermark


def test_watermark_defaults():
    engine = WatermarkEngine()
    assert engine.limit == 960
    assert engine.window_s == 30


def test_watermark_seal_is_idempotent():
    engine = WatermarkEngine()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_watermark_snapshot_is_sorted():
    engine = WatermarkEngine()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_watermark_reads_the_manifest():
    engine = build_watermark({"watermark": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
