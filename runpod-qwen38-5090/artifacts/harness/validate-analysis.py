#!/usr/bin/env python3
"""Recompute RESULT.md's 8K MTP median decode from stream-mtp3-8k.jsonl.

Validates the analysis half of stream-measure.py against the
authoritative round-one data: decode = (tokens-1)/(total-ttft), median
over rows. Must print 184.32 to pass.
"""
import json
import statistics
import sys

path = "/home/slb/runpod-qwen38-5090/results/armb-w3/stream-mtp3-8k.jsonl"
rows = []
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        toks = d["completion_tokens"]
        total = d["total_s"]
        ttft = d["ttft_s"]
        rows.append((toks - 1) / (total - ttft))

med = statistics.median(rows)
print(f"rows={len(rows)} median_decode={med:.2f} min={min(rows):.2f} max={max(rows):.2f}")
print("PASS" if abs(med - 184.32) < 0.5 else "FAIL: expected 184.32")
sys.exit(0 if abs(med - 184.32) < 0.5 else 1)
