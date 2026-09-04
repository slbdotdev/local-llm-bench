#!/usr/bin/env bash
# T2 sweep: KV cache precision vs long-context recall, on q27-Q3_K_S.
# Pass A carries an f16 ground truth (it only fits at 8k); passes B and C rank the
# three configs that actually fit at a working context, with q8_0/q8_0 as reference.
set -u
cd "$(dirname "$0")" || exit 1
M='C:\Users\slb\.ollama\models\blobs\sha256-ba0c5dee3026dccf7126b90f1fbb10f2916d540aad470eb0c03da68734dbe10a'

echo "########## PASS A: 8k, with f16 ground truth ##########"
python kvquality.py --model "$M" --ctx 8192 --records 140 --needles 24 \
    --configs f16:f16,q8_0:q8_0,q4_0:q4_0,q8_0:q4_0 --out ./kv-8k-Q3_K_S.json

echo "########## PASS B: 16k ##########"
python kvquality.py --model "$M" --ctx 16384 --records 300 --needles 24 \
    --configs q8_0:q8_0,q4_0:q4_0,q8_0:q4_0 --out ./kv-16k-Q3_K_S.json

echo "########## PASS C: 24k ##########"
python kvquality.py --model "$M" --ctx 24576 --records 460 --needles 24 \
    --configs q8_0:q8_0,q4_0:q4_0,q8_0:q4_0 --out ./kv-24k-Q3_K_S.json

echo "########## done ##########"
