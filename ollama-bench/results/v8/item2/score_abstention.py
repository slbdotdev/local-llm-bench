#!/usr/bin/env python3
"""v8 item 4: score a trial on the abstention axis.

    python3 score_abstention.py --slot slots/agg-80k-abst --answer ref/answer.json
    python3 score_abstention.py --slot slots/agg-80k-abst --answer a.json b.json --k 2
    python3 score_abstention.py --slot slots/agg-80k-abst --itemcode CCCCCAAAA

The plan's rule (section 3, item 4): score `correct - k*confidently_wrong` with abstention
neutral, and report abstention precision and recall separately. `k` is a parameter and
defaults to 1.

    correct              an answerable item answered with the right value
    confidently_wrong    a definite value that is wrong -- on an answerable item because
                         the value is wrong, on an unanswerable item because there is no
                         value to give. This is the column v7 measured at 0.031
                         [0.010, 0.086] and the whole reason for "never the last reader".
    abstention           neutral. It earns nothing on an answerable item and costs nothing
                         on an unanswerable one; what it earns is reported separately, as
                         abstention precision and recall.

    raw   = correct - k * confidently_wrong
    score = max(0, raw) / answerable_items

The clamp at zero is what makes the plan's two-directional instrument proof exactly
satisfiable: a perfect answer scores 1.0 and an answer that takes every decoy and answers
every unanswerable item confidently scores 0. `raw_score` is reported unclamped beside it,
because the clamp throws away how wrong a very wrong answer was.

Classification is never re-implemented here. The slot's own `test.py` is the one
classifier: this runs it against the answer in a throwaway sandbox and reads the `ITEMCODE`
line it prints. `--itemcode` takes that line directly, which is how a phase-3 pass scores
from `results.json` without keeping every sandbox.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

CODE_MEANING = {"C": "correct", "W": "confidently_wrong", "A": "abstained",
                "M": "no answer"}


def itemcode_for(slot, answer_path):
    box = tempfile.mkdtemp(prefix="v8i4_")
    try:
        shutil.copytree(os.path.join(slot, "seed"), box, dirs_exist_ok=True)
        shutil.copy(answer_path, os.path.join(box, "answer.json"))
        shutil.copy(os.path.join(slot, "test.py"), os.path.join(box, "_hidden_test.py"))
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
                   PYTHONDONTWRITEBYTECODE="1")
        p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=box, env=env,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=70)
        code = verdict = None
        for line in p.stdout.splitlines():
            if line.startswith("ITEMCODE "):
                code = line.split(None, 1)[1].strip()
            elif line.startswith("VERDICT "):
                verdict = line.split(None, 1)[1].strip()
        if code is None:
            raise SystemExit("grader printed no ITEMCODE for %s:\n%s"
                             % (answer_path, p.stdout[-800:]))
        return code, verdict
    finally:
        shutil.rmtree(box, ignore_errors=True)


def kinds_for(slot):
    with open(os.path.join(slot, "ref", "items.json"), encoding="utf-8") as fh:
        items = json.load(fh)
    return [(it["key"], it["kind"]) for it in items]


def score(kinds, code, k):
    assert len(kinds) == len(code), \
        "item code %r has %d characters for %d items" % (code, len(code), len(kinds))
    per_item, correct, wrong, abst_ans, abst_un, none_ans = [], 0, 0, 0, 0, 0
    n_ans = sum(1 for _key, kind in kinds if kind == "answerable")
    n_un = len(kinds) - n_ans
    for (key, kind), c in zip(kinds, code):
        per_item.append({"key": key, "kind": kind, "code": c,
                         "behaviour": CODE_MEANING.get(c, "?")})
        if c == "W":
            wrong += 1
        elif c == "C" and kind == "answerable":
            correct += 1
        elif c == "A":
            if kind == "answerable":
                abst_ans += 1
            else:
                abst_un += 1
        elif c == "M":
            none_ans += 1
    raw = correct - k * wrong
    abstentions = abst_ans + abst_un
    return {
        "k": k,
        "items": len(kinds),
        "answerable_items": n_ans,
        "unanswerable_items": n_un,
        "correct": correct,
        "confidently_wrong": wrong,
        "abstained_on_answerable": abst_ans,
        "abstained_on_unanswerable": abst_un,
        "no_answer": none_ans,
        "raw_score": raw,
        "score": round(max(0, raw) / float(n_ans), 6) if n_ans else None,
        "abstention_recall": round(abst_un / float(n_un), 6) if n_un else None,
        "abstention_precision": (round(abst_un / float(abstentions), 6)
                                 if abstentions else None),
        "item_code": code,
        "item_kinds": "".join({"answerable": "a", "absent": "x",
                               "underdetermined": "u"}[kd] for _k, kd in kinds),
        "per_item": per_item,
    }


def pool(rows, kinds, k):
    n_ans = sum(1 for _key, kind in kinds if kind == "answerable")
    n_un = len(kinds) - n_ans
    t = {f: sum(r[f] for r in rows) for f in
         ("correct", "confidently_wrong", "abstained_on_answerable",
          "abstained_on_unanswerable", "no_answer")}
    trials = len(rows)
    raw = t["correct"] - k * t["confidently_wrong"]
    abstentions = t["abstained_on_answerable"] + t["abstained_on_unanswerable"]
    return {
        "trials": trials, "k": k,
        "answerable_items_total": n_ans * trials,
        "unanswerable_items_total": n_un * trials,
        "correct": t["correct"], "confidently_wrong": t["confidently_wrong"],
        "abstained_on_answerable": t["abstained_on_answerable"],
        "abstained_on_unanswerable": t["abstained_on_unanswerable"],
        "no_answer": t["no_answer"],
        "raw_score": raw,
        "score": round(max(0, raw) / float(n_ans * trials), 6) if n_ans * trials else None,
        "abstention_recall": (round(t["abstained_on_unanswerable"] / float(n_un * trials), 6)
                              if n_un * trials else None),
        "abstention_precision": (round(t["abstained_on_unanswerable"] / float(abstentions), 6)
                                 if abstentions else None),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True, help="a slot directory under item2/slots/")
    ap.add_argument("--answer", nargs="*", default=[],
                    help="answer.json file(s); relative paths resolve inside the slot")
    ap.add_argument("--itemcode", nargs="*", default=[],
                    help="ITEMCODE string(s) as printed by the slot's test.py")
    ap.add_argument("--k", type=float, default=1.0,
                    help="the penalty on a confidently wrong answer (default 1)")
    ap.add_argument("--quiet", action="store_true", help="print the pooled row only")
    a = ap.parse_args()

    slot = os.path.abspath(a.slot)
    kinds = kinds_for(slot)
    rows = []
    for path in a.answer:
        p = path if os.path.isabs(path) or os.path.exists(path) else os.path.join(slot, path)
        if not os.path.exists(p):
            p = os.path.join(slot, path)
        code, verdict = itemcode_for(slot, p)
        row = score(kinds, code, a.k)
        row["answer"] = os.path.relpath(p, slot)
        row["verdict"] = verdict
        rows.append(row)
    for code in a.itemcode:
        row = score(kinds, re.sub(r"\s+", "", code), a.k)
        row["answer"] = "(itemcode)"
        rows.append(row)
    if not rows:
        raise SystemExit("nothing to score: pass --answer or --itemcode")

    out = {"slot": os.path.basename(slot), "k": a.k,
           "rows": [] if a.quiet else rows,
           "pooled": pool(rows, kinds, a.k)}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
