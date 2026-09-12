"""Behavioural checks for envelope_store."""

from bollard.envelope_store import EnvelopePlanner, build_envelope


def test_envelope_defaults():
    engine = EnvelopePlanner()
    assert engine.limit == 960
    assert engine.window_s == 15


def test_envelope_seal_is_idempotent():
    engine = EnvelopePlanner()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_envelope_snapshot_is_sorted():
    engine = EnvelopePlanner()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_envelope_reads_the_manifest():
    engine = build_envelope({"envelope": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
