/** Append every assistant/tool turn of a trial to a per-sandbox trace file. */
import * as fs from "node:fs";
import * as path from "node:path";

const DIR = process.env.PV1_TRACE_DIR || "C:/Users/slb/bench-prompt-variants/traces";
const CAP = 4000;

export default function trace(pi: any) {
	let file: string | null = null;
	pi.on("before_agent_start", async (event: any) => {
		try {
			fs.mkdirSync(DIR, { recursive: true });
			const cwd = String(event?.systemPromptOptions?.cwd ?? "unknown");
			file = path.join(DIR, path.basename(cwd) + ".txt");
			fs.appendFileSync(file, "\n===== USER PROMPT =====\n" +
				String(event?.prompt ?? "").slice(0, 2000) + "\n", "utf8");
		} catch (_e) { /* tracing must never fail a trial */ }
		return undefined;
	});
	pi.on("agent_end", async (event: any) => {
		if (!file) return;
		try {
			for (const m of (event?.messages ?? [])) {
				const parts: string[] = [];
				for (const b of (m?.content ?? [])) {
					if (b?.type === "text") parts.push("[text] " + String(b.text ?? "").slice(0, CAP));
					else if (b?.type === "thinking") parts.push("[thinking] " + String(b.thinking ?? b.text ?? "").slice(0, 1200));
					else if (b?.type === "toolCall") parts.push("[toolCall " + b.name + "] " + JSON.stringify(b.arguments ?? b.input ?? {}).slice(0, CAP));
					else if (b?.type === "toolResult") parts.push("[toolResult] " + JSON.stringify(b.content ?? b.output ?? "").slice(0, 1500));
					else parts.push("[" + String(b?.type) + "]");
				}
				fs.appendFileSync(file, "\n--- " + String(m?.role) + " (stop=" + String(m?.stopReason ?? "-") + ") ---\n" +
					parts.join("\n") + "\n", "utf8");
			}
		} catch (_e) { /* tracing must never fail a trial */ }
	});
}
