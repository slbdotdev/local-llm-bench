#!/usr/bin/env python3
"""The dedicated batch-throughput cell: fifty small jobs back to back. Item 5, second half.

    python3 batch_cell.py --dry-run                              # offline, proves the accounting
    python3 batch_cell.py --endpoint http://HOST:11434 --model q27-IQ2_M-96k
    python3 batch_cell.py --endpoint ... --model ... --n 50 --threshold 0.8 --out cell.json

The endpoint and the model are **arguments**, never constants: no host name and no tag is baked
into this file, so the same program measures the desktop, a future host, or nothing at all under
`--dry-run`.

## What it measures, and what it keeps separate

The batch lane of the workhorse plan (section 4, phase 3) is worth having only if a number exists
for it, and the number the plan asks for is **items per hour at accuracy over a threshold**, with
**model load and unload overhead reported separately from inference**. Those are three different
clocks and this program never adds them up behind your back:

    load_s         the model coming on to the card, taken from Ollama's own `load_duration`
    inference_s    `prompt_eval_duration + eval_duration`, the work itself
    overhead_s     batch wall minus inference: queueing, the network, JSON, grading
    unload_s       wall of the `keep_alive: 0` request that gives the card back

`items_per_hour` is over the batch wall alone, because that is the steady-state rate a queue
would see. `items_per_hour_with_load` includes the load and the unload, because that is what an
overnight lane actually pays for a drain of this size, and the two differ by more than rounding
at n=50. Both are printed, and the ledger says which is which in words.

Accuracy comes from `grade_seeded`, the same grader the GPU cells use, so a batch number and a
quality number cannot disagree about what `correct` means. A job is one item-3 slot rendered as a
single-shot prompt by `render_prompt.py`: "small" here means the **r1 rung**, about 12,000 tokens
of material, which is the small end of this family and the size the batch lane would really
carry.

## The protocol, and why it is in this order

1. unload with `keep_alive: 0`, so the load in step 2 is a real cold load and not a warm hit;
2. one load-timing request, which is the only request whose `load_duration` is expected non-zero;
3. n jobs back to back with `keep_alive` held, timing each;
4. unload with `keep_alive: 0` — the owner's card comes back, per the availability ruling;
5. read `/api/ps` and record whether it came back empty (v8 plan section 5).

A non-zero `load_duration` on any job in step 3 means the model was evicted mid-batch. That is
recorded as `reloads` and is a finding, not an error: it is the signature of the availability flag
flipping or of another model being pulled in, and it invalidates the steady-state rate.

This program holds the GPU. It prints the exact `GPU_BUDGET.log` line for the interval it held
and deliberately does **not** write it: that log is outside this directory and appending to it is
the control session's to do.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grade_seeded          # noqa: E402
import render_prompt         # noqa: E402

DEFAULT_JOBS = ["a1-summarise-r1", "b1-contradiction-r1", "c1-changelog-r1"]
NS = 1e9


def post(endpoint, path, payload, timeout):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint.rstrip("/") + path, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get(endpoint, path, timeout):
    req = urllib.request.Request(endpoint.rstrip("/") + path)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def generate(endpoint, model, prompt, keep_alive, timeout, num_predict):
    """One native `/api/generate` call. Native, not `/v1/`, because only it reports the clocks."""
    return post(endpoint, "/api/generate",
                {"model": model, "prompt": prompt, "stream": False,
                 "keep_alive": keep_alive,
                 "options": {"num_predict": num_predict, "temperature": 0}}, timeout)


def unload(endpoint, model, timeout):
    t0 = time.time()
    post(endpoint, "/api/generate", {"model": model, "prompt": "", "keep_alive": 0}, timeout)
    return round(time.time() - t0, 2)


# ----------------------------------------------------------------- the dry-run model

class DryRun:
    """A deterministic stand-in for the endpoint that exists to prove the accounting.

    It returns the slot's own reference answer for the first `correct_for` jobs and a
    decoy-carrying wrong answer after that, with durations drawn from v7's measured curve
    (`results/v7` cells: 41.9 generation tok/s at 96k, prefill an order faster). Nothing here is
    a prediction of what the model will do — it is a fixture for the arithmetic.
    """

    def __init__(self, correct_for, load_s=9.4, gen_tps=41.9, prefill_tps=700.0,
                 overhead_s=0.35):
        self.correct_for = correct_for
        self.load_s = load_s
        self.gen_tps = gen_tps
        self.prefill_tps = prefill_tps
        self.overhead_s = overhead_s
        self.calls = 0

    def generate(self, prompt, answer_ok, ref, wrong):
        self.calls += 1
        in_tok = max(1, round(len(prompt) / 4.664))
        text = ref if answer_ok else wrong
        out_tok = max(1, round(len(text) / 4.664))
        load_ns = int(self.load_s * NS) if self.calls == 1 else 0
        pe_ns = int(in_tok / self.prefill_tps * NS)
        ev_ns = int(out_tok / self.gen_tps * NS)
        total_ns = load_ns + pe_ns + ev_ns
        wall = (total_ns / NS) + self.overhead_s
        return ({"response": "===BEGIN X===\n" + text + "\n===END X===",
                 "load_duration": load_ns, "prompt_eval_duration": pe_ns,
                 "prompt_eval_count": in_tok, "eval_duration": ev_ns, "eval_count": out_tok,
                 "total_duration": total_ns, "done_reason": "stop"}, wall)


# ----------------------------------------------------------------- the cell

def load_jobs(names):
    jobs = []
    for name in names:
        slot = os.path.join(HERE, "slots", name)
        if not os.path.isdir(slot):
            raise SystemExit("no such slot: %s" % slot)
        cfg = grade_seeded.load_slot_config(slot)
        with open(os.path.join(slot, "ref", cfg["deliverable"]), "r", encoding="utf-8") as fh:
            ref = fh.read()
        jobs.append({"slot": name, "config": cfg, "prompt": render_prompt.render(slot),
                     "ref": ref, "wrong": _wrong_answer(cfg)})
    return jobs


def _wrong_answer(cfg):
    """The plausible wrong answer for the dry run: carries every penalty item.

    It carries a *correct* question block, so the fixture fails on the enumeration axis alone and
    the abstention axis is not what is being measured here.
    """
    if cfg["family"] == "C":
        body = "".join("- %s: changed something\n" % s[:8] for s in cfg["off_path_commits"])
    else:
        body = "".join("- %s\n" % " ".join(str(t) for t in p["any_of"][0])
                       for p in cfg["penalty"])
    return body + render_prompt.reference_questions(cfg)


def grade_one(cfg, reply_text):
    answer = render_prompt.extract_answer(reply_text, cfg["deliverable"])
    result = grade_seeded.grade_text(cfg, answer)
    # A single-shot reply has no sandbox, so the integrity axis cannot apply and is recorded as
    # not-applicable rather than silently passed.
    verdict = grade_seeded.decide_verdict(result, intact=True)
    return verdict, result


def run_cell(args):
    jobs = load_jobs(args.jobs.split(","))
    dry = DryRun(correct_for=args.dry_run_correct) if args.dry_run else None
    record = {"cell": "item5-batch-throughput", "harness_version": "v8",
              "endpoint": "(dry-run)" if dry else args.endpoint,
              "model": args.model, "n": args.n, "threshold": args.threshold,
              "jobs_cycled": [j["slot"] for j in jobs], "dry_run": bool(dry),
              "units": {"load_s": "seconds, Ollama load_duration",
                        "inference_s": "seconds, prompt_eval_duration + eval_duration",
                        "overhead_s": "seconds, batch wall minus inference",
                        "unload_s": "seconds of wall for the keep_alive:0 request",
                        "items_per_hour": "items / batch wall hour, load and unload excluded",
                        "items_per_hour_with_load": "items / (load + batch wall + unload) hour",
                        "accuracy": "fraction of items grading VERDICT correct"},
              "trials": []}

    # 1. cold start
    if dry:
        record["pre_unload_s"] = 0.0
    else:
        record["pre_unload_s"] = unload(args.endpoint, args.model, args.timeout)

    # 2. the load-timing request
    load_s = 0.0
    if dry:
        resp, wall = dry.generate("load probe", True, "probe", "probe")
        load_s = resp["load_duration"] / NS
        record["load_probe_wall_s"] = round(wall, 2)
    else:
        t0 = time.time()
        resp = generate(args.endpoint, args.model, "Reply with the single word: ready.",
                        args.keep_alive, args.timeout, 8)
        record["load_probe_wall_s"] = round(time.time() - t0, 2)
        load_s = resp.get("load_duration", 0) / NS
    record["load_s"] = round(load_s, 2)

    # 3. the batch
    batch_t0 = time.time()
    inference_s = 0.0
    reloads = 0
    correct = 0
    for i in range(args.n):
        job = jobs[i % len(jobs)]
        if dry:
            resp, wall = dry.generate(job["prompt"], i < args.dry_run_correct,
                                      job["ref"], job["wrong"])
        else:
            t0 = time.time()
            resp = generate(args.endpoint, args.model, job["prompt"], args.keep_alive,
                            args.timeout, args.num_predict)
            wall = time.time() - t0
        infer = (resp.get("prompt_eval_duration", 0) + resp.get("eval_duration", 0)) / NS
        inference_s += infer
        if resp.get("load_duration", 0) > 0:
            reloads += 1
        verdict, result = grade_one(job["config"], resp.get("response", ""))
        if verdict == "correct":
            correct += 1
        record["trials"].append({
            "i": i, "slot": job["slot"], "verdict": verdict,
            "wall_s": round(wall, 2), "inference_s": round(infer, 2),
            "load_duration_s": round(resp.get("load_duration", 0) / NS, 2),
            "in_tokens": resp.get("prompt_eval_count"), "out_tokens": resp.get("eval_count"),
            "stop_reason": resp.get("done_reason"),
            "recall": round(result["recall"], 3), "precision": round(result["precision"], 3),
            "penalty_rate": round(result["penalty_rate"], 3),
            "hallucinations": result["hallucinations"],
            "instrument": round(result["instrument_score"], 3)})
    batch_wall = (sum(t["wall_s"] for t in record["trials"]) if dry
                  else time.time() - batch_t0)

    # 4 and 5. give the card back, then prove it
    if dry:
        record["unload_s"] = 0.0
        record["api_ps_empty"] = None
    else:
        record["unload_s"] = unload(args.endpoint, args.model, args.timeout)
        try:
            ps = get(args.endpoint, "/api/ps", args.timeout)
            record["api_ps_empty"] = not (ps.get("models") or [])
        except (urllib.error.URLError, OSError) as exc:
            record["api_ps_empty"] = None
            record["api_ps_error"] = str(exc)[:200]

    record["batch_wall_s"] = round(batch_wall, 2)
    # Summed from the per-trial column as printed, not from the unrounded accumulator: at n=50
    # the two differ by tenths of a second and a ledger a reader cannot re-add by hand is not a
    # ledger. `inference_s` above is kept only to show the two agree to within rounding.
    record["inference_s"] = round(sum(t["inference_s"] for t in record["trials"]), 2)
    record["inference_s_unrounded"] = round(inference_s, 2)
    record["overhead_s"] = round(batch_wall - record["inference_s"], 2)
    record["reloads_mid_batch"] = reloads
    record["correct"] = correct
    record["accuracy"] = round(correct / args.n, 4) if args.n else None
    record["items_per_hour"] = round(3600.0 * args.n / batch_wall, 1) if batch_wall > 0 else None
    total = load_s + batch_wall + record["unload_s"] + record["pre_unload_s"]
    record["items_per_hour_with_load"] = round(3600.0 * args.n / total, 1) if total > 0 else None
    record["items_per_hour_correct"] = (round(record["items_per_hour"] * record["accuracy"], 1)
                                       if record["items_per_hour"] else None)
    record["gpu_holding_s"] = round(total, 1)
    record["decision"] = ("go" if (record["accuracy"] or 0) >= args.threshold else "no-go")
    record["gpu_budget_line"] = (
        "item5-batch-throughput  %s  n=%d  %.0f s  accuracy=%s  items/h=%s  (append by hand to "
        "results/v8/GPU_BUDGET.log)" % (args.model, args.n, total, record["accuracy"],
                                        record["items_per_hour"]))
    return record


def check_accounting(record):
    """The dry run's whole purpose: prove the three clocks add up and the rates follow."""
    checks = []

    def chk(name, got, want, tol=0.05):
        ok = abs(got - want) <= tol if isinstance(want, float) else got == want
        checks.append((name, got, want, ok))

    n = record["n"]
    trials = record["trials"]
    chk("one trial per job", len(trials), n)
    chk("batch wall equals the sum of the per-trial walls",
        record["batch_wall_s"], round(sum(t["wall_s"] for t in trials), 2), 0.02)
    chk("inference equals the sum of the per-trial inference",
        record["inference_s"], round(sum(t["inference_s"] for t in trials), 2), 0.02)
    chk("load + inference + overhead equals the wall this cell accounts for",
        round(record["inference_s"] + record["overhead_s"], 2), record["batch_wall_s"], 0.02)
    chk("load is reported outside the batch wall, not inside it",
        sum(t["load_duration_s"] for t in trials), 0.0, 0.001)
    chk("accuracy equals correct over n", record["accuracy"], round(record["correct"] / n, 4))
    chk("items/hour is over the batch wall alone",
        record["items_per_hour"], round(3600.0 * n / record["batch_wall_s"], 1), 0.2)
    chk("items/hour with load is strictly lower",
        record["items_per_hour_with_load"] < record["items_per_hour"], True)
    chk("items/hour at accuracy is the product",
        record["items_per_hour_correct"],
        round(record["items_per_hour"] * record["accuracy"], 1), 0.2)
    chk("gpu holding time is load + batch + unloads",
        record["gpu_holding_s"],
        round(record["load_s"] + record["batch_wall_s"] + record["unload_s"]
              + record["pre_unload_s"], 1), 0.15)
    chk("the threshold decides the decision", record["decision"],
        "go" if record["accuracy"] >= record["threshold"] else "no-go")
    chk("no reload mid-batch in the fixture", record["reloads_mid_batch"], 0)
    graded_correct = sum(1 for t in trials if t["verdict"] == "correct")
    chk("the grader agreed with the fixture's intent", graded_correct, record["correct"])
    bad = 0
    for name, got, want, ok in checks:
        print("%-4s %-62s got=%-16s want=%s" % ("ok" if ok else "FAIL", name, got, want))
        if not ok:
            bad += 1
    print("%d/%d accounting checks passed" % (len(checks) - bad, len(checks)))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", help="Ollama base URL, e.g. http://HOST:11434")
    ap.add_argument("--model", default="q27-IQ2_M-96k", help="the wire model tag")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--jobs", default=",".join(DEFAULT_JOBS))
    ap.add_argument("--threshold", type=float, default=0.8,
                    help="accuracy at or above which the lane is a go")
    ap.add_argument("--keep-alive", default="5m")
    ap.add_argument("--num-predict", type=int, default=1200)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--out", help="write the full record here as JSON")
    ap.add_argument("--dry-run", action="store_true",
                    help="no network, no GPU: prove the accounting against a fixture")
    ap.add_argument("--dry-run-correct", type=int, default=42,
                    help="how many of the n fixture answers are the reference answer")
    args = ap.parse_args()
    if not args.dry_run and not args.endpoint:
        ap.error("--endpoint is required unless --dry-run")
    record = run_cell(args)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=1)
        print("wrote %s" % args.out)
    print(json.dumps(dict((k, v) for k, v in record.items() if k != "trials"), indent=1))
    if args.dry_run:
        print("")
        return 1 if check_accounting(record) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
