# Published benchmarks for the reference arms — 2026-09-05

*Luna web research (codex-run, run wr-wsl-20260905T032607Z-e14e5a3519c6), brief and verification by the control session. Verified by the session against the cited pages: Terminal-Bench 2.1 (Sonnet 80.4, Luna 84.7), DeepSWE v1.1 (Sonnet 54.0, Luna 67.2), OpenRouter card prices (GLM $0.075/$0.25, Haiku $1/$5), Sonnet 85.2/63.2 via search snippets; GLM 84.3 and 63.4 confirmed by search snippets only, the Z.ai page returned 404 to the session. Companion to reference-arms-2026-09-05.md.*

Release dates: Sonnet 5 — Jun 30, 2026; GPT-5.6 family — Jun 26 preview, Jul 9 GA; Haiku 4.5 — Oct 15, 2025; GLM-5.3 Flash — Aug 26, 2026. OpenAI’s Luna is a public, named GPT-5.6 tier with dedicated benchmark rows—not an internal alias.

| Benchmark | Claude Sonnet 5 | GPT-5.6 Luna | Claude Haiku 4.5 | GLM-5.3 Flash |
|---|---:|---:|---:|---:|
| SWE-bench Verified | 85.2%ᵃ | 74.9%ᵇ† | 73.3%ᶜ |  |
| SWE-bench Pro | 63.2%ᵃ | 62.7%ᵇ | 39.45%ᵈ |  |
| Terminal-Bench 2.0* | 80.4%ᵉ | 84.7%ᵉ | 43.8%ᵉ |  |
| Terminal-Bench 2.1 | 80.4%ᶠ | 84.7%ᶠ |  | 84.3%ᵍ |
| DeepSWE v1.1 | 54.0%ʰ | 67.2%ʰ |  | 63.4%ᵍ |
| LiveCodeBench |  |  |  |  |
| Aider Polyglot |  | 88.0%ⁱ† | 97.6%ʲ‡ |  |

\* Model Beats labels its second-generation leaderboard “Terminal-Bench 2.0”; vendor pages generally call these newer runs 2.1. Anthropic’s Haiku announcement separately reports 41.0% under its generic “Terminal-Bench” label.

† GPT-5 family reference, not an exact GPT-5.6 Luna result.  
‡ Haiku result is Shogo’s 81/83 two-language run, not a directly comparable vendor leaderboard submission.

ᵃ [Anthropic Sonnet 5 announcement](https://www.anthropic.com/research/claude-sonnet-5), Jun 30, 2026; benchmark values cross-checked against [LLM Reference](https://www.llmreference.com/model/claude-sonnet-5), observed Jun 30.  
ᵇ [OpenAI GPT-5.6 announcement](https://openai.com/index/gpt-5-6/), Jul 9, 2026 GA.  
ᶜ [Anthropic Haiku 4.5 announcement](https://www.anthropic.com/news/claude-haiku-4-5?s=08), Oct 15, 2025.  
ᵈ [SWE-bench Pro leaderboard](https://evals.report/benchmarks/swe-bench-pro?tab=scores), Aug 17, 2026 data snapshot.  
ᵉ [Model Beats Terminal-Bench 2.0 leaderboard](https://modelbeats.com/benchmarks/terminal-bench-2), accessed Sep 4, 2026; page has no publication date.  
ᶠ [Terminal-Bench 2.1 leaderboard](https://evals.report/benchmarks/terminal-bench?tab=scores), accessed Sep 4, 2026; rows dated Jun 30/Jul 9, 2026.  
ᵍ [Z.ai AutoClaw GLM-5.3 Flash announcement](https://autoclaw.z.ai/blog/model/glm-5-3-flash/), Sep 4, 2026.  
ʰ [DeepSWE v1.1 leaderboard](https://atlas.kevinhu.io/benchmarks/deepswe-1-1), benchmark page dated Jun 14, 2026.  
ⁱ [OpenAI GPT-5 developer announcement](https://openai.com/index/introducing-gpt-5-for-developers/), Aug 7, 2025.  
ʲ [Shogo Aider Polyglot comparison](https://www.shogo.ai/blog/12x-work-per-dollar-hoshi-vs-haiku/), May 30, 2026.

| Benchmark | Implied public ordering | Internal ordering |
|---|---|---|
| SWE-bench Verified | Sonnet > Haiku; Luna family reference only | Sonnet > Luna > Haiku > GLM |
| SWE-bench Pro | Sonnet > Luna > Haiku | Sonnet > Luna > Haiku > GLM |
| Terminal-Bench 2.0 | Luna > Sonnet > Haiku | Sonnet > Luna > Haiku > GLM |
| Terminal-Bench 2.1 | Luna > GLM > Sonnet | Sonnet > Luna > Haiku > GLM |
| DeepSWE v1.1 | Luna > GLM > Sonnet | Sonnet > Luna > Haiku > GLM |
| LiveCodeBench | No ordering | Sonnet > Luna > Haiku > GLM |
| Aider Polyglot | No comparable four-model ordering | Sonnet > Luna > Haiku > GLM |

Our ordering aligns best with SWE-bench Pro: Sonnet and Luna are nearly tied publicly (63.2% vs. 62.7%), while Haiku is much lower. It does not align on Terminal-Bench 2.1 or DeepSWE, where Luna leads and GLM is at least as strong as Sonnet. The internal Haiku-versus-GLM gap is small, but no directly comparable public result establishes that ordering. Cost explains choosing GLM: OpenRouter listed GLM at $0.075/$0.25 per million input/output tokens versus Haiku’s $1/$5—roughly 13× cheaper on input and 20× on output; GLM’s standard first-party price is $0.15/$0.50, still about 6.7×/10× cheaper. ([OpenRouter](https://openrouter.ai/compare/z-ai/glm-5.3-flash/x-ai/grok-4.5), [Artificial Analysis](https://artificialanalysis.ai/models/glm-5-3-flash/))

I could not find exact-model public LiveCodeBench scores for any of the four, an exact Luna SWE-bench Verified score, a GLM-5.3 Flash SWE-bench score, or directly comparable Sonnet/GLM Aider Polyglot scores.