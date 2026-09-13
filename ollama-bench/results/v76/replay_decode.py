#!/usr/bin/env python3
"""Is slbh's decode rate a function of the tools array it sends?

The v7.6 baseline decomposition put the whole slbh-vs-pi gap in generation: 4,656 s of the
5,199 s wall was streaming, prefill was 217 s against 2.23M of 2.44M prompt tokens reported
cached, and tool execution was 43 s. 97,277 completion tokens over 4,656 s is 20.9 tokens/s,
where pi produced 105,893 output tokens inside 1,912 s of total wall on the same model, the
same GPU and the same host.

slbh sends nineteen tool schemas on every request and pi sends four. This replays ONE real
slbh request three times against the same server -- as sent, with no tools, and with four --
and reports completion tokens over elapsed for each. Same messages, same effort, same model;
only the tools array differs.

slbh records the exact bytes it sent in each `inference_request` event, so this is a replay
and not a reconstruction. `stream` is forced to false because the question is the total rate,
and a non-streaming call reports `usage` in the same response.

Usage:
  python3 replay_decode.py --transcript PATH [--round N] [--endpoint URL]
"""
import argparse
import json
import time
import urllib.request

PI_SHAPED = ["quick_bash", "read_file", "edit_file", "write_file"]


def payloads(path, wanted_round):
    """Every request body in a transcript, in order."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("kind") != "inference_request":
                continue
            body = (ev.get("metadata") or {}).get("payload")
            if body:
                out.append(body)
    if not out:
        raise SystemExit(f"no inference_request payloads in {path}")
    if wanted_round is None:
        wanted_round = len(out) // 2          # mid-session: a real, loaded context
    return out[min(wanted_round, len(out) - 1)]


def post(endpoint, body, timeout=900):
    data = json.dumps(body).encode()
    req = urllib.request.Request(endpoint, data=data,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode())
    return time.time() - t0, payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--round", type=int, default=None)
    ap.add_argument("--endpoint",
                    default="http://fractal.wyvern-temperature.ts.net:11434/v1/chat/completions")
    a = ap.parse_args()

    base = payloads(a.transcript, a.round)
    base = dict(base, stream=False)
    base.pop("stream_options", None)
    tools = base.get("tools") or []
    print(f"replaying {a.transcript}")
    print(f"  model={base.get('model')} effort={base.get('reasoning_effort')} "
          f"messages={len(base.get('messages') or [])} tools={len(tools)}")

    variants = [("as sent (%d tools)" % len(tools), base)]
    no_tools = {k: v for k, v in base.items() if k != "tools"}
    variants.append(("no tools array", no_tools))
    four = [t for t in tools if (t.get("function") or {}).get("name") in PI_SHAPED]
    variants.append(("pi-shaped (%d tools)" % len(four), dict(base, tools=four)))

    print()
    print(f"{'variant':26s} {'elapsed s':>10s} {'prompt tok':>11s} {'completion':>11s} {'tok/s':>8s}")
    for name, body in variants:
        try:
            elapsed, resp = post(a.endpoint, body)
        except Exception as exc:                                  # noqa: BLE001
            print(f"{name:26s} FAILED: {exc}")
            continue
        usage = resp.get("usage") or {}
        comp = usage.get("completion_tokens") or 0
        prompt = usage.get("prompt_tokens") or 0
        rate = comp / elapsed if elapsed else 0
        print(f"{name:26s} {elapsed:10.1f} {prompt:11d} {comp:11d} {rate:8.1f}")


if __name__ == "__main__":
    main()
