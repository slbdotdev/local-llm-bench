/** Dump the chained system prompt as seen after earlier extensions. */
import * as fs from "node:fs";
export default function capture2(pi: any) {
	pi.on("before_agent_start", async (event: any, ctx: any) => {
		try {
			fs.writeFileSync("C:/Users/slb/bench-prompt-variants/chained-capture.md",
				ctx.getSystemPrompt(), "utf8");
			console.error("pv1-capture2: chained prompt " + ctx.getSystemPrompt().length + " chars");
		} catch (e) { console.error("pv1-capture2: FAILED " + e); }
		return undefined;
	});
}
