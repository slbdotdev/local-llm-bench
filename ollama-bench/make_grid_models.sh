#!/usr/bin/env bash
# Build one Ollama model tag per grid cell for the v5 quality-versus-context grid.
#
# WHY THIS EXISTS. pibench.py drives pi, which talks to Ollama over the OpenAI-compatible
# API and passes no options; so num_ctx and num_gpu can only reach the server if they are
# baked into the model tag (this is what make_model.sh's comment means). The plan's grid is
# fifteen (quant, context) cells at num_gpu 66 forced, and only two such tags existed --
# q27-Q3_K_S-64k and q27-IQ3_M-64k. Without the other thirteen, a "48k cell" would silently
# run at whatever num_ctx the base tag baked (32768) and the context axis would measure
# nothing.
#
# `ollama create` here is a metadata-only operation: every tag reuses an existing blob that
# is already on disk, so this costs no download and essentially no disk.
#
# num_gpu 66 forces full layer offload. results/gpu-tune/summary.md measured Ollama's
# scheduler parking 2-7 layers on the CPU while leaving ~600 MiB of VRAM unused, costing
# 50-75% of generation throughput. Forcing it is one of the two levers that reach 64k.
set -euo pipefail
cd "$(dirname "$0")" || exit 1

OLLAMA="${OLLAMA:-/mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe}"

# quant -> blob path, read from the existing base tags on 2026-09-04
declare -A BLOB=(
  [Q2_K_L]='C:\Users\slb\.ollama\models\blobs\sha256-f1447ffd77dd79395208576ac5b122c8a312e652b62c92956d88ae440c294039'
  [Q3_K_S]='C:\Users\slb\.ollama\models\blobs\sha256-ba0c5dee3026dccf7126b90f1fbb10f2916d540aad470eb0c03da68734dbe10a'
  [Q3_K_M]='C:\Users\slb\.ollama\models\blobs\sha256-eebd04d766a6de4778ef8126295d2c30a56472b0f6310730147ae1999edeac6d'
  [IQ3_M]='C:\Users\slb\.ollama\models\blobs\sha256-dd6cccbaed553b08e958bbd759e5f9d8985d782ea016c5eaf3cd770e64615851'
)

# The capacity map from results/gpu-tune/summary.md. Q3_K_M stops at 48k; Q3_K_L is
# excluded entirely by the plan's 32k floor. Fifteen cells.
#
# WHY THIS IS A FLAT LIST AND NOT `echo "$CELLS" | while read q ctxs`. It was that,
# and on 2026-09-04 it silently built only the FIRST quant family -- four of fifteen
# tags -- then exited 0 with no error, twice in a row, stopping at the family
# boundary before printing the next tag's name. Exit 0 with a third of the work done
# is the worst shape a precondition script can fail in: `schedule.md` recorded the
# tags as built on the strength of it. The same creates in a flat loop completed
# fine. Do not reintroduce the pipeline form to make this tidier.
CELLS="Q2_K_L:24576 Q2_K_L:32768 Q2_K_L:49152 Q2_K_L:65536
Q3_K_S:24576 Q3_K_S:32768 Q3_K_S:49152 Q3_K_S:65536
IQ3_M:24576 IQ3_M:32768 IQ3_M:49152 IQ3_M:65536
Q3_K_M:24576 Q3_K_M:32768 Q3_K_M:49152"

made=0
failed=0
for spec in $CELLS; do
    q="${spec%%:*}"
    ctx="${spec##*:}"
    k=$((ctx / 1024))
    tag="q27-${q}-${k}k"
    # The Modelfile MUST live in the Windows-visible tree and be passed as a RELATIVE path.
    # Windows ollama.exe cannot see a WSL /tmp path: `ollama create -f /tmp/xxx` fails with
    # "no Modelfile or safetensors files found" AND EXIT CODE 0 -- a failure that reports
    # success, which is why this is written out rather than left to mktemp.
    tmp="./.modelfile.$$.tmp"
    printf 'FROM %s\nPARAMETER num_ctx %s\nPARAMETER num_gpu 66\n' "${BLOB[$q]}" "$ctx" > "$tmp"
    printf '%-22s ctx=%-6s ' "$tag" "$ctx"
    # verify by reading the tag back, because create's exit code is not trustworthy here
    if "$OLLAMA" create "$tag" -f "$tmp" >/dev/null 2>&1 \
       && "$OLLAMA" show --modelfile "$tag" 2>/dev/null | grep -q "num_ctx $ctx"; then
        echo "ok"
    else
        echo "FAILED"
    fi
    rm -f "$tmp"
done

# Verify the whole set rather than trusting the loop: this script's one previous
# failure was a partial run that reported success.
present=$("$OLLAMA" list 2>/dev/null | awk '/^q27-.*-(24|32|48|64)k/{c++} END{print c+0}')
echo "cell tags present: $present of 15"
[ "$present" -eq 15 ] || { echo "INCOMPLETE -- rerun; do not record the tags as built"; exit 1; }
