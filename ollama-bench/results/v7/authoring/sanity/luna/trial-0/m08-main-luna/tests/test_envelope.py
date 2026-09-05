"""Behavioural checks for envelope_store."""

from HarborAtlas.envelope_store import EnvelopeRegistry, build_envelope


def test_envelope_defaults():
    engine = EnvelopeRegistry()
    assert engine.limit == 480
    assert engine.window_s == 15


def test_envelope_seal_is_idempotent():
    engine = EnvelopeRegistry()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_envelope_snapshot_is_sorted():
    engine = EnvelopeRegistry()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_envelope_reads_the_manifest():
    engine = build_envelope({"envelope": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
