"""Measure TTFT and generation tok/s per ZDR provider for qwen/qwen3.8-27b on OpenRouter.

Streams chat/completions directly with provider.only pinned to one slug at a time.
Key is read from OPENROUTER_API_KEY and never printed.
"""
import json, os, ssl, sys, time, urllib.request

MODEL = "qwen/qwen3.8-27b"
URL = "https://openrouter.ai/api/v1/chat/completions"
SLUGS = ["parasail", "akashml", "ionstream", "reka", "coreweave", "io-net", "venice", "phala", "novita"]
PROMPT = ("Write a clear, self-contained explanation of how a hash table works: "
          "the hash function, bucket array, collision handling by chaining versus open addressing, "
          "load factor, and amortized resizing. Aim for about 300 words of prose, no code, no lists.")
REPEATS = 3
MAX_TOKENS = 400
KEY = os.environ.get("OPENROUTER_API_KEY")
if not KEY:
    sys.exit("OPENROUTER_API_KEY not set")


def one(slug):
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.2,
        "stream": True,
        "stream_options": {"include_usage": True},
        "reasoning": {"effort": "low"},
        "usage": {"include": True},
        "provider": {"only": [slug], "zdr": True, "data_collection": "deny", "allow_fallbacks": False},
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + KEY,
                                          "Accept": "text/event-stream"})
    t0 = time.time()
    ttft = None
    chunks = 0
    text = []
    usage = None
    served_by = None
    err = None
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            for raw in r:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    ev = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if ev.get("error"):
                    err = str(ev["error"])[:300]
                    break
                served_by = ev.get("provider") or served_by
                if ev.get("usage"):
                    usage = ev["usage"]
                for ch in ev.get("choices") or []:
                    d = ch.get("delta") or {}
                    piece = d.get("content") or d.get("reasoning") or ""
                    if piece:
                        if ttft is None:
                            ttft = time.time() - t0
                        chunks += 1
                        text.append(piece)
    except urllib.error.HTTPError as e:
        err = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}"
    except Exception as e:
        err = f"{type(e).__name__}: {str(e)[:300]}"
    total = time.time() - t0
    out_tok = (usage or {}).get("completion_tokens")
    gen_tok = out_tok if out_tok else chunks
    gen_s = total - (ttft or 0)
    return {"slug": slug, "ttft_s": round(ttft, 3) if ttft else None,
            "total_s": round(total, 2), "out_tokens": out_tok, "chunks": chunks,
            "gen_tps": round(gen_tok / gen_s, 1) if gen_s > 0 and gen_tok else None,
            "provider": served_by, "chars": len("".join(text)), "error": err,
            "cost": (usage or {}).get("cost")}


def main():
    out = []
    for slug in SLUGS:
        for i in range(REPEATS):
            r = one(slug)
            r["rep"] = i
            out.append(r)
            print(f"{slug:12s} #{i} ttft={r['ttft_s']} total={r['total_s']}s out={r['out_tokens']} "
                  f"tps={r['gen_tps']} served={r['provider']}" + (f" ERR={r['error'][:120]}" if r["error"] else ""),
                  flush=True)
            if r["error"]:
                break
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "or_provider_tps.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
