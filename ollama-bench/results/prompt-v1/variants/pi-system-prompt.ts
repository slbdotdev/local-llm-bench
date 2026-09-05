/**
 * pi system prompt v1 — GLM 5.3 Flash.
 *
 * Loads beside pi-resilience.ts:
 *   pi -e .../pi-resilience.ts -e .../pi-system-prompt.ts
 *
 * It does NOT replace pi's system prompt. It inserts the guideline bullets from the sibling
 * pi-system-prompt.md immediately after pi's own last standing guideline, which is where the
 * measured variant put them. Inserting rather than replacing keeps pi's live tool list, its
 * host-correct documentation paths and its cwd line, all of which differ per host and per pi
 * version and would be frozen wrong by a full replacement.
 */
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const BULLETS = fs.readFileSync(path.join(HERE, "pi-system-prompt.md"), "utf8").replace(/\s+$/, "") + "\n";
const ANCHOR = "- Show file paths clearly when working with files\n";
const FIRST = BULLETS.split("\n", 1)[0];

export default function systemPrompt(pi: any) {
	pi.on("before_agent_start", async (event: any) => {
		const prompt: string = event?.systemPrompt ?? "";
		if (prompt.includes(FIRST)) return undefined; // already applied this turn
		const i = prompt.indexOf(ANCHOR);
		if (i >= 0) {
			const at = i + ANCHOR.length;
			return { systemPrompt: prompt.slice(0, at) + BULLETS + prompt.slice(at) };
		}
		console.error("pi-system-prompt: pi's anchor guideline is absent (custom prompt, or a pi " +
			"version whose default guidelines changed); appending the block at the end instead");
		return { systemPrompt: prompt + "\n\nGuidelines (continued):\n" + BULLETS };
	});
}
