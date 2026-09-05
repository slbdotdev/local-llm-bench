"""Render results/v6/placement.json into placement.md (plan section 5, phase 0 fields)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "placement.json"), encoding="utf-8"))

def g(r, k, fmt="%s", dash="-"):
    v = r.get(k)
    return dash if v is None else fmt % v

rows = ["# v6 phase 0 — placement",
        "",
        "*Rendered from `placement.json`. Resident GB is `/api/ps` `size` / 2^30 (D6-2), the same",
        "field v5 measured, against the ~14.2 GB fair-weather line. `nvidia-smi` peak is recorded",
        "and never used for the verdict (it reads ~1.5 GB high). Speed gate (plan section 4): gen",
        "tok/s at a ~90% fill >= 35 passes, < 20 is spill, between is marginal.*",
        "",
        "| quant | ctx | resident GB | %GPU | smi peak MiB | load s | gen tok/s empty | gen tok/s @fill | prompt tok/s @fill | TTFT s | fill tok | verdict |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
for r in data:
    rows.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | **%s** |" % (
        r["quant"], "%dk" % (r["num_ctx"] // 1024),
        g(r, "resident_gb", "%.2f"), g(r, "pct_gpu", "%s%%"),
        g(r, "nvidia_smi_peak_mib", "%d"), g(r, "load_s", "%.1f"),
        g(r, "gen_tps_empty", "%.1f"), g(r, "gen_tps_fill", "%.1f"),
        g(r, "prompt_tps_fill", "%.0f"), g(r, "ttft_fill_s", "%.0f"),
        g(r, "fill_prompt_tokens", "%d"), r.get("verdict", "-")))

rows += ["", "## Max viable context per quant", "",
         "| quant | max viable ctx | resident there | gen tok/s there | first rung rejected |",
         "|---|---:|---:|---:|---|"]
latest = {}
for r in data:
    latest[(r["quant"], r["num_ctx"])] = r   # a re-measured cell supersedes the earlier one
byq = {}
for r in latest.values():
    byq.setdefault(r["quant"], []).append(r)
for q, rs in byq.items():
    ok = [r for r in rs if r.get("verdict") in ("pass", "marginal")]
    bad = [r for r in rs if r.get("verdict") not in ("pass", "marginal")]
    best = max(ok, key=lambda r: r["num_ctx"]) if ok else None
    first_bad = min(bad, key=lambda r: r["num_ctx"]) if bad else None
    rows.append("| %s | %s | %s | %s | %s |" % (
        q,
        "%dk" % (best["num_ctx"] // 1024) if best else "**none**",
        g(best, "resident_gb", "%.2f") if best else "-",
        g(best, "gen_tps_fill", "%.1f") if best else "-",
        ("%dk (%s)" % (first_bad["num_ctx"] // 1024, first_bad.get("verdict"))) if first_bad else "-"))

open(os.path.join(HERE, "placement.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("\n".join(rows))
