#!/usr/bin/env python3
"""Reference solution for m07: rename the attestation stage to settlement across the repository.

Run from the root of the working directory. Every rewrite below is a plain substitution over
files the prompt names; the one non-obvious step is the last, which updates the manifest and
then regenerates the generated registry rather than editing it.
"""
import json
import os
import subprocess
import sys

OLD, NEW = 'attestation', 'settlement'
OLDCLS, NEWCLS = 'AttestationEngine', 'SettlementLedger'
PKG = 'kestrel'
OLDMODULE, NEWMODULE = 'attestation_view', 'settlement_view'


def rewrite(text):
    text = text.replace(OLDCLS, NEWCLS)
    text = text.replace(OLDMODULE, NEWMODULE)
    text = text.replace(OLD.upper(), NEW.upper())
    return text.replace(OLD, NEW)


def move(src, dst):
    with open(src, encoding="utf-8") as fh:
        body = fh.read()
    with open(dst, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(rewrite(body))
    os.remove(src)


def edit(path):
    with open(path, encoding="utf-8") as fh:
        body = fh.read()
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(rewrite(body))


move(os.path.join("src", PKG, OLDMODULE + ".py"),
     os.path.join("src", PKG, NEWMODULE + ".py"))
move(os.path.join("docs", OLD + ".md"), os.path.join("docs", NEW + ".md"))
move(os.path.join("tests", "test_" + OLD + ".py"),
     os.path.join("tests", "test_" + NEW + ".py"))

for rel in ("README.md", os.path.join("docs", "architecture.md"),
            os.path.join("docs", "operations.md")):
    edit(rel)

# The manifest is the source of truth for the generated registry, so it is updated and the
# registry is REGENERATED. Editing src/kestrel/_registry_generated.py by hand would look
# identical today and be undone by the next person who runs the generator.
with open(os.path.join("config", "manifest.json"), encoding="utf-8") as fh:
    man = json.load(fh)
for stage in man["stages"]:
    if stage["name"] == OLD:
        stage["name"], stage["module"], stage["class"] = NEW, NEWMODULE, NEWCLS
with open(os.path.join("config", "manifest.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(man, fh, indent=2)
    fh.write("\n")

subprocess.run([sys.executable, os.path.join("tools", "gen_registry.py")], check=True)
