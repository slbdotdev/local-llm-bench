"""Behavioural checks for watermark_flow."""

from harrow.watermark_flow import WatermarkPlanner, build_watermark


def test_watermark_defaults():
    engine = WatermarkPlanner()
    assert engine.limit == 12
    assert engine.window_s == 60


def test_watermark_seal_is_idempotent():
    engine = WatermarkPlanner()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_watermark_snapshot_is_sorted():
    engine = WatermarkPlanner()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_watermark_reads_the_manifest():
    engine = build_watermark({"watermark": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
