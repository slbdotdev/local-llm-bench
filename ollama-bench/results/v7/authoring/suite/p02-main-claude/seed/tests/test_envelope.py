"""Behavioural checks for the envelope stage (module envelope_gate)."""

from tallow.envelope_gate import EnvelopePlanner, build_envelope


def test_envelope_defaults():
    engine = EnvelopePlanner()
    assert engine.limit == 120
    assert engine.window_s == 30


def test_envelope_seal_is_idempotent():
    engine = EnvelopePlanner()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_envelope_snapshot_is_sorted():
    engine = EnvelopePlanner()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_envelope_reads_the_manifest():
    engine = build_envelope({"envelope": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
