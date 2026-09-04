"""Write measured achieved fill into a row's padding.json, replacing char-based estimates.

Characters written to disk are not context fill. The plan's rule is that achieved fill is
taken from the model's own reported prompt token count, so any estimate that could be
mistaken for a measurement is removed rather than left beside the real number.
"""
import json, os, sys, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_fill import peak_prompt_tokens

row, outdir, needle = sys.argv[1], sys.argv[2], sys.argv[3]
pj = os.path.join(row, "padding.json")
data = json.load(open(pj, encoding="utf-8"))
peaks = {}
for f in glob.glob(os.path.join(outdir, "*.output")):
    try:
        head = open(f, encoding="utf-8", errors="replace").read(400000)
    except OSError:
        continue
    if needle not in head:
        continue
    m = re.search(re.escape(needle) + r"/(\w+)", head)
    if not m:
        continue
    pk = peak_prompt_tokens(f)
    if pk > peaks.get(m.group(1), 0):
        peaks[m.group(1)] = pk
for task, v in data.items():
    v.pop("est_tokens_after", None)          # a chars/5.95 estimate, not a measurement
    v.pop("material_chars_before", None)
    v.pop("material_chars_after", None)
    v["achieved_fill_prompt_tokens"] = peaks.get(task)
    v["achieved_fill_source"] = ("model-reported prompt tokens (input + cache_read + "
                                 "cache_creation), peak across the run's assistant messages")
    v["note"] = ("Characters on disk are NOT context fill. Filler only enters the context if "
                 "the model reads it, so achieved_fill_prompt_tokens is the only fill number "
                 "here that is a measurement.")
json.dump(data, open(pj, "w", encoding="utf-8"), indent=1)
print(f"{row}: achieved fill written for {sum(1 for v in data.values() if v['achieved_fill_prompt_tokens'])}/{len(data)} tasks")
for t in sorted(data):
    print(f"  {t}: {data[t]['achieved_fill_prompt_tokens']}")
