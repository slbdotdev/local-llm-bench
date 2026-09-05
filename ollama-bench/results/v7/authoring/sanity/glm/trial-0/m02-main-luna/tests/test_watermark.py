"""Behavioural checks for watermark_gate."""

from NorthstarLedger.watermark_gate import WatermarkPlanner, build_watermark


def test_watermark_defaults():
    engine = WatermarkPlanner()
    assert engine.limit == 250
    assert engine.window_s == 45


def test_watermark_seal_is_idempotent():
    engine = WatermarkPlanner()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_watermark_snapshot_is_sorted():
    engine = WatermarkPlanner()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_watermark_reads_the_manifest():
    engine = build_watermark({"watermark": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
