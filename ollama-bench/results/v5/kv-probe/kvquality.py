"""T2 (v5 rerun): does KV cache quantisation cost long-context recall at 64k?

Runs llama-server directly (Ollama's own vendored build), one server and one model at a
time. Asymmetric K/V is removed from this plan -- Ollama cannot express it and the direct
runner measured a catastrophic fused-flash-attention fallback -- so K != V is rejected in
argument validation.

The probe is a fixed-seed corpus of ~1200 look-alike records with 32 two-record needles.
Each needle names TWO distinct records and asks for FOUR independently scorable fields
(checksum and region from record A, shard and token_budget from record B), so a cell
yields 128 independently scored fields plus an all-four-fields-per-needle count. Records
adjacent to a needle target, and records sharing its name prefix, carry deliberate
near-miss values; the grader rejects them by exact per-field comparison rather than by
searching the response for any six-character string.

Scoring is a pure function (answer text + needle -> per-field scores) shared by the live
run and the no-GPU fixture.

  offline grader fixture:  python3 kvquality.py --selftest-grader
  corpus smoke check:      python3 kvquality.py --corpus-info
  saturation stop rule:    python3 kvquality.py --saturation-check <cell.json>
  live cell:               python kvquality.py --model <blob> --ctx 65536 \
                               --records 1200 --needles 32 --configs q8_0:q8_0 \
                               --out ./kv-64k-<model>-<cache>.json
"""
import argparse, csv, hashlib, json, os, random, re, socket, subprocess, sys, time
import urllib.request, urllib.error

LIBDIR = os.path.expanduser("~/AppData/Local/Programs/Ollama/lib/ollama")
SERVER = os.path.join(LIBDIR, "llama-server.exe")
# Ollama keeps the CUDA backend in a subdirectory and puts it on the library path
# itself when it launches the runner. Launched by hand the loader finds only the CPU
# backends beside the exe and prints "no usable GPU found", silently ignoring -ngl.
CUDA_DIR = os.path.join(LIBDIR, "cuda_v13")
DEFAULT_PORT_BASE = 18080

# Declared before the run, per the plan's saturation stop rule. Do not adjust after
# seeing a score.
SATURATION_FIELD_PCT = 98.0
SATURATION_ALL_FIELDS_PCT = 90.0


def base_url(port):
    return f"http://127.0.0.1:{port}"


def server_env():
    e = dict(os.environ)
    e["PATH"] = CUDA_DIR + os.pathsep + LIBDIR + os.pathsep + e.get("PATH", "")
    # GGML_BACKEND_PATH names the backend *library*, not its directory: pointed at a
    # directory the loader reports "failed to load <dir>" and falls through to CPU.
    e["GGML_BACKEND_PATH"] = os.path.join(CUDA_DIR, "ggml-cuda.dll")
    return e


# ---------------------------------------------------------------------------
# corpus
# ---------------------------------------------------------------------------

REGIONS = ["eu-west-3", "us-east-1", "ap-south-2", "sa-east-1", "af-north-1", "me-central-1"]
WORDS_A = ["harrow", "colden", "brightmoor", "tarnwick", "elderfell", "graystone", "windhollow",
           "ashcombe", "ravensmere", "thornbury", "silverdale", "marlowe", "kestrelby", "downholt",
           "fenwick", "oakmere", "starling", "vaulterra", "quillon", "bramblewood"]
WORDS_B = ["fen", "vale", "reach", "hollow", "cross", "gate", "moor", "ridge", "combe", "hurst"]
HEX = "0123456789ABCDEF"

CORPUS_SEED = 20260903
DEFAULT_RECORDS = 1200
DEFAULT_NEEDLES = 32
FIELDS_PER_NEEDLE = 4
FIELD_KEYS = ("A_checksum", "A_region", "B_shard", "B_token_budget")


def _render(rec):
    return (f"RECORD {rec['index']:04d}: node \"{rec['node']}\" region={rec['region']} "
            f"shard={rec['shard']} checksum={rec['checksum']} "
            f"token_budget={rec['token_budget']} status={rec['status']}")


def _mutate_checksum(cs, rng):
    i = rng.randrange(len(cs))
    return cs[:i] + rng.choice([c for c in HEX if c != cs[i]]) + cs[i + 1:]


def _near_miss_values(target, rng, offset):
    """Values that differ from the target by one character or one digit."""
    return {"region": rng.choice([r for r in REGIONS if r != target["region"]]),
            "shard": max(1, target["shard"] + offset),
            "checksum": _mutate_checksum(target["checksum"], rng),
            "token_budget": max(1, target["token_budget"] + 7 * offset)}


def _bucket(depth):
    return "early" if depth < 1 / 3 else ("middle" if depth < 2 / 3 else "late")


def build_corpus(n_records=DEFAULT_RECORDS, n_needles=DEFAULT_NEEDLES, seed=CORPUS_SEED):
    """Frozen look-alike corpus plus two-record / four-field needles.

    Everything is drawn from one seeded Random in a fixed order, so all four cells see a
    byte-identical corpus and a byte-identical needle list.
    """
    if n_needles < 2:
        raise ValueError("need at least 2 needles")
    rng = random.Random(seed)
    n_suffix = -(-n_records // (len(WORDS_A) * len(WORDS_B)))
    names = [f"{a}-{b}-{n}" for n in range(1, n_suffix + 1)
             for a in WORDS_A for b in WORDS_B][:n_records]
    if len(names) < n_records:
        raise ValueError("name space too small for the requested record count")
    rng.shuffle(names)

    recs = []
    for i, nm in enumerate(names):
        recs.append({"index": i, "node": nm,
                     "region": rng.choice(REGIONS),
                     "shard": rng.randrange(1, 512),
                     "checksum": "".join(rng.choice(HEX) for _ in range(6)),
                     "token_budget": rng.randrange(1000, 99999),
                     "status": "converged"})

    by_prefix = {}
    for r in recs:
        by_prefix.setdefault(r["node"].rsplit("-", 1)[0], []).append(r["index"])

    # Needle A records spread from ~1% to ~99% depth; each needle's B record is a
    # deliberate short join a fixed distance away, so answering needs two lookups.
    depths = [0.01 + 0.98 * i / (n_needles - 1) for i in range(n_needles)]
    pairs = []
    for i, d in enumerate(depths):
        ia = min(n_records - 1, max(0, int(round(d * (n_records - 1)))))
        delta = 13 + (i % 4) * 3
        ib = ia + delta if ia + delta <= n_records - 3 else ia - delta
        if not 0 <= ib < n_records:
            raise ValueError("cannot place record B for needle %d" % i)
        pairs.append((ia, ib))

    targets = [x for p in pairs for x in p]
    if len(set(targets)) != len(targets):
        raise ValueError("needle target indices collide")
    srt = sorted(targets)
    if any(srt[k + 1] - srt[k] < 3 for k in range(len(srt) - 1)):
        raise ValueError("needle target indices are too close for adjacency decoys")

    reserved = set(targets)
    for t in targets:
        reserved.update((t - 1, t + 1))

    # Adjacent-index near-misses: the records immediately before and after every needle
    # target are rewritten to look almost exactly like it.
    adjacent = {}
    for t in targets:
        adj = []
        for off in (-1, 1):
            j = t + off
            if not 0 <= j < n_records:
                continue
            nm = _near_miss_values(recs[t], rng, off)
            recs[j].update(nm)
            adj.append(j)
        adjacent[t] = adj

    # Same-prefix near-misses: one sibling sharing the "<word>-<word>" prefix is rewritten
    # the same way. All siblings count as decoys for the grader either way.
    used_prefix_decoy = set()
    prefix_decoy = {}
    for t in targets:
        pfx = recs[t]["node"].rsplit("-", 1)[0]
        cands = [j for j in by_prefix[pfx]
                 if j != t and j not in reserved and j not in used_prefix_decoy]
        if not cands:
            raise ValueError("no free same-prefix sibling for record %d" % t)
        j = cands[rng.randrange(len(cands))]
        used_prefix_decoy.add(j)
        recs[j].update(_near_miss_values(recs[t], rng, 1))
        prefix_decoy[t] = j

    def decoys_for(t):
        pfx = recs[t]["node"].rsplit("-", 1)[0]
        idxs = sorted(set(adjacent[t]) | {j for j in by_prefix[pfx] if j != t})
        return [recs[j] for j in idxs]

    def near(vals, expected):
        out = []
        for v in vals:
            v = str(v)
            if v != expected and v not in out:
                out.append(v)
        return out

    needles = []
    for i, (ia, ib) in enumerate(pairs):
        a, b = recs[ia], recs[ib]
        da, db = decoys_for(ia), decoys_for(ib)
        depth = ia / (n_records - 1)
        spec = [("A_checksum", "checksum", "A", a, da, a["checksum"].upper()),
                ("A_region", "region", "A", a, da, a["region"].lower()),
                ("B_shard", "int", "B", b, db, str(b["shard"])),
                ("B_token_budget", "int", "B", b, db, str(b["token_budget"]))]
        fields = []
        for key, kind, which, rec, dec, expected in spec:
            src = "checksum" if kind == "checksum" else (
                "region" if kind == "region" else key.split("_", 1)[1])
            fields.append({"key": key, "kind": kind, "record": which,
                           "record_index": rec["index"], "node": rec["node"],
                           "expected": expected,
                           "near_miss": near([d[src] for d in dec], expected)})
        needles.append({"id": i, "depth": round(depth, 4), "bucket": _bucket(depth),
                        "a_index": ia, "b_index": ib,
                        "a_node": a["node"], "b_node": b["node"],
                        "a_prefix_decoy": recs[prefix_decoy[ia]]["node"],
                        "b_prefix_decoy": recs[prefix_decoy[ib]]["node"],
                        "fields": fields})

    corpus = "\n".join(_render(r) for r in recs)
    return corpus, needles, recs


def corpus_digest(corpus, needles):
    h = hashlib.sha256()
    h.update(corpus.encode())
    h.update(json.dumps([n["fields"] for n in needles], sort_keys=True).encode())
    return h.hexdigest()


def ask_order(needles):
    """Deterministic order that walks the depth buckets round-robin, so the first eight
    questions of a cell are a live calibration spread across early/middle/late rather
    than eight consecutive early needles."""
    groups = {b: [n["id"] for n in needles if n["bucket"] == b]
              for b in ("early", "middle", "late")}
    order, k = [], 0
    while len(order) < len(needles):
        for b in ("early", "middle", "late"):
            if k < len(groups[b]):
                order.append(groups[b][k])
        k += 1
    return order


def needle_question(corpus, needle, n_total):
    return (f"{corpus}\n\n"
            f"Question {needle['id'] + 1} of {n_total}.\n"
            f"Record A is the node named exactly \"{needle['a_node']}\".\n"
            f"Record B is the node named exactly \"{needle['b_node']}\".\n"
            f"DECOY WARNING: this dump contains look-alike records. "
            f"\"{needle['a_prefix_decoy']}\" and \"{needle['b_prefix_decoy']}\" share a name "
            f"prefix with A and B, and the records immediately before and after A and B "
            f"carry values that differ from theirs by a single character or a single digit. "
            f"None of those decoy records is an answer. Match the node name character for "
            f"character and read the fields off that one record.\n\n"
            "Reply with exactly these four lines and nothing else:\n"
            "A_checksum: <checksum field of record A>\n"
            "A_region: <region field of record A>\n"
            "B_shard: <shard field of record B>\n"
            "B_token_budget: <token_budget field of record B>")


# ---------------------------------------------------------------------------
# scoring: a pure function, shared by the offline fixture and the live run
# ---------------------------------------------------------------------------

_STRIP = " \t\"'`,.;:!?()[]{}*_"


def extract_field(text, key):
    """Return the raw value token for a labelled field, or None if the label is absent.

    Field boundaries are exact: the value is read from its own labelled line, never
    scavenged out of the surrounding prose.
    """
    m = re.search(r"^[^\S\n]*[-*>\s]*" + re.escape(key) + r"[^\S\n]*[:=][^\S\n]*(.*)$",
                  text or "", re.M | re.I)
    if not m:
        return None
    rest = m.group(1).strip()
    if not rest:
        return None
    return rest.split()[0]


def normalize_field(kind, token):
    """Exact-boundary normalisation. Returns None when the token is not a well-formed
    value of that kind, which scores as a miss rather than as a lucky substring hit."""
    if token is None:
        return None
    t = token.strip().strip(_STRIP)
    if "=" in t:
        t = t.rsplit("=", 1)[1]
    t = t.strip().strip(_STRIP)
    if kind == "checksum":
        t = t.upper()
        return t if re.fullmatch(r"[0-9A-F]{6}", t) else None
    if kind == "region":
        t = t.lower()
        return t if re.fullmatch(r"[a-z]{2}-[a-z]+-[0-9]+", t) else None
    if kind == "int":
        return t if re.fullmatch(r"[0-9]{1,7}", t) else None
    raise ValueError("unknown field kind %r" % kind)


def score_answer(answer_text, needle):
    """PURE: answer text + expected fields -> per-field scores. No I/O, no globals."""
    fields = []
    for f in needle["fields"]:
        raw = extract_field(answer_text, f["key"])
        got = normalize_field(f["kind"], raw)
        if raw is None:
            ok, reason = False, "missing"
        elif got is None:
            ok, reason = False, "unparsable"
        elif got == f["expected"]:
            ok, reason = True, "correct"
        elif got in f["near_miss"]:
            # A value copied off a near-miss record is rejected, not credited.
            ok, reason = False, "near_miss"
        else:
            ok, reason = False, "wrong"
        fields.append({"key": f["key"], "kind": f["kind"], "record": f["record"],
                       "record_index": f["record_index"], "expected": f["expected"],
                       "raw": raw, "got": got, "ok": ok, "reason": reason})
    points = sum(1 for x in fields if x["ok"])
    return {"needle": needle["id"], "depth": needle["depth"], "bucket": needle["bucket"],
            "a_index": needle["a_index"], "b_index": needle["b_index"],
            "a_node": needle["a_node"], "b_node": needle["b_node"],
            "fields": fields, "points": points, "possible": len(fields),
            "all_fields": points == len(fields) and len(fields) > 0}


def aggregate(scored):
    """PURE: per-needle scores -> points, percentage, all-fields, depth buckets."""
    possible = sum(s["possible"] for s in scored)
    points = sum(s["points"] for s in scored)
    all_fields = sum(1 for s in scored if s["all_fields"])
    buckets = {b: {"needles": 0, "fields": 0, "points": 0, "all_fields": 0, "pct": None,
                   "all_fields_pct": None} for b in ("early", "middle", "late")}
    reasons, by_key = {}, {}
    for s in scored:
        b = buckets[s["bucket"]]
        b["needles"] += 1
        b["fields"] += s["possible"]
        b["points"] += s["points"]
        b["all_fields"] += 1 if s["all_fields"] else 0
        for f in s["fields"]:
            reasons[f["reason"]] = reasons.get(f["reason"], 0) + 1
            k = by_key.setdefault(f["key"], {"points": 0, "fields": 0})
            k["fields"] += 1
            k["points"] += 1 if f["ok"] else 0
    for b in buckets.values():
        if b["fields"]:
            b["pct"] = round(100.0 * b["points"] / b["fields"], 3)
        if b["needles"]:
            b["all_fields_pct"] = round(100.0 * b["all_fields"] / b["needles"], 3)
    for k in by_key.values():
        k["pct"] = round(100.0 * k["points"] / k["fields"], 3) if k["fields"] else None
    return {"needles": len(scored), "fields": possible, "points": points,
            "pct": round(100.0 * points / possible, 3) if possible else None,
            "all_fields": all_fields,
            "all_fields_pct": round(100.0 * all_fields / len(scored), 3) if scored else None,
            "buckets": buckets, "reasons": reasons, "by_field": by_key}


def saturation_verdict(agg):
    """The plan's stop rule, declared before the run: a first full cell at or above 98%
    of fields with all-four-fields success at or above 90% cannot separate q8_0 from
    q4_0, so the sweep stops there."""
    pct = agg.get("pct")
    afp = agg.get("all_fields_pct")
    sat = (pct is not None and afp is not None
           and pct >= SATURATION_FIELD_PCT and afp >= SATURATION_ALL_FIELDS_PCT)
    return {"saturated": bool(sat), "field_pct": pct, "all_fields_pct": afp,
            "threshold_field_pct": SATURATION_FIELD_PCT,
            "threshold_all_fields_pct": SATURATION_ALL_FIELDS_PCT,
            "rule": "stop the sweep if field pct >= 98 and all-four-fields pct >= 90"}


# ---------------------------------------------------------------------------
# offline grader fixture (no GPU, no server, no port, no model)
# ---------------------------------------------------------------------------

def synth_answer(needle, overrides=None, omit=()):
    overrides = overrides or {}
    lines = []
    for f in needle["fields"]:
        if f["key"] in omit:
            continue
        lines.append(f"{f['key']}: {overrides.get(f['key'], f['expected'])}")
    return "\n".join(lines)


def selftest_grader(n_records=DEFAULT_RECORDS, n_needles=DEFAULT_NEEDLES, seed=CORPUS_SEED):
    failures = []

    def check(cond, msg):
        print(("  PASS  " if cond else "  FAIL  ") + msg, flush=True)
        if not cond:
            failures.append(msg)

    corpus, needles, recs = build_corpus(n_records, n_needles, seed)
    corpus2, needles2, _ = build_corpus(n_records, n_needles, seed)
    expect_fields = n_needles * FIELDS_PER_NEEDLE

    print("=== grader fixture (offline, no GPU) ===", flush=True)
    check(corpus_digest(corpus, needles) == corpus_digest(corpus2, needles2),
          f"corpus is frozen: rebuild is byte-identical ({corpus_digest(corpus, needles)[:16]})")
    check(len(recs) == n_records, f"record count == {n_records} (got {len(recs)})")
    check(len(needles) == n_needles, f"needle count == {n_needles} (got {len(needles)})")
    check(all(len(n["fields"]) == FIELDS_PER_NEEDLE for n in needles),
          f"every needle has {FIELDS_PER_NEEDLE} fields")
    check(all(n["a_index"] != n["b_index"] for n in needles),
          "every needle names two distinct records")
    check(all(len(f["near_miss"]) > 0 for n in needles for f in n["fields"]),
          "every field carries at least one near-miss decoy value")
    depth_lo, depth_hi = needles[0]["depth"], needles[-1]["depth"]
    check(depth_lo <= 0.02 and depth_hi >= 0.98,
          f"needle depths span {depth_lo:.3f}..{depth_hi:.3f}")

    good = [score_answer(synth_answer(n), n) for n in needles]
    ag = aggregate(good)
    check(ag["fields"] == expect_fields, f"known-good field count == {expect_fields} (got {ag['fields']})")
    check(ag["needles"] == n_needles, f"known-good needle count == {n_needles} (got {ag['needles']})")
    check(ag["points"] == expect_fields, f"known-good scores {expect_fields}/{expect_fields} (got {ag['points']})")
    check(ag["pct"] == 100.0, f"known-good is 100% (got {ag['pct']})")
    check(ag["all_fields"] == n_needles,
          f"known-good all-four-fields == {n_needles} (got {ag['all_fields']})")
    check(sum(b["needles"] for b in ag["buckets"].values()) == n_needles,
          "depth buckets account for every needle")

    # Deliberately degraded set: one wrong field, one near-miss field, one missing field,
    # each in a different needle.
    i_wrong, i_near, i_missing = 3 % n_needles, 11 % n_needles, 19 % n_needles
    if len({i_wrong, i_near, i_missing}) != 3:
        i_wrong, i_near, i_missing = 0, 1, 2
    nw, nn, nm = needles[i_wrong], needles[i_near], needles[i_missing]
    wrong_f = nw["fields"][1]                       # A_region
    bad_region = next(r for r in REGIONS
                      if r != wrong_f["expected"] and r not in wrong_f["near_miss"])
    near_f = nn["fields"][0]                        # A_checksum, the six-character trap
    near_val = near_f["near_miss"][0]

    degraded = []
    for n in needles:
        if n["id"] == nw["id"]:
            degraded.append(score_answer(synth_answer(n, {"A_region": bad_region}), n))
        elif n["id"] == nn["id"]:
            degraded.append(score_answer(synth_answer(n, {"A_checksum": near_val}), n))
        elif n["id"] == nm["id"]:
            degraded.append(score_answer(synth_answer(n, omit=("B_token_budget",)), n))
        else:
            degraded.append(score_answer(synth_answer(n), n))
    dg = aggregate(degraded)
    check(dg["fields"] == expect_fields, f"degraded field count == {expect_fields} (got {dg['fields']})")
    check(dg["needles"] == n_needles, f"degraded needle count == {n_needles} (got {dg['needles']})")
    check(dg["pct"] < 100.0, f"degraded scores strictly under 100% (got {dg['pct']}%)")
    check(dg["points"] == expect_fields - 3,
          f"degraded scores {expect_fields - 3}/{expect_fields} (got {dg['points']})")
    check(dg["all_fields"] == n_needles - 3,
          f"degraded all-four-fields == {n_needles - 3} (got {dg['all_fields']})")
    check(dg["reasons"].get("wrong", 0) == 1, f"exactly one wrong field (got {dg['reasons'].get('wrong', 0)})")
    check(dg["reasons"].get("near_miss", 0) == 1,
          f"exactly one near-miss field rejected (got {dg['reasons'].get('near_miss', 0)})")
    check(dg["reasons"].get("missing", 0) == 1,
          f"exactly one missing field (got {dg['reasons'].get('missing', 0)})")
    check(degraded[i_near]["fields"][0]["ok"] is False,
          "a checksum copied from a near-miss record is rejected, not credited")

    # A response that merely contains the right six characters somewhere, without the
    # labelled field, must not score.
    stray = score_answer("the checksum is probably " + needles[0]["fields"][0]["expected"]
                         + " somewhere in the dump", needles[0])
    check(stray["points"] == 0, "an unlabelled six-character string scores 0")

    print(f"\nknown-good: {ag['points']}/{ag['fields']} fields ({ag['pct']}%), "
          f"all-four-fields {ag['all_fields']}/{ag['needles']}", flush=True)
    print(f"degraded:   {dg['points']}/{dg['fields']} fields ({dg['pct']}%), "
          f"all-four-fields {dg['all_fields']}/{dg['needles']} "
          f"reasons={json.dumps(dg['reasons'], sort_keys=True)}", flush=True)
    for b in ("early", "middle", "late"):
        s = dg["buckets"][b]
        print(f"  {b:<7} needles={s['needles']:<3} fields={s['fields']:<4} "
              f"points={s['points']:<4} pct={s['pct']} all_fields={s['all_fields']}", flush=True)
    if failures:
        print(f"\nGRADER FIXTURE FAILED ({len(failures)} check(s)):", flush=True)
        for f in failures:
            print("  - " + f, flush=True)
        return 1
    print("\nGRADER FIXTURE OK: the scoring path can fail, and fails by exactly 3 fields "
          "and 3 needles on the degraded control.", flush=True)
    return 0


def corpus_info(n_records, n_needles, seed):
    corpus, needles, recs = build_corpus(n_records, n_needles, seed)
    counts = {b: sum(1 for n in needles if n["bucket"] == b)
              for b in ("early", "middle", "late")}
    print(f"seed              {seed}")
    print(f"digest            {corpus_digest(corpus, needles)}")
    print(f"records           {len(recs)}")
    print(f"needles           {len(needles)}")
    print(f"fields per needle {FIELDS_PER_NEEDLE}")
    print(f"fields total      {len(needles) * FIELDS_PER_NEEDLE}")
    print(f"corpus chars      {len(corpus)}")
    print(f"depth range       {needles[0]['depth']} .. {needles[-1]['depth']}")
    print(f"depth buckets     early={counts['early']} middle={counts['middle']} "
          f"late={counts['late']}")
    print(f"ask order (first 8, live calibration spread) {ask_order(needles)[:8]}")
    nm = [len(f["near_miss"]) for n in needles for f in n["fields"]]
    print(f"near-miss values per field  min={min(nm)} max={max(nm)}")
    print("\nsample record   " + _render(recs[needles[0]['a_index']]))
    print("adjacent decoy  " + _render(recs[needles[0]['a_index'] - 1]))
    return 0


# ---------------------------------------------------------------------------
# server lifecycle
# ---------------------------------------------------------------------------

def post(port, path, body, timeout=900):
    req = urllib.request.Request(base_url(port) + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def wait_health(proc, port, timeout=300):
    """Process-aware health poll. Health success is evidence the server came up; it is
    never a substitute for the post-termination drain."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        if proc.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(base_url(port) + "/health", timeout=5) as r:
                if json.load(r).get("status") == "ok":
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


def vram_mib(timeout=30):
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=timeout)
        return int(o.stdout.strip().splitlines()[0])
    except Exception:
        return -1


def _llama_server_pids(timeout=60):
    """Return llama-server.exe PIDs from tasklist; INFO's no-tasks line is not CSV."""
    try:
        o = subprocess.run(["tasklist", "/FI", "IMAGENAME eq llama-server.exe",
                            "/FO", "CSV", "/NH"],
                           capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        return None, str(e)
    pids = []
    try:
        for row in csv.reader(o.stdout.splitlines()):
            if len(row) >= 2 and row[0].lower() == "llama-server.exe":
                pids.append(int(row[1]))
    except (ValueError, csv.Error) as e:
        return None, str(e)
    return pids, None


def port_is_free(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # SO_REUSEADDR would let this bind test lie about an in-use Windows port.
            sock.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False


def reserve_port(base, used, span=200):
    """Give each launch a unique port and verify it is unbound before it is used."""
    for p in range(base, base + span):
        if p in used:
            continue
        if port_is_free(p):
            used.add(p)
            return p
    raise RuntimeError(f"no free port in {base}..{base + span - 1}")


def cleanup_barrier(port, proc=None, *, reason="", idle_ceiling=4000, timeout=240):
    """The single cleanup routine.

    Terminates the whole server process tree, waits for the parent AND the children to
    exit, waits for the launch port to be free, and then requires three CONSECUTIVE
    quiescent samples -- each one being a VRAM reading at or under the idle ceiling with
    no unexpected llama-server process present. Nothing launches until this returns ok.
    """
    started = time.monotonic()
    deadline = started + timeout
    result = {"ok": False, "reason": "", "waited_s": 0.0, "port": port,
              "vram_samples": [], "proc_samples": [], "port_free": False,
              "killed_pids": [], "tree_drained": False, "stray_pids_remaining": []}
    print(f"  [cleanup] start ok=pending waited_s=0.0 port={port} "
          f"reason={reason or 'unspecified'}", flush=True)

    def finish(ok, why=""):
        result["ok"] = ok
        result["reason"] = "" if ok else why
        result["waited_s"] = round(time.monotonic() - started, 1)
        print(f"  [cleanup] finish ok={result['ok']} waited_s={result['waited_s']} "
              f"reason={result['reason'] or 'none'}", flush=True)
        return result

    def remaining():
        return max(0.0, deadline - time.monotonic())

    def command_timeout(limit):
        return min(limit, max(0.001, remaining()))

    try:
        if proc is not None:
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                proc.wait(timeout=min(5, max(0.001, remaining())))
            except (subprocess.TimeoutExpired, ValueError):
                if remaining() <= 0:
                    return finish(False, "timeout waiting for server process")
                try:
                    # /T takes the whole tree, not just the parent.
                    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                   capture_output=True, timeout=command_timeout(60))
                except Exception:
                    pass
            try:
                proc.wait(timeout=min(15, max(0.001, remaining())))
            except (subprocess.TimeoutExpired, ValueError):
                return finish(False, "server process did not exit")

        pids, tasklist_error = _llama_server_pids(timeout=command_timeout(60))
        if tasklist_error:
            return finish(False, f"could not enumerate llama-server.exe: {tasklist_error}")
        for pid in pids:
            if remaining() <= 0:
                return finish(False, "cleanup timeout")
            result["killed_pids"].append(pid)
            try:
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                               capture_output=True, timeout=command_timeout(60))
            except Exception:
                pass

        # Wait for the children to actually go, not just for the kill to be issued.
        while remaining() > 0:
            pids, tasklist_error = _llama_server_pids(timeout=command_timeout(60))
            if tasklist_error:
                return finish(False, f"could not enumerate llama-server.exe: {tasklist_error}")
            if not pids:
                result["tree_drained"] = True
                break
            time.sleep(min(1, remaining()))
        if not result["tree_drained"]:
            return finish(False, "llama-server process tree did not exit")

        while remaining() > 0 and not port_is_free(port):
            time.sleep(min(0.2, remaining()))
        result["port_free"] = port_is_free(port)
        if not result["port_free"]:
            return finish(False, f"port {port} did not become free")

        # One low sample is not a drain: require three consecutive quiescent readings,
        # each with no unexpected llama-server process.
        consecutive = 0
        while consecutive < 3 and remaining() > 0:
            sample = vram_mib(timeout=command_timeout(30))
            pids, tasklist_error = _llama_server_pids(timeout=command_timeout(60))
            result["vram_samples"].append(sample)
            result["proc_samples"].append(pids if pids is not None
                                          else f"error:{tasklist_error}")
            quiet = (sample != -1 and sample <= idle_ceiling
                     and pids is not None and not pids)
            consecutive = consecutive + 1 if quiet else 0
            if consecutive < 3 and remaining() > 0:
                time.sleep(min(2, remaining()))
        if consecutive < 3:
            last = result["proc_samples"][-1] if result["proc_samples"] else None
            result["stray_pids_remaining"] = last if isinstance(last, list) else []
            return finish(False, "did not reach three consecutive quiescent samples "
                                 f"(vram<={idle_ceiling} MiB and no llama-server process); "
                                 f"vram={result['vram_samples'][-6:]} procs={last}")
        return finish(True)
    except BaseException as e:
        return finish(False, f"cleanup error: {e}")


def _log_tail(path, lines=40):
    try:
        with open(path, "rb") as fh:
            return b"\n".join(fh.read().splitlines()[-lines:]).decode(errors="replace")
    except Exception as e:
        return f"<could not read server log: {e}>"


def run_config(model, ctk, ctv, ctx, corpus, needles, logdir, port, idle_ceiling=4000,
               cleanup_timeout=240, cell_timeout=600, calibration_n=8):
    tag = f"{ctk}-{ctv}"
    logpath = os.path.join(logdir, f"server-{tag}-p{port}.log")
    pre_cleanup = cleanup_barrier(port, reason="before launch", idle_ceiling=idle_ceiling,
                                  timeout=cleanup_timeout)
    if not pre_cleanup["ok"]:
        return {"config": tag, "cache_type_k": ctk, "cache_type_v": ctv, "ctx": ctx,
                "port": port, "stopped": True, "partial": True,
                "reason": f"cleanup barrier failed before launch: {pre_cleanup['reason']}",
                "error": f"cleanup barrier failed before launch: {pre_cleanup['reason']}",
                "cleanup": pre_cleanup}
    if not port_is_free(port):
        return {"config": tag, "cache_type_k": ctk, "cache_type_v": ctv, "ctx": ctx,
                "port": port, "stopped": True, "partial": True,
                "reason": f"port {port} is bound immediately before launch",
                "error": f"port {port} is bound immediately before launch",
                "cleanup": pre_cleanup}

    logf = open(logpath, "wb")
    cmd = [SERVER, "--model", model, "--port", str(port), "--host", "127.0.0.1",
           "--no-webui", "--offline", "-c", str(ctx), "-np", "1",
           "-ngl", "99", "--flash-attn", "on",
           "--cache-type-k", ctk, "--cache-type-v", ctv,
           "-b", "512", "-ub", "512", "--no-warmup"]
    print(f"\n### {tag}  (ctx {ctx}, port {port})", flush=True)
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, env=server_env())
    try:
        healthy = wait_health(proc, port)
    except BaseException as e:
        healthy = False
        health_error = str(e)
    else:
        health_error = ""
    if not healthy:
        # Kill and drain BEFORE recording the error, so the next cell cannot start on top
        # of a half-dead server or an undrained allocation.
        cleanup = cleanup_barrier(port, proc, reason="health failure",
                                  idle_ceiling=idle_ceiling, timeout=cleanup_timeout)
        logf.close()
        tail = _log_tail(logpath)
        error = "server did not become healthy"
        if health_error:
            error += f": {health_error}"
        return {"config": tag, "cache_type_k": ctk, "cache_type_v": ctv, "ctx": ctx,
                "port": port, "stopped": True, "partial": True, "reason": error,
                "error": error, "log_tail": tail, "log_path": logpath,
                "cleanup": cleanup}
    load_s = round(time.time() - t0, 1)
    vram_loaded = vram_mib()

    order = ask_order(needles)
    by_id = {n["id"]: n for n in needles}
    scored, raw_answers, peak = [], [], vram_loaded
    stopped_reason = ""
    sys_msg = ("You answer questions about a configuration dump. Reply with the four "
               "requested label: value lines only -- no explanation, no restating the "
               "question, no extra lines.")
    gen_toks = gen_time = prompt_toks = prompt_time = 0
    cold_prompt_s = warm_prompt_s = None
    t_cell = time.time()

    try:
        for pos, nid in enumerate(order):
            if cell_timeout and time.time() - t_cell > cell_timeout:
                stopped_reason = (f"cell safety cap of {cell_timeout}s reached after "
                                  f"{pos} of {len(order)} needles")
                print(f"  [stop] {stopped_reason}", flush=True)
                break
            f = by_id[nid]
            q = needle_question(corpus, f, len(needles))
            t_q = time.time()
            try:
                r = post(port, "/v1/chat/completions", {
                    "messages": [{"role": "system", "content": sys_msg},
                                 {"role": "user", "content": q}],
                    "temperature": 0, "top_k": 1, "seed": CORPUS_SEED,
                    "max_tokens": 96, "cache_prompt": True,
                    # this is a recall probe, not a reasoning one; without this the
                    # Qwen template spends the whole budget inside <think>
                    "chat_template_kwargs": {"enable_thinking": False},
                })
            except Exception as e:
                raw_answers.append({"needle": nid, "answer": None,
                                    "error": f"request failed: {e}",
                                    "wall_s": round(time.time() - t_q, 2)})
                s = score_answer("", f)
                s["reason"] = f"request failed: {e}"
                scored.append(s)
                continue
            txt = r["choices"][0]["message"]["content"]
            # strip any thinking block the template may emit
            txt = re.sub(r"<think>.*?</think>", "", txt, flags=re.S).strip()
            u = r.get("usage", {})
            tim = r.get("timings", {})
            gen_toks += tim.get("predicted_n", 0)
            gen_time += tim.get("predicted_ms", 0) / 1000
            prompt_toks += tim.get("prompt_n", 0)
            prompt_time += tim.get("prompt_ms", 0) / 1000
            if cold_prompt_s is None:
                cold_prompt_s = round(tim.get("prompt_ms", 0) / 1000, 3)
            elif warm_prompt_s is None:
                warm_prompt_s = round(tim.get("prompt_ms", 0) / 1000, 3)
            peak = max(peak, vram_mib())
            s = score_answer(txt, f)
            scored.append(s)
            raw_answers.append({"needle": nid, "depth": f["depth"], "bucket": f["bucket"],
                                "answer": txt, "prompt_tokens": u.get("prompt_tokens", -1),
                                "timings": tim, "wall_s": round(time.time() - t_q, 2)})
            marks = "".join("." if x["ok"] else "x" for x in s["fields"])
            print(f"  d={f['depth']:<6} {f['bucket']:<6} n{nid:<3} "
                  f"{s['points']}/4 [{marks}] "
                  f"{'ALL' if s['all_fields'] else '   '} "
                  f"{[x['got'] for x in s['fields']]}", flush=True)
    except BaseException as e:
        logf.close()
        cleanup = cleanup_barrier(port, proc, reason="question loop failure",
                                  idle_ceiling=idle_ceiling, timeout=cleanup_timeout)
        agg = aggregate(scored) if scored else None
        return {"config": tag, "cache_type_k": ctk, "cache_type_v": ctv, "ctx": ctx,
                "port": port, "stopped": True, "partial": True,
                "reason": f"question loop failed after {len(scored)} needles: {e}",
                "error": f"question loop failed: {e}",
                "load_s": load_s, "vram_loaded_mib": vram_loaded, "vram_peak_mib": peak,
                "score": agg, "per_needle": scored, "raw_answers": raw_answers,
                "log_path": logpath, "log_tail": _log_tail(logpath), "cleanup": cleanup}

    logf.close()
    cleanup = cleanup_barrier(port, proc, reason="normal completion",
                              idle_ceiling=idle_ceiling, timeout=cleanup_timeout)

    agg = aggregate(scored)
    calib = aggregate(scored[:calibration_n]) if scored[:calibration_n] else None
    partial = len(scored) < len(needles) or any(a.get("error") for a in raw_answers)
    reason = stopped_reason
    if not reason and partial:
        errs = [a["error"] for a in raw_answers if a.get("error")]
        reason = f"{len(errs)} of {len(needles)} needles failed: {errs[0]}" if errs else \
                 f"only {len(scored)} of {len(needles)} needles answered"
    if not reason and not cleanup["ok"]:
        reason = f"cleanup barrier failed after the cell: {cleanup['reason']}"
    return {"config": tag, "cache_type_k": ctk, "cache_type_v": ctv, "ctx": ctx,
            "port": port, "stopped": bool(stopped_reason), "partial": partial,
            "reason": reason or "complete",
            "load_s": load_s, "vram_loaded_mib": vram_loaded, "vram_peak_mib": peak,
            "gen_tok_s": round(gen_toks / gen_time, 1) if gen_time else None,
            "prompt_tok_s": round(prompt_toks / prompt_time, 1) if prompt_time else None,
            "cold_prompt_s": cold_prompt_s, "warm_prompt_s": warm_prompt_s,
            "gen_tokens": gen_toks, "gen_time_s": round(gen_time, 3),
            "prompt_tokens_total": prompt_toks, "prompt_time_s": round(prompt_time, 3),
            "prompt_tokens": raw_answers[0].get("prompt_tokens") if raw_answers else None,
            "score": agg, "calibration_first_n": calib,
            "saturation": saturation_verdict(agg),
            "per_needle": scored, "raw_answers": raw_answers,
            "log_path": logpath, "cleanup": cleanup}


def lifecycle_cycle(model, ctx, logdir, cycle, port, idle_ceiling, cleanup_timeout):
    logf = open(os.path.join(logdir, f"lifecycle-{cycle}.log"), "wb")
    cmd = [SERVER, "--model", model, "--port", str(port), "--host", "127.0.0.1",
           "--no-webui", "--offline", "-c", str(ctx), "-np", "1", "-ngl", "99",
           "--flash-attn", "on", "--cache-type-k", "f16", "--cache-type-v", "f16",
           "-b", "512", "-ub", "512", "--no-warmup"]
    proc = None
    t0 = time.time()
    healthy = False
    try:
        proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, env=server_env())
        try:
            healthy = wait_health(proc, port)
        except BaseException:
            healthy = False
    finally:
        health_s = round(time.time() - t0, 1) if proc is not None else None
        # Record what the card actually held WHILE THE SERVER WAS UP, before teardown.
        # Without this the artifact cannot distinguish "the drain branch waited for a real
        # multi-GB allocation to fall" from "VRAM was already under the ceiling and there was
        # nothing to drain" -- the post-teardown samples read the same idle baseline either
        # way, and a green result whose evidence does not cover its own claim is exactly the
        # failure mode this harness exists to avoid.
        resident_samples = []
        if healthy:
            for _ in range(3):
                resident_samples.append(vram_mib())
                time.sleep(1)
        cleanup = cleanup_barrier(port, proc, reason=f"lifecycle selftest cycle {cycle}",
                                  idle_ceiling=idle_ceiling, timeout=cleanup_timeout)
        logf.close()
    good = [v for v in resident_samples if v and v > 0]
    return {"launch_ok": proc is not None and healthy,
            "health_s": health_s, "port": port,
            "vram_resident_samples_mib": resident_samples,
            "vram_peak_while_healthy_mib": max(good) if good else None,
            "drain_observed": bool(good and max(good) > idle_ceiling),
            "cleanup": cleanup}


def check_saturation_file(path):
    try:
        with open(path) as fh:
            doc = json.load(fh)
    except Exception as e:
        print(f"saturation-check error: could not read {path}: {e}", file=sys.stderr)
        return 2
    runs = doc.get("runs") or []
    usable = [r for r in runs if r.get("score") and not r.get("partial")]
    if not usable:
        print("saturated=no")
        print(f"reason=no complete cell in {path}; "
              f"{len(runs)} run(s), none scored a full cell")
        return 0
    r = usable[0]
    v = r.get("saturation") or saturation_verdict(r["score"])
    print("saturated=" + ("yes" if v["saturated"] else "no"))
    print(f"config={r.get('config')} field_pct={v['field_pct']} "
          f"all_fields_pct={v['all_fields_pct']} "
          f"thresholds={v['threshold_field_pct']}/{v['threshold_all_fields_pct']}")
    if v["saturated"]:
        b = r["score"]["buckets"]
        print("saturated_at_depths=" + json.dumps(
            {k: {"pct": b[k]["pct"], "all_fields": b[k]["all_fields"],
                 "needles": b[k]["needles"]} for k in ("early", "middle", "late")}))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model")
    ap.add_argument("--ctx", type=int, default=65536)
    ap.add_argument("--records", type=int, default=DEFAULT_RECORDS)
    ap.add_argument("--needles", type=int, default=DEFAULT_NEEDLES)
    ap.add_argument("--seed", type=int, default=CORPUS_SEED)
    ap.add_argument("--configs", default="q8_0:q8_0")
    ap.add_argument("--out", default=None)
    ap.add_argument("--port-base", type=int, default=DEFAULT_PORT_BASE)
    ap.add_argument("--idle-vram-mib", type=int, default=4000)
    ap.add_argument("--cleanup-timeout", type=int, default=240)
    ap.add_argument("--cell-timeout", type=int, default=600,
                    help="per-cell safety cap in seconds; hitting it is a recorded result")
    ap.add_argument("--calibration-needles", type=int, default=8)
    ap.add_argument("--selftest-grader", action="store_true",
                    help="offline no-GPU grader fixture; exits nonzero if scoring cannot fail")
    ap.add_argument("--corpus-info", action="store_true",
                    help="offline corpus smoke check; builds the corpus and prints its shape")
    ap.add_argument("--saturation-check", metavar="RESULT_JSON",
                    help="apply the plan's saturation stop rule to a finished cell")
    ap.add_argument("--lifecycle-selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest_grader:
        sys.exit(selftest_grader(a.records, a.needles, a.seed))
    if a.corpus_info:
        sys.exit(corpus_info(a.records, a.needles, a.seed))
    if a.saturation_check:
        sys.exit(check_saturation_file(a.saturation_check))

    if not a.model:
        ap.error("--model is required for a live run")

    # Asymmetric K/V is removed from the plan: Ollama cannot express it, and the direct
    # runner measured 7.1 gen tok/s and 18.3 prompt tok/s for q8_0/q4_0 against 51.9 and
    # 1443.3 for q8_0/q8_0 at 16k. Reject it in argument validation.
    configs = []
    for spec in a.configs.split(","):
        spec = spec.strip()
        if not spec:
            continue
        if spec.count(":") != 1:
            ap.error(f"--configs entry {spec!r} must be of the form TYPE:TYPE")
        ctk, ctv = (x.strip() for x in spec.split(":"))
        if ctk != ctv:
            ap.error(
                f"asymmetric K/V is rejected: --configs entry {spec!r} has "
                f"cache-type-k={ctk} != cache-type-v={ctv}. Asymmetric cells were removed "
                "from the 2026-09-03 KV plan (Ollama cannot express them and the direct "
                "runner measured a catastrophic flash-attention fallback). Use symmetric "
                "cells only, e.g. q8_0:q8_0 or q4_0:q4_0.")
        configs.append((ctk, ctv))
    if not configs:
        ap.error("--configs is empty")

    logdir = os.path.dirname(os.path.abspath(a.out or "kv.json")) or "."
    os.makedirs(logdir, exist_ok=True)
    used_ports = set()

    if a.lifecycle_selftest:
        port = reserve_port(a.port_base, used_ports)
        pre_cleanup = cleanup_barrier(port, reason="lifecycle selftest pre",
                                      idle_ceiling=a.idle_vram_mib, timeout=a.cleanup_timeout)
        cycles = []
        if pre_cleanup["ok"]:
            for cycle in (1, 2):
                p = reserve_port(a.port_base, used_ports)
                cycles.append(lifecycle_cycle(a.model, a.ctx, logdir, cycle, p,
                                              a.idle_vram_mib, a.cleanup_timeout))
        verdict = {"lifecycle_selftest": True, "pre_cleanup": pre_cleanup,
                   "cycles": cycles,
                   "ok": pre_cleanup["ok"] and len(cycles) == 2 and
                   all(c["launch_ok"] and c["cleanup"]["ok"] for c in cycles),
                   # ok says the cycle completed; drain_branch_proven says the run actually
                   # exercised the branch that waits for a real allocation to fall. They are
                   # different claims and the artifact must carry both.
                   "drain_branch_proven": any(c.get("drain_observed") for c in cycles)}
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(verdict, fh, indent=1)
        print(json.dumps(verdict, indent=1))
        return

    corpus, needles, recs = build_corpus(a.records, a.needles, a.seed)
    digest = corpus_digest(corpus, needles)
    n_fields = len(needles) * FIELDS_PER_NEEDLE
    counts = {b: sum(1 for n in needles if n["bucket"] == b)
              for b in ("early", "middle", "late")}
    print(f"corpus {len(corpus)} chars, {len(recs)} records, {len(needles)} needles, "
          f"{n_fields} fields; buckets early={counts['early']} middle={counts['middle']} "
          f"late={counts['late']}; digest {digest[:16]}; idle VRAM {vram_mib()} MiB",
          flush=True)

    out = {"model": a.model, "ctx": a.ctx, "records": a.records, "needles": len(needles),
           "fields": n_fields, "seed": a.seed, "corpus_digest": digest,
           "corpus_chars": len(corpus), "depth_buckets": counts,
           "idle_vram_mib": vram_mib(),
           "saturation_rule": {"threshold_field_pct": SATURATION_FIELD_PCT,
                               "threshold_all_fields_pct": SATURATION_ALL_FIELDS_PCT},
           "runs": []}
    for ctk, ctv in configs:
        port = reserve_port(a.port_base, used_ports)
        out["runs"].append(run_config(a.model, ctk, ctv, a.ctx, corpus, needles, logdir,
                                      port, a.idle_vram_mib, a.cleanup_timeout,
                                      a.cell_timeout, a.calibration_needles))
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(out, fh, indent=1)

    print("\n=== summary ===")
    print(f"{'config':<14}{'fields':<12}{'pct':<8}{'all4':<9}{'early/mid/late':<22}"
          f"{'vram peak':<11}{'gen t/s':<10}{'prompt t/s':<12}reason")
    for r in out["runs"]:
        s = r.get("score")
        if not s:
            print(f"{r['config']:<14}{r.get('reason', r.get('error', 'no score'))}")
            continue
        b = s["buckets"]
        buck = f"{b['early']['pct']}/{b['middle']['pct']}/{b['late']['pct']}"
        print(f"{r['config']:<14}{str(s['points']) + '/' + str(s['fields']):<12}"
              f"{str(s['pct']):<8}"
              f"{str(s['all_fields']) + '/' + str(s['needles']):<9}{buck:<22}"
              f"{str(r['vram_peak_mib']):<11}{str(r['gen_tok_s']):<10}"
              f"{str(r['prompt_tok_s']):<12}{r['reason']}")
        v = r.get("saturation") or {}
        if v.get("saturated"):
            print(f"  SATURATED: {v['field_pct']}% of fields >= {v['threshold_field_pct']} "
                  f"and all-four-fields {v['all_fields_pct']}% >= "
                  f"{v['threshold_all_fields_pct']}. Per the plan's stop rule the sweep "
                  f"stops here and the remaining cells are not run.")


if __name__ == "__main__":
    main()
