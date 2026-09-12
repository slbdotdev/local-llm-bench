#!/usr/bin/env python3
"""Escalation economics: hosted-only against local-draft-then-hosted-verify. Item 6.

    python3 escalate.py --dry-run                          # offline, proves the ledger
    python3 escalate.py --dry-run --dry-run-draft-quality bad
    python3 escalate.py --local-endpoint http://HOST:11434 --local-model q27-IQ2_M-96k \\
                        --hosted-endpoint https://API/v1 --hosted-model MODEL \\
                        --hosted-api-key-env SOME_KEY_ENV --n 10

## The question, and why it needs a ledger rather than an opinion

Section 7 of `org/local-workhorse-plan-2026-09-06.md` says in terms that **no per-task cost figure
exists**: "`scripts/plan-usage.py` reports aggregate pressure on four plans and no page itemises a
workload, so every 'displaced per week' is unknown and the ranking below is a judgement about
volume against consequence, not a measurement." This program is the instrument that replaces that
judgement with a number, which is why the v8 plan (item 6) says it "also builds the per-task cost
figure section 7 of the workhorse plan says does not exist".

Two arms over the same items, paired so the correctness difference is a difference and not two
separate rates:

    arm 1  hosted_only                 the hosted model answers the task from the material
    arm 2  local_draft_hosted_verify   the local model drafts; the hosted model is then given
                                       the material *and the draft* and asked to produce the
                                       final answer, correcting the draft where it is wrong

Arm 2 is the one that can lose, and the v8 plan says how: "A local draft that is wrong in a
plausible way can cost more hosted tokens than no draft, and that result kills a use." Arm 2's
hosted input is arm 1's input **plus the draft**, so it is always larger in tokens; it only pays
if it buys enough correctness, or if it lets a cheaper hosted model be used. The ledger reports
both halves and never averages them into one number.

## Units, stated because a cost ledger without units is a rumour

    hosted_input_tokens    tokens the hosted provider counted as input, read from its own
                           `usage.prompt_tokens`. Where the provider reports no usage, the figure
                           is estimated at the suite's 4.664 chars per token and `token_source`
                           says `estimated`, per item. An estimated ledger is never quoted as a
                           measured one.
    hosted_output_tokens   the same, from `usage.completion_tokens`.
    local_*                never billed; recorded as wall seconds and output tokens, because the
                           local arm's cost is GPU time and the owner's contention, not money
                           (workhorse plan section 10: "Accounting replaces token cost with
                           time").
    correct                items grading `VERDICT correct` under `grade_seeded`, the same grader
                           the GPU cells use.

Dollars are deliberately absent: a price per token belongs to whatever endpoint phase 2 points
this at, and baking one in here would be a number that rots. Multiply the token columns by the
provider's own rate at analysis time.

## The harness rule this program must not be used to break

A model reachable on a plan runs through its native harness and never through a raw endpoint
(`org/agent-harnesses.md`, and the fleet's standing rule). The hosted arm here is therefore an
**API-billed** endpoint — which is also the only kind that returns a usage field to put in a
ledger. `--hosted-note` is recorded verbatim in the ledger so the record says what the hosted arm
actually was. A plan-bound reference arm is **out of scope for this program**: it cannot report a
token ledger, which is the only thing this program exists to produce, so run it as an ordinary
reference arm beside the cell rather than as arm 1 here.

No key is ever printed, logged or written to the ledger. `--hosted-api-key-env` names an
environment variable; this program reads it, puts it in one Authorization header, and records only
the variable's **name**.
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

CHARS_PER_TOKEN = 4.664
NS = 1e9
DEFAULT_FAMILIES = ["a1-summarise-r1", "b1-contradiction-r1", "c1-changelog-r1"]

VERIFY_PREAMBLE = """A local assistant has already produced a draft answer to the task below. The
draft is **not** authoritative: it may be right, partly right, or confidently wrong. Produce the
final answer yourself, from the material, using the draft only as a starting point. Correct
anything in it that the material does not support, add anything it missed, and drop anything it
should not have included.

===BEGIN DRAFT===
{draft}
===END DRAFT===

---

"""


def _post_json(url, payload, headers, timeout):
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers=dict(headers, **{"Content-Type": "application/json"}))
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_hosted(args, prompt):
    """One OpenAI-compatible chat completion. Returns (text, in_tokens, out_tokens, source)."""
    headers = {}
    if args.hosted_api_key_env:
        key = os.environ.get(args.hosted_api_key_env)
        if not key:
            raise SystemExit("environment variable %s is empty; refusing to call the hosted arm "
                             "unauthenticated" % args.hosted_api_key_env)
        headers["Authorization"] = "Bearer " + key          # never logged, never stored
    data = _post_json(args.hosted_endpoint.rstrip("/") + "/chat/completions",
                      {"model": args.hosted_model, "temperature": 0,
                       "messages": [{"role": "user", "content": prompt}]},
                      headers, args.timeout)
    text = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    usage = data.get("usage") or {}
    if "prompt_tokens" in usage and "completion_tokens" in usage:
        return text, usage["prompt_tokens"], usage["completion_tokens"], "provider"
    return (text, round(len(prompt) / CHARS_PER_TOKEN), round(len(text) / CHARS_PER_TOKEN),
            "estimated")


def call_local(args, prompt):
    """One native Ollama generate. Returns (text, out_tokens, wall_s, inference_s)."""
    t0 = time.time()
    data = _post_json(args.local_endpoint.rstrip("/") + "/api/generate",
                      {"model": args.local_model, "prompt": prompt, "stream": False,
                       "keep_alive": args.keep_alive,
                       "options": {"num_predict": args.num_predict, "temperature": 0}},
                      {}, args.timeout)
    wall = time.time() - t0
    infer = (data.get("prompt_eval_duration", 0) + data.get("eval_duration", 0)) / NS
    return data.get("response") or "", data.get("eval_count") or 0, wall, infer


# ----------------------------------------------------------------- the dry-run fixture

class DryArms:
    """Stand-in endpoints whose only job is to prove the ledger's arithmetic.

    `draft_quality` is the knob the v8 plan cares about:

      good  the local draft is the reference answer, so the hosted verify keeps it and arm 2
            buys nothing but costs the draft's tokens — the "escalation does not pay" outcome
      bad   the local draft carries every penalty item, the hosted verify repairs it, and arm 2
            pays the draft's tokens *and* a longer hosted output for the same answer arm 1 got
      rescue  arm 1 is wrong on some items and the draft-plus-verify gets them right, the only
            shape in which escalation pays
    """

    def __init__(self, quality, arm1_correct_frac=1.0):
        self.quality = quality
        self.arm1_correct_frac = arm1_correct_frac
        self.i = 0

    def hosted(self, prompt, job, arm, idx):
        if arm == 1:
            ok = idx < round(self.arm1_correct_frac * job["n"])
        elif self.quality == "rescue":
            ok = True
        elif self.quality == "bad":
            ok = idx < round(self.arm1_correct_frac * job["n"])
        else:
            ok = idx < round(self.arm1_correct_frac * job["n"])
        text = job["ref"] if ok else job["wrong"]
        body = "===BEGIN %s===\n%s\n===END %s===" % (job["deliverable"], text,
                                                     job["deliverable"])
        return body, round(len(prompt) / CHARS_PER_TOKEN), round(len(body) / CHARS_PER_TOKEN), \
            "fixture"

    def local(self, prompt, job):
        text = job["wrong"] if self.quality in ("bad", "rescue") else job["ref"]
        body = "===BEGIN %s===\n%s\n===END %s===" % (job["deliverable"], text,
                                                     job["deliverable"])
        out_tok = round(len(body) / CHARS_PER_TOKEN)
        infer = out_tok / 41.9 + round(len(prompt) / CHARS_PER_TOKEN) / 700.0
        return body, out_tok, infer + 0.35, infer


# ----------------------------------------------------------------- the cell

def load_family(name, n):
    slot = os.path.join(HERE, "slots", name)
    if not os.path.isdir(slot):
        raise SystemExit("no such slot: %s" % slot)
    cfg = grade_seeded.load_slot_config(slot)
    with open(os.path.join(slot, "ref", cfg["deliverable"]), "r", encoding="utf-8") as fh:
        ref = fh.read()
    if cfg["family"] == "C":
        wrong = "".join("- %s: changed something\n" % s[:8]
                        for s in cfg["target_commits"] + cfg["off_path_commits"])
    else:
        wrong = (ref + "".join("- %s\n" % " ".join(str(t) for t in p["any_of"][0])
                               for p in cfg["penalty"]))
    return {"slot": name, "config": cfg, "prompt": render_prompt.render(slot), "ref": ref,
            "wrong": wrong, "deliverable": cfg["deliverable"], "n": n}


def grade(cfg, reply):
    answer = render_prompt.extract_answer(reply, cfg["deliverable"])
    result = grade_seeded.grade_text(cfg, answer)
    # No sandbox in a single-shot arm, so the integrity axis is not applicable rather than passed.
    return grade_seeded.decide_verdict(result, intact=True), result


def run_family(args, job, dry):
    items = []
    for idx in range(job["n"]):
        rec = {"i": idx}
        # arm 1: hosted only
        if dry:
            text, tin, tout, src = dry.hosted(job["prompt"], job, 1, idx)
        else:
            text, tin, tout, src = call_hosted(args, job["prompt"])
        v1, r1 = grade(job["config"], text)
        rec["arm1"] = {"hosted_input_tokens": tin, "hosted_output_tokens": tout,
                       "token_source": src, "verdict": v1,
                       "recall": round(r1["recall"], 3),
                       "precision": round(r1["precision"], 3),
                       "penalty_rate": round(r1["penalty_rate"], 3),
                       "hallucinations": r1["hallucinations"]}
        # arm 2: local draft, then hosted verify
        if dry:
            draft, lout, lwall, linfer = dry.local(job["prompt"], job)
        else:
            draft, lout, lwall, linfer = call_local(args, job["prompt"])
        draft_body = render_prompt.extract_answer(draft, job["deliverable"])
        vdraft, rdraft = grade(job["config"], draft_body)
        verify_prompt = VERIFY_PREAMBLE.format(draft=draft_body.rstrip("\n")) + job["prompt"]
        if dry:
            text2, tin2, tout2, src2 = dry.hosted(verify_prompt, job, 2, idx)
        else:
            text2, tin2, tout2, src2 = call_hosted(args, verify_prompt)
        v2, r2 = grade(job["config"], text2)
        rec["draft"] = {"verdict": vdraft, "local_output_tokens": lout,
                        "local_wall_s": round(lwall, 2),
                        "local_inference_s": round(linfer, 2),
                        "recall": round(rdraft["recall"], 3),
                        "penalty_rate": round(rdraft["penalty_rate"], 3),
                        "chars": len(draft_body)}
        rec["arm2"] = {"hosted_input_tokens": tin2, "hosted_output_tokens": tout2,
                       "token_source": src2, "verdict": v2,
                       "recall": round(r2["recall"], 3),
                       "precision": round(r2["precision"], 3),
                       "penalty_rate": round(r2["penalty_rate"], 3),
                       "hallucinations": r2["hallucinations"]}
        if args.keep_drafts:
            rec["draft"]["text"] = draft_body
        items.append(rec)
    return items


def summarise_arm(items, arm):
    n = len(items)
    tin = sum(it[arm]["hosted_input_tokens"] for it in items)
    tout = sum(it[arm]["hosted_output_tokens"] for it in items)
    correct = sum(1 for it in items if it[arm]["verdict"] == "correct")
    srcs = sorted(set(it[arm]["token_source"] for it in items))
    return {"n": n, "hosted_input_tokens": tin, "hosted_output_tokens": tout,
            "hosted_total_tokens": tin + tout, "correct": correct,
            "accuracy": round(correct / n, 4) if n else None,
            "hosted_tokens_per_item": round((tin + tout) / n, 1) if n else None,
            "hosted_tokens_per_correct_item": (round((tin + tout) / correct, 1) if correct
                                               else None),
            "token_source": "+".join(srcs)}


def net(a1, a2, items):
    d_correct = a2["correct"] - a1["correct"]
    d_total = a2["hosted_total_tokens"] - a1["hosted_total_tokens"]
    per_net = (round(d_total / d_correct, 1) if d_correct > 0 else None)
    if d_correct < 0:
        reading = ("the draft made it worse: arm 2 is less correct than arm 1 and costs more "
                   "hosted tokens. On the v8 plan's own terms this kills the use.")
    elif d_correct == 0:
        reading = ("no correctness gain, and arm 2 costs %+d hosted tokens. Drafting locally does "
                   "not pay for this family at this rung." % d_total)
    elif d_total <= 0:
        reading = "arm 2 is more correct and cheaper in hosted tokens. Drafting pays outright."
    else:
        reading = ("arm 2 buys %d more correct items for %+d hosted tokens, %s tokens per net "
                   "correct item. Whether that pays is a price question, not a bench question."
                   % (d_correct, d_total, per_net))
    flips = {"fixed_by_verify": sum(1 for it in items
                                    if it["draft"]["verdict"] != "correct"
                                    and it["arm2"]["verdict"] == "correct"),
             "broken_by_draft": sum(1 for it in items
                                    if it["arm1"]["verdict"] == "correct"
                                    and it["arm2"]["verdict"] != "correct"),
             "draft_already_correct": sum(1 for it in items
                                          if it["draft"]["verdict"] == "correct")}
    return {"correct_delta": d_correct,
            "hosted_input_delta": a2["hosted_input_tokens"] - a1["hosted_input_tokens"],
            "hosted_output_delta": a2["hosted_output_tokens"] - a1["hosted_output_tokens"],
            "hosted_total_delta": d_total,
            "hosted_tokens_per_net_correct_item": per_net,
            "item_flips": flips, "reading": reading}


UNITS = {
    "hosted_input_tokens": "count of input tokens the hosted provider itself reported "
                           "(usage.prompt_tokens); see token_source",
    "hosted_output_tokens": "count of output tokens the hosted provider itself reported "
                            "(usage.completion_tokens); see token_source",
    "hosted_total_tokens": "hosted_input_tokens + hosted_output_tokens, unweighted: input and "
                           "output are not the same price and must be weighted at analysis time",
    "token_source": "provider = read from the provider's usage field; estimated = chars / 4.664; "
                    "fixture = produced by --dry-run and is not a measurement of anything",
    "local_wall_s": "seconds of wall for the local draft, which is GPU-holding time and not "
                    "money",
    "local_inference_s": "seconds of prompt_eval + eval reported by Ollama for the local draft",
    "correct": "items grading VERDICT correct under grade_seeded, the same grader the GPU cells "
               "use",
    "hosted_tokens_per_correct_item": "hosted_total_tokens / correct; None when nothing was "
                                      "correct, because a cost per zero is not a large number",
    "money": "deliberately absent: multiply the token columns by the endpoint's own rate at "
             "analysis time",
}


def run(args):
    dry = DryArms(args.dry_run_draft_quality, args.dry_run_arm1_accuracy) if args.dry_run else None
    ledger = {"cell": "item6-escalation-economics", "harness_version": "v8",
              "dry_run": bool(dry),
              "local": {"endpoint": "(dry-run)" if dry else args.local_endpoint,
                        "model": args.local_model},
              "hosted": {"endpoint": "(dry-run)" if dry else args.hosted_endpoint,
                         "model": args.hosted_model,
                         "api_key_env": args.hosted_api_key_env or None,
                         "note": args.hosted_note},
              "n_per_family": args.n, "units": UNITS, "families": {}}
    for name in args.families.split(","):
        job = load_family(name, args.n)
        items = run_family(args, job, dry)
        a1, a2 = summarise_arm(items, "arm1"), summarise_arm(items, "arm2")
        ledger["families"][name] = {
            "rung": job["config"].get("rung"),
            "prompt_chars": len(job["prompt"]),
            "arms": {"hosted_only": a1, "local_draft_hosted_verify": a2},
            "local_draft": {"correct": sum(1 for it in items
                                           if it["draft"]["verdict"] == "correct"),
                            "wall_s": round(sum(it["draft"]["local_wall_s"] for it in items), 2),
                            "inference_s": round(sum(it["draft"]["local_inference_s"]
                                                     for it in items), 2),
                            "output_tokens": sum(it["draft"]["local_output_tokens"]
                                                 for it in items)},
            "net": net(a1, a2, items),
            "items": items}
    return ledger


def check_ledger(ledger):
    """The dry run's purpose: prove every figure in the ledger follows from the item rows."""
    checks = []

    def chk(name, got, want):
        checks.append((name, got, want, got == want))

    for fam, f in ledger["families"].items():
        items = f["items"]
        a1 = f["arms"]["hosted_only"]
        a2 = f["arms"]["local_draft_hosted_verify"]
        chk("%s: arm1 input tokens re-add" % fam, a1["hosted_input_tokens"],
            sum(it["arm1"]["hosted_input_tokens"] for it in items))
        chk("%s: arm2 input tokens re-add" % fam, a2["hosted_input_tokens"],
            sum(it["arm2"]["hosted_input_tokens"] for it in items))
        chk("%s: arm2 hosted input exceeds arm1 (the draft is in it)" % fam,
            a2["hosted_input_tokens"] > a1["hosted_input_tokens"], True)
        chk("%s: total equals input plus output, arm1" % fam, a1["hosted_total_tokens"],
            a1["hosted_input_tokens"] + a1["hosted_output_tokens"])
        chk("%s: net correctness is a paired difference" % fam, f["net"]["correct_delta"],
            a2["correct"] - a1["correct"])
        chk("%s: net hosted delta is a difference of totals" % fam,
            f["net"]["hosted_total_delta"],
            a2["hosted_total_tokens"] - a1["hosted_total_tokens"])
        chk("%s: tokens per correct item, arm1" % fam, a1["hosted_tokens_per_correct_item"],
            round(a1["hosted_total_tokens"] / a1["correct"], 1) if a1["correct"] else None)
        chk("%s: token source is named on every row" % fam,
            all(it["arm1"]["token_source"] and it["arm2"]["token_source"] for it in items), True)
        chk("%s: the local arm's cost is time, not tokens billed" % fam,
            "local_wall_s" in items[0]["draft"], True)
        chk("%s: cost per net correct item is None when there is no gain" % fam,
            f["net"]["hosted_tokens_per_net_correct_item"] is None,
            f["net"]["correct_delta"] <= 0)
    chk("no key value anywhere in the ledger",
        "Authorization" not in json.dumps(ledger) and "Bearer" not in json.dumps(ledger), True)
    bad = 0
    for name, got, want, ok in checks:
        print("%-4s %-68s got=%-10s want=%s" % ("ok" if ok else "FAIL", name, got, want))
        if not ok:
            bad += 1
    print("%d/%d ledger checks passed" % (len(checks) - bad, len(checks)))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local-endpoint")
    ap.add_argument("--local-model", default="q27-IQ2_M-96k")
    ap.add_argument("--hosted-endpoint", help="OpenAI-compatible base URL ending in /v1")
    ap.add_argument("--hosted-model", default="(unset)")
    ap.add_argument("--hosted-api-key-env",
                    help="NAME of the environment variable holding the key; never the key")
    ap.add_argument("--hosted-note", default="",
                    help="what the hosted arm actually is, recorded verbatim in the ledger")
    ap.add_argument("--families", default=",".join(DEFAULT_FAMILIES))
    ap.add_argument("--n", type=int, default=10, help="items per family; the plan's floor is 10")
    ap.add_argument("--keep-alive", default="5m")
    ap.add_argument("--num-predict", type=int, default=1200)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--keep-drafts", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--dry-run-draft-quality", choices=("good", "bad", "rescue"), default="bad")
    ap.add_argument("--dry-run-arm1-accuracy", type=float, default=0.8)
    args = ap.parse_args()
    if not args.dry_run and not (args.local_endpoint and args.hosted_endpoint):
        ap.error("--local-endpoint and --hosted-endpoint are required unless --dry-run")
    ledger = run(args)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(ledger, fh, indent=1)
        print("wrote %s" % args.out)
    slim = dict((k, v) for k, v in ledger.items() if k != "families")
    slim["families"] = dict((k, dict((kk, vv) for kk, vv in v.items() if kk != "items"))
                            for k, v in ledger["families"].items())
    print(json.dumps(slim, indent=1))
    if args.dry_run:
        print("")
        return 1 if check_ledger(ledger) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
