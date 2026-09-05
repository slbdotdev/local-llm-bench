"""Emit the per-band tables and the summary row for the Luna reference arm page."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = HERE if os.path.basename(HERE) == "gate-luna" else os.path.join(HERE, "gate-luna")
TASKS = ["g01", "g02", "g03", "g04", "t01", "t02", "t03", "t04"]


def note(band, task):
    p = os.path.join(GATE, band, "trial-0", f"{task}.final.txt")
    if not os.path.exists(p):
        return "(no final message)"
    txt = open(p, encoding="utf-8", errors="replace").read().strip()
    txt = re.sub(r"```.*?```", " ", txt, flags=re.S)
    txt = re.sub(r"\[([^\]\n]+)\]\([^)\n]*\)", r"\1", txt)   # md links -> their text
    txt = txt.replace(os.path.join(GATE, band, "trial-0") + "/", "")
    for ln in txt.splitlines():
        s = ln.strip().lstrip("-*# ").strip()
        s = re.sub(r"\s+", " ", s)
        s = re.sub(r"[*`_]", "", s)
        s = s.rstrip(":")
        if len(s) > 15:
            if len(s) < 40:  # a terse answer line: carry the next line too
                rest = [re.sub(r"\s+", " ", x.strip()) for x in
                        txt.splitlines()[txt.splitlines().index(ln) + 1:]]
                rest = [x for x in rest if x]
                if rest:
                    sep = " " if s.endswith((".", "!", "?")) else "; "
                    s = s + sep + re.sub(r"[*`_]", "", rest[0])
            return s[:150] + ("..." if len(s) > 150 else "")
    return (re.sub(r"\s+", " ", txt)[:150] or "(empty)")


def band_table(band):
    p = os.path.join(GATE, band, "trial-0", "results.json")
    d = json.load(open(p, encoding="utf-8"))
    lines = ["| task | pass | score | verdict | wall s | tokens used | codex rc | timed out | note |",
             "|---|---|---|---|---:|---:|---:|---|---|"]
    tw = tt = np_ = nto = 0
    for t in TASKS:
        r = d[t]
        tw += r.get("wall_s") or 0
        tt += r.get("tokens_used") or 0
        np_ += 1 if r.get("pass") else 0
        nto += 1 if r.get("timed_out") else 0
        lines.append("| {} | {} | {} | {} | {:.1f} | {} | {} | {} | {} |".format(
            t, "PASS" if r.get("pass") else "FAIL", r.get("score"), r.get("verdict"),
            r.get("wall_s") or 0, r.get("tokens_used"), r.get("codex_rc"),
            "yes" if r.get("timed_out") else "no", note(band, t)))
    lines.append("| **total (8 tasks)** | **{}/8** | | | **{:.1f}** | **{}** | | **{}** | |".format(
        np_, tw, tt, nto))
    meta = d.get("_meta", {})
    return "\n".join(lines), {"pass": np_, "wall": tw, "tokens": tt, "timeouts": nto,
                              "rate": meta.get("rate_limit_events", []),
                              "final_conc": meta.get("final_max_concurrency")}


if __name__ == "__main__":
    out = {}
    for b in ("tiny", "large"):
        tbl, s = band_table(b)
        out[b] = s
        print(f"\n## {b} band\n\n{tbl}\n")
    print("\n### summary\n")
    print(json.dumps(out, indent=1))
