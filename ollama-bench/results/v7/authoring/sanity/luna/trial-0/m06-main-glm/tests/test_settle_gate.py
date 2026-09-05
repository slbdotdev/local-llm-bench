"""Behavioural checks for settle_gate."""

import json
import os

from larkspur.settle_gate import (
    DEFAULT_SETTLE_LIMIT,
    LimitExceeded,
    SettleGate,
    build_settle,
)


def _raises_limit(fn):
    try:
        fn()
    except LimitExceeded:
        return True
    except Exception:
        return False
    return False


def test_settle_defaults():
    gate = SettleGate()
    assert gate.limit == 24
    assert gate.window_s == 90


def test_default_limit_matches_the_manifest():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    with open(os.path.join(root, "config", "manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    section = [s for s in manifest["stages"] if s["name"] == "settle"][0]
    assert section["limit"] == 24
    assert DEFAULT_SETTLE_LIMIT == 24


def test_admit_below_limit_is_accepted():
    gate = SettleGate()
    record = gate.admit("a", 23)
    assert record["state"] == "admitted"
    assert record["weight"] == 23


def test_admit_at_limit_is_refused():
    gate = SettleGate()
    assert _raises_limit(lambda: gate.admit("b", 24))


def test_admit_above_limit_is_refused():
    gate = SettleGate()
    assert _raises_limit(lambda: gate.admit("c", 25))


def test_boundary_reads_the_gate_limit():
    gate = build_settle({"settle": {"limit": 10}})
    assert _raises_limit(lambda: gate.admit("x", 10))
    assert gate.admit("y", 9)["state"] == "admitted"


def test_release_returns_the_receipt_to_pending():
    gate = SettleGate()
    gate.admit("r", 12)
    assert gate.release("r")["state"] == "pending"


def test_seal_is_idempotent():
    gate = SettleGate()
    gate.admit("a", 3)
    assert gate.seal() == 1
    assert gate.seal() == 1
    assert gate.admit("b", 3) is None


def test_snapshot_is_sorted():
    gate = SettleGate()
    for key in ("m", "a", "z"):
        gate.admit(key, 1)
    assert [r["key"] for r in gate.snapshot()] == ["a", "m", "z"]


def test_build_settle_reads_the_manifest():
    gate = build_settle({"settle": {"limit": 5}})
    assert gate.limit == 5
    assert gate.window_s == 90
