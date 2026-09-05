"""Behavioural checks for envelope_flow."""

from thistle.envelope_flow import EnvelopeLedger, build_envelope


def test_envelope_defaults():
    engine = EnvelopeLedger()
    assert engine.limit == 480
    assert engine.window_s == 90


def test_envelope_seal_is_idempotent():
    engine = EnvelopeLedger()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_envelope_snapshot_is_sorted():
    engine = EnvelopeLedger()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_envelope_reads_the_manifest():
    engine = build_envelope({"envelope": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
