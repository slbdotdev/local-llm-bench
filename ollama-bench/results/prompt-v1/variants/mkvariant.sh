#!/bin/bash
# usage: mkvariant.sh <name>   -- writes <name>.ts beside <name>.md
set -eu
V=/mnt/c/Users/slb/bench-prompt-variants
N=$1
test -f "$V/$N.md" || { echo "missing $V/$N.md"; exit 1; }
cat > "$V/$N.ts" <<TS
/** pv1 variant $N: replaces pi's system prompt with the sibling $N.md. */
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const TEXT = fs.readFileSync(path.join(HERE, "$N.md"), "utf8");

export default function variant(pi: any) {
	pi.on("before_agent_start", async (event: any) => ({
		systemPrompt: TEXT.replace(/<<<CWD>>>/g,
			String(event?.systemPromptOptions?.cwd ?? "").replace(/\\\\/g, "/")),
	}));
}
TS
echo "wrote $V/$N.ts"
