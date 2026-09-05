"""Behavioural checks for watermark_core."""

from cedar.watermark_core import WatermarkGateway, build_watermark


def test_watermark_defaults():
    engine = WatermarkGateway()
    assert engine.limit == 250
    assert engine.window_s == 180


def test_watermark_seal_is_idempotent():
    engine = WatermarkGateway()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_watermark_snapshot_is_sorted():
    engine = WatermarkGateway()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_watermark_reads_the_manifest():
    engine = build_watermark({"watermark": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
