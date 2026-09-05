/** One-shot capture: pi's default system prompt and the resolved model/provider. */
import * as fs from "node:fs";

const DIR = "C:/Users/slb/bench-prompt-variants";
const PROMPT_OUT = DIR + "/baseline-capture.md";
const PROOF_OUT = DIR + "/baseline-proof.json";

export default function capture(pi: any) {
	pi.on("before_agent_start", async (event: any, ctx: any) => {
		try {
			const prompt = ctx.getSystemPrompt();
			if (!fs.existsSync(PROMPT_OUT)) fs.writeFileSync(PROMPT_OUT, prompt, "utf8");
			const m = ctx.model ?? {};
			let baseUrl: string | null = null;
			try {
				const auth = ctx.modelRegistry?.getProviderAuth?.(m.provider ?? m.providerId);
				baseUrl = auth?.baseUrl ?? null;
			} catch (_e) { /* best effort */ }
			const proof = {
				provider: m.provider ?? m.providerId ?? null,
				modelId: m.id ?? m.modelId ?? null,
				modelName: m.name ?? null,
				contextWindow: m.contextWindow ?? null,
				thinkingLevel: ctx.thinkingLevel ?? null,
				baseUrl,
				systemPromptChars: prompt.length,
				importMetaUrl: (typeof import.meta !== "undefined" ? import.meta.url : null),
				cwd: event?.systemPromptOptions?.cwd ?? null,
				toolCount: (event?.systemPromptOptions?.selectedTools ?? []).length,
				skills: (event?.systemPromptOptions?.skills ?? []).length,
				contextFiles: (event?.systemPromptOptions?.contextFiles ?? []).length,
			};
			fs.writeFileSync(PROOF_OUT, JSON.stringify(proof, null, 1), "utf8");
			console.error("pv1-capture: provider=" + proof.provider + " model=" + proof.modelId +
				" base=" + proof.baseUrl + " prompt=" + proof.systemPromptChars + " chars");
		} catch (e) {
			console.error("pv1-capture: FAILED " + e);
		}
		return undefined;
	});
}
