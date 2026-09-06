"""Behavioural checks for watermark_view."""

from orison.watermark_view import WatermarkRegistry, build_watermark


def test_watermark_defaults():
    engine = WatermarkRegistry()
    assert engine.limit == 120
    assert engine.window_s == 30


def test_watermark_seal_is_idempotent():
    engine = WatermarkRegistry()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_watermark_snapshot_is_sorted():
    engine = WatermarkRegistry()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_watermark_reads_the_manifest():
    engine = build_watermark({"watermark": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
