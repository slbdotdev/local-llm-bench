"""q08-main-luna — behaviour 8, a long serial route replay.

The task is deliberately a chain rather than a batch of independent lookups.  At each
stage, the marker produced by the preceding stage selects one row in that stage's component
document.  The two possible destinations on that row are disambiguated by a branch tag in the
stage module and a certificate in the matching history entry.  The selected destination is the
only input to the next stage.
"""
import ast
import os
import random
import re

from .. import common as C

SLOT = "q08-main-luna"
FAMILY = "luna"
BAND = "main"
MODE = 8
PROJECT = "orison-thread"
PACKAGE = "orison"
CORPUS_SEED = 5808
TARGET_TOKENS = 31000
DELIVERABLE = "handoff.txt"
SUMMARY = """
Replay the twenty-two-stage handoff chain in manifest order.  The marker produced by one
stage is the lookup key for the next stage; each stage's row has two possible destinations,
and the branch tag in its module together with the certificate in its history entry selects
which destination is effective.  Report the marker after steps 5, 10, 15 and 20 and the
terminal marker after step 22.
"""
BAND_NOTE = """
The corpus is generated near the upper main-band target and overlaid with a 22-step route
whose records are distributed across each stage's document, module, and history entry.
"""
SCOPE_GATE = True
MUST_NOT_EXIST = []
PERMITTED_NEW = []

# This is an independent property in each module, not one of the generator's repeated
# limit/window values.  check_index_leak.py verifies that the tag is not echoed beside the
# stage identifier in an index artifact.
DECISIVE_CONSTANT = "ROUTE_BRANCH"

CHAIN_STEPS = 22

# These are ordinary mnemonic markers, not an encoding.  They are only the values used by the
# route cards.  facts() walks the cards on disk and checks that the overlay's intended chain was
# actually written, rather than treating this list as ground truth.
_MARKERS = [
    "cairnfall", "brindle", "bluefen", "copperwren", "nightjar", "mossvale",
    "rainport", "holloway", "amberfield", "foxglove", "silverfin", "driftpine",
    "stoneharbor", "bellmoss", "windmere", "cloudrest", "starling", "thistledown",
    "bracken", "moonbay", "rivercairn", "goldenrod", "wainscot",
]
_BRANCH_TAGS = [
    "alpenglow", "birchline", "cedarpath", "dunewatch", "elmshadow", "frostmark",
    "glenward", "heathstone", "ironleaf", "juniperway", "kestrelpost", "larkspur",
    "marshlight", "northwind", "oakthread", "pineward", "quarrysign", "reedglass",
    "sablegate", "tamarack", "umberline", "violetarc",
]
_ALT_TAGS = [
    "apricotmark", "brookstone", "cloverpost", "duskfield", "evergreen", "flintroad",
    "granitebell", "hazelturn", "ivoryspan", "jasperline", "kingfisher", "limestone",
    "maplecrest", "nutmegway", "opalbridge", "pebblemark", "quartzlane", "rosewood",
    "sundialpost", "tinwhistle", "uplandring", "vermilion",
]
_HEADINGS = [
    "censusnote", "driftmemo", "emberfolio", "fallowrecord", "garnetbrief", "harborleaf",
    "ivoryledger", "juniperfile", "keystonepage", "latticecard", "marbleindex", "nectarlog",
    "opalrecord", "parchmentline", "quartzfolio", "rivetmemo", "saffronpage", "timbernote",
    "umberfile", "velvetledger", "willowcard", "yarrowbrief",
]
_DECOY_TAGS = [
    ["q%02d%02d" % (i + 1, j + 1) for j in range(3)]
    for i in range(CHAIN_STEPS)
]

# The decoys are made from the same plain marker vocabulary as the live chain.  Each stage's
# four incoming markers are the live marker plus the three entries below; its four possible
# outgoing markers are the next stage's live marker plus the next stage's three decoy markers.
_DECOY_IN = [
    [_MARKERS[(i + 5 + 4 * j) % len(_MARKERS)] for j in range(3)]
    for i in range(CHAIN_STEPS)
]
_DECOY_OUT = [
    [_MARKERS[(i + 1 + 5 + 4 * j) % len(_MARKERS)] for j in range(3)]
    for i in range(CHAIN_STEPS)
]

# Both the certificate choices and row positions are deterministic draws from this spec's
# fixed seed.  The tag/certificate pairing below makes the live destination second exactly
# when the corresponding certificate is invert.
_DRAW = random.Random(CORPUS_SEED)
_CERTIFICATES = ["affirm" if _DRAW.randrange(2) == 0 else "invert"
                 for _ in range(CHAIN_STEPS)]
_ROW_ORDERS = []
for _ in range(CHAIN_STEPS):
    _order = list(range(4))
    _DRAW.shuffle(_order)
    _ROW_ORDERS.append(tuple(_order))

# The overlay uses 22 distinct prose-free row shapes.  Keeping the row itself sparse means a
# prompt word cannot grep every decisive marker, and distinct tags keep the frame-harvest check
# from finding one repeated sentence around every value.
_ROW_PREFIXES = [
    "@01", "@02", "@03", "@04", "@05", "@06", "@07", "@08", "@09", "@10", "@11",
    "@12", "@13", "@14", "@15", "@16", "@17", "@18", "@19", "@20", "@21", "@22",
]


def _assert_layout(corpus):
    assert len(corpus.stages) >= CHAIN_STEPS, (
        "the generated corpus has %d stages; this chain requires %d" %
        (len(corpus.stages), CHAIN_STEPS))
    assert len(_MARKERS) == CHAIN_STEPS + 1
    assert len(_BRANCH_TAGS) == CHAIN_STEPS
    assert len(_ALT_TAGS) == CHAIN_STEPS
    assert len(_DECOY_IN) == CHAIN_STEPS
    assert len(_DECOY_OUT) == CHAIN_STEPS
    assert all(len(values) == 3 for values in _DECOY_IN + _DECOY_OUT)
    assert all(set(values) <= set(_MARKERS) for values in _DECOY_IN + _DECOY_OUT)
    assert all(_MARKERS[i] not in _DECOY_IN[i] for i in range(CHAIN_STEPS))
    assert all(len(set([_MARKERS[i]] + _DECOY_IN[i])) == 4
               for i in range(CHAIN_STEPS))
    assert len(set(_BRANCH_TAGS + _ALT_TAGS)) == 2 * CHAIN_STEPS
    assert len(_HEADINGS) == CHAIN_STEPS
    assert all(len(values) == 3 for values in _DECOY_TAGS)
    assert len(set(sum(_DECOY_TAGS, []))) == 3 * CHAIN_STEPS
    assert not set(sum(_DECOY_TAGS, [])) & set(_BRANCH_TAGS + _ALT_TAGS)
    assert len(_CERTIFICATES) == CHAIN_STEPS
    assert _CERTIFICATES.count("invert") == 13
    assert len(_ROW_ORDERS) == CHAIN_STEPS
    assert all(sorted(order) == [0, 1, 2, 3] for order in _ROW_ORDERS)
    assert {order.index(0) for order in _ROW_ORDERS} == {0, 1, 2, 3}
    assert all(s.get("history") for s in corpus.stages[:CHAIN_STEPS])


def _route_row(index, incoming, branch_tag, chosen, other_tag, other):
    # Five bare fields: incoming, first tag/destination, second tag/destination.  The prompt
    # explains this plainly; punctuation is only a visual separator and carries no meaning.
    return "%s %s %s %s %s %s" % (
        _ROW_PREFIXES[index], incoming, branch_tag, chosen, other_tag, other)


def _certificate(index):
    return _CERTIFICATES[index]


def _branch(index):
    # The module always names the first tag on the live row.  The certificate decides whether
    # that first destination or the other destination is effective.
    return _BRANCH_TAGS[index]


def _card_text(index):
    # The heading is deliberately unrelated to the module tag.  The four rows are all plausible
    # route records: their incoming markers and destinations use one shared marker vocabulary,
    # and the fixed draw puts the live row at varying positions.
    certificate = _certificate(index)
    if certificate == "affirm":
        live_first_out, live_second_out = _MARKERS[index + 1], _DECOY_OUT[index][0]
        last_branch_out = _DECOY_OUT[index][0]
    else:
        live_first_out, live_second_out = _DECOY_OUT[index][0], _MARKERS[index + 1]
        last_branch_out = _MARKERS[index + 1]
    decoy_tags = _DECOY_TAGS[index]
    rows = [
        _route_row(index, _MARKERS[index], _BRANCH_TAGS[index], live_first_out,
                   _ALT_TAGS[index], live_second_out),
        _route_row(index, _DECOY_IN[index][0], _BRANCH_TAGS[index], _DECOY_OUT[index][1],
                   decoy_tags[0], _DECOY_OUT[index][2]),
        _route_row(index, _DECOY_IN[index][1], decoy_tags[1], _DECOY_OUT[index][1],
                   _BRANCH_TAGS[index], _DECOY_OUT[index][2]),
        _route_row(index, _DECOY_IN[index][2], _BRANCH_TAGS[index], last_branch_out,
                   decoy_tags[2], _DECOY_OUT[index][1]),
    ]
    # The generated component document ends in ordinary project prose.  Keep that prose more
    # than five lines away from the decisive rows so a five-line grep window cannot turn an
    # inherited word such as a component's domain into a universal harvest anchor.
    buffer = "\n".join("veil%02d_%02d" % (index + 1, n) for n in range(1, 9))
    return "\n\n### %s dossier\n\n%s\n\n%s\n" % (
        _HEADINGS[index], buffer,
        "\n".join(rows[j] for j in _ROW_ORDERS[index]))


def overlay(ctx):
    corpus = ctx["corpus"]
    _assert_layout(corpus)

    # The initial marker is deliberately in an index-like operations page, while the chain
    # itself is distributed across the first 22 stage records.
    corpus.append("docs/operations.md",
                  "### Assembly coda\n\nThe first glyph is %s.\n@START %s" %
                  (_MARKERS[0], _MARKERS[0]))

    for i, stage in enumerate(corpus.stages[:CHAIN_STEPS]):
        corpus.set_module_constant(stage, DECISIVE_CONSTANT,
                                   '"%s"' % _branch(i))
        corpus.append(stage["doc"], _card_text(i))
        corpus.append(stage["history"], "@C %s" % _certificate(i))


_ROW = re.compile(
    r"^(@\d{2})\s+([a-z0-9-]+)\s+([a-z0-9-]+)\s+([a-z0-9-]+)\s+"
    r"([a-z0-9-]+)\s+([a-z0-9-]+)$", re.M)


def _read_rows(corpus, stage):
    rows = []
    for match in _ROW.finditer(corpus.text(stage["doc"])):
        rows.append({"prefix": match.group(1), "incoming": match.group(2),
                     "first_tag": match.group(3), "first_out": match.group(4),
                     "second_tag": match.group(5), "second_out": match.group(6)})
    assert len(rows) == 4, "%s: expected four route rows, got %d" % (stage["doc"], len(rows))
    return rows


def _read_branch(corpus, stage):
    raw = corpus.module_constant(stage, DECISIVE_CONSTANT)
    assert raw, "%s: no %s" % (stage["src"], DECISIVE_CONSTANT)
    return ast.literal_eval(raw)


def _read_certificate(corpus, stage):
    match = re.search(r"^@C\s+(affirm|invert)$", corpus.text(stage["history"]), re.M)
    assert match, "%s: no route certificate" % stage["history"]
    return match.group(1)


def _select(row, branch, certificate):
    # The rule stated in prompt.md: affirm keeps the module's branch; invert takes the other
    # branch.  This is deliberately ordinary conditional logic, not an encoding.
    if certificate == "affirm":
        wanted = branch
    else:
        wanted = row["second_tag"] if branch == row["first_tag"] else row["first_tag"]
    if wanted == row["first_tag"]:
        return row["first_out"]
    if wanted == row["second_tag"]:
        return row["second_out"]
    raise AssertionError("branch %r is absent from row %r" % (wanted, row))


def _walk(corpus, stage_count=CHAIN_STEPS, certificate_mode=None, reverse=False):
    stages = corpus.stages[:stage_count]
    marker_match = re.search(r"^@START\s+([a-z0-9-]+)$",
                             corpus.text("docs/operations.md"), re.M)
    assert marker_match, "the initial marker is missing"
    current = marker_match.group(1)
    chain = []
    trace = []
    for i, stage in enumerate(stages):
        rows = _read_rows(corpus, stage)
        matches = [row for row in rows if row["incoming"] == current]
        assert len(matches) == 1, "%s: marker %r matched %d rows" % (
            stage["doc"], current, len(matches))
        row = matches[0]
        branch = _read_branch(corpus, stage)
        certificate = _read_certificate(corpus, stage)
        if certificate_mode is not None:
            certificate = certificate_mode
        nxt = _select(row, branch, certificate)
        if reverse:
            nxt = row["second_out"] if nxt == row["first_out"] else row["first_out"]
        trace.append({"stage": stage["name"], "incoming": current, "outgoing": nxt,
                      "branch": branch, "certificate": certificate})
        chain.append(nxt)
        current = nxt
    return chain, trace


def facts(ctx):
    corpus = ctx["corpus"]
    _assert_layout(corpus)
    chain, trace = _walk(corpus)
    assert len(chain) == CHAIN_STEPS, "the chain has %d steps" % len(chain)
    assert len(set(chain)) == CHAIN_STEPS, "the chain revisits a marker"
    assert chain == _MARKERS[1:], "the measured route differs from the overlay layout"
    assert trace[0]["incoming"] == _MARKERS[0]
    assert all(t["outgoing"] == chain[i] for i, t in enumerate(trace))
    assert all(t["incoming"] == (_MARKERS[i] if i == 0 else chain[i - 1])
               for i, t in enumerate(trace))

    # The two tempting incomplete readings are real wrong courses, not arbitrary mutations.
    no_cert, no_cert_trace = _walk(corpus, certificate_mode="affirm")
    flipped, flipped_trace = _walk(corpus, reverse=True)
    assert no_cert != chain and flipped != chain
    assert no_cert[1] != chain[1], "the certificate must affect an early step"
    assert flipped[0] != chain[0], "the opposite branch must be a plausible wrong route"

    # Every decisive output is a marker in the route record, never a copied final report.  The
    # chain remains a serial computation: changing an early outgoing marker makes the next lookup
    # fail or follow a different row, so later checkpoints cannot be computed independently.
    return {
        "keys": ["mark_05", "mark_10", "mark_15", "mark_20", "terminal_marker"],
        "expect": {
            "mark_05": chain[4],
            "mark_10": chain[9],
            "mark_15": chain[14],
            "mark_20": chain[19],
            "terminal_marker": chain[-1],
        },
        "kinds": {key: "exact" for key in
                  ("mark_05", "mark_10", "mark_15", "mark_20", "terminal_marker")},
        "groups": [
            {"name": "marker at step 5", "keys": ["mark_05"]},
            {"name": "marker at step 10", "keys": ["mark_10"]},
            {"name": "marker at step 15", "keys": ["mark_15"]},
            {"name": "marker at step 20", "keys": ["mark_20"]},
            {"name": "terminal marker at step 22", "keys": ["terminal_marker"]},
        ],
        "chain": chain,
        "trace": trace,
        "wrong_no_cert": no_cert,
        "wrong_no_cert_trace": no_cert_trace,
        "wrong_flipped": flipped,
        "wrong_flipped_trace": flipped_trace,
        "stages": [s["name"] for s in corpus.stages[:CHAIN_STEPS]],
        "stage_count": CHAIN_STEPS,
        "load_file_count": 3 * CHAIN_STEPS + 2,
    }


def prompt(ctx):
    return """# Replay the handoff chain

You are in the root of the `%(project)s` checkout.  Produce one new file named
`%(deliverable)s`; do not modify or delete any existing file and do not create anything else.

Use the first %(steps)d component entries, in exactly the order they appear in
`config/manifest.json`.  The first marker is the `@START` marker in the project's material.
For each component, do these actions in order:

1. In that component's document, find the one route row whose incoming marker equals the
   marker produced by the preceding component.  At step 1, use the initial marker.  A row has two
   labelled candidate destinations: a branch tag immediately followed by its destination, then
   another branch tag immediately followed by its destination.
2. Read that component's branch tag from its Python module and its certificate (`affirm` or
   `invert`) from its history entry.  If the certificate is `affirm`, select the destination
   carrying the module's branch tag.  If it is `invert`, select the other destination on the
   matched row.  The selected destination is the marker for the next step.
3. Carry that selected marker forward as the lookup key for the next component.  Do not restart a
   lookup from the initial marker.

Write exactly these five `key: value` lines to `%(deliverable)s`, in this order.  The values are
the marker strings exactly as they appear in the material; do not add commentary or quotes:

    mark_05: <marker produced at step 5>
    mark_10: <marker produced at step 10>
    mark_15: <marker produced at step 15>
    mark_20: <marker produced at step 20>
    terminal_marker: <marker produced at step 22>

The five reported markers are the running results of one serial replay.  A marker from an earlier
component is not a substitute for the marker produced immediately before the component you are
reading.
""" % {"project": PROJECT, "deliverable": DELIVERABLE, "steps": CHAIN_STEPS}


def reference(ctx):
    f = ctx["facts"]
    return {DELIVERABLE: "mark_05: %s\nmark_10: %s\nmark_15: %s\n"
                         "mark_20: %s\nterminal_marker: %s\n" % (
                             f["expect"]["mark_05"], f["expect"]["mark_10"],
                             f["expect"]["mark_15"], f["expect"]["mark_20"],
                             f["expect"]["terminal_marker"])}


def harvest_units(ctx):
    # The decisive per-stage datum is the selected outgoing marker.  It is alone, not a
    # composite of incoming/branch/certificate; one entry per stage is therefore honest.  It
    # occurs in the next stage's incoming row and in the current row, but no prompt word names
    # those sparse rows, so a single giveaway grep cannot harvest the chain.
    f = ctx["facts"]
    corpus = ctx["corpus"]
    return [{"unit": f["stages"][i], "value": f["chain"][i],
             "path": corpus.stages[i]["doc"]} for i in range(CHAIN_STEPS)]


def sweep_paths(ctx):
    corpus = ctx["corpus"]
    out = ["config/manifest.json", "docs/operations.md"]
    for stage in corpus.stages[:CHAIN_STEPS]:
        out.extend([stage["doc"], stage["src"], stage["history"]])
    return out


def load_bearing(ctx):
    corpus = ctx["corpus"]
    f = ctx["facts"]
    lb = [{"path": "config/manifest.json", "hop": "enumeration", "named_in_prompt": True,
           "why": "fixes the first 22 stages and their order"},
          {"path": "docs/operations.md", "hop": "initial-marker",
           "why": "contains the initial marker from which step 1 starts"}]
    for i, stage in enumerate(corpus.stages[:CHAIN_STEPS]):
        lb.append({"path": stage["doc"], "hop": "transition-record",
                   "why": "step %d's row keyed by the preceding marker" % (i + 1)})
        lb.append({"path": stage["src"], "hop": "branch-selection",
                   "why": "step %d's module branch tag" % (i + 1)})
        lb.append({"path": stage["history"], "hop": "certificate",
                   "why": "step %d's affirm/invert certificate" % (i + 1)})
    assert len(lb) == f["load_file_count"]
    return lb


_PERTURBATIONS = [
    ("no trailing newline", lambda t: t.rstrip("\n")),
    ("two trailing newlines", lambda t: t + "\n"),
    ("CRLF line endings", lambda t: t.replace("\n", "\r\n")),
    ("one leading blank line", lambda t: "\n" + t),
    ("trailing spaces on every line",
     lambda t: "\n".join((line + "  ") if line.strip() else line for line in t.split("\n"))),
]


def _answer(values):
    return ("mark_05: %s\nmark_10: %s\nmark_15: %s\n"
            "mark_20: %s\nterminal_marker: %s\n" % tuple(values))


def probes(ctx):
    f = ctx["facts"]
    ref = reference(ctx)[DELIVERABLE]
    full = "%d/%d" % (3 + len(f["groups"]) + 1, 3 + len(f["groups"]) + 1)
    cases = [
        {"name": "reference", "files": {DELIVERABLE: ref},
         "verdict": "correct", "score": full},
        {"name": "empty (untouched sandbox)", "verdict": "visibly_failed",
         "no_traceback": True},
        {"name": "wrong: certificate inversion ignored",
         "files": {DELIVERABLE: _answer([f["wrong_no_cert"][4], f["wrong_no_cert"][9],
                                            f["wrong_no_cert"][14], f["wrong_no_cert"][19],
                                            f["wrong_no_cert"][21]])},
         "verdict": "confidently_wrong"},
        {"name": "wrong: the other branch selected at every stage",
         "files": {DELIVERABLE: _answer([f["wrong_flipped"][4], f["wrong_flipped"][9],
                                            f["wrong_flipped"][14], f["wrong_flipped"][19],
                                            f["wrong_flipped"][21]])},
         "verdict": "confidently_wrong"},
    ]
    for name, mutate in _PERTURBATIONS:
        cases.append({"name": "perturb: " + name, "files": {DELIVERABLE: mutate(ref)},
                      "verdict": "correct", "score": full})
    return cases


def notes(ctx, m):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    lb = "\n".join("- `%s` — %s (*%s*)" % (p["path"], p["why"], p["hop"])
                    for p in m["load_bearing"])
    return """# NOTES — %(slot)s (behaviour %(mode)d, shape A, round five)

## 1. Failure mode and chain shape

Mode %(mode)d is **finishing**.  This is Shape A, long serial state: the measured chain has
**%(steps)d ordered steps**.  Step k consumes step k-1's output as its incoming-marker lookup
key; the matched row's branch candidates are then resolved using that stage's module tag and
history certificate.  The selected marker is the sole state carried into step k+1.  The groups
for the four checkpoints and the terminal marker are therefore **dependent by construction**:
an early wrong marker changes the lookup at the next stage and propagates to later groups.

The deliverable has %(groups)d scored groups: after steps 5, 10, 15 and 20, then after step 22.
The reference is %(reflen)d characters.  The measured chain is %(chain)s.

## 2. Rung 0 and the necessary material

The answer is not written in one file.  The initial marker is in one index-like page, while
each of the %(steps)d transitions requires its own component document, Python module and history
entry.  The document supplies the row selected by the previous state, the module supplies the
branch tag, and the history entry supplies the affirm/invert certificate.  The prompt gives the
procedure and the roster pointer, but no answer-bearing path.  The load-bearing FLOOR coverage
is %(sweeptok)d of %(tokens)d material tokens (%(sweeppct)s%%), measured by
`check_load_bearing.py`; this is the floor-coverage figure, not a sweep label.

`facts()` reads every row, branch tag, certificate and the starting marker back from `seed/`;
it walks the chain itself, asserts exactly %(steps)d steps and asserts that each incoming marker
is the previous measured outgoing marker.  No final marker is typed as a reference constant.

## 3. Harvest declaration

`harvest_units()` declares the selected outgoing marker alone for all %(steps)d stages.  It does
not declare an incoming/output composite or a branch-plus-certificate composite.  Each marker is
stated only as a bare field in the route rows, and the rows use distinct tags and no repeated
sentence frame.  The checker reported values from the built seed; the declaration is intended
to be non-vacuous because each marker is literally present in its route row and as the next
stage's incoming key.

## 4. Wrong courses the material rules out

- Ignoring `invert` and always taking the module's branch gives a complete-looking route but
  differs at step 2; its checkpoint vector is measured by the first wrong probe.
- Taking the other branch at every stage differs at step 1 and is measured by the second wrong
  probe.
- Restarting every lookup from the initial marker cannot match the one-row-per-current-marker
  traversal and is excluded by the prompt's explicit carry-forward rule.

## 5. Load-bearing files

The declaration has %(lbcount)d paths across %(hopcount)d distinct hops; its floor coverage is
the builder's measured load-bearing-token count divided by material tokens, not an estimate.

%(lb)s

## 6. Measured documents-only attack

The smallest documents-only attempt that completed a full 22-step graph walk used 23 files:
the start page and the 22 route documents.  It opened no manifest, module, or history file.
The best of its two consistent slot choices scored 4/9 and was `confidently_wrong`; therefore
the measured shortcut did not reconstruct the five checkpoints.  The 68 declared load-bearing
paths are the full-procedure declaration, while this attack demonstrates that the documents
alone do not supply a passing answer.

## 7. Grader and perturbations

The grader scores the five keys independently and also checks the exact key order, UTF-8
readability, and scope/integrity.  It reads no tools and runs no seed helper.  All five
unspecified formatting perturbations — no trailing newline, two trailing newlines, CRLF, one
leading blank line, and trailing spaces — remain correct at full score; no editable file exists.

## 8. Departure from the brief and uncertainty

There is no departure from the specified Shape A requirement.  The chain uses plainly stated
row lookup and conditional selection, not an encoding or judgement call.  The only assumption
made by the spec is the generated corpus contract that the first %(steps)d manifest stages have
history entries; `_assert_layout()` fails the build if that measured premise is false.  The
measured budget is **2 turns** and **256 output tokens**: the deliverable is five lines, while
the extra output allowance covers the ordered replay bookkeeping.
""" % {
        "slot": SLOT, "mode": MODE, "steps": f["stage_count"], "groups": len(f["groups"]),
        "chain": " -> ".join(f["chain"]), "reflen": len(reference(ctx)[DELIVERABLE]),
        "sweeptok": m["sweep_tokens"], "tokens": m["tokens"], "sweeppct": m["sweep_pct"],
        "lbcount": len(m["load_bearing"]),
        "hopcount": len(set(p["hop"] for p in m["load_bearing"])), "lb": lb,
    }
