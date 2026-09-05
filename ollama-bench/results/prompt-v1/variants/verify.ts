/** pv1 variant verify: replaces pi's system prompt with the sibling verify.md. */
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const TEXT = fs.readFileSync(path.join(HERE, "verify.md"), "utf8");

export default function variant(pi: any) {
	pi.on("before_agent_start", async (event: any) => ({
		systemPrompt: TEXT.replace(/<<<CWD>>>/g,
			String(event?.systemPromptOptions?.cwd ?? "").replace(/\\/g, "/")),
	}));
}
