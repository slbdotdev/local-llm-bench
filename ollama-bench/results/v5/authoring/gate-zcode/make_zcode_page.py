"""Assemble the ZCode reference-arm page from the two bands' durable results.

Usage: python3 make_zcode_page.py > zcode-2026-09-06.md
Reads <band>/trial-0/results.json and quota/*.json; invents nothing.
"""
import json, glob, os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.expanduser("~/.agent-runs")
RATE1302_RE = re.compile(r"\b1302\b|rate.?limit|\b429\b", re.I)
QUOTA_RE = re.compile(r"\b402\b|balance|insufficient|quota exceeded|out of credit",
                      re.I)
# ansible-slb 2b495f7 changed the supervisor's stderr handling and its failure state
# names mid-arm. Runs are re-classified here from their own durable artifacts so both
# sides of that converge are graded by one rule.
CONVERGE_COMMIT = "2b495f7"
# A plan refusal is not the model failing the task: a 1302 throttle, a real 402/quota
# stop and a task the quota gate never launched are all kept out of the denominator.
EXCLUDE = ("rate_limited", "quota_exhausted", "not_run")
# When the new supervisor landed in WSL, from the deployed script's own mtime.
# A run id embeds its UTC start: wr-wsl-YYYYMMDDTHHMMSSZ-<hex>.
CONVERGE_AT = "20260905T053753Z"
RUNID_TS_RE = re.compile(r"wr-\w+-(\d{8}T\d{6}Z)-")


def pre_converge(run_id):
    """True if this run started before the 2b495f7 supervisor landed.

    Pre-converge runs carry the unread-stderr pipe (a run absorbing many 1302
    retries could stall on a full 64 KB pipe) and the old failure-state names.
    """
    if not run_id:
        return None
    m = RUNID_TS_RE.search(run_id)
    if not m:
        return None
    return m.group(1) < CONVERGE_AT


def reclassify(rec):
    """Recompute outcome from the run's durable result.json, uniformly.

    Accepts both supervisor spellings of a 1302 throttle:
      pre-converge  state=quota_exhausted, detail says reason=rate_limited / 1302
      post-converge state=failed,          detail carries the 1302 text
    `quota_exhausted` is kept only for a genuine 402/balance refusal.
    """
    rid = rec.get("run_id")
    detail, st = "", rec.get("state")
    if rid:
        p = os.path.join(RUNS, rid, "result.json")
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
                detail = d.get("detail") or ""
                st = d.get("state", st)
            except Exception:
                pass
    n1302 = rec.get("rate_1302") or 0
    if rec.get("zrun_rc") == 0 and st == "succeeded":
        return "ok"
    if rec.get("timed_out") or rec.get("zrun_rc") == 124 or st == "timed_out":
        return "timed_out"
    if n1302 or RATE1302_RE.search(detail):
        return "rate_limited"
    if st == "quota_exhausted":
        return "quota_exhausted" if QUOTA_RE.search(detail) else "rate_limited"
    return "failed"
TASKS = ["g01", "g02", "g03", "g04", "t01", "t02", "t03", "t04"]
BANDS = [("tiny", "Tiny band (24k), `round2/suite-0`"),
         ("large", "Large band (64k), `round3/suite`")]

# Comparison rows, quoted from results/v5/authoring/reference-arms-2026-09-05.md.
# GLM baseline/sanity are GLM 5.3 Flash through pi (results/pirun/); Luna is native Codex.
REF = {
    "tiny": {"g01": ("1/1", "1/1", "1/1"), "g02": ("1/1", "1/1", "1/1"),
             "g03": ("0/1", "0/1", "1/1"), "g04": ("0/1", "0/1", "1/1"),
             "t01": ("1/1", "1/1", "1/1"), "t02": ("1/1", "0/1", "1/1"),
             "t03": ("1/1", "1/1", "1/1"), "t04": ("0/1", "1/1", "1/1")},
    "large": {"g01": ("1/1", "1/1", "1/1"), "g02": ("1/1", "1/1", "1/1"),
              "g03": ("0/1", "1/1", "1/1"), "g04": ("1/1", "1/1", "1/1"),
              "t01": ("1/1", "0/1", "1/1"), "t02": ("1/1", "1/1", "1/1"),
              "t03": ("1/1", "1/1", "1/1"), "t04": ("1/1", "1/1", "0/1")},
}


def load(band):
    p = os.path.join(HERE, band, "trial-0", "results.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    for t in TASKS:
        if t in d and isinstance(d[t], dict):
            d[t]["outcome"] = reclassify(d[t])
            d[t]["pre_converge"] = pre_converge(d[t].get("run_id"))
    return d


def note(rec):
    if rec.get("driver_error"):
        return "driver error: " + rec["driver_error"]
    if rec.get("error"):
        return rec["error"]
    if rec.get("timed_out"):
        n = "hit the 900 s timeout; a fail, not resumed"
        if rec.get("sandbox_lost"):
            n += ". Sandbox was wiped by a resume prep before grading, so the "\
                 "score shown by the checker is partial credit on the seed alone "\
                 "and is NOT this run's output; reported as n/a"
        return n
    st = rec.get("state")
    if st and st != "succeeded":
        return "run state %s (z-run rc %s)" % (st, rec.get("zrun_rc"))
    if rec.get("attempt", 1) > 1:
        a1 = rec.get("attempt1") or {}
        extra = (" after a first attempt that took %s refusals" % a1["rate_1302"]
                 if a1.get("rate_1302") else "")
        return "throttled out on attempt 1, re-run 60 s later%s" % extra
    if rec.get("pass"):
        return "clean pass"
    tail = (rec.get("tail") or "").replace("\n", " ").strip()
    return "checker: %s" % (tail[-90:] if tail else "no SCORE/VERDICT emitted")


def fmt(v):
    return "-" if v in (None, "") else str(v)


def band_table(band, title, data):
    out = ["### %s" % title, ""]
    if data is None:
        out += ["*(no results.json)*", ""]
        return out
    out += ["| task | pass | score | verdict | wall s | in tok | out tok | "
            "model reqs | 1302 | pool | outcome | note |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    npass = 0
    walls, ins, outs, reqs, r1302 = [], [], [], [], []
    scored = 0
    for t in TASKS:
        r = data.get(t, {})
        if r.get("outcome") not in EXCLUDE:
            scored += 1
            if r.get("pass"):
                npass += 1
        for lst, k in ((walls, "wall_s"), (ins, "in_tokens"),
                       (outs, "out_tokens"), (reqs, "model_requests"),
                       (r1302, "rate_1302")):
            if isinstance(r.get(k), (int, float)):
                lst.append(r[k])
        # a score measured on a sandbox that was lost is not this run's score
        score = "n/a" if r.get("sandbox_lost") else fmt(r.get("score"))
        verdict = "n/a" if r.get("sandbox_lost") else fmt(r.get("verdict"))
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            t, "PASS" if r.get("pass") else "FAIL", score,
            verdict, fmt(r.get("wall_s")), fmt(r.get("in_tokens")),
            fmt(r.get("out_tokens")), fmt(r.get("model_requests")),
            fmt(r.get("rate_1302")), fmt(r.get("conc_at_launch")),
            fmt(r.get("outcome")), note(r)))
    out.append("| **total** | **%d/%d** | | | **%s** | **%s** | **%s** | **%s** | "
               "**%s** | | | |"
               % (npass, scored, round(sum(walls), 1) if walls else "-",
                  sum(ins) if ins else "-", sum(outs) if outs else "-",
                  sum(reqs) if reqs else "-", sum(r1302) if r1302 else "-"))
    meta = data.get("_meta", {})
    ev = meta.get("rate_limit_events") or []
    pre = [t for t in TASKS if data.get(t, {}).get("pre_converge")]
    post = [t for t in TASKS if data.get(t, {}).get("pre_converge") is False]
    out += ["", "Model %s, effort %s, 900 s timeout, %d concurrent at the end. "
            "Rate-limit backoffs: %s. `1302` is the count of "
            "`[1302] Rate limit reached for requests` refusals the plan returned to "
            "that run; `pool` is the concurrency in force when it launched."
            % (meta.get("model"), meta.get("effort"),
               meta.get("final_max_concurrency", 0), len(ev) if ev else "none"),
            "",
            "Supervisor: pre-`%s` %s; post-`%s` %s."
            % (CONVERGE_COMMIT, ", ".join(pre) if pre else "none",
               CONVERGE_COMMIT, ", ".join(post) if post else "none"), ""]
    return out


def summary(datas):
    out = ["## Summary against the pi plan route and Luna", "",
           "GLM baseline and GLM sanity are GLM 5.3 Flash through pi "
           "(`results/pirun/`); Luna is native Codex at high. Both columns are "
           "quoted from `reference-arms-2026-09-05.md`. ZCode is this arm.", ""]
    for band, title in BANDS:
        d = datas.get(band)
        out += ["**%s**" % title, "",
                "| task | GLM baseline (pi) | GLM sanity (pi) | Luna | ZCode |",
                "| --- | --- | --- | --- | --- |"]
        tot = [0, 0, 0, 0]
        for t in TASKS:
            b, s, l = REF[band][t]
            z = "-"
            if d is not None:
                r = d.get(t, {})
                # a task the plan refused or the gate never launched is not a miss
                z = ("n/a" if r.get("outcome") in EXCLUDE
                     else "1/1" if r.get("pass") else "0/1")
            for i, v in enumerate((b, s, l, z)):
                if v.startswith("1"):
                    tot[i] += 1
            out.append("| %s | %s | %s | %s | %s |" % (t, b, s, l, z))
        out.append("| **total** | **%d/8** | **%d/8** | **%d/8** | **%d/8** |"
                   % tuple(tot))
        out.append("")
    return out


def quota_block():
    out = ["## Plan accounting", ""]
    files = sorted(glob.glob(os.path.join(HERE, "quota", "*.json")))
    if not files:
        return out + ["*(no quota readings)*", ""]
    out += ["| reading | window | used | cap | pct | remaining |",
            "| --- | --- | --- | --- | --- | --- |"]
    UNIT = {3: "hour", 6: "week", 4: "day", 5: "month"}
    firsts = {}
    for f in files:
        label = os.path.basename(f).split("-", 1)[1].rsplit(".", 1)[0]
        d = json.load(open(f))
        for lim in d["data"]["limits"]:
            w = "%s%s" % (lim["number"], UNIT.get(lim["unit"], lim["unit"]))
            pct = 100.0 * lim["currentValue"] / lim["usage"] if lim["usage"] else 0
            out.append("| %s | %s | %s | %s | %.2f%% | %s |"
                       % (label, w, lim["currentValue"], lim["usage"], pct,
                          lim["remaining"]))
            firsts.setdefault((label, w), lim["currentValue"])
    out.append("")
    # consecutive deltas on the 5-hour window, which is the one that gates the arm
    def used5h(f):
        for lim in json.load(open(f))["data"]["limits"]:
            if lim["unit"] == 3:
                return lim["currentValue"], lim["usage"]
        return None, None

    if len(files) >= 2:
        out += ["Consecutive movement on the 5-hour window:", "",
                "| from | to | credits |", "| --- | --- | --- |"]
        for a, b in zip(files, files[1:]):
            la = os.path.basename(a).split("-", 1)[1].rsplit(".", 1)[0]
            lb = os.path.basename(b).split("-", 1)[1].rsplit(".", 1)[0]
            ua, _ = used5h(a)
            ub, _ = used5h(b)
            if ua is None or ub is None:
                continue
            out.append("| %s | %s | **%+d** |" % (la, lb, ub - ua))
        out.append("")
    out += [
        "**What this can and cannot answer.** It settles the direction: ZCode traffic "
        "on the Coding Plan **does** draw credits, so the campaign's unlimited-Flash "
        "allowance does not make it free. It cannot give a per-harness figure. The "
        "same `ZAI_API_KEY` was carrying a pi prompt campaign and the v7 roundtable's "
        "GLM worker throughout, so every delta above is the sum of three workloads "
        "and none of it is attributable to ZCode alone. A clean number needs a quiet "
        "plan, which this arm never had.", ""]
    return out


def main():
    datas = {b: load(b) for b, _ in BANDS}
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    L = ["# ZCode reference arm on the v5 suite — GLM 5.3 Flash, one trial, both bands",
         "",
         "*Run %s UTC by the ZCode arm manager on FRACTAL (WSL), through `z-run` "
         "against ZCode's own app-server runtime on the owner's Z.ai GLM Coding Plan. "
         "Model GLM-5.3-Flash, effort high (runtime variant `high`), 900 s timeout. "
         "prep and grade mirror `prep_gate_sandboxes.py` exactly: sandbox from `seed/` "
         "only, `test.py` copied in as `_hidden_test.py` and run with `cwd=sandbox`, "
         "`PYTHONUTF8=1`, 60 s; pass iff rc 0 and `PASS` in stdout. Driver: "
         "`run_zcode_gate.py`; decisions and incidents in `ledger.md`.*" % today,
         "",
         "**Concurrency, and what it costs the wall column.** The arm opened at four "
         "concurrent as briefed and had to come down to one: the plan was shared that "
         "night with a pi prompt campaign and two v7 workers, and it answered ZCode "
         "with `[1302] Rate limit reached for requests` in volume. ZCode retries a "
         "1302 internally up to eleven times with backoff, so the refusals never "
         "surfaced as an error — they surfaced as wall time. **A `wall s` beside a "
         "high `1302` count measures the plan, not the model**, and no cross-arm speed "
         "claim should be read off this column. Pass/fail is unaffected: the checker "
         "grades the sandbox, not the clock. At one concurrent, refusals fell to "
         "0-2 per run and an unthrottled tiny task finished in about 30 s.",
         "",
         "## Per band", ""]
    for band, title in BANDS:
        L += band_table(band, title, datas[band])
    L += summary(datas)
    L += [
        "## Incidents and caveats",
        "",
        "Full account in `ledger.md`; these are the ones that bear on how the numbers "
        "should be read.",
        "",
        "1. **The plan throttled this arm hard.** 68 `[1302]` refusals across the two "
        "bands, and at four concurrent nothing finished at all in nine minutes. The "
        "pool came down 4 -> 2 -> 1. The brief's own trigger — drop to two on a "
        "rate-limit error at the start of a run — could never fire, because ZCode "
        "retries a 1302 internally up to eleven times and the refusal reaches the "
        "driver as wall time, not as an error.",
        "2. **A supervisor converge landed mid-arm** (`ansible-slb 2b495f7`, "
        "05:37:53Z). It fixed an unread 64 KB stderr pipe that had frozen all four "
        "pool-4 runs, and renamed the failure states. Outcomes are therefore "
        "re-derived at report time from each run's own durable `result.json`, so both "
        "sides of the converge are graded by one rule. Every pool-4 run carried the "
        "pipe fault, so **pool 4 vs pool 1 is not a clean concurrency comparison** and "
        "is not offered as one.",
        "3. **large/g03 timed out at 900 s and is recorded as a fail, not re-run**, "
        "per the brief. Its 5 refusals are far below the 18-30 of genuinely throttled "
        "runs and it ran post-converge, so the timeout is real rather than a plan "
        "artifact. Its sandbox was wiped by a resume prep before grading, so the "
        "checker's 7/14 is partial credit on the seed alone and is reported as `n/a` "
        "rather than as this run's score.",
        "4. **The quota gate did not work on the large band.** It was to stop launches "
        "at 85% of the 5-hour window; it read the window once at 06:18:34Z (78.30%) "
        "and every queued task reused that reading, because the check sat before the "
        "concurrency semaphore rather than after it. The band ran on to leave the "
        "window at 98.85%. No result here is invalidated and no run was cut short, but "
        "the protection was not delivered, and the other workload sharing this key had "
        "22 credits of headroom rather than the ~300 it should have had. Fixed in the "
        "driver afterwards.",
        "5. **A tiny-band column is weaker than it looks.** `conc_at_launch` there "
        "records the pool at finish, not at launch, so every tiny row reads 1 although "
        "g01's first attempt and g02 launched at 2. g01's `1302=0` is its second "
        "attempt; its first took 23 refusals. Neither affects a score.",
        "",
    ]
    L += quota_block()
    print("\n".join(L))


if __name__ == "__main__":
    main()
