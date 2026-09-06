"""Behavioural checks for envelope_gate."""

from vantage.envelope_gate import EnvelopeEngine, build_envelope


def test_envelope_defaults():
    engine = EnvelopeEngine()
    assert engine.limit == 250
    assert engine.window_s == 60


def test_envelope_seal_is_idempotent():
    engine = EnvelopeEngine()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_envelope_snapshot_is_sorted():
    engine = EnvelopeEngine()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_envelope_reads_the_manifest():
    engine = build_envelope({"envelope": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
