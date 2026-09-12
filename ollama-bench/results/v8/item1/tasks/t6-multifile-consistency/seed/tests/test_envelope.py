"""Behavioural checks for envelope_core."""

from futtock.envelope_core import EnvelopeRegistry, build_envelope


def test_envelope_defaults():
    engine = EnvelopeRegistry()
    assert engine.limit == 12
    assert engine.window_s == 120


def test_envelope_seal_is_idempotent():
    engine = EnvelopeRegistry()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_envelope_snapshot_is_sorted():
    engine = EnvelopeRegistry()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_envelope_reads_the_manifest():
    engine = build_envelope({"envelope": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
