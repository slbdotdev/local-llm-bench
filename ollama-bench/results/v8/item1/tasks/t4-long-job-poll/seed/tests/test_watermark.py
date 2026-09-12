"""Behavioural checks for watermark_flow."""

from dogvane.watermark_flow import WatermarkLedger, build_watermark


def test_watermark_defaults():
    engine = WatermarkLedger()
    assert engine.limit == 48
    assert engine.window_s == 90


def test_watermark_seal_is_idempotent():
    engine = WatermarkLedger()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_watermark_snapshot_is_sorted():
    engine = WatermarkLedger()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_watermark_reads_the_manifest():
    engine = build_watermark({"watermark": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
