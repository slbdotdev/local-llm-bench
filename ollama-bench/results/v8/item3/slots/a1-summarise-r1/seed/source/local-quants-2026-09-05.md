# Local quant roster, 2026-09-05

The v6 sweep ran nine Qwen3.8-27B quants on an RTX 5080 16 GB, using Ollama on Windows,
the pi harness, and the frozen v5 suite. Every 3-bit quant except UD-IQ3_S stops at 48k.
UD-IQ3_S was pulled later, passed placement at 64k, and remains unscored for a later candidate run.

## Placement

| quant | max context | resident GB | gen tok/s |
| --- | ---: | ---: | ---: |
| IQ2_M | 96k | 13.27 | 41.9 |
| Q2_K | 64k | 13.07 | 45.1 |
| Q2_K_L | 64k | 13.35 | 44.9 |
| IQ3_XXS | 48k | 13.07 | 47.0 |
| IQ3_XS | 48k, marginal | 14.34 | 26.7 |
| UDQ3KXL | 48k | 13.45 | 44.8 |
| mrIQ3M | 48k | 13.25 | 42.7 |
| UD-IQ3_S | 64k, unscored | 13.03 | 46.5 |
| rejected | Q3_K_S, IQ3_M | no viable rung | - |

## Scored rows

| outcome | rows | rate |
| --- | ---: | ---: |
| pass | 111/148 | 75.0% |
| confidently wrong | 24/148 | 16.2% |
| visibly failed | 13/148 | 8.8% |
| timeouts | 8/148 | 5.4% |

IQ2_M at 64k is the workhorse. Phase D chose it by pass rate, then confidently-wrong rate,
then median wall. UDQ3KXL at 48k and Q2_K at 64k are the neighbours for v7 calibration.
On the shared finalist cells both scored 26/33; IQ2_M had 4% confidently wrong against UDQ3KXL
at 25%. IQ2_M also held 96k at 6/8 on the large band with 0% confidently wrong.
Ollama model storage is managed through `windows_app_config` on 2026-09-05;
`OLLAMA_MODELS` points to `E:\ollama\models`.

## v7 calibration, the same night

One trial per task on the v7 suite (20 tasks, main 48k-authored material run at each quant's rung, cheap 24k):
IQ2_M 19/20, UDQ3KXL 20/20, Q2_K 19/20; main band 10/10 for all three.
Main-band trials read about 4 of 91 files and reached 4 to 27% of the window, so the suite, not the quant, sets the rate.
Three `unsafe` verdicts on the first pass were a grader defect under Windows Python (`os.path.normcase` on one side of a file-set comparison), repaired and re-graded.
Report: local-llm-bench `results/v7/calibration-2026-09-06.md`.

## Withdrawn findings

- D6-34 and D6-36: the 584.1 s Q2_K t03 result did not reproduce; later retests were 48.9 s and 32.9 s under about 6% contention.
- D6-9, withdrawn by D6-26: the claimed i-quant overhead came from offloaded cells; clean cells showed no i-quant penalty.
- D6-18, withdrawn by D6-21: the claimed 89 MB per 1k KV figure became 39 MB per 1k from clean cells.

## Caveats

- Rows fill only 25 to 39% of a 64k window.
- The GPU was shared from 22:44 with about 6% contention.

## Models moved to D:, 2026-09-05

- `OLLAMA_MODELS` now points at `D:\ollama\models` (ansible-managed with the KV and flash-attention variables); the move used robocopy `/E /MOVE` with no server running.
- The running server (pid 19824) was elevated in session 0 and could not be stopped by the user; ansible's elevated WinRM `taskkill` did it.
- E: was tried first and abandoned: it is a Crucial BX500 2 TB, DRAM-less QLC, and sustained writes fell to about 2 MB/s once its cache filled, a 10-hour move for 93 GB. D: (Samsung 840 PRO, MLC) took it in minutes. Do not put bulk data on E: in one pass.

## Owner calls still open

- 48k-only quants stay on disk for now (owner, 2026-09-06); all 35 tags over eight quants, 93 GB on D:.
- Decide the t02 line-number format.

## Addendum, 2026-09-06: a published quant survey against this record

Kai's "I Tested Every Qwen3.8-27B Quant" (YouTube, 2026-09-01, 14 min) was
read against this page by a Luna worker (transcript in the control session's
scratch). What is new here and worth keeping:

- **Quant files are replaced under the same name.** The video reports Unsloth
  swapping files on 2026-08-19 and benchmark artifacts replaced after 2.7
  million downloads; the date and count are unverified, the practice is real.
  This page pins quants by tag name only. A kept quant should carry its file
  hash or Hugging Face revision beside the tag.
- **Tensor protection over nominal bits.** Good quants keep output and
  attention tensors at higher precision and compress the rest (the Ridge and
  Bartowski cards say so). It is the likely reason IQ2_M, UDQ3KXL and Q2_K did
  not separate on the v7 suite: they differ by nominal bits, not by what they
  protect.
- **An MTP draft head** ships in Bartowski's files and enables speculative
  decoding with no second model. Confirmed for those files only; untested here.
- **Chat-template handling** can nest thinking blocks and degrade long
  conversations. Relevant to pibench's multi-turn trials; unchecked.
- **Default reasoning is the highest mode**, spending on the order of 22k
  thinking tokens; the default is confirmed, the figure anecdotal. Consistent
  with the fp8 loop seen at `high` and the bench's choice of `medium`.

Where the video conflicts with this page, the measurements here stand: its
"four-bit is the floor" and "12 GB owners should pick a smaller model" rest on
a study Luna could not locate, while IQ2_M at 64k is measured viable on this
card. Its Q8-versus-Q4 KV-cache figures come from a different 7B model; the
64k KV rerun (`pending.md`) answers that for this one.

