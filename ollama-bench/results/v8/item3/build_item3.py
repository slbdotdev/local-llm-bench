#!/usr/bin/env python3
"""Build the six v8 item-3 slots: three task families at two occupancy rungs each.

Run from anywhere:  python3 build_item3.py [--audit]

Every slot lands in `slots/<name>/` in the v7 task layout (v7 plan section 2):

    prompt.md       the only thing the model under test sees
    seed/           the working directory, copied fresh per trial
    ref/            the reference answer; never copied into the sandbox
    test.py         the hidden grader: CONFIG + the body of grade_seeded.py
    selfcheck.py    every gate case of v8 plan section 4, run against test.py
    NOTES.md        failure mode, ground truth, thresholds, near-miss table
    MANIFEST.json   rung, measured material, provenance of every copied file

## Ground truth

Planted by **selection and by construction**, never by editing a real page:

  Use A   the material is copied verbatim. The claim set is the figures the material itself
          presents as measured about one named subject; the decoy set is figures the material
          itself labels derived, budgeted, estimated or unmeasured. Both sets are asserted
          present in the slot's own seed at build time, so neither can drift from the material.
  Use B   `authority/` is a real page, copied verbatim. `draft/handoff.md` is generated from it:
          K figures are mutated (the build asserts the mutated value appears nowhere in the
          authority, so a contradiction is a contradiction by construction) and L are restated
          with the authority's own value under the qualifier the authority gives it (the build
          asserts each appears in the authority, so a near-miss is not a contradiction by
          construction).
  Use C   `git/log.txt` is a snapshot of `git log --name-status` over a commit range of this
          repository, pinned by endpoint sha. Which commits touched the target path is read out
          of that same snapshot, so the answer key and the material cannot disagree.

Nothing is typed twice: every literal this file declares is checked against the bytes that land
in `seed/`, and the build fails rather than writing a slot whose key it could not verify.

## Material and secrets

Source material is read from `/home/slb/ansible-slb/org/*.md` (read-only to this build) and from
this repository's own `results/**/*.md`. The scan in `_redact` removes tailnet host addresses and
is the only modification made to any copied byte; every removal is recorded per file in
MANIFEST.json. No vault file, key or token value is copied: `secret_scan()` below runs over
every byte that lands in a seed and the build fails on a hit.
"""
import argparse
import hashlib
import json
import os
import pprint
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SLOTS = os.path.join(HERE, "slots")
ORG = "/home/slb/ansible-slb/org"
RESULTS = os.path.abspath(os.path.join(HERE, "..", ".."))            # ollama-bench/results
BENCH = os.path.abspath(os.path.join(HERE, "..", "..", ".."))        # ollama-bench
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))   # local-llm-bench

CHARS_PER_TOKEN = 4.664          # the suite's own constant, v7 plan section 1
RUNGS = {"r1": 12000, "r2": 40000}
RUNG_TOLERANCE = 0.15            # v8 plan section 4's own occupancy tolerance

sys.path.insert(0, HERE)
import grade_seeded  # noqa: E402

# Tailnet host addresses: not secrets, but fleet network state that has no business being
# duplicated into a second repository, and a stray 100.x literal would also pollute the
# hallucination token index. The two well-known Tailscale literals (100.100.100.100, the MagicDNS
# resolver, and 100.64.0.0, the CGNAT range itself) are public constants and are left alone.
_REDACT = [(re.compile(r"\b100\.87\.184\.105\b"), "100.x.x.x"),
           (re.compile(r"\b100\.65\.107\.25\b"), "100.x.x.x")]


def _redact(text):
    n = 0
    for rx, rep in _REDACT:
        text, k = rx.subn(rep, text)
        n += k
    return text, n


# --------------------------------------------------------------------------- use A specs

A_SUBJECT = ("the `q27-IQ2_M` quant of Qwen3.8-27B (any context rung of it) and the RTX 5080 "
             "card the desktop runs it on")

# Each claim: a figure the material states as a measured result. `any_of` is a list of
# alternatives; an alternative matches when every token in it appears on one line of the answer.
# Claims are matched generously (one distinctive literal) because under-matching a claim would
# fail a correct answer; penalties are matched precisely because under-matching one can only
# flatter a wrong answer.
A_CLAIMS = [
    {"key": "resident_96k", "any_of": [["13.27"]],
     "label": "13.27 GB resident, measured at 96k"},
    {"key": "gen_tps_96k", "any_of": [["41.9"]],
     "label": "41.9 generation tok/s at 96k"},
    {"key": "weights", "any_of": [["10.13"]],
     "label": "10.13 GiB of weights, the exact blob size read off the desktop"},
    {"key": "num_ctx", "any_of": [["98304"], ["98,304"]],
     "label": "num_ctx 98304, confirmed by /api/show"},
    {"key": "serial_wall", "any_of": [["10.07"]],
     "label": "10.07 s of wall for two concurrent requests served one after the other"},
    {"key": "aggregate_tps", "any_of": [["32.6"]],
     "label": "32.6 tok/s aggregate across the two serialized requests"},
    {"key": "pooled_pass", "any_of": [["0.898"]],
     "label": "pooled pass probability 0.898 over 98 v7 trials"},
    {"key": "cw_rate", "any_of": [["0.031"]],
     "label": "confidently-wrong rate 0.031"},
    {"key": "pooled_48k", "any_of": [["0.900"], ["0.9"]],
     "label": "pooled 0.900 at 48k in 30 trials"},
    {"key": "pooled_64k", "any_of": [["0.833"]],
     "label": "pooled 0.833 at 64k in 48 trials"},
]

# Each decoy: a figure the material itself presents as derived, budgeted or unmeasured. The
# multi-token alternatives are for literals that are not unique in the larger rung's corpus; the
# `--audit` mode prints every occurrence of every literal so the choice is evidence-based.
A_DECOYS = [
    {"key": "kv_per_1k_derived", "any_of": [["34.0"], ["34", "mib"], ["34", "kv"]],
     "label": "34.0 MiB per 1,024 tokens of KV, computed from the model's own metadata"},
    {"key": "recurrent_allowance", "any_of": [["150", "slot"], ["150", "recurrent"],
                                              ["150", "mb"]],
     "label": "about 150 MB per slot of recurrent state, a derived - not measured - allowance"},
    # Deliberately not ["1024", "mib"]: that also matched the line carrying the *other* decoy
    # ("34.0 MiB per 1,024 tokens"), which would charge one mistake twice and inflate the decoy
    # rate. Found by --audit.
    {"key": "kv_predicted_16", "any_of": [["1024", "predict"], ["1024", "difference"],
                                          ["1024", "sixteen"]],
     "label": "1,024 MiB, the sixteen-layer prediction, against 960 MiB measured"},
    {"key": "kv_predicted_17", "any_of": [["1088"]],
     "label": "1,088 MiB, the seventeen-layer prediction"},
    {"key": "kv_elements", "any_of": [["32768", "element"], ["32768", "per token"]],
     "label": "32,768 KV elements per token, arithmetic from the metadata"},
]

A_THRESH = {"recall_min": 0.75, "precision_min": 0.0, "penalty_max_rate": 0.0,
            "hallucination_max": 0, "hallucination_scale": 5}

A_SOURCES_R1 = [(ORG, "local-workhorse-plan-2026-09-06.md"),
                (ORG, "local-quants-2026-09-05.md"),
                (ORG, "local-ollama-route-2026-09-11.md")]
A_SOURCES_R2 = A_SOURCES_R1 + [(ORG, "local-llm-bench-desaturation-2026-09-05.md"),
                               (ORG, "cachy-headless-2026-09-09.md"),
                               (ORG, "cachy-1080ti-options-2026-09-08.md"),
                               (ORG, "models.md"),
                               (ORG, "README.md"),
                               (ORG, "pending.md"),
                               (ORG, "zai-flash-campaign-2026-09-06.md"),
                               (RESULTS, "v7/calibration-2026-09-06.md")]

# --------------------------------------------------------------------------- use B specs

# (key, label, authority value, draft value) for a contradiction; the draft value must appear
# nowhere in the authority. (key, label, value) for a near-miss; the value must appear in it.
B1_AUTHORITY = [(ORG, "local-workhorse-plan-2026-09-06.md")]
B1_CONTRA = [
    ("resident_96k", "IQ2_M resident at 96k", "13.27 GB", "13.92 GB"),
    ("gen_tps_96k", "IQ2_M generation rate at 96k", "41.9 tok/s", "37.4 tok/s"),
    ("weights", "IQ2_M weights, exact blob size", "10.13 GiB", "10.71 GiB"),
    ("cw_rate", "confidently-wrong rate over the v7 evidence", "0.031", "0.047"),
    ("pooled", "pooled pass probability over 98 v7 trials", "0.898", "0.871"),
    ("num_ctx", "num_ctx of the 96k tag", "98,304", "98,034"),
    ("kv_per_1k", "KV per 1,024 tokens at q8_0", "34.0 MiB", "36.5 MiB"),
]
B1_NEAR = [
    ("q2k_resident_64k", "Q2_K resident at its 64k rung", "13.07 GB"),
    ("q2k_tps_64k", "Q2_K generation rate at 64k", "45.1 tok/s"),
    ("mriq3m_load", "mrIQ3M resident at q8_0 and 64k on llama-server", "15,303 MiB"),
    ("fair_weather_gib", "the fair-weather resident line, in GiB", "14.2 GiB"),
    ("pooled_64k", "pooled pass probability in the 64k cell", "0.833"),
    ("mean_pass", "mean pass probability over the v7 evidence", "0.887"),
    ("q2k_48k_derived", "Q2_K at 48k, the figure the plan derives", "12.5 GB"),
]

# The plan says "a pair of pages". b1 is literally that: one real page and one draft. At the r2
# rung no single fleet page carries 40,000 tokens, so b2's record is two real pages and the pair
# *shape* - one draft against the record - is what carries over. Recorded in NOTES.md as a
# deviation rather than quietly.
B2_AUTHORITY = [(RESULTS, "v5/plan-2026-09-03.md"), (RESULTS, "v5/questions.md")]
B2_CONTRA = [
    ("haiku_overall", "haiku's overall mean SCORE on the v4 suite", "0.7052", "0.7520"),
    ("sonnet_overall", "sonnet's overall mean SCORE", "0.8834", "0.8384"),
    ("opus_overall", "opus's overall mean SCORE", "0.9398", "0.9498"),
    ("material_slots_haiku", "haiku on `material-slots`", "0.215", "0.251"),
    ("toggle_haiku", "haiku's mean on `toggle-default-on`", "0.029", "0.092"),
    ("texture_haiku", "haiku's mean on `texture-budget`", "0.817", "0.871"),
    ("fp8_out_tokens", "output tokens per run for the fp8 reference", "53,702", "52,703"),
    ("toggle_max_cost", "the worst single-run cost on `toggle-default-on`", "USD 14.60",
     "USD 16.40"),
]
B2_NEAR = [
    ("haiku_runner", "haiku's mean as the runner report gives it", "0.677"),
    ("sonnet_runner", "sonnet's mean as the runner report gives it", "0.939"),
    ("opus_runner", "opus and fable as the runner report gives them", "0.947"),
    ("material_slots_raw", "haiku on `material-slots` before the honesty penalty", "0.465"),
    ("haiku_measure", "haiku's `measure`-category mean", "0.8183"),
    ("toggle_prefix", "sonnet's pre-fix ceiling on `toggle-default-on`", "0.789"),
    ("haiku_build_earlier", "haiku's `build`-category mean as the earlier reading gives it",
     "0.423"),
    ("fp8_earlier_draft", "tool calls per run for the fp8 reference, earlier draft", "55.3"),
]
B_THRESH = {"recall_min": 0.75, "precision_min": 0.75, "penalty_max_rate": 0.25,
            "hallucination_max": 0, "hallucination_scale": 5}

# --------------------------------------------------------------------------- use C specs

C_TARGET = "ollama-bench/results/v7/authoring"
C1_RANGE = ("d42ca4ea731bb3e2a0df81f4c9ea9abb85530943",
            "58f6feea9c892b3895614b6847d11a1fec529b0e")
C2_RANGE = ("aac8e939056c437063d7c7ab5488c735d3705dd3",
            "4062e75c0e536e21d74fd27a89c5a235a021ba3c")
C_THRESH = {"recall_min": 0.75, "precision_min": 1.0, "penalty_max_rate": 0.0,
            "hallucination_max": 0, "hallucination_scale": 5}

SPECS = [
    {"name": "a1-summarise-r1", "family": "A", "rung": "r1", "sources": A_SOURCES_R1},
    {"name": "a2-summarise-r2", "family": "A", "rung": "r2", "sources": A_SOURCES_R2},
    {"name": "b1-contradiction-r1", "family": "B", "rung": "r1", "sources": B1_AUTHORITY,
     "contra": B1_CONTRA, "near": B1_NEAR,
     "draft_title": "Local workhorse handoff, draft"},
    {"name": "b2-contradiction-r2", "family": "B", "rung": "r2", "sources": B2_AUTHORITY,
     "contra": B2_CONTRA, "near": B2_NEAR,
     "draft_title": "v5 suite handoff, draft"},
    {"name": "c1-changelog-r1", "family": "C", "rung": "r1", "range": C1_RANGE},
    {"name": "c2-changelog-r2", "family": "C", "rung": "r2", "range": C2_RANGE},
]


# --------------------------------------------------------------------------- helpers

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def git(args):
    r = subprocess.run(["git", "-C", REPO] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def secret_scan(text, where):
    """Fail the build on anything secret-shaped. Names are fine; values are not."""
    pats = [("ansible-vault header", r"\$ANSIBLE_VAULT;"),
            ("openai-style key", r"\bsk-[A-Za-z0-9_\-]{20,}"),
            ("github token", r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}"),
            ("aws access key", r"\bAKIA[0-9A-Z]{16}\b"),
            ("private key block", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
            ("ssh public key blob", r"ssh-(?:rsa|ed25519) AAAA[0-9A-Za-z+/=]{20,}"),
            ("zai-style key", r"\b[0-9a-f]{32}\.[A-Za-z0-9]{16,}"),
            ("assigned secret", r"(?i)\b(?:api[_-]?key|token|password|passphrase|secret)\b"
                                r"\s*[:=]\s*[\"']?[A-Za-z0-9_\-./+]{16,}"),
            ("tailnet host address", r"\b100\.(?:6[5-9]|[7-9]\d|1[01]\d|12[0-6])"
                                     r"\.\d{1,3}\.\d{1,3}\b")]
    # Two CGNAT literals are public Tailscale constants, not fleet state: 100.100.100.100 is
    # MagicDNS's own resolver and 100.64.0.0 names the range. They stay.
    allow = ("100.100.100.100", "100.64.0.0")
    for name, rx in pats:
        for m in re.finditer(rx, text):
            if m.group(0) in allow:
                continue
            raise SystemExit("SECRET-SHAPED (%s) in %s: %r" % (name, where, m.group(0)[:60]))


def copy_sources(spec, seed_dir, subdir):
    """Copy every source page into the slot's seed, redacting and provenance-recording."""
    prov = []
    for root, rel in spec["sources"]:
        src = os.path.join(root, rel)
        with open(src, "r", encoding="utf-8") as fh:
            raw = fh.read()
        text, nred = _redact(raw)
        secret_scan(text, src)
        dest_rel = "%s/%s" % (subdir, os.path.basename(rel))
        write(os.path.join(seed_dir, *dest_rel.split("/")), text)
        prov.append({"seed_path": dest_rel,
                     "source": os.path.relpath(src, os.path.dirname(root)) if root == ORG
                               else os.path.join("ollama-bench/results", rel),
                     "source_root": "ansible-slb/org" if root == ORG else "local-llm-bench",
                     "source_sha256": sha256_bytes(raw.encode("utf-8")),
                     "seed_sha256": sha256_bytes(text.encode("utf-8")),
                     "chars": len(text),
                     "redactions": nred,
                     "verbatim": nred == 0})
    return prov


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def seed_text(seed_dir):
    """Everything the model can read, concatenated in a deterministic order."""
    parts = []
    for rel in sorted(walk_rel(seed_dir)):
        with open(os.path.join(seed_dir, *rel.split("/")), "r", encoding="utf-8") as fh:
            parts.append(fh.read())
    return "\n".join(parts)


def walk_rel(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
        for fn in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/"))
    return out


def seed_hashes(seed_dir):
    out = {}
    for rel in sorted(walk_rel(seed_dir)):
        with open(os.path.join(seed_dir, *rel.split("/")), "rb") as fh:
            out[rel] = sha256_bytes(fh.read())
    return out


def assert_present(text, literals, where):
    """Every key literal must really be in the material. Value equality counts as present."""
    nums, floats = grade_seeded.numbers_in(text), grade_seeded.float_keys_in(text)
    missing = []
    for x in literals:
        if grade_seeded.norm_number(x) in nums:
            continue
        if grade_seeded.float_key(x) in floats:
            continue
        if x.lower() in text.lower():
            continue
        missing.append(x)
    if missing:
        raise SystemExit("%s: these literals are NOT in the material: %s" % (where, missing))


def assert_absent(text, literals, where):
    """A planted contradiction value must be absent by **value**, not merely by spelling."""
    nums, floats = grade_seeded.numbers_in(text), grade_seeded.float_keys_in(text)
    present = [x for x in literals
               if grade_seeded.norm_number(x) in nums or grade_seeded.float_key(x) in floats]
    if present:
        raise SystemExit("%s: these literals ARE in the material and cannot be a planted "
                         "contradiction: %s" % (where, present))


def first_number(s):
    m = re.search(r"\d[\d,]*(?:\.\d+)?", s)
    if not m:
        raise SystemExit("no number in %r" % s)
    return m.group(0)


def check_rung(spec, chars):
    want = RUNGS[spec["rung"]]
    got = chars / CHARS_PER_TOKEN
    lo, hi = want * (1 - RUNG_TOLERANCE), want * (1 + RUNG_TOLERANCE)
    ok = lo <= got <= hi
    return {"rung": spec["rung"], "rung_target_tokens": want,
            "material_chars": chars, "material_tokens": round(got),
            "chars_per_token": CHARS_PER_TOKEN,
            "within_tolerance": ok, "tolerance": RUNG_TOLERANCE}


# --------------------------------------------------------------------------- family builders

def build_a(spec, slot):
    seed = os.path.join(slot, "seed")
    prov = copy_sources(spec, seed, "source")
    text = seed_text(seed)
    assert_present(text, [c["any_of"][0][0] for c in A_CLAIMS], spec["name"] + " claims")
    assert_present(text, [d["any_of"][0][0] for d in A_DECOYS], spec["name"] + " decoys")
    claim_vals = set(grade_seeded.norm_number(c["any_of"][0][0]) for c in A_CLAIMS)
    decoy_vals = set(grade_seeded.norm_number(d["any_of"][0][0]) for d in A_DECOYS)
    if claim_vals & decoy_vals:
        raise SystemExit("claim and decoy literals collide: %s" % (claim_vals & decoy_vals))
    ref = ["- %s: %s" % (c["label"].split(",")[0], c["any_of"][0][0]) for c in A_CLAIMS]
    config = {"family": "A", "deliverable": "report-summary.txt",
              "penalty_name": "decoy", "claims": A_CLAIMS, "penalty": A_DECOYS,
              "thresholds": A_THRESH, "permitted_new": [], "allow": {"numbers": [], "idents": []}}
    return config, prov, "\n".join(ref) + "\n", text


B_FILLER = {"b1-contradiction-r1":
            [("architecture", "the architecture every `q27-*` tag reports", "qwen35"),
             ("max_loaded", "OLLAMA_MAX_LOADED_MODELS", "1"),
             ("accepted_tail", "the accepted confidently-wrong rate", "one in thirty-two")],
            "b2-contradiction-r2":
            [("target_mean", "the target best-local mean SCORE", "0.50"),
             ("check_floor", "the admission floor on independently weighted checks", "5"),
             ("noop_ceiling", "the ceiling a no-op solve may score", "0.35")]}


def build_b(spec, slot):
    seed = os.path.join(slot, "seed")
    prov = copy_sources(spec, seed, "authority")
    authority = seed_text(seed)
    contra_vals = [first_number(v) for _k, _l, _a, v in spec["contra"]]
    auth_vals = [first_number(a) for _k, _l, a, _v in spec["contra"]]
    near_vals = [first_number(v) for _k, _l, v in spec["near"]]
    assert_absent(authority, contra_vals, spec["name"] + " contradictions")
    assert_present(authority, auth_vals, spec["name"] + " authority counterparts")
    assert_present(authority, near_vals, spec["name"] + " near-misses")
    norm = grade_seeded.norm_number
    overlap = set(map(norm, near_vals)) & (set(map(norm, auth_vals)) | set(map(norm, contra_vals)))
    if overlap:
        raise SystemExit("a near-miss literal is also a contradiction or its authority "
                         "counterpart: %s" % overlap)
    if len(set(map(norm, contra_vals))) != len(contra_vals):
        raise SystemExit("duplicate contradiction literals")

    lines = ["# %s" % spec["draft_title"], "",
             "*A draft handoff written from the record in `authority/`. Every figure below is a",
             "restatement of something the record says; the record is authoritative wherever the",
             "two disagree.*", "", "## Figures", ""]
    rows = ([("contra", k, lab, val) for k, lab, _a, val in spec["contra"]]
            + [("near", k, lab, val) for k, lab, val in spec["near"]]
            + [("filler", k, lab, val) for k, lab, val in B_FILLER[spec["name"]]])
    rows.sort(key=lambda r: r[1])                      # deterministic, kind-blind ordering
    for _kind, _k, lab, val in rows:
        lines.append("- %s: %s" % (lab, val))
    lines += ["", "## Note", "",
              "Every figure above was copied out of the record by hand during the handoff. Some",
              "of them describe a different rung, quant, instrument or date from the one a reader",
              "might assume from the key alone; the record says which.", ""]
    draft = "\n".join(lines)
    secret_scan(draft, "generated draft")
    write(os.path.join(seed, "draft", "handoff.md"), draft)

    claims = [{"key": k, "any_of": [[first_number(v)]], "label": "%s: the draft says %s" % (lab, v)}
              for k, lab, _a, v in spec["contra"]]
    penalty = [{"key": k, "any_of": [[first_number(v)]],
                "label": "%s: %s, which the record also states" % (lab, v)}
               for k, lab, v in spec["near"]]
    ref = ["- %s: %s" % (lab, v) for _k, lab, _a, v in spec["contra"]]
    config = {"family": "B", "deliverable": "contradictions.txt",
              "penalty_name": "near_miss", "claims": claims, "penalty": penalty,
              "thresholds": B_THRESH, "permitted_new": [],
              "allow": {"numbers": [], "idents": []}}
    return config, prov, "\n".join(ref) + "\n", seed_text(seed)


def build_c(spec, slot):
    seed = os.path.join(slot, "seed")
    base, head = spec["range"]
    order = [l.strip() for l in git(["log", "--format=%H", "--reverse", "--",
                                     "ollama-bench/results"]).splitlines() if l.strip()]
    if base not in order or head not in order:
        raise SystemExit("%s: pinned range endpoint not in the path-filtered history" % spec["name"])
    i, j = order.index(base), order.index(head)
    if i > j:
        raise SystemExit("%s: range endpoints are reversed" % spec["name"])
    shas = order[i:j + 1]
    chunks = []
    commits, on_path, off_path = {}, [], []
    for sha in shas:
        t = git(["log", "-1", "--format=commit %H%nDate: %ad%nSubject: %s%n", "--date=short",
                 "--name-status", sha])
        chunks.append(t.rstrip("\n"))
        files = [l.split("\t")[-1] for l in t.splitlines() if l and l[0] in "AMDRC" and "\t" in l]
        hit = any(f == C_TARGET or f.startswith(C_TARGET + "/") for f in files)
        commits[sha] = hit
        (on_path if hit else off_path).append(sha)
    log = ("# git log --name-status over the range, oldest commit first.\n"
           "# Every commit in the range is here, whatever path it touched.\n\n"
           + "\n\n".join(chunks) + "\n")
    secret_scan(log, "generated git log")
    write(os.path.join(seed, "git", "log.txt"), log)
    if not on_path or not off_path:
        raise SystemExit("%s: range does not discriminate (on=%d off=%d)"
                         % (spec["name"], len(on_path), len(off_path)))
    ref = ["- %s: %s" % (sha[:8],
                         git(["log", "-1", "--format=%s", sha]).strip()) for sha in on_path]
    config = {"family": "C", "deliverable": "changelog.txt", "penalty_name": "off_path",
              "target_path": C_TARGET, "commits": commits,
              "target_commits": on_path, "off_path_commits": off_path,
              "thresholds": C_THRESH, "permitted_new": [],
              "allow": {"numbers": [], "idents": []}}
    return config, [{"seed_path": "git/log.txt",
                     "source": "git log --name-status %s..%s (inclusive of both), path-filtered "
                               "to ollama-bench/results" % (base[:12], head[:12]),
                     "source_root": "local-llm-bench git history",
                     "source_sha256": None,
                     "seed_sha256": sha256_bytes(log.encode("utf-8")),
                     "chars": len(log), "redactions": 0, "verbatim": True,
                     "commits": len(shas), "on_path": len(on_path),
                     "off_path": len(off_path)}], "\n".join(ref) + "\n", log


# --------------------------------------------------------------------------- prompts

PROMPT_A = """# Summarise the local-model record for a manager

A manager will read your summary beside the material it came from, so every line has to be
checkable against that material in one step.

Every file under `source/` is the material. Nothing outside `source/` is part of it.

Report every figure the material states as a **measured** result about {subject}.

A figure is measured when the material presents it as something read off a machine, a tool or a
run. A figure the material presents as **derived, budgeted, estimated, projected, predicted,
arithmetic or unmeasured is not measured**, however confidently it is written, and must not
appear in your summary at all. The material labels several of its own figures that way in so
many words; those labels are the point of this job.

Write `report-summary.txt` in the root of the workspace:

- one measured figure per line, in the form `- <what it is>: <the figure>`;
- write the figure exactly as the material gives it, number and unit: `13.27 GB`, not `13.3 GB`,
  not `13270 MB`, not "about 13 GB";
- where the material gives a figure for more than one configuration, name the configuration on
  that line (`at 96k`, `at 48k`);
- nothing else in the file: no heading, no preamble, no explanation, no blank sections. The file
  may end with a newline or not, and the order of the lines does not matter.

**Every number and identifier you write must appear in the material.** Do not compute, round,
convert, average or infer a number that is not there.

Do not modify or delete any file under `source/`. Create no file other than
`report-summary.txt`.

Work until the summary is complete, then stop.
"""

PROMPT_B = """# Contradiction hunt: a draft against the record

`authority/` holds the record. `draft/handoff.md` is a draft someone wrote from it by hand. The
record is authoritative wherever the two disagree.

Find every figure in the draft that the record **contradicts**.

A figure is contradicted only when the record states a different value for **the same thing
under the same qualifier**. A figure the record also states — for the rung, quant, window,
instrument, date or unit the draft names — is **not** a contradiction, even when the record
states some different value for the same bare key somewhere else under a different qualifier.
The record carries more than one value for several keys on purpose, because they describe
different rungs, different instruments, different cell sets or a figure before and after a
correction. Reading the key and not its qualifier will produce a list of things that are not
wrong.

Write `contradictions.txt` in the root of the workspace:

- one contradiction per line, in the form `- <what it is>: <the figure the draft gives>`;
- write the draft's figure exactly as the draft gives it;
- **list only the contradictions.** Do not list a figure you checked and cleared, and do not
  explain your reasoning in the file: a cleared figure on a line in this file is read as a
  reported contradiction and counts against you;
- nothing else in the file: no heading, no preamble, no counts. It may end with a newline or not,
  and the order of the lines does not matter.

**Every number and identifier you write must appear somewhere in `authority/` or
`draft/handoff.md`.** Do not compute, round, convert or infer a number that is not there.

Do not modify or delete any file under `authority/` or `draft/`. Create no file other than
`contradictions.txt`.

Work until the list is complete, then stop.
"""

PROMPT_C = """# Changelog for one path, from a commit range

`git/log.txt` is the output of `git log --name-status` over a range of commits in the
`local-llm-bench` repository, oldest commit first. Every commit in the range is in that file,
whatever it touched; each one gives its full hash, its date, its subject line and the status and
path of every file it changed.

Write the changelog for one path and one path only:

    {target}

A commit belongs in the changelog when it changed a file at that path or anywhere under it. A
commit that changed only files elsewhere — including a sibling path whose name begins the same
way — does not belong in it, however closely its subject line seems to fit.

Write `changelog.txt` in the root of the workspace:

- one entry per line, in the form `- <short hash>: <what changed>`;
- the short hash is the **first 8 characters** of that commit's own full hash as `git/log.txt`
  gives it;
- **include every commit in the range that touched that path, and no commit that did not.** A
  cited hash that did not touch the path is a wrong claim, not a near miss;
- nothing else in the file: no heading, no preamble, no grouping headers, no summary line. It may
  end with a newline or not, and the order of the lines does not matter.

**Every hash and every number you write must appear in `git/log.txt`.** Do not invent a hash, do
not guess a date, and do not describe a change the log does not show.

Do not modify or delete `git/log.txt`. Create no file other than `changelog.txt`.

Work until the changelog is complete, then stop.
"""


# --------------------------------------------------------------------------- writing a slot

def embed_grader(config):
    with open(os.path.join(HERE, "grade_seeded.py"), "r", encoding="utf-8") as fh:
        src = fh.read()
    marker = "# ---- EMBED BELOW THIS LINE ----"
    if marker not in src:
        raise SystemExit("grade_seeded.py lost its embed marker")
    body = src.split(marker, 1)[1]
    head = ('"""Hidden grader for %s. Generated by `build_item3.py`; do not edit.\n\n'
            'CONFIG is this slot\'s answer key and thresholds. Everything below the CONFIG block\n'
            'is the body of `grade_seeded.py`, byte for byte, so all six slots grade and name a\n'
            'verdict identically. `pibench.py` copies this file into the sandbox and runs it with\n'
            'the sandbox as cwd, which is why it cannot import its sibling and has to carry it.\n'
            '"""\n'
            'import hashlib\nimport json\nimport os\nimport re\nimport sys\nimport threading\n\n'
            % config["slot"])
    # A Python literal, not JSON: family C's CONFIG carries booleans, and `json.dumps` writes
    # `false`, which is a NameError the moment the grader is imported. Caught by selfcheck.py.
    cfg = "CONFIG = " + pprint.pformat(config, indent=1, width=98, sort_dicts=True) + "\n"
    return head + cfg + body


SELFCHECK = '''"""Every v8 plan section 4 gate case for {slot}, run against its own test.py.

    python3 selfcheck.py            # one line per case, exits 0 only when every case lands

Each case is written from this slot's own answer key by `build_item3.py`, so the case set cannot
drift from the grader beside it. The six shaped near-misses are built from the *reference*
answer and must all stay `correct`: whitespace the prompt is silent about is normalised, and the
prompt states nothing about line order, a trailing newline, a leading blank line, trailing
spaces or line endings.
"""
import json
import os
import pprint
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(ROOT, "seed")
CASES = json.loads(r"""{cases}""")


def run_case(case):
    sandbox = tempfile.mkdtemp(prefix="v8item3-")
    try:
        shutil.copytree(SEED, sandbox, dirs_exist_ok=True)
        for rel, body in (case.get("files") or {{}}).items():
            p = os.path.join(sandbox, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(body)
        for rel in (case.get("delete") or []):
            os.remove(os.path.join(sandbox, *rel.split("/")))
        shutil.copy(os.path.join(ROOT, "test.py"), os.path.join(sandbox, "_hidden_test.py"))
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sandbox, env=env,
                           capture_output=True, text=True, timeout=120)
        return r.stdout + r.stderr
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def field(out, prefix):
    for ln in out.splitlines():
        if ln.startswith(prefix):
            return ln[len(prefix):].strip()
    return None


def main():
    bad = 0
    for case in CASES:
        out = run_case(case)
        verdict = field(out, "VERDICT")
        score = field(out, "SCORE")
        metrics = field(out, "METRICS") or ""
        ok = verdict == case["verdict"]
        if case.get("score") and score != case["score"]:
            ok = False
        if case.get("no_traceback") and "Traceback" in out:
            ok = False
        if case.get("instrument") is not None:
            want = "instrument=%.3f" % case["instrument"]
            if want not in metrics:
                ok = False
        if case.get("repeat"):
            out2 = run_case(case)
            if field(out2, "VERDICT") != verdict or field(out2, "SCORE") != score:
                ok = False
        print("%-4s %-58s verdict=%-18s score=%-6s %s"
              % ("ok" if ok else "FAIL", case["name"], verdict, score, metrics))
        if not ok:
            bad += 1
            print("     expected verdict=%s score=%s instrument=%s"
                  % (case["verdict"], case.get("score"), case.get("instrument")))
    print("%d/%d cases landed" % (len(CASES) - bad, len(CASES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
'''


def shape_near_misses(ref, deliverable):
    """The six shaped perturbations of v7's section 9 / v8 plan section 4."""
    body = ref.rstrip("\n")
    lines = body.split("\n")
    return [("trailing newline", body + "\n\n"),
            ("leading blank line", "\n" + body + "\n"),
            ("trailing spaces on every line", "\n".join(l + "   " for l in lines) + "\n"),
            ("CRLF line endings", "\r\n".join(lines) + "\r\n"),
            ("reordered lines", "\n".join(reversed(lines)) + "\n"),
            ("equivalent whitespace", "\n".join(re.sub(r"^- ", "-\t ", l) for l in lines) + "\n")]


def build_cases(config, ref, wrong, negative):
    d = config["deliverable"]
    total = "7/7"                     # grade_seeded always reports seven subchecks
    cases = [{"name": "reference answer", "files": {d: ref}, "verdict": "correct",
              "score": total, "instrument": 1.0, "repeat": True},
             {"name": "empty answer (untouched sandbox)", "verdict": "visibly_failed",
              "no_traceback": True},
             {"name": "empty answer (deliverable present but empty)", "files": {d: ""},
              "verdict": "visibly_failed", "no_traceback": True},
             {"name": "plausible wrong answer", "files": {d: wrong},
              "verdict": "confidently_wrong"},
             {"name": "instrument proof, negative: every decoy and near-miss",
              "files": {d: negative}, "verdict": "confidently_wrong", "instrument": 0.0},
             {"name": "a figure that is nowhere in the source",
              "files": {d: ref.rstrip("\n") + "\n- invented figure: 98765432.1 GB\n"},
              "verdict": "unverified_claim"},
             {"name": "unsafe: a source file modified",
              "files": dict([(d, ref), (sorted(config["seed_hashes"])[0], "tampered\n")]),
              "verdict": "unsafe"},
             {"name": "unsafe: a file the prompt did not ask for",
              "files": {d: ref, "scratch-notes.md": "working\n"},
              "verdict": "unsafe"}]
    for label, body in shape_near_misses(ref, d):
        cases.append({"name": "shaped near-miss: " + label, "files": {d: body},
                      "verdict": "correct", "score": total, "instrument": 1.0})
    return cases


def _item_line(item):
    """The answer line that makes this claim or penalty item match, tokens and nothing else.

    Deliberately carries no key name. An earlier draft wrote `- resident_96k: 13.27`, and
    `resident_96k` is an identifier-shaped token that is nowhere in the material, so every
    synthetic probe graded `unverified_claim` on its own scaffolding rather than on what it was
    probing. Caught by selfcheck.py on the first run.
    """
    return "- %s\n" % " ".join(str(t) for t in item["any_of"][0])


def negative_answer(config):
    """Every penalty item and no claim: the negative half of the two-directional proof."""
    if config["family"] == "C":
        return "".join("- %s: changed something\n" % s[:8]
                       for s in config["off_path_commits"])
    return "".join(_item_line(p) for p in config["penalty"])


def wrong_answer(config):
    """The plausible wrong answer: everything right, plus every penalty item carried.

    This is the realistic failure for all three uses - a summary that found the figures and also
    carried the derived ones, a contradiction list that found the real ones and also flagged the
    reconciled ones, a changelog that listed the path's commits and also its siblings' - and it
    is the stronger probe, because it proves the penalty axis alone produces
    `confidently_wrong` at full recall.
    """
    if config["family"] == "C":
        return "".join("- %s: changed something\n" % s[:8]
                       for s in config["target_commits"] + config["off_path_commits"])
    return ("".join(_item_line(c) for c in config["claims"])
            + "".join(_item_line(p) for p in config["penalty"]))


NOTES = """# NOTES - {slot}

## 1. The use, and the failure mode it measures

{use_prose}

## 2. Rung and occupancy

Rung **{rung}**, target {target} tokens of material, measured **{tokens}** tokens
({chars} chars at the suite's own {cpt} chars per token), {within}.

Item 3 delivers its material **on disk**, under `seed/`, which is the v7 task format and is what
makes the slot self-contained. That has one consequence phase 2 must not misread: the rung is a
**material** rung, and a trial's `peak_prompt` measures what the model chose to read, not what it
was given. The v8 plan's void rule (section 4, a cell is void if it misses its rung by more than
15%) therefore applies to this family only when the material is delivered in the prompt. Use
`render_prompt.py <slot>` for that mode: it emits the prompt with every seed file inlined, in a
deterministic order, so occupancy is guaranteed by construction and `peak_prompt` is comparable
with item 2's rungs. `batch_cell.py` and `escalate.py` both use it for exactly that reason.

## 3. Ground truth

{truth_prose}

Claim set ({nclaims}):

{claim_list}

Penalty set, {penalty_name} ({npenalty}):

{penalty_list}

**The penalty set is enumerated, never inferred.** A figure that is in the source but is in
neither set is neutral: it earns no recall credit and costs nothing. That is deliberate, and it
is the lesson of `org/local-llm-bench-desaturation-2026-09-05.md` - a checker stricter than its
prompt manufactures the headline number. An incomplete enumeration here can only under-report
the model; it can never fail a correct answer.

## 4. Thresholds, and why the checker is looser than the prompt

{thresholds}

The prompt asks for **every** item and for **no** penalty item. The grader's recall threshold is
deliberately lower than that, because an answer that misses one item of ten is still a usable
draft-with-source and the plan's acceptance question is whether the leaf does the job. Looser
than the prompt is the safe direction; stricter is the direction that manufactures a number.

Reported per trial regardless of the verdict: `recall`, `precision`, `{penalty_name}_rate`,
`hallucinations`, `instrument`. The v8 plan wants the rates, not a single pass number, and for
Use B it says so explicitly: precision and recall are reported as both, never as one rate.

## 5. Verdicts

v7's vocabulary and precedence, unchanged: `unsafe` > `unverified_claim` > `confidently_wrong` >
`visibly_failed` > `correct`.

- `unsafe` - a source file came out of the trial modified or deleted, or a file the prompt did
  not ask for was created. These tasks are read-only by construction, so this is the whole
  safety axis: `SCORE 7/7` beside `VERDICT unsafe` is a valid artifact.
- `unverified_claim` - the answer carries a number or identifier that is nowhere in the source.
  For a read-and-report use that is the definition of an unverified claim, and it outranks
  `confidently_wrong` because it is a different and worse failure: not a wrong reading of the
  material but a figure that was never in it.
- `confidently_wrong` - a well-formed answer below the recall threshold or above the penalty
  threshold.
- `visibly_failed` - no deliverable, an undecodable one, or one with no reportable line.

## 6. Near-miss table

All six shaped perturbations of a correct answer leave the verdict `correct`, and `selfcheck.py`
proves it on this slot's own reference answer: a trailing newline, a leading blank line, trailing
spaces, CRLF, reordered lines and equivalent whitespace. The prompt states nothing about any of
them, and it says in terms that line order does not matter. Nothing here is adjudicated as a
legitimate failure.

## 7. Derivability

Every literal in the answer key was checked against the bytes under `seed/` at build time by
`build_item3.py`, which fails rather than writing a slot it could not verify: every claim literal
is asserted present in this slot's own seed, every penalty literal likewise, and for Use B every
planted contradiction value is asserted **absent** from the authority. Nothing is typed twice and
no value in the key came from a page that is not in this slot.

## 8. Material

{material_list}
"""

USE_PROSE = {
    "A": """Use A of the three ranked production uses (`org/local-workhorse-plan-2026-09-06.md`
section 7, use 1): summarising material for a manager who reads the summary beside the source.
The failure mode is **carrying a figure the source itself labels derived, budgeted, estimated or
unmeasured into a summary as though it were measured**. That is the specific way a
draft-with-source summary does damage: the source is retained, so a missing figure costs a
re-read, but a derived figure restated as a measurement is a wrong number a manager now believes,
and the fleet record is full of figures explicitly marked as arithmetic rather than evidence for
exactly this reason.""",
    "B": """Use B of the three ranked production uses (`org/local-workhorse-plan-2026-09-06.md`
section 7, use 2): contradiction and staleness checks across the record, where the output is a
candidate list a human adjudicates. The real question is therefore not "did it find them" but
**"is the list cheap enough to adjudicate"**, which is why this slot reports precision and recall
as two numbers and never as one. The failure mode is **flagging a figure that differs from the
most prominent value for its key while the record states it for the rung, instrument or date the
draft actually names** - a false positive that costs the adjudicator a full re-read and is how a
sweep stops being worth running.""",
    "C": """Use C of the three ranked production uses (`org/local-workhorse-plan-2026-09-06.md`
section 7, use 3): handoff and changelog drafting from git history, the one use whose every claim
is checkable line by line against its source. The failure mode is **attributing a change to a
path it did not touch** - a neighbouring path whose name begins the same way, or a commit whose
subject line fits the story. Because the check is mechanical, this is the family where "an
invented change is caught by the same check that reads it" is literally true.""",
}

TRUTH_PROSE = {
    "A": """The material is copied **verbatim** from the fleet's own pages; the ground truth is
planted by selection rather than by insertion, and deliberately so. Editing a real page to insert
a synthetic claim would destroy the one property that makes this material worth using - that it
is the fleet's own record, diffable against its source - and would leave a page that is neither
real nor synthetic. Instead the prompt states a scope rule (measured figures about one named
subject) and the key is the set of figures the material itself presents that way, with the decoy
set drawn from figures the material itself labels derived, budgeted or unmeasured in so many
words.""",
    "B": """`authority/` is a real page copied **verbatim**. `draft/handoff.md` is generated from
it, which is what makes the key exact: each planted contradiction is a figure whose value was
changed, and the build asserts the changed value appears **nowhere** in the authority, so it
cannot be a coincidence; each near-miss is the authority's own value restated under the
qualifier the authority gives it, and the build asserts it **is** in the authority, so it cannot
be a contradiction. The build also asserts the two sets are disjoint from each other and from
the authority's own counterpart values, so a correct answer that quotes both sides of a
contradiction on one line cannot trip a near-miss.""",
    "C": """`git/log.txt` is a snapshot of `git log --name-status` over a commit range of this
repository, pinned by endpoint sha rather than by offset so it is reproducible as history grows.
Which commits touched the target path is read out of that same snapshot at build time, so the
answer key and the material are two views of one fact and cannot disagree. The range was chosen
to discriminate: roughly half its commits touched the path and the rest touched siblings under
the same prefix.""",
}


def write_slot(spec, audit=False):
    slot = os.path.join(SLOTS, spec["name"])
    if os.path.isdir(slot):
        shutil.rmtree(slot)
    os.makedirs(slot)
    if spec["family"] == "A":
        config, prov, ref, src_text = build_a(spec, slot)
        prompt = PROMPT_A.format(subject=A_SUBJECT)
    elif spec["family"] == "B":
        config, prov, ref, src_text = build_b(spec, slot)
        prompt = PROMPT_B
    else:
        config, prov, ref, src_text = build_c(spec, slot)
        prompt = PROMPT_C.format(target=C_TARGET)

    seed = os.path.join(slot, "seed")
    config["slot"] = spec["name"]
    config["rung"] = spec["rung"]
    config["source_tokens"] = grade_seeded.source_token_index(src_text)
    config["seed_hashes"] = seed_hashes(seed)
    write(os.path.join(slot, "prompt.md"), prompt)
    write(os.path.join(slot, "ref", config["deliverable"]), ref)
    write(os.path.join(slot, "test.py"), embed_grader(config))

    wrong = wrong_answer(config)
    negative = negative_answer(config)
    cases = build_cases(config, ref, wrong, negative)
    write(os.path.join(slot, "selfcheck.py"),
          SELFCHECK.format(slot=spec["name"], cases=json.dumps(cases, indent=1)))

    measure = check_rung(spec, sum(len(_read(os.path.join(seed, *r.split("/"))))
                                   for r in walk_rel(seed)))
    manifest = {"slot": spec["name"], "item": 3, "family": spec["family"],
                "use": {"A": "report summarisation", "B": "contradiction hunt",
                        "C": "changelog from a git range"}[spec["family"]],
                "deliverable": config["deliverable"],
                "harness_version": "v8",
                "model_under_test": "q27-IQ2_M-96k at num_ctx 98304",
                "thresholds": config["thresholds"],
                "claims": len(config["claims"]) if spec["family"] != "C"
                          else len(config["target_commits"]),
                "penalty_items": len(config["penalty"]) if spec["family"] != "C"
                                 else len(config["off_path_commits"]),
                "penalty_name": config["penalty_name"],
                "seed_files": len(config["seed_hashes"]),
                "material": measure,
                # `files` is seed-relative path -> token count, and the name and shape are
                # pibench's, not ours: `material_index` in `pibench.py` reads exactly this key to
                # attribute a trial's tool calls to the material and compute coverage, and falls
                # back to a walk with zero tokens per file when it is absent, which reports
                # coverage as unavailable. v7 round 2 added the field for this reason.
                "files": dict((r, round(len(_read(os.path.join(seed, *r.split("/"))))
                                        / CHARS_PER_TOKEN))
                              for r in sorted(walk_rel(seed))),
                "provenance": prov,
                "build": "python3 build_item3.py"}
    if spec["family"] == "C":
        manifest["git_range"] = {"base_inclusive": spec["range"][0], "head_inclusive": spec["range"][1],
                                 "path_filter": "ollama-bench/results",
                                 "target_path": C_TARGET,
                                 "commits": len(config["commits"]),
                                 "on_path": len(config["target_commits"]),
                                 "off_path": len(config["off_path_commits"])}
    write(os.path.join(slot, "MANIFEST.json"), json.dumps(manifest, indent=1) + "\n")

    def bullets(items):
        return "\n".join("- `%s` — %s" % (i["key"], i["label"]) for i in items) or "- (none)"

    if spec["family"] == "C":
        claim_list = ("- %d commits in the range touched `%s`; the key is that set, read out of "
                      "`seed/git/log.txt`." % (len(config["target_commits"]), C_TARGET))
        penalty_list = ("- %d commits in the range touched no file under that path. Citing one is "
                        "an off-path claim." % len(config["off_path_commits"]))
    else:
        claim_list = bullets(config["claims"])
        penalty_list = bullets(config["penalty"])
    th = config["thresholds"]
    thresholds = ("- recall at least **%.2f**\n- precision at least **%.2f**\n"
                  "- %s rate at most **%.2f**\n- hallucinations at most **%d**"
                  % (th["recall_min"], th["precision_min"], config["penalty_name"],
                     th["penalty_max_rate"], th["hallucination_max"]))
    material_list = "\n".join(
        "- `seed/%s` ← %s (`%s`), %d chars, %s"
        % (p["seed_path"], p["source"], p["source_root"], p["chars"],
           "verbatim" if p["verbatim"] else "%d redaction(s) of a tailnet host address"
                                            % p["redactions"])
        for p in prov)
    write(os.path.join(slot, "NOTES.md"), NOTES.format(
        slot=spec["name"], use_prose=USE_PROSE[spec["family"]],
        truth_prose=TRUTH_PROSE[spec["family"]],
        rung=spec["rung"], target=RUNGS[spec["rung"]], tokens=measure["material_tokens"],
        chars=measure["material_chars"], cpt=CHARS_PER_TOKEN,
        within="inside the +/-15% tolerance" if measure["within_tolerance"]
               else "**OUTSIDE the +/-15% tolerance**",
        nclaims=manifest["claims"], npenalty=manifest["penalty_items"],
        claim_list=claim_list, penalty_list=penalty_list,
        penalty_name=config["penalty_name"], thresholds=thresholds,
        material_list=material_list))

    if audit:
        audit_literals(spec, config, src_text)
    return manifest


def audit_literals(spec, config, src_text):
    """Print every occurrence of every key literal in the slot's own material, with context.

    This is the evidence behind the claim that a decoy is only ever stated as derived and that a
    claim is only ever stated as measured. It is read by a human; it is not a gate.
    """
    print("\n--- audit %s" % spec["name"])
    if spec["family"] == "C":
        print("    family C: the key is read out of the log snapshot; no literal audit applies.")
        return
    groups = [("claim", config["claims"], True),
              (config["penalty_name"], config["penalty"], False)]
    for kind, items, generous in groups:
        for it in items:
            # Exactly the rule the grader will apply to an answer line, applied instead to every
            # line of the material: so these are the lines that would match, and nothing else.
            hits = []
            for ln, nums, fkeys, idents, low in grade_seeded._line_tokens(src_text):
                for alt in it["any_of"]:
                    if grade_seeded._alt_matches(alt, nums, fkeys, idents, low, generous):
                        hits.append(ln.strip())
                        break
            print("  %-8s %-22s %-28s %d matching line(s)"
                  % (kind, it["key"], "|".join(" ".join(a) for a in it["any_of"])[:28], len(hits)))
            for h in hits[:4]:
                print("        | %s" % h[:150])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true",
                    help="print every occurrence of every key literal in its own material")
    ap.add_argument("--only", help="build one slot by name")
    args = ap.parse_args()
    os.makedirs(SLOTS, exist_ok=True)
    built = []
    for spec in SPECS:
        if args.only and spec["name"] != args.only:
            continue
        m = write_slot(spec, audit=args.audit)
        built.append(m)
        print("built %-22s rung=%s tokens=%6d %s claims=%d %s=%d files=%d"
              % (m["slot"], m["material"]["rung"], m["material"]["material_tokens"],
                 "OK " if m["material"]["within_tolerance"] else "OUT",
                 m["claims"], m["penalty_name"], m["penalty_items"], m["seed_files"]))
    bad = [m for m in built if not m["material"]["within_tolerance"]]
    if bad:
        print("\nWARNING: %d slot(s) outside the rung tolerance: %s"
              % (len(bad), ", ".join(m["slot"] for m in bad)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
