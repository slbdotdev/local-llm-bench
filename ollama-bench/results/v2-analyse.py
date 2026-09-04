"""Analyse v2-low vs v2-medium: per-task pass counts, wall, tokens, significance, cost."""
import json, os, sys, math, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
def load(tag):
    p = os.path.join(HERE, tag + ".json")
    if not os.path.exists(p): return {}
    d = json.load(open(p, encoding="utf-8"))
    out = {}
    for model, r in d.items():
        for x in r["runs"]:
            # a timed-out run counts as a FAIL even if the grader found a usable artefact
            if x.get("timed_out"):
                x = dict(x, pass_orig=x["pass"]); x["pass"] = False
            out.setdefault(x["task"], []).append(x)
    return out
IN_PRICE, OUT_PRICE = 0.425/1e6, 2.55/1e6
def cost(runs): return sum(x["in_tokens"]*IN_PRICE + x["out_tokens"]*OUT_PRICE for x in runs)
def fisher(a,b,c,d):
    """two-sided Fisher exact on [[a,b],[c,d]]"""
    from math import comb
    n = a+b+c+d; r1, r2, c1 = a+b, c+d, a+c
    def p(x): return comb(r1,x)*comb(r2,c1-x)/comb(n,c1)
    p0 = p(a); tot = 0.0
    for x in range(max(0,c1-r2), min(r1,c1)+1):
        px = p(x)
        if px <= p0 + 1e-12: tot += px
    return min(1.0, tot)
lo, me = load("v2-low"), load("v2-medium")
tasks = sorted(set(lo) | set(me))
print(f"{'task':18s} {'low p/n':>8s} {'med p/n':>8s} {'low wall':>9s} {'med wall':>9s} {'low out':>8s} {'med out':>8s}")
LP=LN=MP=MN=0
for t in tasks:
    L, M = lo.get(t, []), me.get(t, [])
    lp, mp = sum(x["pass"] for x in L), sum(x["pass"] for x in M)
    LP+=lp; LN+=len(L); MP+=mp; MN+=len(M)
    fw = lambda R: statistics.mean(x["wall_s"] for x in R) if R else float('nan')
    fo = lambda R: statistics.mean(x["out_tokens"] for x in R) if R else float('nan')
    print(f"{t:18s} {lp}/{len(L):>6} {mp}/{len(M):>6} {fw(L):9.0f} {fw(M):9.0f} {fo(L):8.0f} {fo(M):8.0f}")
print(f"\noverall low {LP}/{LN}  medium {MP}/{MN}")
if LN and MN:
    print("Fisher exact (two-sided) on aggregated pass counts: p =",
          round(fisher(LP, LN-LP, MP, MN-MP), 5))
# paired sign test across tasks on pass RATE
from math import comb
pos = neg = 0
for t in tasks:
    L, M = lo.get(t, []), me.get(t, [])
    if not L or not M: continue
    rl, rm = sum(x["pass"] for x in L)/len(L), sum(x["pass"] for x in M)/len(M)
    if rm > rl: pos += 1
    elif rm < rl: neg += 1
n = pos + neg
if n:
    p2 = sum(comb(n, k) for k in range(0, min(pos, neg) + 1)) / 2**n * 2
    print(f"paired sign test across tasks: medium better on {pos}, low better on {neg}, ties {len(tasks)-n}; two-sided p = {min(1.0, p2):.4f}")

allruns = [x for v in lo.values() for x in v] + [x for v in me.values() for x in v]
print(f"\nruns={len(allruns)} est cost (upper bound) = ${cost(allruns):.2f}")
for tag in ("v2-glm-low","v2-glm-medium"):
    p=os.path.join(HERE,tag+".json")
    if os.path.exists(p):
        d=json.load(open(p,encoding="utf-8")); rs=[x for r in d.values() for x in r["runs"]]
        print(f"{tag}: {sum(x['pass'] for x in rs)}/{len(rs)} pass, mean wall {statistics.mean(x['wall_s'] for x in rs):.0f}s, "
              f"est cost ${sum(x['in_tokens']*0.075/1e6 + x['out_tokens']*0.25/1e6 for x in rs):.3f}")
