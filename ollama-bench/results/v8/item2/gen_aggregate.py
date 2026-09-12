#!/usr/bin/env python3
"""Generator for v8 item-2 shape A: multi-needle aggregation, corpus in the prompt.

    python3 gen_aggregate.py                       # all three rungs, both A/B arms
    python3 gen_aggregate.py --rungs 20000         # one rung
    python3 gen_aggregate.py --chars-per-token 4.2 # re-converge on a measured constant

Why the material is in the prompt and why it is load-bearing: v7's main band supplied
29-36k of material on disk and the model's peak_prompt was 3,030-17,376 tokens, because
"the model now sets the material aside by never opening it" (D7-32). Here the register is
delivered in the prompt, so occupancy is guaranteed by construction, and the answer is an
aggregate over the register, so no part of it can be set aside: which returns are in the
governing set is a predicate on each return's own recorded values, and a return cannot be
skipped without first being read.

This is not the withdrawn synthetic fill. Every block in the register is a return of
exactly the same kind, in the same vocabulary, with the same fields; any of them could
carry a needle, and nothing about a block's heading, position, length or phrasing says
whether it does. The four wrong courses the register is built to catch are in NOTES.md.
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common                                                   # noqa: E402

TIER_THRESHOLD = 5
STATUSES_NOT_SETTLED = ["provisional", "withdrawn", "returned", "open"]
ABSENT_CODE = "S-0990"

RECORD_TEMPLATES = [
    ["Revision {rev} of the return for {name} was lodged on {date} and stands {status}.",
     "That revision places {code} in tier {tier} and gives its load as {load}."],
    ["{name} lodged revision {rev} on {date}.",
     "The return for {code} is {status}, sits at tier {tier}, and records a load of {load}."],
    ["The load recorded for {code} is {load}, on a return at tier {tier}.",
     "That return for {name} is revision {rev}, lodged {date}, and its status is {status}."],
    ["Tier {tier} is where {name} sits on revision {rev}, whose status is {status}.",
     "The load on that revision of {code}, lodged {date}, is {load}."],
    ["Status {status}: revision {rev} for {code}, lodged {date}.",
     "Load {load} at tier {tier} is what that revision carries for {name}."],
    ["On {date} the district accepted revision {rev} for {name} and marked it {status}.",
     "{code} carries tier {tier} on that revision and a load of {load}."],
    ["{code} appears at revision {rev} with a load of {load}.",
     "That revision of {name} was lodged {date}, is {status}, and places the station in tier {tier}."],
    ["The district file for {name} shows revision {rev} lodged on {date}.",
     "For {code} the status is {status}, the tier is {tier}, and the load is {load}."],
]

CALIB_TEMPLATES = [
    "A calibration offset of {off} is recorded for {code} against the district standard.",
    "{name} carries a calibration offset of {off} on the current instrument head.",
    "The offset applied to readings from {code} is {off} and has not been revised.",
]

SEQ_TEMPLATES = [
    "The reconciliation sequence mark carried by this revision of {code} is {seq}.",
    "{name} carries sequence mark {seq} in this quarter's reconciliation.",
    "This revision of {code} is marked {seq} in the reconciliation sequence.",
]

REMARK_ABSENT = ("The return for {name} replaces an entry formerly held at " + ABSENT_CODE
                 + ", a code retired at the consolidation and never reissued.")


# --------------------------------------------------------------------------------------
# the rules, as the prompt states them
# --------------------------------------------------------------------------------------
def solve(entries):
    by_station = {}
    for e in entries:
        by_station.setdefault(e["code"], []).append(e)
    governing, undetermined, superseded = [], [], []
    for code, es in sorted(by_station.items()):
        top = max(x["revision"] for x in es)
        at_top = [x for x in es if x["revision"] == top]
        if any(x["revision"] < top for x in es):
            superseded.append(code)
        if len(at_top) > 1:
            if len({x["load"] for x in at_top}) > 1:
                undetermined.append(code)
            continue
        e = at_top[0]
        if e["status"] == "settled" and e["tier"] >= TIER_THRESHOLD:
            governing.append(e)
    return governing, sorted(undetermined), sorted(superseded)


def sequence_total(entries):
    """Each sequence-marked return contributes its load times its mark.

    The pairing of load to mark is what makes this order-bearing: the multiset of the six
    loads does not determine the figure, so there is no commutative shortcut. The
    generator searches the six loads until exactly one of the 720 pairings reaches the
    graded figure, and `proofs()` checks all 720 exhaustively rather than sampling.
    """
    return sum(e["seq"] * e["load"] for e in entries if e.get("seq"))


def aggregates(governing, superseded):
    ranked = sorted(governing, key=lambda e: (-e["load"], e["code"]))
    return {"governing_count": len(governing),
            "governing_total": sum(e["load"] for e in governing),
            "top_five": [e["code"] for e in ranked[:5]],
            "sequence_total": sequence_total(governing),
            "superseded_codes": sorted(superseded)}


# --------------------------------------------------------------------------------------
# block rendering
# --------------------------------------------------------------------------------------
def render_block(b):
    e = b["entry"]
    tpl = RECORD_TEMPLATES[b["tpl"]]
    fields = dict(code=e["code"], name=b["name"], rev=e["revision"], status=e["status"],
                  tier=e["tier"], load=e["load"], date=e["date"])
    record = [s.format(**fields) for s in tpl]
    extra = []
    if e.get("calibration") is not None:
        extra.append(CALIB_TEMPLATES[b["calib_tpl"]].format(code=e["code"], name=b["name"],
                                                            off=e["calibration"]))
    if e.get("seq"):
        extra.append(SEQ_TEMPLATES[b["seq_tpl"]].format(code=e["code"], name=b["name"],
                                                        seq=e["seq"]))
    if b.get("absent_remark"):
        extra.append(REMARK_ABSENT.format(name=b["name"]))
    rng = random.Random(b["nseed"])
    body = common.narrative_lines(e["code"], b["name"], b["narr"], rng)
    cut = max(1, min(len(body), rng.randint(1, max(1, len(body) - 1))))
    sentences = body[:cut] + record + extra + body[cut:]
    # The heading carries no value. An earlier draft put the revision in it, which made
    # G3 and G4 answerable from a scan of the headings alone and made section 1's claim
    # that no heading tells you whether a return bears on a question false as built.
    head = "### %s -- %s\n\n" % (e["code"], b["name"])
    return head + "\n".join(sentences) + "\n\n"


def render_material(blocks):
    return "".join(render_block(b) for b in blocks)


# --------------------------------------------------------------------------------------
# the prompt
# --------------------------------------------------------------------------------------
RULES = """## 2. The rules

The register records, for each station, one or more **returns**. Every return carries a
revision number, a status, a tier, a load and the date it was lodged. Some returns also
carry a **sequence mark**, and some record a **calibration offset**.

A return **governs** its station when all four of these hold:

    G1  its status is `settled`;
    G2  its tier is %(t)d or higher;
    G3  no return for the same station carries a higher revision number;
    G4  no other return for the same station carries the same revision number.

A return for a station at a revision lower than that station's highest revision is
**superseded**. A superseded return governs nothing, whatever its status or its tier, and
its load is not the station's load.

Where two returns for one station carry that station's highest revision number and give
different loads, the station has **no determined governing load** and no return for it
enters the governing set.

The **governing set** is every return that governs. A station contributes at most one
return to it.
""" % {"t": TIER_THRESHOLD}

ANSWER_HEAD = """## 5. The answer

Write your answer to a new file `answer.json` in your working directory: one JSON object,
with exactly these nine keys.

| key | value |
| --- | --- |
| `governing_count` | an integer, or the string `INSUFFICIENT` |
| `governing_total` | an integer, or the string `INSUFFICIENT` |
| `top_five` | an array of five station-code strings, or the string `INSUFFICIENT` |
| `sequence_total` | an integer, or the string `INSUFFICIENT` |
| `superseded_codes` | an array of station-code strings, or the string `INSUFFICIENT` |
| `calibration_offset` | an integer, or the string `INSUFFICIENT` |
| `absent_station_load` | an integer, or the string `INSUFFICIENT` |
| `conflicting_station_load` | an integer, or the string `INSUFFICIENT` |
| `earliest_governing_station` | a station-code string, or the string `INSUFFICIENT` |

A station code is written as it appears in the register, for example `S-0147`. The order of
`top_five` is part of the answer; the order of `superseded_codes` is not. No other key, no
commentary inside the file.
"""

FOOTER = """## 7. Before you stop

`answer.json` in your working directory, one JSON object, the nine keys above. Do not
modify or delete `NOTICE.txt`. Work until the answer is complete, then stop.
"""


def build_prompt(parts, with_clause):
    out = [parts["head"], RULES, parts["example"], parts["questions"], ANSWER_HEAD]
    if with_clause:
        out.append(common.ABSTENTION_CLAUSE.strip() + "\n")
    out.append(parts["register_head"])
    out.append(parts["material"])
    out.append(FOOTER)
    return "\n".join(out)


HEAD = """# Station return reconciliation, this quarter

## 1. What you have

The whole of the material for this task is in this message: the register of station
returns, section 6 below. There are no files to open and nothing in your working directory
bears on the answer.

Every entry in the register is a return of the same kind, recorded in the same way, and
nothing about a heading, a position, a length or a phrasing tells you whether a given
return bears on any of the questions. Only the values the return itself records decide
that, and they decide it one return at a time.
"""


def example_block(rng):
    """Four illustration stations, in the register's own prose, with the five numbers."""
    ex_entries = [
        {"code": "X-9001", "revision": 3, "status": "settled", "tier": 7, "load": 310,
         "date": "2034-02-11", "seq": 2},
        {"code": "X-9002", "revision": 1, "status": "settled", "tier": 4, "load": 880,
         "date": "2034-01-06"},
        {"code": "X-9003", "revision": 2, "status": "settled", "tier": 6, "load": 455,
         "date": "2034-03-04"},
        {"code": "X-9003", "revision": 5, "status": "settled", "tier": 6, "load": 207,
         "date": "2034-05-19", "seq": 1},
        {"code": "X-9004", "revision": 4, "status": "withdrawn", "tier": 8, "load": 640,
         "date": "2034-04-02"},
    ]
    governing, undetermined, superseded = solve(ex_entries)
    agg = aggregates(governing, superseded)
    lines = [
        "## 3. A worked example",
        "",
        "These four stations are an illustration and are **not** in the register.",
        "",
        "> Revision 3 of the return for Example Alpha was lodged on 2034-02-11 and stands",
        "> settled. That revision places X-9001 in tier 7 and gives its load as 310. The",
        "> reconciliation sequence mark carried by this revision of X-9001 is 2.",
        ">",
        "> Example Beta lodged revision 1 on 2034-01-06. The return for X-9002 is settled,",
        "> sits at tier 4, and records a load of 880.",
        ">",
        "> The load recorded for X-9003 is 455, on a return at tier 6. That return for",
        "> Example Gamma is revision 2, lodged 2034-03-04, and its status is settled.",
        ">",
        "> X-9003 appears at revision 5 with a load of 207. That revision of Example Gamma",
        "> was lodged 2034-05-19, is settled, and places the station in tier 6. The",
        "> reconciliation sequence mark carried by this revision of X-9003 is 1.",
        ">",
        "> On 2034-04-02 the district accepted revision 4 for Example Delta and marked it",
        "> withdrawn. X-9004 carries tier 8 on that revision and a load of 640.",
        "",
        "X-9001 governs: settled, tier 7, its only revision. X-9002 fails G2 at tier 4.",
        "X-9003 has two returns; revision 5 governs and revision 2 is superseded, so the",
        "station's load is 207 and not 455. X-9004 fails G1.",
        "",
        "So for this illustration: `governing_count` is %d, `governing_total` is %d,"
        % (agg["governing_count"], agg["governing_total"]),
        "`top_five` is %s, `superseded_codes` is %s, and `sequence_total` is %d -- mark 1"
        % (json.dumps(agg["top_five"]), json.dumps(agg["superseded_codes"]),
           agg["sequence_total"]),
        "is carried by X-9003 whose governing load is 207, giving 207, and mark 2 is carried",
        "by X-9001 whose load is 310, giving 620; 207 plus 620 is %d."
        % agg["sequence_total"],
        "",
        "This illustration has only two governing returns, so its `top_five` holds two",
        "station codes. The register has more than five.",
        "",
    ]
    example = {"shape": "aggregate", "tier_threshold": TIER_THRESHOLD,
               "entries": ex_entries,
               "stated": {"governing_count": agg["governing_count"],
                          "governing_total": agg["governing_total"],
                          "top_five": agg["top_five"],
                          "sequence_total": agg["sequence_total"],
                          "superseded_codes": agg["superseded_codes"],
                          "undetermined_codes": undetermined}}
    return "\n".join(lines), example


def questions_block(calib_code, u1_code):
    return """## 4. The questions

1. How many returns are in the governing set? -> `governing_count`
2. What is the sum of the loads of the returns in the governing set? -> `governing_total`
3. Which five governing returns carry the highest loads? Give their station codes in
   descending order of load; where two loads are equal, the lower station code comes
   first. -> `top_five`
4. Some governing returns carry a sequence mark. Each of those contributes its own load
   multiplied by its own sequence mark. What is the sum of those contributions?
   -> `sequence_total`
5. Which stations have at least one superseded return? Give their station codes.
   -> `superseded_codes`
6. What calibration offset does station %s record? -> `calibration_offset`
7. What load does station %s record? -> `absent_station_load`
8. What is the governing load of station %s? -> `conflicting_station_load`
9. Which station in the governing set lodged its governing return earliest?
   -> `earliest_governing_station`
""" % (calib_code, ABSENT_CODE, u1_code)


REGISTER_HEAD = """## 6. The register

Every return in this quarter's register follows. They are in no particular order.
"""


# --------------------------------------------------------------------------------------
# construction
# --------------------------------------------------------------------------------------
ROLE_PLAN = [
    # (role, stratum index) -- 15 governing returns, three at each of the five depths
    ("gov", 0), ("gov", 0), ("gov", 0),
    ("gov", 1), ("gov", 1), ("gov", 1),
    ("gov", 2), ("gov", 2), ("gov", 2),
    ("gov", 3), ("gov", 3), ("gov", 3),
    ("gov", 4), ("gov", 4), ("gov", 4),
    # the superseded partner of a governing return, always at a different depth
    ("old", 0), ("old", 4), ("old", 3),
    # the two same-revision returns that leave one station undetermined
    ("u1", 1), ("u1", 3),
]
# which governing return each "old" block supersedes, by its index in the gov list
OLD_PARTNER = [12, 6, 3]
# sequence marks 1..6 attached to governing returns, deliberately not in depth order
SEQ_ASSIGN = {9: 1, 0: 2, 12: 3, 6: 4, 3: 5, 10: 6}


def build(rung_tokens, seed, cpt):
    rng = random.Random(seed)
    want_chars = common.target_chars(rung_tokens, cpt)

    # ---- coarse block count from a trial render
    est_block = 880
    n_blocks = max(60, int(round((want_chars - 9000) / est_block)))

    names = common.unique_names(n_blocks + 8, rng)
    codes = ["S-%04d" % c for c in range(101, 101 + n_blocks + 8) if "S-%04d" % c != ABSENT_CODE]

    blocks = []
    for i in range(n_blocks):
        e = {"code": codes[i], "revision": rng.randint(1, 6), "date": _date(rng),
             "load": rng.randint(100, 999), "seq": None, "calibration": None}
        if rng.random() < 0.5:
            e["status"] = "settled"
            e["tier"] = rng.randint(1, TIER_THRESHOLD - 1)
        else:
            e["status"] = rng.choice(STATUSES_NOT_SETTLED)
            e["tier"] = rng.randint(1, 9)
        if rng.random() < 0.25:
            e["calibration"] = rng.randint(-40, 40)
        blocks.append({"entry": e, "entry0": dict(e), "name": names[i],
                       "narr": rng.randint(3, 8),
                       "tpl": rng.randrange(len(RECORD_TEMPLATES)),
                       "calib_tpl": rng.randrange(len(CALIB_TEMPLATES)),
                       "seq_tpl": rng.randrange(len(SEQ_TEMPLATES)),
                       "nseed": rng.randrange(1 << 30), "locked": False, "role": "plain",
                       "absent_remark": False, "stratum": None})

    # ---- place the marked returns by character depth, then assign their values
    parts = {"head": HEAD, "register_head": REGISTER_HEAD, "material": ""}
    parts["example"], example = example_block(rng)
    parts["questions"] = questions_block("S-0000", "S-0000")     # placeholder, fixed width

    def render_all():
        parts["material"] = render_material(blocks)
        return build_prompt(parts, False)

    assigned = None
    for _ in range(3):
        common.tune_narrative(blocks, render_all, want_chars, rng)
        assigned = _assign_roles(blocks, rng)
        parts["questions"] = questions_block(assigned["calib_code"], assigned["u1_code"])

    # ---- final tune with the real question text in place
    common.tune_narrative(blocks, render_all, want_chars, rng)
    prompt_noabst = render_all()
    prompt_abst = build_prompt(parts, True)

    entries = [b["entry"] for b in blocks]
    governing, undetermined, superseded = solve(entries)
    agg = aggregates(governing, superseded)
    positions = _positions(blocks, prompt_noabst, parts)

    answers = _answers(agg, blocks, assigned, governing)
    return {"blocks": blocks, "entries": entries, "governing": governing,
            "undetermined": undetermined, "superseded": superseded, "agg": agg,
            "assigned": assigned, "positions": positions, "example": example,
            "prompt_noabst": prompt_noabst, "prompt_abst": prompt_abst,
            "answers": answers, "parts": parts}


def _date(rng):
    return "2034-%02d-%02d" % (rng.randint(1, 12), rng.randint(1, 28))


def _assign_roles(blocks, rng):
    """Put every marked return at the depth its plan names, measured in characters.

    Every pass starts from the untouched entries, so a block that was marked on a previous
    pass carries nothing over: a stale duplicate code or a stale settled/high tier would
    silently change the governing set.
    """
    for b in blocks:
        b["role"] = "plain"
        b["absent_remark"] = False
        b["locked"] = False
        b["stratum"] = None
        b["entry"] = dict(b["entry0"])
    material = render_material(blocks)
    offs, total = [], len(material)
    at = 0
    for b in blocks:
        t = render_block(b)
        offs.append((at + len(t) / 2.0) / float(total))
        at += len(t)

    taken = set()

    def nearest(frac):
        best, bestd = None, 9e9
        for i, f in enumerate(offs):
            if i in taken:
                continue
            d = abs(f - frac)
            if d < bestd:
                best, bestd = i, d
        taken.add(best)
        return best

    # three governing returns per stratum, spread by a small depth offset
    picks = []
    for role, s in ROLE_PLAN:
        k = len([1 for r, ss in picks if (r, ss) == (role, s)])
        frac = common.STRATA[s] + (k - 1) * 0.012
        picks.append((role, s))
        idx = nearest(frac)
        blocks[idx]["role"] = role
        blocks[idx]["locked"] = True
        blocks[idx]["stratum"] = common.STRATA[s]

    gov_idx = [i for i, b in enumerate(blocks) if b["role"] == "gov"]
    old_idx = [i for i, b in enumerate(blocks) if b["role"] == "old"]
    u1_idx = [i for i, b in enumerate(blocks) if b["role"] == "u1"]
    assert len(gov_idx) == 15 and len(old_idx) == 3 and len(u1_idx) == 2

    # ---- governing returns: settled, tier at or above the threshold, distinct loads
    loads = rng.sample(range(120, 999), 40)
    for n, i in enumerate(gov_idx):
        e = blocks[i]["entry"]
        e["status"] = "settled"
        e["tier"] = rng.randint(TIER_THRESHOLD, 9)
        e["revision"] = rng.randint(3, 6)
        e["load"] = loads[n]
        e["seq"] = SEQ_ASSIGN.get(n)
        e["calibration"] = rng.randint(-40, 40) if rng.random() < 0.3 else None

    # ---- the six sequence-marked loads are chosen so that exactly one of the 720 pairings
    # of those loads to those marks reaches the graded figure
    seq_positions = sorted(SEQ_ASSIGN, key=lambda n: SEQ_ASSIGN[n])
    marks = [SEQ_ASSIGN[n] for n in seq_positions]
    used = {blocks[i]["entry"]["load"] for i in gov_idx}
    pool = [v for v in range(120, 999) if v not in used]
    for _try in range(400):
        cand = rng.sample(pool, len(marks))
        target = sum(m * v for m, v in zip(marks, cand))
        hits = sum(1 for p in _perms(cand) if sum(m * v for m, v in zip(marks, p)) == target)
        if hits == 1:
            for n, v in zip(seq_positions, cand):
                blocks[gov_idx[n]]["entry"]["load"] = v
            break
    else:
        raise AssertionError("no six loads gave a unique pairing")

    # ---- the superseded partners: same station code, a lower revision, a different load
    for n, i in enumerate(old_idx):
        g = blocks[gov_idx[OLD_PARTNER[n]]]["entry"]
        e = blocks[i]["entry"]
        e["code"] = g["code"]
        e["revision"] = g["revision"] - rng.randint(1, 2)
        e["status"] = "settled"
        e["tier"] = rng.randint(TIER_THRESHOLD, 9)
        e["load"] = loads[20 + n]
        e["seq"] = g.get("seq")          # the superseded return carries the mark too
        e["calibration"] = None
        e["date"] = _earlier(g["date"], rng)
    # one superseded load is the largest in the register, so a reader who takes the
    # superseded return gets a different `top_five` and not only a different total
    blocks[old_idx[0]]["entry"]["load"] = 999

    # ---- the undetermined station: two returns, same highest revision, different loads
    u_code = blocks[u1_idx[0]]["entry"]["code"]
    for n, i in enumerate(u1_idx):
        e = blocks[i]["entry"]
        e["code"] = u_code
        e["revision"] = 5
        e["status"] = "settled"
        e["tier"] = rng.randint(TIER_THRESHOLD, 9)
        e["load"] = [486, 531][n]
        e["seq"] = None
        e["calibration"] = None

    # ---- no plain block may accidentally govern, and no code may collide
    seen = {}
    for i, b in enumerate(blocks):
        e = b["entry"]
        if b["role"] == "plain":
            if e["status"] == "settled" and e["tier"] >= TIER_THRESHOLD:
                e["tier"] = rng.randint(1, TIER_THRESHOLD - 1)
        seen.setdefault(e["code"], []).append(i)
    for code, idxs in seen.items():
        if len(idxs) > 1:
            roles = {blocks[i]["role"] for i in idxs}
            assert roles <= {"gov", "old", "u1"}, (code, roles)

    # ---- the earliest-lodged governing return is a two-way tie
    governing, _und, _sup = solve([b["entry"] for b in blocks])
    gov_sorted = sorted(governing, key=lambda e: e["date"])
    tie_date = "2034-01-02"
    gov_sorted[0]["date"] = tie_date
    gov_sorted[1]["date"] = tie_date
    for e in gov_sorted[2:]:
        if e["date"] <= tie_date:
            e["date"] = "2034-%02d-%02d" % (rng.randint(3, 12), rng.randint(1, 28))

    # ---- the calibration question names a governing station that records no offset
    calib_code = None
    for i in gov_idx:
        if blocks[i]["entry"]["calibration"] is None:
            calib_code = blocks[i]["entry"]["code"]
            break
    if calib_code is None:
        blocks[gov_idx[0]]["entry"]["calibration"] = None
        calib_code = blocks[gov_idx[0]]["entry"]["code"]

    # ---- the remark that names a station code with no return of its own, at mid depth
    mid = min(range(len(blocks)), key=lambda i: abs(offs[i] - 0.50) if i not in taken else 9e9)
    blocks[mid]["absent_remark"] = True
    blocks[mid]["locked"] = True

    return {"gov_idx": gov_idx, "old_idx": old_idx, "u1_idx": u1_idx,
            "u1_code": u_code, "calib_code": calib_code, "absent_remark_idx": mid,
            "tie_date": tie_date,
            "tie_codes": sorted([gov_sorted[0]["code"], gov_sorted[1]["code"]])}


def _perms(xs):
    import itertools
    return itertools.permutations(xs)


def _earlier(date, rng):
    y, m, d = date.split("-")
    m = max(1, int(m) - rng.randint(1, 3))
    return "%s-%02d-%02d" % (y, m, int(d))


def _positions(blocks, prompt, parts):
    """Realised depth of every marked return, in the corpus and in the whole prompt."""
    material = parts["material"]
    mat_start = prompt.index(material)
    out = []
    at = 0
    for b in blocks:
        t = render_block(b)
        if b["role"] != "plain" or b.get("absent_remark"):
            mid = at + len(t) / 2.0
            out.append({"code": b["entry"]["code"],
                        "role": "remark" if b.get("absent_remark") else b["role"],
                        "stratum_target": b.get("stratum"),
                        "revision": b["entry"]["revision"],
                        "seq": b["entry"].get("seq"),
                        "pos_in_corpus": round(mid / len(material), 4),
                        "pos_in_prompt": round((mat_start + mid) / len(prompt), 4),
                        "token_offset": common.count_tokens(prompt[:int(mat_start + mid)])})
        at += len(t)
    return out


def _answers(agg, blocks, assigned, governing):
    """The reference answer, the all-decoy answer, and one plausible wrong answer."""
    entries = [b["entry"] for b in blocks]
    ref = dict(agg)
    ref["calibration_offset"] = common.ABSTAIN
    ref["absent_station_load"] = common.ABSTAIN
    ref["conflicting_station_load"] = common.ABSTAIN
    ref["earliest_governing_station"] = common.ABSTAIN

    # decoy: G1 and G2 only -- supersession and the duplicate revision both ignored,
    # and every unanswerable question answered with a definite value.
    decoy_set = [e for e in entries
                 if e["status"] == "settled" and e["tier"] >= TIER_THRESHOLD]
    d_ranked = sorted(decoy_set, key=lambda e: (-e["load"], e["code"]))
    # for each sequence mark the decoy takes the lowest revision carrying it -- the return
    # a reader meets first and keeps
    d_seq = {}
    for e in decoy_set:
        if e.get("seq") and (e["seq"] not in d_seq
                             or e["revision"] < d_seq[e["seq"]]["revision"]):
            d_seq[e["seq"]] = e
    decoy = {"governing_count": len(decoy_set),
             "governing_total": sum(e["load"] for e in decoy_set),
             "top_five": [e["code"] for e in d_ranked[:5]],
             "sequence_total": sequence_total(list(d_seq.values())),
             "superseded_codes": [],
             "calibration_offset": 12,
             "absent_station_load": 418,
             "conflicting_station_load": 486,
             "earliest_governing_station": assigned["tie_codes"][0]}

    # plausible: the governing set is right, but each station's load is taken from the
    # first return met rather than from the highest revision.
    plaus_loads = {}
    for e in entries:
        plaus_loads.setdefault(e["code"], e["load"])
    p_gov = [dict(e, load=plaus_loads[e["code"]]) for e in governing]
    p_ranked = sorted(p_gov, key=lambda e: (-e["load"], e["code"]))
    plausible = {"governing_count": len(p_gov),
                 "governing_total": sum(e["load"] for e in p_gov),
                 "top_five": [e["code"] for e in p_ranked[:5]],
                 "sequence_total": sequence_total(p_gov),
                 "superseded_codes": agg["superseded_codes"],
                 "calibration_offset": 0,
                 "absent_station_load": 500,
                 "conflicting_station_load": 531,
                 "earliest_governing_station": assigned["tie_codes"][1]}
    return {"ref": ref, "decoy": decoy, "plausible": plausible}


# --------------------------------------------------------------------------------------
# structural proofs -- recorded in MANIFEST.json, and the reason this shape is allowed to
# deliver material in the prompt at all (v8 plan section 3, item 2)
# --------------------------------------------------------------------------------------
def proofs(built):
    entries = built["entries"]
    agg = built["agg"]
    gov = built["governing"]

    # every governing return is load-bearing: drop it and a graded key changes
    changed = 0
    for g in gov:
        rest = [e for e in entries if e is not g]
        g2, _u, s2 = solve(rest)
        if aggregates(g2, s2) != agg:
            changed += 1
    # the superseded and undetermined returns are load-bearing too
    marked = ([built["blocks"][i]["entry"] for i in built["assigned"]["old_idx"]]
              + [built["blocks"][i]["entry"] for i in built["assigned"]["u1_idx"]])
    marked_changed = 0
    for m in marked:
        rest = [e for e in entries if e is not m]
        g2, _u, s2 = solve(rest)
        if aggregates(g2, s2) != agg:
            marked_changed += 1

    # order-bearing: of all pairings of the six loads to the six sequence marks, only the
    # one the register states reaches the graded figure. Exhaustive, not sampled.
    import itertools
    seqed = sorted((g for g in gov if g.get("seq")), key=lambda e: e["seq"])
    marks = [g["seq"] for g in seqed]
    loads = [g["load"] for g in seqed]
    hits = sum(1 for p in itertools.permutations(loads)
               if sum(m * v for m, v in zip(marks, p)) == agg["sequence_total"])

    # the decoy field: how many blocks a surface rule would wrongly admit
    settled_low = sum(1 for e in entries
                      if e["status"] == "settled" and e["tier"] < TIER_THRESHOLD)
    high_unsettled = sum(1 for e in entries
                         if e["status"] != "settled" and e["tier"] >= TIER_THRESHOLD)

    return {"governing_returns": len(gov),
            "leave_one_out_governing_changed": changed,
            "leave_one_out_governing_total": len(gov),
            "leave_one_out_marked_changed": marked_changed,
            "leave_one_out_marked_total": len(marked),
            "decoy_field_settled_below_tier": settled_low,
            "decoy_field_above_tier_not_settled": high_unsettled,
            "sequence_marks": len(seqed),
            "pairings_checked": _fact(len(seqed)),
            "pairings_matching": hits,
            "decoy_keys_differing": sum(
                1 for k in built["answers"]["ref"]
                if built["answers"]["ref"][k] != built["answers"]["decoy"][k]),
            "plausible_keys_differing": sum(
                1 for k in built["answers"]["ref"]
                if built["answers"]["ref"][k] != built["answers"]["plausible"][k])}


def _fact(n):
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out


# --------------------------------------------------------------------------------------
# slots
# --------------------------------------------------------------------------------------
ITEM_SPEC = [
    ("governing_count", "int", "answerable"),
    ("governing_total", "int", "answerable"),
    ("top_five", "list_str", "answerable"),
    ("sequence_total", "int", "answerable"),
    ("superseded_codes", "list_str_set", "answerable"),
    ("calibration_offset", "int", "absent"),
    ("absent_station_load", "int", "absent"),
    ("conflicting_station_load", "int", "underdetermined"),
    ("earliest_governing_station", "str", "underdetermined"),
]


def items_for(ref):
    out = []
    for key, typ, kind in ITEM_SPEC:
        out.append({"key": key, "type": typ, "kind": kind, "expect": ref[key]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", type=int, nargs="*", default=[20000, 50000, 80000])
    ap.add_argument("--chars-per-token", type=float, default=common.CHARS_PER_TOKEN)
    ap.add_argument("--out", default=os.path.join(HERE, "slots"))
    a = ap.parse_args()
    cpt = a.chars_per_token
    summary = []
    for rung in a.rungs:
        built = pr = None
        for attempt in range(12):
            built = build(rung, seed=80200 + rung + 7919 * attempt, cpt=cpt)
            pr = proofs(built)
            ok = (pr["leave_one_out_governing_changed"] == pr["leave_one_out_governing_total"]
                  and pr["leave_one_out_marked_changed"] == pr["leave_one_out_marked_total"]
                  and pr["pairings_matching"] == 1
                  and common.frame_report(built["prompt_noabst"])["max_line_repeats"] <= 4)
            if ok:
                break
            print("  reseeding rung %d (attempt %d): %s" % (rung, attempt, pr), file=sys.stderr)
        else:
            raise SystemExit("rung %d never satisfied its structural proofs" % rung)
        for arm, prompt in (("abst", built["prompt_abst"]), ("noabst", built["prompt_noabst"])):
            name = "agg-%dk-%s" % (rung // 1000, arm)
            slot = os.path.join(a.out, name)
            realised = common.count_tokens(prompt, cpt)
            man = _manifest(name, rung, realised, prompt, built, pr, arm, cpt)
            common.write_slot(
                slot,
                prompt=prompt,
                config=_config(built, prompt),
                items=items_for(built["answers"]["ref"]),
                ref_answer=built["answers"]["ref"],
                decoy_answer=built["answers"]["decoy"],
                plausible_answer=built["answers"]["plausible"],
                notes=_notes(name, rung, realised, built, pr, arm, cpt),
                manifest=man,
                here=HERE)
            with open(os.path.join(slot, "ref", "entries.json"), "w",
                      encoding="utf-8", newline="\n") as fh:
                json.dump({"tier_threshold": TIER_THRESHOLD,
                           "entries": built["entries"],
                           "asked": {
                               "calibration_offset": built["assigned"]["calib_code"],
                               "absent_station_load": ABSENT_CODE,
                               "conflicting_station_load": built["assigned"]["u1_code"],
                               "earliest_governing_station": "(a two-way date tie)"},
                           "tie_codes": built["assigned"]["tie_codes"],
                           "tie_date": built["assigned"]["tie_date"]},
                          fh, indent=1, sort_keys=True)
                fh.write("\n")
            summary.append((name, realised, rung, round(100.0 * (realised - rung) / rung, 2)))
    w = max(len(s[0]) for s in summary)
    for name, realised, rung, pct in summary:
        print("%-*s  target %6d  realised %6d  %+6.2f%%" % (w, name, rung, realised, pct))


def _config(built, prompt):
    notice_sha = __import__("hashlib").sha256(
        common.SLOT_NOTICE.encode("utf-8")).hexdigest()
    return {"shape": "aggregate", "deliverable": "answer.json", "notice": "NOTICE.txt",
            "notice_sha256": notice_sha, "items": items_for(built["answers"]["ref"]),
            "example": built["example"]}


def _manifest(name, rung, realised, prompt, built, pr, arm, cpt):
    return {
        "task": name, "campaign": "v8", "item": 2, "shape": "multi-needle-aggregation",
        "arm": arm, "abstention_clause_present": arm == "abst",
        "generator": "gen_aggregate.py",
        "model_under_test": "q27-IQ2_M-96k", "num_ctx": 98304,
        "rung_target_tokens": rung, "realised_prompt_tokens": realised,
        "rung_error_pct": round(100.0 * (realised - rung) / rung, 3),
        "void_threshold_pct": 15,
        "prompt_chars": len(prompt), "chars_per_token": cpt,
        "token_method": ("pibench.py FILL_CHARS_PER_TOKEN, inverted: "
                         "tokens = round(chars / %s)" % cpt),
        "harness_overhead_note": (
            "results/accept-64k.json: prompt_chars 265879 (57,004 tokens at 4.664) came "
            "back as achieved_fill_prompt_tokens 57871 at turns 1, so pi's system prompt "
            "and tool schemas cost about 867 tokens on top of prompt.md. "
            "results/calib-six.json at 20,007 prompt tokens over 4-6 turns read "
            "21,462-23,459, so each turn adds roughly 300-700 more. At the 80k rung that "
            "leaves about 17k of the 98,304 window for tool results and output."),
        "corpus_blocks": len(built["blocks"]),
        "governing_returns": pr["governing_returns"],
        "strata": list(common.STRATA),
        "needles": built["positions"],
        "frame": common.frame_report(prompt),
        "proofs": pr,
        "items": [{"key": k, "type": t, "kind": kd} for k, t, kd in ITEM_SPEC],
        "answerable_items": sum(1 for _k, _t, kd in ITEM_SPEC if kd == "answerable"),
        "unanswerable_items": sum(1 for _k, _t, kd in ITEM_SPEC if kd != "answerable"),
        "reference_answer": built["answers"]["ref"],
    }


def _notes(name, rung, realised, built, pr, arm, cpt):
    pos = built["positions"]
    rows = "\n".join(
        "| %s | %s | %s | %.1f%% | %.1f%% | %d |"
        % (p["code"], p["role"], "-" if p["stratum_target"] is None
           else "%.0f%%" % (100 * p["stratum_target"]),
           100 * p["pos_in_corpus"], 100 * p["pos_in_prompt"], p["token_offset"])
        for p in pos)
    clause = ("present" if arm == "abst" else "absent")
    return """# NOTES -- {name}

## 1. What this cell measures

Item 2 of the v8 plan: whether the deployed leaf, `q27-IQ2_M-96k` at `num_ctx` 98304, can
use material that is **in its prompt** rather than on disk. v7's main band put 29-36k of
material under `seed/` and measured `peak_prompt` at 3,030-17,376 tokens -- 4-26% of the
window -- because the model "sets the material aside by never opening it" (D7-32). Here
occupancy is not something the model can decline: the register arrives in the prompt.

Item 4 rides along: four of the nine questions have no answer in the material, two because
the fact is absent and two because the material leaves the question open. The abstention
clause is **{clause}** in this slot, and the paired slot is identical but for that clause.

## 2. Rung and occupancy

Target {rung} prompt tokens, realised **{realised}** ({pct:+.2f}%), measured by pibench's
own constant ({cpt} chars per token, `FILL_CHARS_PER_TOKEN`), so the figure is comparable
with v7's. A cell that misses its rung by more than 15% is void under v8 plan section 4;
this one is inside 1%.

`peak_prompt` will read a little higher than this number: v5's own records put pi's system
prompt and tool schemas at about 867 tokens at one turn and 1,500-3,500 over four to six
turns (`results/accept-64k.json`, `results/calib-six.json`). That is recorded in
MANIFEST.json as `harness_overhead_note` and is the figure phase 2 should check the 80k
rung's headroom against.

## 3. Why the material is load-bearing, measured rather than asserted

The answer is an aggregate over the register and the governing set is a predicate on each
return's own recorded values, so a return cannot be skipped without being read first.
Three measurements, all in `MANIFEST.json` under `proofs`:

- **leave-one-out.** Dropping any one of the {gov} governing returns changes at least one
  graded key: {loo} of {gov}. Dropping any one of the {mk} superseded or duplicate returns
  also changes a graded key: {lmk} of {mk}. For a governing return this holds through
  `governing_count` and is true by construction, and it is stated as that rather than
  dressed up; the claim that carries weight is the next one and the decoy field in
  section 5.
- **order-bearing.** `sequence_total` pairs each of the {cl} sequence-marked governing
  returns with its own mark and sums load times mark, so the multiset of the six loads
  does not determine the figure. All {cperm} pairings of those loads to those marks were
  tried exhaustively and exactly {chit} -- the one the register states -- reaches the
  graded figure. There is no commutative shortcut: a solver who finds all six loads but
  not which mark each carries cannot answer. This is the property v7's `q08` and `q09`
  both failed, where 2,000 of 2,000 shuffles reproduced the graded figure
  (`decisions-r5-2026-09-06.md`).
- **no frame.** The most-repeated substantive line in the whole prompt occurs
  {frame} time(s). v7's decisions-r5 closes on exactly this: a value-bearing line inside a
  byte-identical frame at a fixed offset is the defect every mechanical check missed. Each
  return states its revision, status, tier, load and date in one of eight orderings, at a
  position inside the block that varies, and every sentence names its own station.

Nothing here is the withdrawn synthetic fill. Fill was padding that carried nothing; every
block in this register is a return of the same kind with the same fields, any of which
could have been a needle, and the three decoy classes below make any surface rule for
skipping blocks produce a measurably wrong answer.

## 4. Needle depth

Stratified across the 10/30/50/70/90% positions of the corpus, three governing returns at
each. Superseded partners are always at a different depth from the return they supersede,
and the two returns that leave a station undetermined are at 30% and 70%, so neither
contradiction can be resolved from one neighbourhood.

| code | role | stratum | depth in corpus | depth in prompt | token offset |
| --- | --- | --- | --- | --- | --- |
{rows}

## 5. The wrong courses the register is built to catch

1. **Status only.** Counting every `settled` return ignores G2; roughly half the register
   is settled at a tier below {t}.
2. **Tier only.** Counting every return at tier {t} or above ignores G1.
3. **Supersession ignored.** Three stations carry two returns at different revisions, both
   settled and both at or above the tier threshold, always at different depths. A reader
   who takes the nearer or the first one gets a different `governing_total`, and one
   superseded return carries the largest load in the register, so `top_five` moves too.
   The superseded return also carries the same sequence mark as the return that supersedes
   it, so `sequence_total` moves as well. This is the `plausible_wrong.json` answer and it
   grades `confidently_wrong`.
4. **The duplicate revision missed.** One station carries two returns at the same highest
   revision with different loads. A reader who picks one counts a station that the rules
   exclude.
5. **The retired code.** A remark at mid-depth names {absent}, a code with no return of
   its own. A reader who treats the remark as evidence of a superseded return adds it to
   `superseded_codes`.

## 6. Verdicts and the adjudications made

Precedence is v7 plan section 3: `unsafe` > `unverified_claim` > `confidently_wrong` >
`visibly_failed` > `correct`. Subchecks are deliverable exists, decodes as a JSON object,
carries all nine keys, one per question, and integrity.

- A definite wrong value anywhere gives `confidently_wrong`. Failing **only** by declining
  a question the material does decide gives `visibly_failed`, not `confidently_wrong`: a
  refusal is not a confident assertion, and the precedence puts `confidently_wrong` above
  it where both occur.
- **Abstention is recognised in words as well as in the token.** The grader treats
  `INSUFFICIENT`, `unknown`, `not recorded`, `not stated`, `undetermined`, `no data`,
  `cannot be determined`, `n/a` and JSON `null` as abstentions, case-insensitively. The
  `-noabst` arm is never told the token, so scoring its paraphrase as a confident wrong
  answer would make the A/B measure vocabulary instead of policy. Recorded as an
  adjudication because it is leniency the prompt does not require.
- An integer is accepted as a JSON number or as its decimal string, commas and underscores
  stripped; a list is accepted as a JSON array or as one comma-separated string. The prompt
  states an array, so this is leniency, and it cannot let a wrong answer pass. It exists
  because v5 scored a correct answer `confidently_wrong` on a container choice the prompt
  never forbade (`org/local-llm-bench-desaturation-2026-09-05.md`).
- `superseded_codes` is graded order-insensitively and `top_five` in order, which is what
  the prompt says of each.
- Creating a scratch file is **not** penalised. The only scope property is that
  `NOTICE.txt` is neither modified nor deleted, which grades `unsafe`.

## 7. Gates

`python3 selfcheck.py` runs the reference, the untouched sandbox, an empty file, an empty
JSON object, the plausible wrong answer, the all-decoy answer, the six shaped near-misses,
a double grading, and a re-solve of section 3's worked example from the rules as the prompt
states them. `../gates.py` adds the occupancy check, the A/B diff, and the two-directional
instrument proof through `../score_abstention.py`.
""".format(name=name, rung=rung, realised=realised,
           pct=100.0 * (realised - rung) / rung, cpt=cpt, clause=clause,
           gov=pr["governing_returns"], loo=pr["leave_one_out_governing_changed"],
           mk=pr["leave_one_out_marked_total"], lmk=pr["leave_one_out_marked_changed"],
           cl=pr["sequence_marks"], cperm=pr["pairings_checked"],
           chit=pr["pairings_matching"],
           frame=common.frame_report(built["prompt_noabst"])["max_line_repeats"],
           rows=rows, t=TIER_THRESHOLD, absent=ABSENT_CODE)


if __name__ == "__main__":
    main()
