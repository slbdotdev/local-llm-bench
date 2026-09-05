"""The v6 placement verdict, in one place.

Both the instrument (`place.py`, at record time) and the two renderers re-derive the verdict
from a record's raw measured fields, so a rule added later applies to records taken earlier
without ever rewriting `placement.json` -- which plan section 6 requires be appended to and
never rewritten.

Three gates, all from measurements on this card:

1. **Resident** under the ~14.2 GB fair-weather line, from `/api/ps` size / 2^30 (D6-2).
2. **Generation** at a ~90% fill: >= 35 tok/s passes, < 20 tok/s is spill (plan section 4).
3. **Prefill** at the same fill: >= 500 tok/s is clean, < 200 tok/s is spill (D6-19). The plan
   records prompt tok/s but gates only on generation, and Q3_K_S at 48k proved that is not
   enough -- it passed the generation gate at 41.3 tok/s and 100% GPU while prefilling at
   76.4 tok/s, a 571-second wait before the first token of a 44k-token prompt.
"""
LINE_GB = 14.2
GEN_PASS, GEN_SPILL = 35.0, 20.0
PRE_CLEAN, PRE_SPILL = 500.0, 200.0


def verdict_of(rec):
    """Return (verdict, reason) for a placement record."""
    if rec.get("verdict") in ("load_failed",):
        return rec["verdict"], rec.get("error", "")[:80]
    g, p = rec.get("gen_tps_fill"), rec.get("prompt_tps_fill")
    if g is None:
        return "spill", rec.get("fill_error", "no generation at fill")[:80]
    res = rec.get("resident_gb") or 0
    over = res >= LINE_GB
    if p is not None and p < PRE_SPILL:
        return "spill", "prefill %.0f tok/s (TTFT %.0fs)" % (p, rec.get("ttft_fill_s") or 0)
    if g < GEN_SPILL:
        return "spill", "gen %.1f tok/s" % g
    reasons = []
    if g < GEN_PASS:
        reasons.append("gen %.1f tok/s" % g)
    if over:
        reasons.append("resident %.2f GB over the line" % res)
    if p is not None and p < PRE_CLEAN:
        reasons.append("prefill %.0f tok/s" % p)
    if reasons:
        return "marginal", "; ".join(reasons)
    return "pass", ""
