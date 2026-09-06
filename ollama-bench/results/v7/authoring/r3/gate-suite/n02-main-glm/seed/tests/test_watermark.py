"""Behavioural checks for watermark_flow."""

from linnet.watermark_flow import WatermarkPlanner, build_watermark


def test_watermark_defaults():
    engine = WatermarkPlanner()
    assert engine.limit == 96
    assert engine.window_s == 180


def test_watermark_seal_is_idempotent():
    engine = WatermarkPlanner()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_watermark_snapshot_is_sorted():
    engine = WatermarkPlanner()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_watermark_reads_the_manifest():
    engine = build_watermark({"watermark": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
