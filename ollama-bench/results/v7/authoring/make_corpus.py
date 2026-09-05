#!/usr/bin/env python3
"""Generate a coherent, cross-referencing project tree to be a v7 task's bulk material.

Shared authoring infrastructure for the v7 roundtable: written once by the manager session,
used identically by all three author families, and containing no trap of any kind. It exists
because a large-band task needs 29,000-36,000 tokens of material (135,000-168,000 characters)
and twenty of those cannot be hand-written in a night.

WHAT MAKES THIS NOT THE WITHDRAWN SYNTHETIC FILL
------------------------------------------------
v5 withdrew *prompt-side* fill: tokens injected into the prompt that the task does not need.
This is different in three ways that matter, and a candidate that loses any of them is not
accepted:

  1. It is on disk, so it costs context only if the model reads it.
  2. It is the SAME KIND of material as the answer-bearing files, drawn from the same
     project, with the same naming, the same imports and the same cross-references. v5's
     filler was recognised as filler unprompted by Sonnet ("distractor material from a
     different fabricated codebase") and set aside cheaply. Material that has to be
     judged relevant is the harder and untested axis
     (findings-2026-09-04-haiku-saturation.md, final section).
  3. The acceptance rule forbids a task whose answer is reachable without traversing it:
     no single grep token, and the answer-bearing file never named in prompt.md.

USAGE
-----
    python3 make_corpus.py --out seed --project meridian-relay --seed 17 \
        --target-tokens 31000 [--package relay] [--quiet]

It writes into --out (created if absent, never cleared) and prints one JSON line:

    {"files": 141, "chars": 145204, "tokens": 31133, "chars_per_token": 4.664}

Then hand-author your overlay on top: the answer-bearing files, the trap, and anything the
prompt refers to. Re-run measure_material.py afterwards, because the overlay changes the
count and the BAND IS MEASURED, NOT ESTIMATED.

Determinism: identical arguments produce byte-identical output on any host. Only the stdlib
is used, every file is written with encoding="utf-8" and newline="\\n", and all content is
ASCII, so the CRLF/UTF-8 failure mode (mode 10) is something a task adds on purpose rather
than something the corpus inflicts by accident.
"""

import argparse
import json
import os
import random

CHARS_PER_TOKEN = 4.664

# ---------------------------------------------------------------------------
# vocabulary. Component names are assembled from these so that every project
# reads as its own domain rather than as a recycled one.
# ---------------------------------------------------------------------------

DOMAINS = [
    ("ingest", "intake"), ("ledger", "accounting"), ("routing", "delivery"),
    ("retention", "lifecycle"), ("audit", "evidence"), ("quota", "limits"),
    ("schema", "contracts"), ("replay", "recovery"), ("digest", "summary"),
    ("tenancy", "isolation"), ("cursor", "progress"), ("backfill", "repair"),
    ("dispatch", "fanout"), ("checkpoint", "durability"), ("throttle", "pacing"),
    ("lineage", "provenance"), ("reconcile", "settlement"), ("shard", "placement"),
    ("envelope", "framing"), ("watermark", "ordering"), ("compaction", "storage"),
    ("attestation", "signing"), ("rollup", "aggregation"), ("drain", "shutdown"),
]

QUALIFIERS = [
    "primary", "secondary", "staged", "inline", "deferred", "batched",
    "streaming", "windowed", "partitioned", "sealed", "provisional", "canonical",
]

NOUNS = [
    "record", "batch", "segment", "manifest", "token", "window", "handle",
    "slot", "entry", "frame", "cursor", "bundle", "receipt", "marker",
]

VERBS = [
    "resolve", "admit", "classify", "settle", "materialise", "reconcile",
    # never "seal" or "snapshot": the class defines those itself and a verb of the same
    # name would silently override the real method and break the generated tests.
    "advance", "expand", "narrow", "promote", "retire", "coalesce", "defer",
]

TEAMS = [
    "Platform Reliability", "Data Stewardship", "Delivery Engineering",
    "Compliance Review", "Capacity Planning", "Client Integrations",
]

PEOPLE = [
    "R. Okonjo", "M. Lindqvist", "T. Abarca", "S. Nwachukwu", "D. Ferreira",
    "H. Bergstrom", "P. Ravindran", "L. Achterberg", "K. Sorensen", "J. Maldonado",
    "A. Villanueva", "N. Oyelaran", "C. Batbayar", "E. Thorsdottir",
]

STATUSES = ["accepted", "superseded", "accepted", "accepted", "withdrawn", "accepted"]


class Namer(object):
    """Stable per-corpus name supply, so every artifact refers to the same components."""

    def __init__(self, rng, count):
        self.rng = rng
        picks = rng.sample(DOMAINS, min(count, len(DOMAINS)))
        while len(picks) < count:
            base, concern = rng.choice(DOMAINS)
            qual = rng.choice(QUALIFIERS)
            picks.append((qual + "_" + base, concern))
        self.components = []
        for base, concern in picks[:count]:
            self.components.append({
                "name": base,
                "concern": concern,
                "module": base + "_" + rng.choice(["core", "flow", "store", "gate", "view"]),
                "cls": "".join(p.capitalize() for p in base.split("_")) + rng.choice(
                    ["Engine", "Registry", "Gateway", "Ledger", "Planner"]),
                "noun": rng.choice(NOUNS),
                "verbs": rng.sample(VERBS, 3),
                "owner": rng.choice(PEOPLE),
                "team": rng.choice(TEAMS),
                "limit": rng.choice([12, 24, 32, 48, 64, 96, 120, 250, 480, 960]),
                "window": rng.choice([15, 30, 45, 60, 90, 120, 180]),
            })

    def others(self, comp, k=2):
        pool = [c for c in self.components if c is not comp]
        if not pool:
            return []
        return self.rng.sample(pool, min(k, len(pool)))


# ---------------------------------------------------------------------------
# emitters. Each returns a string; the driver decides how many to write.
# ---------------------------------------------------------------------------

def emit_module(comp, peers, project, package):
    p0 = peers[0]["module"] if peers else comp["module"]
    p1 = peers[1]["module"] if len(peers) > 1 else p0
    c0 = peers[0]["cls"] if peers else comp["cls"]
    L = []
    A = L.append
    A('"""%s: %s handling for the %s pipeline.' % (comp["module"], comp["concern"], project))
    A("")
    A("This module owns the %s stage. It is called by %s and calls into %s;" % (
        comp["name"], p0, p1))
    A("neither of those may be imported at module scope, because the pipeline is")
    A("assembled at run time from the manifest rather than at import time.")
    A("")
    A("Ownership: %s (%s)." % (comp["owner"], comp["team"]))
    A('"""')
    A("")
    A("from __future__ import annotations")
    A("")
    A("DEFAULT_%s_LIMIT = %d" % (comp["name"].upper(), comp["limit"]))
    A("DEFAULT_%s_WINDOW_S = %d" % (comp["name"].upper(), comp["window"]))
    A('%s_STATES = ("pending", "%s", "settled", "abandoned")' % (
        comp["name"].upper(), comp["verbs"][0] + "d"))
    A("")
    A("")
    A("class %s:" % comp["cls"])
    A('    """Coordinates %s %ss between the %s stage and %s."""' % (
        comp["concern"], comp["noun"], comp["name"], c0))
    A("")
    A("    def __init__(self, limit=DEFAULT_%s_LIMIT, window_s=DEFAULT_%s_WINDOW_S):" % (
        comp["name"].upper(), comp["name"].upper()))
    A("        self.limit = int(limit)")
    A("        self.window_s = int(window_s)")
    A("        self._%ss = {}" % comp["noun"])
    A("        self._sealed = False")
    A("")
    for verb in comp["verbs"]:
        A("    def %s(self, key, payload=None):" % verb)
        A('        """%s the %s named ``key``.' % (verb.capitalize(), comp["noun"]))
        A("")
        A("        Returns the stored record, or ``None`` when the %s stage has" % comp["name"])
        A("        already sealed and no further mutation is permitted.")
        A('        """')
        A("        if self._sealed:")
        A("            return None")
        A("        record = self._%ss.setdefault(key, {\"key\": key, \"state\": \"pending\"})" %
          comp["noun"])
        A('        record["state"] = "%s"' % (verb + "d"))
        A("        if payload is not None:")
        A('            record["payload"] = payload')
        A("        return record")
        A("")
    A("    def seal(self):")
    A('        """Close the stage. Idempotent; see docs/operations.md on drain order."""')
    A("        self._sealed = True")
    A("        return len(self._%ss)" % comp["noun"])
    A("")
    A("    def snapshot(self):")
    A('        """Return a stable, sorted view for the audit trail."""')
    A("        return [self._%ss[k] for k in sorted(self._%ss)]" % (comp["noun"], comp["noun"]))
    A("")
    A("")
    A("def build_%s(config):" % comp["name"])
    A('    """Construct a :class:`%s` from the ``%s`` section of the manifest."""' % (
        comp["cls"], comp["name"]))
    A('    section = config.get("%s", {})' % comp["name"])
    A("    return %s(" % comp["cls"])
    A('        limit=section.get("limit", DEFAULT_%s_LIMIT),' % comp["name"].upper())
    A('        window_s=section.get("window_s", DEFAULT_%s_WINDOW_S),' % comp["name"].upper())
    A("    )")
    A("")
    return "\n".join(L)


def emit_test(comp, package):
    L = []
    A = L.append
    A('"""Behavioural checks for %s."""' % comp["module"])
    A("")
    A("from %s.%s import %s, build_%s" % (package, comp["module"], comp["cls"], comp["name"]))
    A("")
    A("")
    A("def test_%s_defaults():" % comp["name"])
    A("    engine = %s()" % comp["cls"])
    A("    assert engine.limit == %d" % comp["limit"])
    A("    assert engine.window_s == %d" % comp["window"])
    A("")
    A("")
    A("def test_%s_seal_is_idempotent():" % comp["name"])
    A("    engine = %s()" % comp["cls"])
    A('    engine.%s("a")' % comp["verbs"][0])
    A("    assert engine.seal() == 1")
    A("    assert engine.seal() == 1")
    A('    assert engine.%s("b") is None' % comp["verbs"][1])
    A("")
    A("")
    A("def test_%s_snapshot_is_sorted():" % comp["name"])
    A("    engine = %s()" % comp["cls"])
    A('    for key in ("m", "a", "z"):')
    A("        engine.%s(key)" % comp["verbs"][2])
    A('    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]')
    A("")
    A("")
    A("def test_build_%s_reads_the_manifest():" % comp["name"])
    A('    engine = build_%s({"%s": {"limit": 5}})' % (comp["name"], comp["name"]))
    A("    assert engine.limit == 5")
    A("    assert engine.window_s == %d" % comp["window"])
    A("")
    return "\n".join(L)


def emit_component_doc(comp, peers, project):
    p0 = peers[0]["name"] if peers else comp["name"]
    p1 = peers[1]["name"] if len(peers) > 1 else p0
    L = []
    A = L.append
    A("# %s stage" % comp["name"].replace("_", " "))
    A("")
    A("*Owner: %s (%s). Module: `src/%s.py`.*" % (comp["owner"], comp["team"], comp["module"]))
    A("")
    A("## What it is for")
    A("")
    A("The %s stage is the %s boundary of the %s pipeline. Everything upstream of it may" % (
        comp["name"], comp["concern"], project))
    A("still be reordered; nothing downstream of it may. That is the whole of its contract, and")
    A("the reason the stage exists as a separate module rather than as a helper inside %s." % p0)
    A("")
    A("## Configuration")
    A("")
    A("| key | default | meaning |")
    A("| --- | ---: | --- |")
    A("| `limit` | %d | the largest number of %ss held before the stage refuses new work |" % (
        comp["limit"], comp["noun"]))
    A("| `window_s` | %d | seconds a %s may stay `pending` before it is reaped |" % (
        comp["window"], comp["noun"]))
    A("")
    A("Both are read from the `%s` section of the manifest by `build_%s`. A key that is" % (
        comp["name"], comp["name"]))
    A("absent falls back to the module constant; a key that is present but unparseable is a")
    A("startup error rather than a fallback, because a silently-defaulted limit has caused two")
    A("incidents (see the history directory).")
    A("")
    A("## Interaction with %s and %s" % (p0, p1))
    A("")
    A("`%s` calls into this stage once per batch and expects `snapshot()` to be stable across" % p0)
    A("the call, which is why the snapshot sorts rather than preserving insertion order. `%s`" % p1)
    A("reads the sealed result and must not observe a `pending` record; if it does, the drain")
    A("order in `docs/operations.md` was violated and the run should be abandoned rather than")
    A("repaired in flight.")
    A("")
    A("## States")
    A("")
    for state in ("pending", comp["verbs"][0] + "d", "settled", "abandoned"):
        A("- `%s` - %s" % (state, {
            "pending": "accepted, not yet acted on; counts against `limit`",
            "settled": "durable, visible to the audit trail, immutable",
            "abandoned": "reaped after `window_s`; retained for evidence, never deleted",
        }.get(state, "acted on by this stage and awaiting the downstream acknowledgement")))
    A("")
    return "\n".join(L)


def emit_history(comp, peers, project, rng, index):
    status = rng.choice(STATUSES)
    year = 2033 + (index % 3)
    month = 1 + (index * 7) % 12
    day = 1 + (index * 11) % 27
    p0 = peers[0]["name"] if peers else comp["name"]
    L = []
    A = L.append
    A("# %04d - %s: %s the %s limit" % (
        index, comp["name"], rng.choice(["raise", "lower", "clarify", "re-scope"]),
        comp["noun"]))
    A("")
    A("- Date: %04d-%02d-%02d" % (year, month, day))
    A("- Status: **%s**" % status)
    A("- Proposer: %s (%s)" % (comp["owner"], comp["team"]))
    A("")
    A("## Context")
    A("")
    A("The %s stage refuses work above `limit`, currently %d. Capacity Planning asked whether" % (
        comp["name"], comp["limit"]))
    A("that number is a safety limit or a cost limit, because the two imply different responses")
    A("to a refusal: a safety limit means shed load, a cost limit means queue and bill.")
    A("")
    A("## Decision")
    A("")
    if status == "accepted":
        A("It is a **safety limit**. The %s stage sheds rather than queues, and `%s` is" % (
            comp["name"], p0))
        A("responsible for reporting the shed count. The number itself is unchanged at %d." % (
            comp["limit"]))
    elif status == "superseded":
        A("Recorded as a cost limit at the time. **Superseded** by the later ruling that the")
        A("%s stage sheds rather than queues; this entry is kept because the reasoning is" % (
            comp["name"]))
        A("cited in two audits and removing it would break those references.")
    else:
        A("**Withdrawn** before a ruling. The proposal assumed `%s` could absorb the shed" % p0)
        A("load, which it cannot. Kept as evidence that the option was considered.")
    A("")
    A("## Consequences")
    A("")
    A("- `docs/%s.md` states the current behaviour and is authoritative over this entry." % (
        comp["name"]))
    A("- No change to `DEFAULT_%s_LIMIT`." % comp["name"].upper())
    A("- The %s team owns the shed-count dashboard." % comp["team"])
    A("")
    return "\n".join(L)


def emit_readme(project, package, comps):
    L = []
    A = L.append
    A("# %s" % project)
    A("")
    A("A staged delivery pipeline. Each stage is a module under `src/`, is configured from one")
    A("section of the manifest, and is documented under `docs/`. The dated history of every")
    A("configuration decision is under `history/`.")
    A("")
    A("## Reading order")
    A("")
    A("1. `docs/architecture.md` - how the stages compose, and which order they drain in.")
    A("2. `docs/operations.md` - what to do when a stage refuses work.")
    A("3. `docs/policy/` - the rules that outrank both of the above.")
    A("4. `history/` - why each number is the number it is. **Dated, and superseded entries")
    A("   are kept**: a superseded entry is evidence, not a live instruction.")
    A("")
    A("## Stages")
    A("")
    A("| stage | module | doc | owner |")
    A("| --- | --- | --- | --- |")
    for c in comps:
        A("| %s | `src/%s.py` | `docs/%s.md` | %s |" % (
            c["name"], c["module"], c["name"], c["owner"]))
    A("")
    A("## Conventions")
    A("")
    A("- Nothing is imported at module scope across stages; the pipeline is assembled from the")
    A("  manifest at run time.")
    A("- A `snapshot()` is always sorted. Insertion order is never part of any contract.")
    A("- A configuration key that is present but unparseable is a startup error, never a")
    A("  silent fallback to the module constant.")
    A("- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`")
    A("  outranks everything else.")
    A("")
    return "\n".join(L)


def emit_architecture(project, comps):
    L = []
    A = L.append
    A("# Architecture")
    A("")
    A("`%s` is a linear pipeline of independent stages. A stage never imports another stage;" % project)
    A("the manifest names them in order and the assembler wires them together at run time.")
    A("")
    A("## Drain order")
    A("")
    A("Stages are sealed in **reverse manifest order**, so that no stage is sealed while an")
    A("upstream stage can still hand it work. The order is:")
    A("")
    for i, c in enumerate(comps):
        A("%d. `%s` (%s)" % (i + 1, c["name"], c["concern"]))
    A("")
    A("Sealing out of order is the single most common cause of a `pending` record surviving")
    A("into the audit trail, and it is why `seal()` is idempotent: the drain may be retried")
    A("safely, but it may not be reordered.")
    A("")
    A("## Why stages do not import each other")
    A("")
    A("An earlier revision wired the stages with direct imports. It worked and it made two")
    A("things impossible: running a subset of the pipeline in a test, and replacing one stage")
    A("without a coordinated deploy. Both are now routine. The cost is that a reader cannot")
    A("follow the pipeline by following imports, and must read the manifest instead.")
    A("")
    A("## The manifest")
    A("")
    A("`config/manifest.json` names each stage and carries its section. A section may set")
    A("`limit` and `window_s`; anything else in a section is ignored with a warning, which is")
    A("deliberate - it lets a section carry a note for a human reader.")
    A("")
    return "\n".join(L)


def emit_operations(project, comps, rng):
    L = []
    A = L.append
    A("# Operations")
    A("")
    A("## When a stage refuses work")
    A("")
    A("Every stage refuses rather than queues above its `limit`. A refusal is normal and is")
    A("not an incident on its own. It becomes an incident when the shed count exceeds the")
    A("stage's own window for two consecutive windows.")
    A("")
    A("| stage | limit | window (s) | on-call team |")
    A("| --- | ---: | ---: | --- |")
    for c in comps:
        A("| %s | %d | %d | %s |" % (c["name"], c["limit"], c["window"], c["team"]))
    A("")
    A("## Restart procedure")
    A("")
    A("1. Seal in reverse manifest order (`docs/architecture.md`).")
    A("2. Take a `snapshot()` of every stage and write it to the evidence store **before**")
    A("   anything is restarted. A snapshot taken afterwards is not evidence.")
    A("3. Restart the assembler, not the individual stages.")
    A("4. Compare the new snapshot against the old one. Any record that changed state without")
    A("   passing through `pending` is a defect and is reported rather than corrected.")
    A("")
    A("## What never happens in flight")
    A("")
    A("- A limit is never changed while the pipeline is running. It is changed in the")
    A("  manifest and takes effect on the next assembly.")
    A("- An `abandoned` record is never deleted. Retention is governed by `docs/policy/`.")
    A("- A stage is never sealed twice in the same drain to 'make sure'; `seal()` is")
    A("  idempotent, so a second call is harmless, but a second call in the logs is read as")
    A("  evidence that the operator was unsure, and the drain is audited.")
    A("")
    return "\n".join(L)


def emit_policy(project, comps, rng, index):
    c = comps[index % len(comps)]
    topics = [
        ("retention", "How long each record class is kept, and who may shorten it"),
        ("evidence", "What counts as evidence, and why a snapshot's timing matters"),
        ("access", "Who may read a snapshot, and what is redacted before they do"),
        ("change", "What may be changed in flight, and what may not"),
        ("escalation", "Who is called, in what order, and what they are told"),
    ]
    name, title = topics[index % len(topics)]
    L = []
    A = L.append
    A("# Policy: %s" % name)
    A("")
    A("*%s.*" % title)
    A("")
    A("**This policy outranks `docs/architecture.md`, `docs/operations.md`, every component")
    A("document and every history entry.** Where a component document describes behaviour this")
    A("policy forbids, the component document is stale and is to be corrected, not followed.")
    A("")
    A("## Rules")
    A("")
    A("1. A record that has reached `settled` is immutable. No stage, no operator and no")
    A("   repair script may alter it. A correction is a new record that cites the old one.")
    A("2. An `abandoned` record is retained for the full retention term of its class, even")
    A("   when it is obviously the result of a defect. Deleting it destroys the evidence that")
    A("   the defect existed.")
    A("3. The retention term is a property of the record's class and never of the stage that")
    A("   produced it. Two stages may hold records of the same class for different reasons and")
    A("   for the same term.")
    A("4. A limit change is a manifest change and takes effect at the next assembly. A limit")
    A("   changed by any other route is reverted and the route is reported.")
    A("5. The %s stage carries the longest term of any stage, %d days, because it is the" % (
        c["name"], c["limit"]))
    A("   boundary at which ordering becomes durable.")
    A("")
    A("## What this policy does not cover")
    A("")
    A("It does not say what a stage should do when it cannot reach the evidence store. That")
    A("is deliberately left to `docs/operations.md`, because the answer depends on which")
    A("stage and on how far the drain has progressed, and a policy that tried to enumerate")
    A("those cases would be wrong within a quarter.")
    A("")
    return "\n".join(L)


def emit_manifest(project, package, comps):
    return json.dumps({
        "project": project,
        "package": package,
        "stages": [
            {"name": c["name"], "module": c["module"], "class": c["cls"],
             "limit": c["limit"], "window_s": c["window"], "owner": c["owner"]}
            for c in comps
        ],
    }, indent=2) + "\n"


def emit_changelog(comps, rng):
    L = []
    A = L.append
    A("# Changelog")
    A("")
    A("Newest first. Every entry names the stage it touched and the history entry that")
    A("authorised it. An entry with no history reference was an emergency and is audited.")
    A("")
    for i, c in enumerate(comps):
        A("## %04d-%02d-%02d" % (2033 + (i % 3), 1 + (i * 5) % 12, 1 + (i * 13) % 27))
        A("")
        A("- `%s`: %s the %s window to %d s (history/%04d)." % (
            c["module"], rng.choice(["widened", "narrowed", "documented", "re-derived"]),
            c["noun"], c["window"], i))
        A("- `docs/%s.md`: brought in line with the module constants." % c["name"])
        A("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return len(text)


def measure(root):
    chars = 0
    files = 0
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                continue
            with open(os.path.join(base, n), encoding="utf-8") as fh:
                chars += len(fh.read())
            files += 1
    return files, chars


def build(out, project, package, seed, target_tokens):
    rng = random.Random(seed)
    target_chars = int(target_tokens * CHARS_PER_TOKEN)

    # Components are emitted one at a time and the total is measured after each, so the
    # corpus lands on the requested size rather than on an estimate of it. The index-summary
    # files (README, architecture, operations, changelog) list every component, so they are
    # written LAST, once the component set is final.
    namer = Namer(rng, len(DOMAINS) + 20)
    pool = namer.components

    # a fixed overhead allowance for the index files, which grow with the component count
    def index_overhead(n):
        return 3200 + 380 * n

    comps = []
    body = 0
    for i, comp in enumerate(pool):
        if len(comps) >= 3 and body + index_overhead(len(comps)) >= target_chars:
            break
        peers = [c for c in pool[:i] + pool[i + 1:i + 3]][:2] or [comp]
        body += write(os.path.join(out, "src", package, comp["module"] + ".py"),
                      emit_module(comp, peers, project, package))
        body += write(os.path.join(out, "tests", "test_" + comp["name"] + ".py"),
                      emit_test(comp, package))
        body += write(os.path.join(out, "docs", comp["name"] + ".md"),
                      emit_component_doc(comp, peers, project))
        body += write(os.path.join(out, "history", "%04d-%s.md" % (i, comp["name"])),
                      emit_history(comp, peers, project, rng, i))
        comps.append(comp)

    write(os.path.join(out, "README.md"), emit_readme(project, package, comps))
    write(os.path.join(out, "docs", "architecture.md"), emit_architecture(project, comps))
    write(os.path.join(out, "docs", "operations.md"), emit_operations(project, comps, rng))
    write(os.path.join(out, "config", "manifest.json"), emit_manifest(project, package, comps))
    write(os.path.join(out, "history", "CHANGELOG.md"), emit_changelog(comps, rng))
    write(os.path.join(out, "src", package, "__init__.py"),
          '"""%s pipeline stages. Assembled from config/manifest.json at run time."""\n'
          % project)

    # top up with policy pages until the target is reached; they are the cheapest
    # honest material to add, and every one of them is genuinely authoritative.
    idx = 0
    while True:
        files, chars = measure(out)
        if chars >= target_chars or idx >= 40:
            break
        write(os.path.join(out, "docs", "policy", "%02d-policy.md" % idx),
              emit_policy(project, comps, rng, idx))
        idx += 1

    files, chars = measure(out)
    return {"files": files, "chars": chars,
            "tokens": int(round(chars / CHARS_PER_TOKEN)),
            "chars_per_token": CHARS_PER_TOKEN,
            "components": len(comps), "policy_pages": idx}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--package", default=None)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--target-tokens", type=int, default=31000)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    package = args.package or args.project.replace("-", "_").split("_")[0]
    info = build(args.out, args.project, package, args.seed, args.target_tokens)
    if not args.quiet:
        print(json.dumps(info))


if __name__ == "__main__":
    main()
