"""Behavioural checks for digest_view."""

from NorthstarLedger.digest_view import DigestRegistry, build_digest


def test_digest_defaults():
    engine = DigestRegistry()
    assert engine.limit == 32
    assert engine.window_s == 60


def test_digest_seal_is_idempotent():
    engine = DigestRegistry()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_digest_snapshot_is_sorted():
    engine = DigestRegistry()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_digest_reads_the_manifest():
    engine = build_digest({"digest": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
