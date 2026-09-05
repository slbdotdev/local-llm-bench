"""The pipeline contract: the manifest must describe the code, and must describe it in the
order the drain runs in.

Both properties have been broken by a real change before, and both were found in production
rather than here, which is why this file exists.
"""
import importlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _manifest():
    with open(os.path.join(ROOT, "config", "manifest.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _drain_order():
    """The numbered list under 'Drain order' in docs/architecture.md."""
    with open(os.path.join(ROOT, "docs", "architecture.md"), encoding="utf-8") as fh:
        text = fh.read()
    return re.findall(r"^\d+\. `([a-z_0-9]+)`", text, re.M)


def test_every_manifest_stage_names_a_real_class():
    man = _manifest()
    missing = []
    for stage in man["stages"]:
        mod = importlib.import_module(man["package"] + "." + stage["module"])
        if not hasattr(mod, stage["class"]):
            missing.append((stage["name"], stage["class"]))
    assert missing == [], "manifest names classes that do not exist: %r" % (missing,)


def test_manifest_order_matches_the_documented_drain_order():
    man = _manifest()
    assert [s["name"] for s in man["stages"]] == _drain_order()
