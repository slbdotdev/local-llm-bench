"""Fresh m08 main-band serial-state candidate."""
import csv
import itertools
import os
import random
import re

from r5 import common as C

SLOT = "m08-main-glm"
FAMILY = "glm"
BAND = "main"
MODE = 9
PROJECT = "emberledger"
PACKAGE = "emberledger_core"
CORPUS_SEED = 908173
TARGET_TOKENS = 24500
DELIVERABLE = "reconciliation.txt"
SUMMARY = "Reconcile a sealed, predecessor-linked sequence from scattered evidence pages."
BAND_NOTE = "main band; 20-step modular serial reconciliation with independent evidence frames"
SCOPE_GATE = True
MUST_NOT_EXIST = []
PERMITTED_NEW = []

MODULUS = 1000003
START = 271828


def _labels():
    rng = random.Random(8008)
    out = []
    while len(out) < 20:
        s = "".join(rng.choice("bcdfghjklmnpqrstvwxz") for _ in range(7)).title()
        grams = {s.lower()[i:i + 2] for i in range(len(s) - 1)}
        if not any(grams & {x.lower()[i:i + 2] for i in range(len(x) - 1)} for x in out):
            out.append(s)
    return out


def _numbers():
    rng = random.Random(8011)
    vals = list(range(1301, 9000))
    rng.shuffle(vals)
    charges = vals[:20]
    reserves = vals[20:40]
    return charges, reserves


def _folio_words(idx):
    rng = random.Random(9000 + idx)
    top = 3 + idx
    tail = 4 + idx
    words = ["".join(rng.choice("bcdghjklmnprstvwxyz") for _ in range(8))
             for _ in range(top * 3 + tail + 8)]
    return words, top, tail


def _unit_tags():
    rng = random.Random(9029)
    tags = []
    grams = set()
    while len(tags) < 40:
        tag = "".join(rng.choice("bcdghjklmnprstvwxyz") for _ in range(8))
        tgrams = {tag[i:i + 2] for i in range(len(tag) - 1)}
        if not (tgrams & grams):
            tags.append(tag)
            grams |= tgrams
    return tags


def _roster_tags():
    rng = random.Random(9031)
    tags = []
    grams = set()
    while len(tags) < 40:
        tag = "".join(rng.choice("bcdghjklmnprstvwxyz") for _ in range(8))
        tgrams = {tag[i:i + 2] for i in range(len(tag) - 1)}
        if not (tgrams & grams):
            tags.append(tag)
            grams |= tgrams
    return tags


def _rows(labels):
    rng = random.Random(8017)
    rids = []
    while len(rids) < 20:
        rid = "".join(rng.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(6))
        if rid not in rids:
            rids.append(rid)
    rows = []
    previous = "START"
    for i, label in enumerate(labels):
        rows.append({
            "rid": rids[i], "previous": previous, "card": label,
            "mult": 17 + ((i * 29) % 83), "bias": 91 + ((i * 47) % 701),
            "cw": 3 + ((i * 11) % 17), "rw": 5 + ((i * 19) % 23),
        })
        previous = rows[-1]["rid"]
    shuffled = list(rows)
    rng.shuffle(shuffled)
    return rows, shuffled


def _card_text(label, charge, reserve, idx):
    words, top, tail = _folio_words(idx)
    lines = ["# Evidence folio %s" % label]
    lines += ["Margin note %s: %s %s %s." % (words[j], words[j + 1], words[j + 2], words[j + 3])
              for j in range(0, top * 3, 3)]
    tags = _unit_tags()
    lines.append("%s: %d" % (tags[idx * 2], charge))
    lines += ["Cross-link %s %s %s." % (words[j], words[j + 1], words[j + 2])
              for j in range(top, top + 3)]
    lines += [""] * 18
    lines.append("%s: %d" % (tags[idx * 2 + 1], reserve))
    lines += ["Closing annotation %s: %s %s." % (words[j], words[j + 1], words[j + 2])
              for j in range(top + 3, top + 3 + tail)]
    lines += ["Appendix trace %s." % words[j] for j in range(top + 3 + tail, len(words))]
    return "\n".join(lines) + "\n"


def overlay(ctx):
    seed = ctx["seed"]
    labels = _labels()
    charges, reserves = _numbers()
    ordered, shuffled = _rows(labels)
    C.write(os.path.join(seed, "handbook", "reconciliation-procedure.md"), """# Reconciliation procedure

This procedure is the complete rule for the sealed reconciliation. Treat the repository as
read-only and use only information present in it. The twenty evidence folios each contain two
figures. The first is the signal and the second is the pulse; both figures for a folio are used.

Read `records/sequence.csv` as a sealed log. Its rows are deliberately not in execution order.
Each row has a `rid` and a `previous` field. Begin with the row whose `previous` is `START`, then
repeatedly choose the row whose `previous` equals the `rid` just consumed. Do not sort rows by
their printed position, identifier, or any other column. Every row must be consumed exactly once.

The row's `card` names the evidence folio. Read that folio's two numeric lines. Starting with
the opening figure 271828, apply each row in the linked order using this exact rule:

    next = (current * mult + signal * cw + pulse * rw + bias) modulo 1000003

Here `mult`, `cw`, `rw`, and `bias` are the numeric columns in the sealed log. The modulo is
the least non-negative remainder. This is a state transition: use the previous result as
`current`; never replace it with the opening figure between rows. The assembler's numbers are
not a source of figures and must not override a folio.

Write exactly one UTF-8 text file named `reconciliation.txt` at the repository root. It must
contain these six non-empty lines, in this order, with the decimal number after each colon:

opening: the opening figure
checkpoint_05: the state immediately after linked row 5
checkpoint_10: the state immediately after linked row 10
checkpoint_15: the state immediately after linked row 15
checkpoint_20: the state immediately after linked row 20
final: the state after linked row 20, repeated as the final value

Do not create any other file and do not modify an existing file.
""")
    for stage in ctx["corpus"].stages[:3]:
        ctx["corpus"].append(stage["doc"], "Output vocabulary is recorded here for interface review: opening, checkpoint_05, checkpoint_10, checkpoint_15, checkpoint_20, final.")
    rows_path = os.path.join(seed, "records", "sequence.csv")
    csv_text = "rid,previous,card,mult,bias,cw,rw\n"
    csv_text += "\n".join("%(rid)s,%(previous)s,%(card)s,%(mult)d,%(bias)d,%(cw)d,%(rw)d" % r
                           for r in shuffled) + "\n"
    C.write(rows_path, csv_text)
    for i, (label, charge, reserve) in enumerate(zip(labels, charges, reserves)):
        C.write(os.path.join(seed, "records", "folios", label.lower() + ".md"),
                _card_text(label, charge, reserve, i))
    C.write(os.path.join(seed, "decisions", "emberledger-reconciliation.md"), """# Emberledger decision record

The reconciliation review approved a linked-state reading of the sealed records. The log is an
index, not an answer table: its predecessor links determine the walk, while the folios supply
the two figures consumed by each transition. The procedure's opening figure and modulus are
authoritative. A checkpoint is a snapshot after the stated number of consumed links.

Reviewers must preserve the evidence folios byte-for-byte. A row that cannot be reached from the
START link is a malformed sealed log. A folio may be read when its linked row calls for it, but
its figures must not be copied into a new index or summary before the walk is complete.
""")


def _read_material(ctx):
    seed = ctx["seed"]
    rows = []
    with open(os.path.join(seed, "records", "sequence.csv"), encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    figures = {}
    for row in rows:
        path = os.path.join(seed, "records", "folios", row["card"].lower() + ".md")
        text = C.read(path)
        nums = [int(x) for x in re.findall(r"^[a-z][a-z-]*:\s*(\d+)$", text, re.M)]
        assert len(nums) == 2
        figures[row["card"]] = tuple(nums)
    return rows, figures


def _walk(rows):
    by_prev = {r["previous"]: r for r in rows}
    out = []
    prev = "START"
    while prev in by_prev:
        row = by_prev[prev]
        out.append(row)
        prev = row["rid"]
    return out


def _replay(order, figures):
    state = START
    states = []
    for row in order:
        signal, pulse = figures[row["card"]]
        state = (state * int(row["mult"]) + signal * int(row["cw"]) +
                 pulse * int(row["rw"]) + int(row["bias"])) % MODULUS
        states.append(state)
    return states


def _procedure_replay(ctx):
    text = C.read(os.path.join(ctx["seed"], "handbook", "reconciliation-procedure.md"))
    start = int(re.search(r"opening figure (\d+)", text).group(1))
    modulus = int(re.search(r"modulo (\d+)", text).group(1))
    assert start == START and modulus == MODULUS
    rows, figures = _read_material(ctx)
    state = start
    out = []
    for row in _walk(rows):
        signal, pulse = figures[row["card"]]
        state = (state * int(row["mult"]) + signal * int(row["cw"]) +
                 pulse * int(row["rw"]) + int(row["bias"])) % modulus
        out.append(state)
    return out


def _assert_shape(ctx, ordered, figures):
    rows, _ = _read_material(ctx)
    assert len(ordered) == 20 and len(rows) == 20
    assert len({r["rid"] for r in rows}) == 20
    positions = {r["rid"]: i for i, r in enumerate(rows)}
    actual_positions = [positions[r["rid"]] for r in ordered]
    fields = ("rid", "previous", "card", "mult", "bias", "cw", "rw")
    for field in fields:
        assert [r["rid"] for r in sorted(rows, key=lambda x: x[field])] != [r["rid"] for r in ordered]
    for k in range(2, 9):
        assert [r["rid"] for r in sorted(rows, key=lambda x: (positions[x["rid"]] % k, positions[x["rid"]]))] != [r["rid"] for r in ordered]
    for a in range(-64, 65):
        for b in range(20):
            assert actual_positions != [(a * i + b) % 20 for i in range(20)]
    baseline = _replay(ordered, figures)[-1]
    assert _replay(sorted(rows, key=lambda x: positions[x["rid"]]), figures)[-1] != baseline
    for i, row in enumerate(ordered):
        changed = dict(row)
        changed["bias"] = str(int(row["bias"]) + 1)
        altered = list(ordered)
        altered[i] = changed
        assert _replay(altered, figures)[-1] != baseline
    rng = random.Random(8023)
    for lo in range(20):
        for hi in range(lo + 2, 21):
            segment = ordered[lo:hi]
            expected = _replay(segment, figures)[-1]
            for _ in range(3):
                trial = list(segment)
                rng.shuffle(trial)
                if trial == segment:
                    trial = trial[1:] + trial[:1]
                assert _replay(trial, figures)[-1] != expected
    procedure = _procedure_replay(ctx)
    assert procedure == _replay(ordered, figures)


def _assert_frames(ctx, labels, charges, reserves):
    seed = ctx["seed"]
    top_offsets, eof_offsets, frames = [], [], []
    all_values = charges + reserves
    assert len(set(all_values)) == 40
    for label in labels:
        path = os.path.join(seed, "records", "folios", label.lower() + ".md")
        lines = C.read(path).splitlines()
        for value in (charges[labels.index(label)], reserves[labels.index(label)]):
            hits = [i for i, line in enumerate(lines) if str(value) in line]
            assert len(hits) == 1 and hits[0] != len(lines) - 1
            top_offsets.append(hits[0])
            eof_offsets.append(len(lines) - 1 - hits[0])
            stripped = re.sub(re.escape(str(value)), "", lines[hits[0]])
            frames.append(stripped)
    assert len(set(top_offsets)) >= 12 and len(set(eof_offsets)) >= 12
    assert max(top_offsets.count(x) for x in set(top_offsets)) <= 1
    assert max(eof_offsets.count(x) for x in set(eof_offsets)) <= 1
    assert max(frames.count(x) for x in set(frames)) <= 4
    for left, right in itertools.combinations(labels, 2):
        lg = {left.lower()[i:i + 2] for i in range(len(left) - 1)}
        rg = {right.lower()[i:i + 2] for i in range(len(right) - 1)}
        assert not (lg & rg)
    unit_names = _roster_tags()
    for left, right in itertools.combinations(unit_names, 2):
        lg = {left.lower()[i:i + 2] for i in range(len(left) - 1)}
        rg = {right.lower()[i:i + 2] for i in range(len(right) - 1)}
        assert not (lg & rg)
    # The independently drawn numeric sequences have no repeating first-difference cycle.
    for seq in (charges, reserves):
        diffs = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
        assert all(diffs != diffs[:k] * (len(diffs) // k) + diffs[:len(diffs) % k]
                   for k in range(1, 10))


def facts(ctx):
    labels = _labels()
    charges, reserves = _numbers()
    ordered, _ = _rows(labels)
    rows, figures = _read_material(ctx)
    assert [r["card"] for r in ordered] == labels
    assert {r["rid"] for r in ordered} == {r["rid"] for r in rows}
    _assert_shape(ctx, ordered, figures)
    _assert_frames(ctx, labels, charges, reserves)
    states = _replay(ordered, figures)
    assert states == _procedure_replay(ctx)
    expect = {"opening": str(START), "checkpoint_05": str(states[4]),
              "checkpoint_10": str(states[9]), "checkpoint_15": str(states[14]),
              "checkpoint_20": str(states[19]), "final": str(states[19])}
    return {"keys": list(expect), "expect": expect, "kinds": {},
            "groups": [{"name": k, "keys": [k]} for k in expect]}


def prompt(ctx):
    return """Read the repository's written material and reconcile its sealed records. The repository is your complete source of truth; do not infer a missing rule and do not use assembler-generated summaries as evidence.

Create exactly one UTF-8 text file at `reconciliation.txt` in the repository root. Do not create any other file and do not modify any existing file. Its six non-empty lines must use these keys in exactly this order, with one decimal integer after each colon:

opening
checkpoint_05
checkpoint_10
checkpoint_15
checkpoint_20
final

The value for `opening` is the stated opening figure. The four checkpoints are the running state after 5, 10, 15, and 20 linked records; `final` repeats the state after record 20.

Read all relevant repository material before calculating. Find the written reconciliation procedure, then follow its complete instructions: use the sealed record links to determine order, retrieve both figures associated with each linked record from its evidence material, and apply the stated transition successively. The printed row order is not execution order. Preserve the repository and verify your six numbers before finishing.
"""


def reference(ctx):
    f = ctx["facts"]["expect"]
    return {DELIVERABLE: "\n".join("%s: %s" % (k, f[k]) for k in ctx["facts"]["keys"]) + "\n"}


def harvest_units(ctx):
    labels = _labels()
    charges, reserves = _numbers()
    out = []
    tags = _roster_tags()
    for idx, (label, charge, reserve) in enumerate(zip(labels, charges, reserves)):
        path = "records/folios/%s.md" % label.lower()
        out.append({"unit": tags[idx * 2], "value": str(charge), "path": path})
        out.append({"unit": tags[idx * 2 + 1], "value": str(reserve), "path": path})
    return out


def sweep_paths(ctx):
    return C.walk_rel(ctx["seed"])


def load_bearing(ctx):
    paths = ["handbook/reconciliation-procedure.md", "records/sequence.csv",
             "decisions/emberledger-reconciliation.md"]
    paths += ["records/folios/%s.md" % x.lower() for x in _labels()[:12]]
    return ([{"path": paths[0], "hop": "procedure"},
             {"path": paths[1], "hop": "ordering"},
             {"path": paths[2], "hop": "ruling"}] +
            [{"path": p, "hop": "figure-%02d" % i} for i, p in enumerate(paths[3:], 1)])


def _answer(ctx, changes=None):
    f = ctx["facts"]["expect"]
    changes = changes or {}
    return "\n".join("%s: %s" % (k, changes.get(k, f[k])) for k in ctx["facts"]["keys"]) + "\n"


def probes(ctx):
    ref = _answer(ctx)
    wrong_final = _answer(ctx, {"final": str((int(ctx["facts"]["expect"]["final"]) + 1) % MODULUS)})
    wrong_mid = _answer(ctx, {"checkpoint_10": str((int(ctx["facts"]["expect"]["checkpoint_10"]) + 1) % MODULUS)})
    return [
        {"name": "reference", "files": {DELIVERABLE: ref}, "verdict": "correct", "score": "10/10", "no_traceback": True},
        {"name": "untouched", "verdict": "visibly_failed", "no_traceback": True},
        {"name": "wrong final arithmetic", "files": {DELIVERABLE: wrong_final}, "verdict": "confidently_wrong", "score": "9/10"},
        {"name": "wrong checkpoint arithmetic", "files": {DELIVERABLE: wrong_mid}, "verdict": "confidently_wrong", "score": "9/10"},
        {"name": "no trailing newline", "files": {DELIVERABLE: ref.rstrip("\n")}, "verdict": "correct", "score": "10/10"},
        {"name": "two trailing newlines", "files": {DELIVERABLE: ref + "\n"}, "verdict": "correct", "score": "10/10"},
        {"name": "crlf", "files": {DELIVERABLE: ref.replace("\n", "\r\n")}, "verdict": "correct", "score": "10/10"},
        {"name": "leading blank", "files": {DELIVERABLE: "\n" + ref}, "verdict": "correct", "score": "10/10"},
        {"name": "trailing spaces", "files": {DELIVERABLE: "\n".join(x + "  " for x in ref.split("\n"))}, "verdict": "correct", "score": "10/10"},
        {"name": "wrong order", "files": {DELIVERABLE: "\n".join(reversed(ref.splitlines())) + "\n"}, "verdict": "confidently_wrong", "score": "3/10"},
    ]


def notes(ctx, m):
    return """Failure mode 9: reading past the first screen, measured here as maintaining a linked 20-step state while reconciling scattered figures.

The distinguishing condition is a non-commutative predecessor walk. A model that sorts the visible CSV or treats the two folio figures as an order-free sum gets a plausible-looking integer but misses checkpoints and the final state.

The grader checks file existence, UTF-8 readability, exact key order, six dependent checkpoint groups, and the scope/integrity gate. Build assertions additionally replay the procedure from the seed, reject field/index/affine order shortcuts, perturb every row, reject shuffled contiguous segments, and inspect figure offsets and frames.

The answer is positive: six stated numeric snapshots are required. The shape-A checkpoint groups are dependent by construction; each later state consumes the prior state, so their separate groups expose where a chain breaks rather than claiming independent facts.

The sweep covers %(sweep_tokens)d of %(tokens)d material tokens (%(sweep_pct)s%%). Load-bearing hops are procedure, ordering, ruling, and twelve distinct folio-figure hops; the prompt gives no answer-bearing filename.

Near-miss probes: reference 10/10 correct; untouched visibly_failed; two one-number arithmetic errors 9/10 confidently_wrong; reversed order 3/10 confidently_wrong; all five whitespace/line-ending perturbations 10/10 correct.

No tool is added by the overlay, and generated tools are not allowed to print scored values with no arguments; this is checked by r5/check_tools.py.
""" % m
