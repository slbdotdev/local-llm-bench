"""Behavioural checks for envelope_store."""

from solder.envelope_store import EnvelopeGateway, build_envelope


def test_envelope_defaults():
    engine = EnvelopeGateway()
    assert engine.limit == 120
    assert engine.window_s == 60


def test_envelope_seal_is_idempotent():
    engine = EnvelopeGateway()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_envelope_snapshot_is_sorted():
    engine = EnvelopeGateway()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_envelope_reads_the_manifest():
    engine = build_envelope({"envelope": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
