#!/bin/bash
# Run one band of the ZCode reference arm. Usage: run_band.sh {tiny|large}
# Sources the fleet env for ZAI_API_KEY; the key is never echoed.
set -a
. "$HOME/.config/devbox/env" >/dev/null 2>&1
set +a
BAND="$1"
D="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$D/$BAND/trial-0"
rm -f "$D/$BAND.done"
python3 -u "$D/run_zcode_gate.py" "$BAND" "$2" >> "$D/$BAND.driver.log" 2>&1 < /dev/null
echo "EXIT=$?" > "$D/$BAND.done"
